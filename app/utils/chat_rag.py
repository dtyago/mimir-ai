#list of librarys for requirement.txt
import os
import re
import hashlib
import asyncio
import pretty_errors
import logging

from langchain_community.document_loaders import PyPDFLoader

# Import embeddings module from langchain_community for vector representations of text
from langchain_community.embeddings import HuggingFaceEmbeddings

# Import text splitter for handling large texts
from langchain.text_splitter import CharacterTextSplitter

# Import vector store for database operations
from langchain_community.vectorstores import Chroma

# Import Azure OpenAI for LLM functionality
from langchain_openai import AzureChatOpenAI

from langchain.chains.router.llm_router import LLMRouterChain, RouterOutputParser
from langchain.chains.router.multi_prompt_prompt import MULTI_PROMPT_ROUTER_TEMPLATE

from langchain.chains.router import MultiPromptChain
from langchain.chains import ConversationChain
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory, VectorStoreRetrieverMemory
from langchain.chains import ConversationalRetrievalChain

# Configure basic logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def sanitize_collection_name(email):
    # Replace invalid characters with an underscore
    sanitized = re.sub(r'[^a-zA-Z0-9_-]', '_', email)
    # Ensure the name is within the length limits
    if len(sanitized) > 63:
        # Hashing the name to ensure uniqueness and length constraint
        hash_suffix = hashlib.sha256(email.encode()).hexdigest()[:8]
        sanitized = sanitized[:55] + "_" + hash_suffix
    # Ensure it starts and ends with an alphanumeric character
    if not re.match(r'^[a-zA-Z0-9].*[a-zA-Z0-9]$', sanitized):
        sanitized = "a" + sanitized + "1"
    return sanitized


# Modify vectordb initialization to be dynamic based on user_id
async def get_vectordb_for_user(user_collection_name):
    # Get Chromadb location
    CHROMADB_LOC = os.getenv('CHROMADB_LOC')

    vectordb = Chroma(
        collection_name=user_collection_name,
        embedding_function=HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2'),
        persist_directory=f"{CHROMADB_LOC}" # Optional: Separate directory for each user's data
    )
    return vectordb

vectordb_cache = {}

async def get_vectordb_for_user_cached(user_collection_name):
    try:
        if user_collection_name not in vectordb_cache:
            vectordb_cache[user_collection_name] = await get_vectordb_for_user(user_collection_name)
        return vectordb_cache[user_collection_name]
    except Exception as e:
        logging.error(f'Error accessing vector DB for user {user_collection_name}: {e}')
        raise

def pdf_to_vec(filename, user_collection_name):
    
    # Get Chromadb location
    CHROMADB_LOC = os.getenv('CHROMADB_LOC')

    document = []
    loader = PyPDFLoader(filename)
    document.extend(loader.load()) #which library is this from?

    # Initialize HuggingFaceEmbeddings with the 'sentence-transformers/all-MiniLM-L6-v2' model for generating text embeddings
    embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')

    # Initialize a CharacterTextSplitter to split the loaded documents into smaller chunks
    document_splitter = CharacterTextSplitter(separator='\n', chunk_size=500, chunk_overlap=100)

    # Use the splitter to divide the 'document' content into manageable chunks
    document_chunks = document_splitter.split_documents(document) #which library is this from?

    # Create a Chroma vector database from the document chunks with the specified embeddings, and set a directory for persistence
    vectordb = Chroma.from_documents(document_chunks, embedding=embeddings, collection_name=user_collection_name, persist_directory=CHROMADB_LOC) ## change to GUI path

    # Persist the created vector database to disk in the specified directory
    vectordb.persist() #this is mandatory?

    return(vectordb)
    #return collection  # Return the collection as the asset


class AzureOpenAIModelSingleton:
    _instance = None
    _metadata = None  # Store metadata alongside the instance for easy access

    @classmethod
    async def get_instance(cls):
        if cls._instance is None:
            cls._instance, cls._metadata = await cls._load_llm()  # Adjust to return both model and metadata
        return cls._instance, cls._metadata

    @staticmethod
    async def _load_llm():
        print('Loading Azure OpenAI model...')
        
        # Get Azure OpenAI configuration from environment variables
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
        deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")
        
        if not azure_endpoint or not api_key:
            raise ValueError("Azure OpenAI endpoint and API key must be set in environment variables")
        
        try:
            llm = AzureChatOpenAI(
                azure_endpoint=azure_endpoint,
                api_key=api_key,
                api_version=api_version,
                deployment_name=deployment_name,
                temperature=0.1,
                max_tokens=2000,
            )
            
            # Metadata for Azure OpenAI
            metadata = {
                'model.context_length': 4096,  # Default context length for GPT-4
                'model.deployment_name': deployment_name,
                'model.api_version': api_version,
                'model.temperature': 0.1,
                'model.max_tokens': 2000,
            }
            print(f'Azure OpenAI model loaded with deployment: {deployment_name}')
            return llm, metadata
        except Exception as e:
            logging.error(f'Failed to load Azure OpenAI model: {e}')
            raise

async def load_llm():
    """Load just the LLM instance (without metadata)"""
    llm, _ = await AzureOpenAIModelSingleton.get_instance()
    return llm

class EnhancedConversationalChain:
    _instance = None
    _lock = asyncio.Lock()

    def __init__(self, llm, retriever, context_length, deployment_name, api_version):
        # Initialize with Azure OpenAI specific parameters
        self.llm = llm
        self.retriever = retriever
        self.context_length = context_length
        self.deployment_name = deployment_name
        self.api_version = api_version
        # Additional initialization based on metadata...

    @classmethod
    async def get_instance(cls):
        async with cls._lock:
            if cls._instance is None:
                # Load the model and retrieve necessary metadata for initialization
                llm, model_metadata = await AzureOpenAIModelSingleton.get_instance()
                logging.info(f"Loaded model metadata keys: {list(model_metadata.keys())}")
                # Extract needed parameters from metadata
                context_length = model_metadata['model.context_length']
                deployment_name = model_metadata['model.deployment_name']
                api_version = model_metadata['model.api_version']

                retriever = None  # Initialize retriever based on application logic
                cls._instance = cls(llm, retriever, context_length, deployment_name, api_version)
            return cls._instance

    async def run(self, input_text, user_collection_name):
        vectordb = await get_vectordb_for_user_cached(user_collection_name)
        retrieved_docs = vectordb.similarity_search(input_text)
        augmented_input = self.augment_input_with_docs(input_text, retrieved_docs)
        
        # Use the LLM directly since this class doesn't inherit from a chain
        try:
            response = await self.llm.ainvoke([{"role": "user", "content": augmented_input}])
            return response.content
        except Exception as e:
            # Fallback to sync invoke if async is not available
            response = self.llm.invoke([{"role": "user", "content": augmented_input}])
            return response.content

    def augment_input_with_docs(self, input_text, docs):
        max_docs = 3
        sentences_per_summary = 2

        summaries = [self.generate_summary(doc.page_content, sentences_per_summary) for doc in docs[:max_docs]]
        augmented_input = "\n".join(["Summary: " + summary for summary in summaries] + [input_text])

        return augmented_input

    def generate_summary(self, text, num_sentences):
        sentences = text.split('. ')[:num_sentences]
        return '. '.join(sentences)
    

async def llm_infer(user_collection_name, prompt):
    try:
        llm = await load_llm()
        conversation_chain = await EnhancedConversationalChain.get_instance()  # Assuming an async get_instance method
        response = await conversation_chain.run(prompt, user_collection_name)
        return response
    except Exception as e:
        logging.error(f'Error during LLM inference for user {user_collection_name}: {e}')
        raise


# Assuming a simplified caching mechanism for demonstration
chain_cache = {}

async def get_or_create_chain(user_collection_name, llm):
    if 'default_chain' in chain_cache and 'router_chain' in chain_cache:
        default_chain = chain_cache['default_chain']
        router_chain = chain_cache['router_chain']
        destination_chains = chain_cache['destination_chains']
    else:
        vectordb = await get_vectordb_for_user_cached(user_collection_name)  # User-specific vector database
        sum_template = """
        As a machine learning education specialist, our expertise is pivotal in deepening the comprehension of complex machine learning concepts for both educators and students.

        our role entails:

        Providing Detailed Explanations: Deliver comprehensive answers to these questions, elucidating the underlying technical principles.
        Assisting in Exam Preparation: Support educators in formulating sophisticated exam and quiz questions, including MCQs, accompanied by thorough explanations.
        Summarizing Course Material: Distill key information from course materials, articulating complex ideas within the context of advanced machine learning practices.

        Objective: to summarize and explain the key points.
        Here the question:
        {input}"""

        mcq_template = """
        As a machine learning education specialist, our expertise is pivotal in deepening the comprehension of complex machine learning concepts for both educators and students.

        our role entails:
        Crafting Insightful Questions: Develop thought-provoking questions that explore the intricacies of machine learning topics.
        Generating MCQs: Create MCQs for each machine learning topic, comprising a question, four choices (A-D), and the correct answer, along with a rationale explaining the answer.

        Objective: to create multiple choice question in this format
        [question:
        options A:
        options B:
        options C:
        options D:
        correct_answer:
        explanation:]

        Here the question:
        {input}"""

        prompt_infos = [
            {
                "name": "SUMMARIZE",
                "description": "Good for summarizing and explaination ",
                "prompt_template": sum_template,
            },
            {
                "name": "MCQ",
                "description": "Good for creating multiple choices questions",
                "prompt_template": mcq_template,
            },
        ]

        destination_chains = {}

        for p_info in prompt_infos:
            name = p_info["name"]
            prompt_template = p_info["prompt_template"]
            prompt = PromptTemplate(template=prompt_template, input_variables=["input"])
            chain = LLMChain(llm=llm, prompt=prompt)
            destination_chains[name] = chain
        #default_chain = ConversationChain(llm=llm, output_key="text")
        #memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)

        default_chain = ConversationalRetrievalChain.from_llm(llm=llm,
                                                    retriever=vectordb.as_retriever(search_kwargs={'k': 3}),
                                                    verbose=True, output_key="text" )

        destinations = [f"{p['name']}: {p['description']}" for p in prompt_infos]
        destinations_str = "\n".join(destinations)
        router_template = MULTI_PROMPT_ROUTER_TEMPLATE.format(destinations=destinations_str)
        router_prompt = PromptTemplate(
            template=router_template,
            input_variables=["input"],
            output_parser=RouterOutputParser(),
        )
        router_chain = LLMRouterChain.from_llm(llm, router_prompt)
#
        chain_cache['default_chain'] = default_chain
        chain_cache['router_chain'] = router_chain
        chain_cache['destination_chains'] = destination_chains
    
    # Here we can adapt the chains if needed based on the user_id, for example, by adjusting the vectordb retriever
    # This is where user-specific adaptations occur

    return default_chain, router_chain, destination_chains

#!/usr/bin/env python3
"""
Enhanced RAG System for Mimir API
Combines multiple data sources:
1. Backend data sources (data mart)
2. Common knowledge base from PDFs
3. Conversation history context per user
4. Role-based content filtering
"""

import os
import json
import logging
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

import asyncio
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_openai import AzureChatOpenAI
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataSourceType(Enum):
    """Types of data sources in the RAG system"""
    USER_DOCUMENTS = "user_documents"
    COMMON_KNOWLEDGE = "common_knowledge"
    DATA_MART = "data_mart"
    CONVERSATION_HISTORY = "conversation_history"
    ROLE_SPECIFIC = "role_specific"

@dataclass
class RAGContext:
    """Context information for RAG retrieval"""
    user_id: str
    role: str
    session_id: str
    data_sources: List[DataSourceType]
    max_tokens: int = 4000
    max_documents: int = 5
    conversation_window: int = 10

class EnhancedRAGSystem:
    """
    Enhanced RAG system that integrates multiple data sources
    and maintains conversation context per user
    """
    
    def __init__(self):
        self.chromadb_loc = os.getenv('CHROMADB_LOC')
        self.embeddings = HuggingFaceEmbeddings(
            model_name='sentence-transformers/all-MiniLM-L6-v2'
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        # Initialize collections for different data sources
        self._init_collections()
        
        # Cache for conversation memories per user
        self.conversation_memories = {}
        
        # Cache for role-specific retrievers
        self.role_retrievers = {}
        
        logger.info("Enhanced RAG System initialized")

    def _init_collections(self):
        """Initialize ChromaDB collections for different data sources"""
        try:
            # Common knowledge base (shared across all users)
            self.common_knowledge_db = Chroma(
                collection_name="common_knowledge_base",
                embedding_function=self.embeddings,
                persist_directory=self.chromadb_loc
            )
            
            # Data mart collection (business data)
            self.data_mart_db = Chroma(
                collection_name="data_mart_base",
                embedding_function=self.embeddings,
                persist_directory=self.chromadb_loc
            )
            
            # Role-specific collections
            self.role_collections = {
                "Analyst-Gaming": Chroma(
                    collection_name="role_analyst_gaming",
                    embedding_function=self.embeddings,
                    persist_directory=self.chromadb_loc
                ),
                "Analyst-Non-Gaming": Chroma(
                    collection_name="role_analyst_non_gaming",
                    embedding_function=self.embeddings,
                    persist_directory=self.chromadb_loc
                ),
                "Leadership-Gaming": Chroma(
                    collection_name="role_leadership_gaming",
                    embedding_function=self.embeddings,
                    persist_directory=self.chromadb_loc
                ),
                "Leadership-Non-Gaming": Chroma(
                    collection_name="role_leadership_non_gaming",
                    embedding_function=self.embeddings,
                    persist_directory=self.chromadb_loc
                )
            }
            
            logger.info("ChromaDB collections initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing ChromaDB collections: {e}")
            raise

    def sanitize_collection_name(self, name: str) -> str:
        """Sanitize collection name for ChromaDB compatibility"""
        sanitized = ''.join(c if c.isalnum() or c in '-_' else '_' for c in name)
        if len(sanitized) > 63:
            hash_suffix = hashlib.sha256(name.encode()).hexdigest()[:8]
            sanitized = sanitized[:55] + "_" + hash_suffix
        return sanitized

    async def get_user_document_db(self, user_id: str) -> Chroma:
        """Get or create user-specific document collection"""
        collection_name = self.sanitize_collection_name(f"user_docs_{user_id}")
        
        return Chroma(
            collection_name=collection_name,
            embedding_function=self.embeddings,
            persist_directory=self.chromadb_loc
        )

    async def get_conversation_history_db(self, user_id: str) -> Chroma:
        """Get or create user-specific conversation history collection"""
        collection_name = self.sanitize_collection_name(f"chat_history_{user_id}")
        
        return Chroma(
            collection_name=collection_name,
            embedding_function=self.embeddings,
            persist_directory=self.chromadb_loc
        )

    async def add_to_common_knowledge(self, documents: List[Document], source: str = "manual"):
        """Add documents to the common knowledge base"""
        try:
            # Add metadata to track source
            for doc in documents:
                doc.metadata.update({
                    "source_type": "common_knowledge",
                    "source": source,
                    "added_at": datetime.utcnow().isoformat()
                })
            
            # Split documents into chunks
            chunks = self.text_splitter.split_documents(documents)
            
            # Add to common knowledge base
            self.common_knowledge_db.add_documents(chunks)
            self.common_knowledge_db.persist()
            
            logger.info(f"Added {len(chunks)} chunks to common knowledge base from {source}")
            
        except Exception as e:
            logger.error(f"Error adding to common knowledge: {e}")
            raise

    async def add_to_data_mart(self, data: Dict[str, Any], data_type: str = "business_data"):
        """Add structured data to the data mart"""
        try:
            # Convert structured data to text documents
            text_content = self._structure_data_to_text(data, data_type)
            
            doc = Document(
                page_content=text_content,
                metadata={
                    "source_type": "data_mart",
                    "data_type": data_type,
                    "added_at": datetime.utcnow().isoformat(),
                    "original_data": json.dumps(data)
                }
            )
            
            chunks = self.text_splitter.split_documents([doc])
            self.data_mart_db.add_documents(chunks)
            self.data_mart_db.persist()
            
            logger.info(f"Added data mart entry of type {data_type}")
            
        except Exception as e:
            logger.error(f"Error adding to data mart: {e}")
            raise

    async def add_to_role_specific(self, role: str, documents: List[Document]):
        """Add documents to role-specific collection"""
        try:
            if role not in self.role_collections:
                logger.warning(f"Role {role} not found in role collections")
                return
            
            # Add metadata
            for doc in documents:
                doc.metadata.update({
                    "source_type": "role_specific",
                    "role": role,
                    "added_at": datetime.utcnow().isoformat()
                })
            
            chunks = self.text_splitter.split_documents(documents)
            self.role_collections[role].add_documents(chunks)
            self.role_collections[role].persist()
            
            logger.info(f"Added {len(chunks)} chunks to role-specific collection for {role}")
            
        except Exception as e:
            logger.error(f"Error adding to role-specific collection: {e}")
            raise

    async def store_conversation_turn(self, user_id: str, user_input: str, ai_response: str):
        """Store a conversation turn in user's history"""
        try:
            conversation_db = await self.get_conversation_history_db(user_id)
            
            # Create document for the conversation turn
            conversation_text = f"User: {user_input}\nAssistant: {ai_response}"
            
            doc = Document(
                page_content=conversation_text,
                metadata={
                    "source_type": "conversation_history",
                    "user_id": user_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "user_input": user_input,
                    "ai_response": ai_response
                }
            )
            
            conversation_db.add_documents([doc])
            conversation_db.persist()
            
            logger.info(f"Stored conversation turn for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error storing conversation: {e}")
            raise

    def _structure_data_to_text(self, data: Dict[str, Any], data_type: str) -> str:
        """Convert structured data to searchable text format"""
        if data_type == "business_metrics":
            return self._format_business_metrics(data)
        elif data_type == "user_analytics":
            return self._format_user_analytics(data)
        elif data_type == "gaming_data":
            return self._format_gaming_data(data)
        else:
            # Generic formatting
            text_parts = [f"{data_type.replace('_', ' ').title()} Data:"]
            for key, value in data.items():
                text_parts.append(f"{key.replace('_', ' ').title()}: {value}")
            return "\n".join(text_parts)

    def _format_business_metrics(self, data: Dict[str, Any]) -> str:
        """Format business metrics data"""
        parts = ["Business Metrics Report:"]
        for metric, value in data.items():
            parts.append(f"- {metric.replace('_', ' ').title()}: {value}")
        return "\n".join(parts)

    def _format_user_analytics(self, data: Dict[str, Any]) -> str:
        """Format user analytics data"""
        parts = ["User Analytics Data:"]
        if "engagement_metrics" in data:
            parts.append("Engagement Metrics:")
            for metric, value in data["engagement_metrics"].items():
                parts.append(f"  - {metric.replace('_', ' ').title()}: {value}")
        if "behavior_patterns" in data:
            parts.append("Behavior Patterns:")
            for pattern in data["behavior_patterns"]:
                parts.append(f"  - {pattern}")
        return "\n".join(parts)

    def _format_gaming_data(self, data: Dict[str, Any]) -> str:
        """Format gaming-specific data"""
        parts = ["Gaming Data Analysis:"]
        if "game_performance" in data:
            parts.append("Game Performance:")
            for game, metrics in data["game_performance"].items():
                parts.append(f"  {game}:")
                for metric, value in metrics.items():
                    parts.append(f"    - {metric.replace('_', ' ').title()}: {value}")
        return "\n".join(parts)

    async def retrieve_relevant_context(self, 
                                      query: str, 
                                      context: RAGContext) -> List[Document]:
        """
        Retrieve relevant documents from multiple sources based on context
        """
        all_documents = []
        
        try:
            # 1. User-specific documents
            if DataSourceType.USER_DOCUMENTS in context.data_sources:
                user_docs_db = await self.get_user_document_db(context.user_id)
                user_docs = user_docs_db.similarity_search(
                    query, k=context.max_documents // len(context.data_sources)
                )
                all_documents.extend(user_docs)
            
            # 2. Common knowledge base
            if DataSourceType.COMMON_KNOWLEDGE in context.data_sources:
                common_docs = self.common_knowledge_db.similarity_search(
                    query, k=context.max_documents // len(context.data_sources)
                )
                all_documents.extend(common_docs)
            
            # 3. Data mart
            if DataSourceType.DATA_MART in context.data_sources:
                data_mart_docs = self.data_mart_db.similarity_search(
                    query, k=context.max_documents // len(context.data_sources)
                )
                all_documents.extend(data_mart_docs)
            
            # 4. Role-specific documents
            if DataSourceType.ROLE_SPECIFIC in context.data_sources and context.role in self.role_collections:
                role_docs = self.role_collections[context.role].similarity_search(
                    query, k=context.max_documents // len(context.data_sources)
                )
                all_documents.extend(role_docs)
            
            # 5. Conversation history
            if DataSourceType.CONVERSATION_HISTORY in context.data_sources:
                history_db = await self.get_conversation_history_db(context.user_id)
                history_docs = history_db.similarity_search(
                    query, k=min(3, context.max_documents // len(context.data_sources))
                )
                all_documents.extend(history_docs)
            
            # Sort by relevance and limit total documents
            all_documents = all_documents[:context.max_documents]
            
            logger.info(f"Retrieved {len(all_documents)} documents for query")
            return all_documents
            
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return []

    def _create_enhanced_prompt(self, 
                               query: str, 
                               documents: List[Document], 
                               context: RAGContext) -> str:
        """Create an enhanced prompt with context from multiple sources"""
        
        # Organize documents by source type
        docs_by_source = {}
        for doc in documents:
            source_type = doc.metadata.get('source_type', 'unknown')
            if source_type not in docs_by_source:
                docs_by_source[source_type] = []
            docs_by_source[source_type].append(doc)
        
        prompt_parts = [
            f"You are Mimir, an AI assistant for a {context.role} user.",
            "Use the following context from multiple sources to answer the question.",
            "Prioritize the most relevant and recent information.\n"
        ]
        
        # Add context from each source type
        if 'user_documents' in docs_by_source:
            prompt_parts.append("=== USER DOCUMENTS ===")
            for doc in docs_by_source['user_documents']:
                prompt_parts.append(doc.page_content[:500] + "...")
            prompt_parts.append("")
        
        if 'common_knowledge' in docs_by_source:
            prompt_parts.append("=== KNOWLEDGE BASE ===")
            for doc in docs_by_source['common_knowledge']:
                prompt_parts.append(doc.page_content[:500] + "...")
            prompt_parts.append("")
        
        if 'data_mart' in docs_by_source:
            prompt_parts.append("=== BUSINESS DATA ===")
            for doc in docs_by_source['data_mart']:
                prompt_parts.append(doc.page_content[:500] + "...")
            prompt_parts.append("")
        
        if 'role_specific' in docs_by_source:
            prompt_parts.append(f"=== {context.role.upper()} SPECIFIC CONTENT ===")
            for doc in docs_by_source['role_specific']:
                prompt_parts.append(doc.page_content[:500] + "...")
            prompt_parts.append("")
        
        if 'conversation_history' in docs_by_source:
            prompt_parts.append("=== RECENT CONVERSATION ===")
            for doc in docs_by_source['conversation_history']:
                prompt_parts.append(doc.page_content[:300] + "...")
            prompt_parts.append("")
        
        prompt_parts.extend([
            f"User Question: {query}",
            "",
            "Provide a comprehensive answer based on the available context.",
            f"Tailor your response to the {context.role} perspective.",
            "If you don't have enough information, say so clearly."
        ])
        
        return "\n".join(prompt_parts)

# Global instance
enhanced_rag_system = None

async def get_enhanced_rag_system() -> EnhancedRAGSystem:
    """Get or create the global enhanced RAG system instance"""
    global enhanced_rag_system
    if enhanced_rag_system is None:
        enhanced_rag_system = EnhancedRAGSystem()
    return enhanced_rag_system

async def enhanced_chat_inference(user_id: str, 
                                role: str, 
                                query: str, 
                                session_id: str = None,
                                data_sources: List[DataSourceType] = None) -> str:
    """
    Enhanced chat inference using multiple data sources
    """
    try:
        # Default data sources if not specified
        if data_sources is None:
            data_sources = [
                DataSourceType.USER_DOCUMENTS,
                DataSourceType.COMMON_KNOWLEDGE,
                DataSourceType.DATA_MART,
                DataSourceType.ROLE_SPECIFIC,
                DataSourceType.CONVERSATION_HISTORY
            ]
        
        # Create context
        context = RAGContext(
            user_id=user_id,
            role=role,
            session_id=session_id or f"{user_id}_{datetime.utcnow().isoformat()}",
            data_sources=data_sources
        )
        
        # Get RAG system
        rag_system = await get_enhanced_rag_system()
        
        # Retrieve relevant documents
        documents = await rag_system.retrieve_relevant_context(query, context)
        
        # Create enhanced prompt
        enhanced_prompt = rag_system._create_enhanced_prompt(query, documents, context)
        
        # Get Azure OpenAI response
        from .chat_rag import load_llm
        llm = await load_llm()
        
        response = await llm.ainvoke([{"role": "user", "content": enhanced_prompt}])
        ai_response = response.content
        
        # Store conversation for future context
        await rag_system.store_conversation_turn(user_id, query, ai_response)
        
        logger.info(f"Enhanced chat inference completed for user {user_id}")
        return ai_response
        
    except Exception as e:
        logger.error(f"Error in enhanced chat inference: {e}")
        raise

# Convenience functions for adding data to different sources
async def add_pdf_to_common_knowledge(pdf_path: str, source_name: str = None):
    """Add a PDF to the common knowledge base"""
    from langchain_community.document_loaders import PyPDFLoader
    
    rag_system = await get_enhanced_rag_system()
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    
    source = source_name or os.path.basename(pdf_path)
    await rag_system.add_to_common_knowledge(documents, source)

async def add_business_data_to_mart(data: Dict[str, Any], data_type: str = "business_data"):
    """Add business data to the data mart"""
    rag_system = await get_enhanced_rag_system()
    await rag_system.add_to_data_mart(data, data_type)

async def add_role_specific_content(role: str, content: str, metadata: Dict[str, Any] = None):
    """Add content to role-specific collection"""
    rag_system = await get_enhanced_rag_system()
    
    doc = Document(
        page_content=content,
        metadata=metadata or {}
    )
    
    await rag_system.add_to_role_specific(role, [doc])

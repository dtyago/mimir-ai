# Mimir API

## Overview

Mimir API is a FastAPI-based conversational platform that combines AI-powered chat capabilities with face recognition authentication. The system allows users to authenticate using facial recognition, upload and process educational documents, and engage in intelligent conversations with an AI assistant powered by Azure OpenAI and Retrieval-Augmented Generation (RAG).

## Features

### 🔐 Face Recognition Authentication
- **Facial Login**: Users authenticate using their face images instead of traditional passwords
- **MTCNN Face Detection**: Utilizes MTCNN for accurate face detection and cropping
- **FaceNet Embeddings**: Leverages FaceNet for generating face embeddings and verification
- **JWT Token Management**: Secure session management with JWT tokens

### 🤖 AI-Powered Chat System
- **Azure OpenAI Integration**: Powered by Azure OpenAI models for intelligent conversations
- **Enterprise-Grade Security**: Benefit from Azure's enterprise security and compliance
- **RAG (Retrieval-Augmented Generation)**: Answers questions based on uploaded documents
- **Multi-Prompt Routing**: Supports different conversation modes (summarization, MCQ generation)
- **User-Specific Context**: Each user has their own document collection and chat context
- **Scalable Cloud Infrastructure**: No need for local GPU hardware

### 📚 Document Management
- **PDF Processing**: Upload and process PDF documents for AI knowledge base
- **ChromaDB Vector Storage**: Efficient vector storage for document embeddings
- **User-Specific Collections**: Each user has their own document collection
- **Intelligent Search**: Semantic search through uploaded documents

### 🛠️ Admin Interface
- **Web-based Admin Panel**: HTML interface for system administration
- **User Registration**: Register new users with face images
- **Data Management**: View and manage user data and collections
- **System Monitoring**: Monitor disk usage and database statistics

## Technical Architecture

### Core Technologies
- **FastAPI**: High-performance web framework for building APIs
- **ChromaDB**: Vector database for storing embeddings and documents
- **TinyDB**: Lightweight database for JWT token management
- **LangChain**: Framework for building AI applications with LLMs
- **OpenCV**: Computer vision library for image processing
- **Sentence Transformers**: For text embeddings

### Machine Learning Models
- **Azure OpenAI**: Large language models for conversational AI (GPT-4, GPT-3.5)
- **FaceNet**: Face recognition and embedding generation
- **MTCNN**: Multi-task CNN for face detection
- **Sentence Transformers**: all-MiniLM-L6-v2 for text embeddings

## Project Structure

```
mimir-api/
├── app/
│   ├── dependencies.py              # Main FastAPI application and dependencies
│   ├── admin/
│   │   ├── admin_functions.py       # Admin functionality (user registration, data management)
│   │   └── templates/               # Jinja2 templates for admin UI
│   │       ├── admin_login.html     # Admin login page
│   │       ├── user_registration.html # User registration form
│   │       ├── data_management.html # Data management interface
│   │       └── registration_success.html # Registration success page
│   ├── api/
│   │   ├── userlogin.py             # Face-based authentication endpoint
│   │   ├── userlogout.py            # User logout functionality
│   │   ├── userchat.py              # AI chat interface
│   │   └── userupload.py            # Document upload endpoint
│   └── utils/
│       ├── db.py                    # Database utilities (ChromaDB, TinyDB)
│       ├── chat_rag.py              # LLM and RAG functionality
│       ├── doc_ingest.py            # Document processing utilities
│       ├── jwt_utils.py             # JWT token utilities
│       └── mm_image_utils.py        # Image processing utilities
├── static/
│   ├── css/                         # CSS stylesheets
│   └── js/                          # JavaScript files
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

## Installation

### Prerequisites
- Python 3.8+
- Docker (optional, for containerized deployment)
- Azure OpenAI Service access and API key

### Setup

1. **Clone the repository:**
```bash
git clone https://github.com/dtyago/mimir-api.git
cd mimir-api
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables:**
```bash
export CHROMADB_LOC="/path/to/chromadb/data"
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
export AZURE_OPENAI_API_KEY="your-api-key"
export AZURE_OPENAI_API_VERSION="2024-02-01"
export AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4"
export EC_ADMIN_PWD="your_hashed_admin_password"
```

4. **Run the application:**
```bash
uvicorn app.dependencies:app --host 0.0.0.0 --port 8000
```

### Azure OpenAI Setup

1. **Create Azure OpenAI Resource:**
   - Go to the Azure Portal
   - Create a new Azure OpenAI resource
   - Deploy a model (e.g., GPT-4, GPT-3.5-turbo)
   - Note the endpoint URL and API key

2. **Configure Environment Variables:**
   ```bash
   # Your Azure OpenAI resource endpoint
   export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
   
   # Your Azure OpenAI API key
   export AZURE_OPENAI_API_KEY="your-api-key-here"
   
   # API version (use latest available)
   export AZURE_OPENAI_API_VERSION="2024-02-01"
   
   # Your deployment name (the name you gave when deploying the model)
   export AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4"
   ```

3. **Test the Configuration:**
   ```bash
   python -c "
   import os
   from langchain_openai import AzureChatOpenAI
   
   llm = AzureChatOpenAI(
       azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
       api_key=os.getenv('AZURE_OPENAI_API_KEY'),
       api_version=os.getenv('AZURE_OPENAI_API_VERSION'),
       deployment_name=os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')
   )
   
   response = llm.invoke('Hello, how are you?')
   print(response.content)
   "
   ```

## API Endpoints

### Authentication
- `POST /user/login` - Face-based user authentication
- `POST /user/logout` - User logout

### Chat & Documents
- `POST /user/chat` - Chat with AI assistant
- `POST /user/upload` - Upload PDF documents

### Admin Interface
- `GET /` - Admin login page
- `POST /admin/login` - Admin authentication
- `GET /admin/register_user` - User registration page
- `POST /admin/register_user` - Register new user
- `GET /admin/data_management` - Data management interface
- `POST /admin/delete_faces` - Delete all user data

## Usage Examples

### User Authentication
```python
# Upload face image for authentication
files = {'file': open('user_face.jpg', 'rb')}
response = requests.post('http://localhost:8000/user/login', files=files)
token = response.json()['access_token']
```

### Chat with AI
```python
headers = {'Authorization': f'Bearer {token}'}
data = {'user_input': 'Explain machine learning concepts from my uploaded documents'}
response = requests.post('http://localhost:8000/user/chat', json=data, headers=headers)
```

### Document Upload
```python
headers = {'Authorization': f'Bearer {token}'}
files = {'file': open('document.pdf', 'rb')}
response = requests.post('http://localhost:8000/user/upload', files=files, headers=headers)
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CHROMADB_LOC` | ChromaDB data directory | Required |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI service endpoint | Required |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key | Required |
| `AZURE_OPENAI_API_VERSION` | Azure OpenAI API version | 2024-02-01 |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | Azure OpenAI deployment name | gpt-4 |
| `EC_ADMIN_PWD` | Hashed admin password | Required |

## Security Features

- **Face Recognition**: Biometric authentication using FaceNet embeddings
- **JWT Tokens**: Secure session management with expiration
- **Input Validation**: Comprehensive input validation and sanitization
- **CORS Configuration**: Configurable CORS settings for web security
- **Admin Authentication**: Separate admin authentication system

## Migration from LLaMA to Azure OpenAI

This project has been refactored to use Azure OpenAI instead of local LLaMA models. Key benefits include:

### Benefits of Azure OpenAI
- **No Local GPU Required**: Eliminates the need for expensive GPU hardware
- **Enterprise Security**: Built-in security and compliance features
- **Better Performance**: Faster response times and higher throughput
- **Automatic Scaling**: Handles traffic spikes automatically
- **Multiple Models**: Access to GPT-4, GPT-3.5, and other cutting-edge models
- **Cost Efficiency**: Pay-per-use pricing model

### Migration Steps
If you're migrating from a LLaMA-based setup:

1. **Remove LLaMA Dependencies:**
   ```bash
   pip uninstall torch sentencepiece
   ```

2. **Install Azure OpenAI Dependencies:**
   ```bash
   pip install openai langchain-openai
   ```

3. **Update Environment Variables:**
   - Remove: `MODEL_PATH`
   - Add: `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_API_VERSION`, `AZURE_OPENAI_DEPLOYMENT_NAME`

4. **Test the Migration:**
   Run the application and verify that chat functionality works correctly.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Azure OpenAI**: For providing enterprise-grade AI capabilities
- **LangChain**: For providing the framework for building AI applications
- **ChromaDB**: For efficient vector storage and retrieval
- **FaceNet**: For face recognition capabilities
- **MTCNN**: For face detection
- **FastAPI**: For the high-performance web framework

## Support

For support, please open an issue on the GitHub repository or contact the maintainers.

---

**Note**: This project has been updated to use Azure OpenAI instead of local LLaMA models, providing better performance, enterprise-grade security, and eliminating the need for local GPU hardware. The migration ensures better scalability and reliability for production deployments.
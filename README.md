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

## 🚀 Deployment Options

### **Development Environment**

#### Option 1: DevContainer (Recommended for VS Code)
```bash
# Universal startup script - auto-detects environment
./start.sh
```

#### Option 2: Local Development
```bash
# Universal startup script - auto-detects environment
./start.sh
```

#### Option 3: Manual Development
```bash
# Load environment variables and start manually
source .env
uvicorn app.dependencies:app --host 0.0.0.0 --port 8000 --reload
```

### **Production Environment**

#### Option 1: Azure App Service (Recommended for Production)
```bash
# Automated Azure deployment
./deploy-azure.sh

# Configuration management
./azure-config.sh
```

#### Option 2: Docker Deployment
```bash
# Build and deploy with Docker Compose
docker-compose up --build -d

# View logs
docker-compose logs -f mimir-api
```

#### Option 3: Local Production
```bash
# Universal startup script - auto-detects environment
./start.sh
```

### **🔷 Azure App Service Deployment**

Azure App Service provides enterprise-grade hosting with automatic scaling, integrated security, and managed infrastructure.

#### Prerequisites for Azure Deployment
- Azure subscription
- Azure CLI installed (`az --version`)
- Azure OpenAI resource created
- GitHub repository (for CI/CD)

#### Quick Azure Deployment
1. **Configure your environment:**
   ```bash
   # Update .env.azure with your credentials
   cp .env.azure .env.azure.local
   # Edit .env.azure.local with your actual values
   ```

2. **Deploy to Azure:**
   ```bash
   # Login to Azure
   az login
   
   # Deploy the application
   ./deploy-azure.sh
   ```

3. **Manage your deployment:**
   ```bash
   # Configuration helper
   ./azure-config.sh
   ```

#### Azure App Service Features
- **Automatic Scaling**: Handles traffic spikes automatically
- **Integrated Security**: Built-in SSL and authentication
- **Monitoring**: Application Insights integration
- **CI/CD**: GitHub Actions workflow included
- **Custom Domains**: SSL certificate support
- **Health Checks**: Built-in monitoring endpoint

#### Azure URLs
- **Production App**: `https://mimir-api-prod.azurewebsites.net`
- **Health Check**: `https://mimir-api-prod.azurewebsites.net/health`
- **Admin Interface**: `https://mimir-api-prod.azurewebsites.net`

### **📊 GitHub Actions CI/CD**

Automated deployment pipeline is configured in `.github/workflows/azure-deploy.yml`:

1. **Set up GitHub Secrets:**
   - `AZURE_OPENAI_ENDPOINT`
   - `AZURE_OPENAI_API_KEY`
   - `AZURE_OPENAI_API_VERSION`
   - `AZURE_OPENAI_DEPLOYMENT_NAME`
   - `AZURE_WEBAPP_PUBLISH_PROFILE`

2. **Automatic Deployment:**
   - Triggers on push to `main` branch
   - Runs tests and health checks
   - Deploys to Azure App Service
   - Validates deployment with health check

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

## Quick Start

### Option 1: DevContainer (Recommended)
The easiest way to get started is using VS Code with DevContainer:

1. **Prerequisites:** Install VS Code and Docker Desktop
2. **Open:** Open the project in VS Code
3. **Reopen in Container:** When prompted, select "Reopen in Container"
4. **Wait:** Let VS Code build the development container (first time only)
5. **Start:** Run the application:
   ```bash
   ./start.sh
   ```
6. **Access:** Open http://localhost:8000 in your browser

**Benefits:**
- ✅ All dependencies pre-installed
- ✅ SQLite compatibility handled automatically
- ✅ Data persists between container restarts
- ✅ Consistent development environment

**⚠️ Note:** GitHub Codespaces is not recommended due to SQLite version limitations. Use local DevContainer or Docker Compose instead.

### Option 2: Docker Compose
For a quick Docker-based setup:

1. **Prerequisites:** Install Docker Desktop
2. **Run:**
   ```bash
   git clone https://github.com/dtyago/mimir-api.git
   cd mimir-api
   docker-compose up --build
   ```
3. **Access:** Open http://localhost:8000 in your browser

### Option 3: Local Development
For local development without Docker:

1. **Clone and setup:**
   ```bash
   git clone https://github.com/dtyago/mimir-api.git
   cd mimir-api
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure:** Copy `.env.example` to `.env` and set your Azure OpenAI credentials

3. **Start:** Run the application:
   ```bash
   ./start.sh
   ```

### Option 3: Docker Production
For production deployment:

```bash
docker build -t mimir-api .
docker run -p 8000:8000 --env-file .env mimir-api
```

### First Steps After Startup
1. **Admin Access:** Go to http://localhost:8000/admin
2. **Register Users:** Use the admin interface to register users with face images
3. **Upload Documents:** Users can upload PDFs for AI knowledge base
4. **Start Chatting:** Users can authenticate with face recognition and chat with AI

## Environment Variables

### **Development Environment**
Configure these in your `.env` file:

| Variable | Description | Example |
|----------|-------------|---------|
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI service endpoint | `https://mimir-base.openai.azure.com/` |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key | `G7u29wUa...` |
| `AZURE_OPENAI_API_VERSION` | Azure OpenAI API version | `2024-12-01-preview` |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | Azure OpenAI deployment name | `gpt-4o` |
| `CHROMADB_LOC` | ChromaDB data directory | `/workspaces/mimir-api/data/chromadb` |
| `EC_ADMIN_PWD` | Hashed admin password | `$2b$12$...` |
| `JWT_SECRET_KEY` | JWT signing key | `WWjndJ4E...` |

### **Azure App Service Environment**
Configure these in Azure Portal > App Service > Configuration:

| Variable | Description | Azure Value |
|----------|-------------|-------------|
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI service endpoint | `https://mimir-base.openai.azure.com/` |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key | Your actual API key |
| `AZURE_OPENAI_API_VERSION` | Azure OpenAI API version | `2024-12-01-preview` |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | Azure OpenAI deployment name | `gpt-4o` |
| `CHROMADB_LOC` | ChromaDB data directory | `/tmp/chromadb` |
| `EC_ADMIN_PWD` | Hashed admin password | Your hashed password |
| `JWT_SECRET_KEY` | JWT signing key | Your JWT secret |
| `APP_ENV` | Application environment | `production` |
| `SCM_DO_BUILD_DURING_DEPLOYMENT` | Build during deployment | `true` |

### **Environment Setup Helper**
```bash
# Generate hashed admin password
python -c "import bcrypt; print(bcrypt.hashpw(b'your_password', bcrypt.gensalt()).decode())"

# Generate JWT secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 🛠️ Development Tools

### **Setup Scripts**
- **`start.sh`** - Universal startup script (auto-detects environment)

### **Azure Deployment Tools**
- **`deploy-azure.sh`** - Automated Azure App Service deployment
- **`azure-config.sh`** - Azure App Service configuration management
- **`startup.py`** - Azure App Service startup script
- **`startup.sh`** - Bash startup script for Azure

### **Testing Tools**
- **Health Check Endpoint**: `/health` - Application health monitoring

### **Configuration Files**
- **`.env`** - Development environment variables
- **`.env.azure`** - Azure App Service environment template
- **`.env.example`** - Environment variables template
- **`web.config`** - IIS configuration for Azure App Service
- **`Dockerfile`** - Docker container configuration
- **`docker-compose.yml`** - Docker Compose for local deployment

### **CI/CD Pipeline**
- **`.github/workflows/azure-deploy.yml`** - GitHub Actions workflow for Azure deployment

## 📋 Project Structure

```
mimir-api/
├── app/                            # Application source code
│   ├── dependencies.py            # Main FastAPI app and dependencies
│   ├── admin/                      # Admin interface
│   │   ├── admin_functions.py     # Admin functionality
│   │   └── templates/              # Jinja2 templates
│   ├── api/                        # API endpoints
│   │   ├── userlogin.py           # Face authentication
│   │   ├── userlogout.py          # User logout
│   │   ├── userchat.py            # AI chat interface
│   │   └── userupload.py          # Document upload
│   └── utils/                      # Utility modules
│       ├── db.py                  # Database utilities
│       ├── chat_rag.py            # AI chat and RAG
│       ├── doc_ingest.py          # Document processing
│       ├── jwt_utils.py           # JWT token utilities
│       └── mm_image_utils.py      # Image processing
├── static/                         # Static files (CSS, JS)
├── data/                          # Application data (created at runtime)
│   ├── chromadb/                  # Vector database storage
│   ├── uploads/                   # Processed uploads
│   ├── tmp/                       # Temporary files
│   └── logs/                      # Application logs
├── .github/workflows/             # GitHub Actions CI/CD
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Docker configuration
├── docker-compose.yml            # Docker Compose configuration
├── start.sh                      # Universal startup script
├── startup.sh                    # Azure startup wrapper
├── startup.py                    # Azure startup Python script
├── deploy-azure.sh               # Azure deployment script
├── azure-config.sh               # Azure configuration helper
├── .env*                         # Environment configuration files
├── DEPLOYMENT.md                 # Deployment documentation
├── AZURE_DEPLOYMENT.md           # Azure-specific deployment guide
└── README.md                     # This file
```

## 🔧 Troubleshooting

### **Common Issues**

#### **Azure OpenAI Connection Issues**
```bash
# Check environment variables
python -c "import os; print(os.getenv('AZURE_OPENAI_ENDPOINT'))"

# Test the health endpoint
curl http://localhost:8000/health
```

#### **Port Already in Use**
```bash
# Kill processes on port 8000
sudo lsof -ti:8000 | xargs sudo kill -9
```

#### **Dependencies Issues**
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Or rebuild the Docker container
docker-compose up --build
```

#### **Azure Deployment Issues**
```bash
# Check Azure CLI login
az account show

# View deployment logs
az webapp log tail --name mimir-api-prod --resource-group rg-mimir-api

# Restart the application
az webapp restart --name mimir-api-prod --resource-group rg-mimir-api
```

### **Debug Commands**
```bash
# Check application health
curl http://localhost:8000/health

# View local logs
tail -f data/logs/mimir-api.log

# Test face detection
python -c "from app.utils.mm_image_utils import detect_faces_with_mtcnn; print('Face detection working')"
```

## 📊 Monitoring and Maintenance

### **Health Monitoring**
- **Local**: `http://localhost:8000/health`
- **Azure**: `https://mimir-api-prod.azurewebsites.net/health`

### **Log Management**
- **Local Logs**: `data/logs/mimir-api.log`
- **Azure Logs**: Available in Azure Portal > App Service > Log stream

### **Performance Monitoring**
- **Azure Application Insights**: Integrated monitoring and analytics
- **GitHub Actions**: Automated deployment and health checks

### **Backup and Recovery**
- **Database**: ChromaDB data in `data/chromadb/`
- **User Data**: Face embeddings and documents in `data/`
- **Configuration**: Environment variables and settings

## 🎯 Best Practices

### **Development**
- Use `./start-devcontainer.sh` for consistent development environment
- Test Azure OpenAI connection before deployment
- Keep environment variables secure and never commit to version control

### **Production**
- Use Azure App Service for scalable production deployment
- Enable Application Insights for monitoring
- Set up auto-scaling based on traffic
- Use Azure Key Vault for sensitive configuration

### **Security**
- Rotate API keys regularly
- Use managed identities where possible
- Enable HTTPS/SSL for all endpoints
- Monitor access patterns and unusual activity

### **Maintenance**
- Regular dependency updates
- Monitor resource usage and costs
- Set up automated backups
- Test disaster recovery procedures

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

## 🔒 Security Features

- **Face Recognition**: Biometric authentication using FaceNet embeddings
- **JWT Tokens**: Secure session management with expiration
- **Input Validation**: Comprehensive input validation and sanitization
- **CORS Configuration**: Configurable CORS settings for web security
- **Admin Authentication**: Separate admin authentication system
- **Azure Security**: Enterprise-grade security with Azure App Service
- **Environment Variables**: Secure configuration management
- **API Key Protection**: Encrypted storage of sensitive credentials

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Mimir API Architecture                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │   Web UI    │    │   Mobile    │    │   API       │         │
│  │  (Admin)    │    │    App      │    │  Clients    │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│           │                │                    │               │
│           └────────────────┼────────────────────┘               │
│                           │                                    │
│  ┌─────────────────────────┼─────────────────────────────────┐  │
│  │                    FastAPI                                │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │  │
│  │  │    Auth     │  │    Chat     │  │   Upload    │      │  │
│  │  │  (Face ID)  │  │   (RAG)     │  │   (PDF)     │      │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘      │  │
│  └─────────────────────────────────────────────────────────┘  │
│                           │                                    │
│  ┌─────────────────────────┼─────────────────────────────────┐  │
│  │                   AI Services                            │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │  │
│  │  │ Azure OpenAI│  │   FaceNet   │  │   MTCNN     │      │  │
│  │  │   (GPT-4)   │  │ (Embedding) │  │(Detection)  │      │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘      │  │
│  └─────────────────────────────────────────────────────────┘  │
│                           │                                    │
│  ┌─────────────────────────┼─────────────────────────────────┐  │
│  │                   Data Layer                             │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │  │
│  │  │  ChromaDB   │  │   TinyDB    │  │ File System │      │  │
│  │  │  (Vector)   │  │   (JWT)     │  │   (Temp)    │      │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘      │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## 🌐 API Reference

### **Authentication Endpoints**
- **POST** `/user/login` - Authenticate user with face image
- **POST** `/user/logout` - Logout current user

### **Chat Endpoints**
- **POST** `/user/chat` - Chat with AI assistant (requires auth)

### **Document Management**
- **POST** `/user/upload` - Upload PDF documents (requires auth)

### **Admin Endpoints**
- **GET** `/` - Admin login page
- **POST** `/admin/login` - Admin authentication
- **GET** `/admin/register_user` - User registration form
- **POST** `/admin/register_user` - Register new user
- **GET** `/admin/data_management` - Data management interface
- **POST** `/admin/delete_faces` - Delete all user data

### **System Endpoints**
- **GET** `/health` - Health check endpoint

### **Request/Response Examples**

#### User Authentication
```bash
curl -X POST "http://localhost:8000/user/login" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@user_face.jpg"
```

#### Chat with AI
```bash
curl -X POST "http://localhost:8000/user/chat" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_input": "Explain machine learning concepts"}'
```

#### Document Upload
```bash
curl -X POST "http://localhost:8000/user/upload" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf"
```

## 📈 Performance Optimization

### **Development Settings**
- Single worker process
- Auto-reload enabled
- Debug logging
- Local file storage

### **Production Settings**
- Multiple worker processes (4)
- Production-grade logging
- Optimized for Azure App Service
- Persistent storage solutions

### **Azure App Service Optimization**
- **Auto-scaling**: Automatic horizontal scaling
- **Application Insights**: Performance monitoring
- **CDN Integration**: Static file optimization
- **Connection Pooling**: Database connection optimization

## 📚 Additional Resources

### **Documentation**
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - General deployment guide
- **[AZURE_DEPLOYMENT.md](AZURE_DEPLOYMENT.md)** - Azure-specific deployment
- **[Azure App Service Documentation](https://docs.microsoft.com/en-us/azure/app-service/)**
- **[Azure OpenAI Documentation](https://docs.microsoft.com/en-us/azure/cognitive-services/openai/)**

### **Development Tools**
- **[VS Code Dev Containers](https://code.visualstudio.com/docs/remote/containers)**
- **[FastAPI Documentation](https://fastapi.tiangolo.com/)**
- **[LangChain Documentation](https://python.langchain.com/)**

### **AI/ML Resources**
- **[FaceNet Paper](https://arxiv.org/abs/1503.03832)**
- **[MTCNN Paper](https://arxiv.org/abs/1604.02878)**
- **[ChromaDB Documentation](https://docs.trychroma.com/)**

## 🤝 Contributing

### **Development Workflow**
1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Set up development environment**
   ```bash
   # Use the universal startup script
   ./start.sh
   ```
4. **Make your changes and test**
   ```bash
   # Test the health endpoint
   curl http://localhost:8000/health
   ```
5. **Commit your changes**
   ```bash
   git commit -m 'Add amazing feature'
   ```
6. **Push to the branch**
   ```bash
   git push origin feature/amazing-feature
   ```
7. **Open a Pull Request**

### **Code Standards**
- Follow PEP 8 for Python code
- Use type hints where appropriate
- Add docstrings to functions and classes
- Include unit tests for new features
- Update documentation for API changes

### **Testing**
- Test Azure OpenAI integration
- Verify face recognition functionality
- Test file upload and processing
- Ensure proper error handling

## 📞 Support

### **Getting Help**
- **GitHub Issues**: Report bugs and request features
- **Documentation**: Check DEPLOYMENT.md and AZURE_DEPLOYMENT.md
- **Health Check**: Use `/health` endpoint for debugging

### **Common Support Topics**
- Azure OpenAI configuration
- Face recognition setup
- Deployment issues
- Performance optimization

For support, please open an issue on the GitHub repository with:
- Clear description of the problem
- Steps to reproduce
- Environment details (development/production)
- Error messages and logs

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Azure OpenAI**: For providing enterprise-grade AI capabilities
- **LangChain**: For the AI application framework
- **ChromaDB**: For efficient vector storage and retrieval
- **FaceNet**: For face recognition capabilities
- **MTCNN**: For face detection technology
- **FastAPI**: For the high-performance web framework
- **Microsoft Azure**: For cloud infrastructure and services

---

**✨ Ready to Deploy!** Your Mimir API is now fully configured with Azure OpenAI integration and ready for both development and production deployment on Azure App Service.

**🚀 Quick Start**: `./start.sh` (Universal) or `./deploy-azure.sh` (Production)
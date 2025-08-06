# Mimir AI

## Overview

Mimir AI is a modern FastAPI-based conversational platform that combines AI-powered chat capabilities with facial recognition authentication. The system enables secure, biometric user authentication and intelligent document-based conversations powered by Azure OpenAI and Retrieval-Augmented Generation (RAG).

## ✨ Key Features

### 🔐 Facial Recognition Authentication
- **Biometric Login**: Secure authentication using facial recognition instead of passwords
- **FaceNet + MTCNN**: Advanced face detection and embedding generation
- **JWT Security**: Secure session management with token-based authentication
- **Multi-Role Support**: Environment-configurable user roles for any domain

### 🤖 Enhanced AI-Powered Chat with Multi-Source RAG
- **Azure OpenAI GPT-4o**: Enterprise-grade conversational AI
- **Enhanced RAG System**: Multi-source data integration for intelligent responses
- **Role-Specific Context**: Personalized AI responses based on user roles and permissions
- **Document-Aware Responses**: AI answers questions based on uploaded documents
- **User-Specific Context**: Personalized document collections per user
- **Vector Search**: Intelligent semantic search through document content
- **Data Source Integration**: Common knowledge, data marts, and role-specific collections

### 🎯 Generic Framework Architecture
- **Environment-Driven Configuration**: Deploy in any domain via .env settings
- **Dynamic Role Management**: Configure unlimited roles through MIMIR_ROLES variable
- **Domain-Agnostic Design**: Healthcare, education, gaming, corporate, or custom domains
- **Scalable Test Framework**: Test suites automatically adapt to configured roles
- **Flexible Deployment**: Same codebase works across different use cases

### 📚 Document Processing
- **PDF Upload & Processing**: Automatic document ingestion and vectorization
- **ChromaDB Storage**: Efficient vector database for embeddings
- **Contextual Retrieval**: Smart document retrieval for enhanced AI responses

### 🛠️ Admin Management
- **Web Interface**: User-friendly admin panel for system management
- **User Registration**: Secure face-based user onboarding
- **Data Management**: Comprehensive user and document administration

## 🏗️ Technical Stack

### **Core Framework**
- **FastAPI**: High-performance async web framework
- **Uvicorn**: ASGI server for production deployment
- **Python 3.12**: Modern Python with type hints

### **AI & Machine Learning**
- **Azure OpenAI GPT-4o**: Advanced language model for conversations
- **FaceNet**: Deep learning model for facial recognition
- **MTCNN**: Multi-task CNN for face detection
- **LangChain**: Framework for AI application development
- **HuggingFace Transformers**: Text embedding models

### **Data Storage**
- **ChromaDB**: Vector database for document embeddings
- **TinyDB**: Lightweight database for JWT token management
- **File System**: Secure document and image storage

## 📁 Project Structure

```
mimir-ai/
├── app/                            # Application source code
│   ├── main.py                     # FastAPI main application entry
│   ├── dependencies.py             # Dependency injection and configuration
│   ├── admin/                      # Admin interface modules
│   │   ├── admin_functions.py      # Admin authentication and management
│   │   └── templates/              # Jinja2 HTML templates
│   │       ├── admin_login.html    # Admin login page
│   │       ├── user_registration.html  # User registration form
│   │       ├── data_management.html    # Data management interface
│   │       └── registration_success.html  # Success confirmation
│   ├── api/                        # API endpoint modules
│   │   ├── userlogin.py           # Facial recognition authentication
│   │   ├── userlogout.py          # User session termination
│   │   ├── userchat.py            # AI chat with RAG
│   │   └── userupload.py          # Document upload processing
│   └── utils/                      # Utility modules
│       ├── chat_rag.py            # RAG implementation with Azure OpenAI
│       ├── db.py                  # Database connection helpers
│       ├── doc_ingest.py          # Document processing pipeline
│       ├── jwt_utils.py           # JWT token management
│       ├── mm_image_utils.py      # Face detection and processing
│       └── sqlite_compat.py      # SQLite version compatibility
├── static/                         # Static web assets
│   ├── css/mvp.css                # Clean CSS framework
│   └── js/script.js               # JavaScript functionality
├── data/                          # Application data (runtime generated)
│   ├── chromadb/                  # Vector database storage
│   ├── uploads/                   # Processed document uploads
│   ├── tmp/                       # Temporary processing files
│   └── logs/                      # Application logs
├── test/                          # Test files and sample data
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Container configuration
├── docker-compose.yml            # Local development stack
├── start.sh                      # Universal startup script
├── startup.py                    # Azure App Service startup
└── deploy-container-to-azure.sh  # Azure deployment automation
```

## 🚀 Quick Start

### Prerequisites
- **Azure OpenAI Access**: Active Azure subscription with OpenAI service
- **Python 3.12+**: Modern Python environment
- **Docker** (optional): For containerized development

### Option 1: DevContainer (Recommended)
Perfect for VS Code users with consistent development environment:

```bash
git clone https://github.com/dtyago/mimir-ai.git
cd mimir-ai
code .
# VS Code will prompt to "Reopen in Container" - click it
# Wait for container build, then:
./start.sh
```

### Option 2: Local Development
For direct local development:

```bash
git clone https://github.com/dtyago/mimir-ai.git
cd mimir-ai
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env      # Configure your Azure OpenAI credentials
./start.sh
```

### Option 3: Docker Compose
For containerized local development:

```bash
git clone https://github.com/dtyago/mimir-ai.git
cd mimir-ai
docker-compose up --build
```

### First Steps
1. **Configure Environment**: Set your Azure OpenAI credentials in `.env`
2. **Access Admin**: Navigate to `http://localhost:8000`
3. **Register Users**: Use admin interface to add users with face photos
4. **Test Login**: Users can authenticate with facial recognition
5. **Upload Documents**: Add PDFs for AI knowledge base
6. **Start Chatting**: Experience document-aware AI conversations

## ⚙️ Configuration

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI service URL | `https://your-resource.openai.azure.com/` |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key | `your-api-key-here` |
| `AZURE_OPENAI_API_VERSION` | API version | `2024-12-01-preview` |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | Model deployment name | `gpt-4o` |
| `EC_ADMIN_PWD` | Hashed admin password | Generate with bcrypt |
| `JWT_SECRET_KEY` | JWT signing secret | Generate with `secrets.token_urlsafe(32)` |
| `CHROMADB_LOC` | Vector database path | `./data/chromadb` |
| `MIMIR_ROLES` | Comma-separated user roles | `doctor,nurse,admin` or `analyst,leadership` |
| `DEFAULT_ROLE` | Default role for users | `human` |
| `L2_FACE_THRESHOLD` | Face recognition threshold | `0.6` (lower = stricter) |

### Role Configuration Examples

The framework adapts to any domain through environment configuration:

```bash
# Healthcare Environment
MIMIR_ROLES=doctor,nurse,administrator,patient
DEFAULT_ROLE=human

# Education Environment  
MIMIR_ROLES=teacher,student,administrator,parent
DEFAULT_ROLE=human

# Gaming/Analytics Environment
MIMIR_ROLES=analyst-gaming,analyst-non-gaming,leadership-gaming,leadership-non-gaming
DEFAULT_ROLE=human

# Corporate Environment
MIMIR_ROLES=employee,manager,executive,contractor
DEFAULT_ROLE=human

# Simple/Generic Environment
MIMIR_ROLES=human
DEFAULT_ROLE=human
```

### Generate Secure Credentials
```bash
# Generate admin password hash
python -c "import bcrypt; print(bcrypt.hashpw(b'your_password', bcrypt.gensalt()).decode())"

# Generate JWT secret
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 🌐 API Reference

### **Core Endpoints**

#### Authentication
- `POST /user/login` - Facial recognition authentication
  - **Input**: Face image file (multipart/form-data)
  - **Output**: JWT access token
- `POST /user/logout` - User session termination
  - **Input**: JWT token (Authorization header)
  - **Output**: Logout confirmation

#### AI Chat & Documents
- `POST /user/chat` - Enhanced conversational AI with multi-source document context
  - **Input**: User message + JWT token + enhanced_rag flag
  - **Output**: AI response with document references and data source information
  - **Features**: Role-specific responses, multi-source data integration
- `POST /user/upload` - PDF document upload and processing
  - **Input**: PDF file + JWT token
  - **Output**: Upload confirmation and processing status
- `POST /user/chat/data-sources` - Get available data sources for user role
  - **Input**: JWT token
  - **Output**: List of enabled data sources for the user's role

#### Admin Interface
- `GET /` - Admin login page
- `POST /admin/login` - Admin authentication
- `GET /admin/register_user` - User registration interface
- `POST /admin/register_user` - Create new user with face image
- `GET /admin/data_management` - System administration panel

#### System
- `GET /health` - Application health status

### **Usage Examples**

#### User Authentication
```bash
curl -X POST "http://localhost:8000/user/login" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@user_face.jpg"
```

#### Enhanced AI Chat
```bash
# Traditional RAG
curl -X POST "http://localhost:8000/user/chat" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_input": "Explain the key concepts from my uploaded documents", "use_enhanced_rag": false}'

# Enhanced RAG with multi-source integration
curl -X POST "http://localhost:8000/user/chat" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_input": "What analytics best practices should I follow?", "use_enhanced_rag": true}'

# Check available data sources for role
curl -X POST "http://localhost:8000/user/chat/data-sources" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### Document Upload
```bash
curl -X POST "http://localhost:8000/user/upload" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf"
```

## 🐳 Production Deployment

### Azure App Service (Recommended)
For enterprise-grade production deployment with automatic scaling:

```bash
# Clone and configure
git clone https://github.com/dtyago/mimir-ai.git
cd mimir-ai

# Configure Azure credentials
az login

# Set up environment configuration
cp .env.azure.example .env.azure
# Edit .env.azure with your Azure settings and credentials

# One-command deployment
./deploy-container-to-azure.sh
```

**What gets configured in `.env.azure`:**
```bash
# Azure Deployment Settings
RESOURCE_GROUP=your-resource-group
LOCATION="Canada Central"
APP_NAME=your-app-service-name
ACR_NAME=your-container-registry  # optional

# Application Settings
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
EC_ADMIN_PWD=your-bcrypt-hashed-password
JWT_SECRET_KEY=your-jwt-secret
```

**Deployment Features:**
- ✅ **Intelligent Resource Management**: Auto-detects existing Azure resources
- ✅ **Cloud-Based Building**: Uses Azure Container Registry (no local Docker needed)
- ✅ **Complete Configuration**: Deploys both infrastructure and application settings
- ✅ **Production Optimized**: Includes health checks, logging, and performance tuning
- ✅ **Secure by Default**: Proper authentication and environment variable management

**Quick Updates After Initial Deployment:**
```bash
# Code changes only (fast)
./qd.sh rebuild

# Configuration changes (full sync)
./deploy-container-to-azure.sh
```

**Security Best Practices:**
- **Never commit `.env.azure`** - Contains sensitive production secrets
- **Generate secure credentials**:
  ```bash
  # Admin password hash
  python -c "import bcrypt; print(bcrypt.hashpw(b'YourPassword123!', bcrypt.gensalt()).decode())"
  
  # JWT secret
  python -c "import secrets; print(secrets.token_urlsafe(64))"
  ```
- **Use Azure Key Vault** for additional security in production
- **Rotate credentials regularly**

For detailed Azure deployment instructions, see: **[AZURE_DEPLOYMENT.md](./AZURE_DEPLOYMENT.md)**

### Docker Production
For self-hosted production deployment:

```bash
# Production Docker build (Azure-optimized)
docker build -f Dockerfile.azure -t mimir-ai-prod .
docker run -d \
  --name mimir-ai \
  -p 8000:8000 \
  --env-file .env.production \
  --restart unless-stopped \
  mimir-ai-prod

# Development Docker build (DevContainer)
docker build -f Dockerfile -t mimir-ai-dev .
```

## 🔒 Security Features

- **Biometric Authentication**: Face-based user identification
- **JWT Token Security**: Secure session management with expiration
- **Azure Managed Identity**: Eliminates credential management in production
- **Input Validation**: Comprehensive request validation and sanitization
- **CORS Protection**: Configurable cross-origin request policies
- **Admin Access Control**: Separate administrative authentication
- **Secure File Handling**: Safe upload and processing pipelines

## 🎯 Framework Capabilities

### Generic Multi-Domain Framework
Mimir AI is designed as a **domain-agnostic framework** that can be deployed in any environment through simple configuration:

- **Healthcare**: `doctor,nurse,administrator,patient`
- **Education**: `teacher,student,administrator,parent`  
- **Gaming/Analytics**: `analyst-gaming,analyst-non-gaming,leadership-gaming,leadership-non-gaming`
- **Corporate**: `employee,manager,executive,contractor`
- **Generic**: `human` (default single-role deployment)

### Role-Based Intelligence
- **Dynamic Role Configuration**: Unlimited roles via `MIMIR_ROLES` environment variable
- **Role-Specific AI Responses**: AI adapts responses based on user's role and permissions
- **Access Control**: Role-based access to different data sources and knowledge bases
- **Test Framework Scalability**: Test suites automatically adapt to configured roles

### Enhanced RAG Architecture
- **Multi-Source Integration**: Common knowledge, data marts, role-specific collections
- **Conversation History**: Maintains context across chat sessions
- **User Documents**: Personal document collections per user
- **Data Source Transparency**: Shows which sources contributed to each response

## 🧪 Testing

The application includes comprehensive testing capabilities that adapt to your environment:

```bash
# Health check
curl http://localhost:8000/health

# Test all configured roles (adapts to MIMIR_ROLES)
python test/scripts/test_all_roles.py

# Test enhanced RAG system
python test/scripts/test_enhanced_rag.py

# Test comprehensive APIs
python test/scripts/test_comprehensive_apis.py
```

### Test Framework Features
- **Environment-Driven Testing**: Test suites read roles from your .env configuration
- **Dynamic Test Generation**: Number of tests scales with configured roles
- **Role-Specific Validation**: Verifies role isolation and permissions
- **Enhanced RAG Testing**: Validates multi-source data integration
- **100% Pass Rate**: All tests designed to work with any role configuration

## 🛠️ Development Tools

- **Universal Startup**: `./start.sh` auto-detects and configures environment (DevContainer/local)
- **Quick Azure Deploy**: `./qd.sh restart|rebuild` for fast Azure iteration cycles
- **Full Azure Deploy**: `./deploy-container-to-azure.sh` for complete environment setup
- **Health Monitoring**: Built-in `/health` endpoint for system status and diagnostics
- **Hot Reload**: Development mode with automatic code reloading
- **Containerized Dev**: DevContainer for consistent development environment
- **Dual Docker Strategy**: Separate optimized containers for development vs production

## 📚 Documentation

- **[DEPLOYMENT_SECURE.md](DEPLOYMENT_SECURE.md)** - Secure production deployment guide
- **[AZURE_DEPLOYMENT.md](AZURE_DEPLOYMENT.md)** - Azure-specific deployment instructions
- **[ENVIRONMENT_GUIDE.md](ENVIRONMENT_GUIDE.md)** - Environment configuration reference

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Set up development**: `./start.sh`
4. **Make changes and test**: `curl http://localhost:8000/health`
5. **Commit changes**: `git commit -m 'Add amazing feature'`
6. **Push and create PR**: `git push origin feature/amazing-feature`

### Code Standards
- Follow PEP 8 Python style guidelines
- Use type hints for all function parameters and returns
- Add comprehensive docstrings for public APIs
- Include unit tests for new functionality
- Update documentation for user-facing changes

## 📞 Support

For issues and questions:

1. **Check Health**: `curl http://localhost:8000/health`
2. **Review Logs**: Check `data/logs/` directory
3. **Open Issue**: Use GitHub Issues with:
   - Clear problem description
   - Steps to reproduce
   - Environment details
   - Error messages and logs

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Azure OpenAI**: Enterprise AI capabilities
- **LangChain**: AI application framework
- **ChromaDB**: Vector database technology
- **FaceNet & MTCNN**: Face recognition technology
- **FastAPI**: High-performance web framework
- **Microsoft Azure**: Cloud infrastructure

---

**🚀 Ready to Deploy!** 

- **Development**: `./start.sh` (local/DevContainer)
- **Quick Azure Deploy**: `./qd.sh rebuild` (fast iteration)
- **Full Azure Deploy**: `./deploy-container-to-azure.sh` (complete setup)
- **Health Check**: `http://localhost:8000/health` or your Azure URL
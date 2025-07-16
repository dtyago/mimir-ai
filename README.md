# Mimir API

## Overview

Mimir API is a FastAPI-based conversationa platform that combines AI-powered chat capabilities with face recognition authentication. The system allows users to authenticate using facial recognition, upload and process educational documents, and engage in intelligent conversations with an AI assistant powered by LLaMA models and Retrieval-Augmented Generation (RAG).

## Features

### 🔐 Face Recognition Authentication
- **Facial Login**: Users authenticate using their face images instead of traditional passwords
- **MTCNN Face Detection**: Utilizes MTCNN for accurate face detection and cropping
- **FaceNet Embeddings**: Leverages FaceNet for generating face embeddings and verification
- **JWT Token Management**: Secure session management with JWT tokens

### 🤖 AI-Powered Chat System
- **LLaMA Integration**: Powered by LLaMA models for intelligent conversations
- **RAG (Retrieval-Augmented Generation)**: Answers questions based on uploaded documents
- **Multi-Prompt Routing**: Supports different conversation modes (summarization, MCQ generation)
- **User-Specific Context**: Each user has their own document collection and chat context

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
- **LLaMA**: Large language model for conversational AI
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
- CUDA-compatible GPU (recommended for LLaMA model)

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
export MODEL_PATH="/path/to/llama/model.gguf"
export EC_ADMIN_PWD="your_hashed_admin_password"
```

4. **Run the application:**
```bash
uvicorn app.dependencies:app --host 0.0.0.0 --port 8000
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
| `MODEL_PATH` | Path to LLaMA model file | Required |
| `EC_ADMIN_PWD` | Hashed admin password | Required |

## Security Features

- **Face Recognition**: Biometric authentication using FaceNet embeddings
- **JWT Tokens**: Secure session management with expiration
- **Input Validation**: Comprehensive input validation and sanitization
- **CORS Configuration**: Configurable CORS settings for web security
- **Admin Authentication**: Separate admin authentication system

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **LangChain**: For providing the framework for building AI applications
- **ChromaDB**: For efficient vector storage and retrieval
- **FaceNet**: For face recognition capabilities
- **MTCNN**: For face detection
- **FastAPI**: For the high-performance web framework

## Support

For support, please open an issue on the GitHub repository or contact the maintainers.

---

**Note**: This is an educational project designed to demonstrate AI integration with face recognition authentication. Ensure proper security measures are in place before deploying in production environments.
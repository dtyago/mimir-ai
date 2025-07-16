# mimir-api
---
title: mimir-api
emoji: 🏆
colorFrom: red
colorTo: pink
sdk: docker
pinned: false
license: MIT License
---


```
**EduConnect/
├── app/
│   ├── __init__.py                  # Initializes the FastAPI app and global configurations
│   ├── main.py                      # Entry point for the FastAPI application, defining routes
│   ├── dependencies.py              # Dependency utilities for JWT token verification, etc.
│   ├── api/
│   │   ├── __init__.py
│   │   ├── userlogin.py             # Endpoint for user login functionality
│   │   ├── userlogout.py            # Endpoint for user logout functionality
│   │   ├── userchat.py              # Endpoint for chat functionality
│   │   └── userupload.py            # Endpoint for file upload functionality
│   ├── admin/
│   │   ├── __init__.py
│   │   ├── admin_functions.py       # Contains server-side logic for admin tasks
│   │   └── templates/               # Jinja2 templates for admin UI
│   │       ├── admin_login.html     # Template for admin login page
│   │       └── user_registration.html # Template for user registration page
│   └── utils/
│       ├── __init__.py
│       ├── db.py                    # Centraized DB functions for ChromaDB collections, TinyDB
│       ├── chat_rag.py              # LLM chat function with RAG from vector DB
│       ├── doc_ingest.py            # Utility to ingest pdf documents into vector DB
│       ├── jwt_utils.py             # Utility for JWT tokens
│       └── ec_image_utils.py        # Integrates MTCNN and Facenet for login authentication
├── static/
│   ├── css/                         # CSS for the administration portal
│   ├── js/                          # Javascripts if any for administration portal
│   └── images/                      # UI rendering images for administration page
├── requirements.txt                 # Lists all Python library dependencies
├── .env                             # Environment variables for configuration settings**
└── docs/                            # Project Documents (ONLY MARKDOWNs and UML diagrams)
```
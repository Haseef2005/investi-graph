# Investi-Graph Backend 🚀

**AI-Powered Financial Document Analysis Backend API**

Investi-Graph is a backend service built with FastAPI that provides RAG (Retrieval-Augmented Generation) capabilities for analyzing financial documents. This backend includes JWT authentication, asynchronous file processing, vector embeddings, and knowledge graph generation.

## 🏗️ Architecture

**Backend API Service** (This Repository)
- FastAPI with async support
- JWT Authentication
- PostgreSQL + pgvector for vector storage 
- Neo4j for knowledge graphs
- Background processing pipeline
- Docker containerization

## ✨ Features

- 🔐 **JWT Authentication** - Secure API access with passlib[argon2] and python-jose
- 📄 **Document Processing** - Async PDF/TXT upload with immediate API response
- 🤖 **AI Pipeline** - Extract → Chunk → Embed → Store workflow
- 🔍 **Vector Search** - pgvector-powered similarity search
- 💬 **RAG Querying** - LLM-powered document Q&A via Groq/Llama 3
- 📊 **Knowledge Graphs** - Neo4j integration for relationship mapping
- 🐳 **Containerized** - Full Docker Compose setup
- 🔄 **Database Migrations** - Alembic schema management

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **API Framework** | FastAPI (async) |
| **Database** | PostgreSQL 15 + pgvector |
| **Graph DB** | Neo4j |
| **ORM** | SQLAlchemy (async) |
| **Authentication** | JWT (python-jose) + Argon2 |
| **LLM Provider** | Groq via litellm |
| **Embeddings** | sentence-transformers |
| **Containers** | Docker + Docker Compose |
| **Migrations** | Alembic |

## 🚀 Quick Start

### Prerequisites
- Docker Desktop
- Git
- Groq API Key ([Get one here](https://console.groq.com/keys))

### 1. Clone Repository
```bash
git clone https://github.com/[Your-Username]/investi-graph.git
cd investi-graph
```

### 2. Create Environment File
Create a `.env` file in the project root:

```env
# Project Settings
PROJECT_NAME="Investi-Graph"

# JWT Configuration (generate with: openssl rand -hex 32)
JWT_SECRET_KEY="819a30a0bdd36693dea696ea47169899e2b3f3f4ceb2f97ae037981abc57c609"
JWT_ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database Configuration (for Docker Compose)
DATABASE_USER=postgres
DATABASE_PASSWORD=mysecretpassword
DATABASE_NAME=postgres
DATABASE_HOST=db
DATABASE_PORT=5432
DATABASE_URL="postgresql+psycopg://${DATABASE_USER}:${DATABASE_PASSWORD}@${DATABASE_HOST}:${DATABASE_PORT}/${DATABASE_NAME}"

# LLM Configuration
LLM_PROVIDER="groq"
LLM_API_KEY="gsk_your_groq_api_key_here"

# Neo4j Graph Database
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=mysecretneo4jpassword
```

### 3. Start Services
```bash
# Build and start all services
docker-compose up --build -d

# Check if services are running
docker-compose ps
```

### 4. Initialize Database
```bash
# Run database migrations
docker-compose exec app alembic upgrade head
```

### 5. Verify Installation
- **API Documentation**: http://localhost:8000/docs
- **Neo4j Browser**: http://localhost:7474 (neo4j/mysecretneo4jpassword)
- **Health Check**: http://localhost:8000/health

## 📚 API Usage

### Authentication Flow
1. **Register User**: `POST /users/`
2. **Get Token**: `POST /token`
3. **Use Token**: Include `Authorization: Bearer <token>` in headers

### Document Processing Flow
1. **Upload Document**: `POST /documents/`
2. **Monitor Processing**: `GET /documents/{doc_id}`
3. **Query Chunks**: `GET /documents/{doc_id}/chunks`
4. **RAG Search**: `POST /documents/search`

### Example API Calls
```bash
# Register new user
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "secretpassword"}'

# Login to get token
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=secretpassword"

# Upload document (requires auth token)
curl -X POST "http://localhost:8000/documents/" \
  -H "Authorization: Bearer <your_token>" \
  -F "file=@financial_report.pdf"
```

## 🔧 Development Setup

### Local Development (without Docker)
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Update .env for local development
DATABASE_HOST=localhost
NEO4J_URI=bolt://localhost:7687

# Start PostgreSQL and Neo4j services only
docker-compose up db neo4j -d

# Run FastAPI development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Database Management
```bash
# Create new migration
docker-compose exec app alembic revision --autogenerate -m "Description"

# Apply migrations
docker-compose exec app alembic upgrade head

# View migration history
docker-compose exec app alembic history
```

## 📁 Project Structure

```
investi-graph/
├── app/                    # FastAPI application
│   ├── main.py            # API entry point
│   ├── config.py          # Configuration settings
│   ├── database.py        # Database connection
│   ├── models.py          # SQLAlchemy models
│   ├── schemas.py         # Pydantic schemas
│   ├── crud.py            # Database operations
│   ├── security.py        # Authentication logic
│   ├── processing.py      # Document processing pipeline
│   └── knowledge_graph.py # Neo4j graph operations
├── alembic/               # Database migrations
├── uploads/               # File upload directory
├── docker-compose.yml     # Multi-container setup
├── Dockerfile            # App container definition
├── requirements.txt      # Python dependencies
└── .env                  # Environment variables
```

## 🐛 Troubleshooting

### Common Issues

**Port Already in Use**
```bash
# Check what's using port 8000
netstat -tulpn | grep 8000
# Kill the process or change port in docker-compose.yml
```

**Database Connection Failed**
```bash
# Check if PostgreSQL container is running
docker-compose logs db
# Recreate database container
docker-compose down && docker-compose up db -d
```

**Authentication Errors**
- Verify JWT_SECRET_KEY in `.env`
- Check token expiration time
- Ensure proper Authorization header format

**Slow First Run**
- Embedding models download on first use (~500MB)
- Check disk space and internet connection

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes and test locally
4. Create database migration if needed: `alembic revision --autogenerate -m "Description"`
5. Commit changes: `git commit -m "Add amazing feature"`
6. Push to branch: `git push origin feature/amazing-feature`
7. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Need help?** Open an issue or check the [API documentation](http://localhost:8000/docs) after starting the services.

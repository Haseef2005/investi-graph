# 📊 Investi-Graph Backend

> **Advanced RAG-Powered Financial Document Analysis API**

Investi-Graph is a state-of-the-art backend system that combines **Vector Search**, **Knowledge Graphs**, and **Cross-Encoder Reranking** to deliver intelligent financial document analysis. Built with FastAPI, it provides enterprise-grade performance with async processing, JWT authentication, and containerized deployment.

## 🚀 What Makes It Special

🧠 **Hybrid RAG Architecture**
- Vector embeddings for semantic search (pgvector)
- Knowledge graph relationships (Neo4j)  
- Smart reranking with Cross-Encoder models
- Multi-modal context fusion for superior accuracy

🔒 **Enterprise Security**
- JWT authentication with Argon2 hashing
- Role-based access control
- Secure file upload handling
- Production-ready CORS configuration

⚡ **High Performance**
- Async document processing pipeline
- Background task queue for heavy operations
- Optimized database queries with SQLAlchemy
- Docker containerization for scalability

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Client App    │───▶│   FastAPI App    │───▶│   PostgreSQL    │
│   (Frontend)    │    │   (Backend)      │    │   + pgvector    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │     Neo4j        │
                       │ (Knowledge Graph)│
                       └──────────────────┘
```

**Processing Flow:**
1. **Upload** → PDF/TXT document processing
2. **Extract** → Text extraction and chunking  
3. **Embed** → Vector embeddings generation
4. **Graph** → Entity/relationship extraction
5. **Store** → Multi-database persistence
6. **Query** → Hybrid RAG with reranking

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **API Framework** | FastAPI + Uvicorn | Async REST API |
| **Database** | PostgreSQL 15 | Primary data storage |
| **Vector Storage** | pgvector | Embeddings & similarity search |
| **Graph Database** | Neo4j | Knowledge graph storage |
| **Authentication** | JWT + Argon2 | Secure user management |
| **Embeddings** | sentence-transformers | Text vectorization |
| **Reranking** | CrossEncoder | Precision improvement |
| **LLM** | Groq (Llama 3.1) | Answer generation |
| **Containerization** | Docker Compose | Environment management |
| **Migrations** | Alembic | Database versioning |

## 📋 Prerequisites

- **Docker Desktop** (v20.10+)
- **Docker Compose** (v2.0+)
- **Git**
- **Groq API Key** ([Get Free Key](https://console.groq.com))

## ⚡ Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/your-username/investi-graph.git
cd investi-graph
```

### 2. Environment Setup
Create `.env` file in project root:

```bash
# Copy example environment file
cp .env.example .env
```

**Example .env Configuration:**
```env
# ===========================================
# PROJECT CONFIGURATION
# ===========================================
PROJECT_NAME="Investi-Graph"
DEBUG=false
ENVIRONMENT="development"

# ===========================================
# SECURITY & AUTHENTICATION  
# ===========================================
# Generate with: openssl rand -hex 32
JWT_SECRET_KEY="your-super-secret-jwt-key-minimum-32-characters-long"
JWT_ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# ===========================================
# DATABASE CONFIGURATION (PostgreSQL)
# ===========================================
DATABASE_USER=postgres
DATABASE_PASSWORD=your-secure-password-123
DATABASE_NAME=investi_graph_db
DATABASE_HOST=db
DATABASE_PORT=5432
DATABASE_URL="postgresql+psycopg://${DATABASE_USER}:${DATABASE_PASSWORD}@${DATABASE_HOST}:${DATABASE_PORT}/${DATABASE_NAME}"

# ===========================================
# GRAPH DATABASE (Neo4j)
# ===========================================
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j  
NEO4J_PASSWORD=your-neo4j-password-123

# ===========================================
# AI/LLM CONFIGURATION
# ===========================================
LLM_PROVIDER="groq"
LLM_API_KEY="gsk_your_groq_api_key_here"

# ===========================================
# OPTIONAL: CUSTOM SETTINGS
# ===========================================
# CORS_ORIGINS=["http://localhost:3000", "https://yourdomain.com"]
# MAX_FILE_SIZE_MB=50
# CHUNK_SIZE=1000
# CHUNK_OVERLAP=200
```

### 3. Start Services
```bash
# Build and start all containers
docker-compose up -d --build

# Check container status
docker-compose ps
```

### 4. Initialize Database
```bash
# Apply database migrations
docker exec investi_app alembic upgrade head

# Verify database connection
docker-compose logs app | grep -i "database"
```

### 5. Verify Installation
✅ **API Documentation:** http://localhost:8000/docs  
✅ **Health Check:** http://localhost:8000/health  
✅ **Neo4j Browser:** http://localhost:7474 (neo4j/your-neo4j-password-123)

## 📖 API Usage Guide

### 🔐 Authentication Workflow

#### 1. Register New User
```bash
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@company.com",
    "password": "SecurePassword123!",
    "full_name": "John Doe"
  }'
```

#### 2. Login & Get Access Token
```bash
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john.doe@company.com&password=SecurePassword123!"
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

### 📄 Document Management

#### 1. Upload Document
```bash
curl -X POST "http://localhost:8000/documents/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@financial-report-2024.pdf"
```

**Response:**
```json
{
  "id": 1,
  "filename": "financial-report-2024.pdf", 
  "status": "processing",
  "uploaded_at": "2024-11-19T09:13:46.549Z",
  "file_size": 2048576
}
```

#### 2. Check Processing Status
```bash
curl -X GET "http://localhost:8000/documents/1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### 3. List All Documents
```bash
curl -X GET "http://localhost:8000/documents/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 🤖 Advanced RAG Queries

#### 1. Chat with Specific Document
```bash
curl -X POST "http://localhost:8000/documents/1/chat" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What was the company revenue growth in Q3 2024?",
    "include_sources": true
  }'
```

**Response:**
```json
{
  "answer": "Based on the financial report, the company achieved a 15.3% revenue growth in Q3 2024, reaching $2.8 billion compared to $2.43 billion in Q3 2023...",
  "sources": [
    {
      "chunk_id": 45,
      "text": "Q3 2024 revenue increased to $2.8B...",
      "relevance_score": 0.94
    }
  ],
  "processing_time": 1.2,
  "method": "hybrid_rag"
}
```

#### 2. Global Search (All Documents)
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Compare the risk factors between Tesla and NVIDIA",
    "max_sources": 5
  }'
```

#### 3. Knowledge Graph Query
```bash
curl -X POST "http://localhost:8000/documents/1/graph-query" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show relationships between executives and subsidiaries"
  }'
```

### 📊 Knowledge Graph Visualization

#### Get Document Graph Structure
```bash
curl -X GET "http://localhost:8000/documents/1/graph" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "nodes": [
    {
      "id": "Tesla Inc",
      "label": "Tesla Inc", 
      "type": "COMPANY",
      "properties": {
        "industry": "Automotive",
        "founded": "2003"
      }
    },
    {
      "id": "Elon Musk",
      "label": "Elon Musk",
      "type": "PERSON", 
      "properties": {
        "role": "CEO"
      }
    }
  ],
  "edges": [
    {
      "source": "Elon Musk",
      "target": "Tesla Inc",
      "relationship": "CEO_OF",
      "properties": {
        "since": "2008"
      }
    }
  ],
  "statistics": {
    "total_nodes": 156,
    "total_relationships": 234
  }
}
```

## 🔧 Development Setup

### Local Development (No Docker)
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Update .env for local development
DATABASE_HOST=localhost
NEO4J_URI=bolt://localhost:7687

# Start only database services
docker-compose up db neo4j -d

# Run FastAPI development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Database Operations
```bash
# Create new migration
docker exec investi_app alembic revision --autogenerate -m "Add new feature"

# Apply migrations  
docker exec investi_app alembic upgrade head

# Rollback migration
docker exec investi_app alembic downgrade -1

# View migration history
docker exec investi_app alembic history
```

## 📁 Project Structure

```
investi-graph/
├── 📁 app/                          # Main application code
│   ├── 🐍 main.py                   # FastAPI app & routes
│   ├── 🔧 config.py                 # Configuration settings  
│   ├── 💾 database.py               # Database connection
│   ├── 📋 models.py                 # SQLAlchemy models
│   ├── 📄 schemas.py                # Pydantic schemas
│   ├── 🔨 crud.py                   # Database operations
│   ├── 🔐 security.py               # Authentication logic
│   ├── ⚙️  processing.py            # Document processing pipeline
│   └── 🕸️  knowledge_graph.py       # Neo4j operations
├── 📁 alembic/                      # Database migrations
│   └── 📁 versions/                 # Migration files
├── 📁 uploads/                      # File upload directory
├── 🐳 docker-compose.yml            # Multi-service orchestration
├── 🐳 Dockerfile                    # Application container
├── 📦 requirements.txt              # Python dependencies
├── ⚙️  alembic.ini                  # Migration configuration  
├── 📝 README.md                     # Project documentation
└── 🔒 .env                          # Environment variables
```

## 🐛 Troubleshooting

### Common Issues & Solutions

**🔌 Port Already in Use**
```bash
# Kill process using port 8000
sudo kill -9 $(lsof -ti:8000)
# Or change port in docker-compose.yml
```

**💾 Database Connection Failed** 
```bash
# Check PostgreSQL logs
docker-compose logs db

# Reset database container
docker-compose down
docker volume rm investi-graph_postgres_data
docker-compose up db -d
```

**🔐 JWT Authentication Errors**
- Verify `JWT_SECRET_KEY` is at least 32 characters
- Check token hasn't expired
- Ensure `Authorization: Bearer TOKEN` format

**🤖 LLM API Errors**
```bash
# Test Groq API connection
curl -H "Authorization: Bearer YOUR_GROQ_KEY" \
  https://api.groq.com/openai/v1/models
```

**🕸️ Neo4j Connection Issues**
```bash
# Check Neo4j logs
docker-compose logs neo4j

# Access Neo4j browser
open http://localhost:7474
```

**🚀 Slow Performance**
- First run downloads ML models (~1GB total)
- Increase Docker memory allocation (8GB recommended)
- Use SSD storage for better I/O performance

## 📈 Performance Optimization

### Production Recommendations

**🔧 System Requirements:**
- CPU: 4+ cores
- RAM: 8GB+ (16GB recommended) 
- Storage: SSD with 50GB+ free space
- Network: Stable internet for model downloads

**⚡ Optimization Tips:**
```bash
# Increase worker processes
# In docker-compose.yml, add:
environment:
  - WORKERS=4

# Use Redis for caching (optional)
# Add Redis service and configure in app/config.py

# Enable compression
# Add to FastAPI app initialization:
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

## 🔒 Security Best Practices

**Production Checklist:**
- [ ] Change all default passwords in `.env`
- [ ] Use strong JWT secret (32+ characters)
- [ ] Enable HTTPS in production
- [ ] Configure CORS for specific domains only
- [ ] Implement rate limiting
- [ ] Regular security updates
- [ ] Monitor API usage and errors
- [ ] Backup databases regularly

```bash
# Generate secure JWT secret
openssl rand -hex 32

# Test security headers
curl -I http://localhost:8000/docs
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork** the repository
2. **Create** feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** changes: `git commit -m 'Add amazing feature'`
4. **Test** your changes thoroughly
5. **Push** to branch: `git push origin feature/amazing-feature`  
6. **Open** a Pull Request

### Development Guidelines
- Follow PEP 8 style guide
- Add type hints to all functions
- Write tests for new features
- Update documentation for API changes
- Use conventional commit messages

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **📚 Documentation:** [API Docs](http://localhost:8000/docs) (after setup)
- **🐛 Issues:** [GitHub Issues](https://github.com/your-username/investi-graph/issues)
- **💬 Discussions:** [GitHub Discussions](https://github.com/your-username/investi-graph/discussions)
- **📧 Contact:** [your.email@domain.com](mailto:your.email@domain.com)

---

**⭐ If this project helps you, please give it a star on GitHub!**

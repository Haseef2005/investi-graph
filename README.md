# 📊 Investi-Graph Backend

> **Advanced AI-Powered Financial Document Intelligence Platform**

Investi-Graph is a cutting-edge backend system that revolutionizes financial document analysis by combining **Hybrid RAG Architecture**, **Knowledge Graph Intelligence**, and **SEC EDGAR Integration**. Built with FastAPI, it provides enterprise-grade performance with async processing, JWT authentication, and automated financial data retrieval.

## 🚀 What Makes It Special

🧠 **Intelligent Document Processing**
- **Hybrid RAG**: Vector embeddings + Knowledge graphs + Cross-encoder reranking
- **Smart Content Extraction**: Automatic removal of cover pages, TOC, and exhibits 
- **Knowledge Graph Generation**: AI-powered entity and relationship extraction
- **Multi-source Context Fusion**: Superior accuracy through intelligent context merging

📈 **SEC EDGAR Integration**
- **Automated 10-K/10-Q Retrieval**: Direct access to official SEC filings
- **Smart Content Filtering**: Removes XBRL tags, binary data, and irrelevant sections
- **Ticker-Based Queries**: Simple company ticker input for instant document access
- **Clean Financial Data**: Pre-processed, analysis-ready content

🔒 **Enterprise-Grade Security**
- JWT authentication with Argon2 password hashing
- Role-based access control and document ownership
- Secure file upload with content validation
- Production-ready CORS and rate limiting

⚡ **High Performance Architecture**
- Async document processing pipeline with background tasks
- Optimized vector search with pgvector
- Smart chunking with overlap optimization
- Docker containerization for horizontal scaling

## 🏗️ System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │───▶│   FastAPI App    │───▶│   PostgreSQL    │
│   (React/Vue)   │    │   (Python)       │    │   + pgvector    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        │
                       ┌──────────────────┐              │
                       │     Neo4j        │              │
                       │ (Knowledge Graph)│              │
                       └──────────────────┘              │
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │   SEC EDGAR      │    │   File Storage  │
                       │   (10-K/10-Q)    │    │   (Documents)   │
                       └──────────────────┘    └─────────────────┘
```

**Enhanced Processing Pipeline:**
1. **Input** → Manual upload OR automated SEC ticker retrieval
2. **Extract** → PDF/HTML parsing with smart content cropping
3. **Clean** → Remove cover pages, XBRL tags, and binary content
4. **Chunk** → Intelligent text segmentation with overlap
5. **Embed** → Vector embeddings generation (sentence-transformers)
6. **Graph** → AI-powered entity/relationship extraction
7. **Store** → Multi-database persistence (PostgreSQL + Neo4j)
8. **Query** → Hybrid RAG with graph-enhanced context

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **API Framework** | FastAPI + Uvicorn | Async REST API with OpenAPI docs |
| **Database** | PostgreSQL 15 + pgvector | Primary data & vector storage |
| **Graph Database** | Neo4j | Knowledge graph storage |
| **Authentication** | JWT + Argon2 | Secure user management |
| **Text Processing** | sentence-transformers | Text vectorization |
| **AI Models** | CrossEncoder | Precision reranking |
| **LLM Provider** | Groq (Llama 3.1) | Answer generation |
| **SEC Data** | sec-edgar-downloader | Official SEC filings |
| **Content Parsing** | BeautifulSoup + PyPDF2 | Document extraction |
| **Containerization** | Docker + Compose | Environment management |
| **Migrations** | Alembic | Database versioning |

## 📋 Prerequisites

- **Docker Desktop** (v20.10+)
- **Docker Compose** (v2.0+)
- **Git**
- **Groq API Key** ([Get Free Key](https://console.groq.com))
- **SEC API Email** (Required for SEC EDGAR access)

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
# SEC EDGAR INTEGRATION  
# ===========================================
SEC_API_EMAIL="your-email@company.com"

# ===========================================
# OPTIONAL: CUSTOM SETTINGS
# ===========================================
# CORS_ORIGINS=["http://localhost:3000", "https://yourdomain.com"]
# MAX_FILE_SIZE_MB=50
# CHUNK_SIZE=1000
# CHUNK_OVERLAP=200
# MAX_GRAPH_CHUNKS=10
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
    "username": "john_doe",
    "email": "john.doe@company.com", 
    "password": "SecurePassword123!"
  }'
```

#### 2. Login & Get Access Token
```bash
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john_doe&password=SecurePassword123!"
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 📄 Document Management

#### 1. Upload Document (Manual)
```bash
curl -X POST "http://localhost:8000/documents/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@financial-report-2024.pdf"
```

#### 2. Fetch SEC Document (Automated)
```bash
curl -X POST "http://localhost:8000/documents/fetch-sec" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "TSLA"
  }'
```

**Response:**
```json
{
  "message": "Started fetching 10-K for TSLA. Check your documents list in a few minutes."
}
```

#### 3. List All Documents
```bash
curl -X GET "http://localhost:8000/documents/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
[
  {
    "id": 1,
    "filename": "TSLA_10K_Report.txt",
    "uploaded_at": "2024-11-20T10:30:00Z",
    "owner_id": 1
  },
  {
    "id": 2, 
    "filename": "quarterly-earnings-q3.pdf",
    "uploaded_at": "2024-11-20T11:15:00Z",
    "owner_id": 1
  }
]
```

### 🤖 Advanced AI Queries

#### 1. Document-Specific RAG Query
```bash
curl -X POST "http://localhost:8000/documents/1/query" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are Tesla main revenue streams in 2023?"
  }'
```

**Response:**
```json
{
  "answer": "Based on Tesla's 10-K filing, the company's main revenue streams in 2023 include: 1) Automotive sales (81.4% of total revenue) including Model S, 3, X, and Y vehicles; 2) Energy generation and storage (6.8%) through solar panels and Powerwall systems; 3) Services and other (11.8%) including Supercharging, insurance, and vehicle services...",
  "context": [
    {
      "id": 45,
      "text": "Automotive sales revenue increased to $75.2B in 2023...",
      "document_id": 1
    }
  ]
}
```

#### 2. Global Knowledge Query (All Documents)
```bash
curl -X POST "http://localhost:8000/documents/query" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Compare the risk factors between Tesla and Apple"
  }'
```

#### 3. Knowledge Graph Visualization
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
      "type": "COMPANY"
    },
    {
      "id": "Elon Musk",
      "label": "Elon Musk",
      "type": "PERSON"
    },
    {
      "id": "Gigafactory",
      "label": "Gigafactory",
      "type": "FACILITY"
    }
  ],
  "edges": [
    {
      "source": "Elon Musk",
      "target": "Tesla Inc",
      "relation": "CEO_OF"
    },
    {
      "source": "Tesla Inc",
      "target": "Gigafactory", 
      "relation": "OWNS"
    }
  ]
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
investi-graph-backend/
├── 📁 app/                          # Main application code
│   ├── 🐍 main.py                   # FastAPI app & API routes
│   ├── 🔧 config.py                 # Configuration settings  
│   ├── 💾 database.py               # Database connection & session
│   ├── 📋 models.py                 # SQLAlchemy ORM models
│   ├── 📄 schemas.py                # Pydantic request/response schemas
│   ├── 🔨 crud.py                   # Database CRUD operations
│   ├── 🔐 security.py               # JWT auth & password hashing
│   ├── ⚙️  processing.py            # Document processing pipeline
│   ├── 🕸️  knowledge_graph.py       # Neo4j graph operations
│   └── 🏢 sec_service.py            # SEC EDGAR integration
├── 📁 alembic/                      # Database migrations
│   └── 📁 versions/                 # Migration files
├── 📁 temp_sec/                     # Temporary SEC download storage
├── 📁 uploads/                      # User uploaded files
├── 🐳 docker-compose.yml            # Multi-service orchestration
├── 🐳 Dockerfile                    # Application container config
├── 📦 requirements.txt              # Python dependencies
├── ⚙️  alembic.ini                  # Database migration config  
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

**🤖 SEC API Errors**
```bash
# Test SEC EDGAR availability
curl "https://www.sec.gov/files/company_tickers.json" | head

# Check SEC rate limiting (max 10 requests/second)
# Add delays between requests if needed
```

**🔐 Invalid Ticker Symbol**
- Verify ticker exists on SEC EDGAR database
- Use exact company ticker (e.g., TSLA not Tesla)
- Check company has filed 10-K reports recently

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
- [ ] Set valid SEC API email address
- [ ] Enable HTTPS in production
- [ ] Configure CORS for specific domains only
- [ ] Implement rate limiting for SEC requests
- [ ] Regular security updates and monitoring
- [ ] Backup databases regularly
- [ ] Monitor SEC API usage limits (10 req/sec)

```bash
# Generate secure JWT secret
openssl rand -hex 32

# Test security headers
curl -I http://localhost:8000/docs

# Verify SEC email format
echo "your-email@company.com" | grep -E "^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
```

## 🆕 New Features & Enhancements

### 📈 SEC EDGAR Integration
- **Automated Document Retrieval**: Fetch official 10-K/10-Q reports directly from SEC EDGAR
- **Ticker-Based Access**: Simple company ticker input (e.g., "TSLA", "AAPL") 
- **Smart Content Processing**: Removes cover pages, table of contents, and exhibits
- **Clean Financial Data**: Filters out XBRL tags and binary content automatically

### 🧹 Enhanced Document Processing
- **Intelligent Content Cropping**: Auto-removes non-essential sections (covers, signatures, exhibits)
- **XBRL Tag Filtering**: Eliminates technical metadata from SEC filings
- **Optimized Chunking**: Improved text segmentation for better context preservation
- **Binary Content Removal**: Strips out embedded images and unnecessary data

### 🕸️ Advanced Knowledge Graph
- **AI Entity Extraction**: Automatic identification of companies, people, locations, concepts
- **Relationship Mapping**: Smart detection of business relationships and hierarchies  
- **Graph Filtering**: Removes low-quality entities and maintains graph cleanliness
- **Neo4j Integration**: Persistent storage with Cypher query capabilities

### 🔧 Technical Improvements
- **Background Processing**: Async document handling for better user experience
- **Error Handling**: Robust error recovery and logging throughout the pipeline
- **Content Validation**: Smart document format detection and processing
- **Performance Optimization**: Efficient database queries and caching strategies

---

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

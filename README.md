# 📈 Investi-Graph Backend

Investi-Graph is a **state-of-the-art financial document analysis backend** that goes beyond traditional search. It implements an **Advanced RAG (Retrieval-Augmented Generation) architecture** by combining Vector Search, Cross-Encoder Reranking, and GraphRAG (Knowledge Graphs) to provide highly accurate and context-aware insights.

Unlike simple RAG systems, Investi-Graph understands both the **semantic meaning of text** (via Vectors) and the **relationships between entities** (via Neo4j Graph), refined by a Reranker to eliminate irrelevant information before generating answers with Llama 3.

## ✨ Key Features

### 🧠 Advanced RAG Pipeline:
- **Vector Search**: High-recall retrieval using pgvector.
- **Smart Reranking**: High-precision filtering using Cross-Encoder (ms-marco) to select only the most relevant chunks.
- **GraphRAG**: Injects knowledge graph context (Entities & Relationships) from Neo4j to answer complex relational queries.

### 🕸️ Automated Knowledge Graph: 
Uses LLM to extract nodes (Companies, People) and edges (CEO_OF, LOCATED_IN) automatically from uploaded documents.

### 🔐 Secure Architecture: 
Robust JWT Authentication with Argon2 password hashing.

### 📄 Async Document Processing: 
Non-blocking upload pipeline: Extract → Chunk → Embed → Graph Extraction.

### 🌍 Global & Local Context: 
Chat with a specific document or query across all your documents simultaneously.

### 🐳 Production Ready: 
Fully containerized with Docker Compose (App + DB + Neo4j) and Alembic migrations.

## 🏗️ Architecture Pipeline

When a user queries the system, Investi-Graph performs a multi-stage retrieval process:

```mermaid
graph TD
    Q[User Query] --> V[1. Vector Search (pgvector)]
    Q --> G[3. GraphRAG Extraction]
    
    V -->|Top 20 Chunks| R[2. Reranking (Cross-Encoder)]
    R -->|Top 5 Relevant Chunks| C[Context Fusion]
    
    G -->|Entity Extraction| N[Neo4j Search]
    N -->|Relationships Context| C
    
    C -->|Combined Context| L[LLM (Llama 3)]
    L --> A[Final Answer]
```

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **API Framework** | FastAPI (Async) |
| **Vector DB** | PostgreSQL 15 + pgvector |
| **Graph DB** | Neo4j |
| **ORM** | SQLAlchemy (Async) |
| **Embeddings** | sentence-transformers/all-MiniLM-L6-v2 |
| **Reranker** | cross-encoder/ms-marco-MiniLM-L-6-v2 |
| **LLM Engine** | Llama 3.1-8b (via Groq API) |
| **Orchestration** | Docker Compose |

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose installed.
- Git installed.
- Groq API Key (Get one at console.groq.com).

### 1. Clone Repository
```bash
git clone https://github.com/[Your-Username]/investi-graph-backend.git
cd investi-graph-backend
```

### 2. Configure Environment
Create a `.env` file in the root directory.

```bash
cp .env.example .env
```

Ensure your `.env` matches Docker service names:

```properties
# ... (Project & Auth settings)

# Database (Host MUST be 'db')
DATABASE_HOST=db
DATABASE_URL="postgresql+psycopg://postgres:mysecretpassword@db:5432/postgres"

# Neo4j (Host MUST be 'neo4j')
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=mysecretneo4jpassword

# LLM
LLM_PROVIDER="groq"
LLM_API_KEY="gsk_your_key_here"
```

### 3. Start Services
Build and start the containers.

```bash
docker-compose up -d --build
```

### 4. Apply Database Schema
Initialize the database tables using Alembic.

```bash
docker exec investi_app alembic upgrade head
```

## 🔌 API Usage

Access the interactive Swagger documentation at:
**👉 http://localhost:8000/docs**

### 1. Authentication
- **Register**: `POST /users/`
- **Login**: `POST /token` (Returns Bearer Token)

### 2. Document Management
- **Upload**: `POST /documents/`  
  Uploads PDF, extracts text, generates vectors, and builds the knowledge graph in background.
- **List**: `GET /documents/`
- **Delete**: `DELETE /documents/{id}`  
  Note: Deletion cascades to remove vectors from Postgres and nodes/edges from Neo4j.

### 3. Advanced RAG Chat
Investi-Graph automatically applies **Hybrid Search** (Vector + Rerank + Graph) for best results.

**Chat with specific document:**
```bash
POST /documents/{doc_id}/query
{
  "question": "How does the new CEO impact the revenue guidance?"
}
```

**Global Chat (Search all documents):**
```bash
POST /documents/query
{
  "question": "Compare the risks between NVIDIA and Tesla."
}
```

### 4. Knowledge Graph Visualization
Retrieve the raw graph structure (Nodes/Edges) for frontend visualization.

```bash
GET /documents/{doc_id}/graph
```

**Response Example:**
```json
{
  "nodes": [
    {"id": "NVIDIA", "label": "NVIDIA", "type": "ORG"},
    {"id": "Jensen Huang", "label": "Jensen Huang", "type": "PERSON"}
  ],
  "edges": [
    {"source": "Jensen Huang", "target": "NVIDIA", "relation": "CEO_OF"}
  ]
}
```

## 📁 Project Structure

```
investi-graph-backend/
├── app/
│   ├── main.py             # API Entrypoint & Routes
│   ├── processing.py       # RAG Pipeline (Vector + Rerank)
│   ├── knowledge_graph.py  # Graph Pipeline (Extraction + GraphRAG)
│   ├── models.py           # Database Models
│   ├── schemas.py          # Pydantic Models
│   └── ...
├── alembic/                # DB Migrations
├── docker-compose.yml      # Service Orchestration
├── Dockerfile              # App Container
└── requirements.txt        # Python Dependencies
```

## 🛡️ Security Best Practices

- **Passwords**: Change default DB/Neo4j passwords in `.env`.
- **JWT**: Generate a strong `JWT_SECRET_KEY` using `openssl rand -hex 32`.
- **CORS**: In `main.py`, restrict `allow_origins` to your specific frontend domain for production.

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## 📝 License

MIT

# InvestiGraph
InvestiGraph is an advanced financial analysis tool that leverages Knowledge Graphs and GraphRAG (Retrieval-Augmented Generation) to extract, structure, and query insights from SEC 10-K documents.
## 🚀 Work Technique
The system employs a sophisticated pipeline to transform unstructured financial text into a structured knowledge graph:
1.  **Data Ingestion**: Downloads and parses SEC 10-K filings using `sec-edgar-downloader` and `beautifulsoup4`.
2.  **Graph Extraction**: Utilizes LLMs (Llama 3.1 via LiteLLM) to intelligently extract entities (Companies, People, Products) and relationships (CEO_OF, COMPETES_WITH, etc.) from text chunks.
3.  **Graph Storage**: Stores the extracted knowledge in a **Neo4j** graph database, ensuring data isolation per user and document.
4.  **GraphRAG Querying**: Enhances RAG by querying the knowledge graph for relevant connections based on user questions, providing context-aware answers that standard vector search might miss.
5.  **Reranking**: Uses a Cross-Encoder (`cross-encoder/ms-marco-MiniLM-L-6-v2`) to re-score and rank the retrieved documents, ensuring the most relevant context is passed to the LLM.
## 🏗️ Project Structure
- **`backend/`**: The core API and logic.
    - **`app/`**: FastAPI application source code.
        - **`knowledge_graph.py`**: Core logic for graph extraction, storage, and querying.
        - **`sec_service.py`**: Handling SEC document downloading and processing.
        - **`routers/`**: API endpoints for auth, users, and documents.
- **`frontend/`**: The user interface.
    - Built with React and Vite for a fast, modern experience.
    - Uses Tailwind CSS for styling and Framer Motion for animations.
## 🛠️ Tech Stack
### Backend
- **Framework**: FastAPI
- **Database**: Neo4j (Graph), PostgreSQL (User data via SQLAlchemy/AsyncPG)
- **AI/LLM**: LiteLLM (Llama 3.1), Sentence Transformers (Embeddings & Reranking)
- **Reranker**: Cross-Encoder (`ms-marco-MiniLM-L-6-v2`)
- **Tools**: Tenacity (Retries), Pydantic (Validation)
### Frontend
- **Framework**: React (Vite)
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios
- **Routing**: React Router DOM
- **Animation**: Framer Motion
## 🚦 Getting Started
### Prerequisites
- **Docker** & **Docker Compose** (for running the entire service stack)

### Quick Start
1. Create a `.env` file in the project root with your configuration:
   ```env
   PROJECT_NAME="Investi-Graph"
   # `openssl rand -hex 32` in git bash or use a web key generator
   JWT_SECRET_KEY="your_super_secret_key_here"
   JWT_ALGORITHM="HS256"
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   # --- DB Settings ---
   DATABASE_USER=postgres
   DATABASE_PASSWORD=mysecretpassword
   DATABASE_NAME=postgres
   DATABASE_URL="postgresql+psycopg://${DATABASE_USER}:${DATABASE_PASSWORD}@db:5432/${DATABASE_NAME}"
   # --- LLM Configuration ---
   LLM_PROVIDER="groq"
   LLM_API_KEY="gsk_..."
   # --- SEC API Configuration ---
   SEC_API_EMAIL="your_email@example.com"
   ```

2. Run the entire service stack from the project root:
   ```bash
   docker-compose up --build
   ```

This will start:
- **Frontend** (React + Vite) at `http://localhost` (port 80)
- **Backend** (FastAPI) at `http://localhost:8000`
- **PostgreSQL** database with pgvector extension
- **Neo4j** graph database at `http://localhost:7474` (browser interface)
# Investi-Graph 📈

Investi-Graph is a full-stack, AI-powered RAG (Retrieval-Augmented Generation) system for analyzing financial documents (e.g., 10-K, 56-1). The project is asynchronous, containerized with Docker, and uses pgvector for vector search.

Quick links
- [docker-compose.yml](docker-compose.yml)
- [Dockerfile](Dockerfile)
- [.env](.env)
- [`app.main`](app/main.py)
- [`app.processing.save_extract_chunk_and_embed`](app/processing.py)
- [`app.crud.create_document`](app/crud.py)
- [`app.crud.create_user`](app/crud.py)
- [`app.security.create_access_token`](app/security.py)
- [`app.models.Document`](app/models.py)
- [`app.models.Chunk`](app/models.py)
- [`app.database.get_db`](app/database.py)
- [alembic/](alembic/README)

Features
- JWT Authentication with passlib[argon2] and python-jose.
- Asynchronous file uploads (PDF/TXT) and immediate API response; heavy processing runs in background via [`app.processing.save_extract_chunk_and_embed`](app/processing.py).
- AI pipeline: extract (pypdf), chunk (langchain-text-splitters), embed (sentence-transformers).
- Vector storage using pgvector (PostgreSQL extension).
- RAG querying with LLM provider (configured for Groq via litellm).
- Containerized: API + DB via [docker-compose.yml](docker-compose.yml).
- Schema migrations with Alembic.

Tech stack
- Backend: FastAPI (async)
- Container: Docker & Docker Compose
- Database: PostgreSQL 15 + pgvector
- ORM: SQLAlchemy (async)
- Migrations: Alembic
- Auth: JWT (python-jose) + passlib[argon2]
- LLM: litellm (Groq / Llama 3)
- Embeddings: sentence-transformers (all-MiniLM-L6-v2)
- Chunking: langchain-text-splitters
- File handling: pypdf, aiofiles

Getting started (Docker)
1. Prerequisites
   - Git
   - Docker Desktop
   - Groq API Key (if using the LLM integration)

2. Clone
   git clone https://github.com/[Your-Username]/investi-graph.git
   cd investi-graph

3. Create `.env`
   - Use the project root `.env` referenced by [app/config.py](app/config.py).
   - Example (for Docker Compose):
     ```
     PROJECT_NAME="Investi-Graph"
     JWT_SECRET_KEY="your-secret"
     JWT_ALGORITHM="HS256"
     ACCESS_TOKEN_EXPIRE_MINUTES=30
     DATABASE_USER=postgres
     DATABASE_PASSWORD=mysecretpassword
     DATABASE_NAME=postgres
     DATABASE_HOST=db
     DATABASE_PORT=5432
     DATABASE_URL="postgresql+psycopg://${DATABASE_USER}:${DATABASE_PASSWORD}@${DATABASE_HOST}:${DATABASE_PORT}/${DATABASE_NAME}"
     LLM_PROVIDER="groq"
     LLM_API_KEY="gsk_..."
     ```

4. Build & run
   docker-compose up --build -d

5. Run migrations (after DB ready)
   docker-compose exec app alembic upgrade head

API quickstart
- Open OpenAPI docs: http://127.0.0.1:8000/docs
1. Sign up: POST /users/ → uses [`app.crud.create_user`](app/crud.py)
2. Login: POST /token → returns JWT created by [`app.security.create_access_token`](app/security.py)
3. Upload document: POST /documents/ → creates DB record via [`app.crud.create_document`](app/crud.py) and starts background processing via [`app.processing.save_extract_chunk_and_embed`](app/processing.py)
4. List documents: GET /documents/ (auth required)
5. List chunks: GET /documents/{doc_id}/chunks → returns [`app.models.Chunk`](app/models.py)

Notes & troubleshooting
- Embedding model downloads on first run (may take time).
- pgvector extension is enabled in [`app.database`](app/database.py) and migrations ([alembic/versions](alembic/versions/)).
- If authentication fails, check `.env` and JWT settings in [app/config.py](app/config.py).

Contributing
- Use Alembic for schema changes ([alembic/](alembic/README)).
- Keep Docker Compose and `.env` in sync for local dev.

License & acknowledgements
- (Add licensing info here)

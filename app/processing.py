import logging
import os
import aiofiles
from pypdf import PdfReader

# "Import" ตัว "หั่น" (Chunking) และ "แปลง" (Embedding)
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app import models, crud
from app.database import SessionLocal
from app.config import settings
import sqlalchemy as sa

# --- [จุดแก้ที่ 1] เปลี่ยนเป็น acompletion (Async) ---
from litellm import acompletion
# -------------------------------------------------

# Import Retry
from tenacity import retry, stop_after_attempt, wait_exponential

UPLOAD_DIRECTORY = "/app/uploads"
log = logging.getLogger("uvicorn.error")

# --- "โหลด" AI (แค่ครั้งเดียว) ---
log.info("Loading SentenceTransformer model...")
EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
log.info("Model loaded.")
# ---------------------------------


# "สร้าง" ตัว "หั่น"
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
)


async def save_extract_chunk_and_embed(
    document_id: int,
    filename: str,
    content_type: str,
    content: bytes
):
    """
    Process: Upload -> Extract -> Chunk -> Embed -> Save to DB
    """
    os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIRECTORY, f"doc_{document_id}_{filename}")

    log.info(f"--- 🤖 TASK START (Doc ID: {document_id}) ---")

    try:
        # 1. Save File
        async with aiofiles.open(file_path, "wb") as out_file:
            await out_file.write(content)
        log.info(f"File saved.")

        # 2. Extract Text
        extracted_text = ""
        if content_type == "application/pdf":
            reader = PdfReader(file_path)
            for page in reader.pages:
                extracted_text += page.extract_text() + "\n"
        else:
            extracted_text = content.decode("utf-8")
        log.info(f"Text extracted. Length: {len(extracted_text)}")

        # 3. Chunk
        chunks = text_splitter.split_text(extracted_text)
        log.info(f"Text chunked into {len(chunks)} pieces.")

        # 4. Embed
        log.info(f"Embedding chunks...")
        embeddings = EMBEDDING_MODEL.encode(chunks)
        log.info(f"Embeddings created.")

        # 5. Save to DB
        db_chunks = []
        for i in range(len(chunks)):
            db_chunks.append(
                models.Chunk(
                    text=chunks[i],
                    embedding=embeddings[i],
                    document_id=document_id
                )
            )

        async with SessionLocal() as db:
            log.info(f"Saving to DB...")
            db.add_all(db_chunks)
            await db.commit()

        log.info(f"--- 🤖 TASK DONE (Doc ID: {document_id}) ---")

    except Exception as e:
        log.error(f"Error processing file {file_path}: {e}", exc_info=True)
        log.error(f"--- 🤖 TASK FAILED (Doc ID: {document_id}) ---")

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
        log.info(f"Cleaned up {file_path}")


# 1. ฟังก์ชัน "ค้นหา" (Retrieval)
async def retrieve_relevant_chunks(
    document_id: int, 
    query_text: str
) -> list[models.Chunk]:
    """
    Query -> Embed -> Vector Search
    """
    log.info(f"Embedding query: {query_text}")
    query_embedding = EMBEDDING_MODEL.encode(query_text)

    async with SessionLocal() as db:
        stmt = (
            sa.select(models.Chunk)
            .where(models.Chunk.document_id == document_id)
            .order_by(
                models.Chunk.embedding.l2_distance(query_embedding)
            )
            .limit(5)
        )
        result = await db.execute(stmt)
        return result.scalars().all()


# 2. ฟังก์ชัน "สร้างคำตอบ" (Generation)
async def generate_answer(
    query: str, 
    context_chunks: list[models.Chunk]
) -> str:
    """
    Context + Query -> LLM -> Answer
    """
    log.info(f"Generating answer using {len(context_chunks)} chunks...")

    context_text = "\n\n---\n\n".join(
        [chunk.text for chunk in context_chunks]
    )

    prompt = f"""
    You are an expert financial analyst AI.
    Answer the user's question based *only* on the context provided below.
    If the answer is not found in the context, say "I cannot find the answer in the provided context."

    CONTEXT:
    ---
    {context_text}
    ---

    QUESTION:
    {query}
    """

    # Retry Logic
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def call_llm_api():
        # --- [จุดแก้ที่ 2] ใช้ await acompletion(...) ---
        return await acompletion( 
            model=f"{settings.LLM_PROVIDER}/llama-3.1-8b-instant",
            api_key=settings.LLM_API_KEY,
            messages=[
                {"role": "system", "content": "You are a helpful analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8
        )
    
    try:
        response = await call_llm_api()
        answer = response.choices[0].message.content
        log.info(f"Answer generated.")
        return answer

    except Exception as e:
        log.error(f"LLM completion failed after retries: {e}", exc_info=True)
        return f"Error: The AI service is currently unavailable. Please try again later. ({str(e)})"
import asyncio
import logging 
from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

# --- Import ใหม่ของเรา ---
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud, models, schemas # <-- Import ห้องครัว, ตาราง, API
from app.database import engine, Base, get_db # <-- Import เครื่องยนต์, รุ่นพ่อ, คนงาน

from app.config import settings
from app.security import (
    verify_password, 
    create_access_token, 
    verify_token,
    oauth2_scheme,
)
from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, BackgroundTasks
import time

log = logging.getLogger("uvicorn.error")

# --- "สร้าง" ตาราง (Table) ---
# เราจะบอกให้แอป "สร้างตาราง" (ถ้ายังไม่มี) ตอนที่มันเริ่มทำงาน
# (นี่คือวิธีง่ายๆ... Task ต่อไปเราจะใช้ "Alembic" ที่โปรขึ้น)
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0"
)

# alembic จะจัดการเรื่องตารางให้เราเอง
# @app.on_event("startup")
# async def on_startup():
#     """Create the database tables on startup."""
#     async with engine.begin() as conn:
#         # await conn.run_sync(Base.metadata.drop_all) # <-- (ไว้ล้างตาราง ถ้าอยากเริ่มใหม่)
#         await conn.run_sync(Base.metadata.create_all)


# --- Auth Functions (อัปเกรดแล้ว!) ---

# เราจะ "เปลี่ยน" get_current_user ให้ "คุย" กับ DB จริง
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_db) # <-- "ฉีด" DB Session เข้ามา
) -> models.User: # <-- คืนค่าเป็น "โมเดล" (DB)

    # 1. ตรวจ Token
    token_data: schemas.TokenData = await verify_token(token)

    # 2. หา User ใน DB จริง (โดยใช้ crud)
    user = await crud.get_user_by_username(db, username=token_data.username)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found (from token)",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )

    return user

# --- Dummy funcition AI ---
async def process_document_in_background(document_name: str):
    """(Dummy) AI processing function."""
    log.info(f"--- 🤖 BACKGROUND TASK: START ---") # <-- แก้
    log.info(f"Processing document: {document_name}") # <-- แก้
    await asyncio.sleep(10)
    log.info(f"--- 🤖 BACKGROUND TASK: DONE ---") # <-- แก้

# --- Endpoints ---

@app.get("/")
def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME} API!"}

@app.get("/health")
def health_check():
    return {"status": "ok"}


# (ใหม่!) Endpoint "สมัครสมาชิก" (Sign Up)
@app.post("/users/", response_model=schemas.User)
async def create_user_endpoint(
    user: schemas.UserCreate, # <-- รับ "พิมพ์เขียว" สมัคร
    db: AsyncSession = Depends(get_db)
):
    # 1. เช็กว่า email หรือ username ซ้ำไหม
    db_user = await crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = await crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already taken")

    # 2. สร้าง User (โดย crud.py)
    return await crud.create_user(db=db, user=user)


# Endpoint "Login" (อัปเกรดแล้ว!)
@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_db) # <-- "ฉีด" DB Session
):
    # 1. ตรวจสอบ User/Password (ใน DB จริง!)
    user = await crud.get_user_by_username(db, username=form_data.username)

    # 2. เช็กว่า user มีจริงไหม และ รหัสผ่านตรงกันไหม
    if not user or not verify_password(
        form_data.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )

    # 3. สร้าง Token (เหมือนเดิม)
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    token_data = {"sub": user.username} 
    access_token = create_access_token(
        data=token_data, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


# Endpoint ที่ "ถูกป้องกัน" (อัปเกรดแล้ว!)
@app.get("/users/me", response_model=schemas.User)
async def read_users_me(
    current_user: Annotated[models.User, Depends(get_current_user)]
):
    # ฟังก์ชันนี้ "แทบ" ไม่ต้องแก้เลย
    # มันจะคืนค่า User (จาก DB) ที่ "สะอาด" (ตาม response_model)
    # Pydantic (schemas.User) จะ "อ่าน" (from_attributes=True)
    # จาก current_user (models.User) ให้เราเอง
    return current_user

# Endpoint "รับข้อมูล" (Data Ingestion)
@app.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...) # <-- "รับ" ไฟล์
):
    # (เรายังไม่เซฟไฟล์จริง... เราแค่ "อ่าน" ชื่อมัน)
    filename = file.filename

    # "โยน" งานหนักไปทำเบื้องหลัง
    asyncio.create_task(
        process_document_in_background(filename)
    )

    # "ตอบ" User กลับไป "ทันที"
    return {
        "message": "File received. Processing started in background.",
        "filename": filename
    }
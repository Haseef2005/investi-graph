# app/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Annotated  # Import Annotated

from app.config import settings # <-- Import settings ของเรา

# (เราจะย้ายส่วน Auth นี้ไปไว้ไฟล์อื่นในอนาคต แต่ตอนนี้แปะไว้ที่นี่ก่อน)
# --- FAKE DATABASE (เรายังไม่มี DB) ---
fake_users_db = {
    "intern": {
        "username": "intern",
        "full_name": "Intern Developer",
        "email": "intern@investigraph.com",
        "hashed_password": "$2b$12$Eix3.13GfbuQJSO.9hGJA.J/R.IfzP.nS3zD.S.VYDQJgPayJmG0e", # "password"
        "disabled": False,
    }
}

# --- FAKE SECURITY FUNCTIONS (เราจะย้ายไป app/security.py) ---

# (ในชีวิตจริง เราจะใช้ passlib ที่นี่)
def verify_password(plain_password, hashed_password):
    # นี่คือ Demo ที่ไม่ปลอดภัย ห้ามใช้จริง!
    # เราจะมาแทนที่ด้วย passlib ใน Task ถัดไป
    return hashed_password == "$2b$12$Eix3.13GfbuQJSO.9hGJA.J/R.IfzP.nS3zD.S.VYDQJgPayJmG0e" # "password"

def get_user(db, username: str):
    if username in db:
        return db[username]
    return None

# --- END FAKE STUFF ---


# --- Pydantic Models ---
class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None

class Token(BaseModel):
    access_token: str
    token_type: str


# --- FastAPI App ---
app = FastAPI(
    title=settings.PROJECT_NAME, # <-- ใช้ Config
    version="0.1.0"
)

# นี่คือ "ตัวบอก" FastAPI ว่า Token จะถูกส่งมายังไง
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# --- Auth Functions ---
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    # (นี่คือเวอร์ชัน Demo เราจะมาใส่ JWT logic จริงจังที่นี่)
    # ตอนนี้เราแค่ "แกล้ง" ว่า Token ถูกต้องเสมอ
    user = get_user(fake_users_db, "intern") 
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return User(**user)


# --- Endpoints ---

@app.get("/")
def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME} API!"} # <-- ใช้ Config

@app.get("/health")
def health_check():
    return {"status": "ok"}


# Endpoint สำหรับ "Login"
@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    # (เรายังไม่ได้ใช้ form_data.username, form_data.password จริงจัง)
    # (เรายังไม่ได้สร้าง JWT Token จริงจัง)

    # 1. ตรวจสอบ User/Password (เราจะข้ามไปก่อน)
    # user = get_user(fake_users_db, form_data.username)
    # if not user or not verify_password(form_data.password, user["hashed_password"]):
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Incorrect username or password",
    #         headers={"WWW-Authenticate": "Bearer"},
    #     )

    # 2. สร้าง Token (ตอนนี้เราแกล้งๆ สร้าง Token ปลอม)
    access_token = "fake_access_token_for_demo" # <-- นี่คือ Token ปลอม

    return {"access_token": access_token, "token_type": "bearer"}


# Endpoint ที่ "ถูกป้องกัน" (Protected)
@app.get("/users/me", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)]
):
    # ฟังก์ชันนี้จะทำงานได้ "ก็ต่อเมื่อ" get_current_user ทำงานสำเร็จ
    return current_user
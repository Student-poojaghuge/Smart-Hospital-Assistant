
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, ConfigDict
from passlib.context import CryptContext

from database.database import get_db
from database.models import User
from backend.services.auth_service import create_access_token
from backend.services.auth_dependency import get_current_user


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)


# =========================
# REQUEST MODELS
# =========================

class RegisterRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=2, max_length=100)
    email: str = Field(min_length=5, max_length=254)
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    email: str = Field(min_length=5, max_length=254)
    password: str = Field(min_length=1, max_length=128)


# =========================
# REGISTER
# =========================

@router.post("/register")
def register_user(
    user_data: RegisterRequest,
    db: Session = Depends(get_db)
):
    email = user_data.email.strip().lower()
    name = user_data.name.strip()

    if len(name) < 2:
        raise HTTPException(
            status_code=422,
            detail="Name must contain at least 2 characters"
        )

    existing_user = db.query(User).filter(
        User.email == email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Public registration always creates a patient account.
    # Admin accounts must be created through a protected process.
    hashed_password = pwd_context.hash(user_data.password)

    new_user = User(
        name=name,
        email=email,
        password=hashed_password,
        role="patient"
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {
            "message": "User registered successfully",
            "user_id": new_user.user_id
        }

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to register user"
        )


# =========================
# LOGIN
# =========================

@router.post("/login")
def login_user(
    user_data: LoginRequest,
    db: Session = Depends(get_db)
):
    email = user_data.email.strip().lower()

    user = db.query(User).filter(
        User.email == email
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not pwd_context.verify(
        user_data.password,
        user.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token({
        "user_id": user.user_id,
        "role": user.role,
        "email": user.email
    })

    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.user_id,
        "name": user.name,
        "email": user.email,
        "role": user.role
    }


# =========================
# CURRENT AUTHENTICATED USER
# =========================

@router.get("/me")
def get_me(
    current_user: dict = Depends(get_current_user)
):
    return {
        "message": "Authenticated user",
        "user": current_user
    }

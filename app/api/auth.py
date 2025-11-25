"""
MUSE Language - Authentication API

인증 및 사용자 관리 엔드포인트
"""

from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import uuid

from app.core.config import settings

router = APIRouter()

# 비밀번호 해싱
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


class UserCreate(BaseModel):
    """회원가입 요청."""
    email: EmailStr
    password: str
    name: str
    native_language: str = "ko"
    target_languages: List[str] = ["en"]


class UserResponse(BaseModel):
    """사용자 응답."""
    id: str
    email: str
    name: str
    native_language: str
    is_premium: bool
    created_at: datetime


class TokenResponse(BaseModel):
    """토큰 응답."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class ProfileUpdate(BaseModel):
    """프로필 수정 요청."""
    name: Optional[str] = None
    native_language: Optional[str] = None
    daily_goal_minutes: Optional[int] = None
    notification_enabled: Optional[bool] = None


def create_access_token(data: dict, expires_delta: timedelta = None):
    """JWT 토큰 생성."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호 검증."""
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """비밀번호 해싱."""
    return pwd_context.hash(password)


@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate):
    """
    회원가입

    새로운 사용자를 등록합니다.
    """
    # 이메일 중복 체크 (실제 구현에서는 DB 조회)
    # ...

    user_id = str(uuid.uuid4())
    hashed_pw = hash_password(user.password)

    # 사용자 생성 (실제 구현에서는 DB 저장)
    new_user = {
        "id": user_id,
        "email": user.email,
        "name": user.name,
        "native_language": user.native_language,
        "hashed_password": hashed_pw,
        "is_premium": False,
        "created_at": datetime.utcnow()
    }

    return UserResponse(
        id=user_id,
        email=user.email,
        name=user.name,
        native_language=user.native_language,
        is_premium=False,
        created_at=datetime.utcnow()
    )


@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    로그인

    이메일/비밀번호로 로그인하고 JWT 토큰을 발급받습니다.
    """
    # 사용자 조회 및 비밀번호 검증 (실제 구현에서는 DB 조회)
    # user = await get_user_by_email(form_data.username)
    # if not user or not verify_password(form_data.password, user.hashed_password):
    #     raise HTTPException(status_code=401, detail="Invalid credentials")

    # 토큰 생성
    access_token = create_access_token(
        data={"sub": form_data.username, "user_id": "test_user_id"}
    )

    return TokenResponse(
        access_token=access_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    현재 사용자 정보

    토큰으로 인증된 사용자 정보를 반환합니다.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")

        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    # 사용자 조회 (실제 구현에서는 DB 조회)
    return UserResponse(
        id=user_id,
        email="user@example.com",
        name="Test User",
        native_language="ko",
        is_premium=False,
        created_at=datetime.utcnow()
    )


@router.put("/me")
async def update_profile(
    profile: ProfileUpdate,
    token: str = Depends(oauth2_scheme)
):
    """
    프로필 수정

    사용자 프로필을 업데이트합니다.
    """
    return {
        "message": "Profile updated successfully",
        "updated_fields": {k: v for k, v in profile.dict().items() if v is not None}
    }


@router.post("/me/languages/{language}")
async def add_target_language(
    language: str,
    token: str = Depends(oauth2_scheme)
):
    """
    학습 언어 추가

    새로운 학습 언어를 추가합니다.
    """
    if language not in settings.SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Unsupported language: {language}")

    return {
        "message": f"Language {language} added successfully",
        "learning_profile_id": str(uuid.uuid4())
    }


@router.delete("/me/languages/{language}")
async def remove_target_language(
    language: str,
    token: str = Depends(oauth2_scheme)
):
    """학습 언어 제거."""
    return {"message": f"Language {language} removed successfully"}


@router.post("/me/daily-goal")
async def set_daily_goal(
    goal_minutes: int,
    token: str = Depends(oauth2_scheme)
):
    """
    일일 목표 설정

    하루 학습 목표 시간(분)을 설정합니다.
    """
    if goal_minutes < 5 or goal_minutes > 120:
        raise HTTPException(status_code=400, detail="Daily goal must be between 5 and 120 minutes")

    return {
        "message": "Daily goal updated",
        "daily_goal_minutes": goal_minutes
    }


@router.post("/refresh")
async def refresh_token(token: str = Depends(oauth2_scheme)):
    """토큰 갱신."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
        email = payload.get("sub")

        new_token = create_access_token(data={"sub": email, "user_id": user_id})

        return TokenResponse(
            access_token=new_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    """
    로그아웃

    현재 세션을 종료합니다.
    (실제 구현에서는 토큰 블랙리스트에 추가)
    """
    return {"message": "Logged out successfully"}


@router.post("/password/reset-request")
async def request_password_reset(email: EmailStr):
    """비밀번호 재설정 요청."""
    return {"message": "Password reset email sent if account exists"}


@router.post("/password/reset")
async def reset_password(token: str, new_password: str):
    """비밀번호 재설정."""
    return {"message": "Password reset successfully"}

"""
MUSE Language - AI 기반 언어 학습 플랫폼

Features:
- AI 튜터와 실시간 대화 학습
- 음성 인식 기반 발음 평가
- 적응형 학습 알고리즘
- 게이미피케이션
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 생명주기 관리."""
    # 시작 시
    from app.services.ai.tutor import AITutor
    from app.services.speech.processor import SpeechProcessor

    app.state.ai_tutor = AITutor()
    app.state.speech_processor = SpeechProcessor()

    print("MUSE Language API started")
    yield

    # 종료 시
    print("MUSE Language API shutting down")


app = FastAPI(
    title="MUSE Language API",
    description="AI 기반 언어 학습 플랫폼",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """헬스 체크."""
    return {
        "status": "healthy",
        "service": "MUSE Language",
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """루트 엔드포인트."""
    return {
        "message": "Welcome to MUSE Language API",
        "docs": "/docs",
        "health": "/health"
    }

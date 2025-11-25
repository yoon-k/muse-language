"""
MUSE Language - API Router
"""

from fastapi import APIRouter

from app.api import sessions, lessons, vocabulary, pronunciation, progress, auth

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["Study Sessions"])
api_router.include_router(lessons.router, prefix="/lessons", tags=["Lessons"])
api_router.include_router(vocabulary.router, prefix="/vocabulary", tags=["Vocabulary"])
api_router.include_router(pronunciation.router, prefix="/pronunciation", tags=["Pronunciation"])
api_router.include_router(progress.router, prefix="/progress", tags=["Progress & Stats"])

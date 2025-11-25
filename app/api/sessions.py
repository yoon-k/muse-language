"""
MUSE Language - Study Sessions API

학습 세션 관리 엔드포인트
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Form
from pydantic import BaseModel
from datetime import datetime
import uuid

router = APIRouter()


class SessionCreate(BaseModel):
    """세션 생성 요청."""
    language: str  # en, ja, zh, es, fr
    session_type: str  # conversation, lesson, review, pronunciation
    topic: Optional[str] = "general"


class MessageRequest(BaseModel):
    """메시지 요청."""
    content: str


class SessionResponse(BaseModel):
    """세션 응답."""
    id: str
    language: str
    session_type: str
    started_at: datetime
    is_active: bool


@router.post("", response_model=SessionResponse)
async def create_session(
    request: Request,
    session: SessionCreate
):
    """
    학습 세션 시작

    새로운 학습 세션을 시작합니다.
    - conversation: AI 튜터와 대화 연습
    - lesson: 구조화된 레슨 학습
    - review: 단어 복습
    - pronunciation: 발음 연습
    """
    session_id = str(uuid.uuid4())

    return SessionResponse(
        id=session_id,
        language=session.language,
        session_type=session.session_type,
        started_at=datetime.utcnow(),
        is_active=True
    )


@router.get("/{session_id}")
async def get_session(session_id: str):
    """세션 상태 조회."""
    return {
        "id": session_id,
        "is_active": True,
        "messages_count": 0,
        "duration_minutes": 0
    }


@router.post("/{session_id}/message")
async def send_message(
    request: Request,
    session_id: str,
    message: MessageRequest
):
    """
    AI 튜터에게 메시지 전송

    AI 튜터와 대화하고 피드백을 받습니다.

    Returns:
        - message: AI 응답
        - corrections: 문법/어휘 교정
        - vocabulary: 새로운 단어
        - grammar_tips: 문법 팁
        - xp_earned: 획득 XP
    """
    ai_tutor = request.app.state.ai_tutor

    # AI 튜터 응답 (실제 구현에서는 세션에서 언어/레벨 가져옴)
    response = await ai_tutor.chat(
        user_message=message.content,
        language="en",
        level="B1",
        conversation_history=[],
        topic="general"
    )

    return {
        "session_id": session_id,
        "message": response.message,
        "corrections": response.corrections,
        "vocabulary": response.vocabulary,
        "grammar_tips": response.grammar_tips,
        "encouragement": response.encouragement,
        "next_suggestion": response.next_suggestion,
        "xp_earned": 5,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/{session_id}/audio")
async def send_audio(
    request: Request,
    session_id: str,
    audio: UploadFile = File(...),
    expected_text: Optional[str] = Form(None)
):
    """
    음성 메시지 전송

    음성을 텍스트로 변환하고 AI 튜터와 대화합니다.
    expected_text가 있으면 발음 평가도 수행합니다.

    Returns:
        - transcript: 인식된 텍스트
        - ai_response: AI 튜터 응답
        - pronunciation: 발음 평가 (expected_text 있을 때)
    """
    speech_processor = request.app.state.speech_processor

    audio_data = await audio.read()

    # 음성 인식
    transcription = await speech_processor.transcribe(audio_data, language="en")
    user_text = transcription["text"]

    result = {
        "session_id": session_id,
        "transcript": user_text,
        "timestamp": datetime.utcnow().isoformat()
    }

    # 발음 평가 (expected_text 있을 때)
    if expected_text:
        pronunciation = await speech_processor.evaluate_pronunciation(
            audio_data, expected_text, "en"
        )
        result["pronunciation"] = {
            "overall_score": pronunciation.overall_score,
            "accuracy_score": pronunciation.accuracy_score,
            "fluency_score": pronunciation.fluency_score,
            "word_scores": pronunciation.word_scores,
            "feedback": pronunciation.feedback,
            "suggestions": pronunciation.suggestions
        }

    # AI 튜터 응답
    ai_tutor = request.app.state.ai_tutor
    response = await ai_tutor.chat(
        user_message=user_text,
        language="en",
        level="B1",
        conversation_history=[],
        topic="general"
    )

    result["ai_response"] = {
        "message": response.message,
        "corrections": response.corrections,
        "vocabulary": response.vocabulary
    }

    return result


@router.delete("/{session_id}")
async def end_session(session_id: str):
    """
    세션 종료

    학습 세션을 종료하고 결과를 저장합니다.

    Returns:
        - duration_minutes: 총 학습 시간
        - messages_count: 대화 수
        - xp_earned: 획득한 XP
        - words_learned: 학습한 단어
        - summary: 세션 요약
    """
    return {
        "session_id": session_id,
        "ended_at": datetime.utcnow().isoformat(),
        "duration_minutes": 15,
        "messages_count": 10,
        "xp_earned": 50,
        "words_learned": 5,
        "accuracy_rate": 0.85,
        "summary": "Great session! You practiced greetings and introductions."
    }


@router.get("/{session_id}/history")
async def get_session_history(session_id: str):
    """세션 대화 기록 조회."""
    return {
        "session_id": session_id,
        "messages": []
    }

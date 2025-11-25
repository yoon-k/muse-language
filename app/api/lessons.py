"""
MUSE Language - Lessons API

레슨 관리 엔드포인트
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()


class LessonResponse(BaseModel):
    """레슨 응답."""
    id: str
    language: str
    level: str
    title: str
    description: str
    category: str
    estimated_minutes: int
    xp_reward: int
    is_completed: bool = False
    is_locked: bool = False


@router.get("", response_model=List[LessonResponse])
async def list_lessons(
    language: str = Query(..., description="학습 언어 (en, ja, zh, es, fr)"),
    level: Optional[str] = Query(None, description="레벨 필터 (A1-C2)"),
    category: Optional[str] = Query(None, description="카테고리 필터"),
    limit: int = Query(20, le=50)
):
    """
    레슨 목록 조회

    사용자 레벨에 맞는 레슨 목록을 반환합니다.

    Categories:
    - grammar: 문법
    - vocabulary: 어휘
    - conversation: 회화
    - reading: 독해
    - listening: 청취
    - writing: 작문
    """
    # 샘플 레슨 목록
    lessons = [
        LessonResponse(
            id="lesson_001",
            language=language,
            level="A1",
            title="Basic Greetings",
            description="Learn how to greet people in everyday situations",
            category="conversation",
            estimated_minutes=10,
            xp_reward=20,
            is_completed=True
        ),
        LessonResponse(
            id="lesson_002",
            language=language,
            level="A1",
            title="Introducing Yourself",
            description="Learn to introduce yourself and talk about basic personal information",
            category="conversation",
            estimated_minutes=15,
            xp_reward=25
        ),
        LessonResponse(
            id="lesson_003",
            language=language,
            level="A1",
            title="Present Simple Tense",
            description="Master the present simple tense for everyday actions",
            category="grammar",
            estimated_minutes=20,
            xp_reward=30
        ),
        LessonResponse(
            id="lesson_004",
            language=language,
            level="A1",
            title="Numbers and Counting",
            description="Learn numbers 1-100 and how to count",
            category="vocabulary",
            estimated_minutes=15,
            xp_reward=20
        ),
        LessonResponse(
            id="lesson_005",
            language=language,
            level="A2",
            title="Past Simple Tense",
            description="Learn to talk about past events and experiences",
            category="grammar",
            estimated_minutes=25,
            xp_reward=35,
            is_locked=True
        )
    ]

    # 필터 적용
    if level:
        lessons = [l for l in lessons if l.level == level]
    if category:
        lessons = [l for l in lessons if l.category == category]

    return lessons[:limit]


@router.get("/{lesson_id}")
async def get_lesson(lesson_id: str):
    """
    레슨 상세 조회

    레슨의 전체 콘텐츠를 반환합니다.

    Returns:
        - info: 레슨 기본 정보
        - sections: 레슨 섹션들
        - exercises: 연습 문제
        - vocabulary: 핵심 어휘
    """
    return {
        "id": lesson_id,
        "language": "en",
        "level": "A1",
        "title": "Basic Greetings",
        "description": "Learn how to greet people in everyday situations",
        "category": "conversation",
        "estimated_minutes": 10,
        "xp_reward": 20,

        "sections": [
            {
                "id": "section_1",
                "type": "introduction",
                "title": "Introduction",
                "content": "In this lesson, you'll learn common greetings used in English-speaking countries."
            },
            {
                "id": "section_2",
                "type": "vocabulary",
                "title": "Key Phrases",
                "items": [
                    {"phrase": "Hello", "translation": "안녕하세요", "audio_url": None},
                    {"phrase": "Good morning", "translation": "좋은 아침", "audio_url": None},
                    {"phrase": "How are you?", "translation": "어떻게 지내세요?", "audio_url": None},
                    {"phrase": "Nice to meet you", "translation": "만나서 반갑습니다", "audio_url": None}
                ]
            },
            {
                "id": "section_3",
                "type": "dialogue",
                "title": "Example Dialogue",
                "dialogue": [
                    {"speaker": "A", "text": "Hello! How are you?"},
                    {"speaker": "B", "text": "I'm fine, thank you. And you?"},
                    {"speaker": "A", "text": "I'm great, thanks!"}
                ]
            },
            {
                "id": "section_4",
                "type": "grammar",
                "title": "Grammar Note",
                "content": "In English, we often use contractions in informal speech: 'I am' → 'I'm', 'How are' → 'How're'"
            }
        ],

        "exercises": [
            {
                "id": "ex_1",
                "type": "multiple_choice",
                "question": "What is the correct response to 'How are you?'",
                "options": [
                    "I'm fine, thank you",
                    "My name is John",
                    "Nice to meet you",
                    "Goodbye"
                ],
                "correct_answer": 0,
                "explanation": "'I'm fine, thank you' is the standard response to 'How are you?'"
            },
            {
                "id": "ex_2",
                "type": "fill_blank",
                "question": "Complete the dialogue: A: Hello! B: ___!",
                "correct_answer": "Hello",
                "hint": "The most common response to 'Hello'"
            },
            {
                "id": "ex_3",
                "type": "matching",
                "question": "Match the greetings with their meanings",
                "pairs": [
                    {"left": "Good morning", "right": "Used before noon"},
                    {"left": "Good afternoon", "right": "Used after noon"},
                    {"left": "Good evening", "right": "Used in the evening"}
                ]
            },
            {
                "id": "ex_4",
                "type": "speaking",
                "question": "Practice saying: 'Hello, nice to meet you!'",
                "target_text": "Hello, nice to meet you!",
                "min_score": 70
            }
        ],

        "vocabulary": [
            {"word": "Hello", "meaning": "인사말", "example": "Hello, how are you?"},
            {"word": "morning", "meaning": "아침", "example": "Good morning!"},
            {"word": "nice", "meaning": "좋은, 멋진", "example": "Nice to meet you."},
            {"word": "meet", "meaning": "만나다", "example": "Nice to meet you."}
        ]
    }


@router.post("/{lesson_id}/complete")
async def complete_lesson(
    lesson_id: str,
    score: int = Query(..., ge=0, le=100, description="레슨 점수")
):
    """
    레슨 완료 처리

    레슨을 완료하고 XP와 진도를 업데이트합니다.

    Returns:
        - xp_earned: 획득 XP
        - achievements: 새로 획득한 업적
        - level_up: 레벨업 여부
        - next_lesson: 다음 추천 레슨
    """
    # XP 계산 (점수에 따른 보너스)
    base_xp = 20
    bonus_xp = int(score / 10)  # 최대 10 추가
    total_xp = base_xp + bonus_xp

    return {
        "lesson_id": lesson_id,
        "completed_at": datetime.utcnow().isoformat(),
        "score": score,
        "xp_earned": total_xp,
        "is_perfect": score == 100,
        "achievements": [],
        "level_up": False,
        "next_lesson": {
            "id": "lesson_002",
            "title": "Introducing Yourself"
        },
        "feedback": "Great job completing this lesson!" if score >= 70 else "Keep practicing to improve your score!"
    }


@router.get("/{lesson_id}/exercises")
async def get_lesson_exercises(lesson_id: str):
    """레슨 연습 문제만 조회."""
    return {
        "lesson_id": lesson_id,
        "exercises": []
    }


@router.post("/{lesson_id}/exercises/{exercise_id}/submit")
async def submit_exercise_answer(
    lesson_id: str,
    exercise_id: str,
    answer: str
):
    """
    연습 문제 답안 제출

    Returns:
        - is_correct: 정답 여부
        - correct_answer: 정답
        - explanation: 설명
        - xp_earned: 획득 XP
    """
    return {
        "exercise_id": exercise_id,
        "is_correct": True,
        "user_answer": answer,
        "correct_answer": answer,
        "explanation": "Correct! Well done.",
        "xp_earned": 5
    }

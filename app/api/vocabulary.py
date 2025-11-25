"""
MUSE Language - Vocabulary API

단어장 및 복습 엔드포인트
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel
from datetime import datetime
import uuid

router = APIRouter()


class WordAdd(BaseModel):
    """단어 추가 요청."""
    word: str
    language: str
    translation: Optional[str] = None


class ReviewAnswer(BaseModel):
    """복습 답변."""
    word_id: str
    quality: int  # 0-5 (SM-2 품질)
    response_time_ms: int


@router.get("")
async def get_vocabulary(
    language: str = Query(..., description="언어"),
    status: Optional[str] = Query(None, description="학습 상태 (learning/mastered/due)"),
    limit: int = Query(50, le=200)
):
    """
    단어장 조회

    사용자의 단어장을 조회합니다.

    Status:
    - learning: 학습 중인 단어
    - mastered: 숙달한 단어
    - due: 복습 필요한 단어
    """
    words = [
        {
            "id": "word_001",
            "word": "apple",
            "language": language,
            "translation": "사과",
            "pronunciation": "/ˈæp.əl/",
            "example": "I eat an apple every day.",
            "mastery_level": 75,
            "status": "learning",
            "next_review": datetime.utcnow().isoformat(),
            "times_reviewed": 5
        },
        {
            "id": "word_002",
            "word": "beautiful",
            "language": language,
            "translation": "아름다운",
            "pronunciation": "/ˈbjuː.tɪ.fəl/",
            "example": "What a beautiful day!",
            "mastery_level": 90,
            "status": "mastered",
            "next_review": None,
            "times_reviewed": 12
        },
        {
            "id": "word_003",
            "word": "challenge",
            "language": language,
            "translation": "도전",
            "pronunciation": "/ˈtʃæl.ɪndʒ/",
            "example": "Learning a new language is a challenge.",
            "mastery_level": 45,
            "status": "due",
            "next_review": datetime.utcnow().isoformat(),
            "times_reviewed": 3
        }
    ]

    if status:
        words = [w for w in words if w["status"] == status]

    return {
        "total": len(words),
        "words": words[:limit],
        "stats": {
            "total_words": len(words),
            "mastered": 1,
            "learning": 1,
            "due_today": 1
        }
    }


@router.post("")
async def add_word(request: Request, word_data: WordAdd):
    """
    단어 추가

    단어장에 새 단어를 추가합니다.
    AI가 자동으로 발음, 예문, 번역을 생성합니다.
    """
    ai_tutor = request.app.state.ai_tutor

    # AI로 단어 정보 생성
    word_info = await ai_tutor.explain_word(
        word=word_data.word,
        language=word_data.language,
        user_native_language="ko"
    )

    word_id = str(uuid.uuid4())

    return {
        "id": word_id,
        "word": word_data.word,
        "language": word_data.language,
        "translation": word_info.get("definitions", [{}])[0].get("translation", word_data.translation),
        "pronunciation": word_info.get("pronunciation", ""),
        "part_of_speech": word_info.get("part_of_speech", ""),
        "examples": word_info.get("examples", []),
        "synonyms": word_info.get("synonyms", []),
        "added_at": datetime.utcnow().isoformat(),
        "mastery_level": 0,
        "next_review": datetime.utcnow().isoformat()
    }


@router.get("/{word_id}")
async def get_word_detail(word_id: str):
    """단어 상세 조회."""
    return {
        "id": word_id,
        "word": "example",
        "language": "en",
        "translation": "예시",
        "pronunciation": "/ɪɡˈzæm.pəl/",
        "part_of_speech": "noun",
        "definitions": [
            {"meaning": "a thing characteristic of its kind", "translation": "그 종류의 특징적인 것"}
        ],
        "examples": [
            {"sentence": "This is a good example.", "translation": "이것은 좋은 예시입니다."}
        ],
        "synonyms": ["instance", "specimen"],
        "antonyms": [],
        "related_words": ["exemplify", "exemplary"],
        "srs_data": {
            "ease_factor": 2.5,
            "interval_days": 3,
            "repetitions": 4,
            "mastery_level": 65
        },
        "history": [
            {"date": "2024-01-15", "quality": 4, "response_time_ms": 2500},
            {"date": "2024-01-12", "quality": 3, "response_time_ms": 4000}
        ]
    }


@router.delete("/{word_id}")
async def delete_word(word_id: str):
    """단어 삭제."""
    return {"deleted": True, "word_id": word_id}


@router.get("/review/due")
async def get_due_reviews(
    language: str = Query(...),
    limit: int = Query(20, le=50)
):
    """
    복습 필요한 단어 조회

    간격 반복 알고리즘에 따라 오늘 복습할 단어를 반환합니다.
    """
    return {
        "due_count": 15,
        "new_count": 5,
        "cards": [
            {
                "id": "word_003",
                "word": "challenge",
                "language": language,
                "card_type": "review",  # review or new
                "front": "challenge",
                "back": "도전",
                "hint": "도... 으로 시작",
                "audio_url": None
            },
            {
                "id": "word_004",
                "word": "opportunity",
                "language": language,
                "card_type": "new",
                "front": "opportunity",
                "back": "기회",
                "hint": None,
                "audio_url": None
            }
        ]
    }


@router.post("/review/submit")
async def submit_review(answers: List[ReviewAnswer]):
    """
    복습 결과 제출

    복습 결과를 제출하고 다음 복습 일정을 계산합니다.

    Quality (SM-2):
    - 0: 전혀 기억 못함
    - 1: 틀렸지만 정답 보고 기억남
    - 2: 틀렸지만 쉽게 떠올림
    - 3: 맞았지만 어려웠음
    - 4: 맞았고 약간 망설임
    - 5: 완벽하게 기억
    """
    results = []

    for answer in answers:
        # SRS 계산 (실제 구현에서는 SRS 엔진 사용)
        is_correct = answer.quality >= 3

        results.append({
            "word_id": answer.word_id,
            "quality": answer.quality,
            "is_correct": is_correct,
            "new_interval_days": 3 if is_correct else 1,
            "new_ease_factor": 2.5,
            "xp_earned": 3 if is_correct else 1
        })

    total_xp = sum(r["xp_earned"] for r in results)
    correct_count = sum(1 for r in results if r["is_correct"])

    return {
        "reviewed_count": len(answers),
        "correct_count": correct_count,
        "accuracy": correct_count / len(answers) if answers else 0,
        "xp_earned": total_xp,
        "results": results,
        "remaining_due": 10,
        "encouragement": "Great review session!" if correct_count / len(answers) > 0.7 else "Keep practicing!"
    }


@router.get("/stats")
async def get_vocabulary_stats(language: str = Query(...)):
    """단어장 통계."""
    return {
        "language": language,
        "total_words": 150,
        "mastered": 45,
        "learning": 80,
        "new": 25,
        "due_today": 15,
        "reviewed_today": 20,
        "accuracy_7days": 0.82,
        "words_by_level": {
            "A1": 50,
            "A2": 40,
            "B1": 35,
            "B2": 20,
            "C1": 5,
            "C2": 0
        },
        "review_forecast": [
            {"date": "2024-01-16", "due": 15},
            {"date": "2024-01-17", "due": 22},
            {"date": "2024-01-18", "due": 18},
            {"date": "2024-01-19", "due": 12},
            {"date": "2024-01-20", "due": 8}
        ]
    }

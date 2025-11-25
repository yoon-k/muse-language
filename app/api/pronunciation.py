"""
MUSE Language - Pronunciation API

발음 평가 및 연습 엔드포인트
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Form, Query
from datetime import datetime

router = APIRouter()


@router.post("/evaluate")
async def evaluate_pronunciation(
    request: Request,
    audio: UploadFile = File(..., description="발음 음성 파일"),
    text: str = Form(..., description="읽어야 할 텍스트"),
    language: str = Form("en", description="언어 코드")
):
    """
    발음 평가

    음성 파일을 분석하여 발음 정확도를 평가합니다.

    Returns:
        - overall_score: 종합 점수 (0-100)
        - accuracy_score: 정확도 점수
        - fluency_score: 유창성 점수
        - completeness_score: 완성도 점수
        - word_scores: 단어별 점수
        - feedback: 피드백 메시지
        - suggestions: 개선 제안
    """
    speech_processor = request.app.state.speech_processor

    audio_data = await audio.read()

    result = await speech_processor.evaluate_pronunciation(
        audio_data=audio_data,
        expected_text=text,
        language=language
    )

    return {
        "evaluated_at": datetime.utcnow().isoformat(),
        "expected_text": text,
        "transcript": result.transcript,
        "overall_score": result.overall_score,
        "accuracy_score": result.accuracy_score,
        "fluency_score": result.fluency_score,
        "completeness_score": result.completeness_score,
        "word_scores": result.word_scores,
        "phoneme_errors": result.phoneme_errors,
        "feedback": result.feedback,
        "suggestions": result.suggestions,
        "xp_earned": int(result.overall_score / 10),
        "is_passed": result.overall_score >= 70
    }


@router.get("/word/{word}")
async def get_word_pronunciation(
    request: Request,
    word: str,
    language: str = Query("en", description="언어")
):
    """
    단어 발음 정보

    단어의 발음 기호, 음절, 오디오를 제공합니다.
    """
    speech_processor = request.app.state.speech_processor

    result = await speech_processor.get_word_pronunciation(word, language)

    return {
        "word": word,
        "language": language,
        "ipa": result.get("ipa", ""),
        "syllables": result.get("syllables", []),
        "audio_base64": result.get("audio_base64", ""),
        "tips": f"Focus on clear pronunciation of each syllable"
    }


@router.post("/practice")
async def start_pronunciation_practice(
    language: str = Form(...),
    level: str = Form("A1"),
    focus: Optional[str] = Form(None, description="연습 포커스 (vowels, consonants, intonation)")
):
    """
    발음 연습 시작

    레벨에 맞는 발음 연습 문장을 제공합니다.
    """
    # 레벨별 연습 문장
    practice_sentences = {
        "A1": [
            {"id": "p1", "text": "Hello, how are you?", "focus": "greeting"},
            {"id": "p2", "text": "My name is John.", "focus": "introduction"},
            {"id": "p3", "text": "Nice to meet you.", "focus": "greeting"},
            {"id": "p4", "text": "I like coffee.", "focus": "preference"},
            {"id": "p5", "text": "Thank you very much.", "focus": "politeness"}
        ],
        "A2": [
            {"id": "p6", "text": "I would like a cup of tea, please.", "focus": "ordering"},
            {"id": "p7", "text": "Where is the nearest station?", "focus": "directions"},
            {"id": "p8", "text": "I have been studying English for two years.", "focus": "duration"},
            {"id": "p9", "text": "Could you repeat that, please?", "focus": "clarification"},
            {"id": "p10", "text": "The weather is beautiful today.", "focus": "weather"}
        ],
        "B1": [
            {"id": "p11", "text": "I'm looking forward to meeting you.", "focus": "anticipation"},
            {"id": "p12", "text": "In my opinion, learning languages is important.", "focus": "opinion"},
            {"id": "p13", "text": "If I had more time, I would travel more.", "focus": "conditional"},
            {"id": "p14", "text": "The conference has been postponed until next week.", "focus": "passive"},
            {"id": "p15", "text": "Despite the rain, we decided to go hiking.", "focus": "contrast"}
        ]
    }

    sentences = practice_sentences.get(level, practice_sentences["A1"])

    return {
        "practice_id": f"practice_{datetime.utcnow().timestamp()}",
        "language": language,
        "level": level,
        "focus": focus,
        "sentences": sentences,
        "total_sentences": len(sentences),
        "tip": "Speak clearly and at a natural pace. Focus on vowel sounds."
    }


@router.get("/history")
async def get_pronunciation_history(
    language: str = Query(...),
    limit: int = Query(20, le=50)
):
    """발음 연습 기록 조회."""
    return {
        "total_practices": 45,
        "average_score": 78.5,
        "improvement": "+5.2%",
        "history": [
            {
                "id": "hist_001",
                "date": "2024-01-15T10:30:00Z",
                "text": "Hello, how are you?",
                "overall_score": 85,
                "accuracy_score": 88,
                "fluency_score": 82
            },
            {
                "id": "hist_002",
                "date": "2024-01-15T10:25:00Z",
                "text": "Nice to meet you.",
                "overall_score": 72,
                "accuracy_score": 75,
                "fluency_score": 68
            }
        ],
        "weak_sounds": ["th", "r", "v"],
        "strong_sounds": ["s", "t", "k"],
        "recommendations": [
            "Practice 'th' sound: 'this', 'that', 'think'",
            "Focus on 'r' pronunciation at the end of words"
        ]
    }


@router.get("/challenges")
async def get_pronunciation_challenges(language: str = Query(...)):
    """
    발음 챌린지 목록

    도전적인 발음 연습을 제공합니다.
    """
    return {
        "daily_challenge": {
            "id": "challenge_daily",
            "title": "Tongue Twister Tuesday",
            "text": "She sells seashells by the seashore.",
            "difficulty": "medium",
            "xp_reward": 30,
            "attempts_today": 0
        },
        "challenges": [
            {
                "id": "challenge_001",
                "title": "Minimal Pairs: Ship vs Sheep",
                "description": "Practice distinguishing similar sounds",
                "words": ["ship", "sheep", "chip", "cheap"],
                "difficulty": "easy",
                "xp_reward": 15
            },
            {
                "id": "challenge_002",
                "title": "Fast Speech",
                "description": "Speak naturally at native speed",
                "text": "I would have thought that they had already left.",
                "difficulty": "hard",
                "xp_reward": 40
            },
            {
                "id": "challenge_003",
                "title": "Intonation Pattern",
                "description": "Match the intonation of a native speaker",
                "text": "Are you coming to the party tonight?",
                "difficulty": "medium",
                "xp_reward": 25
            }
        ]
    }


@router.post("/tts")
async def text_to_speech(
    request: Request,
    text: str = Form(...),
    voice: str = Form("alloy", description="음성 종류"),
    speed: float = Form(1.0, ge=0.5, le=2.0)
):
    """
    텍스트 음성 변환 (TTS)

    텍스트를 원어민 발음 오디오로 변환합니다.

    Voices:
    - alloy: 중성적
    - echo: 남성
    - fable: 영국 발음
    - onyx: 깊은 남성
    - nova: 여성
    - shimmer: 여성 (밝은)
    """
    speech_processor = request.app.state.speech_processor

    import base64
    audio_data = await speech_processor.synthesize(text, voice, speed)
    audio_base64 = base64.b64encode(audio_data).decode()

    return {
        "text": text,
        "voice": voice,
        "speed": speed,
        "audio_base64": audio_base64,
        "audio_format": "mp3"
    }

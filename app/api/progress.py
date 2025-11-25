"""
MUSE Language - Progress & Stats API

학습 진도 및 통계 엔드포인트
"""

from typing import Optional
from fastapi import APIRouter, Query
from datetime import datetime, timedelta

router = APIRouter()


@router.get("")
async def get_progress(language: str = Query(...)):
    """
    학습 진도 조회

    전체 학습 진도와 현재 상태를 반환합니다.
    """
    return {
        "language": language,
        "level": {
            "current": "A2",
            "progress_percent": 65,
            "xp_for_next_level": 350
        },
        "streak": {
            "current": 7,
            "longest": 23,
            "is_today_complete": True
        },
        "today": {
            "study_minutes": 25,
            "lessons_completed": 2,
            "words_reviewed": 15,
            "xp_earned": 85,
            "daily_goal_progress": 70  # percent
        },
        "total": {
            "study_time_hours": 45,
            "lessons_completed": 42,
            "words_learned": 350,
            "words_mastered": 120,
            "conversations": 28
        },
        "skills": {
            "vocabulary": 72,
            "grammar": 65,
            "listening": 58,
            "speaking": 55,
            "reading": 70,
            "writing": 48
        }
    }


@router.get("/stats")
async def get_detailed_stats(
    language: str = Query(...),
    period: str = Query("week", description="기간 (day, week, month, all)")
):
    """
    상세 학습 통계

    기간별 상세 학습 통계를 반환합니다.
    """
    # 일주일 데이터 예시
    daily_data = []
    base_date = datetime.utcnow()

    for i in range(7):
        date = base_date - timedelta(days=6-i)
        daily_data.append({
            "date": date.strftime("%Y-%m-%d"),
            "study_minutes": 20 + (i * 5) % 30,
            "xp_earned": 50 + (i * 10) % 50,
            "words_reviewed": 10 + (i * 3) % 15,
            "accuracy": 0.75 + (i * 0.02) % 0.2
        })

    return {
        "period": period,
        "language": language,
        "summary": {
            "total_study_minutes": sum(d["study_minutes"] for d in daily_data),
            "total_xp": sum(d["xp_earned"] for d in daily_data),
            "average_accuracy": 0.82,
            "best_day": "2024-01-15",
            "most_active_hour": 20  # 8 PM
        },
        "daily_data": daily_data,
        "comparisons": {
            "vs_last_period": "+15%",
            "vs_average": "+8%"
        },
        "insights": [
            "You're most productive in the evening",
            "Your vocabulary is improving faster than grammar",
            "You've maintained a 7-day streak!"
        ]
    }


@router.get("/achievements")
async def get_achievements():
    """
    업적 목록

    획득한 업적과 진행 중인 업적을 반환합니다.
    """
    return {
        "total_achievements": 45,
        "earned_count": 12,
        "total_xp_from_achievements": 850,
        "earned": [
            {
                "id": "streak_7",
                "name": "일주일 완주",
                "description": "7일 연속 학습",
                "icon": "🔥",
                "xp_reward": 100,
                "earned_at": "2024-01-15T10:30:00Z",
                "rarity": "common"
            },
            {
                "id": "words_50",
                "name": "단어 수집가",
                "description": "50개 단어 학습",
                "icon": "📚",
                "xp_reward": 50,
                "earned_at": "2024-01-10T15:20:00Z",
                "rarity": "common"
            },
            {
                "id": "first_lesson",
                "name": "첫 발자국",
                "description": "첫 레슨 완료",
                "icon": "👣",
                "xp_reward": 20,
                "earned_at": "2024-01-01T09:00:00Z",
                "rarity": "common"
            }
        ],
        "in_progress": [
            {
                "id": "streak_30",
                "name": "한 달 마스터",
                "description": "30일 연속 학습",
                "icon": "🏆",
                "xp_reward": 500,
                "progress": 7,
                "target": 30,
                "percent": 23
            },
            {
                "id": "words_200",
                "name": "어휘 전문가",
                "description": "200개 단어 학습",
                "icon": "🎓",
                "xp_reward": 150,
                "progress": 150,
                "target": 200,
                "percent": 75
            }
        ],
        "locked": [
            {
                "id": "streak_365",
                "name": "언어 전사",
                "description": "365일 연속 학습",
                "icon": "⚔️",
                "xp_reward": 5000,
                "rarity": "legendary",
                "hint": "Keep your streak going for a full year!"
            }
        ]
    }


@router.get("/leaderboard")
async def get_leaderboard(
    language: str = Query(...),
    period: str = Query("week", description="기간 (week, month, all)")
):
    """
    리더보드

    XP 기준 랭킹을 반환합니다.
    """
    return {
        "period": period,
        "language": language,
        "my_rank": 42,
        "my_tier": "Gold",
        "my_xp": 1250,
        "total_participants": 5000,
        "top_users": [
            {"rank": 1, "name": "LanguageMaster", "xp": 3500, "tier": "Diamond", "streak": 45},
            {"rank": 2, "name": "WordWizard", "xp": 3200, "tier": "Diamond", "streak": 38},
            {"rank": 3, "name": "GrammarGuru", "xp": 2900, "tier": "Platinum", "streak": 30},
            {"rank": 4, "name": "SpeakEasy", "xp": 2750, "tier": "Platinum", "streak": 28},
            {"rank": 5, "name": "LingoPro", "xp": 2600, "tier": "Platinum", "streak": 25}
        ],
        "nearby_users": [
            {"rank": 40, "name": "LearnerX", "xp": 1300, "tier": "Gold"},
            {"rank": 41, "name": "StudyBuddy", "xp": 1275, "tier": "Gold"},
            {"rank": 42, "name": "You", "xp": 1250, "tier": "Gold", "is_me": True},
            {"rank": 43, "name": "NewLearner", "xp": 1220, "tier": "Gold"},
            {"rank": 44, "name": "VocabKing", "xp": 1200, "tier": "Gold"}
        ],
        "tier_info": {
            "Diamond": {"min_percentile": 1, "color": "#b9f2ff"},
            "Platinum": {"min_percentile": 5, "color": "#e5e4e2"},
            "Gold": {"min_percentile": 15, "color": "#ffd700"},
            "Silver": {"min_percentile": 35, "color": "#c0c0c0"},
            "Bronze": {"min_percentile": 100, "color": "#cd7f32"}
        }
    }


@router.get("/daily-goals")
async def get_daily_goals():
    """
    일일 목표

    오늘의 학습 목표와 진행 상황을 반환합니다.
    """
    return {
        "date": datetime.utcnow().date().isoformat(),
        "goal_xp": 50,
        "earned_xp": 35,
        "progress_percent": 70,
        "is_complete": False,
        "streak_at_risk": False,
        "challenges": [
            {
                "id": "daily_lesson",
                "title": "레슨 1개 완료",
                "target": 1,
                "current": 1,
                "is_complete": True,
                "xp_reward": 20
            },
            {
                "id": "daily_vocabulary",
                "title": "단어 10개 복습",
                "target": 10,
                "current": 8,
                "is_complete": False,
                "xp_reward": 15
            },
            {
                "id": "daily_conversation",
                "title": "AI와 3회 대화",
                "target": 3,
                "current": 1,
                "is_complete": False,
                "xp_reward": 15
            }
        ],
        "bonus_challenge": {
            "title": "모든 목표 달성",
            "xp_reward": 30,
            "is_available": False
        },
        "time_remaining": "5h 30m"
    }


@router.get("/recommendations")
async def get_recommendations(language: str = Query(...)):
    """
    맞춤 추천

    사용자 학습 패턴 기반 추천을 제공합니다.
    """
    return {
        "language": language,
        "next_lesson": {
            "id": "lesson_015",
            "title": "Past Simple Tense",
            "reason": "Based on your grammar progress"
        },
        "words_to_review": 15,
        "weak_areas": [
            {
                "skill": "speaking",
                "score": 55,
                "recommendation": "Practice more conversation with AI tutor",
                "suggested_activity": "10-minute conversation practice"
            },
            {
                "skill": "listening",
                "score": 58,
                "recommendation": "Listen to more native audio",
                "suggested_activity": "Complete 2 listening exercises"
            }
        ],
        "strong_areas": [
            {"skill": "vocabulary", "score": 72},
            {"skill": "reading", "score": 70}
        ],
        "study_tip": "You learn best in the evening. Try scheduling your practice sessions after 7 PM.",
        "motivation": "You're making great progress! Just 2 more days to reach your weekly goal."
    }

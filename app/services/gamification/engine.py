"""
MUSE Language - Gamification Engine

게이미피케이션 시스템
- XP & 레벨 시스템
- 스트릭 관리
- 업적 시스템
- 리더보드
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import uuid


@dataclass
class XPEvent:
    """XP 획득 이벤트."""
    event_type: str
    xp_amount: int
    multiplier: float = 1.0
    bonus_reason: Optional[str] = None


class GamificationEngine:
    """
    게이미피케이션 엔진

    기능:
    - XP 계산 및 레벨업
    - 일일/주간 스트릭
    - 업적 해금
    - 리더보드 관리
    """

    # XP 기준
    XP_VALUES = {
        "lesson_complete": 20,
        "conversation_message": 5,
        "word_learned": 3,
        "word_mastered": 10,
        "pronunciation_practice": 8,
        "daily_goal_met": 30,
        "streak_bonus": 5,  # 스트릭 일수당 보너스
        "perfect_score": 25,
        "first_lesson_of_day": 15,
        "challenge_complete": 50,
    }

    # 레벨별 필요 XP
    LEVEL_THRESHOLDS = [
        0,      # Level 1
        100,    # Level 2
        300,    # Level 3
        600,    # Level 4
        1000,   # Level 5
        1500,   # Level 6
        2100,   # Level 7
        2800,   # Level 8
        3600,   # Level 9
        4500,   # Level 10
        5500,   # Level 11
        6600,   # Level 12
        7800,   # Level 13
        9100,   # Level 14
        10500,  # Level 15
        12000,  # Level 16
        13600,  # Level 17
        15300,  # Level 18
        17100,  # Level 19
        19000,  # Level 20+
    ]

    # 업적 정의
    ACHIEVEMENTS = {
        # 스트릭 관련
        "streak_3": {"name": "3일 연속", "desc": "3일 연속 학습", "condition": ("streak", 3), "xp": 50},
        "streak_7": {"name": "일주일 완주", "desc": "7일 연속 학습", "condition": ("streak", 7), "xp": 100},
        "streak_30": {"name": "한 달 마스터", "desc": "30일 연속 학습", "condition": ("streak", 30), "xp": 500},
        "streak_100": {"name": "백일장", "desc": "100일 연속 학습", "condition": ("streak", 100), "xp": 1000},
        "streak_365": {"name": "언어 전사", "desc": "365일 연속 학습", "condition": ("streak", 365), "xp": 5000},

        # 단어 관련
        "words_50": {"name": "단어 수집가", "desc": "50개 단어 학습", "condition": ("words", 50), "xp": 50},
        "words_200": {"name": "어휘 전문가", "desc": "200개 단어 학습", "condition": ("words", 200), "xp": 150},
        "words_500": {"name": "사전 마스터", "desc": "500개 단어 학습", "condition": ("words", 500), "xp": 300},
        "words_1000": {"name": "언어학자", "desc": "1000개 단어 학습", "condition": ("words", 1000), "xp": 500},

        # 레슨 관련
        "lessons_10": {"name": "학습 시작", "desc": "10개 레슨 완료", "condition": ("lessons", 10), "xp": 50},
        "lessons_50": {"name": "열정 학습자", "desc": "50개 레슨 완료", "condition": ("lessons", 50), "xp": 200},
        "lessons_100": {"name": "레슨 마스터", "desc": "100개 레슨 완료", "condition": ("lessons", 100), "xp": 400},

        # 대화 관련
        "conversations_10": {"name": "대화 시작", "desc": "10회 AI 대화", "condition": ("conversations", 10), "xp": 50},
        "conversations_100": {"name": "수다쟁이", "desc": "100회 AI 대화", "condition": ("conversations", 100), "xp": 300},

        # 발음 관련
        "pronunciation_perfect": {"name": "완벽한 발음", "desc": "발음 100점 달성", "condition": ("pronunciation_perfect", 1), "xp": 100},
        "pronunciation_10": {"name": "발음 연습생", "desc": "10회 발음 연습", "condition": ("pronunciation_count", 10), "xp": 50},

        # 레벨 관련
        "level_5": {"name": "성장 중", "desc": "레벨 5 달성", "condition": ("level", 5), "xp": 100},
        "level_10": {"name": "중급 학습자", "desc": "레벨 10 달성", "condition": ("level", 10), "xp": 250},
        "level_20": {"name": "언어 달인", "desc": "레벨 20 달성", "condition": ("level", 20), "xp": 500},

        # 특별 업적
        "first_lesson": {"name": "첫 발자국", "desc": "첫 레슨 완료", "condition": ("lessons", 1), "xp": 20},
        "night_owl": {"name": "올빼미", "desc": "자정 이후 학습", "condition": ("special", "night_owl"), "xp": 30},
        "early_bird": {"name": "얼리버드", "desc": "오전 6시 전 학습", "condition": ("special", "early_bird"), "xp": 30},
        "weekend_warrior": {"name": "주말 전사", "desc": "주말에 1시간 이상 학습", "condition": ("special", "weekend_warrior"), "xp": 50},
    }

    def calculate_xp(
        self,
        event_type: str,
        streak_days: int = 0,
        is_first_of_day: bool = False,
        is_perfect: bool = False
    ) -> XPEvent:
        """
        XP 계산

        Args:
            event_type: 이벤트 유형
            streak_days: 현재 스트릭 일수
            is_first_of_day: 오늘 첫 활동인지
            is_perfect: 만점인지

        Returns:
            XPEvent: XP 정보
        """
        base_xp = self.XP_VALUES.get(event_type, 0)

        # 스트릭 보너스 (연속 학습 일수에 따른 배율)
        streak_multiplier = 1.0 + min(streak_days * 0.02, 0.5)  # 최대 50% 보너스

        # 첫 학습 보너스
        if is_first_of_day:
            base_xp += self.XP_VALUES["first_lesson_of_day"]

        # 만점 보너스
        if is_perfect:
            base_xp += self.XP_VALUES["perfect_score"]

        total_xp = int(base_xp * streak_multiplier)

        bonus_reason = None
        if streak_multiplier > 1.0:
            bonus_reason = f"{streak_days}일 연속 학습 보너스 (+{int((streak_multiplier - 1) * 100)}%)"

        return XPEvent(
            event_type=event_type,
            xp_amount=total_xp,
            multiplier=streak_multiplier,
            bonus_reason=bonus_reason
        )

    def get_level_from_xp(self, total_xp: int) -> Dict[str, Any]:
        """
        XP로부터 레벨 계산

        Returns:
            현재 레벨, 다음 레벨까지 필요 XP, 진행률
        """
        level = 1

        for i, threshold in enumerate(self.LEVEL_THRESHOLDS):
            if total_xp >= threshold:
                level = i + 1
            else:
                break

        # 현재 레벨 XP 범위
        current_threshold = self.LEVEL_THRESHOLDS[min(level - 1, len(self.LEVEL_THRESHOLDS) - 1)]

        if level < len(self.LEVEL_THRESHOLDS):
            next_threshold = self.LEVEL_THRESHOLDS[level]
        else:
            # 최대 레벨 이후 (레벨당 2000XP 추가 필요)
            next_threshold = current_threshold + 2000

        xp_in_level = total_xp - current_threshold
        xp_needed = next_threshold - current_threshold
        progress = (xp_in_level / xp_needed) * 100 if xp_needed > 0 else 100

        return {
            "level": level,
            "current_xp": total_xp,
            "xp_in_level": xp_in_level,
            "xp_for_next_level": xp_needed,
            "progress_percent": round(progress, 1),
            "xp_until_next": xp_needed - xp_in_level
        }

    def check_achievements(
        self,
        user_stats: Dict[str, Any],
        earned_achievements: List[str]
    ) -> List[Dict[str, Any]]:
        """
        업적 달성 여부 확인

        Args:
            user_stats: 사용자 통계
            earned_achievements: 이미 획득한 업적 ID 목록

        Returns:
            새로 획득한 업적 목록
        """
        newly_earned = []

        for ach_id, ach_data in self.ACHIEVEMENTS.items():
            if ach_id in earned_achievements:
                continue

            condition_type, condition_value = ach_data["condition"]
            is_earned = False

            if condition_type == "streak":
                is_earned = user_stats.get("current_streak", 0) >= condition_value
            elif condition_type == "words":
                is_earned = user_stats.get("total_words", 0) >= condition_value
            elif condition_type == "lessons":
                is_earned = user_stats.get("total_lessons", 0) >= condition_value
            elif condition_type == "conversations":
                is_earned = user_stats.get("total_conversations", 0) >= condition_value
            elif condition_type == "level":
                is_earned = user_stats.get("level", 1) >= condition_value
            elif condition_type == "pronunciation_perfect":
                is_earned = user_stats.get("pronunciation_perfects", 0) >= condition_value
            elif condition_type == "pronunciation_count":
                is_earned = user_stats.get("pronunciation_count", 0) >= condition_value
            elif condition_type == "special":
                is_earned = condition_value in user_stats.get("special_achievements", [])

            if is_earned:
                newly_earned.append({
                    "id": ach_id,
                    "name": ach_data["name"],
                    "description": ach_data["desc"],
                    "xp_reward": ach_data["xp"],
                    "earned_at": datetime.utcnow().isoformat()
                })

        return newly_earned

    def update_streak(
        self,
        last_study_date: Optional[datetime],
        current_streak: int
    ) -> Dict[str, Any]:
        """
        스트릭 업데이트

        Args:
            last_study_date: 마지막 학습 날짜
            current_streak: 현재 스트릭

        Returns:
            업데이트된 스트릭 정보
        """
        today = datetime.utcnow().date()

        if last_study_date is None:
            # 첫 학습
            return {
                "streak": 1,
                "streak_continued": True,
                "streak_broken": False
            }

        last_date = last_study_date.date()
        days_diff = (today - last_date).days

        if days_diff == 0:
            # 오늘 이미 학습함
            return {
                "streak": current_streak,
                "streak_continued": False,
                "streak_broken": False
            }
        elif days_diff == 1:
            # 연속 학습 성공
            return {
                "streak": current_streak + 1,
                "streak_continued": True,
                "streak_broken": False
            }
        else:
            # 스트릭 끊김
            return {
                "streak": 1,
                "streak_continued": False,
                "streak_broken": True,
                "previous_streak": current_streak
            }

    def generate_daily_challenge(
        self,
        user_level: int,
        language: str,
        completed_today: List[str]
    ) -> Dict[str, Any]:
        """
        일일 챌린지 생성

        Args:
            user_level: 사용자 레벨
            language: 학습 언어
            completed_today: 오늘 완료한 챌린지 ID

        Returns:
            일일 챌린지 정보
        """
        challenges = [
            {
                "id": "daily_conversation",
                "type": "conversation",
                "title": "AI와 3회 대화하기",
                "target": 3,
                "xp_reward": 30,
                "icon": "💬"
            },
            {
                "id": "daily_vocabulary",
                "type": "vocabulary",
                "title": "새 단어 10개 학습",
                "target": 10,
                "xp_reward": 25,
                "icon": "📚"
            },
            {
                "id": "daily_pronunciation",
                "type": "pronunciation",
                "title": "발음 연습 5회",
                "target": 5,
                "xp_reward": 25,
                "icon": "🎤"
            },
            {
                "id": "daily_lesson",
                "type": "lesson",
                "title": "레슨 1개 완료",
                "target": 1,
                "xp_reward": 20,
                "icon": "📖"
            },
            {
                "id": "daily_review",
                "type": "review",
                "title": "복습 단어 20개",
                "target": 20,
                "xp_reward": 20,
                "icon": "🔄"
            }
        ]

        # 완료되지 않은 챌린지 필터링
        available = [c for c in challenges if c["id"] not in completed_today]

        return {
            "date": datetime.utcnow().date().isoformat(),
            "challenges": available[:3],  # 하루 3개 챌린지
            "bonus_challenge": {
                "id": "daily_all",
                "title": "모든 챌린지 완료",
                "xp_reward": 50,
                "icon": "⭐"
            }
        }

    def calculate_league_points(
        self,
        weekly_xp: int,
        streak: int,
        achievements_this_week: int
    ) -> int:
        """리그 포인트 계산."""
        base_points = weekly_xp
        streak_bonus = streak * 10
        achievement_bonus = achievements_this_week * 50

        return base_points + streak_bonus + achievement_bonus

    def get_leaderboard_tier(self, rank: int, total_users: int) -> str:
        """리더보드 티어 결정."""
        percentile = (rank / total_users) * 100

        if percentile <= 1:
            return "Diamond"
        elif percentile <= 5:
            return "Platinum"
        elif percentile <= 15:
            return "Gold"
        elif percentile <= 35:
            return "Silver"
        else:
            return "Bronze"

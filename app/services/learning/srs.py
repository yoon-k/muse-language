"""
MUSE Language - Spaced Repetition System (SRS)

간격 반복 학습 알고리즘 (SM-2 기반)
- 최적의 복습 시점 계산
- 난이도 적응형 간격 조절
- 학습 효율 최적화
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import IntEnum
import math


class ReviewQuality(IntEnum):
    """복습 품질 등급."""
    COMPLETE_BLACKOUT = 0  # 전혀 기억 못함
    INCORRECT_REMEMBERED = 1  # 틀렸지만 정답 보고 기억남
    INCORRECT_EASY_RECALL = 2  # 틀렸지만 쉽게 떠올림
    CORRECT_DIFFICULT = 3  # 맞았지만 어려웠음
    CORRECT_HESITATION = 4  # 맞았고 약간 망설임
    CORRECT_PERFECT = 5  # 완벽하게 기억


@dataclass
class ReviewResult:
    """복습 결과."""
    word_id: str
    quality: ReviewQuality
    response_time_ms: int
    is_correct: bool


@dataclass
class SRSCard:
    """SRS 카드 (단어/문장)."""
    id: str
    word: str
    meaning: str

    # SRS 파라미터
    ease_factor: float = 2.5  # 난이도 계수 (1.3 ~ 2.5)
    interval: int = 1  # 현재 간격 (일)
    repetitions: int = 0  # 연속 정답 횟수
    next_review: datetime = None
    last_reviewed: datetime = None

    # 통계
    total_reviews: int = 0
    correct_count: int = 0
    incorrect_count: int = 0
    average_response_time: float = 0


class SpacedRepetitionEngine:
    """
    간격 반복 학습 엔진

    SM-2 알고리즘 기반 + 응답 시간 고려
    """

    # 기본 설정
    MIN_EASE_FACTOR = 1.3
    MAX_EASE_FACTOR = 2.5
    INITIAL_EASE_FACTOR = 2.5

    # 간격 설정
    LEARNING_STEPS = [1, 10, 60, 1440]  # 분 단위 (1분, 10분, 1시간, 1일)
    GRADUATING_INTERVAL = 1  # 첫 졸업 간격 (일)
    EASY_INTERVAL = 4  # 쉬운 카드 초기 간격 (일)
    MAX_INTERVAL = 365  # 최대 간격 (일)

    def calculate_next_review(
        self,
        card: SRSCard,
        quality: ReviewQuality,
        response_time_ms: int
    ) -> Tuple[SRSCard, Dict[str, Any]]:
        """
        다음 복습 시점 계산

        Args:
            card: 현재 카드 상태
            quality: 복습 품질 (0-5)
            response_time_ms: 응답 시간 (ms)

        Returns:
            (업데이트된 카드, 변경 정보)
        """
        now = datetime.utcnow()

        # 응답 시간 보정 계수 (빠른 응답 = 더 잘 기억함)
        time_factor = self._calculate_time_factor(response_time_ms)

        # 새 ease factor 계산
        new_ease = self._calculate_ease_factor(
            card.ease_factor,
            quality,
            time_factor
        )

        changes = {
            "previous_interval": card.interval,
            "previous_ease": card.ease_factor,
            "quality": quality,
            "time_factor": time_factor
        }

        if quality < ReviewQuality.CORRECT_DIFFICULT:
            # 틀린 경우: 처음부터 다시
            card.repetitions = 0
            card.interval = 1
            card.incorrect_count += 1
            changes["action"] = "reset"
        else:
            # 맞은 경우
            card.correct_count += 1

            if card.repetitions == 0:
                # 첫 번째 정답
                card.interval = self.GRADUATING_INTERVAL
            elif card.repetitions == 1:
                # 두 번째 정답
                card.interval = 6
            else:
                # 이후: 간격 * ease factor
                card.interval = int(card.interval * new_ease)

            # 쉬웠으면 보너스
            if quality == ReviewQuality.CORRECT_PERFECT:
                card.interval = int(card.interval * 1.3)

            card.repetitions += 1
            changes["action"] = "advance"

        # 간격 제한
        card.interval = min(card.interval, self.MAX_INTERVAL)
        card.interval = max(card.interval, 1)

        # ease factor 업데이트
        card.ease_factor = new_ease

        # 다음 복습 시간 설정
        card.next_review = now + timedelta(days=card.interval)
        card.last_reviewed = now
        card.total_reviews += 1

        # 평균 응답 시간 업데이트
        card.average_response_time = (
            (card.average_response_time * (card.total_reviews - 1) + response_time_ms)
            / card.total_reviews
        )

        changes["new_interval"] = card.interval
        changes["new_ease"] = card.ease_factor
        changes["next_review"] = card.next_review.isoformat()

        return card, changes

    def _calculate_ease_factor(
        self,
        current_ease: float,
        quality: ReviewQuality,
        time_factor: float
    ) -> float:
        """
        새 ease factor 계산 (SM-2 공식 변형)

        EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02)) * time_factor
        """
        q = int(quality)

        # SM-2 기본 공식
        delta = 0.1 - (5 - q) * (0.08 + (5 - q) * 0.02)

        # 응답 시간 반영
        delta *= time_factor

        new_ease = current_ease + delta

        # 범위 제한
        return max(self.MIN_EASE_FACTOR, min(self.MAX_EASE_FACTOR, new_ease))

    def _calculate_time_factor(self, response_time_ms: int) -> float:
        """
        응답 시간 기반 보정 계수

        빠른 응답 = 잘 기억함 = factor > 1
        느린 응답 = 힘들게 기억 = factor < 1
        """
        # 기준: 3초 (3000ms)
        baseline = 3000

        if response_time_ms < baseline:
            # 빠른 응답: 최대 1.2배
            return 1.0 + (baseline - response_time_ms) / baseline * 0.2
        else:
            # 느린 응답: 최소 0.8배
            excess = min(response_time_ms - baseline, baseline * 2)
            return 1.0 - excess / (baseline * 2) * 0.2

    def get_due_cards(
        self,
        cards: List[SRSCard],
        limit: int = 20,
        include_new: int = 5
    ) -> Dict[str, List[SRSCard]]:
        """
        복습할 카드 조회

        Args:
            cards: 전체 카드 목록
            limit: 최대 복습 카드 수
            include_new: 새 카드 수

        Returns:
            {"review": [...], "new": [...]}
        """
        now = datetime.utcnow()

        # 복습 필요한 카드 (기한 지남)
        due_cards = [
            c for c in cards
            if c.next_review and c.next_review <= now
        ]

        # 우선순위 정렬: 오래 지난 것 > ease 낮은 것
        due_cards.sort(key=lambda c: (
            (now - c.next_review).days,
            -c.ease_factor
        ), reverse=True)

        # 새 카드 (아직 학습 안 함)
        new_cards = [
            c for c in cards
            if c.repetitions == 0 and c.next_review is None
        ]

        return {
            "review": due_cards[:limit],
            "new": new_cards[:include_new],
            "total_due": len(due_cards),
            "total_new": len(new_cards)
        }

    def predict_retention(
        self,
        card: SRSCard,
        days_from_now: int = 0
    ) -> float:
        """
        기억 유지율 예측

        지수 망각 곡선 모델:
        R = e^(-t/S)
        R: 유지율, t: 시간, S: 안정도(interval)
        """
        if card.last_reviewed is None:
            return 0.0

        now = datetime.utcnow()
        target_date = now + timedelta(days=days_from_now)

        elapsed_days = (target_date - card.last_reviewed).days

        # 안정도 = 현재 간격 * ease_factor
        stability = card.interval * card.ease_factor

        # 망각 곡선
        retention = math.exp(-elapsed_days / stability)

        return round(retention * 100, 1)

    def estimate_workload(
        self,
        cards: List[SRSCard],
        days_ahead: int = 7
    ) -> List[Dict[str, int]]:
        """
        향후 학습량 예측

        Args:
            cards: 카드 목록
            days_ahead: 예측 일수

        Returns:
            일별 예상 복습 카드 수
        """
        now = datetime.utcnow()
        workload = []

        for day in range(days_ahead):
            target_date = now + timedelta(days=day)
            due_count = sum(
                1 for c in cards
                if c.next_review and c.next_review.date() <= target_date.date()
            )
            workload.append({
                "date": target_date.date().isoformat(),
                "due_count": due_count
            })

        return workload

    def get_mastery_level(self, card: SRSCard) -> Dict[str, Any]:
        """
        단어 숙달도 계산

        Returns:
            숙달 레벨 및 상세 정보
        """
        # 정답률
        total = card.correct_count + card.incorrect_count
        accuracy = card.correct_count / total if total > 0 else 0

        # 간격 기반 숙달도
        interval_score = min(card.interval / 90, 1.0)  # 90일 = 100%

        # ease factor 기반 난이도
        ease_score = (card.ease_factor - self.MIN_EASE_FACTOR) / (
            self.MAX_EASE_FACTOR - self.MIN_EASE_FACTOR
        )

        # 종합 숙달도
        mastery = (accuracy * 0.3 + interval_score * 0.5 + ease_score * 0.2) * 100

        # 레벨 결정
        if mastery >= 90:
            level = "Mastered"
            color = "gold"
        elif mastery >= 70:
            level = "Familiar"
            color = "green"
        elif mastery >= 40:
            level = "Learning"
            color = "blue"
        else:
            level = "New"
            color = "gray"

        return {
            "mastery_percent": round(mastery, 1),
            "level": level,
            "color": color,
            "accuracy": round(accuracy * 100, 1),
            "interval_days": card.interval,
            "reviews_count": card.total_reviews,
            "is_mastered": mastery >= 90
        }


class AdaptiveLearning:
    """
    적응형 학습 시스템

    사용자 성과에 따라 학습 난이도 자동 조절
    """

    def __init__(self):
        self.difficulty_history: List[float] = []
        self.accuracy_history: List[float] = []

    def calculate_optimal_difficulty(
        self,
        recent_accuracy: float,
        target_accuracy: float = 0.8
    ) -> float:
        """
        최적 난이도 계산

        목표: 정답률 80% 유지 (최적 학습 구간)
        """
        # PID 제어 유사 방식
        error = target_accuracy - recent_accuracy

        # 난이도 조절 (-0.2 ~ +0.2)
        adjustment = error * 0.5

        current_difficulty = self.difficulty_history[-1] if self.difficulty_history else 0.5
        new_difficulty = current_difficulty + adjustment

        # 범위 제한 (0.1 ~ 0.9)
        new_difficulty = max(0.1, min(0.9, new_difficulty))

        self.difficulty_history.append(new_difficulty)
        self.accuracy_history.append(recent_accuracy)

        return new_difficulty

    def select_content(
        self,
        available_content: List[Dict[str, Any]],
        user_difficulty: float,
        user_weaknesses: List[str]
    ) -> List[Dict[str, Any]]:
        """
        맞춤 콘텐츠 선택

        Args:
            available_content: 사용 가능한 콘텐츠
            user_difficulty: 사용자 적정 난이도
            user_weaknesses: 사용자 약점 영역

        Returns:
            선택된 콘텐츠 목록
        """
        scored_content = []

        for content in available_content:
            score = 0

            # 난이도 일치도
            difficulty_match = 1 - abs(content.get("difficulty", 0.5) - user_difficulty)
            score += difficulty_match * 50

            # 약점 영역 보너스
            content_tags = content.get("tags", [])
            weakness_match = len(set(content_tags) & set(user_weaknesses))
            score += weakness_match * 30

            # 신선도 (이미 학습한 것은 낮은 점수)
            if not content.get("completed", False):
                score += 20

            scored_content.append((content, score))

        # 점수 내림차순 정렬
        scored_content.sort(key=lambda x: x[1], reverse=True)

        return [c[0] for c in scored_content]

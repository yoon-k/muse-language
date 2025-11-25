"""
MUSE Language - User & Learning Models
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()


class LanguageLevel(str, enum.Enum):
    """CEFR 언어 수준."""
    A1 = "A1"  # 입문
    A2 = "A2"  # 초급
    B1 = "B1"  # 중급
    B2 = "B2"  # 중상급
    C1 = "C1"  # 고급
    C2 = "C2"  # 원어민 수준


class User(Base):
    """사용자 모델."""
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    native_language = Column(String, default="ko")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # 프리미엄 상태
    is_premium = Column(Boolean, default=False)
    premium_until = Column(DateTime, nullable=True)

    # 관계
    learning_profiles = relationship("LearningProfile", back_populates="user")
    study_sessions = relationship("StudySession", back_populates="user")
    achievements = relationship("UserAchievement", back_populates="user")


class LearningProfile(Base):
    """학습 프로필 (언어별)."""
    __tablename__ = "learning_profiles"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    target_language = Column(String, nullable=False)  # en, ja, zh, es, fr

    # 레벨
    current_level = Column(SQLEnum(LanguageLevel), default=LanguageLevel.A1)
    level_progress = Column(Float, default=0.0)  # 0-100%

    # 통계
    total_study_time = Column(Integer, default=0)  # 분
    total_lessons = Column(Integer, default=0)
    total_words_learned = Column(Integer, default=0)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_study_date = Column(DateTime, nullable=True)

    # 강점/약점
    strengths = Column(JSON, default=list)  # ["grammar", "vocabulary"]
    weaknesses = Column(JSON, default=list)  # ["pronunciation", "listening"]

    # XP & 게이미피케이션
    xp_total = Column(Integer, default=0)
    xp_this_week = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계
    user = relationship("User", back_populates="learning_profiles")
    vocabulary = relationship("UserVocabulary", back_populates="profile")


class StudySession(Base):
    """학습 세션."""
    __tablename__ = "study_sessions"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    profile_id = Column(String, ForeignKey("learning_profiles.id"), nullable=False)

    session_type = Column(String, nullable=False)  # conversation, lesson, review, pronunciation
    target_language = Column(String, nullable=False)

    # 세션 데이터
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    duration_minutes = Column(Integer, default=0)

    # 성과
    xp_earned = Column(Integer, default=0)
    words_practiced = Column(Integer, default=0)
    accuracy_rate = Column(Float, nullable=True)

    # 대화 기록 (AI 튜터)
    messages = Column(JSON, default=list)

    # 상태
    is_active = Column(Boolean, default=True)

    # 관계
    user = relationship("User", back_populates="study_sessions")


class Lesson(Base):
    """학습 레슨."""
    __tablename__ = "lessons"

    id = Column(String, primary_key=True)
    language = Column(String, nullable=False)
    level = Column(SQLEnum(LanguageLevel), nullable=False)

    title = Column(String, nullable=False)
    description = Column(String)
    category = Column(String, nullable=False)  # grammar, vocabulary, conversation, etc.
    topic = Column(String)  # business, travel, daily, etc.

    # 콘텐츠
    content = Column(JSON, nullable=False)  # 레슨 구조화된 콘텐츠
    exercises = Column(JSON, default=list)

    # 메타데이터
    estimated_minutes = Column(Integer, default=15)
    xp_reward = Column(Integer, default=20)
    order_index = Column(Integer, default=0)

    is_premium = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)


class UserVocabulary(Base):
    """사용자 단어장."""
    __tablename__ = "user_vocabulary"

    id = Column(String, primary_key=True)
    profile_id = Column(String, ForeignKey("learning_profiles.id"), nullable=False)

    word = Column(String, nullable=False)
    language = Column(String, nullable=False)
    translation = Column(String)
    pronunciation = Column(String)  # IPA or romanization
    example_sentence = Column(String)
    audio_url = Column(String)

    # 간격 반복 학습 (SRS)
    ease_factor = Column(Float, default=2.5)
    interval_days = Column(Integer, default=1)
    repetitions = Column(Integer, default=0)
    next_review = Column(DateTime, default=datetime.utcnow)
    last_reviewed = Column(DateTime, nullable=True)

    # 통계
    times_correct = Column(Integer, default=0)
    times_incorrect = Column(Integer, default=0)

    # 상태
    mastery_level = Column(Float, default=0.0)  # 0-100%
    is_mastered = Column(Boolean, default=False)

    added_at = Column(DateTime, default=datetime.utcnow)

    # 관계
    profile = relationship("LearningProfile", back_populates="vocabulary")


class Achievement(Base):
    """업적 정의."""
    __tablename__ = "achievements"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    icon = Column(String)

    # 조건
    condition_type = Column(String, nullable=False)  # streak, words, lessons, etc.
    condition_value = Column(Integer, nullable=False)

    xp_reward = Column(Integer, default=0)
    is_hidden = Column(Boolean, default=False)


class UserAchievement(Base):
    """사용자 업적."""
    __tablename__ = "user_achievements"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    achievement_id = Column(String, ForeignKey("achievements.id"), nullable=False)

    earned_at = Column(DateTime, default=datetime.utcnow)

    # 관계
    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement")


class DailyChallenge(Base):
    """일일 챌린지."""
    __tablename__ = "daily_challenges"

    id = Column(String, primary_key=True)
    date = Column(DateTime, nullable=False)

    challenge_type = Column(String, nullable=False)  # conversation, vocabulary, pronunciation
    description = Column(String, nullable=False)
    target_value = Column(Integer, default=1)

    xp_reward = Column(Integer, default=50)


class UserDailyProgress(Base):
    """사용자 일일 진도."""
    __tablename__ = "user_daily_progress"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime, nullable=False)

    study_minutes = Column(Integer, default=0)
    lessons_completed = Column(Integer, default=0)
    words_reviewed = Column(Integer, default=0)
    conversations = Column(Integer, default=0)
    xp_earned = Column(Integer, default=0)

    daily_goal_met = Column(Boolean, default=False)

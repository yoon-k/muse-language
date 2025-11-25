"""
MUSE Language - AI Tutor Service

AI 기반 언어 학습 튜터
- 대화형 학습
- 문법 교정
- 맞춤형 피드백
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from openai import OpenAI
from dataclasses import dataclass
import json

from app.core.config import settings


@dataclass
class TutorResponse:
    """튜터 응답."""
    message: str
    corrections: List[Dict[str, str]]
    vocabulary: List[Dict[str, str]]
    grammar_tips: List[str]
    encouragement: str
    next_suggestion: Optional[str] = None


class AITutor:
    """
    AI 언어 튜터

    기능:
    - 자연스러운 대화 진행
    - 실시간 문법/어휘 교정
    - 수준 맞춤 대화
    - 학습 진도 추적
    """

    SYSTEM_PROMPTS = {
        "en": """You are MUSE, a friendly and encouraging English language tutor.
Your role is to help the user practice English through natural conversation.

Guidelines:
1. Respond in English, but adapt complexity to the user's level: {level}
2. If the user makes mistakes, gently correct them
3. Introduce new vocabulary naturally
4. Keep responses conversational and engaging
5. Praise good usage and encourage practice

Current conversation topic: {topic}

Respond in JSON format:
{{
    "message": "Your conversational response",
    "corrections": [
        {{"original": "user's text", "corrected": "correct version", "explanation": "why"}}
    ],
    "vocabulary": [
        {{"word": "new word", "definition": "meaning", "example": "usage example"}}
    ],
    "grammar_tips": ["tip 1", "tip 2"],
    "encouragement": "positive feedback",
    "next_suggestion": "optional topic suggestion"
}}""",

        "ja": """あなたはMUSE、親切で励ましてくれる日本語チューターです。
自然な会話を通じて、ユーザーの日本語学習をサポートします。

ガイドライン:
1. ユーザーのレベルに合わせて対応: {level}
2. 間違いがあれば優しく訂正
3. 新しい語彙を自然に紹介
4. 会話を楽しく続ける
5. 良い表現を褒めて励ます

現在の会話トピック: {topic}

JSON形式で返答:
{{
    "message": "会話の返答",
    "corrections": [
        {{"original": "ユーザーの文", "corrected": "正しい文", "explanation": "説明"}}
    ],
    "vocabulary": [
        {{"word": "新語", "definition": "意味", "example": "例文"}}
    ],
    "grammar_tips": ["ヒント1"],
    "encouragement": "励ましの言葉",
    "next_suggestion": "次のトピック提案"
}}""",

        "zh": """你是MUSE，一位友好且鼓励人的中文老师。
通过自然对话帮助用户学习中文。

指南：
1. 根据用户水平调整难度：{level}
2. 温和地纠正错误
3. 自然地介绍新词汇
4. 保持对话有趣
5. 表扬好的表达并鼓励练习

当前话题：{topic}

用JSON格式回复：
{{
    "message": "对话回复",
    "corrections": [
        {{"original": "用户原文", "corrected": "正确表达", "explanation": "解释"}}
    ],
    "vocabulary": [
        {{"word": "新词", "definition": "意思", "example": "例句"}}
    ],
    "grammar_tips": ["语法提示"],
    "encouragement": "鼓励的话",
    "next_suggestion": "下一个话题建议"
}}""",

        "es": """Eres MUSE, un tutor de español amigable y alentador.
Tu rol es ayudar al usuario a practicar español a través de conversación natural.

Pautas:
1. Adapta la complejidad al nivel del usuario: {level}
2. Corrige errores de manera gentil
3. Introduce vocabulario nuevo naturalmente
4. Mantén la conversación interesante
5. Elogia el buen uso y anima a practicar

Tema actual: {topic}

Responde en formato JSON:
{{
    "message": "Tu respuesta conversacional",
    "corrections": [...],
    "vocabulary": [...],
    "grammar_tips": [...],
    "encouragement": "comentario positivo",
    "next_suggestion": "sugerencia de tema"
}}""",

        "fr": """Tu es MUSE, un tuteur de français amical et encourageant.
Ton rôle est d'aider l'utilisateur à pratiquer le français par la conversation naturelle.

Directives:
1. Adapte la complexité au niveau de l'utilisateur: {level}
2. Corrige les erreurs gentiment
3. Introduis du nouveau vocabulaire naturellement
4. Garde la conversation engageante
5. Félicite les bonnes expressions

Sujet actuel: {topic}

Réponds en format JSON:
{{
    "message": "Ta réponse conversationnelle",
    "corrections": [...],
    "vocabulary": [...],
    "grammar_tips": [...],
    "encouragement": "commentaire positif",
    "next_suggestion": "suggestion de sujet"
}}"""
    }

    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    def get_system_prompt(
        self,
        language: str,
        level: str,
        topic: str = "general conversation"
    ) -> str:
        """언어별 시스템 프롬프트 생성."""
        base_prompt = self.SYSTEM_PROMPTS.get(language, self.SYSTEM_PROMPTS["en"])
        return base_prompt.format(level=level, topic=topic)

    async def chat(
        self,
        user_message: str,
        language: str,
        level: str,
        conversation_history: List[Dict[str, str]],
        topic: str = "general"
    ) -> TutorResponse:
        """
        AI 튜터와 대화

        Args:
            user_message: 사용자 입력
            language: 학습 언어 (en, ja, zh, es, fr)
            level: 사용자 레벨 (A1-C2)
            conversation_history: 이전 대화 기록
            topic: 대화 주제

        Returns:
            TutorResponse: 튜터 응답 및 교정 정보
        """
        system_prompt = self.get_system_prompt(language, level, topic)

        messages = [
            {"role": "system", "content": system_prompt}
        ]

        # 대화 기록 추가
        for msg in conversation_history[-10:]:  # 최근 10개만
            messages.append(msg)

        messages.append({"role": "user", "content": user_message})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)

            return TutorResponse(
                message=result.get("message", ""),
                corrections=result.get("corrections", []),
                vocabulary=result.get("vocabulary", []),
                grammar_tips=result.get("grammar_tips", []),
                encouragement=result.get("encouragement", ""),
                next_suggestion=result.get("next_suggestion")
            )

        except Exception as e:
            # 에러 시 기본 응답
            return TutorResponse(
                message="I apologize, I had trouble processing that. Could you try again?",
                corrections=[],
                vocabulary=[],
                grammar_tips=[],
                encouragement="Keep practicing!"
            )

    async def correct_grammar(
        self,
        text: str,
        language: str
    ) -> Dict[str, Any]:
        """
        문법 교정 전용

        Args:
            text: 교정할 텍스트
            language: 언어 코드

        Returns:
            교정 결과 및 설명
        """
        prompt = f"""Analyze and correct this {language} text. Return JSON:
{{
    "original": "{text}",
    "corrected": "corrected version",
    "is_correct": true/false,
    "errors": [
        {{"type": "grammar/spelling/word_choice", "original": "...", "correction": "...", "explanation": "..."}}
    ],
    "overall_feedback": "summary feedback"
}}

Text to analyze: {text}"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        return json.loads(response.choices[0].message.content)

    async def generate_exercise(
        self,
        language: str,
        level: str,
        exercise_type: str,
        topic: str
    ) -> Dict[str, Any]:
        """
        학습 문제 생성

        Args:
            language: 언어
            level: 레벨
            exercise_type: 문제 유형 (fill_blank, translation, multiple_choice, etc.)
            topic: 주제

        Returns:
            생성된 문제
        """
        prompt = f"""Create a {exercise_type} exercise for {language} learners at {level} level.
Topic: {topic}

Return JSON:
{{
    "type": "{exercise_type}",
    "instruction": "What the user should do",
    "question": "The question or sentence",
    "options": ["option1", "option2", ...] (for multiple choice),
    "correct_answer": "the answer",
    "explanation": "why this is correct",
    "hint": "optional hint"
}}"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            response_format={"type": "json_object"}
        )

        return json.loads(response.choices[0].message.content)

    async def explain_word(
        self,
        word: str,
        language: str,
        user_native_language: str = "ko"
    ) -> Dict[str, Any]:
        """
        단어 상세 설명

        Args:
            word: 설명할 단어
            language: 단어의 언어
            user_native_language: 사용자 모국어

        Returns:
            단어 설명, 예문, 관련 단어 등
        """
        prompt = f"""Explain this {language} word/phrase for a {user_native_language} speaker.
Word: {word}

Return JSON:
{{
    "word": "{word}",
    "pronunciation": "IPA or romanization",
    "part_of_speech": "noun/verb/etc",
    "definitions": [
        {{"meaning": "definition", "translation": "in {user_native_language}"}}
    ],
    "examples": [
        {{"sentence": "example in {language}", "translation": "in {user_native_language}"}}
    ],
    "synonyms": ["syn1", "syn2"],
    "antonyms": ["ant1"],
    "related_words": ["related1", "related2"],
    "usage_notes": "when/how to use this word",
    "common_mistakes": "mistakes learners often make"
}}"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        return json.loads(response.choices[0].message.content)

    async def suggest_topic(
        self,
        language: str,
        level: str,
        interests: List[str],
        recent_topics: List[str]
    ) -> str:
        """대화 주제 추천."""
        prompt = f"""Suggest a conversation topic for a {language} learner at {level} level.
Their interests: {', '.join(interests)}
Recently discussed: {', '.join(recent_topics)}

Suggest something new, relevant, and appropriate for their level.
Return just the topic name, nothing else."""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,
            max_tokens=50
        )

        return response.choices[0].message.content.strip()

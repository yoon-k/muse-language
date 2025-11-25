"""
MUSE Language - Speech Processing Service

음성 인식 및 발음 평가
- STT (Speech-to-Text)
- TTS (Text-to-Speech)
- 발음 정확도 평가
"""

from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
import io
import base64
import numpy as np
from openai import OpenAI

from app.core.config import settings


@dataclass
class PronunciationResult:
    """발음 평가 결과."""
    transcript: str
    accuracy_score: float  # 0-100
    fluency_score: float   # 0-100
    completeness_score: float  # 0-100
    overall_score: float   # 0-100
    word_scores: List[Dict[str, Any]]
    phoneme_errors: List[Dict[str, str]]
    feedback: str
    suggestions: List[str]


class SpeechProcessor:
    """
    음성 처리 서비스

    기능:
    - Whisper 기반 음성 인식
    - OpenAI TTS 기반 음성 합성
    - 발음 정확도 평가
    - 억양/리듬 분석
    """

    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    async def transcribe(
        self,
        audio_data: bytes,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        음성을 텍스트로 변환 (STT)

        Args:
            audio_data: 오디오 바이트 데이터
            language: 언어 코드

        Returns:
            변환된 텍스트 및 메타데이터
        """
        # 바이트 데이터를 파일 객체로 변환
        audio_file = io.BytesIO(audio_data)
        audio_file.name = "audio.webm"

        response = self.client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language=language,
            response_format="verbose_json",
            timestamp_granularities=["word"]
        )

        return {
            "text": response.text,
            "language": response.language,
            "duration": response.duration,
            "words": [
                {
                    "word": w.word,
                    "start": w.start,
                    "end": w.end
                }
                for w in (response.words or [])
            ]
        }

    async def synthesize(
        self,
        text: str,
        voice: str = "alloy",
        speed: float = 1.0
    ) -> bytes:
        """
        텍스트를 음성으로 변환 (TTS)

        Args:
            text: 변환할 텍스트
            voice: 음성 종류 (alloy, echo, fable, onyx, nova, shimmer)
            speed: 재생 속도 (0.25 ~ 4.0)

        Returns:
            MP3 오디오 데이터
        """
        response = self.client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text,
            speed=speed
        )

        return response.content

    async def evaluate_pronunciation(
        self,
        audio_data: bytes,
        expected_text: str,
        language: str = "en"
    ) -> PronunciationResult:
        """
        발음 평가

        Args:
            audio_data: 사용자 음성 데이터
            expected_text: 예상 텍스트 (읽어야 할 문장)
            language: 언어

        Returns:
            PronunciationResult: 발음 평가 결과
        """
        # 음성 인식
        transcription = await self.transcribe(audio_data, language)
        user_text = transcription["text"]
        words_timing = transcription.get("words", [])

        # 단어별 비교
        expected_words = expected_text.lower().split()
        spoken_words = user_text.lower().split()

        word_scores = []
        correct_count = 0

        for i, expected in enumerate(expected_words):
            if i < len(spoken_words):
                spoken = spoken_words[i]
                # 간단한 유사도 계산
                similarity = self._calculate_word_similarity(expected, spoken)
                is_correct = similarity > 0.8

                if is_correct:
                    correct_count += 1

                word_scores.append({
                    "expected": expected,
                    "spoken": spoken,
                    "score": similarity * 100,
                    "is_correct": is_correct
                })
            else:
                word_scores.append({
                    "expected": expected,
                    "spoken": "",
                    "score": 0,
                    "is_correct": False
                })

        # 점수 계산
        accuracy = (correct_count / len(expected_words)) * 100 if expected_words else 0

        # 완성도 (모든 단어를 말했는지)
        completeness = min(len(spoken_words) / len(expected_words), 1.0) * 100 if expected_words else 0

        # 유창성 (대략적 계산 - 실제로는 음성 분석 필요)
        fluency = self._estimate_fluency(words_timing)

        # 종합 점수
        overall = (accuracy * 0.5 + completeness * 0.25 + fluency * 0.25)

        # 발음 오류 분석
        phoneme_errors = self._analyze_phoneme_errors(expected_words, spoken_words, language)

        # 피드백 생성
        feedback, suggestions = self._generate_feedback(
            accuracy, fluency, completeness, phoneme_errors, language
        )

        return PronunciationResult(
            transcript=user_text,
            accuracy_score=round(accuracy, 1),
            fluency_score=round(fluency, 1),
            completeness_score=round(completeness, 1),
            overall_score=round(overall, 1),
            word_scores=word_scores,
            phoneme_errors=phoneme_errors,
            feedback=feedback,
            suggestions=suggestions
        )

    def _calculate_word_similarity(self, word1: str, word2: str) -> float:
        """레벤슈타인 거리 기반 유사도 계산."""
        if word1 == word2:
            return 1.0

        len1, len2 = len(word1), len(word2)
        if len1 == 0 or len2 == 0:
            return 0.0

        # 레벤슈타인 거리 계산
        dp = [[0] * (len2 + 1) for _ in range(len1 + 1)]

        for i in range(len1 + 1):
            dp[i][0] = i
        for j in range(len2 + 1):
            dp[0][j] = j

        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                cost = 0 if word1[i-1] == word2[j-1] else 1
                dp[i][j] = min(
                    dp[i-1][j] + 1,      # 삭제
                    dp[i][j-1] + 1,      # 삽입
                    dp[i-1][j-1] + cost  # 대체
                )

        distance = dp[len1][len2]
        max_len = max(len1, len2)

        return 1 - (distance / max_len)

    def _estimate_fluency(self, words_timing: List[Dict]) -> float:
        """유창성 추정 (단어 간 간격 기반)."""
        if len(words_timing) < 2:
            return 80.0  # 기본값

        gaps = []
        for i in range(1, len(words_timing)):
            gap = words_timing[i].get("start", 0) - words_timing[i-1].get("end", 0)
            gaps.append(gap)

        if not gaps:
            return 80.0

        avg_gap = sum(gaps) / len(gaps)

        # 평균 간격이 짧을수록 유창함
        if avg_gap < 0.3:
            return 95.0
        elif avg_gap < 0.5:
            return 85.0
        elif avg_gap < 0.8:
            return 70.0
        else:
            return 55.0

    def _analyze_phoneme_errors(
        self,
        expected: List[str],
        spoken: List[str],
        language: str
    ) -> List[Dict[str, str]]:
        """음소 오류 분석."""
        errors = []

        # 흔한 발음 오류 패턴 (언어별)
        common_errors = {
            "en": {
                "th": ["s", "z", "d"],  # th 발음 오류
                "r": ["l"],             # r/l 혼동
                "v": ["b"],             # v/b 혼동
            },
            "ja": {
                "つ": ["す"],
                "ん": ["む"],
            }
        }

        for exp, spk in zip(expected, spoken):
            if exp != spk and self._calculate_word_similarity(exp, spk) < 0.9:
                # 어떤 음소에서 오류가 났는지 추정
                for i, (c1, c2) in enumerate(zip(exp, spk)):
                    if c1 != c2:
                        errors.append({
                            "word": exp,
                            "expected_sound": c1,
                            "spoken_sound": c2,
                            "position": i
                        })
                        break

        return errors[:5]  # 최대 5개 오류만

    def _generate_feedback(
        self,
        accuracy: float,
        fluency: float,
        completeness: float,
        errors: List[Dict],
        language: str
    ) -> Tuple[str, List[str]]:
        """피드백 및 제안 생성."""
        suggestions = []

        # 정확도 기반 피드백
        if accuracy >= 90:
            feedback = "Excellent pronunciation! You're doing great!"
        elif accuracy >= 75:
            feedback = "Good job! A few words need more practice."
        elif accuracy >= 60:
            feedback = "Nice effort! Keep practicing the difficult words."
        else:
            feedback = "Keep going! Focus on pronouncing each word clearly."

        # 제안 생성
        if accuracy < 80:
            suggestions.append("Try speaking more slowly and clearly")

        if fluency < 70:
            suggestions.append("Practice reading the sentence multiple times to improve flow")

        if completeness < 90:
            suggestions.append("Make sure to pronounce all words in the sentence")

        if errors:
            error_sounds = set(e.get("expected_sound", "") for e in errors)
            if error_sounds:
                suggestions.append(f"Focus on these sounds: {', '.join(error_sounds)}")

        return feedback, suggestions

    async def get_word_pronunciation(
        self,
        word: str,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        단어 발음 정보 조회

        Args:
            word: 단어
            language: 언어

        Returns:
            발음 기호, 음절, 오디오 등
        """
        # TTS로 오디오 생성
        audio_data = await self.synthesize(word, speed=0.8)
        audio_base64 = base64.b64encode(audio_data).decode()

        # 발음 기호 (실제로는 발음 사전 API 사용)
        # 여기서는 placeholder
        ipa = self._get_ipa(word, language)

        return {
            "word": word,
            "language": language,
            "ipa": ipa,
            "audio_base64": audio_base64,
            "syllables": self._split_syllables(word, language)
        }

    def _get_ipa(self, word: str, language: str) -> str:
        """IPA 발음 기호 (placeholder)."""
        # 실제 구현에서는 발음 사전 API 사용
        return f"/{word}/"

    def _split_syllables(self, word: str, language: str) -> List[str]:
        """음절 분리 (placeholder)."""
        # 실제 구현에서는 언어별 음절 분리 라이브러리 사용
        return [word]

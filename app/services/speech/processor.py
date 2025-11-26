"""
MUSE Language - Speech Processing Service

음성 인식 및 발음 평가
- STT (Speech-to-Text)
- TTS (Text-to-Speech)
- 발음 정확도 평가
- IPA 발음 기호 변환
- 음절 분리 및 강세 분석
"""

from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field
import io
import base64
import numpy as np
import re
from openai import OpenAI

from app.core.config import settings


# ============================================================
# IPA 발음 사전 (주요 영어 단어)
# ============================================================
IPA_DICTIONARY = {
    "en": {
        # Common words
        "hello": "həˈloʊ",
        "world": "wɜːrld",
        "the": "ðə",
        "a": "ə",
        "an": "æn",
        "is": "ɪz",
        "are": "ɑːr",
        "was": "wʌz",
        "were": "wɜːr",
        "be": "biː",
        "been": "bɪn",
        "being": "ˈbiːɪŋ",
        "have": "hæv",
        "has": "hæz",
        "had": "hæd",
        "do": "duː",
        "does": "dʌz",
        "did": "dɪd",
        "will": "wɪl",
        "would": "wʊd",
        "could": "kʊd",
        "should": "ʃʊd",
        "may": "meɪ",
        "might": "maɪt",
        "must": "mʌst",
        "can": "kæn",
        "this": "ðɪs",
        "that": "ðæt",
        "these": "ðiːz",
        "those": "ðoʊz",
        "i": "aɪ",
        "you": "juː",
        "he": "hiː",
        "she": "ʃiː",
        "it": "ɪt",
        "we": "wiː",
        "they": "ðeɪ",
        "what": "wʌt",
        "which": "wɪtʃ",
        "who": "huː",
        "when": "wen",
        "where": "wer",
        "why": "waɪ",
        "how": "haʊ",
        "all": "ɔːl",
        "each": "iːtʃ",
        "every": "ˈevri",
        "both": "boʊθ",
        "few": "fjuː",
        "more": "mɔːr",
        "most": "moʊst",
        "other": "ˈʌðər",
        "some": "sʌm",
        "such": "sʌtʃ",
        "no": "noʊ",
        "not": "nɑːt",
        "only": "ˈoʊnli",
        "own": "oʊn",
        "same": "seɪm",
        "so": "soʊ",
        "than": "ðæn",
        "too": "tuː",
        "very": "ˈveri",
        "just": "dʒʌst",
        "about": "əˈbaʊt",
        "after": "ˈæftər",
        "again": "əˈɡen",
        "air": "er",
        "also": "ˈɔːlsoʊ",
        "always": "ˈɔːlweɪz",
        "animal": "ˈænɪməl",
        "another": "əˈnʌðər",
        "answer": "ˈænsər",
        "any": "ˈeni",
        "ask": "æsk",
        "away": "əˈweɪ",
        "back": "bæk",
        "because": "bɪˈkɔːz",
        "before": "bɪˈfɔːr",
        "begin": "bɪˈɡɪn",
        "between": "bɪˈtwiːn",
        "big": "bɪɡ",
        "book": "bʊk",
        "boy": "bɔɪ",
        "bring": "brɪŋ",
        "build": "bɪld",
        "but": "bʌt",
        "by": "baɪ",
        "call": "kɔːl",
        "came": "keɪm",
        "change": "tʃeɪndʒ",
        "children": "ˈtʃɪldrən",
        "city": "ˈsɪti",
        "close": "kloʊz",
        "come": "kʌm",
        "country": "ˈkʌntri",
        "day": "deɪ",
        "different": "ˈdɪfərənt",
        "earth": "ɜːrθ",
        "eat": "iːt",
        "end": "end",
        "enough": "ɪˈnʌf",
        "even": "ˈiːvən",
        "example": "ɪɡˈzæmpəl",
        "eye": "aɪ",
        "face": "feɪs",
        "family": "ˈfæməli",
        "far": "fɑːr",
        "father": "ˈfɑːðər",
        "feel": "fiːl",
        "find": "faɪnd",
        "first": "fɜːrst",
        "follow": "ˈfɑːloʊ",
        "food": "fuːd",
        "for": "fɔːr",
        "form": "fɔːrm",
        "found": "faʊnd",
        "four": "fɔːr",
        "friend": "frend",
        "from": "frʌm",
        "get": "ɡet",
        "girl": "ɡɜːrl",
        "give": "ɡɪv",
        "go": "ɡoʊ",
        "good": "ɡʊd",
        "government": "ˈɡʌvərnmənt",
        "great": "ɡreɪt",
        "group": "ɡruːp",
        "grow": "ɡroʊ",
        "hand": "hænd",
        "happen": "ˈhæpən",
        "happy": "ˈhæpi",
        "head": "hed",
        "hear": "hɪr",
        "help": "help",
        "here": "hɪr",
        "high": "haɪ",
        "home": "hoʊm",
        "house": "haʊs",
        "idea": "aɪˈdiːə",
        "important": "ɪmˈpɔːrtənt",
        "in": "ɪn",
        "interest": "ˈɪntrəst",
        "into": "ˈɪntuː",
        "keep": "kiːp",
        "kind": "kaɪnd",
        "know": "noʊ",
        "land": "lænd",
        "language": "ˈlæŋɡwɪdʒ",
        "large": "lɑːrdʒ",
        "last": "læst",
        "late": "leɪt",
        "later": "ˈleɪtər",
        "learn": "lɜːrn",
        "leave": "liːv",
        "left": "left",
        "let": "let",
        "letter": "ˈletər",
        "life": "laɪf",
        "light": "laɪt",
        "like": "laɪk",
        "line": "laɪn",
        "list": "lɪst",
        "little": "ˈlɪtəl",
        "live": "lɪv",
        "long": "lɔːŋ",
        "look": "lʊk",
        "love": "lʌv",
        "made": "meɪd",
        "make": "meɪk",
        "man": "mæn",
        "many": "ˈmeni",
        "mean": "miːn",
        "men": "men",
        "money": "ˈmʌni",
        "mother": "ˈmʌðər",
        "move": "muːv",
        "much": "mʌtʃ",
        "music": "ˈmjuːzɪk",
        "name": "neɪm",
        "near": "nɪr",
        "need": "niːd",
        "never": "ˈnevər",
        "new": "nuː",
        "next": "nekst",
        "night": "naɪt",
        "number": "ˈnʌmbər",
        "of": "ʌv",
        "off": "ɔːf",
        "often": "ˈɔːfən",
        "old": "oʊld",
        "on": "ɑːn",
        "once": "wʌns",
        "one": "wʌn",
        "open": "ˈoʊpən",
        "or": "ɔːr",
        "order": "ˈɔːrdər",
        "our": "aʊr",
        "out": "aʊt",
        "over": "ˈoʊvər",
        "page": "peɪdʒ",
        "paper": "ˈpeɪpər",
        "part": "pɑːrt",
        "people": "ˈpiːpəl",
        "picture": "ˈpɪktʃər",
        "place": "pleɪs",
        "play": "pleɪ",
        "point": "pɔɪnt",
        "problem": "ˈprɑːbləm",
        "public": "ˈpʌblɪk",
        "put": "pʊt",
        "question": "ˈkwestʃən",
        "read": "riːd",
        "really": "ˈriːəli",
        "right": "raɪt",
        "room": "ruːm",
        "run": "rʌn",
        "said": "sed",
        "same": "seɪm",
        "say": "seɪ",
        "school": "skuːl",
        "see": "siː",
        "seem": "siːm",
        "sentence": "ˈsentəns",
        "set": "set",
        "show": "ʃoʊ",
        "side": "saɪd",
        "small": "smɔːl",
        "sound": "saʊnd",
        "spell": "spel",
        "stand": "stænd",
        "start": "stɑːrt",
        "state": "steɪt",
        "still": "stɪl",
        "stop": "stɑːp",
        "story": "ˈstɔːri",
        "student": "ˈstuːdənt",
        "study": "ˈstʌdi",
        "system": "ˈsɪstəm",
        "take": "teɪk",
        "talk": "tɔːk",
        "teach": "tiːtʃ",
        "teacher": "ˈtiːtʃər",
        "tell": "tel",
        "test": "test",
        "thank": "θæŋk",
        "then": "ðen",
        "there": "ðer",
        "thing": "θɪŋ",
        "think": "θɪŋk",
        "three": "θriː",
        "through": "θruː",
        "time": "taɪm",
        "today": "təˈdeɪ",
        "together": "təˈɡeðər",
        "tomorrow": "təˈmɑːroʊ",
        "try": "traɪ",
        "turn": "tɜːrn",
        "two": "tuː",
        "under": "ˈʌndər",
        "understand": "ˌʌndərˈstænd",
        "until": "ənˈtɪl",
        "up": "ʌp",
        "us": "ʌs",
        "use": "juːz",
        "usually": "ˈjuːʒuəli",
        "want": "wɑːnt",
        "water": "ˈwɔːtər",
        "way": "weɪ",
        "week": "wiːk",
        "well": "wel",
        "while": "waɪl",
        "with": "wɪð",
        "without": "wɪˈðaʊt",
        "woman": "ˈwʊmən",
        "women": "ˈwɪmɪn",
        "word": "wɜːrd",
        "work": "wɜːrk",
        "world": "wɜːrld",
        "write": "raɪt",
        "year": "jɪr",
        "yes": "jes",
        "yesterday": "ˈjestərdeɪ",
        "young": "jʌŋ",
        "your": "jɔːr",
        # Difficult pronunciation words
        "pronunciation": "prəˌnʌnsiˈeɪʃən",
        "necessary": "ˈnesəseri",
        "restaurant": "ˈrestərɑːnt",
        "comfortable": "ˈkʌmftərbəl",
        "vegetable": "ˈvedʒtəbəl",
        "temperature": "ˈtemprətʃər",
        "actually": "ˈæktʃuəli",
        "beautiful": "ˈbjuːtɪfəl",
        "chocolate": "ˈtʃɔːklət",
        "library": "ˈlaɪbreri",
        "wednesday": "ˈwenzdeɪ",
        "February": "ˈfebrueri",
        "colonel": "ˈkɜːrnəl",
        "island": "ˈaɪlənd",
        "receipt": "rɪˈsiːt",
        "queue": "kjuː",
        "suite": "swiːt",
        "yacht": "jɑːt",
        "chaos": "ˈkeɪɑːs",
        "rhythm": "ˈrɪðəm",
    },
    "ja": {
        "こんにちは": "koɴnitɕiwa",
        "ありがとう": "ariɡatoː",
        "さようなら": "sajoːnara",
        "すみません": "sɯmimaseɴ",
        "おはよう": "ohajoː",
        "はい": "hai",
        "いいえ": "iːe",
    },
    "zh": {
        "你好": "nǐ hǎo",
        "谢谢": "xiè xiè",
        "再见": "zài jiàn",
        "对不起": "duì bu qǐ",
        "是": "shì",
        "不是": "bú shì",
    },
    "es": {
        "hola": "ˈo.la",
        "gracias": "ˈɡɾa.θjas",
        "adiós": "a.ˈðjos",
        "por favor": "poɾ faˈβoɾ",
        "bueno": "ˈbwe.no",
    },
    "fr": {
        "bonjour": "bɔ̃.ʒuʁ",
        "merci": "mɛʁ.si",
        "au revoir": "o ʁə.vwaʁ",
        "s'il vous plaît": "sil vu plɛ",
        "oui": "wi",
        "non": "nɔ̃",
    }
}

# ============================================================
# 음절 분리 규칙
# ============================================================
SYLLABLE_RULES = {
    "en": {
        # 모음 패턴
        "vowels": "aeiouyAEIOUY",
        # 이중 자음 (분리하지 않음)
        "consonant_blends": [
            "bl", "br", "ch", "cl", "cr", "dr", "fl", "fr", "gl", "gr",
            "pl", "pr", "sc", "sh", "sk", "sl", "sm", "sn", "sp", "st",
            "sw", "th", "tr", "tw", "wh", "wr", "sch", "scr", "shr",
            "spl", "spr", "squ", "str", "thr"
        ],
        # 이중 모음 (하나의 음절)
        "vowel_teams": [
            "ai", "ay", "ea", "ee", "ei", "ey", "ie", "oa", "oe", "oi",
            "oo", "ou", "ow", "oy", "ue", "ui"
        ]
    }
}

# ============================================================
# 발음 난이도 데이터
# ============================================================
PRONUNCIATION_DIFFICULTY = {
    "en": {
        # 한국어 화자에게 어려운 발음
        "th_voiced": {"sound": "ð", "difficulty": 5, "tip": "Put your tongue between your teeth and vibrate"},
        "th_voiceless": {"sound": "θ", "difficulty": 5, "tip": "Put your tongue between your teeth without vibration"},
        "r_sound": {"sound": "r", "difficulty": 4, "tip": "Curl your tongue back, don't touch the roof"},
        "l_sound": {"sound": "l", "difficulty": 3, "tip": "Touch the roof of your mouth with tongue tip"},
        "v_sound": {"sound": "v", "difficulty": 3, "tip": "Bite your lower lip gently and vibrate"},
        "f_sound": {"sound": "f", "difficulty": 2, "tip": "Bite your lower lip gently without vibration"},
        "z_sound": {"sound": "z", "difficulty": 3, "tip": "Like 's' but with voice vibration"},
        "ʃ_sound": {"sound": "ʃ", "difficulty": 2, "tip": "Like 'sh' in 'ship'"},
        "ʒ_sound": {"sound": "ʒ", "difficulty": 4, "tip": "Like 's' in 'measure'"},
        "æ_sound": {"sound": "æ", "difficulty": 4, "tip": "Open mouth wide, tongue low and front"},
        "ʌ_sound": {"sound": "ʌ", "difficulty": 3, "tip": "Relaxed, central vowel like 'uh'"},
        "ɪ_sound": {"sound": "ɪ", "difficulty": 2, "tip": "Short 'i' sound, relax your mouth"},
    }
}


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
    difficult_sounds: List[Dict[str, Any]] = field(default_factory=list)
    ipa_comparison: Optional[Dict[str, str]] = None


@dataclass
class WordPronunciationInfo:
    """단어 발음 정보."""
    word: str
    ipa: str
    syllables: List[str]
    stress_pattern: str  # e.g., "1-0-0" for 3 syllables, stress on first
    audio_base64: Optional[str] = None
    difficulty_level: int = 1  # 1-5
    difficult_sounds: List[Dict[str, Any]] = field(default_factory=list)
    similar_words: List[str] = field(default_factory=list)
    common_mistakes: List[str] = field(default_factory=list)


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
        """IPA 발음 기호 조회."""
        word_lower = word.lower().strip()
        lang_dict = IPA_DICTIONARY.get(language, IPA_DICTIONARY.get("en", {}))

        # 사전에서 직접 조회
        if word_lower in lang_dict:
            return f"/{lang_dict[word_lower]}/"

        # 영어의 경우 규칙 기반 IPA 생성 시도
        if language == "en":
            return f"/{self._generate_ipa_english(word_lower)}/"

        return f"/{word_lower}/"

    def _generate_ipa_english(self, word: str) -> str:
        """영어 단어의 규칙 기반 IPA 생성."""
        # 기본적인 영어 철자-발음 규칙
        ipa_rules = {
            # 이중 모음
            "oo": "uː",
            "ee": "iː",
            "ea": "iː",
            "ai": "eɪ",
            "ay": "eɪ",
            "oa": "oʊ",
            "ow": "aʊ",
            "ou": "aʊ",
            "oi": "ɔɪ",
            "oy": "ɔɪ",
            # 자음
            "th": "θ",
            "sh": "ʃ",
            "ch": "tʃ",
            "ph": "f",
            "wh": "w",
            "ck": "k",
            "ng": "ŋ",
            # 단일 모음 (기본)
            "a": "æ",
            "e": "ɛ",
            "i": "ɪ",
            "o": "ɑ",
            "u": "ʌ",
        }

        result = word
        for pattern, replacement in sorted(ipa_rules.items(), key=lambda x: -len(x[0])):
            result = result.replace(pattern, replacement)

        return result

    def _split_syllables(self, word: str, language: str) -> List[str]:
        """음절 분리."""
        if language != "en":
            return [word]

        rules = SYLLABLE_RULES.get("en", {})
        vowels = rules.get("vowels", "aeiouy")

        word_lower = word.lower()
        syllables = []
        current = ""

        i = 0
        while i < len(word_lower):
            current += word_lower[i]

            # 현재 위치가 모음이고, 다음 문자가 자음이면
            if word_lower[i] in vowels:
                # 다음 문자들 확인
                if i + 1 < len(word_lower):
                    next_char = word_lower[i + 1]

                    # 다음이 자음이고, 그 다음이 모음이면 여기서 분리
                    if next_char not in vowels and i + 2 < len(word_lower):
                        if word_lower[i + 2] in vowels:
                            syllables.append(current)
                            current = ""
            i += 1

        if current:
            syllables.append(current)

        # 너무 짧은 음절 병합
        if len(syllables) > 1 and len(syllables[-1]) == 1:
            syllables[-2] += syllables[-1]
            syllables = syllables[:-1]

        return syllables if syllables else [word]

    def _get_stress_pattern(self, word: str, language: str) -> str:
        """강세 패턴 분석."""
        syllables = self._split_syllables(word, language)
        n_syllables = len(syllables)

        if n_syllables == 1:
            return "1"

        # IPA에서 강세 마커 확인
        ipa = self._get_ipa(word, language)
        if "ˈ" in ipa:  # 주강세
            # 강세 위치 찾기
            ipa_clean = ipa.strip("/")
            stress_pos = ipa_clean.find("ˈ")
            # 대략적인 음절 위치 계산
            if stress_pos < len(ipa_clean) // n_syllables:
                return "1" + "-0" * (n_syllables - 1)
            elif stress_pos < 2 * len(ipa_clean) // n_syllables:
                return "0-1" + "-0" * (n_syllables - 2)
            else:
                return "0" * (n_syllables - 1) + "-1"

        # 영어 기본 규칙: 2음절은 보통 첫 음절에 강세
        if n_syllables == 2:
            return "1-0"
        elif n_syllables == 3:
            return "1-0-0"
        else:
            return "-".join(["1"] + ["0"] * (n_syllables - 1))

    def _analyze_difficult_sounds(self, word: str, language: str) -> List[Dict[str, Any]]:
        """단어 내 어려운 발음 분석."""
        if language != "en":
            return []

        difficulties = PRONUNCIATION_DIFFICULTY.get("en", {})
        ipa = self._get_ipa(word, language).strip("/")
        found = []

        for name, info in difficulties.items():
            sound = info["sound"]
            if sound in ipa or sound in word.lower():
                found.append({
                    "sound": sound,
                    "difficulty": info["difficulty"],
                    "tip": info["tip"],
                    "position": word.lower().find(sound[0]) if len(sound) == 1 else -1
                })

        return sorted(found, key=lambda x: -x["difficulty"])

    def _get_similar_words(self, word: str, language: str) -> List[str]:
        """발음이 비슷한 단어 찾기."""
        lang_dict = IPA_DICTIONARY.get(language, {})
        target_ipa = lang_dict.get(word.lower(), "")

        if not target_ipa:
            return []

        similar = []
        for w, ipa in lang_dict.items():
            if w != word.lower():
                # IPA 유사도 계산
                similarity = self._calculate_word_similarity(target_ipa, ipa)
                if similarity > 0.6:
                    similar.append(w)

        return similar[:5]

    def _get_common_mistakes(self, word: str, language: str) -> List[str]:
        """흔한 발음 실수 패턴."""
        mistakes = []
        word_lower = word.lower()

        if language == "en":
            # th 발음 실수
            if "th" in word_lower:
                mistakes.append("'th' sound: Don't pronounce as 's' or 'd'")
            # r/l 혼동
            if "r" in word_lower:
                mistakes.append("'r' sound: Don't flatten the tongue")
            if "l" in word_lower:
                mistakes.append("'l' sound: Touch the roof with tongue tip")
            # v/b 혼동
            if "v" in word_lower:
                mistakes.append("'v' sound: Use teeth on lower lip, not like 'b'")
            # 묵음 문자
            silent_patterns = {
                "kn": "Silent 'k' at the beginning",
                "wr": "Silent 'w' at the beginning",
                "mb": "Silent 'b' at the end",
                "gh": "'gh' may be silent or pronounced as 'f'",
            }
            for pattern, msg in silent_patterns.items():
                if pattern in word_lower:
                    mistakes.append(msg)

        return mistakes

    async def get_detailed_word_info(
        self,
        word: str,
        language: str = "en"
    ) -> WordPronunciationInfo:
        """
        단어의 상세 발음 정보 조회

        Args:
            word: 단어
            language: 언어

        Returns:
            WordPronunciationInfo: 상세 발음 정보
        """
        ipa = self._get_ipa(word, language)
        syllables = self._split_syllables(word, language)
        stress = self._get_stress_pattern(word, language)
        difficult_sounds = self._analyze_difficult_sounds(word, language)
        similar = self._get_similar_words(word, language)
        mistakes = self._get_common_mistakes(word, language)

        # 난이도 계산
        difficulty = 1
        if difficult_sounds:
            difficulty = max(d["difficulty"] for d in difficult_sounds)

        # TTS 오디오 생성
        try:
            audio_data = await self.synthesize(word, speed=0.8)
            audio_base64 = base64.b64encode(audio_data).decode()
        except Exception:
            audio_base64 = None

        return WordPronunciationInfo(
            word=word,
            ipa=ipa,
            syllables=syllables,
            stress_pattern=stress,
            audio_base64=audio_base64,
            difficulty_level=difficulty,
            difficult_sounds=difficult_sounds,
            similar_words=similar,
            common_mistakes=mistakes
        )

    async def analyze_sentence_pronunciation(
        self,
        sentence: str,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        문장 전체의 발음 분석

        Args:
            sentence: 분석할 문장
            language: 언어

        Returns:
            문장 발음 분석 결과
        """
        words = sentence.split()
        word_analyses = []
        total_difficulty = 0

        for word in words:
            # 구두점 제거
            clean_word = re.sub(r'[^\w]', '', word)
            if clean_word:
                info = await self.get_detailed_word_info(clean_word, language)
                word_analyses.append({
                    "word": clean_word,
                    "ipa": info.ipa,
                    "difficulty": info.difficulty_level,
                    "difficult_sounds": info.difficult_sounds[:2]  # 상위 2개
                })
                total_difficulty += info.difficulty_level

        avg_difficulty = total_difficulty / len(word_analyses) if word_analyses else 1

        # 연음/연결 발음 분석
        linking_notes = self._analyze_linking(words, language)

        # 억양 패턴 제안
        intonation = self._suggest_intonation(sentence, language)

        return {
            "sentence": sentence,
            "word_count": len(words),
            "word_analyses": word_analyses,
            "average_difficulty": round(avg_difficulty, 1),
            "linking_notes": linking_notes,
            "intonation_suggestion": intonation,
            "practice_tips": self._generate_practice_tips(word_analyses, language)
        }

    def _analyze_linking(self, words: List[str], language: str) -> List[str]:
        """연음/연결 발음 분석."""
        if language != "en":
            return []

        notes = []
        vowels = "aeiouAEIOU"

        for i in range(len(words) - 1):
            word1 = words[i].rstrip(".,!?;:")
            word2 = words[i + 1]

            if not word1 or not word2:
                continue

            last_char = word1[-1].lower()
            first_char = word2[0].lower()

            # 자음 -> 모음: 연결 발음
            if last_char not in vowels and first_char in vowels:
                notes.append(f"Link '{word1}' to '{word2}': Connect the final consonant to the next vowel")

            # 모음 -> 모음: 글라이드 삽입
            elif last_char in vowels and first_char in vowels:
                if last_char in "iey":
                    notes.append(f"'{word1} {word2}': Add a slight 'y' sound between words")
                elif last_char in "ouw":
                    notes.append(f"'{word1} {word2}': Add a slight 'w' sound between words")

        return notes[:3]  # 최대 3개

    def _suggest_intonation(self, sentence: str, language: str) -> str:
        """억양 패턴 제안."""
        sentence = sentence.strip()

        if sentence.endswith("?"):
            if sentence.lower().startswith(("do", "does", "did", "is", "are", "was", "were", "can", "will", "should")):
                return "Yes/No question: Rising intonation at the end ↗"
            elif sentence.lower().startswith(("what", "where", "when", "why", "how", "who")):
                return "Wh-question: Falling intonation at the end ↘"
            return "Question: Generally rising intonation ↗"

        elif sentence.endswith("!"):
            return "Exclamation: Strong stress on key words, falling at end ↘"

        elif "," in sentence:
            return "List/complex sentence: Rise at commas, fall at the end ↗...↗...↘"

        else:
            return "Statement: Slight fall at the end for finality ↘"

    def _generate_practice_tips(
        self,
        word_analyses: List[Dict],
        language: str
    ) -> List[str]:
        """연습 팁 생성."""
        tips = []

        # 가장 어려운 단어 찾기
        difficult_words = [w for w in word_analyses if w["difficulty"] >= 3]
        if difficult_words:
            words = ", ".join(w["word"] for w in difficult_words[:3])
            tips.append(f"Focus on these challenging words: {words}")

        # 공통 어려운 소리 찾기
        all_sounds = []
        for w in word_analyses:
            all_sounds.extend([s["sound"] for s in w.get("difficult_sounds", [])])

        if all_sounds:
            common_sound = max(set(all_sounds), key=all_sounds.count)
            tips.append(f"Practice the '{common_sound}' sound - it appears multiple times")

        tips.append("Record yourself and compare with the TTS audio")
        tips.append("Practice slowly first, then gradually increase speed")

        return tips

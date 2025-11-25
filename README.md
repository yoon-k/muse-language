# MUSE Language

AI 기반 언어 학습 플랫폼 - 개인 맞춤형 언어 교육 시스템

## Features

### AI 튜터 시스템
- **실시간 대화 연습**: AI와 자연스러운 대화로 회화 실력 향상
- **문법 교정**: 실시간 문법 오류 감지 및 상세 설명
- **발음 평가**: 음성 인식 기반 발음 정확도 분석
- **맞춤형 피드백**: 학습자 수준에 맞는 개인화된 조언

### 학습 콘텐츠
- **적응형 학습**: AI가 분석한 약점 기반 맞춤 커리큘럼
- **다국어 지원**: 영어, 일본어, 중국어, 스페인어, 프랑스어
- **레벨별 콘텐츠**: CEFR 기준 A1~C2 레벨
- **상황별 학습**: 비즈니스, 여행, 일상 등 목적별 학습

### 게이미피케이션
- **일일 미션**: 매일 달성 가능한 학습 목표
- **스트릭 시스템**: 연속 학습 보상
- **리더보드**: 주간/월간 학습 랭킹
- **뱃지 & 업적**: 학습 성취 보상

### 음성 기능
- **STT (Speech-to-Text)**: 음성 입력으로 대화 연습
- **TTS (Text-to-Speech)**: 원어민 발음 청취
- **발음 점수**: 음소 단위 발음 정확도 측정
- **억양 분석**: 문장 억양 패턴 분석

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL + Redis
- **AI**: OpenAI GPT-4, Whisper, TTS
- **Speech**: Google Cloud Speech API
- **Queue**: Celery + Redis

### Frontend (Web)
- **Framework**: React 18 + TypeScript
- **State**: Zustand
- **Styling**: Tailwind CSS
- **Audio**: Web Audio API

### Mobile
- **iOS**: SwiftUI + AVFoundation
- **Android**: Kotlin + Jetpack Compose

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Apps                          │
├──────────────┬──────────────────┬──────────────────────────┤
│   React Web  │   iOS (SwiftUI)  │   Android (Compose)      │
└──────┬───────┴────────┬─────────┴────────────┬─────────────┘
       │                │                       │
       └────────────────┼───────────────────────┘
                        │
              ┌─────────▼─────────┐
              │   API Gateway     │
              │   (FastAPI)       │
              └─────────┬─────────┘
                        │
       ┌────────────────┼────────────────┐
       │                │                │
┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐
│  AI Tutor   │  │   Speech    │  │   Content   │
│  Service    │  │   Service   │  │   Service   │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                │
       │         ┌──────▼──────┐         │
       │         │   Whisper   │         │
       │         │   + TTS     │         │
       │         └─────────────┘         │
       │                                 │
┌──────▼─────────────────────────────────▼──────┐
│                 PostgreSQL                     │
│            + Redis (Cache/Queue)               │
└───────────────────────────────────────────────┘
```

## API Endpoints

### 학습 세션
```
POST   /api/v1/sessions              # 학습 세션 시작
GET    /api/v1/sessions/{id}         # 세션 상태 조회
POST   /api/v1/sessions/{id}/message # AI 튜터와 대화
POST   /api/v1/sessions/{id}/audio   # 음성 입력
DELETE /api/v1/sessions/{id}         # 세션 종료
```

### 학습 콘텐츠
```
GET    /api/v1/lessons               # 레슨 목록
GET    /api/v1/lessons/{id}          # 레슨 상세
POST   /api/v1/lessons/{id}/complete # 레슨 완료
GET    /api/v1/vocabulary            # 단어장
POST   /api/v1/vocabulary/review     # 단어 복습
```

### 발음 평가
```
POST   /api/v1/pronunciation/evaluate # 발음 평가
GET    /api/v1/pronunciation/history  # 발음 기록
```

### 진도 & 통계
```
GET    /api/v1/progress              # 학습 진도
GET    /api/v1/stats                 # 학습 통계
GET    /api/v1/achievements          # 업적 목록
GET    /api/v1/leaderboard           # 리더보드
```

## Quick Start

### Backend
```bash
cd app
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 환경변수 설정
cp .env.example .env
# .env 파일 편집

# 서버 실행
uvicorn app.main:app --reload
```

### Frontend (Web)
```bash
cd frontend
npm install
npm run dev
```

### Docker
```bash
docker-compose up -d
```

## Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/muse_language

# Redis
REDIS_URL=redis://localhost:6379

# AI Services
OPENAI_API_KEY=your_openai_key

# Speech Services (Optional)
GOOGLE_CLOUD_CREDENTIALS=path/to/credentials.json

# Security
SECRET_KEY=your-secret-key
```

## Learning Algorithm

### 간격 반복 시스템 (Spaced Repetition)
```
복습 간격 = 기본_간격 × (2.5 ^ 정답_연속_횟수) × 난이도_계수
```

### 적응형 난이도 조절
- 정답률 > 80%: 난이도 상승
- 정답률 < 50%: 난이도 하락
- 응답 시간 고려한 숙련도 측정

### CEFR 레벨 매핑
| 레벨 | 설명 | 어휘 수 |
|------|------|---------|
| A1 | 입문 | ~1,000 |
| A2 | 초급 | ~2,000 |
| B1 | 중급 | ~4,000 |
| B2 | 중상급 | ~6,000 |
| C1 | 고급 | ~10,000 |
| C2 | 원어민 수준 | 10,000+ |

## License

MIT License

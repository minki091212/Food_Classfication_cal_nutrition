# 🍱 Food Nutrition AI
### LangChain + Google Gemini (무료 티어) + ChromaDB

이미지에서 음식을 인식하고, RAG 기반으로 칼로리 및 영양 정보를 JSON으로 제공하는 AI 시스템.

## 아키텍처

```
이미지 (파일 / URL)
  │
  ▼
[Vision Chain]  Gemini Vision (gemini-1.5-flash)
  │               └─ LangChain HumanMessage (image_url block)
  │               └─ StrOutputParser
  │
  ▼  ["비빔밥", "된장국", ...]
  │
  ▼ (음식명별 반복)
[RAG Chain]     ChromaDB 벡터 검색
  │               └─ Gemini Embedding (text-embedding-004)
  │               └─ similarity_search (top-k)
  │               └─ format_docs → context string
  │
  ▼
[LLM Chain]     ChatGemini (gemini-1.5-flash)
  │               └─ ChatPromptTemplate (system + human)
  │               └─ JsonOutputParser
  │
  ▼
[JSON 출력]
```

## 사용 모델 (모두 무료 티어)

| 용도 | 모델 |
|------|------|
| 이미지 인식 + 텍스트 생성 | `gemini-1.5-flash` |
| 벡터 임베딩 | `snunlp/KR-SBERT-V40K-klueNLI-augSTS` |

## 설치

```bash
# 1. 의존성 설치 (uv)
uv sync

# 2. 환경변수 설정
cp .env.example .env
# .env 파일에 GOOGLE_API_KEY 입력
# API 키 발급: https://aistudio.google.com/app/apikey
```

## 사용법

### 1단계: 식품 데이터 벡터 DB 구축 (최초 1회)

xlsx 파일을 `data/`에 놓고 실행:

```bash
uv run ingest
```

### 2단계: 이미지 분석

```bash
# 로컬 파일
uv run analyze food.jpg

# URL 이미지
uv run analyze https://example.com/bibimbap.jpg

# 결과를 JSON 파일로 저장
uv run analyze food.jpg -o result.json
```

### Python 코드에서 사용

```python
from src.api import analyze_from_file, analyze_from_url, analyze_from_food_names

# 파일
result = analyze_from_file("food.jpg")

# URL
result = analyze_from_url("https://example.com/food.jpg")

# 음식명 직접 입력 (Vision 단계 생략)
result = analyze_from_food_names(["비빔밥", "된장국"])

import json
print(json.dumps(result, ensure_ascii=False, indent=2))
```

## 출력 예시

```json
[
  {
    "food_name": "비빔밥",
    "input_name": "비빔밥",
    "serving_size": "100g",
    "calories_kcal": 130.0,
    "nutrients": {
      "protein_g": 4.2,
      "fat_g": 2.5,
      "carbohydrate_g": 21.3,
      "sugar_g": 1.8,
      "dietary_fiber_g": 1.2,
      "moisture_g": 69.5,
      "ash_g": 1.1,
      "calcium_mg": 22.0,
      "iron_mg": 1.3,
      "phosphorus_mg": 78.0,
      "potassium_mg": 210.0,
      "sodium_mg": 380.0
    },
    "match_confidence": "high",
    "note": ""
  }
]
```

## 프로젝트 구조

```
food-nutrition-ai/
├── data/
│   ├── food_data.xlsx        ← 직접 준비 (농식품부 등 공공 데이터)
│   └── chroma_db/            ← ingest 실행 시 자동 생성
├── src/
│   ├── config.py             환경변수 & 모델/경로 설정
│   ├── ingest.py             xlsx → LangChain Document → ChromaDB
│   ├── retriever.py          LangChain Chroma 벡터 검색 (RAG)
│   ├── vision.py             LangChain + Gemini Vision 음식 인식
│   ├── analyzer.py           LangChain RAG Chain → 영양 정보 JSON
│   ├── main.py               CLI 진입점
│   └── api.py                Python import용 공개 API
├── .env.example
├── pyproject.toml
└── README.md
```

## Gemini 무료 티어 한도 (2024년 기준)

| 모델 | 분당 요청 | 일일 요청 |
|------|-----------|-----------|
| gemini-1.5-flash | 15 RPM | 1,500 |

> ingest 시 배치 크기를 100으로 제한해 rate limit을 방지합니다.
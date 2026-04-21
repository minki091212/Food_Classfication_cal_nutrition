# 🍱 Food Nutrition AI
### LangChain + Google Gemini (무료) + SQLite

## 아키텍처

```
이미지 (파일 / URL)
  │
  ▼
[Step 1] Gemini Vision → 음식명 추론
  │        예: "비빔밥, 된장국"
  │
  ▼ (음식명별 반복)
[Step 2] SQLite 조회 (food_name 검색)
  │
  ├─ 있음 ──► DB 데이터 반환  (source: "db")
  │
  └─ 없음 ──► Gemini LLM 추정 (source: "llm")
                └─ 영양 정보 직접 생성
  │
  ▼
[JSON 출력]
```

## 설치

```bash
uv sync
cp .env.example .env
# .env 에 GOOGLE_API_KEY 입력
# 발급: https://aistudio.google.com/app/apikey
```

## 사용법

### 1단계: SQLite DB 구축 (최초 1회)

```bash
uv run ingest
```

### 2단계: 이미지 분석

```bash
uv run analyze food.jpg
uv run analyze food.jpg -o result.json
uv run analyze https://example.com/food.jpg
```

## 출력 예시

```json
[
  {
    "input_name": "비빔밥",
    "food_name": "비빔밥",
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
    "source": "db",
    "note": ""
  },
  {
    "input_name": "파스타",
    "food_name": "파스타",
    "serving_size": "1인분(200g)",
    "calories_kcal": 310.0,
    "nutrients": { "..." : "..." },
    "source": "llm",
    "note": "DB에 데이터 없음. LLM 추정값입니다."
  }
]
```

## 프로젝트 구조

```
food-nutrition-ai/
├── data/
│   ├── 20260402_가공식품_268422건.xlsx
│   ├── 20251229_음식DB 19495건.xlsx
│   └── food.db                  ← ingest 실행 시 자동 생성
├── src/
│   ├── config.py                설정
│   ├── ingest.py                xlsx → SQLite 변환
│   ├── db.py                    SQLite 조회
│   ├── vision.py                Gemini Vision 음식 인식
│   ├── llm_fallback.py          DB 미존재 시 LLM 추정
│   ├── analyzer.py              DB조회 → fallback 조합
│   ├── main.py                  CLI 진입점
│   └── api.py                   Python import용 API
├── .env.example
├── pyproject.toml
└── README.md
```
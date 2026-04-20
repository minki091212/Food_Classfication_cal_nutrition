from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

# ── API 키 ────────────────────────────────────────────────────────────
GOOGLE_API_KEY: str = os.environ["GOOGLE_API_KEY"]

# ── Gemini 모델 (LLM + Vision) ────────────────────────────────────────
VISION_MODEL = "gemini-2.5-flash-lite"

# ── 임베딩: HuggingFace 로컬 모델 (무료, API 키 불필요) ──────────────
# 한국어 특화 모델 - 최초 실행 시 자동 다운로드 (~400MB)
EMBEDDING_MODEL = "snunlp/KR-SBERT-V40K-klueNLI-augSTS"

# ── 경로 설정 ─────────────────────────────────────────────────────────
_raw_paths = os.getenv(
    "FOOD_DATA_PATHS",
    "data/20260402_가공식품_268422건.xlsx,data/20251229_음식DB 19495건.xlsx",
)
FOOD_DATA_PATHS: list[Path] = [Path(p.strip()) for p in _raw_paths.split(",") if p.strip()]

CHROMA_DB_PATH: str = os.getenv("CHROMA_DB_PATH", "data/chroma_db")
COLLECTION_NAME = "food_nutrition"
TOP_K: int = int(os.getenv("TOP_K", "5"))

# ── 사용 컬럼 ─────────────────────────────────────────────────────────
NUTRITION_COLUMNS = [
    "식품명",
    "영양성분함량기준량",
    "에너지(kcal)",
    "수분(g)",
    "단백질(g)",
    "지방(g)",
    "회분(g)",
    "탄수화물(g)",
    "당류(g)",
    "식이섬유(g)",
    "칼슘(mg)",
    "철(mg)",
    "인(mg)",
    "칼륨(mg)",
    "나트륨(mg)",
]
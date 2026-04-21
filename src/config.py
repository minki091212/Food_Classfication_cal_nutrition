from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

GOOGLE_API_KEY: str = os.environ["GOOGLE_API_KEY"]
VISION_MODEL        = "gemini-1.5-flash"

_raw_paths = os.getenv(
    "FOOD_DATA_PATHS",
    "data/20260402_가공식품_268422건.xlsx,data/20251229_음식DB 19495건.xlsx",
)
FOOD_DATA_PATHS: list[Path] = [Path(p.strip()) for p in _raw_paths.split(",") if p.strip()]
DB_PATH: str = os.getenv("DB_PATH", "data/food.db")

# xlsx에서 사용할 컬럼 → SQLite 컬럼명 매핑
COLUMN_MAP: dict[str, str] = {
    "식품명":            "food_name",
    "영양성분함량기준량": "serving_size",
    "에너지(kcal)":      "calories_kcal",
    "수분(g)":           "moisture_g",
    "단백질(g)":         "protein_g",
    "지방(g)":           "fat_g",
    "회분(g)":           "ash_g",
    "탄수화물(g)":       "carbohydrate_g",
    "당류(g)":           "sugar_g",
    "식이섬유(g)":       "dietary_fiber_g",
    "칼슘(mg)":          "calcium_mg",
    "철(mg)":            "iron_mg",
    "인(mg)":            "phosphorus_mg",
    "칼륨(mg)":          "potassium_mg",
    "나트륨(mg)":        "sodium_mg",
}
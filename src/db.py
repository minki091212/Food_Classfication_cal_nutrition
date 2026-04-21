"""
SQLite에서 식품명으로 조회하는 모듈
"""
import sqlite3
from src.config import DB_PATH

# 반환할 컬럼 목록
FIELDS = [
    "food_name", "serving_size", "calories_kcal",
    "protein_g", "fat_g", "carbohydrate_g", "sugar_g",
    "dietary_fiber_g", "moisture_g", "ash_g",
    "calcium_mg", "iron_mg", "phosphorus_mg", "potassium_mg", "sodium_mg",
]


def _row_to_dict(row: tuple) -> dict:
    return dict(zip(FIELDS, row))


def search_exact(food_name: str) -> dict | None:
    """
    식품명 완전 일치 검색.
    여러 건이면 첫 번째 반환.
    """
    sql = f"SELECT {', '.join(FIELDS)} FROM foods WHERE food_name = ? LIMIT 1"
    with sqlite3.connect(DB_PATH) as con:
        row = con.execute(sql, (food_name,)).fetchone()
    return _row_to_dict(row) if row else None


def search_like(food_name: str, limit: int = 5) -> list[dict]:
    """
    식품명 부분 일치 검색 (LIKE).
    LLM이 추론한 이름과 DB 이름이 약간 다를 때 사용.
    """
    sql = f"""
        SELECT {', '.join(FIELDS)} FROM foods
        WHERE food_name LIKE ?
        LIMIT {limit}
    """
    with sqlite3.connect(DB_PATH) as con:
        rows = con.execute(sql, (f"%{food_name}%",)).fetchall()
    return [_row_to_dict(r) for r in rows]


def find_best(food_name: str) -> dict | None:
    """
    1) 완전 일치 시도
    2) 없으면 LIKE 부분 일치에서 첫 번째 반환
    3) 둘 다 없으면 None
    """
    result = search_exact(food_name)
    if result:
        return result

    candidates = search_like(food_name, limit=1)
    return candidates[0] if candidates else None
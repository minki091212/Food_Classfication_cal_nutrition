"""
핵심 분석 로직:
  음식명 리스트
    └─► SQLite 조회 (find_best)
          ├─ 있음 → DB 데이터 반환 (source: "db")
          └─ 없음 → LLM 추정   (source: "llm")
"""
from src.db import find_best
from src.llm_fallback import estimate_nutrition


def _format_db_result(food_name: str, row: dict) -> dict:
    """DB 조회 결과를 최종 출력 형식으로 변환"""
    return {
        "input_name":    food_name,
        "food_name":     row["food_name"],
        "serving_size":  row.get("serving_size") or "",
        "calories_kcal": row.get("calories_kcal"),
        "nutrients": {
            "protein_g":       row.get("protein_g"),
            "fat_g":           row.get("fat_g"),
            "carbohydrate_g":  row.get("carbohydrate_g"),
            "sugar_g":         row.get("sugar_g"),
            "dietary_fiber_g": row.get("dietary_fiber_g"),
            "moisture_g":      row.get("moisture_g"),
            "ash_g":           row.get("ash_g"),
            "calcium_mg":      row.get("calcium_mg"),
            "iron_mg":         row.get("iron_mg"),
            "phosphorus_mg":   row.get("phosphorus_mg"),
            "potassium_mg":    row.get("potassium_mg"),
            "sodium_mg":       row.get("sodium_mg"),
        },
        "source": "db",
        "note": "",
    }


def _format_llm_result(food_name: str, llm_data: dict) -> dict:
    """LLM 추정 결과를 최종 출력 형식으로 변환"""
    return {
        "input_name":    food_name,
        "food_name":     llm_data.get("food_name", food_name),
        "serving_size":  llm_data.get("serving_size") or "",
        "calories_kcal": llm_data.get("calories_kcal"),
        "nutrients": {
            "protein_g":       llm_data.get("protein_g"),
            "fat_g":           llm_data.get("fat_g"),
            "carbohydrate_g":  llm_data.get("carbohydrate_g"),
            "sugar_g":         llm_data.get("sugar_g"),
            "dietary_fiber_g": llm_data.get("dietary_fiber_g"),
            "moisture_g":      llm_data.get("moisture_g"),
            "ash_g":           llm_data.get("ash_g"),
            "calcium_mg":      llm_data.get("calcium_mg"),
            "iron_mg":         llm_data.get("iron_mg"),
            "phosphorus_mg":   llm_data.get("phosphorus_mg"),
            "potassium_mg":    llm_data.get("potassium_mg"),
            "sodium_mg":       llm_data.get("sodium_mg"),
        },
        "source": "llm",
        "note": "DB에 데이터 없음. LLM 추정값입니다.",
    }


def analyze_nutrition(food_names: list[str]) -> list[dict]:
    """
    음식명 리스트를 받아 각각 DB 조회 → LLM fallback 처리 후 반환

    Args:
        food_names: ["비빔밥", "된장국"] 형태

    Returns:
        source 가 "db" 또는 "llm" 인 영양 정보 딕셔너리 리스트
    """
    results = []
    for food_name in food_names:
        row = find_best(food_name)
        if row:
            results.append(_format_db_result(food_name, row))
        else:
            llm_data = estimate_nutrition(food_name)
            results.append(_format_llm_result(food_name, llm_data))
    return results
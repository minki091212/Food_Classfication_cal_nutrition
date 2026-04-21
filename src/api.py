"""
다른 Python 코드에서 import해서 사용할 수 있는 공개 인터페이스

사용 예시:
    from src.api import analyze_from_file, analyze_from_url, analyze_from_food_names
"""
from pathlib import Path
from src.vision import recognize_from_file, recognize_from_url
from src.analyzer import analyze_nutrition


def analyze_from_file(image_path: str | Path) -> list[dict]:
    """로컬 이미지 파일에서 영양 정보 분석"""
    food_names = recognize_from_file(image_path)
    return analyze_nutrition(food_names) if food_names else []


def analyze_from_url(image_url: str) -> list[dict]:
    """이미지 URL에서 영양 정보 분석"""
    food_names = recognize_from_url(image_url)
    return analyze_nutrition(food_names) if food_names else []


def analyze_from_food_names(food_names: list[str]) -> list[dict]:
    """음식명 리스트에서 직접 영양 정보 분석 (Vision 단계 생략)"""
    return analyze_nutrition(food_names) if food_names else []
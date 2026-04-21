"""
DB에 해당 식품이 없을 때 Gemini LLM이 영양 정보를 직접 추론하는 모듈
"""
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from src.config import GOOGLE_API_KEY, VISION_MODEL

SYSTEM_PROMPT = """당신은 식품 영양 전문가입니다.
요청된 음식의 영양 정보를 최대한 정확하게 추정해 주세요.
반드시 순수한 JSON 객체만 출력하세요. 마크다운이나 설명은 절대 포함하지 마세요."""

USER_PROMPT = """음식명: {food_name}

아래 JSON 형식으로 '{food_name}'의 영양 정보를 반환하세요.
DB에 데이터가 없어 LLM이 추정하는 값입니다.

{{
  "food_name": "{food_name}",
  "serving_size": "일반적인 1회 제공량 (예: 100g, 1인분(300g))",
  "calories_kcal": 숫자 또는 null,
  "protein_g": 숫자 또는 null,
  "fat_g": 숫자 또는 null,
  "carbohydrate_g": 숫자 또는 null,
  "sugar_g": 숫자 또는 null,
  "dietary_fiber_g": 숫자 또는 null,
  "moisture_g": 숫자 또는 null,
  "ash_g": 숫자 또는 null,
  "calcium_mg": 숫자 또는 null,
  "iron_mg": 숫자 또는 null,
  "phosphorus_mg": 숫자 또는 null,
  "potassium_mg": 숫자 또는 null,
  "sodium_mg": 숫자 또는 null
}}"""


def _get_llm():
    return ChatGoogleGenerativeAI(
        model=VISION_MODEL,
        google_api_key=GOOGLE_API_KEY,
        max_output_tokens=1024,
        temperature=0,
    )


def estimate_nutrition(food_name: str) -> dict:
    """DB에 없는 음식의 영양 정보를 LLM으로 추정"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", USER_PROMPT),
    ])
    chain = prompt | _get_llm() | JsonOutputParser()
    return chain.invoke({"food_name": food_name})
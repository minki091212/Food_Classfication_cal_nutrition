"""
LangChain RAG Chain: 음식명 → 벡터 검색 → Gemini LLM → 영양 정보 JSON

핵심 흐름:
  food_name
    └─► retriever (ChromaDB similarity search)
          └─► context docs
                └─► PromptTemplate
                      └─► ChatGemini
                            └─► JsonOutputParser → dict
"""
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from pydantic import BaseModel, Field


from src.config import GOOGLE_API_KEY, TOP_K, VISION_MODEL
from src.retriever import get_vectorstore, search_foods, format_docs


# ── 출력 스키마 (Pydantic) ────────────────────────────────────────────
class Nutrients(BaseModel):
    protein_g: float | None = Field(None, description="단백질(g)")
    fat_g: float | None = Field(None, description="지방(g)")
    carbohydrate_g: float | None = Field(None, description="탄수화물(g)")
    sugar_g: float | None = Field(None, description="당류(g)")
    dietary_fiber_g: float | None = Field(None, description="식이섬유(g)")
    moisture_g: float | None = Field(None, description="수분(g)")
    ash_g: float | None = Field(None, description="회분(g)")
    calcium_mg: float | None = Field(None, description="칼슘(mg)")
    iron_mg: float | None = Field(None, description="철(mg)")
    phosphorus_mg: float | None = Field(None, description="인(mg)")
    potassium_mg: float | None = Field(None, description="칼륨(mg)")
    sodium_mg: float | None = Field(None, description="나트륨(mg)")


class FoodNutrition(BaseModel):
    food_name: str = Field(..., description="DB에서 선택된 정확한 식품명")
    input_name: str = Field(..., description="사용자가 입력한 음식명")
    serving_size: str = Field(..., description="기준량 (예: 100g)")
    calories_kcal: float | None = Field(None, description="에너지(kcal)")
    nutrients: Nutrients
    match_confidence: str = Field(..., description="high | medium | low")
    note: str = Field("", description="특이사항")


# ── 프롬프트 ─────────────────────────────────────────────────────────
SYSTEM_PROMPT = """당신은 식품 영양 정보 분석 전문가입니다.
제공된 식품 데이터베이스 후보 중 입력 음식명과 가장 유사한 항목을 선택하세요.
반드시 순수한 JSON 객체만 출력하세요. 마크다운 코드블록이나 설명은 절대 포함하지 마세요."""

USER_PROMPT = """음식명: {food_name}

아래는 식품 데이터베이스에서 검색된 후보 데이터입니다:
{context}

위 후보 중 '{food_name}'과 가장 유사한 항목을 선택해 아래 JSON 형식으로 반환하세요:
{{
  "food_name": "DB의 정확한 식품명",
  "input_name": "{food_name}",
  "serving_size": "기준량",
  "calories_kcal": 숫자 또는 null,
  "nutrients": {{
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
  }},
  "match_confidence": "high 또는 medium 또는 low",
  "note": "특이사항 또는 빈 문자열"
}}"""

def _build_rag_chain():
    llm = ChatGoogleGenerativeAI(
        model=VISION_MODEL,
        google_api_key=GOOGLE_API_KEY,
        max_output_tokens=1024,
        temperature=0,
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", USER_PROMPT),
    ])

    def retrieve_context(inputs: dict) -> dict:
        query = inputs["food_name"]
        vs = get_vectorstore()

        exact_docs = vs.similarity_search(
            query,
            k=TOP_K,
            filter={"식품명": query}
        )

        docs = exact_docs if exact_docs else vs.similarity_search(query, k=TOP_K)

        return {
            "food_name": query,
            "context": format_docs(docs),
        }

    chain = (
        RunnableLambda(retrieve_context)
        | prompt
        | llm
        | JsonOutputParser()
    )

    return chain

    # retriever를 RunnableLambda로 래핑 (단일 음식명 처리)
def retrieve_context(inputs: dict) -> dict:
    query = inputs["food_name"]

    vs = get_vectorstore()

    # 1. exact match 먼저
    exact_docs = vs.similarity_search(
        query,
        k=TOP_K,
        filter={"식품명": query}
    )

    # 2. fallback: 일반 유사도 검색
    docs = exact_docs if exact_docs else vs.similarity_search(query, k=TOP_K)

    return {
        "food_name": query,
        "context": format_docs(docs),
    }


def analyze_nutrition(food_names: list[str]) -> list[dict]:
    """
    음식명 리스트를 받아 각각 RAG Chain을 실행하고 결과 리스트 반환

    Args:
        food_names: ["비빔밥", "된장국"] 형태

    Returns:
        FoodNutrition 스키마 형태의 딕셔너리 리스트
    """
    chain = _build_rag_chain()
    results = []

    for food_name in food_names:
        result = chain.invoke({"food_name": food_name})
        results.append(result)

    return results
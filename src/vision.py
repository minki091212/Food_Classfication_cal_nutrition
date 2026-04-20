"""
LangChain + Gemini Vision으로 이미지에서 음식명을 인식하는 모듈
"""
import base64
from pathlib import Path

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser

from src.config import GOOGLE_API_KEY, VISION_MODEL


def _get_vision_llm() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=VISION_MODEL,
        google_api_key=GOOGLE_API_KEY,
        max_output_tokens=256,
        temperature=0,
    )


def _parse_food_names(raw: str) -> list[str]:
    """LLM 응답에서 음식명 리스트 파싱"""
    return [f.strip() for f in raw.strip().split(",") if f.strip()]


def _build_vision_message(image_block: dict) -> HumanMessage:
    return HumanMessage(
        content=[
            image_block,
            {
                "type": "text",
                "text": (
                    "이 이미지에서 보이는 음식을 한국어로 식별하세요.\n"
                    "반드시 쉼표로 구분된 음식명만 출력하세요. 설명은 하지 마세요.\n"
                    "예시: 비빔밥, 된장국, 깍두기"
                ),
            },
        ]
    )


def recognize_food_from_file(image_path: str | Path) -> list[str]:
    """
    로컬 이미지 파일에서 음식명 인식

    Returns: ["비빔밥", "된장국", ...] 형태의 리스트
    """
    path = Path(image_path)
    suffix = path.suffix.lower()
    media_map = {
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".png": "image/png", ".gif": "image/gif", ".webp": "image/webp",
    }
    media_type = media_map.get(suffix, "image/jpeg")
    data = base64.standard_b64encode(path.read_bytes()).decode("utf-8")

    image_block = {
        "type": "image_url",
        "image_url": {"url": f"data:{media_type};base64,{data}"},
    }

    llm = _get_vision_llm()
    chain = llm | StrOutputParser()
    result = chain.invoke([_build_vision_message(image_block)])
    return _parse_food_names(result)


def recognize_food_from_url(image_url: str) -> list[str]:
    """
    이미지 URL에서 음식명 인식

    Returns: ["비빔밥", "된장국", ...] 형태의 리스트
    """
    image_block = {
        "type": "image_url",
        "image_url": {"url": image_url},
    }

    llm = _get_vision_llm()
    chain = llm | StrOutputParser()
    result = chain.invoke([_build_vision_message(image_block)])
    return _parse_food_names(result)
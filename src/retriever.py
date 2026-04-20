"""
LangChain + ChromaDB로 음식명 쿼리에 유사한 식품 문서를 검색하는 모듈
"""
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain.tools import tool

from src.config import (
    CHROMA_DB_PATH,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
    TOP_K,
)

def get_vectorstore() -> Chroma:
    """저장된 ChromaDB 벡터스토어 로드"""
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
    return Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_DB_PATH,
        embedding_function=embeddings,
    )

def get_retriever(top_k: int = TOP_K):
    """LangChain Retriever 반환 (chain에 직접 연결 가능)"""
    return get_vectorstore().as_retriever(
        search_type="similarity",
        search_kwargs={"k": top_k},
    )


def search_foods(query: str, top_k: int = TOP_K) -> list[Document]:
    """음식명으로 유사 식품 문서 검색"""
    return get_vectorstore().similarity_search(query, k=top_k)


def format_docs(docs: list[Document]) -> str:
    """검색된 Document 리스트를 LLM 컨텍스트 문자열로 변환"""
    parts = [f"[후보 {i}]\n{doc.page_content}" for i, doc in enumerate(docs, 1)]
    return "\n\n---\n\n".join(parts)
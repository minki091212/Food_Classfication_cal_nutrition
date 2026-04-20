"""
여러 xlsx 식품 데이터를 읽어 합친 뒤
LangChain Document로 변환 후 HuggingFace 로컬 임베딩으로 ChromaDB에 저장

실행: uv run ingest
"""
from pathlib import Path
import shutil

import pandas as pd
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from rich.console import Console
from rich.progress import track

from src.config import (
    FOOD_DATA_PATHS,
    CHROMA_DB_PATH,
    COLLECTION_NAME,
    NUTRITION_COLUMNS,
    EMBEDDING_MODEL,
)

console = Console()


def load_all_xlsx(paths: list[Path]) -> pd.DataFrame:
    """여러 xlsx 파일을 읽어 필요한 컬럼만 추출 후 하나로 합침"""
    frames = []
    for path in paths:
        if not path.exists():
            console.print(f"[red]파일 없음 (건너뜀):[/red] {path}")
            continue

        console.print(f"[blue]로드 중:[/blue] {path.name}")
        df = pd.read_excel(path)

        available = [c for c in NUTRITION_COLUMNS if c in df.columns]
        missing   = [c for c in NUTRITION_COLUMNS if c not in df.columns]
        if missing:
            console.print(f"  [yellow]누락 컬럼:[/yellow] {missing}")

        df = df[available].dropna(subset=["식품명"]).reset_index(drop=True)
        df["source"] = path.name
        console.print(f"  [green]완료:[/green] {len(df):,}개 식품")
        frames.append(df)

    if not frames:
        raise FileNotFoundError(f"로드 가능한 파일이 없습니다: {paths}")

    combined = pd.concat(frames, ignore_index=True)
    console.print(f"\n[bold green]전체 합계:[/bold green] {len(combined):,}개 식품 ({len(frames)}개 파일 병합)\n")
    return combined


def df_to_documents(df: pd.DataFrame) -> list[Document]:
    """DataFrame 행을 LangChain Document로 변환"""
    docs = []
    for _, row in df.iterrows():
        lines = [f"{col}: {row[col]}" for col in NUTRITION_COLUMNS
                 if col in row.index and pd.notna(row[col])]
        page_content = "\n".join(lines)

        metadata: dict = {"source": str(row.get("source", ""))}
        for col in NUTRITION_COLUMNS:
            val = row.get(col)
            if val is None or (isinstance(val, float) and pd.isna(val)):
                metadata[col] = ""
            elif isinstance(val, (int, float)):
                metadata[col] = float(val)
            else:
                metadata[col] = str(val)

        docs.append(Document(page_content=page_content, metadata=metadata))
    return docs


def ingest(documents: list[Document]) -> None:
    """HuggingFace 로컬 임베딩으로 ChromaDB에 배치 저장"""
    if Path(CHROMA_DB_PATH).exists():
        shutil.rmtree(CHROMA_DB_PATH)
        console.print("[yellow]기존 벡터 DB 삭제[/yellow]")

    console.print(f"임베딩 모델 로드 중: [cyan]{EMBEDDING_MODEL}[/cyan]")
    console.print("(최초 실행 시 모델 다운로드 ~400MB, 이후 캐시 사용)\n")

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

    # 로컬 임베딩은 rate limit 없음 → 배치 500건
    batch_size = 500
    total = len(documents)
    vectorstore = None

    for start in track(range(0, total, batch_size), description="벡터 DB 저장 중..."):
        batch = documents[start : start + batch_size]
        ids   = [f"food_{i}" for i in range(start, start + len(batch))]

        if vectorstore is None:
            vectorstore = Chroma.from_documents(
                documents=batch,
                embedding=embeddings,
                ids=ids,
                collection_name=COLLECTION_NAME,
                persist_directory=CHROMA_DB_PATH,
            )
        else:
            vectorstore.add_documents(documents=batch, ids=ids)

    console.print(f"[bold green]✓ 저장 완료:[/bold green] {total:,}개 → {CHROMA_DB_PATH}")


def main():
    console.rule("[bold]식품 데이터 벡터 DB 구축[/bold]")
    console.print(f"대상 파일 {len(FOOD_DATA_PATHS)}개:")
    for p in FOOD_DATA_PATHS:
        console.print(f"  • {p}")
    console.print()

    df        = load_all_xlsx(FOOD_DATA_PATHS)
    documents = df_to_documents(df)
    ingest(documents)

    console.rule("[bold green]완료[/bold green]")


if __name__ == "__main__":
    main()
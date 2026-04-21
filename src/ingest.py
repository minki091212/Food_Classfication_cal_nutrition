"""
xlsx 식품 데이터를 SQLite DB로 변환 (최초 1회 실행)

실행: uv run ingest
"""
import sqlite3
from pathlib import Path

import pandas as pd
from rich.console import Console
from rich.progress import track

from src.config import FOOD_DATA_PATHS, DB_PATH, COLUMN_MAP

console = Console()

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS foods (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    food_name        TEXT NOT NULL,
    serving_size     TEXT,
    calories_kcal    REAL,
    moisture_g       REAL,
    protein_g        REAL,
    fat_g            REAL,
    ash_g            REAL,
    carbohydrate_g   REAL,
    sugar_g          REAL,
    dietary_fiber_g  REAL,
    calcium_mg       REAL,
    iron_mg          REAL,
    phosphorus_mg    REAL,
    potassium_mg     REAL,
    sodium_mg        REAL,
    source           TEXT
);
"""

CREATE_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_food_name ON foods (food_name);
"""


def load_all_xlsx(paths: list[Path]) -> pd.DataFrame:
    frames = []
    for path in paths:
        if not path.exists():
            console.print(f"[red]파일 없음 (건너뜀):[/red] {path}")
            continue

        console.print(f"[blue]로드 중:[/blue] {path.name}")
        df = pd.read_excel(path)

        # 필요한 컬럼만 선택
        available = {k: v for k, v in COLUMN_MAP.items() if k in df.columns}
        missing   = [k for k in COLUMN_MAP if k not in df.columns]
        if missing:
            console.print(f"  [yellow]누락 컬럼:[/yellow] {missing}")

        df = df[list(available.keys())].rename(columns=available)
        df = df.dropna(subset=["food_name"]).reset_index(drop=True)
        df["source"] = path.name
        console.print(f"  [green]완료:[/green] {len(df):,}개 식품")
        frames.append(df)

    if not frames:
        raise FileNotFoundError(f"로드 가능한 파일이 없습니다: {paths}")

    combined = pd.concat(frames, ignore_index=True)
    console.print(f"\n[bold green]전체 합계:[/bold green] {len(combined):,}개 ({len(frames)}개 파일)\n")
    return combined


def build_db(df: pd.DataFrame) -> None:
    db_path = Path(DB_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    if db_path.exists():
        db_path.unlink()
        console.print("[yellow]기존 DB 삭제[/yellow]")

    con = sqlite3.connect(DB_PATH)
    con.execute(CREATE_TABLE_SQL)
    con.execute(CREATE_INDEX_SQL)

    # 숫자 컬럼 강제 변환 (문자열 섞인 경우 대비)
    numeric_cols = [c for c in df.columns if c not in ("food_name", "serving_size", "source")]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    batch_size = 5000
    total = len(df)
    for start in track(range(0, total, batch_size), description="SQLite 저장 중..."):
        df.iloc[start : start + batch_size].to_sql(
            "foods", con, if_exists="append", index=False
        )

    con.commit()
    con.close()
    console.print(f"[bold green]✓ 완료:[/bold green] {total:,}개 → {DB_PATH}")


def main():
    console.rule("[bold]식품 데이터 SQLite DB 구축[/bold]")
    console.print(f"대상 파일 {len(FOOD_DATA_PATHS)}개:")
    for p in FOOD_DATA_PATHS:
        console.print(f"  • {p}")
    console.print()

    df = load_all_xlsx(FOOD_DATA_PATHS)
    build_db(df)

    console.rule("[bold green]완료[/bold green]")


if __name__ == "__main__":
    main()
"""
음식 이미지 → 영양 정보 JSON 변환 메인 CLI

실행:
  uv run analyze food.jpg
  uv run analyze https://example.com/food.jpg -o result.json
  uv run python -m src.main food.jpg
"""
import argparse
import json
import sys

from rich.console import Console
from rich.json import JSON
from rich.panel import Panel

from src.vision import recognize_food_from_file, recognize_food_from_url
from src.analyzer import analyze_nutrition

console = Console()


def run(image_source: str, output_file: str | None = None) -> list[dict]:
    # ── Step 1: 이미지에서 음식명 인식 (Gemini Vision) ────────────────
    console.rule("[bold blue]Step 1 · 음식 인식 (Gemini Vision)[/bold blue]")

    is_url = image_source.startswith("http://") or image_source.startswith("https://")
    console.print(f"[dim]{'URL' if is_url else '파일'}:[/dim] {image_source}")

    food_names = (
        recognize_food_from_url(image_source)
        if is_url
        else recognize_food_from_file(image_source)
    )

    if not food_names:
        console.print("[red]음식을 인식하지 못했습니다.[/red]")
        sys.exit(1)

    console.print(f"[green]인식된 음식:[/green] {', '.join(food_names)}")

    # ── Step 2: RAG 검색 + LLM 분석 (LangChain Chain) ────────────────
    console.rule("[bold blue]Step 2 · RAG 검색 + 영양 분석 (LangChain + Gemini)[/bold blue]")
    console.print(f"ChromaDB 검색 후 Gemini 분석 중... ({len(food_names)}개 음식)")

    result = analyze_nutrition(food_names)

    # ── Step 3: 결과 출력 ─────────────────────────────────────────────
    console.rule("[bold green]결과[/bold green]")
    console.print(Panel(JSON(json.dumps(result, ensure_ascii=False, indent=2)), title="영양 정보 JSON"))

    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        console.print(f"[green]저장 완료:[/green] {output_file}")

    return result


def main():
    parser = argparse.ArgumentParser(
        description="음식 이미지에서 칼로리 및 영양 정보를 분석합니다."
    )
    parser.add_argument("image", help="이미지 파일 경로 또는 URL")
    parser.add_argument("-o", "--output", help="결과를 저장할 JSON 파일 경로", default=None)
    args = parser.parse_args()
    run(args.image, args.output)


if __name__ == "__main__":
    main()
"""
음식 이미지 → 영양 정보 JSON 변환 CLI

실행:
  uv run analyze food.jpg
  uv run analyze https://example.com/food.jpg -o result.json
"""
import argparse
import json
import sys

from rich.console import Console
from rich.json import JSON
from rich.panel import Panel

from src.vision import recognize_from_file, recognize_from_url
from src.analyzer import analyze_nutrition

console = Console()


def run(image_source: str, output_file: str | None = None) -> list[dict]:
    # ── Step 1: 이미지 → 음식명 (Gemini Vision) ───────────────────────
    console.rule("[bold blue]Step 1 · 음식 인식 (Gemini Vision)[/bold blue]")

    is_url = image_source.startswith("http://") or image_source.startswith("https://")
    console.print(f"[dim]{'URL' if is_url else '파일'}:[/dim] {image_source}")

    food_names = recognize_from_url(image_source) if is_url else recognize_from_file(image_source)

    if not food_names:
        console.print("[red]음식을 인식하지 못했습니다.[/red]")
        sys.exit(1)

    console.print(f"[green]인식된 음식:[/green] {', '.join(food_names)}")

    # ── Step 2: DB 조회 → 없으면 LLM fallback ─────────────────────────
    console.rule("[bold blue]Step 2 · 영양 정보 조회[/bold blue]")

    results = analyze_nutrition(food_names)

    # 결과별 출처 표시
    for r in results:
        tag = "[green]DB[/green]" if r["source"] == "db" else "[yellow]LLM 추정[/yellow]"
        console.print(f"  {tag} {r['input_name']} → {r['food_name']}")

    # ── Step 3: 출력 ──────────────────────────────────────────────────
    console.rule("[bold green]결과[/bold green]")
    console.print(Panel(
        JSON(json.dumps(results, ensure_ascii=False, indent=2)),
        title="영양 정보 JSON",
    ))

    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        console.print(f"[green]저장 완료:[/green] {output_file}")

    return results


def main():
    parser = argparse.ArgumentParser(description="음식 이미지에서 영양 정보를 분석합니다.")
    parser.add_argument("image", help="이미지 파일 경로 또는 URL")
    parser.add_argument("-o", "--output", help="결과를 저장할 JSON 파일 경로", default=None)
    args = parser.parse_args()
    run(args.image, args.output)


if __name__ == "__main__":
    main()
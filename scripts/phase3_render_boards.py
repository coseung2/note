#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

from pipeline_utils import (
    lesson_indexed_name,
    load_json,
    resolve_task_dir,
    write_json,
)


def wait_until_ready(page) -> None:
    try:
        page.wait_for_function("document.fonts && document.fonts.status === 'loaded'", timeout=15000)
    except Exception:
        pass
    try:
        page.wait_for_load_state("networkidle", timeout=15000)
    except Exception:
        pass


def lesson_selected(lesson_no: int, only: int | None, start: int | None, end: int | None) -> bool:
    if only is not None:
        return lesson_no == only
    if start is not None and lesson_no < start:
        return False
    if end is not None and lesson_no > end:
        return False
    return True


def render_outputs(
    task_dir: Path,
    only: int | None = None,
    start: int | None = None,
    end: int | None = None,
) -> None:
    req = load_json(task_dir / "phase0" / "request.json")
    phase2 = task_dir / "phase2"
    phase3 = task_dir / "phase3"
    phase3.mkdir(parents=True, exist_ok=True)

    manifest: dict[str, object] = {
        "task_id": req["task_id"],
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "items": [],
    }

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": 1240, "height": 1754}, device_scale_factor=2)
        for lesson in req.get("lessons", []):
            lesson_no = int(lesson["number"])
            if not lesson_selected(lesson_no, only, start, end):
                continue

            src_html = phase2 / f"preview_{lesson_no:02d}.html"
            if not src_html.exists():
                raise FileNotFoundError(f"missing preview html: {src_html}")

            dst_html = phase3 / lesson_indexed_name(lesson_no, "html")
            shutil.copy2(src_html, dst_html)

            url = dst_html.resolve().as_uri()
            page.goto(url, wait_until="load")
            wait_until_ready(page)

            png_out = phase3 / lesson_indexed_name(lesson_no, "png")
            pdf_out = phase3 / lesson_indexed_name(lesson_no, "pdf")

            page.screenshot(path=str(png_out), full_page=True)
            page_pngs: list[str] = []
            page_count = page.locator(".page").count()
            for page_idx in range(page_count):
                page_png = phase3 / f"lesson_{lesson_no:02d}_p{page_idx + 1:02d}.png"
                page.locator(".page").nth(page_idx).screenshot(path=str(page_png))
                page_pngs.append(str(page_png.relative_to(task_dir)))
            page.pdf(
                path=str(pdf_out),
                format="A4",
                margin={"top": "0mm", "bottom": "0mm", "left": "0mm", "right": "0mm"},
                print_background=True,
                prefer_css_page_size=True,
            )

            manifest["items"].append(
                {
                    "lesson_number": lesson_no,
                    "lesson_title": lesson["title"],
                    "source_html": str(src_html.relative_to(task_dir)),
                    "html": str(dst_html.relative_to(task_dir)),
                    "png": str(png_out.relative_to(task_dir)),
                    "page_pngs": page_pngs,
                    "pdf": str(pdf_out.relative_to(task_dir)),
                }
            )
        browser.close()

    write_json(phase3 / "board_manifest.json", manifest)


def main() -> None:
    parser = argparse.ArgumentParser(description="Render phase2 preview HTML into phase3 PNG/PDF boards.")
    parser.add_argument("task", help="task_id or task directory")
    parser.add_argument("--only", type=int, help="render only one lesson number")
    parser.add_argument("--start", type=int, help="render from this lesson number")
    parser.add_argument("--end", type=int, help="render through this lesson number")
    args = parser.parse_args()
    render_outputs(resolve_task_dir(args.task), only=args.only, start=args.start, end=args.end)


if __name__ == "__main__":
    main()

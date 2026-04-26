#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from pipeline_utils import (
    clean_lesson_title,
    lesson_indexed_name,
    lesson_output_name,
    load_json,
    resolve_task_dir,
    resolve_style_anchor,
    sanitize_filename,
    write_json,
)


def build_prompt(
    req: dict,
    lesson: dict,
    note: dict | None = None,
    page_index: int | None = None,
    page_count: int | None = None,
    page_blocks: list[dict] | None = None,
) -> str:
    unit_title = req.get("unit_title", "")
    lesson_title = note.get("lesson_title") if note else None
    if not isinstance(lesson_title, str) or not lesson_title.strip():
        lesson_title = clean_lesson_title(str(lesson.get("title", "")))
    lesson_title = clean_prompt_text(str(lesson_title))
    extra = ""
    if note:
        highlights = []
        fill_sentences = []
        blocks_for_prompt = page_blocks if page_blocks is not None else note.get("blocks", [])
        for block in blocks_for_prompt:
            keyword = block.get("keyword")
            section_title = block.get("section_title")
            if isinstance(keyword, str) and keyword.strip():
                highlights.append(clean_prompt_text(keyword))
            elif isinstance(section_title, str) and section_title.strip():
                highlights.append(clean_prompt_text(section_title))
            if block.get("type") == "fill_blank" and isinstance(block.get("sentence"), str):
                fill_sentences.append(clean_prompt_text(block["sentence"]))
        if highlights:
            extra = " 핵심 항목은 " + ", ".join(highlights[:6]) + "를 중심으로 유지한다."
        if fill_sentences:
            extra += " 한 문장 정리 문장은 다음 문자열을 그대로 유지한다: " + " / ".join(fill_sentences) + "."
        elif page_index is not None and page_count and page_count > 1:
            extra += " 이 쪽에는 한 문장 정리를 넣지 않는다."
    page_note = ""
    if page_index is not None and page_count and page_count > 1:
        page_note = f"\n이 보드는 같은 차시의 {page_index}/{page_count}쪽이다. 한 장 안에 다른 쪽 내용을 합치지 말고, 이 입력 이미지에 보이는 내용만 공책정리로 만든다."
    return (
        "1번 이미지를 최우선 스타일 레퍼런스로 사용한다.\n"
        "2번 이미지는 내용과 레이아웃 레퍼런스다.\n"
        "1번의 공책정리 분위기, 손그림 느낌, 색감, 여백 구성은 유지한다.\n"
        "2번 이미지의 한국어 제목, 핵심 개념, 섹션 흐름을 보존한 채 학생용 공책정리 결과물로 다시 만든다.\n"
        "2번 이미지의 프레임 상자 안 설명을 읽고, 그 자리에 알맞은 삽화를 채운다.\n"
        "텍스트는 한국어로 정확하게, 읽기 쉽게 유지한다. 글자 누락, 오탈자, 깨짐을 만들지 않는다.\n"
        "2번 이미지의 한 문장 정리 빈칸은 그대로 빈칸으로 둔다. 정답, 초성 힌트, 답안 안내를 추가하지 않는다.\n"
        "내용과 무관한 다이어리식 꾸밈은 넣지 않는다. 꽃, 별, 이파리, 반짝이, 랜덤 스티커 같은 장식 요소는 금지한다.\n"
        "메인 타이틀 앞에는 기호를 붙이지 않는다. 타이틀은 이전 결과처럼 얇은 박스, 형광펜, 라벨 테두리로 감싸 강조한다.\n"
        "기호와 작은 표시는 본문 안의 핵심 키워드, 섹션 소제목, 중요 문장을 부각할 때만 제한적으로 사용한다.\n"
        f"과목/단원: {sanitize_filename(str(unit_title))}\n"
        f"차시명: {sanitize_filename(str(lesson_title))}.{extra}"
        f"{page_note}"
    )


def clean_prompt_text(value: str) -> str:
    value = re.sub(r"\[주제\s*\d+\s*(?:요약)?\]\s*", "", value)
    value = re.sub(r"주제\s*\d+\s*마무리", "마무리", value)
    return sanitize_filename(value).strip()


def lesson_selected(lesson_no: int, only: int | None, start: int | None, end: int | None) -> bool:
    if only is not None:
        return lesson_no == only
    if start is not None and lesson_no < start:
        return False
    if end is not None and lesson_no > end:
        return False
    return True


def split_note_blocks(note: dict | None) -> list[list[dict]] | None:
    if not note:
        return None
    blocks = note.get("blocks", [])
    if not isinstance(blocks, list):
        return None
    splits = note.get("splits")
    if splits is None:
        split_at = note.get("split_at")
        splits = [split_at] if split_at is not None else []
    splits = sorted(set(s for s in splits if isinstance(s, int) and 0 < s < len(blocks)))
    pages: list[list[dict]] = []
    prev = 0
    for split in splits:
        pages.append(blocks[prev:split])
        prev = split
    pages.append(blocks[prev:])
    return pages


def run_stylize(
    task_dir: Path,
    style_refs: list[str],
    server: str,
    only: int | None = None,
    start: int | None = None,
    end: int | None = None,
    jobs: int = 1,
    page_index_filter: int | None = None,
) -> None:
    req = load_json(task_dir / "phase0" / "request.json")
    phase3 = task_dir / "phase3"
    phase4 = task_dir / "phase4"
    prompts_dir = phase4 / "prompts"
    phase4.mkdir(parents=True, exist_ok=True)
    prompts_dir.mkdir(parents=True, exist_ok=True)

    style_anchor = resolve_style_anchor(req, style_refs)
    if not style_anchor.exists():
        raise FileNotFoundError(f"style reference not found: {style_anchor}")

    requests_log: dict[str, object] = {
        "task_id": req["task_id"],
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "server": server,
        "style_anchor": str(style_anchor),
        "defaults": {
            "quality": "medium",
            "size": "1536x2048",
            "format": "png",
            "moderation": "low",
            "count": 1,
        },
        "items": [],
    }
    run_log: list[str] = []

    generation_jobs: list[dict[str, object]] = []
    for lesson in req.get("lessons", []):
        lesson_no = int(lesson["number"])
        if not lesson_selected(lesson_no, only, start, end):
            continue

        board_png = phase3 / lesson_indexed_name(lesson_no, "png")
        if not board_png.exists():
            raise FileNotFoundError(f"missing phase3 board png: {board_png}")
        split_boards = sorted(phase3.glob(f"lesson_{lesson_no:02d}_p*.png"))
        board_inputs = split_boards if len(split_boards) > 1 else [board_png]

        note_path = task_dir / "phase2" / f"notebook_{lesson_no:02d}.json"
        note = load_json(note_path) if note_path.exists() else None
        note_pages = split_note_blocks(note)
        page_count = len(board_inputs)
        for page_index, board_input in enumerate(board_inputs, start=1):
            split_page = page_count > 1
            if split_page and page_index_filter is not None and page_index != page_index_filter:
                continue
            page_blocks = None
            if split_page and note_pages and page_index <= len(note_pages):
                page_blocks = note_pages[page_index - 1]
            prompt = build_prompt(req, lesson, note, page_index if split_page else None, page_count, page_blocks)
            prompt_suffix = f"_p{page_index:02d}" if split_page else ""
            prompt_path = prompts_dir / f"{lesson_no:02d}{prompt_suffix}.txt"
            prompt_path.write_text(prompt + "\n", encoding="utf-8")

            base_out = lesson_output_name(req, lesson, "png")
            if split_page:
                base = Path(base_out)
                out_name = f"{base.stem}_{page_index}쪽{base.suffix}"
            else:
                out_name = base_out
            out_path = phase4 / out_name
            cmd = [
                "ima2",
                "gen",
                "--server",
                server,
                "--timeout",
                "420",
                "-q",
                "medium",
                "-s",
                "1536x2048",
                "-o",
                str(out_path),
                "--ref",
                str(style_anchor),
                "--ref",
                str(board_input),
            ]
            cmd.append(prompt)

            generation_jobs.append(
                {
                    "lesson_number": lesson_no,
                    "lesson_title": lesson["title"],
                    "page_index": page_index if split_page else None,
                    "page_count": page_count if split_page else None,
                    "prompt_file": str(prompt_path.relative_to(task_dir)),
                    "board_png": str(board_input.relative_to(task_dir)),
                    "output_png": str(out_path.relative_to(task_dir)),
                    "style_anchor": str(style_anchor),
                    "cmd": cmd,
                    "out_name": out_name,
                    "log_page": f" p{page_index}/{page_count}" if split_page else "",
                }
            )

    def run_job(job: dict[str, object]) -> dict[str, object]:
        started = time.time()
        proc = subprocess.run(job["cmd"], capture_output=True, text=True)
        elapsed = round(time.time() - started, 1)
        result = dict(job)
        result["returncode"] = proc.returncode
        result["elapsed_sec"] = elapsed
        result["stdout"] = proc.stdout
        result["stderr"] = proc.stderr
        return result

    max_workers = max(1, int(jobs or 1))
    results: list[dict[str, object]] = []
    if max_workers == 1:
        for job in generation_jobs:
            results.append(run_job(job))
    else:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_map = {executor.submit(run_job, job): job for job in generation_jobs}
            for future in as_completed(future_map):
                results.append(future.result())

    results.sort(key=lambda row: (int(row["lesson_number"]), int(row["page_index"] or 0)))
    for result in results:
        requests_log["items"].append(
            {
                "lesson_number": result["lesson_number"],
                "lesson_title": result["lesson_title"],
                "page_index": result["page_index"],
                "page_count": result["page_count"],
                "prompt_file": result["prompt_file"],
                "board_png": result["board_png"],
                "output_png": result["output_png"],
                "style_anchor": result["style_anchor"],
                "cmd": result["cmd"],
                "returncode": result["returncode"],
                "elapsed_sec": result["elapsed_sec"],
            }
        )
        run_log.append(
            f"[L{int(result['lesson_number']):02d}{result['log_page']}] "
            f"rc={result['returncode']} elapsed={result['elapsed_sec']}s out={result['out_name']}"
        )
        if str(result["stdout"]).strip():
            run_log.append(str(result["stdout"]).strip())
        if str(result["stderr"]).strip():
            run_log.append(str(result["stderr"]).strip())
        if result["returncode"] != 0:
            (phase4 / "run.log").write_text("\n".join(run_log) + "\n", encoding="utf-8")
            write_json(phase4 / "requests.json", requests_log)
            msg = str(result["stderr"]).strip() or str(result["stdout"]).strip()
            raise RuntimeError(f"ima2 failed for lesson {result['lesson_number']}: {msg}")

    write_json(phase4 / "requests.json", requests_log)
    (phase4 / "run.log").write_text("\n".join(run_log) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate final lesson PNGs via ima2.")
    parser.add_argument("task", help="task_id or task directory")
    parser.add_argument("--style-ref", action="append", default=[], help="style reference image path; repeatable")
    parser.add_argument("--server", default="http://localhost:3333", help="ima2 server URL")
    parser.add_argument("--only", type=int, help="run only one lesson number")
    parser.add_argument("--start", type=int, help="run from this lesson number")
    parser.add_argument("--end", type=int, help="run through this lesson number")
    parser.add_argument("--jobs", type=int, default=1, help="number of ima2 generations to run in parallel")
    parser.add_argument("--page-index", type=int, help="for split lessons, run only this page index")
    args = parser.parse_args()
    run_stylize(
        resolve_task_dir(args.task),
        args.style_ref,
        args.server,
        only=args.only,
        start=args.start,
        end=args.end,
        jobs=args.jobs,
        page_index_filter=args.page_index,
    )


if __name__ == "__main__":
    main()

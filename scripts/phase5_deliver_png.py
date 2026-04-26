#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import time
from pathlib import Path

from pipeline_utils import (
    copy_with_version,
    hash_file,
    lesson_output_name,
    load_json,
    resolve_delivery_dir,
    resolve_task_dir,
)


def lesson_selected(lesson_no: int, only: int | None, start: int | None, end: int | None) -> bool:
    if only is not None:
        return lesson_no == only
    if start is not None and lesson_no < start:
        return False
    if end is not None and lesson_no > end:
        return False
    return True


def deliver(
    task_dir: Path,
    output_dir_override: str | None = None,
    skip_external: bool = False,
    only: int | None = None,
    start: int | None = None,
    end: int | None = None,
) -> None:
    req = load_json(task_dir / "phase0" / "request.json")
    phase4 = task_dir / "phase4"
    phase5 = task_dir / "phase5"
    phase5.mkdir(parents=True, exist_ok=True)
    local_output_dir = phase5 / "output"
    local_output_dir.mkdir(parents=True, exist_ok=True)
    external_dir = None if skip_external else resolve_delivery_dir(req, override=output_dir_override)

    manifest_lines = []
    delivered_rows = []
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S%z")

    for lesson in req.get("lessons", []):
        lesson_no = int(lesson["number"])
        if not lesson_selected(lesson_no, only, start, end):
            continue
        file_name = lesson_output_name(req, lesson, "png")
        src = phase4 / file_name
        if not src.exists():
            raise FileNotFoundError(f"missing phase4 output: {src}")

        local_dest = local_output_dir / file_name
        shutil.copy2(src, local_dest)
        local_sha = hash_file(local_dest)
        manifest_lines.append(f"{local_sha}  {local_dest}")

        external_dest = None
        if external_dir is not None:
            external_dest = copy_with_version(src, external_dir, file_name)
            external_sha = hash_file(external_dest)
            manifest_lines.append(f"{external_sha}  {external_dest}")

        delivered_rows.append(
            {
                "lesson_number": lesson_no,
                "lesson_title": lesson["title"],
                "local_output": str(local_dest),
                "external_output": str(external_dest) if external_dest else None,
            }
        )

    (phase5 / "manifest.sha256").write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")

    lines = [
        "---",
        f"task_id: {req['task_id']}",
        f"delivered_at: {timestamp}",
        "format: png",
        "---",
        "",
        "# 배송 완료",
        "",
        f"- 로컬 산출물 폴더: `{local_output_dir}`",
    ]
    if external_dir is not None:
        lines.append(f"- 외부 산출물 폴더: `{external_dir}`")
    lines.extend(["", "## 파일 목록", ""])
    for row in delivered_rows:
        lines.append(f"- {row['lesson_number']:02d}차시 `{row['lesson_title']}`")
        lines.append(f"  로컬: `{row['local_output']}`")
        if row["external_output"]:
            lines.append(f"  외부: `{row['external_output']}`")
    (phase5 / "DELIVERED.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Copy phase4 PNG outputs into final output folders.")
    parser.add_argument("task", help="task_id or task directory")
    parser.add_argument("--output-dir", help="override external output directory")
    parser.add_argument("--skip-external", action="store_true", help="write only task-local phase5/output")
    parser.add_argument("--only", type=int, help="deliver only one lesson number")
    parser.add_argument("--start", type=int, help="deliver from this lesson number")
    parser.add_argument("--end", type=int, help="deliver through this lesson number")
    args = parser.parse_args()
    deliver(
        resolve_task_dir(args.task),
        output_dir_override=args.output_dir,
        skip_external=args.skip_external,
        only=args.only,
        start=args.start,
        end=args.end,
    )


if __name__ == "__main__":
    main()

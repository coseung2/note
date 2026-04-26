#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import shutil
from hashlib import sha256
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TASKS_DIR = ROOT / "tasks"
DEFAULT_STYLE_REFERENCE_DIR = Path(
    "/mnt/c/Users/심보승/OneDrive - 남선초등학교/학습자료/사회/공책정리/2026 아이스크림 4학년"
)
DEFAULT_DELIVERY_DIR = Path(
    "/mnt/c/Users/심보승/OneDrive - 남선초등학교/학습자료/사회/공책정리"
)


def resolve_task_dir(task: str) -> Path:
    candidate = Path(task)
    if candidate.exists():
        return candidate.resolve()
    candidate = TASKS_DIR / task
    if candidate.exists():
        return candidate.resolve()
    raise FileNotFoundError(f"task not found: {task}")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sanitize_filename(value: str) -> str:
    value = re.sub(r'[<>:"/\\\\|?*]+', "", value).strip()
    value = re.sub(r"\s+", " ", value)
    return value


def clean_lesson_title(value: str) -> str:
    value = re.sub(r"^\s*\[주제\s*\d+\]\s*", "", value).strip()
    return sanitize_filename(value)


def slugify_korean(value: str) -> str:
    value = sanitize_filename(value)
    value = value.replace(" ", "_")
    return value


def subject_grade(req: dict[str, Any]) -> str:
    return f"{req['subject']}{req['grade']}-{req['semester']}"


def lesson_output_name(req: dict[str, Any], lesson: dict[str, Any], ext: str = "png") -> str:
    title = clean_lesson_title(lesson["title"])
    return (
        f"{subject_grade(req)}_{req['unit_number']}단원_"
        f"{int(lesson['number']):02d}차시_{title}.{ext}"
    )


def lesson_indexed_name(lesson_number: int, ext: str) -> str:
    return f"lesson_{lesson_number:02d}.{ext}"


def is_image_path(path: Path) -> bool:
    return path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}


def list_image_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path] if is_image_path(path) else []
    if not path.is_dir():
        return []
    return sorted([p for p in path.iterdir() if p.is_file() and is_image_path(p)])


def resolve_style_anchor(req: dict[str, Any], explicit_refs: list[str] | None = None) -> Path:
    candidates: list[Path] = []

    for raw in explicit_refs or []:
        path = Path(raw).expanduser().resolve()
        candidates.extend(list_image_files(path))
        if candidates:
            return candidates[0]

    for raw in req.get("style_reference_paths", []) or []:
        path = Path(raw).expanduser()
        if not path.is_absolute():
            path = (ROOT / path).resolve()
        else:
            path = path.resolve()
        candidates.extend(list_image_files(path))
        if candidates:
            return candidates[0]

    raw_dir = req.get("style_reference_dir")
    if isinstance(raw_dir, str) and raw_dir.strip():
        path = windows_path_to_wsl(raw_dir).resolve()
        candidates.extend(list_image_files(path))
        if candidates:
            return candidates[0]

    candidates.extend(list_image_files(DEFAULT_STYLE_REFERENCE_DIR))
    if candidates:
        return candidates[0]
    raise FileNotFoundError(
        f"no style reference image found; checked request and default dir: {DEFAULT_STYLE_REFERENCE_DIR}"
    )


def hash_file(path: Path) -> str:
    h = sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def windows_path_to_wsl(value: str) -> Path:
    m = re.match(r"^([A-Za-z]):\\(.*)$", value)
    if not m:
        return Path(value)
    drive = m.group(1).lower()
    parts = [p for p in m.group(2).split("\\") if p]
    return Path("/mnt") / drive / Path(*parts)


def infer_windows_user(req: dict[str, Any]) -> str | None:
    for key in ("textbook_pdf_path_windows", "textbook_pdf_path"):
        raw = req.get(key)
        if not isinstance(raw, str):
            continue
        m = re.match(r"^[A-Za-z]:\\Users\\([^\\]+)\\", raw)
        if m:
            return m.group(1)
    return None


def resolve_delivery_dir(req: dict[str, Any], override: str | None = None) -> Path:
    if override:
        return Path(override).resolve()

    raw = req.get("delivery_path")
    if not isinstance(raw, str) or not raw.strip():
        return DEFAULT_DELIVERY_DIR.resolve()
    if raw.startswith("/"):
        return Path(raw).resolve()
    if re.match(r"^[A-Za-z]:\\", raw):
        return windows_path_to_wsl(raw).resolve()

    parts = [p for p in raw.split("\\") if p]
    if not parts:
        return DEFAULT_DELIVERY_DIR.resolve()

    env_root = os.environ.get("ONEDRIVE_SCHOOL")
    if env_root:
        env_path = Path(env_root)
        if parts[0].startswith("OneDrive - "):
            if env_path.name == parts[0]:
                return (env_path / Path(*parts[1:])).resolve()
        return (env_path / Path(*parts)).resolve()

    user = infer_windows_user(req)
    if not user:
        return DEFAULT_DELIVERY_DIR.resolve()
    return (Path("/mnt/c/Users") / user / Path(*parts)).resolve()


def copy_with_version(src: Path, dest_dir: Path, preferred_name: str) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    stem = Path(preferred_name).stem
    suffix = Path(preferred_name).suffix
    candidate = dest_dir / preferred_name
    idx = 2
    while candidate.exists():
        candidate = dest_dir / f"{stem}_v{idx}{suffix}"
        idx += 1
    shutil.copy2(src, candidate)
    return candidate

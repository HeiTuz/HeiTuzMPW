#!/usr/bin/env python3
"""Compile a portable, runtime-neutral image-production handoff."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import urlparse

REQUEST_VERSION = "image-production-request/v2"
HANDOFF_VERSION = "image-production-handoff/v2"
MAX_PROMPT_CHARS = 2000
MAX_NEGATIVE_CHARS = 1000
JOB_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
ASPECT_RATIO = re.compile(r"^[1-9][0-9]*:[1-9][0-9]*$")
IMAGE_SIZE = re.compile(r"^[1-9][0-9]{2,4}x[1-9][0-9]{2,4}$")
OUTPUT_NAME = re.compile(r"^[^/\\]+\.(?:png|jpe?g|webp)$")
PROMPT_FIELDS = ("subject", "action", "scene", "composition", "lighting", "style", "text")
ALLOWED_FIELDS = {
    "schema_version", "job_id", "operation", *PROMPT_FIELDS, "negative_prompt",
    "input_images", "aspect_ratio", "image_size", "output", "metadata",
}


class CompileError(RuntimeError):
    """The request cannot produce a valid portable handoff."""


def _text(value: Any, field: str, *, required: bool = False, limit: int | None = None) -> str | None:
    if value is None and not required:
        return None
    if not isinstance(value, str) or not value.strip():
        raise CompileError(f"{field} must be a non-empty string")
    normalized = " ".join(value.split())
    if limit is not None and len(normalized) > limit:
        raise CompileError(f"{field} exceeds {limit} characters")
    return normalized


def _portable_reference(value: Any, field: str) -> str:
    reference = _text(value, field, required=True, limit=1024)
    assert reference is not None
    parsed = urlparse(reference)
    if parsed.scheme:
        if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
            raise CompileError(f"{field} must be a relative path or public HTTPS URL")
        return reference
    if "\\" in reference or reference.startswith(("/", "~")):
        raise CompileError(f"{field} must be a portable relative path")
    path = PurePosixPath(reference)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise CompileError(f"{field} must not contain traversal or empty segments")
    return reference


def _compile_inputs(raw: Any) -> list[dict[str, str]]:
    if raw is None:
        return []
    if not isinstance(raw, list) or len(raw) > 20:
        raise CompileError("input_images must be an array with at most 20 entries")
    result: list[dict[str, str]] = []
    seen: set[str] = set()
    for index, item in enumerate(raw):
        if not isinstance(item, dict) or set(item) != {"path", "role"}:
            raise CompileError(f"input_images[{index}] must contain only path and role")
        path = _portable_reference(item["path"], f"input_images[{index}].path")
        role = _text(item["role"], f"input_images[{index}].role", required=True, limit=200)
        if path in seen:
            raise CompileError(f"duplicate input image: {path}")
        seen.add(path)
        result.append({"path": path, "role": role or ""})
    return result


def _compile_output(raw: Any) -> dict[str, str]:
    if not isinstance(raw, dict) or set(raw) != {"filename"}:
        raise CompileError("output must contain only filename")
    filename = _text(raw["filename"], "output.filename", required=True, limit=255)
    if filename is None or not OUTPUT_NAME.fullmatch(filename):
        raise CompileError("output.filename must be one PNG, JPEG, or WebP basename")
    return {"filename": filename}


def compile_request(request: Any) -> dict[str, Any]:
    if not isinstance(request, dict) or request.get("schema_version") != REQUEST_VERSION:
        raise CompileError(f"schema_version must be {REQUEST_VERSION}")
    unknown = set(request) - ALLOWED_FIELDS
    if unknown:
        raise CompileError(f"unknown request fields: {', '.join(sorted(unknown))}")
    job_id = _text(request.get("job_id"), "job_id", required=True)
    if job_id is None or not JOB_ID.fullmatch(job_id):
        raise CompileError("job_id must use only letters, digits, dot, underscore, and hyphen")
    operation = request.get("operation")
    if operation not in {"generate", "edit"}:
        raise CompileError("operation must be generate or edit")
    inputs = _compile_inputs(request.get("input_images"))
    if operation == "edit" and not inputs:
        raise CompileError("edit operation requires at least one input image")

    clauses: list[str] = []
    for field in PROMPT_FIELDS:
        value = _text(request.get(field), field, required=field == "subject")
        if value:
            clauses.append(f"{field.replace('_', ' ').title()}: {value}.")
    prompt = " ".join(clauses)
    if len(prompt) > MAX_PROMPT_CHARS:
        raise CompileError(f"prompt exceeds {MAX_PROMPT_CHARS} characters")

    handoff: dict[str, Any] = {
        "schema_version": HANDOFF_VERSION,
        "job_id": job_id,
        "operation": operation,
        "prompt": prompt,
        "output": _compile_output(request.get("output")),
    }
    negative = _text(request.get("negative_prompt"), "negative_prompt", limit=MAX_NEGATIVE_CHARS)
    if negative:
        handoff["negative_prompt"] = negative
    if inputs:
        handoff["input_images"] = inputs
    for field, pattern in (("aspect_ratio", ASPECT_RATIO), ("image_size", IMAGE_SIZE)):
        value = _text(request.get(field), field)
        if value:
            if not pattern.fullmatch(value):
                raise CompileError(f"{field} has an invalid format")
            handoff[field] = value
    metadata = request.get("metadata")
    if metadata is not None:
        if not isinstance(metadata, dict) or any(
            not isinstance(key, str) or not key or _text(value, f"metadata.{key}", required=True, limit=500) is None
            for key, value in metadata.items()
        ):
            raise CompileError("metadata must map non-empty keys to strings")
        handoff["metadata"] = {key: " ".join(value.split()) for key, value in metadata.items()}
    return handoff


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compile a portable image-production handoff")
    parser.add_argument("request", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        handoff = compile_request(json.loads(args.request.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError, CompileError) as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)}, ensure_ascii=False))
        return 2
    text = json.dumps(handoff, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

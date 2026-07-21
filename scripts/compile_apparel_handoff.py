#!/usr/bin/env python3
"""Compile a portable apparel request into a fail-closed generation handoff."""
from __future__ import annotations

import argparse
import json
import unicodedata
from pathlib import Path
from typing import Any

MAX_PROMPT_CHARS = 2000
REQUEST_VERSION = "apparel-compile-request/v1"
HANDOFF_VERSION = 1


class CompileError(RuntimeError):
    """The request cannot produce a complete, verifiable handoff."""


def normalize_color_identity(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return " ".join(unicodedata.normalize("NFKC", value).split()).casefold()


def _basename(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value or Path(value).name != value or value in {".", ".."}:
        raise CompileError(f"{field} must be one non-empty basename")
    return value


def _nonempty(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CompileError(f"{field} must be a non-empty string")
    return " ".join(value.split())


def _validate_sources(request: dict[str, Any]) -> tuple[Path, list[str]]:
    source_folder = Path(_nonempty(request.get("source_folder"), "source_folder")).expanduser().resolve()
    if not source_folder.is_dir():
        raise CompileError(f"source_folder is not a directory: {source_folder}")
    raw = request.get("sources")
    if not isinstance(raw, list) or not raw:
        raise CompileError("sources must be a non-empty complete inventory")
    sources: list[str] = []
    seen: set[str] = set()
    for index, item in enumerate(raw):
        name = _basename(item, f"sources[{index}]")
        if name in seen:
            raise CompileError(f"duplicate inventory source: {name}")
        if not (source_folder / name).is_file():
            raise CompileError(f"missing inventory source: {name}")
        seen.add(name)
        sources.append(name)
    return source_folder, sources


def _validate_role_map(raw: Any, sources: list[str]) -> tuple[list[dict[str, Any]], list[str]]:
    if not isinstance(raw, list) or not raw:
        raise CompileError("vision_role_map must be a non-empty list")
    inventory = set(sources)
    normalized_map: list[dict[str, Any]] = []
    unique_front_colors: list[str] = []
    seen_colors: set[str] = set()
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            raise CompileError(f"vision_role_map[{index}] must be an object")
        row = dict(item)
        filename = _basename(row.get("file"), f"vision_role_map[{index}].file")
        if filename not in inventory:
            raise CompileError(f"role-map source missing from inventory: {filename}")
        role = _nonempty(row.get("role"), f"vision_role_map[{index}].role")
        row["role"] = role
        if "color_identity" in row:
            normalized = normalize_color_identity(row["color_identity"])
            if not normalized:
                raise CompileError(f"vision_role_map[{index}].color_identity must be non-empty")
            row["color_identity"] = normalized
        if role == "color_front":
            if "color_identity" not in row:
                raise CompileError(f"color_front record {filename} requires explicit color_identity")
            normalized = row["color_identity"]
            if normalized not in seen_colors:
                seen_colors.add(normalized)
                unique_front_colors.append(normalized)
        normalized_map.append(row)
    if not unique_front_colors:
        raise CompileError("blocked: vision_role_map contains zero unique color_front identities")
    return normalized_map, unique_front_colors


def _render_prompt(output: dict[str, Any], valid_colors: set[str]) -> tuple[str, str, str]:
    output_id = _basename(output.get("id"), "requested_outputs[].id")
    filename = _basename(output.get("filename"), "requested_outputs[].filename")
    if not filename.lower().endswith(".png"):
        raise CompileError(f"output {output_id} filename must end in .png")
    view = _nonempty(output.get("view"), f"output {output_id} view")
    color = normalize_color_identity(output.get("color_identity"))
    if not color:
        raise CompileError(f"output {output_id} requires explicit color_identity")
    if color not in valid_colors:
        raise CompileError(f"output {output_id} color_identity has no color_front authority: {color}")
    product = _nonempty(output.get("product_description"), f"output {output_id} product_description")
    details = output.get("visible_details", [])
    if not isinstance(details, list) or any(not isinstance(item, str) or not item.strip() for item in details):
        raise CompileError(f"output {output_id} visible_details must contain non-empty strings")
    detail_text = "; ".join(" ".join(item.split()) for item in details)
    detail_clause = f" Preserve these source-visible details exactly: {detail_text}." if detail_text else ""
    prompt = (
        f"IMAGE. Create a {view} apparel product cut for color {color}. Product: {product}. "
        "Use only the complete attached original source inventory and validated Vision role map as evidence. "
        "Preserve visible construction, silhouette, proportions, material behavior, trim, print, and exact color."
        f"{detail_clause} Remove mannequin, hanger, stand, rod, cord, clip, hand, prop, and all remnants. "
        "Use uniform #FFFFFF with no cast/contact shadow, halo, floor line, or gradient. "
        "Reconstruct only source-supported hidden areas; invent no seam, lining, label, panel, button, print, "
        "embroidery, pocket, fastener, or hem. Keep the series canvas, occupancy, centerline, scale, and lighting coherent."
    )
    if len(prompt) > MAX_PROMPT_CHARS:
        raise CompileError(f"self_contained_prompt_overflow:{output_id}:{len(prompt)}>{MAX_PROMPT_CHARS}")
    return output_id, filename, prompt


def compile_request(request: Any) -> dict[str, Any]:
    if not isinstance(request, dict) or request.get("schema_version") != REQUEST_VERSION:
        raise CompileError(f"schema_version must be {REQUEST_VERSION}")
    folder_id = _basename(request.get("folder_id"), "folder_id")
    source_folder, sources = _validate_sources(request)
    role_map, colors = _validate_role_map(request.get("vision_role_map"), sources)
    requested = request.get("requested_outputs")
    if not isinstance(requested, list) or not requested:
        raise CompileError("requested_outputs must be a non-empty complete inventory")
    outputs: list[dict[str, str]] = []
    ids: set[str] = set()
    filenames: set[str] = set()
    for item in requested:
        if not isinstance(item, dict):
            raise CompileError("each requested output must be an object")
        output_id, filename, prompt = _render_prompt(item, set(colors))
        if output_id in ids or filename in filenames:
            raise CompileError(f"duplicate output id or filename: {output_id}/{filename}")
        ids.add(output_id)
        filenames.add(filename)
        outputs.append({"id": output_id, "filename": filename, "prompt": prompt})
    color_list = ", ".join(colors)
    return {
        "schema_version": HANDOFF_VERSION,
        "folder_id": folder_id,
        "source_folder": str(source_folder),
        "sources": sources,
        "vision_role_map": role_map,
        "normalized_color_identity": colors,
        "unique_color_count": len(colors),
        "mpw_folder_master": (
            "Compile one coherent apparel family from the complete source inventory and validated Vision role map. "
            f"Authoritative front colors: {color_list}. Preserve source-supported construction, material, trim, print, "
            "color, scale, framing, and view relationships. Reconstruct only source-supported hidden areas."
        ),
        "qc_contract": (
            "Accept only source-faithful apparel with required support removal, uniform #FFFFFF, no cast/contact shadow, "
            "no invented construction, exact visible copy, and at least 0.80 family similarity."
        ),
        "outputs": outputs,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compile a portable apparel generation handoff")
    parser.add_argument("request", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        request = json.loads(args.request.read_text(encoding="utf-8"))
        handoff = compile_request(request)
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

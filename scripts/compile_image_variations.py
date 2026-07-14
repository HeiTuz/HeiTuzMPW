#!/usr/bin/env python3
"""Compile one image idea into deterministic, self-contained production variations."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys
from typing import Any

MAX_COUNT = 1000
MAX_PROMPT_CHARS = 2000

AXES: dict[str, tuple[str, ...]] = {
    "composition": (
        "off-center editorial framing with deliberate negative space",
        "tight graphic crop with a strong foreground anchor",
        "symmetrical frontal composition with one controlled disruption",
        "layered depth using foreground, subject plane, and distant field",
        "diagonal movement crossing an otherwise quiet frame",
        "wide environmental composition with a small visual protagonist",
        "compressed collage-like framing without literal borders",
        "top-weighted composition with open breathing room below",
    ),
    "camera": (
        "eye-level 50mm natural perspective",
        "wide 28mm perspective with restrained edge distortion",
        "85mm compressed portrait perspective",
        "slightly elevated observational viewpoint",
        "low viewpoint that gives the subject graphic weight",
        "close macro-detail perspective with tactile scale cues",
        "orthographic-feeling straight-on view",
        "handheld documentary viewpoint with precise subject readability",
    ),
    "lighting": (
        "soft overcast daylight with long tonal transitions",
        "hard late-afternoon side light and crisp geometric shadows",
        "cool fluorescent ambient light with one warm practical accent",
        "diffused studio skylight with subtle floor bounce",
        "direct on-camera flash balanced by dark ambient exposure",
        "low-key window light with dense but readable shadows",
        "high-key paper-white illumination with restrained reflections",
        "mixed neon spill with controlled color separation",
    ),
    "palette": (
        "muted charcoal, dirty cream, and one acidic yellow accent",
        "dusty burgundy, tobacco brown, and faded blue",
        "ink black, cold silver, and desaturated moss green",
        "chalk white, concrete gray, and a restrained cobalt accent",
        "washed denim blue, oxidized orange, and smoke gray",
        "low-saturation plum, beige, and deep forest green",
        "near-monochrome warm gray with one vermilion interruption",
        "cool off-white, faded pink, and dense black",
    ),
    "surface": (
        "visible paper grain, dry ink edges, and tactile print texture",
        "clean photographic realism with subtle halation",
        "matte painted surfaces with imperfect hand-worked edges",
        "rough photocopy texture used sparingly around crisp focal detail",
        "soft textile and brushed-metal material contrast",
        "weathered urban surfaces with controlled patina",
        "translucent plastic, glass, and condensation details",
        "flat graphic color fields interrupted by one highly tactile object",
    ),
    "rhythm": (
        "one dominant mass, two small echoes, and generous quiet space",
        "repeated vertical intervals with one deliberate break",
        "dense lower-third activity fading into an empty upper field",
        "alternating large and small forms that guide a zig-zag reading path",
        "a central still point surrounded by peripheral motion cues",
        "asymmetric clusters connected by a single color thread",
        "slow horizontal rhythm with cropped forms entering from the edges",
        "tight serial repetition that loosens toward one corner",
    ),
}


def _request(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot read request JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("Request must be a JSON object.")
    concept = data.get("concept")
    if not isinstance(concept, str) or not concept.strip():
        raise ValueError("concept must be a non-empty string.")
    style = data.get("style", "")
    if not isinstance(style, str):
        raise ValueError("style must be a string.")
    locks = data.get("locks", {})
    if not isinstance(locks, dict) or any(not isinstance(k, str) or not isinstance(v, (str, int, float, bool)) for k, v in locks.items()):
        raise ValueError("locks must be a flat JSON object with scalar values.")
    prefix = data.get("output_prefix", "images")
    if not isinstance(prefix, str) or not prefix.strip():
        raise ValueError("output_prefix must be a non-empty portable relative path.")
    posix = PurePosixPath(prefix)
    if posix.is_absolute() or ".." in posix.parts or "\\" in prefix or ":" in prefix:
        raise ValueError("output_prefix must be a portable relative path without traversal.")
    return {"concept": concept.strip(), "style": style.strip(), "locks": locks, "output_prefix": posix.as_posix()}


def _seed(data: dict[str, Any], explicit: int | None) -> int:
    if explicit is not None:
        return explicit
    canonical = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return int(hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:12], 16)


def _decode_variation(index: int) -> dict[str, str]:
    result: dict[str, str] = {}
    for name, choices in AXES.items():
        result[name] = choices[index % len(choices)]
        index //= len(choices)
    return result


def _prompt(data: dict[str, Any], axes: dict[str, str]) -> str:
    locks = data["locks"]
    lock_text = ""
    if locks:
        lock_text = " Preserve these invariants exactly: " + "; ".join(f"{key}={value}" for key, value in sorted(locks.items())) + "."
    style_text = f" Style direction: {data['style']}." if data["style"] else ""
    prompt = (
        f"Create one finished, standalone image from this concept: {data['concept']}."
        f"{style_text} Composition: {axes['composition']}. Camera/view: {axes['camera']}."
        f" Lighting: {axes['lighting']}. Palette: {axes['palette']}."
        f" Material and finish: {axes['surface']}. Spatial rhythm: {axes['rhythm']}."
        f"{lock_text} Make the visual choice coherent rather than combining unrelated motifs."
        " Keep the primary subject immediately readable, avoid generic stock-image polish, accidental text, watermarks, logos, and decorative UI frames."
    )
    if len(prompt) > MAX_PROMPT_CHARS:
        raise ValueError(f"Compiled prompt exceeds {MAX_PROMPT_CHARS} characters; shorten concept/style/locks.")
    return prompt


def compile_variations(request: dict[str, Any], count: int, seed: int | None = None) -> list[dict[str, Any]]:
    if isinstance(count, bool) or not 1 <= count <= MAX_COUNT:
        raise ValueError(f"count must be between 1 and {MAX_COUNT}.")
    actual_seed = _seed(request, seed)
    total = 1
    for choices in AXES.values():
        total *= len(choices)
    step = 7919  # odd, therefore coprime with the 8^6 variation space
    offset = actual_seed % total
    width = max(3, len(str(count)))
    records: list[dict[str, Any]] = []
    for position in range(count):
        axes = _decode_variation((offset + position * step) % total)
        number = position + 1
        records.append({
            "id": f"variation-{number:0{width}d}",
            "full_prompt": _prompt(request, axes),
            "output_path": f"{request['output_prefix']}/{number:0{width}d}.png",
            "qc_required": False,
            "metadata": {
                "mpw_compiled": True,
                "ideation_batch": count > 1,
                "variation_index": number,
                "variation_axes": axes,
                "seed": actual_seed,
            },
        })
    return records


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compile deterministic self-contained image prompt variations")
    parser.add_argument("--request", required=True, type=Path)
    parser.add_argument("--count", required=True, type=int)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--seed", type=int)
    args = parser.parse_args(argv)
    try:
        request = _request(args.request)
        rows = compile_variations(request, args.count, args.seed)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8", newline="\n") as handle:
            for row in rows:
                handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    except (OSError, ValueError) as exc:
        print(f"MPW variation compiler: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"count": len(rows), "output": str(args.output), "seed": rows[0]["metadata"]["seed"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Compile a validated GardenRecipe into a versioned PromptBundle."""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
MAX_BLOCK_CHARS = 2000


class CompileError(ValueError):
    """A recipe cannot be compiled without violating the handoff contract."""


def _load_contract_api() -> tuple[Callable[..., list[str]], Callable[[Any], str]]:
    contract_root = Path(os.environ.get("MASTER_PROMPT_CONTRACT_ROOT", ROOT / "contracts"))
    validator_path = contract_root / "validate.py"
    if not validator_path.is_file():
        raise CompileError(
            f"contract_validator_missing:{validator_path}; install or sync the authoritative contracts first"
        )
    spec = importlib.util.spec_from_file_location("master_prompt_contracts", validator_path)
    if spec is None or spec.loader is None:
        raise CompileError(f"contract_validator_unloadable:{validator_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.validate_document, module.canonical_hash


def _strings(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    return [value.strip() for value in values if isinstance(value, str) and value.strip()]


def _axis_values(recipe: dict[str, Any], axis: str) -> list[str]:
    evidence = recipe["observations"].get(axis, {})
    if evidence.get("status") != "observed":
        return []
    return [item["value"].strip() for item in evidence.get("items", []) if item.get("value", "").strip()]


def _qualified_tokens(recipe: dict[str, Any]) -> list[str]:
    result = []
    for token in recipe["qualified_tokens"]:
        scene = f"; scene: {token['scene_fit']}" if token.get("scene_fit") else ""
        result.append(f"{token['term']} ({token['effect']}{scene})")
    return result


def _render_prompt(recipe: dict[str, Any]) -> str:
    intended = recipe["intended_use"]
    locks = recipe["locks"]
    sections: list[str] = [
        f"Goal: {intended['goal'].strip()}",
        f"Mode: {intended['mode']}. Target engine: {intended['engine']}.",
    ]
    labels = {
        "subject": "Observed subject",
        "camera": "Observed camera",
        "lighting": "Observed lighting",
        "palette": "Observed palette",
        "layout": "Observed layout",
    }
    for axis, label in labels.items():
        values = _axis_values(recipe, axis)
        if values:
            sections.append(f"{label}: {'; '.join(values)}.")
    tokens = _qualified_tokens(recipe)
    if tokens:
        sections.append(f"Direction: {'; '.join(tokens)}.")
    inferences = [item["claim"].strip() for item in recipe["inferences"] if item["confidence"] >= 0.5]
    if inferences:
        sections.append(f"Qualified interpretation: {'; '.join(inferences)}.")
    identity = _strings(locks.get("identity"))
    subject = _strings(locks.get("subject"))
    sections.append(
        "Immutable locks: "
        + "; ".join([*(f"identity={value}" for value in identity), *(f"subject={value}" for value in subject)])
        + "."
    )
    sections.append(f"Exclude: {'; '.join(_strings(recipe['exclusions']))}.")
    sections.append(
        f"Reference requirement: attach opaque reference {recipe['source']['reference_id']} for evidence-backed visual guidance; do not infer a local path from the ID."
    )
    sections.append("Return one result that satisfies every immutable lock and exclusion.")
    return "\n".join(sections)


def _variable_axes(recipe: dict[str, Any]) -> list[dict[str, Any]]:
    mode = recipe["intended_use"]["mode"]
    if mode == "DESIGN":
        return [{"name": "non_locked_responsive_detail", "allowed_values": ["adapt spacing without changing locked hierarchy"]}]
    if mode == "IMAGE_COMPOSITE":
        return [{"name": "non_locked_background_detail", "allowed_values": ["minor detail variation consistent with observed evidence"]}]
    return [{"name": "non_locked_render_detail", "allowed_values": ["minor detail variation consistent with observed evidence"]}]


def compile_recipe(recipe: dict[str, Any]) -> dict[str, Any]:
    validate_document, canonical_hash = _load_contract_api()
    errors = validate_document(recipe)
    if errors:
        raise CompileError("garden_recipe_validation_failed:" + " | ".join(errors))
    if recipe.get("schema_version") != "garden-recipe/v1":
        raise CompileError("garden_recipe_validation_failed:unsupported GardenRecipe version")

    text = _render_prompt(recipe)
    count = len(text)
    if count > MAX_BLOCK_CHARS:
        raise CompileError(
            f"self_contained_prompt_overflow:{count}>{MAX_BLOCK_CHARS}; reduce the GardenRecipe without dropping locks or exclusions"
        )
    recipe_hash = canonical_hash(recipe)
    bundle_suffix = recipe_hash.removeprefix("sha256:")[:20]
    locks = recipe["locks"]
    exclusions = list(recipe["exclusions"])
    qc = [
        *(f"Identity lock holds: {value}" for value in locks["identity"]),
        *(f"Subject lock holds: {value}" for value in locks["subject"]),
        *(f"Excluded condition is absent: {value}" for value in exclusions),
        "The attached reference is used only for the stated evidence-backed visual guidance.",
        "Every prompt block is self-contained and at most 2000 Unicode characters.",
    ]
    return {
        "schema_version": "prompt-bundle/v1",
        "bundle_version": 1,
        "bundle_id": f"pb_{bundle_suffix}",
        "source_recipe": {"recipe_id": recipe["recipe_id"], "recipe_hash": recipe_hash},
        "handoff": {
            "protocol": "generation-handoff/v1",
            "mode": recipe["intended_use"]["mode"],
            "engine": recipe["intended_use"]["engine"],
            "prompt_blocks": [{"block_id": f"block_{bundle_suffix}", "text": text, "unicode_char_count": count}],
            "immutable_locks": locks,
            "variable_axes": _variable_axes(recipe),
            "negative_constraints": exclusions,
            "reference_requirements": [{
                "reference_id": recipe["source"]["reference_id"],
                "purpose": "evidence-backed visual guidance and locked-attribute QC",
                "required": True,
            }],
            "qc_acceptance_criteria": qc,
        },
    }


def legacy_bridge_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    """Losslessly adapt v1 prompt blocks to the installed bridge's legacy shape."""
    return {
        "compiled_by": "master-prompt-writer",
        "blocks": [
            {"text": block["text"]}
            for block in bundle["handoff"]["prompt_blocks"]
        ],
        "assumptions": ["Adapted from prompt-bundle/v1; authoritative locks and QC remain in the v1 handoff."],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compile a validated GardenRecipe JSON into PromptBundle JSON")
    parser.add_argument("recipe", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--format", choices=("prompt-bundle", "legacy-bridge"), default="prompt-bundle")
    args = parser.parse_args(argv)
    try:
        recipe = json.loads(args.recipe.read_text(encoding="utf-8"))
        bundle = compile_recipe(recipe)
        output = bundle if args.format == "prompt-bundle" else legacy_bridge_bundle(bundle)
    except (OSError, json.JSONDecodeError, CompileError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1
    rendered = json.dumps(output, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

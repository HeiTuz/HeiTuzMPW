#!/usr/bin/env python3
"""Synchronize byte-identical shared contracts from the canonical source repo."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
CONTRACTS = ROOT / "contracts"
MANIFEST = CONTRACTS / "manifest.json"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_manifest() -> dict[str, Any]:
    value = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if value.get("manifest_version") != 1 or not isinstance(value.get("files"), dict):
        raise ValueError("invalid_contract_manifest")
    return value


def source_errors(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for relative, expected in sorted(manifest["files"].items()):
        path = CONTRACTS / relative
        if not path.is_file():
            errors.append(f"missing_source:{relative}")
        elif sha256_file(path) != expected:
            errors.append(f"source_drift:{relative}")
    return errors


def mirror_errors(destination_root: Path, manifest: dict[str, Any]) -> list[str]:
    destination = destination_root / "contracts"
    errors: list[str] = []
    for relative, expected in sorted(manifest["files"].items()):
        path = destination / relative
        if not path.is_file():
            errors.append(f"missing_mirror:{destination_root}:{relative}")
        elif sha256_file(path) != expected:
            errors.append(f"mirror_drift:{destination_root}:{relative}")
    mirror_manifest = destination / "manifest.json"
    if not mirror_manifest.is_file():
        errors.append(f"missing_mirror:{destination_root}:manifest.json")
    elif sha256_file(mirror_manifest) != sha256_file(MANIFEST):
        errors.append(f"mirror_drift:{destination_root}:manifest.json")
    return errors


def sync(destination_root: Path, manifest: dict[str, Any]) -> None:
    destination = destination_root / "contracts"
    for relative in sorted(manifest["files"]):
        source = CONTRACTS / relative
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    destination.mkdir(parents=True, exist_ok=True)
    shutil.copy2(MANIFEST, destination / "manifest.json")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check or synchronize portable GardenRecipe/PromptBundle contract mirrors")
    parser.add_argument("--dest", action="append", type=Path, default=[], help="Independent skill repo or installed skill root")
    parser.add_argument("--sync", action="store_true", help="Copy canonical contracts before checking")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    try:
        manifest = load_manifest()
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        result = {"ok": False, "errors": [str(exc)]}
    else:
        errors = source_errors(manifest)
        if not errors:
            for destination in args.dest:
                destination = destination.expanduser().resolve()
                if args.sync:
                    sync(destination, manifest)
                errors.extend(mirror_errors(destination, manifest))
        result = {"ok": not errors, "checked_destinations": [str(path) for path in args.dest], "errors": errors}

    if args.json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    elif result["ok"]:
        print(f"OK contract source and {len(args.dest)} mirror(s)")
    else:
        for error in result["errors"]:
            print(f"FAIL {error}", file=sys.stderr)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

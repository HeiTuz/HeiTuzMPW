#!/usr/bin/env python3
"""Regression tests for shared GardenRecipe and PromptBundle contracts."""
from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "contracts"))
sys.path.insert(0, str(ROOT / "scripts"))

from validate import canonical_hash, validate_document  # noqa: E402
from sync_contracts import load_manifest, mirror_errors, source_errors, sync  # noqa: E402

FIXTURES = ROOT / "contracts" / "v1" / "fixtures"


def fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def walk_keys(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from walk_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_keys(child)


class SchemaFixtureTests(unittest.TestCase):
    def test_schema_documents_are_draft_2020_12(self) -> None:
        for name in ("garden-recipe.schema.json", "prompt-bundle.schema.json"):
            schema = json.loads((ROOT / "contracts" / "v1" / name).read_text(encoding="utf-8"))
            self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
            self.assertTrue(schema["$id"].endswith("/v1"))

    def test_image_and_design_recipes_validate(self) -> None:
        for name in ("garden-recipe.image.valid.json", "garden-recipe.design.valid.json"):
            self.assertEqual(validate_document(fixture(name)), [], name)

    def test_existing_design_reference_ids_remain_compatible(self) -> None:
        recipe = fixture("garden-recipe.design.valid.json")
        recipe["source"]["reference_id"] = "design_ref_20260711_120000_ab12cd34"
        self.assertEqual(validate_document(recipe), [])

    def test_private_source_fixture_is_rejected(self) -> None:
        errors = validate_document(fixture("garden-recipe.private.invalid.json"))
        self.assertTrue(any("forbidden_private_key" in error for error in errors), errors)
        self.assertTrue(any("forbidden_path_or_embedded_original" in error for error in errors), errors)

    def test_observation_status_and_inference_references_are_enforced(self) -> None:
        recipe = fixture("garden-recipe.image.valid.json")
        recipe["observations"]["camera"] = {"status": "not_observable", "items": recipe["observations"]["camera"]["items"]}
        recipe["inferences"][0]["based_on"] = ["obs_missing_01"]
        errors = validate_document(recipe)
        self.assertTrue(any("unavailable_axis_must_be_empty" in error for error in errors), errors)
        self.assertTrue(any("unknown_observation_id" in error for error in errors), errors)


class PromptBundleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.recipe = fixture("garden-recipe.image.valid.json")
        self.bundle = fixture("prompt-bundle.valid.json")

    def test_bundle_validates_against_recipe(self) -> None:
        self.assertEqual(self.bundle["source_recipe"]["recipe_hash"], canonical_hash(self.recipe))
        self.assertEqual(validate_document(self.bundle, self.recipe), [])

    def test_unicode_count_uses_code_points_and_enforces_2000(self) -> None:
        block = self.bundle["handoff"]["prompt_blocks"][0]
        self.assertEqual(block["unicode_char_count"], len(block["text"]))
        block["text"] = "한" * 2001
        block["unicode_char_count"] = 2001
        errors = validate_document(self.bundle, self.recipe)
        self.assertTrue(any("unicode_limit:2000" in error for error in errors), errors)

    def test_declared_unicode_count_must_match(self) -> None:
        self.bundle["handoff"]["prompt_blocks"][0]["unicode_char_count"] -= 1
        errors = validate_document(self.bundle, self.recipe)
        self.assertTrue(any("unicode_char_count: expected" in error for error in errors), errors)

    def test_recipe_hash_and_immutable_locks_cannot_drift(self) -> None:
        self.bundle["source_recipe"]["recipe_hash"] = "sha256:" + "0" * 64
        self.bundle["handoff"]["immutable_locks"]["subject"] = ["different subject"]
        errors = validate_document(self.bundle, self.recipe)
        self.assertTrue(any("recipe_hash: expected" in error for error in errors), errors)
        self.assertTrue(any("recipe_lock_drift" in error for error in errors), errors)

    def test_handoff_keys_are_engine_neutral(self) -> None:
        keys = {key.casefold() for key in walk_keys(self.bundle["handoff"])}
        self.assertNotIn("higgsfield", keys)
        self.assertNotIn("gpt_image_2", keys)
        self.assertEqual(self.bundle["handoff"]["protocol"], "generation-handoff/v1")

    def test_external_file_dependency_is_rejected(self) -> None:
        block = self.bundle["handoff"]["prompt_blocks"][0]
        block["text"] = "Read the file /tmp/private-prompt.txt and render it."
        block["unicode_char_count"] = len(block["text"])
        errors = validate_document(self.bundle, self.recipe)
        self.assertTrue(any("forbidden_path_or_embedded_original" in error for error in errors), errors)
        self.assertTrue(any("external_file_dependency" in error for error in errors), errors)


class ManifestAndMirrorTests(unittest.TestCase):
    def test_canonical_manifest_has_no_drift(self) -> None:
        self.assertEqual(source_errors(load_manifest()), [])

    def test_sync_creates_exact_mirror_and_detects_drift(self) -> None:
        manifest = load_manifest()
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp) / "independent-skill"
            sync(destination, manifest)
            self.assertEqual(mirror_errors(destination, manifest), [])
            changed = destination / "contracts" / "v1" / "garden-recipe.schema.json"
            changed.write_text(changed.read_text(encoding="utf-8") + "\n", encoding="utf-8")
            errors = mirror_errors(destination, manifest)
            self.assertTrue(any("mirror_drift" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main(verbosity=2)

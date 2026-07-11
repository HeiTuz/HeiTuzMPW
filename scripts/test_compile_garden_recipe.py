#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_ROOT = Path(os.environ.get("MASTER_PROMPT_CONTRACT_ROOT", ROOT / "contracts"))
FIXTURE = CONTRACT_ROOT / "v1" / "fixtures" / "garden-recipe.image.valid.json"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@unittest.skipUnless(FIXTURE.is_file(), "authoritative contracts must be present or MASTER_PROMPT_CONTRACT_ROOT set")
class CompileGardenRecipeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.compiler = load_module(ROOT / "scripts" / "compile_garden_recipe.py", "recipe_compiler")
        cls.contracts = load_module(CONTRACT_ROOT / "validate.py", "contract_validator")
        cls.recipe = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_compiles_valid_recipe_to_schema_valid_bundle(self) -> None:
        bundle = self.compiler.compile_recipe(copy.deepcopy(self.recipe))
        self.assertEqual([], self.contracts.validate_document(bundle, self.recipe))
        handoff = bundle["handoff"]
        self.assertEqual(self.recipe["locks"], handoff["immutable_locks"])
        self.assertEqual(self.recipe["exclusions"], handoff["negative_constraints"])
        self.assertTrue(handoff["variable_axes"])
        self.assertTrue(handoff["reference_requirements"])
        self.assertTrue(handoff["qc_acceptance_criteria"])

    def test_unicode_count_uses_code_points_and_stays_within_limit(self) -> None:
        recipe = copy.deepcopy(self.recipe)
        recipe["intended_use"]["goal"] = "Create a quiet portrait 🎞️ with 한글 direction."
        block = self.compiler.compile_recipe(recipe)["handoff"]["prompt_blocks"][0]
        self.assertEqual(len(block["text"]), block["unicode_char_count"])
        self.assertLessEqual(block["unicode_char_count"], 2000)

    def test_rejects_unvalidated_legacy_payload(self) -> None:
        with self.assertRaisesRegex(self.compiler.CompileError, "garden_recipe_validation_failed"):
            self.compiler.compile_recipe({"prompt": "legacy raw analysis"})

    def test_rejects_lock_drift_and_overflow(self) -> None:
        recipe = copy.deepcopy(self.recipe)
        recipe["locks"]["subject"] = []
        with self.assertRaisesRegex(self.compiler.CompileError, "garden_recipe_validation_failed"):
            self.compiler.compile_recipe(recipe)

        recipe = copy.deepcopy(self.recipe)
        recipe["intended_use"]["goal"] = "가" * 1000
        recipe["locks"]["subject"] = ["나" * 500]
        recipe["exclusions"] = ["다" * 500, "라" * 500]
        with self.assertRaisesRegex(self.compiler.CompileError, "self_contained_prompt_overflow"):
            self.compiler.compile_recipe(recipe)

    def test_legacy_bridge_adapter_preserves_blocks(self) -> None:
        bundle = self.compiler.compile_recipe(copy.deepcopy(self.recipe))
        legacy = self.compiler.legacy_bridge_bundle(bundle)
        self.assertEqual("master-prompt-writer", legacy["compiled_by"])
        self.assertEqual(
            [block["text"] for block in bundle["handoff"]["prompt_blocks"]],
            [block["text"] for block in legacy["blocks"]],
        )

    def test_cli_emits_machine_readable_failure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "legacy.json"
            path.write_text('{"prompt":"raw"}', encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "compile_garden_recipe.py"), str(path)],
                cwd=ROOT,
                env={**os.environ, "MASTER_PROMPT_CONTRACT_ROOT": str(CONTRACT_ROOT)},
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(1, result.returncode)
        self.assertIn("garden_recipe_validation_failed", result.stderr)


if __name__ == "__main__":
    unittest.main()

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
DESIGN_FIXTURE = CONTRACT_ROOT / "v1" / "fixtures" / "garden-recipe.design.valid.json"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CompileGardenRecipeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not FIXTURE.is_file() or not DESIGN_FIXTURE.is_file():
            raise RuntimeError("authoritative contracts missing; sync contracts/ or set MASTER_PROMPT_CONTRACT_ROOT")
        cls.compiler = load_module(ROOT / "scripts" / "compile_garden_recipe.py", "recipe_compiler")
        cls.contracts = load_module(CONTRACT_ROOT / "validate.py", "contract_validator")
        cls.recipe = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_compiles_valid_recipe_to_schema_valid_bundle(self) -> None:
        bundle = self.compiler.compile_recipe(copy.deepcopy(self.recipe))
        self.assertEqual([], self.contracts.validate_document(bundle, self.recipe))
        handoff = bundle["handoff"]
        self.assertEqual(self.recipe["locks"], handoff["immutable_locks"])
        self.assertEqual(self.recipe["exclusions"], handoff["negative_constraints"])
        self.assertEqual([], handoff["variable_axes"])
        self.assertTrue(handoff["reference_requirements"])
        self.assertTrue(handoff["qc_acceptance_criteria"])
        text = handoff["prompt_blocks"][0]["text"]
        self.assertTrue(text.startswith("[프리셋: Warm Ambient · 비율 2:3 | Color signature:"))
        self.assertNotIn("Exclude:", text)
        self.assertEqual(1, text.count("\n"))
        self.assertNotIn("#C7B7A4", text)
        self.assertIn("natural skin texture, visible pores, subtle film grain", text)
        self.assertIn("unbranded clean finish", text)



    def test_design_recipe_routes_from_intended_use(self) -> None:
        recipe = json.loads(DESIGN_FIXTURE.read_text(encoding="utf-8"))
        bundle = self.compiler.compile_recipe(recipe)
        self.assertEqual([], self.contracts.validate_document(bundle, recipe))
        self.assertEqual("DESIGN", bundle["handoff"]["mode"])
        self.assertEqual("frontend-agent", bundle["handoff"]["engine"])
        self.assertEqual([], bundle["handoff"]["variable_axes"])
        text = bundle["handoff"]["prompt_blocks"][0]["text"]
        self.assertIn("Visual thesis:", text)
        self.assertIn("Reference decomposition:", text)
        self.assertIn("Viewport QC:", text)
        self.assertIn("Qualified layout tokens: twelve-column content grid", text)



    def test_composite_renderer_applies_preservation_gate(self) -> None:
        recipe = copy.deepcopy(self.recipe)
        recipe["category"] = "composite_reference"
        recipe["intended_use"] = {
            "mode": "IMAGE_COMPOSITE",
            "engine": "generic-image",
            "goal": "Replace only the background with a quiet studio environment.",
        }
        bundle = self.compiler.compile_recipe(recipe)
        self.assertEqual([], self.contracts.validate_document(bundle, recipe))
        text = bundle["handoff"]["prompt_blocks"][0]["text"]
        self.assertIn("PIXEL-BOUND COMPOSITE", text)
        self.assertIn("locked photographic plate", text)
        self.assertIn("coordinates stay 1:1", text)
        self.assertIn("dial B partial", text)
        self.assertIn("FINAL INTENT:", text)
        self.assertIn("FAIL if", text)


    def test_gpt_image_renderer_requires_palette_gate_and_terminal_ar(self) -> None:
        recipe = copy.deepcopy(self.recipe)
        recipe["intended_use"]["engine"] = "gpt-image-2"
        with self.assertRaisesRegex(self.compiler.CompileError, "requires 3-5 distinct observed #RRGGBB"):
            self.compiler.compile_recipe(recipe)
        recipe["observations"]["palette"]["items"][0]["value"] = "warm beige without a color token"
        with self.assertRaisesRegex(self.compiler.CompileError, "received 0"):
            self.compiler.compile_recipe(recipe)
        recipe["observations"]["palette"]["items"][0]["value"] = "#C7B7A4"

        palette = recipe["observations"]["palette"]["items"]
        for index, value in ((2, "#2A2520"), (3, "#F2E9DD")):
            item = copy.deepcopy(palette[0])
            item["observation_id"] = f"obs_palette_0{index}"
            item["value"] = value
            palette.append(item)
        bundle = self.compiler.compile_recipe(recipe)
        self.assertEqual([], self.contracts.validate_document(bundle, recipe))
        text = bundle["handoff"]["prompt_blocks"][0]["text"]
        self.assertTrue(text.endswith("AR 2:3"))
        self.assertNotIn("Exclude:", text)

    def test_low_confidence_valid_inference_is_not_dropped(self) -> None:
        recipe = copy.deepcopy(self.recipe)
        recipe["inferences"][0]["confidence"] = 0.01
        claim = recipe["inferences"][0]["claim"]
        text = self.compiler.compile_recipe(recipe)["handoff"]["prompt_blocks"][0]["text"]
        self.assertIn(claim, text)

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
        recipe["exclusions"] = ["watermark"]
        with self.assertRaisesRegex(self.compiler.CompileError, "self_contained_prompt_overflow"):
            self.compiler.compile_recipe(recipe)

    def test_positive_lane_rejects_untranslatable_exclusion(self) -> None:
        recipe = copy.deepcopy(self.recipe)
        recipe["exclusions"] = ["sentinel forbidden artifact"]
        with self.assertRaisesRegex(self.compiler.CompileError, "untranslatable_positive_exclusion"):
            self.compiler.compile_recipe(recipe)

    def test_legacy_bridge_adapter_preserves_blocks(self) -> None:
        recipe = copy.deepcopy(self.recipe)
        recipe["exclusions"] = ["watermark"]
        bundle = self.compiler.compile_recipe(recipe)
        legacy = self.compiler.legacy_bridge_bundle(bundle)
        self.assertEqual("master-prompt-writer", legacy["compiled_by"])
        self.assertEqual(
            [block["text"] for block in bundle["handoff"]["prompt_blocks"]],
            [block["text"] for block in legacy["blocks"]],
        )
        self.assertIn("unbranded clean finish", legacy["blocks"][0]["text"])

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

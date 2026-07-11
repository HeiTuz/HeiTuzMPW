#!/usr/bin/env python3
"""Cross-repository contract and closed-loop integration verification."""
from __future__ import annotations

import importlib.util
import json
import os
import sys
import unittest
from pathlib import Path
from typing import Any

MASTER_ROOT = Path(__file__).resolve().parents[1]


def skill_root(env_name: str, skill_name: str) -> Path:
    configured = os.environ.get(env_name)
    if configured:
        return Path(configured)
    candidates = [
        MASTER_ROOT.parent / skill_name,
        Path.home() / "src" / skill_name,
        Path.home() / ".hermes" / "skills" / "prompt-writing" / skill_name,
    ]
    return next((path for path in candidates if path.is_dir()), candidates[0])


IMAGE_ROOT = skill_root("IMAGE_REFERENCE_GARDENER_ROOT", "image-reference-gardener")
DESIGN_ROOT = skill_root("DESIGN_REFERENCE_GARDENER_ROOT", "design-reference-gardener")
BRIDGE_ROOT = skill_root("HIGGSFIELD_BRIDGE_ROOT", "higgsfield-prompt-bridge")
CONTRACT_ROOT = Path(os.environ.get("MASTER_PROMPT_CONTRACT_ROOT", MASTER_ROOT / "contracts"))
COMPILER_ROOT = Path(os.environ.get("MASTER_PROMPT_COMPILER_ROOT", MASTER_ROOT))


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load integration module: {name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class GardenerMasterIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        required = [
            CONTRACT_ROOT / "validate.py",
            CONTRACT_ROOT / "v1/fixtures/garden-recipe.image.valid.json",
            CONTRACT_ROOT / "v1/fixtures/garden-recipe.design.valid.json",
            COMPILER_ROOT / "scripts/compile_garden_recipe.py",
            IMAGE_ROOT / "scripts/gardener_loop.py",
            DESIGN_ROOT / "scripts/gardener_loop.py",
            BRIDGE_ROOT / "scripts/higgsfield_job.py",
        ]
        missing = [str(path) for path in required if not path.is_file()]
        if missing:
            raise RuntimeError("integration dependencies missing: " + ", ".join(missing))
        os.environ["MASTER_PROMPT_CONTRACT_ROOT"] = str(CONTRACT_ROOT)
        cls.contracts = load_module("integration_contracts", CONTRACT_ROOT / "validate.py")
        cls.compiler = load_module("integration_compiler", COMPILER_ROOT / "scripts/compile_garden_recipe.py")
        cls.image_loop = load_module("integration_image_loop", IMAGE_ROOT / "scripts/gardener_loop.py")
        cls.design_loop = load_module("integration_design_loop", DESIGN_ROOT / "scripts/gardener_loop.py")
        cls.bridge = load_module("integration_higgsfield_bridge", BRIDGE_ROOT / "scripts/higgsfield_job.py")
        cls.image_recipe = json.loads((CONTRACT_ROOT / "v1/fixtures/garden-recipe.image.valid.json").read_text(encoding="utf-8"))
        cls.design_recipe = json.loads((CONTRACT_ROOT / "v1/fixtures/garden-recipe.design.valid.json").read_text(encoding="utf-8"))

    def test_canonical_recipes_cross_gardener_validation_boundary(self) -> None:
        self.assertEqual([], self.image_loop.recipe_contract_errors(
            self.image_recipe,
            reference_id=self.image_recipe["source"]["reference_id"],
            lane="photo_editorial",
        ))
        self.assertEqual([], self.design_loop.recipe_contract_errors(
            self.design_recipe,
            reference_id=self.design_recipe["source"]["reference_id"],
            lane="ui_layout",
        ))

    def test_machine_handoff_carries_complete_private_recipe(self) -> None:
        handoff = self.image_loop.build_compile_handoff(
            self.image_recipe,
            reference_id=self.image_recipe["source"]["reference_id"],
            lane="photo_editorial",
            executor_handoff=True,
            now=__import__("datetime").datetime(2026, 7, 11, tzinfo=__import__("datetime").timezone.utc),
        )
        self.assertEqual(self.image_recipe, handoff.get("garden_recipe"))
        self.assertEqual([], self.image_loop.privacy_errors(handoff))

    def test_compile_bundle_and_legacy_bridge_remain_compatible(self) -> None:
        bundle = self.compiler.compile_recipe(self.image_recipe)
        self.assertEqual([], self.contracts.validate_document(bundle, self.image_recipe))
        self.assertEqual(self.image_recipe["locks"], bundle["handoff"]["immutable_locks"])
        self.assertTrue(all(len(block["text"]) <= 2000 for block in bundle["handoff"]["prompt_blocks"]))
        legacy = self.compiler.legacy_bridge_bundle(bundle)
        job = {
            "schema_version": "higgsfield-job/v1",
            "mode": "prompt_only",
            "intent": {"goal": self.image_recipe["intended_use"]["goal"], "lane": "photo_still"},
            "executor": {"kind": "web_ui", "target": "higgsfield_web"},
            "payload_kind": "compiled_prompt",
            "prompt_bundle": legacy,
            "media": [],
        }
        self.assertEqual([], self.bridge.schema_errors(job))

    def test_feedback_is_explicit_scoped_and_proposal_only(self) -> None:
        module = self.image_loop
        now = __import__("datetime").datetime(2026, 7, 11, tzinfo=__import__("datetime").timezone.utc)
        event = module.build_feedback_event(
            reference_id=self.image_recipe["source"]["reference_id"],
            lane="photo_editorial",
            decision="correction",
            correction="reduce grain",
            now=now,
        )
        self.assertEqual("correction", event["evaluation"]["decision"])
        self.assertEqual([{
            "reference_id": self.image_recipe["source"]["reference_id"],
            "decision": "correction",
            "correction": "reduce grain",
            "status": "proposal_only",
        }], module.feedback_candidates([event], lane="photo_editorial"))
        with self.assertRaisesRegex(ValueError, "feedback_privacy_violation"):
            module.build_feedback_event(
                reference_id=self.image_recipe["source"]["reference_id"],
                lane="photo_editorial",
                decision="correction",
                correction="open /Users/private/original.jpg",
                now=now,
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)

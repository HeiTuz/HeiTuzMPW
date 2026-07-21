#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import re
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("compile_image_handoff", ROOT / "scripts/compile_image_handoff.py")
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def request(**overrides):
    value = {
        "schema_version": "image-production-request/v2",
        "job_id": "catalog-01",
        "operation": "edit",
        "subject": "A ceramic cup with its exact logo preserved",
        "scene": "A pale stone tabletop",
        "composition": "Centered product framing",
        "input_images": [{"path": "assets/cup.png", "role": "Product identity reference"}],
        "aspect_ratio": "1:1",
        "image_size": "1024x1024",
        "output": {"filename": "catalog-01.png"},
    }
    value.update(overrides)
    return value


class CompileImageHandoffTests(unittest.TestCase):
    def test_emits_shared_portable_contract(self):
        result = MODULE.compile_request(request())
        self.assertEqual(result["schema_version"], "image-production-handoff/v2")
        self.assertEqual(result["input_images"][0]["path"], "assets/cup.png")
        self.assertIn("Subject: A ceramic cup", result["prompt"])
        self.assertLessEqual(len(result["prompt"]), 2000)

    def test_generate_is_standalone_without_inputs(self):
        result = MODULE.compile_request(request(operation="generate", input_images=None))
        self.assertNotIn("input_images", result)

    def test_edit_requires_input(self):
        with self.assertRaisesRegex(MODULE.CompileError, "requires at least one"):
            MODULE.compile_request(request(input_images=[]))
    def test_all_supported_lowercase_output_extensions_match_schema(self):
        schema = json.loads((ROOT / "contracts/v1/image-production-handoff.schema.json").read_text())
        pattern = schema["properties"]["output"]["properties"]["filename"]["pattern"]
        for suffix in ("png", "jpg", "jpeg", "webp"):
            result = MODULE.compile_request(request(output={"filename": f"catalog-01.{suffix}"}))
            self.assertRegex(result["output"]["filename"], pattern)

    def test_rejects_uppercase_output_extension(self):
        for suffix in ("PNG", "JPG", "JPEG", "WEBP"):
            with self.subTest(suffix=suffix):
                with self.assertRaisesRegex(MODULE.CompileError, "one PNG, JPEG, or WebP basename"):
                    MODULE.compile_request(request(output={"filename": f"catalog-01.{suffix}"}))

    def test_schema_requires_input_for_edit(self):
        schema = json.loads((ROOT / "contracts/v1/image-production-handoff.schema.json").read_text())
        invariant = schema["allOf"][0]
        self.assertEqual(invariant["if"]["properties"]["operation"]["const"], "edit")
        self.assertIn("input_images", invariant["then"]["required"])
        self.assertEqual(invariant["then"]["properties"]["input_images"]["minItems"], 1)

    def test_rejects_absolute_private_path(self):
        with self.assertRaisesRegex(MODULE.CompileError, "portable relative path"):
            MODULE.compile_request(request(input_images=[{"path": "/home/person/cup.png", "role": "reference"}]))

    def test_rejects_traversal(self):
        with self.assertRaisesRegex(MODULE.CompileError, "traversal"):
            MODULE.compile_request(request(input_images=[{"path": "../cup.png", "role": "reference"}]))

    def test_accepts_public_https_reference(self):
        result = MODULE.compile_request(request(input_images=[{
            "path": "https://example.com/assets/cup.png", "role": "reference"
        }]))
        self.assertEqual(result["input_images"][0]["path"], "https://example.com/assets/cup.png")

    def test_rejects_prompt_overflow(self):
        with self.assertRaisesRegex(MODULE.CompileError, "prompt exceeds"):
            MODULE.compile_request(request(subject="x" * 2000, scene="y"))

    def test_fixture_matches_schema_shape(self):
        schema = json.loads((ROOT / "contracts/v1/image-production-handoff.schema.json").read_text())
        fixture = json.loads((ROOT / "contracts/v1/fixtures/image-production-handoff.valid.json").read_text())
        self.assertEqual(fixture["schema_version"], schema["properties"]["schema_version"]["const"])
        self.assertEqual(set(schema["required"]) - set(fixture), set())
        self.assertEqual(set(fixture) - set(schema["properties"]), set())
    def test_schema_rejects_nonportable_input_paths(self):
        schema = json.loads((ROOT / "contracts/v1/image-production-handoff.schema.json").read_text())
        alternatives = schema["properties"]["input_images"]["items"]["properties"]["path"]["oneOf"]

        def accepted(value):
            return sum(bool(re.search(item["pattern"], value)) for item in alternatives) == 1

        self.assertTrue(accepted("assets/cup.png"))
        self.assertTrue(accepted("https://example.com/assets/cup.png"))
        for value in (
            "/" + "Users/person/cup.png",
            "~/.local/cup.png",
            "../cup.png",
            "assets/../cup.png",
            "http://example.com/cup.png",
            "https://user:password@example.com/cup.png",
        ):
            with self.subTest(value=value):
                self.assertFalse(accepted(value))

    def test_cli_writes_canonical_json(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "request.json"
            output = Path(directory) / "handoff.json"
            source.write_text(json.dumps(request()), encoding="utf-8")
            self.assertEqual(MODULE.main([str(source), "--output", str(output)]), 0)
            self.assertEqual(json.loads(output.read_text())["job_id"], "catalog-01")


if __name__ == "__main__":
    unittest.main()

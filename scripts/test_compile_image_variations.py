import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location("compile_image_variations", ROOT / "scripts" / "compile_image_variations.py")
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ImageVariationCompilerTests(unittest.TestCase):
    def request(self):
        return {
            "concept": "홍대 골목의 독립 잡지 같은 고양이 초상",
            "style": "anti-mainstream editorial, dry and strange",
            "locks": {"subject": "same fictional black cat", "text": "none"},
            "output_prefix": "images",
        }

    def test_hundred_variations_are_unique_deterministic_and_qc_free(self):
        first = MODULE.compile_variations(self.request(), 100, 17)
        second = MODULE.compile_variations(self.request(), 100, 17)
        self.assertEqual(first, second)
        self.assertEqual(len(first), 100)
        self.assertEqual(len({row["full_prompt"] for row in first}), 100)
        self.assertTrue(all(row["qc_required"] is False for row in first))
        self.assertTrue(all(row["metadata"]["ideation_batch"] is True for row in first))
        self.assertEqual(first[0]["output_path"], "images/001.png")
        self.assertEqual(first[-1]["output_path"], "images/100.png")
        self.assertTrue(all(len(row["full_prompt"]) <= 2000 for row in first))

    def test_single_request_is_strengthened(self):
        row = MODULE.compile_variations({"concept": "a blue cup", "style": "", "locks": {}, "output_prefix": "images"}, 1, 3)[0]
        self.assertNotEqual(row["full_prompt"], "a blue cup")
        self.assertIn("Composition:", row["full_prompt"])
        self.assertFalse(row["metadata"]["ideation_batch"])

    def test_cli_writes_portable_jsonl_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            request = root / "request.json"
            output = root / "manifest.jsonl"
            request.write_text(json.dumps(self.request(), ensure_ascii=False), encoding="utf-8")
            self.assertEqual(MODULE.main(["--request", str(request), "--count", "3", "--output", str(output), "--seed", "9"]), 0)
            rows = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(len(rows), 3)
            self.assertEqual(MODULE.main(["--request", str(request), "--count", "3", "--output", str(output)]), 2)

    def test_invalid_inputs_fail_closed(self):
        with self.assertRaises(ValueError):
            MODULE.compile_variations(self.request(), 0)
        with self.assertRaises(ValueError):
            MODULE.compile_variations(self.request(), 1001)
        with tempfile.TemporaryDirectory() as tmp:
            request = Path(tmp) / "bad.json"
            request.write_text(json.dumps({"concept": "x", "output_prefix": "../escape"}), encoding="utf-8")
            with self.assertRaises(ValueError):
                MODULE._request(request)


if __name__ == "__main__":
    unittest.main()

"""Regressions for chapter-local definitions overriding canonical citations."""
import contextlib
import importlib.util
import io
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Citations(unittest.TestCase):
    def test_sourceless_canonical_override_is_rejected(self):
        spec = importlib.util.spec_from_file_location("citation_gate", ROOT / "scripts/check_citations.py")
        gate = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(gate)
        with tempfile.TemporaryDirectory() as temporary:
            gate.CONTENT = Path(temporary) / "content"
            shutil.copytree(ROOT / "content", gate.CONTENT)
            chapter = gate.CONTENT / "chapters/01-faster-coding-is-only-part.md"
            chapter.write_text(chapter.read_text(encoding="utf-8") +
                               "\n[^bockeler-harness]: This definition has no source URL.\n", encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()) as output:
                result = gate.main()
            self.assertEqual(result, 1)
            self.assertIn("cannot be redefined locally", output.getvalue())

    def test_generator_also_rejects_canonical_override(self):
        spec = importlib.util.spec_from_file_location("site_generator", ROOT / "site/generate.py")
        generator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(generator)
        with self.assertRaisesRegex(SystemExit, "cannot be redefined"):
            generator.preprocess_markdown("Text.[^bockeler-harness]\n\n[^bockeler-harness]: No source.", "part-1")

"""Regressions for the citation gate: canonical overrides and diagram text."""
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


def load_gate(temporary):
    spec = importlib.util.spec_from_file_location("citation_gate", ROOT / "scripts/check_citations.py")
    gate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gate)
    gate.CONTENT = Path(temporary) / "content"
    shutil.copytree(ROOT / "content", gate.CONTENT)
    return gate


def run(gate):
    with contextlib.redirect_stdout(io.StringIO()) as output:
        result = gate.main()
    return result, output.getvalue()


class DiagramText(unittest.TestCase):
    SVG = ('<svg xmlns="http://www.w3.org/2000/svg"{refs}><title>Example</title><desc>{desc}</desc>'
           '<text x="0" y="0">{text}</text></svg>')

    def write(self, gate, text="Work tracking", desc="A diagram.", refs=""):
        attr = f' data-references="{refs}"' if refs else ""
        (gate.CONTENT / "diagrams/svg/zz-test.svg").write_text(
            self.SVG.format(refs=attr, desc=desc, text=text), encoding="utf-8")

    def test_keep_out_and_product_names_in_diagram_text_fail(self):
        with tempfile.TemporaryDirectory() as temporary:
            gate = load_gate(temporary)
            self.write(gate, text="Backlog in Jira / Confluence", desc="SDD with GitHub Spec Kit")
            result, output = run(gate)
            self.assertEqual(result, 1)
            for name in ("Jira", "Confluence", "GitHub", "Spec Kit"):
                self.assertIn(f"diagram zz-test: '{name}'", output)

    def test_neutral_diagram_passes_and_lowercase_urls_are_not_products(self):
        with tempfile.TemporaryDirectory() as temporary:
            gate = load_gate(temporary)
            self.write(gate, text="Beyond Faster Coding · vishalkhondre.github.io/ai-sdlc")
            self.assertEqual(run(gate)[0], 0)

    def test_unknown_data_reference_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            gate = load_gate(temporary)
            self.write(gate, refs="bockeler-harness no-such-key")
            result, output = run(gate)
            self.assertEqual(result, 1)
            self.assertIn("data-references key 'no-such-key' is not in references.yml", output)

    def test_reference_cited_only_by_a_diagram_is_dead_without_it(self):
        with tempfile.TemporaryDirectory() as temporary:
            gate = load_gate(temporary)
            svg = gate.CONTENT / "diagrams/svg/ai-sdlc-map.svg"
            svg.write_text(svg.read_text(encoding="utf-8").replace(" dora-metrics", ""), encoding="utf-8")
            result, output = run(gate)
            self.assertEqual(result, 1)
            self.assertIn("'dora-metrics' is never cited", output)

    def test_map_generator_output_is_committed(self):
        spec = importlib.util.spec_from_file_location("build_map", ROOT / "content/diagrams/map/build_map.py")
        build_map = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(build_map)
        svg = ROOT / "content/diagrams/svg"
        self.assertEqual(build_map.page_map(), (svg / "ai-sdlc-map.svg").read_text(encoding="utf-8"))
        self.assertEqual(build_map.page_path(), (svg / "ai-sdlc-adoption-path.svg").read_text(encoding="utf-8"))

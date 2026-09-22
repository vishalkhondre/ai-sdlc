"""Build-time checks for the generated site. Run: python -m unittest discover -s scripts/tests -v"""
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "site"
CONTENT = ROOT / "content"


class Generated(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(SITE / "generate.py")], check=True, capture_output=True)
        cls.toc = yaml.safe_load((CONTENT / "toc.yml").read_text(encoding="utf-8"))

    def test_every_chapter_has_a_page(self):
        for ch in self.toc["chapters"]:
            self.assertTrue((SITE / f"{ch['slug']}.html").exists(), ch["slug"])

    def test_internal_links_resolve(self):
        pages = list(SITE.glob("*.html"))
        names = {p.name for p in pages}
        for p in pages:
            html = p.read_text(encoding="utf-8")
            for href in re.findall(r'href="([^"#:]+\.html)', html):
                self.assertIn(Path(href).name, names, f"{p.name} -> {href}")
            ids = set(re.findall(r'id="([^"]+)"', html))
            for frag in re.findall(r'href="#([^"]+)"', html):
                if frag.startswith("fn") or frag.startswith("W") or frag in ("notes",):
                    continue
                self.assertIn(frag, ids, f"{p.name} -> #{frag}")

    def test_diagrams_referenced_exist(self):
        for p in SITE.glob("*.html"):
            for did in re.findall(r'data-diagram="([^"]+)"', p.read_text(encoding="utf-8")):
                self.assertTrue((SITE / "diagrams" / f"{did}.svg").exists(), did)

    def test_no_keep_out_names_in_pages(self):
        banned = ["Regal", "Rexnord", "RRX", "Cursor", "Copilot", "Lovable"]
        for p in SITE.glob("*.html"):
            html = p.read_text(encoding="utf-8")
            for b in banned:
                self.assertNotRegex(html, rf"\b{b}\b", f"{p.name} contains {b}")

    def test_footnotes_have_backing(self):
        for ch in self.toc["chapters"]:
            html = (SITE / f"{ch['slug']}.html").read_text(encoding="utf-8")
            refs = re.findall(r'href="#fn:([^"]+)"', html)
            for r in set(refs):
                self.assertIn(f'id="fn:{r}"', html, f"{ch['slug']}: fn:{r}")

    def test_search_index_and_llms(self):
        idx = json.loads((SITE / "search-index.json").read_text(encoding="utf-8"))
        self.assertGreater(len(idx), 40)
        self.assertIn("Beyond Faster Coding", (SITE / "llms.txt").read_text(encoding="utf-8"))

    def test_catalog_data(self):
        cat = yaml.safe_load((CONTENT / "workflows" / "catalog.yml").read_text(encoding="utf-8"))
        ids = [w["id"] for w in cat["workflows"]]
        self.assertEqual(len(ids), len(set(ids)))
        phases = {p["key"] for p in cat["phases"]}
        for w in cat["workflows"]:
            self.assertIn(w["phase"], phases, w["id"])
            self.assertIn(w["maturity"], cat["maturity"], w["id"])
            for k in ("decision", "trigger", "agent", "checks", "people", "evidence"):
                self.assertTrue(w[k], f"{w['id']} missing {k}")
        for r in cat["traditional_map"]:
            for part in str(r["lands_in"]).split("/"):
                part = part.strip()
                if part.startswith("W"):
                    self.assertIn(part, ids, r["activity"])

    def test_citation_gate(self):
        res = subprocess.run([sys.executable, str(ROOT / "scripts" / "check_citations.py")], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)


if __name__ == "__main__":
    unittest.main()

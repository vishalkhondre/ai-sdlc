"""Citation and terminology gate.

Fails (exit 1) when:
  1. a chapter uses a footnote [^key] that is neither defined in the chapter nor a key in references.yml
  2. a glossary term is `adopted` or `adapted` but names no `source`, or its source is not in references.yml
  3. a chapter listed under an adopted/adapted term's `chapters:` never cites that term's source
     (a chapter that uses someone else's vocabulary must point at them at least once)
  4. a reference in references.yml is never cited by any chapter or glossary term (dead reference)
  5. a diagram embed ![..](diagram:id) points at an id that does not exist
  6. a chapter mentions a vendor / organisation name the series has chosen to keep out of the prose
  7. diagram text (every <text>, <title> and <desc> in content/diagrams/svg) contains a keep-out name or a
     product name: diagrams are not category pages, so they stay vendor-neutral (GR-3.3). Credit lines
     (<text class="credit">) may name a source, as chapter notes may, but never a keep-out name.
  8. a diagram's data-references attribute (on the root or a credit line) names a key that is not in
     references.yml (keys listed there count as cited, so a reference used only by a diagram is not dead)
  9. a diagram that no chapter embeds uses an adopted or adapted glossary term without a credit line
     naming that term's source: a downloaded diagram has no chapter notes to carry the credit (GR-2.2)

Run:  python scripts/check_citations.py
"""
from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"

# Words the series deliberately keeps out of chapter prose (they may appear in references.yml).
BANNED_IN_PROSE = [
    r"\bCursor\b", r"\bCopilot\b", r"\bLovable\b", r"\bClaude\b", r"\bChatGPT\b", r"\bGemini\b",
    r"\bAzure DevOps\b", r"\bJira\b", r"\bRegal\b", r"\bRexnord\b", r"\bRRX\b", r"\bNRC\b",
]

# Product names allowed only on a page about their category (GR-3.3); never in a diagram.
PRODUCT_NAMES = [
    r"\bGitHub\b", r"\bGitLab\b", r"\bBitbucket\b", r"\bConfluence\b", r"\bSpec Kit\b", r"\bOpenSpec\b",
    r"\bJenkins\b", r"\bCircleCI\b", r"\bCodex\b", r"\bWindsurf\b", r"\bDevin\b", r"\bKiro\b",
    r"\bCodeRabbit\b", r"\bSonarQube\b", r"\bSnyk\b",
]


def diagram_text(svg: ET.Element) -> tuple[str, str, set[str]]:
    """Reader-visible text of a diagram (text, title and desc elements, one per line), split into
    body text and credit lines, plus the reference keys its credit lines declare."""
    body, credits, credited = [], [], set()
    for el in svg.iter():
        if el.tag.rsplit("}", 1)[-1] not in ("text", "title", "desc"):
            continue
        if "credit" in (el.get("class") or "").split():
            credits.append("".join(el.itertext()))
            credited.update((el.get("data-references") or "").split())
        else:
            body.append("".join(el.itertext()))
    return "\n".join(body), "\n".join(credits), credited


def check_diagrams(refs: dict, glossary: list, embedded: set[str]) -> tuple[list[str], set[str]]:
    problems: list[str] = []
    cited: set[str] = set()
    for path in sorted((CONTENT / "diagrams" / "svg").glob("*.svg")):
        svg = ET.parse(path).getroot()
        body, credits, credited = diagram_text(svg)
        for pat in BANNED_IN_PROSE + PRODUCT_NAMES:
            for m in re.finditer(pat, body):
                problems.append(f"diagram {path.stem}: '{m.group(0)}' is a keep-out or product name; diagrams stay vendor-neutral")
        for pat in BANNED_IN_PROSE:
            for m in re.finditer(pat, credits):
                problems.append(f"diagram {path.stem}: credit line names '{m.group(0)}', which is on the keep-out list")
        for key in sorted(set((svg.get("data-references") or "").split()) | credited):
            if key in refs:
                cited.add(key)
            else:
                problems.append(f"diagram {path.stem}: data-references key '{key}' is not in references.yml")
        if path.stem in embedded:
            continue  # the embedding chapter's notes carry the credit (checks 3 and 4)
        for g in glossary:
            if g.get("attribution") not in ("adopted", "adapted") or not g.get("source"):
                continue
            for name in [g["term"]] + list(g.get("match") or []):
                if re.search(rf"\b{re.escape(name)}\b", body, flags=re.I):
                    if g["source"] not in credited:
                        problems.append(f"diagram {path.stem}: uses '{g['term']}' ({g['attribution']} from {g['source']}) "
                                        f"but no credit line names {g['source']}")
                    break
    return problems, cited


def main() -> int:
    toc = yaml.safe_load((CONTENT / "toc.yml").read_text(encoding="utf-8"))
    glossary = yaml.safe_load((CONTENT / "glossary.yml").read_text(encoding="utf-8"))
    refs = yaml.safe_load((CONTENT / "references.yml").read_text(encoding="utf-8"))
    diagram_ids = {p.stem for p in (CONTENT / "diagrams" / "svg").glob("*.svg")}
    for n, name in {1: "kit-touched", 2: "run", 3: "exits", 4: "flows", 5: "measures"}.items():
        for v in ("generic", "export"):
            diagram_ids.add(f"p7-{n}-{name}-{v}")

    problems: list[str] = []
    cited_by_chapter: dict[str, set[str]] = {}
    for ch in toc["chapters"]:
        text = (CONTENT / "chapters" / ch["file"]).read_text(encoding="utf-8")
        used = set(re.findall(r"\[\^([a-z0-9\-]+)\](?!:)", text))
        defined = set(re.findall(r"^\[\^([a-z0-9\-]+)\]:", text, flags=re.M))
        for key in sorted(defined & refs.keys()):
            problems.append(f"{ch['id']}: canonical reference [^{key}] cannot be redefined locally; use a distinct note key")
        cited = set()
        for key in used:
            if key in refs and key not in defined:
                cited.add(key)
            elif key in defined:
                # an inline note: it must still link to at least one canonical reference URL
                body = re.search(rf"^\[\^{re.escape(key)}\]:(.*)$", text, flags=re.M).group(1)
                urls = [r["url"] for r in refs.values() if r.get("url") and r["url"] in body]
                if not urls:
                    problems.append(f"{ch['id']}: note [^{key}] does not link to any URL in references.yml")
                for k, r in refs.items():
                    if r.get("url") and r["url"] in body:
                        cited.add(k)
            else:
                problems.append(f"{ch['id']}: footnote [^{key}] is neither defined in the chapter nor in references.yml")
        for key in defined - used:
            problems.append(f"{ch['id']}: footnote [^{key}] is defined but never used")
        cited_by_chapter[ch["id"]] = cited
        for did in re.findall(r"\]\(diagram:([a-z0-9\-]+)\)", text):
            if did not in diagram_ids:
                problems.append(f"{ch['id']}: unknown diagram '{did}'")
        prose = re.sub(r"^\[\^.*$", "", text, flags=re.M)  # notes may name sources
        for pat in BANNED_IN_PROSE:
            for m in re.finditer(pat, prose):
                line = prose[: m.start()].count("\n") + 1
                problems.append(f"{ch['id']}: line {line}: '{m.group(0)}' is on the keep-out list for chapter prose")

    used_refs: set[str] = set().union(*cited_by_chapter.values()) if cited_by_chapter else set()
    embedded = set()
    for ch in toc["chapters"]:
        embedded |= set(re.findall(r"\]\(diagram:([a-z0-9\-]+)\)", (CONTENT / "chapters" / ch["file"]).read_text(encoding="utf-8")))
    diagram_problems, cited_by_diagrams = check_diagrams(refs, glossary, embedded)
    problems += diagram_problems
    used_refs |= cited_by_diagrams
    for g in glossary:
        attr = g.get("attribution")
        src = g.get("source")
        if attr in ("adopted", "adapted"):
            if not src:
                problems.append(f"glossary '{g['id']}': attribution '{attr}' requires a source")
            elif src not in refs:
                problems.append(f"glossary '{g['id']}': source '{src}' is not in references.yml")
            else:
                used_refs.add(src)
                accepted = {src} | set(g.get("also") or [])
                for cid in g.get("chapters") or []:
                    if cid in cited_by_chapter and not (cited_by_chapter[cid] & accepted):
                        problems.append(f"{cid}: uses '{g['term']}' ({attr} from {src}) but never cites {src}")
        for k in g.get("also") or []:
            if k not in refs:
                problems.append(f"glossary '{g['id']}': 'also' source '{k}' is not in references.yml")
            used_refs.add(k)
        for cid in g.get("chapters") or []:
            if cid not in {c["id"] for c in toc["chapters"]}:
                problems.append(f"glossary '{g['id']}': unknown chapter '{cid}'")
    for k in refs:
        if k not in used_refs:
            problems.append(f"references.yml: '{k}' is never cited by a chapter, a glossary term or a diagram")

    if problems:
        print("Citation check FAILED:")
        for p in problems:
            print("  -", p)
        return 1
    n_notes = sum(len(v) for v in cited_by_chapter.values())
    print(f"Citation check passed: {len(toc['chapters'])} chapters, {n_notes} citations, {len(glossary)} terms, {len(refs)} references.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Citation and terminology gate.

Fails (exit 1) when:
  1. a chapter uses a footnote [^key] that is neither defined in the chapter nor a key in references.yml
  2. a glossary term is `adopted` or `adapted` but names no `source`, or its source is not in references.yml
  3. a chapter listed under an adopted/adapted term's `chapters:` never cites that term's source
     (a chapter that uses someone else's vocabulary must point at them at least once)
  4. a reference in references.yml is never cited by any chapter or glossary term (dead reference)
  5. a diagram embed ![..](diagram:id) points at an id that does not exist
  6. a chapter mentions a vendor / organisation name the series has chosen to keep out of the prose

Run:  python scripts/check_citations.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"

# Words the series deliberately keeps out of chapter prose (they may appear in references.yml).
BANNED_IN_PROSE = [
    r"\bCursor\b", r"\bCopilot\b", r"\bLovable\b", r"\bClaude\b", r"\bChatGPT\b", r"\bGemini\b",
    r"\bAzure DevOps\b", r"\bJira\b", r"\bRegal\b", r"\bRexnord\b", r"\bRRX\b", r"\bNRC\b",
]


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
            problems.append(f"references.yml: '{k}' is never cited by a chapter or a glossary term")

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

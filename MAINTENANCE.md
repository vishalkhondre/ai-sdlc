# Maintenance

*Beyond Faster Coding* is complete. This repository publishes the seven-part series at
<https://vishalkhondre.github.io/ai-sdlc/> and is maintained only (decision D-010, recorded in
`vishalkhondre/ai-sdlc-map`).

## Where new work happens

*AI SDLC on one page*, the reference site built around the five-band map, lives in
[`vishalkhondre/ai-sdlc-map`](https://github.com/vishalkhondre/ai-sdlc-map) and is published at
<https://vishalkhondre.github.io/ai-sdlc-map/>. Its goal, ground rules, status, approach and
decision log are in that repository's `CLAUDE.md` and `project/` folder, which moved there from
here. The series links to it from its home page; it links back to each part.

## What maintenance covers here

- Corrections to the series text, references, glossary or workflow catalog.
- Broken links, and cross-links to and from `ai-sdlc-map`.
- Build, CI and security fixes.

New topics, reference pages and map work go to `ai-sdlc-map`, not here.

## How to change anything

Work on a branch and land it through a pull request; `main` always builds and passes validation.
Follow `.github/prompts/update-content.prompt.md`: reader-visible content changes need an edition
bump, a changelog entry and a recorded reviewer ACCEPT
(`scripts/release_content.py record-review`). Tooling-only changes keep the edition. The ground
rules in `vishalkhondre/ai-sdlc-map` (`project/GROUND-RULES.md`) apply here too.

```bash
pip install -r scripts/requirements.txt
python -m playwright install chromium
python scripts/check_citations.py
python scripts/release_content.py check --base <base commit>
python site/generate.py
python scripts/render_diagrams.py
python -m unittest discover -s scripts/tests
python scripts/check_browser.py
```

## Open items for this repository

- Replace the plain-text keep-out names in `scripts/check_citations.py` and
  `scripts/tests/test_site.py` with a hashed deny-list (GR-1.4), as `ai-sdlc-map` already does
  (D-012), and decide whether to rewrite history here.

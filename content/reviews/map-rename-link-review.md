# Review: whole-picture link renamed to The AI SDLC Map (tooling-only, edition stays 1.1.0)

Editorial and confidentiality review of `git diff origin/main 797ff1e`, run by a reviewer agent in a fresh context, read-only.

## Scope
Four files, 5 lines changed: `CLAUDE.md`, `MAINTENANCE.md`, `README.md` and `site/generate.py` (the `id="whole-picture"` section of the home page). No files under `content/` changed. Built output checked: `site/index.html`.

## Evidence
- New home-page text: "The series follows one change through the lifecycle. The AI SDLC Map sets all of it on one page in five bands (context, lifecycle, core, enablement and assurance) with the adoption path, and links back to each part of this series." Button: "Open The AI SDLC Map". The link still points to `https://vishalkhondre.github.io/ai-sdlc-map/`.
- D-013 in `vishalkhondre/ai-sdlc-map` (`project/DECISIONS.md`) sets the name as The AI SDLC Map, keeps the URL and repository name, and rules out "AI SDLC on one page" as the site name.
- The map site describes itself as "One map in five bands (context, lifecycle, core, enablement and assurance) and an adoption path" and links to all seven series parts.
- `MAINTENANCE.md` lists cross-links to and from `ai-sdlc-map` as maintenance work, and tooling-only changes keep the edition. Commit eb5a97b added this section on the same basis; the edition is still 1.1.0.
- Validation on 797ff1e: `check_citations.py` passed; `release_content.py check` passed with no content changes; 32 unit tests OK; browser checks passed.

## Checks performed
1. Old name: gone from README, CLAUDE.md, MAINTENANCE.md, `generate.py` and `index.html`. The series' own diagram title "The AI SDLC on one page" remains; it names a series diagram from edition 1.1.0, not the companion site, and is outside what D-013 renames.
2. GR-3.1: the sentence is plain and present tense. "On one page" avoids "Map ... on one map" and matches the D-013 subtitle.
3. Accuracy: five bands, the adoption path and the links back to each part are confirmed on the map site's built pages.
4. GR-3.2: no provisional language; the only match was the search input's HTML `placeholder` attribute.
5. GR-1.1: the diff adds only the public site name.
6. Edition: `content/` is untouched and the change is a cross-link label, so tooling-only is correct.

## Blocking issues
None.

## Suggestions
- The series diagram titled "The AI SDLC on one page" shows on the References page next to a companion site now called The AI SDLC Map. Retitling it would be a content change (edition bump, changelog, review). Leaving it fits D-013 as written.
- Say in the PR that the change is tooling-only and the edition stays at 1.1.0.

Verdict: ACCEPT

# Editorial review: handover of ai-sdlc to ai-sdlc-map (eb5a97b)

## Scope

This review covers `git -C /home/user/ai-sdlc diff 4a997c8 eb5a97b` on branch `claude/hopeful-pasteur-7og55e`:

- the removal of `project/` (seven files);
- the new `MAINTENANCE.md`;
- the rewritten `CLAUDE.md`;
- the pointer added to `README.md`;
- the "See the whole picture" section added to `site/generate.py`, and how it renders in `site/index.html` (`#whole-picture`).

`content/`, `.github/`, `reviews/` and `scripts/` are unchanged. I checked the change against `/home/user/ai-sdlc-map/project/GROUND-RULES.md` and D-010, D-012 in `/home/user/ai-sdlc-map/project/DECISIONS.md`.

## Evidence revision

- **Series repository:** ai-sdlc at eb5a97b, base 4a997c8.
- **Map repository:** the local clone of ai-sdlc-map has `main` at 5647b45 and the working branch `claude/fix-search-race` at 1d4539b. Commit 076629f is not in the local clone, and the deployed URL could not be fetched from this sandbox (the egress proxy returned 403).
- **Map-site checks:** the claims about the map site were checked against the local source and the built output in `/home/user/ai-sdlc-map/site/`. That the site is live rests on the caller's deployment evidence.
- **Gate results:** the citation gate, the `release_content.py check --base 4a997c8` result, the unit tests and the browser checks were supplied by the caller. I did not re-run them.

## Findings checked

**Nothing needed for maintenance is lost:**
- `/home/user/ai-sdlc-map/project/` holds all seven files that were removed: AGENTS, APPROACH, ASSUMPTIONS, DECISIONS, GOAL, GROUND-RULES and STATUS.
- `GROUND-RULES.md` in ai-sdlc-map is byte-identical to the copy at 4a997c8.
- D-010 and D-012 are recorded in ai-sdlc-map.
- ai-sdlc-map's `CLAUDE.md` points back to this repository's `MAINTENANCE.md`.
- Nothing left in ai-sdlc still points to `project/` or to its files.

**MAINTENANCE.md is accurate:**
- `.github/prompts/update-content.prompt.md` exists and matches the description. It asks for an edition bump, a changelog entry and a recorded ACCEPT, and says tooling-only changes keep the edition.
- `scripts/release_content.py` has the `check` and `record-review` subcommands.
- `scripts/check_browser.py` exists, and `playwright` is in `scripts/requirements.txt`.
- The command list matches the validation list in ai-sdlc-map's `CLAUDE.md`.
- "D-012: ai-sdlc-map already uses a hashed deny-list" matches DECISIONS.md.
- The open item names files but not the keep-out names themselves.

**CLAUDE.md and README.md:**
- Both statements are accurate: new work happens in ai-sdlc-map, and that repository's `CLAUDE.md` and `project/` folder hold the goal, rules, status and decisions.
- Nothing still claims that this repository builds the map site. The old `CLAUDE.md` text ("This repository builds … AI SDLC on one page") is gone.

**Home-page section is accurate:**
- **Five bands:** the map site's `index.html` names the bands "context, lifecycle, core, enablement and assurance", the same set and order as the section.
- **Adoption path:** the map home page has an "The adoption path" section.
- **Links back to each part:** the map home page links to all seven parts of the series (`faster-coding-is-only-part`, `the-ai-sdlc`, `software-factory`, `harness-engineering`, `workflows`, `pull-request-verification`, `engineering-kit`). This matches the seven parts in `content/toc.yml`.

**Ground rules:**
- **GR-3.1 / GR-3.2 (voice):** the section is in the present tense and uses no first person or provisional language.
- **GR-3.3:** no product is named.
- **GR-4.3 (links):**
  - The new links are absolute links to the ai-sdlc-map site, which the caller reports as deployed.
  - No relative link was changed.
  - `rel="noopener"` is present.
- **GR-1:** the change adds no reference to the employer. `MAINTENANCE.md` deliberately leaves the protected names out.

## Blocking issues

None.

## Suggestions (non-blocking)

1. **Home-page edition.** `MAINTENANCE.md` says "reader-visible content changes need an edition bump". The new home-page section is visible to readers, but it lives in `site/generate.py`, so the content gate treats it as tooling and the edition stays 1.1.0. That fits the prompt's wording ("reader-visible *source* changes", meaning `content/`) and fits "cross-links … are maintenance". It is still worth one clarifying clause, for example "changes under `content/`", so a later maintainer does not read the rule as covering this kind of cross-link.
2. **Evidence trail.** Record the ai-sdlc-map commit that was deployed (076629f) in the PR description, or in ai-sdlc-map's `STATUS.md` session log. Neither local clone contains that commit, so the deployment claim cannot be traced from either repository alone.
3. **Pointer precision.** `MAINTENANCE.md` says the decision log "moved there from here". That is accurate, and the copy there has since grown (D-010 to D-012). Wording such as "which moved there from here and continue there" would make it clear that the copy in ai-sdlc-map is now the only one that is current.

Verdict: ACCEPT

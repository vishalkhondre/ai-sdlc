# Confirmation review: 1.1.0 reference updates (`dora-metrics`, `safe-framework`, `aicpa-soc2`)

## Scope

This review is limited to the change made after acceptance, on top of the accepted edition 1.1.0 review (`content/reviews/1.1.0-citation-review.md`, `Verdict: ACCEPT` at `e878d83`):

- **What changed:** three entries in `content/references.yml`: `dora-metrics`, `safe-framework` and `aicpa-soc2`. Each has a new URL, title and org, and a rewritten note. The `accessed` value stays at `2026-09-25`, and the "direct fetch blocked" YAML comments are removed.
- **What I checked:**
  1. GR-2.5 field completeness for the three entries.
  2. Whether each entry is internally consistent, and whether each note matches the diagram text that relies on it. That text is in `content/diagrams/svg/ai-sdlc-map.svg` and `content/diagrams/svg/ai-sdlc-adoption-path.svg`, both `<text>` and `<desc>`.
  3. Whether any reasoning in the earlier ACCEPT report no longer holds, including the CHANGELOG sentence.

Rules applied: `project/GROUND-RULES.md` (GR-2.5, GR-2.1, GR-2.2) and `.github/agents/citation-reviewer.agent.md`.

## Evidence (working tree on top of `e878d83`)

- **Revision:** HEAD is `e878d83`. `git status` shows `M content/references.yml` as the only tracked change. `content/release-review.json` and `content/reviews/` are untracked.
- **Diff:** `git diff e878d83 --stat` shows one file changed, `content/references.yml`, with 15 insertions and 15 deletions. The diff touches only the three entries in scope.
- **Gate output (supplied by the caller, exit 0; I did not run it):**
  `Citation check passed: 7 chapters, 12 citations, 34 terms, 11 references.`
  The counts match the output reported at `e878d83`. No keys were added or removed, so every `data-references` key still resolves (`aicpa-soc2`, `dora-metrics` and `safe-framework` on the map, `safe-framework` on the adoption path).
- **Live URL checks (reviewer step 3): all three fetches were blocked.**
  - `curl` got `CONNECT tunnel failed, response 403` and WebFetch got `EGRESS_BLOCKED` for:
    - `dora.dev`
    - `framework.scaledagile.com`
    - `www.aicpa-cima.com`
  - I could not confirm the titles, orgs or dates against the live pages.
  - As the caller instructed, I rely on the human author's recorded verification of all three pages, accessed 2026-09-25. The blocked fetch is not a blocker.

## Blocking issues

None. The change introduces no ground-rule violation.

### 1. GR-2.5 fields

All three entries record a title, an author and organisation, a URL and a date accessed:

| Key | Title | Author / org | URL | Accessed |
|---|---|---|---|---|
| `dora-metrics` | "DORA Research" | DORA (DevOps Research and Assessment) / Google, published on dora.dev | `https://dora.dev/research/` | 2026-09-25 |
| `safe-framework` | "Planning Interval (PI)" | Scaled Agile, Inc. / Scaled Agile Framework (SAFe), framework.scaledagile.com | `https://framework.scaledagile.com/planning-interval` | 2026-09-25 |
| `aicpa-soc2` | "2017 Trust Services Criteria (With Revised Points of Focus – 2022)" | AICPA & CIMA / AICPA Assurance Services Executive Committee (ASEC) | `https://www.aicpa-cima.com/resources/download/2017-trust-services-criteria-with-revised-points-of-focus-2022` | 2026-09-25 |

- The "direct fetch blocked" comments are gone. The `accessed` date now records the author's actual visit, which is what the earlier report asked for (its step 4).
- The org style "Google, published on dora.dev" matches the existing "Thoughtworks, published on martinfowler.com" pattern.

### 2. Internal consistency, and fit with the diagrams

**`dora-metrics`**
- Title, URL and org agree: a research overview page on dora.dev, under the program Google runs.
- The note ("The research program behind the DORA Core model and its software delivery performance metrics, which the map's measurement band points to") is accurate. It matches the map's Measurement card, "Flow metrics and DORA delivery metrics".
- The old claim "originally the four keys and now five" was never verified and is now gone. That removes a factual risk.

**`safe-framework`**
- Title, URL and org agree: SAFe's Planning Interval page.
- The note's first sentence is correct. In SAFe, PI planning, the system demo and Inspect & Adapt are all events of the Planning Interval. This matches:
  - on the map: "features · PI planning · system demo" (Agile Release Train row), "PI cadence, system demo, Inspect & Adapt" (Operating model) and "Inspect & Adapt each PI…";
  - on the adoption path: "Inspect & Adapt reviews which…", and its credit "Inspect & Adapt: SAFe term (Scaled Agile, Inc.)".
- The map `<desc>` phrase "PI a planning interval" now matches the cited page's own title exactly. This makes the earlier report's "SAFe 6.0 naming" check stronger.
- The second sentence attributes the portfolio, Agile Release Train and team levels and WSJF to SAFe as a framework, not to this page. It keeps the "one framework that uses these terms, not as a requirement" framing. This matches the map's "Portfolio … epics · WSJF · lean budgets" row, its `<desc>` ("SAFe levels (portfolio, Agile Release Train, team; WSJF…")") and the credit "Lifecycle terms: SAFe (Scaled Agile, Inc.)".

**`aicpa-soc2`**
- The title, the URL slug and the ASEC org agree. ASEC is the AICPA body that issues the Trust Services Criteria.
- The note ("The control criteria used in SOC 2 examinations, including the change-management criteria behind the map's SOC 2 change controls") is accurate. The TSC common criteria include change management (CC8.1). This matches the map's "SOC 2 change controls; domain standards as they apply".
- The rewrite also resolves suggestion 6 of the earlier report. SOC 2 is no longer called "the attestation framework"; the criteria are now correctly identified as the framework used in the examination.

### 3. Earlier report reasoning

- **Still holds:**
  - GR-2.1 backing for SAFe, DORA and SOC 2. The keys are unchanged.
  - The GR-2.2 credits, the `<desc>` accuracy findings and the GR-2.5 finding.
- **Superseded, and now better:**
  - The "Reference URL verification" section's statement that the `accessed` date reflects search results only, not a visit. It no longer applies.
  - Its checklist items are also superseded. Nothing that the checklist raised as a risk has turned into a problem:
    - The version question falls away because the title no longer names "SAFe 6.0".
    - The "four keys / five" claim was removed.
    - The SOC 2 landing-page URL was replaced by the criteria document.
- **CHANGELOG sentence** ("References added for DORA's software delivery metrics, SAFe and SOC 2, which the map names"): still accurate.
  - The three references still exist and are still cited for those three things. The `dora-metrics` note explicitly covers "its software delivery performance metrics", and the `aicpa-soc2` note ties the criteria to SOC 2 examinations.
  - The sentence describes what was added and why, not the page titles, so it needs no change.

## Suggestions (non-blocking)

1. **DORA page specificity.** The author asked for more specific pages, but for the metrics claim `https://dora.dev/research/` is broader than the previous `https://dora.dev/guides/dora-metrics/`. The map names "DORA delivery metrics", and a reader following the link lands on a research overview. The author has verified the page and the note describes it correctly, so this is only a reader-navigation point. If the metrics guide was also verified, it could be the URL, with the research page left to the note. Otherwise leave it as is.
2. **SAFe link coverage.** The cited page covers the PI events. The levels and WSJF are attributed to SAFe in general, and the note already makes that clear. No change is needed. A second entry (for example SAFe's WSJF page) would only be worth adding if a chapter later relies on those terms.
3. **WSJF origin (carried over from earlier suggestion 5, not introduced by this change).** "SAFe is also the source of … WSJF" is slightly imprecise, because WSJF comes from Reinertsen's work and SAFe adopted it. A wording such as "…and WSJF as SAFe uses it" would be more precise.
4. **Acceptance record needs refreshing (process, not content).** `content/release-review.json` pins `source_sha256` to the accepted sources. `scripts/release_content.py` checks that fingerprint, and the change to `references.yml` will almost certainly invalidate it. The caller should record acceptance again with the release script after this confirmation review, and should not edit the record by hand. The generated References page will pick up the new titles, orgs and URLs when `site/generate.py` runs in CI.
5. **Live link check.** GR-2.5 also says links are checked on every build. The new URLs could not be reached from this environment, so confirm that the build's link check passes for them.

Verdict: ACCEPT

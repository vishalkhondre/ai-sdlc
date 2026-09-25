# Citation review: content edition 1.1.0 (AI SDLC map and adoption-path diagrams)

## Scope

This review covers the `content/` changes from base `a695d54` (deployed main) to `e878d83`:

- `content/diagrams/svg/ai-sdlc-map.svg` (new, standalone, not embedded in any chapter)
- `content/diagrams/svg/ai-sdlc-adoption-path.svg` (new, standalone, not embedded in any chapter)
- `content/diagrams/map/build_map.py` (new generator for both SVGs)
- `content/references.yml` (new entries: `dora-metrics`, `safe-framework`, `aicpa-soc2`)
- `content/VERSION` (1.0.0 to 1.1.0) and `content/CHANGELOG.md` (1.1.0 entry and the reworded bump rule)

Rules applied: `project/GROUND-RULES.md` GR-1 to GR-4, the reviewer brief in `.github/agents/citation-reviewer.agent.md`, and decision `project/DECISIONS.md` D-009. D-009 allows a diagram credit line (`<text class="credit">`) to name a source product, as a chapter footnote may.

## Evidence revision

- Commit `e878d83` (HEAD, working tree clean), as stated by the caller.
- The caller supplied the gate output for `e878d83`, with exit code 0. I did not run the gate myself:
  `Citation check passed: 7 chapters, 12 citations, 34 terms, 11 references.`
- **What the PASS covers for diagrams** (from the `scripts/check_citations.py` docstring, checks 7 to 9):
  - Diagram `<text>`, `<title>` and `<desc>` contain no keep-out name or listed product name. Credit lines are checked against the keep-out list only.
  - Every `data-references` key resolves in `references.yml`.
  - A standalone diagram credits the source of every adopted or adapted glossary term. The term, or one of its `match:` phrases, is matched case-insensitively in the body text, and a credit line must carry that term's source key.
- **What the PASS does not cover:**
  - Borrowed vocabulary that has no glossary entry, such as SAFe terms.
  - Whether a visible credit exists for named frameworks. A key in the root `data-references` attribute is invisible to readers.
  - Accuracy of `<desc>` against sources, voice, unsourced claims, and the CHANGELOG.
  - GR-2.5 field completeness and link liveness.
  - The GR-1 deny-list, which is a separate check. No output from it was supplied.

  I reviewed all of these by hand below.

## Blocking issues

None. I found no ground-rule violation introduced by this change that a rule requires fixing before release.

The review found the following:

- **Borrowed glossary terms are all credited on the diagram that uses them (GR-2.2).**
  - *Map:*
    - "Harness engineering", "Feedback path" and "validators" are covered by the credit line `Harness engineering, feedback path and validators: after Böckeler (martinfowler.com)`, with keys `bockeler-harness bockeler-sensors`.
    - "Spec-driven development" is covered by `Spec-driven development: after GitHub Spec Kit`, with key `spec-kit`.
  - *Adoption path:*
    - "Feedback path", "validators" and "Review skill" are covered by `Feedback path, validators and review skills: after Böckeler (martinfowler.com)`.
  - The other glossary terms on the diagrams are `coined` or `common`: Engineering Kit, rule registry, evidence schema/record, deterministic floor, workflow, software factory, risk tier, could_not_run, thin adapters, skill erosion. "After" is a suitable credit for both the adopted and the adapted terms.
- **Every named framework or standard is backed by a `references.yml` entry (GR-2.1).**
  - SAFe is backed by `safe-framework` through the credit line.
  - DORA and SOC 2 are backed by `dora-metrics` and `aicpa-soc2` through the map's root `data-references`.
  - Spec Kit and Böckeler are backed by existing entries.
- **Product naming (GR-3.3).** No product names appear in body text. "GitHub Spec Kit" appears only in a credit line, which D-009 permits. MCP, SAFe, DORA, SOC 2, Scrum and Kanban are protocols, frameworks or standards, not products.
- **Voice and provisional language (GR-3.1, GR-3.2).**
  - There is no first person and no provisional language.
  - The specific numbers are labelled as recommendations, not findings, which GR-2.3 allows: "Suggested: 3–5 validators", "Suggested: run on 20+ real changes", "Suggested: each of the last three incidents".
- **The `<desc>` texts are accurate** against the visible content and the cited sources:
  - "PI a planning interval" matches SAFe 6.0's naming. This was corrected in `e878d83`.
  - The expansions are correct: WSJF (weighted shortest job first), HIL (hardware-in-the-loop), OTA (over-the-air) and MCP (Model Context Protocol).
  - "SOC 2 change controls" is consistent with the change-management criterion in the Trust Services Criteria (CC8).
  - Both descriptions summarise every band or stage and mention the credit lines.
- **GR-2.5.** All three new references record a title, an author and organisation, a URL and an `accessed` date.
- **The CHANGELOG entry is accurate.**
  - The five band names match the map.
  - Taken together, the credit attributions it lists match the credit lines on the two diagrams.
  - "Listed on the References page" matches the new `Diagrams` chips in `site/generate.py`. The adoption path is listed through its credit-line keys.
  - The reference sentence ("DORA's software delivery metrics, SAFe and SOC 2, which the map names") is correct.
  - A 1.1.0 minor bump is consistent with the reworded bump rule.

## Reference URL verification (reviewer step 3)

I could not verify any of the three new pages. All three fetches were refused by the network egress proxy (`EGRESS_BLOCKED` for `dora.dev`, `framework.scaledagile.com` and `www.aicpa-cima.com`). As instructed, this alone is not treated as a blocker.

Each entry's YAML comment also says the authoring session could not fetch the page directly. The `accessed: "2026-09-25"` date therefore records confirmation through search results, not an actual visit.

All three entries look plausible: the domains are the official ones, and the titles and orgs are consistent with each publisher. Before release, a human should open each URL and check:

1. **`dora-metrics`** — https://dora.dev/guides/dora-metrics/
   - Is the page title exactly "DORA's software delivery performance metrics"? Earlier versions were titled "…the four keys".
   - Does the page currently describe five metrics grouped as throughput and instability? The note claims "originally the four keys and now five".
2. **`safe-framework`** — https://framework.scaledagile.com/
   - Is SAFe **6.0** still the current version? The title says "SAFe 6.0". If a later version is live, update the title.
   - Is PI still expanded as "Planning Interval"?
   - Are Portfolio, Agile Release Train, Team, WSJF, lean budgets, PI planning, system demo, Inspect & Adapt and Built-in Quality all present?
3. **`aicpa-soc2`** — https://www.aicpa-cima.com/topic/audit-assurance/audit-and-assurance-greater-than-soc-2
   - Does the URL resolve without a redirect to a different page?
   - Does the page title match "SOC 2® — SOC for Service Organizations: Trust Services Criteria"?
   - Is AICPA & CIMA the publisher?
4. **For all three:** once a page has actually been opened, keep or update the `accessed` date and remove the "direct fetch blocked" comment. The recorded access date should then reflect a real visit.

## Suggestions (non-blocking)

1. **Built-in quality credit (GR-2.2, author's judgment).** The map's Core band caption opens with "Built-in quality:". This is a SAFe core-competency term, but the SAFe credit line reads "Lifecycle terms: SAFe", and this term sits outside the lifecycle band. The same applies to "PI cadence, system demo, Inspect & Adapt" in the Enablement band.
   - *Option A:* widen the credit to `SAFe terms: SAFe (Scaled Agile, Inc.)`.
   - *Option B:* add a `common` or `adopted` glossary entry so the gate can see these terms. No gate check applies today because they are not glossary terms.
2. **Visible credit for DORA and SOC 2 (GR-2.1).** On the map, `dora-metrics` and `aicpa-soc2` appear only in the root `data-references` attribute. A reader of the downloaded SVG sees the names but no pointer to the sources. Consider a short third credit line, for example `Delivery metrics: DORA · Change controls: SOC 2 (AICPA)`. This is optional: the names identify themselves, and the References page links them.
3. **Unsourced generalisation (GR-2.3, author's judgment).** Both the adoption-path footer and its `<desc>` say that skills, agents and platforms added early "tend to become the sprawl they were meant to prevent". "Tend to" reads as an empirical finding without a source. A recommendation register is safer, for example "Add skills, agents and platforms only after the floor and the first workflow exist."
4. **Product name in the CHANGELOG (GR-3.3, author's judgment).** The published CHANGELOG (`site/generate.py` reads it) says "GitHub Spec Kit for spec-driven development". This describes an attribution, as a footnote does. D-009 covers credit lines and footnotes but not the changelog. Either phrase it as "the Spec Kit reference", or extend D-009 to cover changelog attribution. The gate does not scan `CHANGELOG.md`.
5. **Unlisted SAFe and Scrum vocabulary (reviewer step 2).**
   - Definition of Ready / Definition of Done, WSJF, lean budgets and flow metrics are used without glossary entries.
   - They are widely used practitioner vocabulary; a `common` entry for DoR/DoD and a SAFe-attributed entry for WSJF and PI would let the gate police them.
   - A small precision point: WSJF comes from Reinertsen's work and was adopted by SAFe.
6. **`aicpa-soc2` note wording.** It calls SOC 2 "the attestation framework". SOC 2 is an attestation examination and report, and the Trust Services Criteria are the framework. Consider "The SOC 2 examination and its Trust Services Criteria, including change management…".
7. **Old reference entries (predates this change, GR-2.5).** Only the three new entries have an `accessed` field. The eight older entries in `content/references.yml` do not. The gate does not check GR-2.5 fields; consider adding the check (GR-5.3).
8. **Accessibility polish (GR-4.4).**
   - Both SVGs start with `<title>` and `<desc>`, which is a valid text alternative.
   - Adding `role="img"` and `aria-labelledby` pointing at them would improve screen-reader handling if the files are ever inlined.
   - They use a fixed white background, so they render the same in either site theme when opened as downloads.
9. **GR-1 evidence.** No deny-list (GR-1.1/1.3) output for `e878d83` was supplied, and this review cannot check hashed names. I saw nothing in the diagram text or `build_map.py` headers that looks like an employer, product or internal code. The domain examples (firmware/device, HIL, OTA) are generic industry vocabulary. Confirm that the deny-list check passed on this revision before release.

Verdict: ACCEPT

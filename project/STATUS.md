# Status

Update at the end of every session (see `CLAUDE.md`).

## Where things stand

- **Live (once the 1.1.0 PR merges and deploys):** release 1.1.0 — the 1.0.0 series plus two
  downloadable diagrams (the five-band map and the adoption path) and references for DORA, SAFe
  and SOC 2. Deployed from `main` via GitHub Actions; the Jekyll workflow was removed.
- **Review record:** `content/reviews/1.1.0-citation-review.md` (full review, ACCEPT on the fourth
  review) and `content/reviews/1.1.0-references-confirmation.md` (confirmation of the author's
  reference-URL change, ACCEPT; this is the report bound in `content/release-review.json`).
- **Current wave:** 0 Foundations — map labels neutral (Q1 applied to the map); diagram text now
  gated for keep-out and product names and for credits (D-009).

## Next (in order)

1. Author answers the open questions Q2–Q4 in `ASSUMPTIONS.md` (Q1 applied to the map in 1.1.0).
2. Replace the plain-text employer names in `scripts/check_citations.py` with a hashed deny-list
   (GR-1.4), as its own PR, and rewrite history if the author wants the old names gone.
3. Wave 0: page templates, agents and skills, new checks (banned phrases, template structure,
   link check, review-record gate).
4. Wave 0: source inventory — every library document mapped to map boxes, gaps listed.
5. Wave 0: clickable map as the home page with the purpose routing row.

## Wave 0 retrospective items

Raised during the 1.1.0 release; decide at the wave 0 retrospective (GR-5.3).

- **Enforce the GR-2.5 access date.** `check_citations.py` should fail a reference without an
  `accessed` date. Only the three 1.1.0 references have one; the eight older entries need
  backfilling, from a real visit, before the check can be switched on.
- **Add an outdated-terms check.** Review 3 caught "program increment" (SAFe 6.0 says planning
  interval) and the map had said "the four DORA keys" after DORA moved to five metrics. A
  maintained list of superseded terms, checked against prose and diagram text, would catch these.
- **Review rounds.** 1.1.0 took four reviews: the first two REVISE on credits and product names,
  which the new diagram checks (D-009) now catch; the third REVISE on accuracy and GR-2.5. Each
  fresh reviewer found new issues rather than repeating old ones. Consider a reviewer checklist
  generated from the ground rules so a first review covers everything once.
- **Open review suggestions, not acted on in 1.1.0:** wider SAFe credit (built-in quality, PI
  cadence); visible DORA / SOC 2 credit line; "tend to become the sprawl" reads as an unsourced
  finding; product name in the changelog (extend D-009 or reword); glossary entries for DoR/DoD,
  WSJF (Reinertsen via SAFe) and flow metrics; `role="img"` / `aria-labelledby` if diagrams are
  ever inlined; DORA metrics guide as a more specific link than the research page.

## Wave tracker

| Wave | State | Pages planned | Pages published |
|---|---|---|---|
| 0 Foundations | not started | — | — |
| 1 Core and lifecycle | not started | set by inventory | 0 |
| 2 Assurance and enablement | not started | set by inventory | 0 |
| 3 Context and adoption | not started | set by inventory | 0 |

## Session log

| # | Date | What happened | Handover |
|---|---|---|---|
| 1 | 2026-09-25 | Built and released 1.0.0; drew the five-band map and adoption path; reviewed the Hopsworks landing pattern; agreed the goal, ground rules and approach; wrote these project files | Two map commits and this commit need pushing; session could not push (repo not selected at start) |
| 2 | 2026-09-25 | Pushed 1.0.0 to GitHub and applied the publishing-and-review-gates patch; removed the Jekyll workflow; merged the map bundle; released 1.1.0 after four citation reviews (REVISE ×3, ACCEPT) plus a confirmation review of the author's reference URLs; diagram text checks and credit lines added (D-009) | Branch `claude/hopeful-pasteur-7og55e` deleted after merge; retrospective items above |

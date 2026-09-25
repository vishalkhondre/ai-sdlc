# Status

Update at the end of every session (see `CLAUDE.md`).

## Where things stand

- **Live:** release 1.0.0 — the seven-part series, workflow catalog (35 workflows), glossary,
  references, Part 7 reference sheet. Deployed from `main` via GitHub Actions.
- **Committed but not pushed:** `dd089cf` (one-page map) and `76d0756` (five-band redraw and
  adoption path). Available as `ai-sdlc-map-update.bundle` from session 1.
- **Current wave:** 0 Foundations — not started beyond these project files.

## Next (in order)

1. Author confirms the ground rules and answers the open questions Q1–Q4 in `ASSUMPTIONS.md`.
2. Push the unpushed commits and these project files from a session with the repo selected.
3. Delete the stale branch `claude/hopeful-pasteur-7og55e`.
4. Replace the plain-text employer names in `scripts/check_citations.py` with a hashed deny-list
   (GR-1.4) and rewrite history if the author wants the old names gone from past commits.
5. Wave 0: page templates, agents and skills, new checks (banned phrases, template structure,
   link check, review-record gate).
6. Wave 0: source inventory — every library document mapped to map boxes, gaps listed.
7. Wave 0: neutral labels on the map (per Q1); clickable map as the home page with the purpose
   routing row.

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

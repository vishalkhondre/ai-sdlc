# Assumptions and open questions

An assumption is held true until evidence or the author says otherwise. When one changes,
record it in `DECISIONS.md`.

## Assumptions

- **A1 Audience.** Practitioners and leaders in organisations of any size; familiarity with
  agile delivery and CI/CD is assumed, familiarity with AI agents is not.
- **A2 Scope.** The five-band map (as of commit `76d0756`) is the agreed scope. New boxes are
  added only through the architect agent with the author's approval.
- **A3 Source library.** The author's private Google Drive folder `ai-sdlc` is the source of
  practice experience: a delivery framework, executive and organisation-wide summaries, a
  delivery package, runbooks and playbooks. It is reachable only through the Google Drive
  connector in Claude sessions. It is internal material and falls under GR-1 in full.
- **A4 Public evidence exists** for most practices on the map. Where it does not, the page
  presents recommended practice (GR-2.3) rather than dropping the topic.
- **A5 Tooling.** The existing generator (Python, Markdown, YAML, inline SVG, vanilla JS) scales
  to the full site without a framework change.
- **A6 Hosting.** GitHub Pages via GitHub Actions from `main`.
- **A7 Sessions.** Work spans many sessions. Continuity lives in this folder, not in any
  session's memory.
- **A8 Push access.** A session can push only if `vishalkhondre/ai-sdlc` was selected when the
  session started. Otherwise work is handed over as a git bundle.

## Open questions (need the author)

- **Q1 Vendor names on the map.** Proposed: generic labels on the map ("SDD framework",
  "work tracker", "iteration method"); named tools only on category pages, as examples.
- **Q2 Approval after wave 1.** Proposed: author approves every wave 1 page; agent-only
  approval for small edits from wave 2, if the retrospective supports it.
- **Q3 SAFe on the map.** Proposed: keep portfolio / train / team as the lifecycle levels,
  labelled generically, with SAFe cited as one framework that uses them.
- **Q4 Release versioning.** Proposed: the site moves to 2.0.0 when every map box links to a
  published page; waves ship as 1.x minor releases in between.

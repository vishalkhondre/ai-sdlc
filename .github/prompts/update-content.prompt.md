---
description: Research, author, verify and review a scoped update to Beyond Faster Coding.
---
# Update content

1. Read the requested scope, repository instructions and git status. Preserve unrelated
   work. Record the exact base commit, intended change and affected chapter/term/workflow
   IDs. Work on a feature branch and keep one writer per file.
2. Use content-researcher's responsibilities to gather an evidence brief, then
   content-author's responsibilities to update affected sources. These roles can be
   performed sequentially; do not launch agents merely because their files exist.
3. Have the command-capable caller run the citation gate, generator, diagram renderer,
   site tests and browser checks documented in README.md. Supply actual command output
   and the source fingerprint to citation-reviewer. Missing execution is a blocker,
   not a pass. Revise and rerun relevant checks until blockers are closed.
4. For reader-visible source changes choose the prose edition (patch corrections,
   minor additions, major restructuring), update VERSION and CHANGELOG.md, then obtain
   the final review of those exact sources. Save the real report under
   content/reviews/<edition>-<revision>.md. Include scope, source fingerprint,
   evidence, findings and exactly one standalone Verdict: ACCEPT or Verdict: REVISE.
5. Only after an actual ACCEPT, run:
   `python scripts/release_content.py record-review --report content/reviews/<report>.md`
   Then run `python scripts/release_content.py check --base <base-commit>`.
   A changed manuscript, diagram, catalog, version, changelog or report requires renewed
   review. Do not fabricate approval to satisfy a gate.
6. Prepare a PR describing changes, evidence and limitations. Human review and merge
   remain the publishing boundary. Do not merge or dispatch deployment as part of this
   prompt. Tooling-only changes keep the prose edition and need no new content report.

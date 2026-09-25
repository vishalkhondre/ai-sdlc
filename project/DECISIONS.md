# Decision log

Newest last. Each entry: what was decided, why, and what it rules out. Reopen only with the
author.

## D-001 · Independent, public work
The site is the author's independent work. It carries no reference to any employer or its
internal work. Rules out: case studies, internal names, internal numbers (GR-1).

## D-002 · Title, home and licences
"Beyond Faster Coding", hosted at `vishalkhondre.github.io/ai-sdlc`. Prose CC BY 4.0, tooling
MIT. The web edition may diverge from the LinkedIn text.

## D-003 · The one-page map is the site's front door
The five-band AI SDLC map becomes the landing page with every box clickable, following the
Hopsworks documentation overview pattern. The seven-part series stays as the narrative
introduction. Rules out: a blog-style home page.

## D-004 · Claude Code agents, not GitHub Copilot agents
The source library is reachable only through the Google Drive connector in Claude sessions.
Rules out: a Copilot-only agent fleet for research. CI stays GitHub Actions.

## D-005 · Private sources never enter the repo
Practice briefs drawn from the library live only in session scratch space and are discarded.
Only de-identified, rewritten pages are committed. Rules out: a `content/sources/` folder of
extracts.

## D-006 · Reviewer gate enforced in CI
Every published page needs a review record with ACCEPT from the confidentiality, accuracy and
editorial reviewers, tied to the page hash. Rules out: publishing on author judgment alone
without a record.

## D-007 · Reference register, complete pages only
No provisional language on the site; unwritten map boxes appear as plain labels. Rules out:
"coming soon" markers and partial pages.

## D-008 · Diagrams as code, vendor-neutral
All diagrams are generated from source, with text alternatives. Tool names appear only as
examples on category pages.

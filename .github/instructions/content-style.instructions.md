---
applyTo: "content/**"
---
# Content rules for Beyond Faster Coding

These apply to any person or agent editing `content/`.

## Voice
- Plain practitioner English. No consultant, marketing or "AI thought-leadership" tone.
- Third person. No "I", no "we" describing an organisation's internal progress.
- No invented anecdotes, metrics, outcomes or company practices. Hypotheticals are labelled as such.
- Uncertainty stays visible. Each part ends with what remains open.
- Avoid: "game changer", "unlock", "revolutionize", "transformative", "paradigm shift", "at its core", "here's the thing", bold pull-quote sentences.

## Neutrality
- Vendor and tool neutral in chapter prose: execution surface, change host, pipeline runner, agentic IDE, coding agent.
  `scripts/check_citations.py` fails the build on names from its keep-out list.
- No employer, client or internal-programme names anywhere in the site.

## Citations
- A term that is `adopted` or `adapted` in `content/glossary.yml` must name a `source` in `content/references.yml`.
- Every chapter listed under such a term must cite that source at least once (a `[^key]` footnote or a note linking its URL).
- New references go in `references.yml` first; chapters cite them as `[^key]`.

## Diagrams
- Diagrams are code: hand-authored SVG in `content/diagrams/svg/`, or the Part 7 generators in `content/diagrams/p7/`.
- Embed with `![caption](diagram:<id>)`. PNGs are build output, never committed.
- One palette: purple = agent, coral = checks / blocked, teal = people / passing, grey = project meaning.

## Versioning
- `content/VERSION` is the prose edition (semver). Bump it and add a `CHANGELOG.md` entry for reader-visible changes only.

# Beyond Faster Coding

**Harness engineering, the Engineering Kit, workflows and the software factory: a seven-part series on what has to change around the coding agent.**

Read it at **https://vishalkhondre.github.io/ai-sdlc/**

The series is complete and maintained only; see [`MAINTENANCE.md`](MAINTENANCE.md). The whole
picture, *AI SDLC on one page*, is built in
[`vishalkhondre/ai-sdlc-map`](https://github.com/vishalkhondre/ai-sdlc-map) and published at
<https://vishalkhondre.github.io/ai-sdlc-map/>.

| Part | Title |
|---|---|
| 1 | Faster coding is only part of the software delivery problem |
| 2 | The AI SDLC: same phases, different bottleneck |
| 3 | Harness engineering in the SDLC: designing the environment around the agent |
| 4 | Engineering Kit: packaging the reusable engineering environment |
| 5 | Workflows: making one part of the SDLC repeatable, measurable and improvable |
| 6 | Software factory: connecting workflows across delivery and operations |
| 7 | One workflow in full: pull-request verification |

Beyond the articles, the site has:

- **SDLC workflow catalog**: 35 workflows across eight phases, each mapped one-to-one to the traditional activity it absorbs (123 activities from seven reference models), filterable by phase, maturity and change type.
- **Pull-request verification reference sheet**: the Part 7 images in a worked-example version and a generic template with identical layouts, plus a 9-page PDF.
- **Terminology and sources**: every term, marked as adopted, adapted, coined or common, with a translation table to Birgitta Böckeler's harness-engineering vocabulary on martinfowler.com.

## How it is built

```
content/
  toc.yml               chapters and site identity (source of truth)
  chapters/*.md         the seven parts, Markdown with [^ref] footnotes and ![..](diagram:id) embeds
  glossary.yml          terms, attribution (adopted / adapted / coined / common), sources
  references.yml        canonical references
  workflows/catalog.yml the workflow catalog and traditional-activity map
  diagrams/svg/         hand-authored SVG diagrams
  diagrams/p7/          Part 7 generators: one layout, two label sets (generic + worked example)
  VERSION, CHANGELOG.md prose edition
site/
  generate.py           content/ -> static HTML (inline SVG, no framework, no external requests)
  assets/               one CSS file, one JS file
scripts/
  check_citations.py    the attribution and neutrality gate
  render_diagrams.py    SVG -> PNG (LinkedIn / OG sizes) and the reference-sheet PDF
  release_content.py    edition/changelog validation and source-bound editorial acceptance
  check_browser.py      browser regressions for navigation, catalog, copy and zoom
  tests/                site, citation and release regression tests
.github/
  workflows/            validate on every PR; deploy to GitHub Pages from main
  instructions/         content rules for people and agents
  agents/               content-researcher, content-author, citation-reviewer
  prompts/              scoped content updates and release preparation
```

The build checks the glossary's declared attribution-to-chapter mappings, footnote references,
diagram IDs and the prose keep-out list. Canonical reference keys cannot be overridden by
chapter-local notes. These checks do not discover every borrowed idea or establish that a
source supports a claim; the citation reviewer handles that editorial judgment.

## Run locally

```bash
pip install -r scripts/requirements.txt
python -m playwright install chromium     # only for PNG/PDF rendering
python scripts/check_citations.py
python site/generate.py
python scripts/render_diagrams.py
python -m unittest discover -s scripts/tests
python scripts/check_browser.py           # requires Chromium; also enforced in CI
python -m http.server -d site 8000        # http://localhost:8000
```

## Publishing

In the repository settings, set **Pages → Source** to **GitHub Actions**. Every push to `main` runs the gate, builds the site and deploys it.

### Content authoring and review

Use `.github/prompts/update-content.prompt.md` for a bounded change. The researcher
supplies primary-source evidence; the author updates the sources; the citation reviewer
checks attribution, voice and the caller's actual verification output. Work through
research → author → verify → review → revise, then prepare a PR. Roles can run sequentially.

For reader-visible changes under `content/`:

1. Capture the base commit before editing (`git rev-parse HEAD`).
2. Update `content/VERSION` (MAJOR.MINOR.PATCH) and add a nonempty changelog entry.
   Patches correct content, minor editions add material, major editions restructure it.
3. Run the build/checks above. Obtain a real final review covering the exact sources,
   including version and changelog. Save it under `content/reviews/<edition>-<revision>.md`,
   with scope, source fingerprint, evidence, findings and one `Verdict: ACCEPT` or
   `Verdict: REVISE` line. `python scripts/release_content.py fingerprint` gives the fingerprint.
4. Only after ACCEPT, record and check it:

   ```bash
   python scripts/release_content.py record-review --report content/reviews/<report>.md
   python scripts/release_content.py check --base <base-commit>
   ```

The record binds both source and report hashes. Subsequent changes invalidate it and
require renewed review; recording a hash is not proof of a person's identity or approval.
Commit the report and `content/release-review.json` with the content changes. The
release-content prompt prepares the PR; human review and merge precede deployment.

CI compares PRs with their base SHA and pushes with their preceding SHA. Manual runs
compare with the preceding commit. Tooling-only changes must keep the prose edition.
Existing content from before this gate needs no retroactive acceptance record, but its
next source change requires a version bump and actual review. No acceptance record is
pre-populated by the tooling. GitHub branch protection must separately require validation
and reviewer approval if those controls should prevent direct pushes to `main`.

## Credits

The harness-engineering vocabulary this series builds on comes from Birgitta Böckeler, [Harness Engineering for Coding Agent Users](https://martinfowler.com/articles/harness-engineering.html) and [Maintainability Sensors for Coding Agents](https://martinfowler.com/articles/sensors-for-coding-agents.html) (Thoughtworks, on martinfowler.com), and from OpenAI's [Harness engineering](https://openai.com/index/harness-engineering/). See the site's Terminology page for exactly which terms are adopted, adapted or coined.

The site structure (content as source of truth, deterministic generator, CI gate) follows the pattern of [webmaxru/github-agentic-workflows-book](https://github.com/webmaxru/github-agentic-workflows-book).

## Licence

Prose, diagrams and data: CC BY 4.0. Tooling: MIT. See [LICENSE](LICENSE).

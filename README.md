# Beyond Faster Coding

**Harness engineering, the Engineering Kit, workflows and the software factory: a seven-part series on what has to change around the coding agent.**

Read it at **https://vishalkhondre.github.io/ai-sdlc/**

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
  tests/                site build tests
.github/
  workflows/            validate on every PR; deploy to GitHub Pages from main
  instructions/         content rules for people and agents
  agents/               citation-reviewer
```

The build refuses to publish when a chapter uses someone else's term without citing them, a footnote has no reference, a diagram id does not exist, or a keep-out name appears in the prose.

## Run locally

```bash
pip install -r scripts/requirements.txt
python -m playwright install chromium     # only for PNG/PDF rendering
python scripts/check_citations.py
python site/generate.py
python scripts/render_diagrams.py
python -m unittest discover -s scripts/tests
python -m http.server -d site 8000        # http://localhost:8000
```

## Publishing

In the repository settings, set **Pages → Source** to **GitHub Actions**. Every push to `main` runs the gate, builds the site and deploys it.

## Credits

The harness-engineering vocabulary this series builds on comes from Birgitta Böckeler, [Harness Engineering for Coding Agent Users](https://martinfowler.com/articles/harness-engineering.html) and [Maintainability Sensors for Coding Agents](https://martinfowler.com/articles/sensors-for-coding-agents.html) (Thoughtworks, on martinfowler.com), and from OpenAI's [Harness engineering](https://openai.com/index/harness-engineering/). See the site's Terminology page for exactly which terms are adopted, adapted or coined.

The site structure (content as source of truth, deterministic generator, CI gate) follows the pattern of [webmaxru/github-agentic-workflows-book](https://github.com/webmaxru/github-agentic-workflows-book).

## Licence

Prose, diagrams and data: CC BY 4.0. Tooling: MIT. See [LICENSE](LICENSE).

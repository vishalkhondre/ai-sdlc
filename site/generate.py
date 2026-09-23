"""Generate the Beyond Faster Coding site from content/.

Source of truth:
  content/toc.yml            chapters, appendices, site identity
  content/chapters/*.md      chapter prose (Markdown, footnotes as [^ref-key])
  content/glossary.yml       terms, attribution, sources, auto-link phrases
  content/references.yml     canonical references
  content/workflows/catalog.yml   the SDLC workflow catalog
  content/diagrams/svg/*.svg      diagram sources (hand-authored SVG)
  content/diagrams/p7/*.py        Part 7 image generators (one layout, two label sets)

Output: site/ (static HTML, inline SVG, one CSS file, one JS file).
Run:    python site/generate.py
"""
from __future__ import annotations

import html
import importlib.util
import json
import math
import re
import sys
from datetime import date
from pathlib import Path

import markdown
import yaml

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
SITE = ROOT / "site"
DIAGRAMS_SVG = CONTENT / "diagrams" / "svg"
P7_DIR = CONTENT / "diagrams" / "p7"
OUT_DIAGRAMS = SITE / "diagrams"

TOC = yaml.safe_load((CONTENT / "toc.yml").read_text(encoding="utf-8"))
GLOSSARY = yaml.safe_load((CONTENT / "glossary.yml").read_text(encoding="utf-8"))
REFERENCES = yaml.safe_load((CONTENT / "references.yml").read_text(encoding="utf-8"))
CATALOG = yaml.safe_load((CONTENT / "workflows" / "catalog.yml").read_text(encoding="utf-8"))
VERSION = (CONTENT / "VERSION").read_text(encoding="utf-8").strip()
CHANGELOG = (CONTENT / "CHANGELOG.md").read_text(encoding="utf-8")

SITE_URL = TOC["site_url"].rstrip("/")
TITLE = TOC["title"]
CHAPTERS = TOC["chapters"]
BY_ID = {c["id"]: c for c in CHAPTERS}
TODAY = date.today().isoformat()

GLOSS_BY_ID = {g["id"]: g for g in GLOSSARY}


def esc(s) -> str:
    return html.escape(str(s), quote=True)


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def write(p: Path, s: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(s, encoding="utf-8")


# --------------------------------------------------------------------------- diagrams
def svg_source(diagram_id: str, instance: str) -> tuple[str, int, int]:
    """Return (svg markup, width, height) for a diagram id."""
    p = DIAGRAMS_SVG / f"{diagram_id}.svg"
    if p.exists():
        svg = read(p)
    elif diagram_id.startswith("p7-"):
        svg = P7_SVGS[diagram_id]
    else:
        raise SystemExit(f"Unknown diagram: {diagram_id}")
    m = re.search(r'<svg[^>]*width="(\d+)"[^>]*height="(\d+)"', svg)
    w, h = (int(m.group(1)), int(m.group(2))) if m else (1200, 628)
    # Namespace definitions per occurrence, including repeats and Part 7 markers.
    id_map = {old: f"{instance}-{old}" for old in re.findall(r'\bid="([^"]+)"', svg)}
    svg = re.sub(r'\bid="([^"]+)"', lambda m: f'id="{id_map[m.group(1)]}"', svg)
    svg = re.sub(r'url\(#([^)]+)\)', lambda m: f'url(#{id_map.get(m.group(1), m.group(1))})', svg)
    svg = re.sub(r'((?:xlink:)?href=")#([^"]+)(")',
                 lambda m: m.group(1) + '#' + id_map.get(m.group(2), m.group(2)) + m.group(3), svg)
    # scope the style rules to this svg only
    svg = re.sub(r"<style>(.*?)</style>", lambda mm: "<style>" + scope_css(mm.group(1), instance) + "</style>", svg, flags=re.S)
    svg = svg.replace("<svg ", f'<svg id="svg-{instance}" role="img" aria-labelledby="cap-{instance}" ', 1)
    return svg, w, h


def scope_css(css: str, scope: str) -> str:
    out = []
    for rule in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
        selectors, body = rule
        sels = []
        for sel in selectors.split(","):
            sel = sel.strip()
            if not sel or sel == "body":
                continue
            sels.append(f"#svg-{scope} {sel}")
        if sels:
            out.append(",".join(sels) + "{" + body + "}")
    return "".join(out)


def load_p7() -> dict[str, str]:
    """Run the Part 7 generators and return {diagram_id: standalone svg}."""
    sys.path.insert(0, str(P7_DIR))
    svgs: dict[str, str] = {}
    common = importlib.import_module("common")
    for n in range(1, 6):
        spec = importlib.util.spec_from_file_location(f"img{n}", P7_DIR / f"img{n}.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        variants = ("generic",) if n == 5 else ("generic", "export")
        for v in variants:
            page = mod.build(v)
            m = re.search(r"(<svg.*</svg>)", page, re.S)
            svg = m.group(1)
            style = f"<style>{common.STYLE}</style>"
            svg = svg.replace(">", ">" + style, 1)
            svg = svg.replace('<svg width', '<svg xmlns="http://www.w3.org/2000/svg" width', 1) if "xmlns" not in svg[:200] else svg
            name = {1: "kit-touched", 2: "run", 3: "exits", 4: "flows", 5: "measures"}[n]
            svgs[f"p7-{n}-{name}-{v}"] = svg
    return svgs


P7_SVGS = load_p7()


def write_diagram_files() -> list[str]:
    """Write every diagram as a standalone .svg into site/diagrams (PNG rendering is scripts/render_diagrams.py)."""
    OUT_DIAGRAMS.mkdir(parents=True, exist_ok=True)
    ids = []
    for p in sorted(DIAGRAMS_SVG.glob("*.svg")):
        write(OUT_DIAGRAMS / p.name, read(p))
        ids.append(p.stem)
    for did, svg in P7_SVGS.items():
        write(OUT_DIAGRAMS / f"{did}.svg", svg)
        ids.append(did)
    return ids


def figure(diagram_id: str, caption: str, number: int | None = None, cls: str = "") -> str:
    count = _FIGURE_COUNTS.get(diagram_id, 0) + 1
    _FIGURE_COUNTS[diagram_id] = count
    instance = f"{diagram_id}-{count}"
    svg, w, h = svg_source(diagram_id, instance)
    label = f"Figure {number}. " if number else ""
    return (
        f'<figure class="diagram {cls}" data-diagram="{diagram_id}" style="--ar:{w}/{h}">'
        f'<div class="diagram-frame"><button class="zoom" type="button" aria-label="Open diagram full size" data-zoom="{diagram_id}">⤢</button>{svg}</div>'
        f'<figcaption id="cap-{instance}"><span class="fig-label">{label}</span>{esc(caption)}'
        f' <span class="fig-links"><a href="{rel("diagrams/" + diagram_id + ".svg")}" download>SVG</a> · <a href="{rel("diagrams/" + diagram_id + ".png")}" download>PNG</a></span></figcaption>'
        f"</figure>"
    )


# --------------------------------------------------------------------------- paths
_PREFIX = ""
_FIGURE_COUNTS: dict[str, int] = {}


def set_prefix(p: str) -> None:
    global _PREFIX
    _PREFIX = p
    _FIGURE_COUNTS.clear()


def rel(path: str) -> str:
    return _PREFIX + path


# --------------------------------------------------------------------------- markdown
MD_EXT = ["extra", "toc", "sane_lists", "codehilite"]
MD_CFG = {"toc": {"toc_depth": "2-3", "permalink": False}, "codehilite": {"guess_lang": False, "css_class": "hl"}}


def ref_footnote(key: str) -> str:
    r = REFERENCES[key]
    bits = [f"<strong>{esc(r['title'])}</strong>"]
    who = ", ".join(x for x in [r.get("author"), r.get("org")] if x)
    if who:
        bits.append(esc(who))
    if r.get("date"):
        bits.append(esc(r["date"]))
    line = " — ".join(bits)
    if r.get("url"):
        line += f' · <a href="{esc(r["url"])}" rel="noopener">source</a>'
    if r.get("note"):
        line += f" <span class=\"ref-note\">{esc(r['note'])}</span>"
    return line


def preprocess_markdown(md: str, chapter_id: str) -> tuple[str, list[str], list[str]]:
    """Resolve diagram embeds and add reference footnote definitions.

    Returns (markdown, diagram ids used in order, footnote keys used).
    """
    diagrams: list[str] = []

    def fig_sub(m: re.Match) -> str:
        diagrams.append(m.group(2))
        n = len(diagrams)
        return f"\n\n<!--FIG:{m.group(2)}|{n}|{m.group(1)}-->\n\n"

    md = re.sub(r"!\[([^\]]*)\]\(diagram:([a-z0-9\-]+)\)", fig_sub, md)
    used = sorted(set(re.findall(r"\[\^([a-z0-9\-]+)\](?!:)", md)))
    defined = set(re.findall(r"^\[\^([a-z0-9\-]+)\]:", md, flags=re.M))
    overrides = defined & REFERENCES.keys()
    if overrides:
        raise SystemExit(f"{chapter_id}: canonical reference keys cannot be redefined locally: {', '.join(sorted(overrides))}")
    extra = []
    for key in used:
        if key in defined:
            continue
        if key not in REFERENCES:
            raise SystemExit(f"{chapter_id}: footnote [^{key}] has no definition and is not in references.yml")
        extra.append(f"[^{key}]: {ref_footnote(key)}")
    if extra:
        md += "\n\n" + "\n".join(extra) + "\n"
    return md, diagrams, used


def render_markdown(md: str) -> tuple[str, list[dict]]:
    m = markdown.Markdown(extensions=MD_EXT, extension_configs=MD_CFG)
    body = m.convert(md)
    toc = [t for t in m.toc_tokens if t["level"] == 2] if hasattr(m, "toc_tokens") else []
    return body, toc


def autolink_terms(body: str, chapter_id: str) -> tuple[str, list[str]]:
    """Link the first occurrence of each glossary phrase in the running prose."""
    linked: list[str] = []
    # split into segments we may touch (text nodes outside tags/headings/links/code)
    protected = re.compile(r"(<(?:h[1-6]|a|code|pre|figure|sup|strong)\b[^>]*>.*?</(?:h[1-6]|a|code|pre|figure|sup|strong)>|<[^>]+>)", re.S)
    parts = protected.split(body)
    for g in GLOSSARY:
        phrases = g.get("match") or []
        if not phrases:
            continue
        done = False
        for i, part in enumerate(parts):
            if done or not part or part.startswith("<"):
                continue
            for phrase in phrases:
                pat = re.compile(r"(?<![\w-])(" + re.escape(phrase) + r")(?![\w-])")
                if pat.search(part):
                    parts[i] = pat.sub(
                        lambda mm: f'<a class="term" href="{rel("glossary.html")}#{g["id"]}" data-term="{g["id"]}">{mm.group(1)}</a>',
                        part, count=1)
                    linked.append(g["id"])
                    done = True
                    break
    return "".join(parts), linked


def reading_minutes(text: str) -> int:
    words = len(re.findall(r"\w+", text))
    return max(1, math.ceil(words / 220))


# --------------------------------------------------------------------------- page chrome
def head(title: str, description: str, path: str, og_image: str = "og-image.png", extra: str = "") -> str:
    canonical = f"{SITE_URL}/{path}" if path != "index.html" else f"{SITE_URL}/"
    return f"""<!DOCTYPE html>
<html lang="en" data-theme="auto">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="article">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:image" content="{SITE_URL}/{og_image}">
<meta property="og:url" content="{canonical}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#f6f4ee" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#14130f" media="(prefers-color-scheme: dark)">
<link rel="icon" href="{rel('favicon.svg')}" type="image/svg+xml">
<link rel="stylesheet" href="{rel('assets/style.css')}?v={VERSION}">
<script>try{{const t=localStorage.getItem('bfc-theme');if(t)document.documentElement.dataset.theme=t;}}catch(e){{}}</script>
{extra}
</head>
"""


def nav(current: str = "") -> str:
    def item(href: str, label: str, key: str) -> str:
        cls = ' class="on"' if key == current else ""
        return f'<a href="{rel(href)}"{cls}>{label}</a>'

    return f"""<header class="topbar">
<div class="topbar-inner">
<a class="brand" href="{rel('index.html')}"><span class="brand-mark" aria-hidden="true"></span><span>{esc(TITLE)}</span></a>
<nav class="topnav" aria-label="Site">
{item('index.html#series', 'Series', 'series')}
{item('workflow-catalog.html', 'Workflow catalog', 'workflows')}
{item('pr-verification-reference.html', 'Reference sheet', 'reference')}
{item('glossary.html', 'Terminology', 'glossary')}
<button class="iconbtn" id="search-open" type="button" aria-label="Search (press /)"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg></button>
<button class="iconbtn" id="theme-toggle" type="button" aria-label="Toggle colour theme"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3a9 9 0 1 0 9 9c0-.5 0-1-.1-1.4A5.5 5.5 0 0 1 12 3z"/></svg></button>
<button class="iconbtn menu" id="menu-toggle" type="button" aria-label="Menu" aria-expanded="false"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 7h16M4 12h16M4 17h16"/></svg></button>
</nav>
</div>
<div class="progress" id="progress" aria-hidden="true"><span></span></div>
</header>
"""


def footer() -> str:
    return f"""<footer class="footer">
<div class="footer-inner">
<div>
<div class="footer-title">{esc(TITLE)}</div>
<div class="muted">A seven-part series by <a href="{esc(TOC['author_url'])}" rel="noopener">{esc(TOC['author'])}</a>. Edition {esc(VERSION)}. Prose <a href="https://creativecommons.org/licenses/by/4.0/" rel="noopener">CC BY 4.0</a>; site tooling MIT.</div>
</div>
<div class="footer-links">
<a href="{rel('index.html#series')}">Series</a>
<a href="{rel('workflow-catalog.html')}">Workflow catalog</a>
<a href="{rel('pr-verification-reference.html')}">Reference sheet</a>
<a href="{rel('glossary.html')}">Terminology</a>
<a href="{rel('references.html')}">References</a>
<a href="{esc(TOC['repo_url'])}" rel="noopener">Source</a>
<a href="{rel('llms.txt')}">llms.txt</a>
</div>
</div>
</footer>
<div class="lightbox" id="lightbox" hidden><button class="lightbox-close" type="button" aria-label="Close">×</button><div class="lightbox-body"></div></div>
<div class="search" id="search" hidden><div class="search-box"><input id="search-input" type="search" placeholder="Search the series…" autocomplete="off"><div id="search-results" class="search-results"></div><div class="search-hint">Type to search chapters, terms and workflows. <kbd>Esc</kbd> closes.</div></div></div>
<div class="tip" id="tip" role="tooltip" hidden></div>
<script src="{rel('assets/app.js')}?v={VERSION}"></script>
"""


def glossary_json() -> str:
    data = {g["id"]: {"term": g["term"], "def": g["definition"].strip(), "attr": g["attribution"], "src": g.get("source")} for g in GLOSSARY}
    return f'<script id="glossary-data" type="application/json">{json.dumps(data)}</script>'


# --------------------------------------------------------------------------- chapter page
def render_chapter(idx: int) -> tuple[str, dict]:
    ch = CHAPTERS[idx]
    set_prefix("")
    raw = read(CONTENT / "chapters" / ch["file"])
    # drop the H1 and the italic "Part N of" line: the page hero renders those
    raw = re.sub(r"^# .*\n", "", raw, count=1)
    raw = re.sub(r"^\*Part \d+ of Beyond Faster Coding\*\n", "", raw, count=1, flags=re.M)
    md, diagrams, used_refs = preprocess_markdown(raw, ch["id"])
    body, toc = render_markdown(md)
    body, linked_terms = autolink_terms(body, ch["id"])

    # figures
    def fig_sub(m: re.Match) -> str:
        did, n, cap = m.group(1), int(m.group(2)), m.group(3)
        return figure(did, cap, n)

    plain = re.sub(r"<[^>]+>", " ", body)
    body = re.sub(r"<!--FIG:([a-z0-9\-]+)\|(\d+)\|([^>]*)-->", fig_sub, body)
    body = body.replace('<div class="footnote">', '<div class="footnote"><h2 id="notes">Notes and sources</h2>')
    # external links open safely
    body = re.sub(r'<a href="(https?://[^"]+)"', r'<a href="\1" rel="noopener"', body)

    minutes = reading_minutes(plain)
    prev_ch = CHAPTERS[idx - 1] if idx > 0 else None
    next_ch = CHAPTERS[idx + 1] if idx + 1 < len(CHAPTERS) else None

    toc_html = "".join(f'<li><a href="#{esc(t["id"])}">{t["name"]}</a></li>' for t in toc)
    if used_refs:
        toc_html += '<li><a href="#notes">Notes and sources</a></li>'
    terms_html = "".join(
        f'<li><a href="glossary.html#{tid}" class="term-chip">{esc(GLOSS_BY_ID[tid]["term"])}</a></li>'
        for tid in ch.get("key_terms", []) if tid in GLOSS_BY_ID)

    dots = "".join(
        f'<a href="{c["slug"]}.html" class="dot{" on" if c["id"] == ch["id"] else ""}{" done" if c["number"] < ch["number"] else ""}" title="Part {c["number"]}: {esc(c["title"])}"><span>{c["number"]}</span></a>'
        for c in CHAPTERS)

    cover = figure(ch["cover"], ch["title"], None, "cover") if ch.get("cover") else ""

    page = head(f"{ch['title']} · {TITLE}", ch["summary"], f"{ch['slug']}.html", f"diagrams/{ch['cover']}.png")
    page += "<body class=\"chapter-page\">" + nav("series")
    page += f"""
<main>
<div class="hero hero-chapter">
<div class="hero-inner hero-split">
<div>
<div class="crumbs"><a href="index.html">{esc(TITLE)}</a> <span>/</span> Part {ch['number']} of {len(CHAPTERS)}</div>
<h1>{esc(ch['title'])}</h1>
<p class="lede">{esc(ch['summary'])}</p>
<div class="meta"><span>{minutes} min read</span><span class="sep">·</span><span>{len(diagrams)} figure{'s' if len(diagrams) != 1 else ''}</span><span class="sep">·</span><span>{len(used_refs)} source{'s' if len(used_refs) != 1 else ''} cited</span></div>
<div class="dots" aria-label="Series progress">{dots}</div>
</div>
<div class="hero-art">{cover}</div>
</div>
</div>
<div class="layout">
<aside class="side">
<div class="side-sticky">
<nav class="toc" aria-label="On this page"><div class="side-title">On this page</div><ol>{toc_html}</ol></nav>
<div class="side-block"><div class="side-title">Terms in this part</div><ul class="chips">{terms_html}</ul></div>
<div class="side-block share"><div class="side-title">Share</div>
<a class="btn small" href="https://www.linkedin.com/sharing/share-offsite/?url={esc(SITE_URL)}/{ch['slug']}.html" rel="noopener">LinkedIn</a>
<button class="btn small" type="button" data-copy="{esc(SITE_URL)}/{ch['slug']}.html">Copy link</button></div>
</div>
</aside>
<article class="prose" id="article">
{body}
<nav class="pager" aria-label="Series navigation">
{f'<a class="pager-prev" href="{prev_ch["slug"]}.html"><span class="pager-k">Previous · Part {prev_ch["number"]}</span><span class="pager-t">{esc(prev_ch["title"])}</span></a>' if prev_ch else '<span></span>'}
{f'<a class="pager-next" href="{next_ch["slug"]}.html"><span class="pager-k">Next · Part {next_ch["number"]}</span><span class="pager-t">{esc(next_ch["title"])}</span></a>' if next_ch else f'<a class="pager-next" href="workflow-catalog.html"><span class="pager-k">Continue</span><span class="pager-t">Browse the SDLC workflow catalog</span></a>'}
</nav>
</article>
</div>
</main>
{glossary_json()}
{footer()}
</body></html>"""
    info = {"chapter": ch, "minutes": minutes, "diagrams": diagrams, "refs": used_refs, "terms": linked_terms, "plain": plain, "cover": cover}
    return page, info


# --------------------------------------------------------------------------- home
def render_index(infos: list[dict]) -> str:
    set_prefix("")
    cards = ""
    for info in infos:
        ch = info["chapter"]
        cards += f"""
<article class="card chapter-card" style="--i:{ch['number']}">
<div class="card-num">Part {ch['number']}</div>
<div class="card-art">{figure(ch['cover'], ch['title'], None, 'thumb')}</div>
<h3><a href="{ch['slug']}.html">{esc(ch['title'])}</a></h3>
<p>{esc(ch['summary'])}</p>
<div class="card-meta">{info['minutes']} min · {len(info['diagrams'])} figures</div>
</article>"""
    n_workflows = len(CATALOG["workflows"])
    n_terms = len(GLOSSARY)
    n_figs = sum(len(i["diagrams"]) for i in infos)
    page = head(f"{TITLE} — {TOC['tagline'][:80]}", TOC["tagline"], "index.html", "diagrams/bottleneck.png")
    page += "<body class=\"home\">" + nav("home")
    page += f"""
<main>
<section class="hero hero-home">
<div class="hero-inner">
<div class="kicker">A seven-part series · edition {esc(VERSION)}</div>
<h1>Beyond Faster <em>Coding</em></h1>
<p class="lede">{esc(TOC['tagline'])}</p>
<div class="hero-actions"><a class="btn primary" href="{CHAPTERS[0]['slug']}.html">Start with Part 1</a><a class="btn" href="#model">See the model</a></div>
<div class="stats"><div><b>{len(CHAPTERS)}</b><span>parts</span></div><div><b>{n_figs}</b><span>figures</span></div><div><b>{n_workflows}</b><span>catalogued workflows</span></div><div><b>{n_terms}</b><span>terms, each with a source</span></div></div>
</div>
<div class="hero-art">{figure('bottleneck', 'Faster implementation does not automatically mean faster delivery.', None, 'hero-fig')}</div>
</section>

<section class="section" id="model">
<div class="section-inner">
<div class="section-head"><h2>Four things at four levels</h2><p>The series argues that harness engineering, the Engineering Kit, workflows and the software factory are not competing answers to one question. They nest. Tap a layer to jump to its part.</p></div>
<div class="model-explorer" id="model-explorer">
<div class="model-art">{figure('explainer', 'The model this series uses to organize its thinking.', None, 'model-fig')}</div>
<div class="model-layers">
{''.join(f'<a class="layer" data-layer="{i}" href="{c["slug"]}.html"><span class="layer-k">Part {c["number"]}</span><span class="layer-t">{esc(c["short"])}</span><span class="layer-s">{esc(c["summary"][:110])}…</span></a>' for i, c in enumerate(CHAPTERS))}
</div>
</div>
</div>
</section>

<section class="section alt" id="series">
<div class="section-inner">
<div class="section-head"><h2>The series</h2><p>Read in order: each part hands off to the next, and one hypothetical feature, a customer-record export, runs through all of them.</p></div>
<div class="cards">{cards}</div>
</div>
</section>

<section class="section" id="more">
<div class="section-inner">
<div class="section-head"><h2>Beyond the articles</h2><p>Material the articles could not hold.</p></div>
<div class="cards three">
<a class="card" href="workflow-catalog.html"><div class="card-num">Catalog</div><h3>{n_workflows} SDLC workflows, mapped to what they replace</h3><p>Every candidate workflow across eight phases, each with its decision, trigger, agent task, checks, human decision and evidence record, and a one-to-one map to the traditional activity it absorbs. Filter by phase, maturity and change type.</p></a>
<a class="card" href="pr-verification-reference.html"><div class="card-num">Reference sheet</div><h3>Pull-request verification, generic and worked</h3><p>The five Part 7 images in two versions with the same layout: one filled with the export example, one left generic for a team to fill in its own rules, thresholds and tiers.</p></a>
<a class="card" href="glossary.html"><div class="card-num">Terminology</div><h3>Every term, and where it comes from</h3><p>Which words are adopted from Böckeler and Thoughtworks, which are adapted, and which this series coined, with a translation table between the two vocabularies.</p></a>
</div>
</div>
</section>
</main>
{glossary_json()}
{footer()}
</body></html>"""
    return page


# --------------------------------------------------------------------------- glossary
ATTR_LABEL = {"adopted": "Adopted from source", "adapted": "Adapted from source", "coined": "Coined in this series", "common": "Common engineering usage"}


def render_glossary() -> str:
    set_prefix("")
    groups = {"adopted": [], "adapted": [], "coined": [], "common": []}
    for g in GLOSSARY:
        groups[g["attribution"]].append(g)
    items = ""
    for g in GLOSSARY:
        src = g.get("source")
        srcs = [src] + list(g.get("also") or []) if src else list(g.get("also") or [])
        src_html = " ".join(
            f'<a class="src" href="references.html#{k}">{esc(REFERENCES[k]["author"] if REFERENCES[k].get("author") else REFERENCES[k]["title"])}</a>'
            for k in srcs)
        chapters = " ".join(f'<a class="chip" href="{BY_ID[c]["slug"]}.html">Part {BY_ID[c]["number"]}</a>' for c in g.get("chapters", []) if c in BY_ID)
        counterpart = f'<div class="counterpart"><span class="k">In Böckeler\'s terms</span> {esc(g["counterpart"])}</div>' if g.get("counterpart") else ""
        items += f"""
<article class="term-entry" id="{g['id']}" data-attr="{g['attribution']}">
<div class="term-head"><h3>{esc(g['term'])}</h3><span class="attr attr-{g['attribution']}">{ATTR_LABEL[g['attribution']]}</span></div>
<p>{esc(g['definition'].strip())}</p>
{counterpart}
<div class="term-foot">{('<span class="k">Source</span> ' + src_html) if src_html else ''} {('<span class="k">Used in</span> ' + chapters) if chapters else ''}</div>
</article>"""

    translation = [
        ("Harness", "Harness (wide sense: the whole engineering environment)", "adopted"),
        ("Guides (feedforward controls)", "Skills, constitution, readiness questions", "adapted"),
        ("Sensors (feedback controls)", "Validators, tests, review skill", "adapted"),
        ("Computational controls", "Deterministic machinery; validators; gates", "adapted"),
        ("Inferential controls", "Probabilistic machinery; the review skill; harness evaluations", "adapted"),
        ("Regulation categories (maintainability, architecture, behaviour)", "Not used as categories; rules carry a route instead (gate / judgment / guidance)", "different"),
        ("Steering loop", "Feedback path, with its conversions named", "adapted"),
        ("Harnessability", "Give the agent a usable starting point; brownfield pre-flight analysis", "adapted"),
        ("Ambient affordances", "Not used; closest is the kit's technology profile", "different"),
        ("Harness templates", "Engineering Kit technology profiles", "adapted"),
        ("—", "Rule registry, evidence record, could_not_run, risk tier, workflow, software factory", "coined"),
    ]
    trans_html = "".join(f'<tr><td>{esc(a)}</td><td>{esc(b)}</td><td><span class="attr attr-{c}">{c}</span></td></tr>' for a, b, c in translation)

    page = head(f"Terminology and sources · {TITLE}", "Every term the series uses, what it means, and where it comes from: adopted from Böckeler and Thoughtworks, adapted, or coined here.", "glossary.html")
    page += "<body>" + nav("glossary")
    page += f"""
<main>
<div class="hero hero-plain"><div class="hero-inner"><div class="crumbs"><a href="index.html">{esc(TITLE)}</a> <span>/</span> Terminology</div><h1>Terminology and sources</h1>
<p class="lede">The series reuses vocabulary that Birgitta Böckeler set out in <a href="https://martinfowler.com/articles/harness-engineering.html" rel="noopener">Harness Engineering for Coding Agent Users</a> on martinfowler.com, adds a few working names of its own, and leans on ordinary engineering words for the rest. This page says which is which, so a reader moving between the two vocabularies can translate.</p>
<div class="filterbar" id="term-filter"><button class="chipbtn on" data-attr="all">All ({len(GLOSSARY)})</button>{''.join(f'<button class="chipbtn" data-attr="{k}">{ATTR_LABEL[k]} ({len(v)})</button>' for k, v in groups.items())}</div>
</div></div>
<div class="section-inner narrow">
<section class="translation">
<h2>Translation table</h2>
<p class="muted">Böckeler's vocabulary on the left, this series' on the right. "Adapted" means the idea is hers and the word or scope is different here.</p>
<table class="table"><thead><tr><th>Böckeler / Thoughtworks</th><th>This series</th><th>Relation</th></tr></thead><tbody>{trans_html}</tbody></table>
</section>
<section class="terms" id="terms">{items}</section>
</div>
</main>
{glossary_json()}
{footer()}
</body></html>"""
    return page


# --------------------------------------------------------------------------- references
def render_references(infos: list[dict]) -> str:
    set_prefix("")
    used_by: dict[str, list[dict]] = {k: [] for k in REFERENCES}
    for info in infos:
        for k in info["refs"]:
            if k in used_by:
                used_by[k].append(info["chapter"])
    for g in GLOSSARY:
        for k in [g.get("source")] + list(g.get("also") or []):
            if k:
                used_by.setdefault(k, [])
    items = ""
    for k, r in REFERENCES.items():
        chs = " ".join(f'<a class="chip" href="{c["slug"]}.html">Part {c["number"]}</a>' for c in used_by.get(k, []))
        terms = " ".join(f'<a class="chip" href="glossary.html#{g["id"]}">{esc(g["term"])}</a>' for g in GLOSSARY if k in ([g.get("source")] + list(g.get("also") or [])))
        items += f"""
<article class="ref-entry" id="{k}">
<h3><a href="{esc(r['url'])}" rel="noopener">{esc(r['title'])}</a></h3>
<div class="muted">{esc(', '.join(x for x in [r.get('author'), r.get('org')] if x))}{(' · ' + esc(r['date'])) if r.get('date') else ''}</div>
<p>{esc(r.get('note', ''))}</p>
<div class="term-foot">{('<span class="k">Cited in</span> ' + chs) if chs else ''} {('<span class="k">Terms</span> ' + terms) if terms else ''}</div>
</article>"""
    page = head(f"References · {TITLE}", "Canonical list of the sources this series cites.", "references.html")
    page += "<body>" + nav("glossary")
    page += f"""
<main>
<div class="hero hero-plain"><div class="hero-inner"><div class="crumbs"><a href="index.html">{esc(TITLE)}</a> <span>/</span> References</div><h1>References</h1>
<p class="lede">Everything the series cites, in one place. Each chapter's own notes link here, and every glossary term that is adopted or adapted names one of these.</p></div></div>
<div class="section-inner narrow"><section class="refs">{items}</section></div>
</main>
{glossary_json()}
{footer()}
</body></html>"""
    return page


# --------------------------------------------------------------------------- workflow catalog
def render_catalog() -> str:
    set_prefix("")
    data = CATALOG
    phases = {p["key"]: p["name"] for p in data["phases"]}
    wf_json = json.dumps({"phases": data["phases"], "maturity": data["maturity"], "sources": data["sources"], "workflows": data["workflows"], "traditional_map": data["traditional_map"]})
    counts = {}
    for w in data["workflows"]:
        counts[w["maturity"]] = counts.get(w["maturity"], 0) + 1
    page = head(f"SDLC workflow catalog · {TITLE}", f"{len(data['workflows'])} candidate workflows across the software lifecycle, each mapped to the traditional activity it absorbs, with its activities split into agent, checks and people.", "workflow-catalog.html")
    page += "<body>" + nav("workflows")
    page += f"""
<main>
<div class="hero hero-plain"><div class="hero-inner"><div class="crumbs"><a href="index.html">{esc(TITLE)}</a> <span>/</span> Workflow catalog</div><h1>SDLC workflow catalog</h1>
<p class="lede">Every candidate workflow across the lifecycle, using the definition from <a href="workflows.html">Part 5</a>: it supports one delivery decision; it has a trigger, an agent action, deterministic checks, a human decision, an evidence record and a named owner. Each one is mapped one-to-one to the traditional activity it absorbs, so a reader can see that almost nothing here is new; the mechanical part moved to a check, the reading and drafting moved to an agent, and the decision stayed with a person but now carries evidence.</p>
<div class="stats small"><div><b>{len(data['workflows'])}</b><span>workflows</span></div><div><b>{len(data['phases'])}</b><span>phases</span></div><div><b>{counts.get('Floor',0)}</b><span>floor</span></div><div><b>{counts.get('First',0)}</b><span>first</span></div><div><b>{counts.get('Later',0)}</b><span>later</span></div><div><b>{len(data['traditional_map'])}</b><span>traditional activities mapped</span></div></div>
</div></div>
<div class="section-inner">
<div class="catalog-controls">
<div class="viewtabs" role="tablist"><button class="on" data-view="map" role="tab">Map</button><button data-view="table" role="tab">Table</button><button data-view="traditional" role="tab">Traditional map</button></div>
<input id="wf-search" type="search" placeholder="Filter workflows…" aria-label="Filter workflows">
<div class="filterbar" id="wf-maturity"><span class="k">Maturity</span><button class="chipbtn on" data-m="all">All</button><button class="chipbtn m-Floor" data-m="Floor">Floor</button><button class="chipbtn m-First" data-m="First">First</button><button class="chipbtn m-Later" data-m="Later">Later</button></div>
<div class="filterbar" id="wf-applies"><span class="k">Change type</span><button class="chipbtn on" data-a="all">All</button><button class="chipbtn" data-a="UI">UI</button><button class="chipbtn" data-a="API">API</button><button class="chipbtn" data-a="Data">Data</button></div>
</div>
<div class="legend-row"><span class="k">Maturity</span>{''.join(f'<span class="lg m-{k}"><i></i>{k} — {esc(v)}</span>' for k, v in data['maturity'].items())}</div>
<div id="wf-map" class="wf-map" data-view="map"></div>
<div id="wf-table" class="wf-table" data-view="table" hidden></div>
<div id="wf-trad" class="wf-trad" data-view="traditional" hidden></div>
<p class="muted small-note">Sources for the traditional side: {', '.join(esc(v) for v in data['sources'].values())}. No tool names in the catalog by design; tools appear only in the traditional map as they were in the sources. Download the catalog as <a href="data/workflow-catalog.json" download>JSON</a> or <a href="data/workflow-catalog.csv" download>CSV</a>.</p>
</div>
<div class="wf-detail" id="wf-detail" hidden><div class="wf-detail-panel"><button class="lightbox-close" type="button" aria-label="Close">×</button><div class="wf-detail-body"></div></div></div>
</main>
<script id="wf-data" type="application/json">{wf_json}</script>
{glossary_json()}
{footer()}
</body></html>"""
    return page


# --------------------------------------------------------------------------- Part 7 reference sheet
def render_reference() -> str:
    set_prefix("")
    pairs = [
        ("1", "kit-touched", "What pull-request verification takes from the kit", "Mechanism comes from the kit; meaning comes from the project. The evidence row is the one thing a project cannot override."),
        ("2", "run", "One run, step by step", "Seven steps from trigger to reviewer. Revision 1 of the export change is blocked for two causes; the generic sheet shows the same seven steps as a protocol."),
        ("3", "exits", "Four ways out, and one through", "Every exit has a destination and an owner. The example marks which exits revision 1 took."),
        ("4", "flows", "The next revision, and what flowed where", "Revision 2 passes. Upstream: the readiness record. Downstream: the verification record with its expiry rule. Backwards: three feedback conversions, and one failure that did not need one."),
    ]
    sections = ""
    for n, key, title, blurb in pairs:
        sections += f"""
<section class="ref-pair" id="image-{n}">
<div class="ref-pair-head"><h2>{n}. {esc(title)}</h2><p>{esc(blurb)}</p>
<div class="toggle" role="tablist" data-pair="{n}"><button class="on" data-variant="export" role="tab">Worked example</button><button data-variant="generic" role="tab">Generic</button></div></div>
<div class="variant" data-variant="export">{figure(f'p7-{n}-{key}-export', f'{title} — worked example', None, 'sheet')}</div>
<div class="variant" data-variant="generic" hidden>{figure(f'p7-{n}-{key}-generic', f'{title} — generic', None, 'sheet')}</div>
</section>"""
    sections += f"""
<section class="ref-pair" id="image-5">
<div class="ref-pair-head"><h2>5. What to measure</h2><p>Generic only: the five measures are the same for every team. Read them in pairs.</p></div>
{figure('p7-5-measures-generic', 'What to measure', None, 'sheet')}
</section>"""
    page = head(f"Pull-request verification reference sheet · {TITLE}", "The five Part 7 images in two versions with the same layout: worked example and generic template.", "pr-verification-reference.html", "diagrams/p7-2-run-export.png")
    page += "<body>" + nav("reference")
    page += f"""
<main>
<div class="hero hero-plain"><div class="hero-inner"><div class="crumbs"><a href="index.html">{esc(TITLE)}</a> <span>/</span> Reference sheet</div><h1>Pull-request verification, drawn in full</h1>
<p class="lede">The companion to <a href="pull-request-verification.html">Part 7</a>. Each image exists in two versions with exactly the same layout: the worked example, filled with the customer-record export story, and the generic sheet, with every label made neutral so a team can fill in its own rules, thresholds and tiers. A box in one has exactly one counterpart in the other. Toggle between them on each image, or <button class="linkbtn" id="toggle-all" type="button">switch all to generic</button>.</p>
<div class="hero-actions"><a class="btn primary" href="downloads/pr-verification-reference-sheet.pdf" download>Download the PDF (9 pages)</a><a class="btn" href="pull-request-verification.html">Read Part 7</a></div>
</div></div>
<div class="section-inner">{sections}</div>
</main>
{glossary_json()}
{footer()}
</body></html>"""
    return page


# --------------------------------------------------------------------------- discovery files
def write_discovery(infos: list[dict]) -> None:
    urls = ["index.html"] + [i["chapter"]["slug"] + ".html" for i in infos] + ["workflow-catalog.html", "pr-verification-reference.html", "glossary.html", "references.html"]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for u in urls:
        loc = f"{SITE_URL}/" if u == "index.html" else f"{SITE_URL}/{u}"
        sm += f"  <url><loc>{loc}</loc><lastmod>{TODAY}</lastmod></url>\n"
    sm += "</urlset>\n"
    write(SITE / "sitemap.xml", sm)
    write(SITE / "robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")
    # llms.txt
    lines = [f"# {TITLE}", "", f"> {TOC['tagline']}", "", f"A seven-part series by {TOC['author']}. Edition {VERSION}. Prose CC BY 4.0.", "", "## Parts"]
    for i in infos:
        c = i["chapter"]
        lines.append(f"- [Part {c['number']}: {c['title']}]({SITE_URL}/{c['slug']}.html): {c['summary']}")
    lines += ["", "## Reference", f"- [Terminology and sources]({SITE_URL}/glossary.html)", f"- [SDLC workflow catalog]({SITE_URL}/workflow-catalog.html)", f"- [Pull-request verification reference sheet]({SITE_URL}/pr-verification-reference.html)", f"- [References]({SITE_URL}/references.html)", f"- [Full text]({SITE_URL}/llms-full.txt)"]
    write(SITE / "llms.txt", "\n".join(lines) + "\n")
    full = [f"# {TITLE}", "", TOC["tagline"], ""]
    for i in infos:
        c = i["chapter"]
        full += [f"\n\n# Part {c['number']}: {c['title']}", "", read(CONTENT / "chapters" / c["file"])]
    full += ["\n\n# Terminology", ""]
    for g in GLOSSARY:
        full.append(f"- **{g['term']}** ({g['attribution']}{', source: ' + g['source'] if g.get('source') else ''}): {g['definition'].strip()}")
    write(SITE / "llms-full.txt", "\n".join(full) + "\n")
    # search index
    idx = []
    for i in infos:
        c = i["chapter"]
        idx.append({"t": f"Part {c['number']}: {c['title']}", "u": c["slug"] + ".html", "k": "chapter", "s": c["summary"], "b": i["plain"][:20000]})
    for g in GLOSSARY:
        idx.append({"t": g["term"], "u": f"glossary.html#{g['id']}", "k": "term", "s": g["definition"].strip()[:200], "b": g["definition"].strip()})
    for w in CATALOG["workflows"]:
        idx.append({"t": f"{w['id']} {w['name']}", "u": f"workflow-catalog.html#{w['id']}", "k": "workflow", "s": w["decision"], "b": " ".join(str(v) for v in [w["agent"], w["checks"], w["people"], w["traditional"]["activity"]])})
    write(SITE / "search-index.json", json.dumps(idx))
    # data downloads
    (SITE / "data").mkdir(exist_ok=True)
    write(SITE / "data" / "workflow-catalog.json", json.dumps(CATALOG["workflows"], indent=1))
    import csv, io
    buf = io.StringIO()
    wcsv = csv.writer(buf)
    wcsv.writerow(["id", "phase", "name", "decision", "trigger", "agent", "checks", "people", "evidence", "applies_to", "maturity", "traditional_activity", "traditional_owner", "traditional_artefact", "notes"])
    for w in CATALOG["workflows"]:
        wcsv.writerow([w["id"], w["phase"], w["name"], w["decision"], w["trigger"], w["agent"], w["checks"], w["people"], w["evidence"], "; ".join(w["applies_to"]), w["maturity"], w["traditional"]["activity"], w["traditional"]["owner"], w["traditional"]["artefact"], w.get("notes") or ""])
    write(SITE / "data" / "workflow-catalog.csv", buf.getvalue())
    # 404
    set_prefix("")
    page = head(f"Not found · {TITLE}", "Page not found.", "404.html") + "<body>" + nav("") + f'<main><div class="hero hero-plain"><div class="hero-inner"><h1>Not found</h1><p class="lede">That page is not part of the series. <a href="{SITE_URL}/">Start from the beginning</a>.</p></div></div></main>' + glossary_json() + footer() + "</body></html>"
    write(SITE / "404.html", page)
    write(SITE / ".nojekyll", "")


# --------------------------------------------------------------------------- main
def main() -> None:
    ids = write_diagram_files()
    infos = []
    for idx, ch in enumerate(CHAPTERS):
        page, info = render_chapter(idx)
        write(SITE / f"{ch['slug']}.html", page)
        infos.append(info)
    write(SITE / "index.html", render_index(infos))
    write(SITE / "glossary.html", render_glossary())
    write(SITE / "references.html", render_references(infos))
    write(SITE / "workflow-catalog.html", render_catalog())
    write(SITE / "pr-verification-reference.html", render_reference())
    write_discovery(infos)
    print(f"Generated {len(CHAPTERS)} chapters + 5 pages, {len(ids)} diagrams → {SITE}")
    for i in infos:
        c = i["chapter"]
        print(f"  Part {c['number']}: {i['minutes']:>2} min · {len(i['diagrams'])} figures · {len(i['refs'])} sources · {len(i['terms'])} terms linked")


if __name__ == "__main__":
    main()

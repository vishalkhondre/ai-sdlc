"""Generate the one-page AI SDLC map (five bands) and its adoption-path companion page.

    python content/diagrams/map/build_map.py      -> writes ../svg/ai-sdlc-map.svg and ../svg/ai-sdlc-adoption-path.svg
"""
from __future__ import annotations

import html
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "svg"

INK, MUTE, FAINT, LINE = "#1f1f1c", "#5F5E5A", "#888780", "#d3d1c7"
C = {  # stroke, fill, dark text
    "amber": ("#8a5a00", "#FAEEDA", "#5a3b00"),
    "grey": ("#888780", "#F1EFE8", "#2C2C2A"),
    "purple": ("#534AB7", "#EEEDFE", "#26215C"),
    "teal": ("#0F6E56", "#E1F5EE", "#04342C"),
    "coral": ("#993C1D", "#FAECE7", "#4A1B0C"),
}
FONT = '"Liberation Sans","DejaVu Sans",Arial,sans-serif'


def esc(s: str) -> str:
    return html.escape(s, quote=False)


def wrap(text: str, width: float, size: float) -> list[str]:
    maxc = max(6, int(width / (size * 0.53)))
    out, cur = [], ""
    for w in text.split():
        if len(cur) + len(w) + (1 if cur else 0) > maxc:
            out.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}" if cur else w
    if cur:
        out.append(cur)
    return out


def t(x, y, s, size=14, fill=INK, weight=400, anchor="start", italic=False, spacing=0):
    st = f' font-style="italic"' if italic else ""
    ls = f' letter-spacing="{spacing}"' if spacing else ""
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}" text-anchor="{anchor}"{st}{ls}>{esc(s)}</text>'


def r(x, y, w, h, fill="#fff", stroke=LINE, sw=1.4, rx=10, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>'


def para(x, y, text, width, size=14, fill=INK, lh=None, weight=400):
    lh = lh or size * 1.42
    s = ""
    for i, line in enumerate(wrap(text, width, size)):
        s += t(x, y + i * lh, line, size, fill, weight)
    return s, y + len(wrap(text, width, size)) * lh


def chip(x, y, w, label, color, h=30, size=13):
    stroke, fill, dark = C[color]
    return r(x, y, w, h, "#fff", stroke, 1.2, 8) + t(x + w / 2, y + h / 2 + size * 0.36, label, size, dark, 600, "middle")


def svg_open(w: int, h: int, title: str, desc: str, refs: list[str]) -> str:
    """Root element with a text alternative and the reference keys the diagram relies on.

    scripts/check_citations.py checks each key in data-references against references.yml.
    """
    return (f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" '
            f'font-family=\'{FONT}\' data-references="{" ".join(refs)}">'
            f"<title>{esc(title)}</title><desc>{esc(desc)}</desc>")


def credit(x, y, text, refs: list[str], size=12, anchor="start") -> str:
    """A credit line for borrowed terms. It may name a source (like a chapter footnote);
    scripts/check_citations.py requires one for every adopted or adapted glossary term a
    standalone diagram uses, and skips the product-name check on it."""
    return (f'<text class="credit" data-references="{" ".join(refs)}" x="{x}" y="{y}" font-size="{size}" '
            f'fill="{FAINT}" text-anchor="{anchor}">{esc(text)}</text>')


def arrow_defs():
    out = "<defs>"
    for name, col in [("a", FAINT), ("p", C["purple"][0]), ("r", C["coral"][0])]:
        out += (f'<marker id="{name}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
                f'<path d="M1 1L8 5L1 9" fill="none" stroke="{col}" stroke-width="1.6"/></marker>')
    return out + "</defs>"


def band_label(y, h, num, name, sub, notes, color):
    stroke, fill, dark = C[color]
    s = r(60, y, 175, h, fill, stroke, 1.4, 12)
    s += t(78, y + 30, f"{num} · {name}", 15, dark, 700)
    s += t(78, y + 50, sub, 13, stroke, 600, italic=True)
    yy = y + 76
    for n in notes:
        p, yy = para(78, yy, n, 145, 12, MUTE, 16)
        s += p
        yy += 4
    return s


def group(x, y, w, h, title, color):
    stroke, fill, dark = C[color]
    return r(x, y, w, h, fill, stroke, 1.3, 11) + t(x + 14, y + 22, title.upper(), 11.5, stroke, 700, spacing=0.6)


def bullet_col(x, y, w, h, title, items, color):
    stroke, fill, dark = C[color]
    s = r(x, y, w, h, fill, stroke, 1.3, 11) + t(x + 16, y + 26, title.upper(), 12, stroke, 700, spacing=0.6)
    yy = y + 52
    for it in items:
        lines = wrap(it, w - 44, 14)
        s += f'<circle cx="{x + 20}" cy="{yy - 5}" r="2.6" fill="{stroke}"/>'
        for i, ln in enumerate(lines):
            s += t(x + 30, yy + i * 19, ln, 14, INK)
        yy += len(lines) * 19 + 4
    return s


MAP_DESC = (
    "A one-page map of the AI-assisted software lifecycle in five bands. "
    "1 Context: project, product and flow type set the risk tier (HIL is hardware-in-the-loop testing, "
    "OTA over-the-air updates, CVE a published vulnerability). "
    "2 Lifecycle: SAFe levels (portfolio, Agile Release Train, team; WSJF is weighted shortest job first, "
    "PI a planning interval), phases from idea to operate with the workflow in each, Definition of Ready (DoR) "
    "and Definition of Done (DoD), and a traceability spine from requirement to incident. Incident feedback "
    "loops back to change what Specification asks. "
    "3 Core: harness engineering as the discipline, the Engineering Kit as the artefact, workflows as the unit of work, "
    "and the software factory as the operating state that emerges. "
    "4 Enablement: agent runtime and tools (MCP is the Model Context Protocol), people and roles "
    "(PO / PM: product owner / product manager), and the operating model. "
    "5 Assurance: evidence and traceability, standards and AI governance (templates include ADRs, "
    "architecture decision records), and measurement. "
    "A footer shows the adoption path: deterministic floor, one workflow, a second workflow with hand-off, "
    "feedback path proven, factory emerges. Credit lines in the footer name the sources of borrowed terms."
)
PATH_DESC = (
    "Five adoption stages left to right: 0 Deterministic floor, 1 One workflow, 2 Second workflow and hand-off, "
    "3 Feedback path proven, 4 Factory emerges. For each stage the diagram lists what to build, what to measure, "
    "a suggested condition for moving on, and a failure pattern to watch for. "
    "The order is the point: skills, agents and platforms added before the floor and the first workflow tend to "
    "become sprawl. A credit line in the footer names the sources of borrowed terms."
)


# ============================================================================ page 1
def page_map() -> str:
    W, H = 1600, 1152
    s = [svg_open(W, H, "The AI SDLC on one page", MAP_DESC, ["aicpa-soc2", "dora-metrics"]),
         arrow_defs(), f'<rect width="{W}" height="{H}" fill="#fff"/>',
         t(60, 58, "The AI SDLC on one page", 34, INK, 700),
         t(60, 88, "Five bands. Context sets the risk tier; the lifecycle says where; the core does the work; enablement makes it possible; assurance proves it.", 16, MUTE)]

    # ---------------- band 1: context
    y0, h = 110, 150
    s.append(band_label(y0, h, "1", "CONTEXT", "what kind of work", ["Together these set the risk tier: which gates run, how deep, who approves."], "amber"))
    s.append(group(250, y0, 300, h, "Project type", "amber"))
    s.append(chip(264, y0 + 38, 132, "Greenfield", "amber"))
    s.append(chip(404, y0 + 38, 132, "Brownfield", "amber"))
    s.append(chip(264, y0 + 76, 272, "Modernisation / migration", "amber"))
    s.append(t(264, y0 + 132, "brownfield starts with pre-flight analysis", 12, MUTE, italic=True))
    s.append(group(566, y0, 330, h, "Product type", "amber"))
    s.append(chip(580, y0 + 38, 150, "Web / cloud app", "amber"))
    s.append(chip(738, y0 + 38, 144, "Firmware / device", "amber"))
    s.append(chip(580, y0 + 76, 150, "Data & ML models", "amber"))
    s.append(chip(738, y0 + 76, 144, "Platform / shared lib", "amber", size=12))
    s.append(t(580, y0 + 132, "changes which gates make sense (HIL, OTA, drift)", 12, MUTE, italic=True))
    s.append(group(912, y0, 628, h, "Flow", "amber"))
    flows = ["Full feature", "Bug fix", "Hotfix *", "Trivial / config", "Spike / research", "Refactor / tech debt", "Dependency / CVE fix", "Migration · rollback"]
    for i, f in enumerate(flows):
        cx = 926 + (i % 4) * 152
        cy = y0 + 38 + (i // 4) * 38
        s.append(chip(cx, cy, 146, f, "amber", size=12))
    s.append(t(926, y0 + 132, "* hotfix: expedited path, evidence completed afterwards, never skipped", 12, MUTE, italic=True))

    # ---------------- band 2: lifecycle
    y0, h = 280, 210
    s.append(band_label(y0, h, "2", "LIFECYCLE", "where it runs", ["SAFe levels, phases, the workflow in each phase, Definition of Ready / Done, and the traceability spine underneath."], "grey"))
    s.append(r(250, y0, 1290, h, "#fff", C["grey"][0], 1.3, 12))
    levels = [("Portfolio", "epics · WSJF · lean budgets", 264, 390), ("Agile Release Train", "features · PI planning · system demo", 662, 450), ("Team", "stories · iterations · DoR / DoD", 1120, 406)]
    for i, (n, sub, x, w) in enumerate(levels):
        s.append(r(x, y0 + 12, w, 32, C["grey"][1], C["grey"][0], 1.1, 16))
        s.append(t(x + 14, y0 + 33, n, 13.5, C["grey"][2], 700) + t(x + w - 14, y0 + 33, sub, 12, MUTE, anchor="end"))
        if i < 2:
            s.append(f'<line x1="{x + w + 2}" y1="{y0 + 28}" x2="{levels[i + 1][2] - 4}" y2="{y0 + 28}" stroke="{FAINT}" stroke-width="1.4" marker-end="url(#a)"/>')
    phases = ["Idea", "Specification", "Design", "Develop", "Build", "QA", "Deploy", "Release", "Operate"]
    px = [264 + i * 141.5 for i in range(9)]
    pw = 133
    py = y0 + 70
    # feedback loop above phases
    s.append(f'<path d="M{px[8] + pw / 2} {py} L{px[8] + pw / 2} {py - 12} L{px[1] + pw / 2} {py - 12} L{px[1] + pw / 2} {py - 3}" fill="none" stroke="{C["coral"][0]}" stroke-width="1.4" stroke-dasharray="5 4" marker-end="url(#r)"/>')
    s.append(r(700, py - 20, 360, 16, "#fff", "#fff", 0, 3) + t(880, py - 8, "incident feedback changes what Specification asks", 11.5, C["coral"][0], 600, "middle", italic=True))
    for i, p in enumerate(phases):
        s.append(r(px[i], py, pw, 44, "#faf9f5", "#b4b2a9", 1.3, 8))
        if p == "QA":
            s.append(t(px[i] + pw / 2, py + 20, "QA", 14.5, INK, 700, "middle") + t(px[i] + pw / 2, py + 36, "security · performance", 10.5, MUTE, anchor="middle"))
        else:
            s.append(t(px[i] + pw / 2, py + 27, p, 14.5, INK, 700, "middle"))
    for i, tag in [(1, "DoR"), (7, "DoD")]:
        s.append(r(px[i] + pw - 38, py - 8, 34, 16, C["teal"][0], C["teal"][0], 0, 8) + t(px[i] + pw - 21, py + 4, tag, 10.5, "#fff", 700, "middle"))
    wy = py + 52
    wfs = [(0, 0, "intake & triage"), (1, 1, "spec readiness"), (2, 2, "design conformance"), (3, 5, "pull-request verification  ·  security & performance checks by tier"), (6, 6, "deploy verification"), (7, 7, "release readiness"), (8, 8, "incident feedback")]
    for a, b, lab in wfs:
        x1, x2 = px[a], px[b] + pw
        bold = a == 3
        s.append(r(x1, wy, x2 - x1, 22, C["purple"][1], C["purple"][0], 1.8 if bold else 1.1, 11))
        s.append(t((x1 + x2) / 2, wy + 15.5, lab, 11.5, C["purple"][2], 700 if bold else 600, "middle"))
    # traceability spine
    sy = wy + 50
    s.append(f'<line x1="{px[0]}" y1="{sy}" x2="{px[8] + pw}" y2="{sy}" stroke="{C["teal"][0]}" stroke-width="2"/>')
    spine = ["requirement", "spec", "task", "test", "change", "release", "incident"]
    for i, n in enumerate(spine):
        cx = px[0] + 40 + i * ((px[8] + pw - px[0] - 80) / 6)
        s.append(f'<circle cx="{cx}" cy="{sy}" r="5" fill="#fff" stroke="{C["teal"][0]}" stroke-width="2"/>')
        s.append(t(cx, sy + 20, n, 12, C["teal"][2], 600, "middle"))
    s.append(t(px[0], sy - 8, "TRACEABILITY SPINE · linked by rule IDs", 10.5, C["teal"][0], 700, spacing=0.5))
    s.append(t(px[8] + pw, sy - 8, "Inspect & Adapt each PI: which workflow to add or tighten next", 11.5, MUTE, anchor="end", italic=True))

    # ---------------- band 3: core
    y0, h = 510, 118
    s.append(band_label(y0, h, "3", "CORE", "what does the work", ["Built-in quality: gates enforce what a machine can check."], "purple"))
    core = [("DISCIPLINE", "Harness engineering", "what the agent may do, what a machine checks, what a person decides", "purple", None),
            ("ARTEFACT", "Engineering Kit", "rule registry, validators, skills with evals, evidence schema, adapters", "teal", None),
            ("UNIT OF WORK", "Workflows", "one decision end to end, with evidence; e.g. pull-request verification", "coral", None),
            ("OPERATING STATE", "Software factory", "emerges when workflows share rules, evidence and feedback", "grey", "6 4")]
    cw, gap = 300, 30
    for i, (k, n, d, col, dash) in enumerate(core):
        x = 250 + i * (cw + gap)
        stroke, fill, dark = C[col]
        s.append(r(x, y0, cw, h, fill if not dash else "#fff", stroke, 1.6, 12, dash))
        s.append(t(x + 16, y0 + 24, k, 11.5, stroke, 700, spacing=0.6) + t(x + 16, y0 + 50, n, 20, dark, 700))
        p, _ = para(x + 16, y0 + 74, d, cw - 32, 13, MUTE, 17)
        s.append(p)
        if i < 3:
            s.append(f'<line x1="{x + cw + 3}" y1="{y0 + h / 2}" x2="{x + cw + gap - 4}" y2="{y0 + h / 2}" stroke="{FAINT}" stroke-width="1.6" marker-end="url(#a)"/>')

    # ---------------- band 4: enablement
    y0, h = 648, 176
    s.append(band_label(y0, h, "4", "ENABLEMENT", "what makes it possible", ["Tools, people and the operating model. The kit enforces policy; it never holds authority."], "teal"))
    s.append(bullet_col(250, y0, 420, h, "Agent runtime & tools", [
        "Coding agents and agentic IDEs; model providers",
        "Tool access (MCP), sandboxes, permissions, secrets",
        "Spec-driven development (SDD) frameworks",
        "CI runner and change host, bound by thin adapters"], "teal"))
    s.append(bullet_col(685, y0, 420, h, "People & roles", [
        "PO / PM own intent and open decisions",
        "Architects own rules; QA owns scenarios and evals",
        "Engineers direct, verify, turn lessons into gates",
        "Platform team owns the kit",
        "Watch: review load, skill erosion, adoption"], "teal"))
    s.append(bullet_col(1120, y0, 420, h, "Operating model", [
        "Scrum / Kanban teams on an Agile Release Train",
        "PI cadence, system demo, Inspect & Adapt",
        "Work tracking & knowledge base",
        "Decision rights and approvals; policy wins"], "teal"))

    # ---------------- band 5: assurance
    y0, h = 844, 190
    s.append(band_label(y0, h, "5", "ASSURANCE", "what must be provable", ["Every workflow run leaves an evidence record. Auditors, release and incident review all read the same one."], "coral"))
    s.append(bullet_col(250, y0, 420, h, "Evidence & traceability", [
        "Evidence record on every run, fixed schema",
        "Rule IDs link rule → check → decision",
        "passed · failed · skipped · could_not_run",
        "Valid for one revision; a new push expires it"], "coral"))
    s.append(bullet_col(685, y0, 420, h, "Standards & AI governance", [
        "Templates: spec, plan, ADR, release notes",
        "SOC 2 change controls; domain standards as they apply",
        "AI use policy: data sent to models, IP of generated code",
        "Agent permissions reviewed as privileged access"], "coral"))
    s.append(bullet_col(1120, y0, 420, h, "Measurement", [
        "Baseline before changing anything",
        "Flow metrics and DORA delivery metrics",
        "Escaped defects; reviewer load and concentration",
        "Cost per change, including tokens and evals"], "coral"))

    # ---------------- footer: adoption path
    fy = 1056
    s.append(t(60, fy + 24, "ADOPTION PATH", 12, MUTE, 700, spacing=0.8))
    steps = ["0  Deterministic floor", "1  One workflow", "2  Second workflow + hand-off", "3  Feedback path proven", "4  Factory emerges"]
    sx = 250
    for i, st in enumerate(steps):
        w = 238
        s.append(r(sx, fy, w, 38, C["purple"][1] if i else C["teal"][1], C["purple"][0] if i else C["teal"][0], 1.2, 19))
        s.append(t(sx + w / 2, fy + 24, st, 13.5, C["purple"][2] if i else C["teal"][2], 700, "middle"))
        if i < 4:
            s.append(f'<line x1="{sx + w + 3}" y1="{fy + 19}" x2="{sx + w + 22}" y2="{fy + 19}" stroke="{FAINT}" stroke-width="1.5" marker-end="url(#a)"/>')
        sx += w + 25
    s.append(credit(60, fy + 64, "Harness engineering, feedback path and validators: after Böckeler (martinfowler.com)",
                    ["bockeler-harness", "bockeler-sensors"]))
    s.append(credit(60, fy + 82, "Spec-driven development: after GitHub Spec Kit · Lifecycle terms: SAFe (Scaled Agile, Inc.)",
                    ["spec-kit", "safe-framework"]))
    s.append(t(1540, fy + 64, "Detail: the adoption-path companion diagram.  Beyond Faster Coding · vishalkhondre.github.io/ai-sdlc", 12, FAINT, anchor="end"))
    s.append("</svg>")
    return "\n".join(s)


# ============================================================================ page 2
STAGES = [
    ("0", "Deterministic floor", "teal",
     ["A quality command that runs the same way locally and in CI", "Suggested: 3–5 validators for rules the team has already been hurt by", "Rule registry: every rule gets an ID, a route and an owner", "Evidence schema; branch protection actually enforced"],
     ["Baseline: lead time, review time, escaped defects", "Share of rules still guidance-only"],
     "Every merge passes the same checks, and enforcement is verified, not assumed.",
     "Skipping straight to skills and agents on top of no gates."),
    ("1", "One workflow", "purple",
     ["Pull-request verification end to end", "Review skill with an evaluation set before it ships", "Risk tiers; failure paths including could_not_run", "Expected checks recorded before results"],
     ["Reviewer minutes per PR", "Blocks by checks vs by people", "Agent finding acceptance rate"],
     "Suggested: run on 20+ real changes, evidence every time, one measure better than baseline.",
     "A demo-quality skill with no evals treated as a gate."),
    ("2", "Second workflow + hand-off", "purple",
     ["Specification readiness as the Definition of Ready", "Risk tier set at spec, read by verification", "Readiness record consumed automatically"],
     ["Work returned for clarification", "Time waiting on decisions"],
     "Verification reads readiness evidence without anyone copying it across.",
     "Each workflow inventing its own evidence format."),
    ("3", "Feedback path proven", "coral",
     ["Incident review converts findings: criterion, test, validator or eval", "Inspect & Adapt reviews which conversions landed", "Kit versioned; changes go through the kit's own tests"],
     ["Repeat defect categories", "Conversions closed vs opened"],
     "Suggested: each of the last three incidents changed an upstream check.",
     "Retro actions that are written down and never close."),
    ("4", "Factory emerges", "grey",
     ["Shared registry and evidence across workflows", "A second team installs the kit and passes its first feature", "Named owner for the connections between workflows"],
     ["Requirement-to-release time", "Escaped defects vs throughput", "Cost per change incl. tokens and evals"],
     "A second team adopts the kit without the original author in the room.",
     "Building the platform before the workflows exist."),
]


def page_path() -> str:
    W, H = 1600, 790
    s = [svg_open(W, H, "Adoption path: one step at a time, one workflow at a time", PATH_DESC, []),
         arrow_defs(), f'<rect width="{W}" height="{H}" fill="#fff"/>',
         t(60, 58, "Adoption path: one step at a time, one workflow at a time", 32, INK, 700),
         t(60, 88, "Companion to the one-page map. Each stage has something to build, something to measure, and a condition for moving on.", 16, MUTE)]
    cw, gap, x0, y0 = 280, 17, 66, 120
    rows = [("BUILD", 0), ("MEASURE", 1), ("MOVE ON WHEN", 2), ("WATCH FOR", 3)]
    for i, (num, name, col, build, measure, exit_, risk) in enumerate(STAGES):
        x = x0 + i * (cw + gap)
        stroke, fill, dark = C[col]
        s.append(r(x, y0, cw, 70, fill, stroke, 1.6, 12))
        s.append(t(x + 16, y0 + 26, f"STAGE {num}", 11.5, stroke, 700, spacing=0.6) + t(x + 16, y0 + 52, name, 18, dark, 700))
        if i < 4:
            s.append(f'<line x1="{x + cw + 2}" y1="{y0 + 35}" x2="{x + cw + gap - 3}" y2="{y0 + 35}" stroke="{FAINT}" stroke-width="1.6" marker-end="url(#a)"/>')
        s.append(r(x, y0 + 82, cw, 500, "#fff", stroke, 1.2, 12))
        yy = y0 + 110
        for label, idx in rows:
            s.append(t(x + 16, yy, label, 11, stroke, 700, spacing=0.6))
            yy += 20
            if idx in (0, 1):
                for it in (build if idx == 0 else measure):
                    lines = wrap(it, cw - 46, 13.5)
                    s.append(f'<circle cx="{x + 20}" cy="{yy - 4.5}" r="2.4" fill="{stroke}"/>')
                    for j, ln in enumerate(lines):
                        s.append(t(x + 30, yy + j * 18, ln, 13.5, INK))
                    yy += len(lines) * 18 + 5
            else:
                txt = exit_ if idx == 2 else risk
                p, yy = para(x + 16, yy, txt, cw - 32, 13.5, INK if idx == 2 else C["coral"][0], 18, 600 if idx == 2 else 400)
                s.append(p)
                yy += 5
            yy += 14
            if idx < 3:
                s.append(f'<line x1="{x + 14}" y1="{yy - 12}" x2="{x + cw - 14}" y2="{yy - 12}" stroke="{LINE}" stroke-width="1"/>')
    s.append(credit(1540, H - 10, "Feedback path, validators and review skills: after Böckeler (martinfowler.com) · Inspect & Adapt: SAFe term (Scaled Agile, Inc.)",
                    ["bockeler-harness", "bockeler-sensors", "safe-framework"], 11, "end"))
    s.append(t(800, H - 36, "The order is the point. Skills, agents and platforms added before the floor and the first workflow tend to become the sprawl they were meant to prevent.", 14, MUTE, anchor="middle", italic=True))
    s.append("</svg>")
    return "\n".join(s)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "ai-sdlc-map.svg").write_text(page_map(), encoding="utf-8")
    (OUT / "ai-sdlc-adoption-path.svg").write_text(page_path(), encoding="utf-8")
    print("written")

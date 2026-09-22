"""Shared drawing helpers for Part 7 images. One layout, two label sets."""
import html

W, H = 1600, 1000

# palette
P = dict(
    ink="#1f1f1c", mute="#5F5E5A", faint="#888780", line="#d3d1c7",
    purple="#534AB7", purple_bg="#EEEDFE", purple_dk="#26215C",
    teal="#0F6E56", teal_bg="#E1F5EE", teal_dk="#04342C",
    coral="#993C1D", coral_bg="#FAECE7", coral_dk="#4A1B0C",
    gray="#b4b2a9", gray_bg="#faf9f5", gray_dk="#5F5E5A",
    dim="#e9e8e2", dim_txt="#a8a69e",
)

STYLE = """
body{margin:0;background:#fff;font-family:"Liberation Sans","DejaVu Sans",Arial,sans-serif}
text{fill:#1f1f1c}
.t{font-size:34px;font-weight:600}
.sub{font-size:17px;fill:#5F5E5A}
.tag{font-size:13px;fill:#888780;letter-spacing:.3px}
.badge{font-size:13px;font-weight:600}
.h{font-size:17px;font-weight:600}
.b{font-size:15px}
.s{font-size:13px}
.xs{font-size:12px}
.mono{font-family:"Liberation Mono","DejaVu Sans Mono",monospace;font-size:13px}
.cap{font-size:18px;fill:#5F5E5A}
.leg{font-size:12.5px;fill:#5F5E5A}
"""


def esc(s):
    return html.escape(str(s), quote=False)


def wrap(text, width_px, size=15, factor=0.52):
    """Greedy wrap by estimated glyph width."""
    maxc = max(8, int(width_px / (size * factor)))
    out = []
    for para in str(text).split("\n"):
        line = ""
        for w in para.split(" "):
            if len(line) + len(w) + (1 if line else 0) <= maxc:
                line = (line + " " + w) if line else w
            else:
                if line:
                    out.append(line)
                line = w
        out.append(line)
    return out


def tspans(lines, x, y, lh, cls="b", fill=None, anchor="start", weight=None):
    f = f' fill="{fill}"' if fill else ""
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    wgt = f' font-weight="{weight}"' if weight else ""
    s = f'<text class="{cls}" x="{x}" y="{y}"{f}{a}{wgt}>'
    for i, ln in enumerate(lines):
        dy = 0 if i == 0 else lh
        s += f'<tspan x="{x}" dy="{dy}">{esc(ln)}</tspan>'
    return s + "</text>"


def text(s, x, y, cls="b", fill=None, anchor="start", weight=None):
    return tspans([s], x, y, 0, cls, fill, anchor, weight)


def para(s, x, y, width, size=15, lh=None, cls="b", fill=None, anchor="start", weight=None):
    lh = lh or round(size * 1.35)
    return tspans(wrap(s, width, size), x, y, lh, cls, fill, anchor, weight), len(wrap(s, width, size)) * lh


def rect(x, y, w, h, fill, stroke, r=10, sw=1.5, dash=None, extra=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}{extra}/>'


def line(x1, y1, x2, y2, stroke, sw=1.5, dash=None, marker=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = f' marker-end="url(#{marker})"' if marker else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{sw}"{d}{m}/>'


def path(d, stroke, sw=1.5, dash=None, marker=None, fill="none"):
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    m = f' marker-end="url(#{marker})"' if marker else ""
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{dd}{m}/>'


def chip(x, y, w, h, label, kind, size=13, dimmed=False):
    """Small rounded chip with a colour kind: agent|check|human|project|dim."""
    k = KIND[kind] if not dimmed else KIND["dim"]
    return rect(x, y, w, h, k["bg"], k["stroke"], r=7, sw=1.2) + \
        text(label, x + w / 2, y + h / 2 + size * 0.36, cls="s", fill=k["txt"], anchor="middle", weight=600)


KIND = {
    "agent": dict(bg=P["purple_bg"], stroke=P["purple"], txt=P["purple_dk"]),
    "check": dict(bg=P["teal_bg"], stroke=P["teal"], txt=P["teal_dk"]),
    "human": dict(bg=P["coral_bg"], stroke=P["coral"], txt=P["coral_dk"]),
    "project": dict(bg=P["gray_bg"], stroke=P["gray"], txt=P["gray_dk"]),
    "dim": dict(bg=P["dim"], stroke=P["dim"], txt=P["dim_txt"]),
}

DEFS = """
<defs>
<marker id="ar" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M1 1L8 5L1 9" fill="none" stroke="#5F5E5A" stroke-width="1.5"/></marker>
<marker id="art" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M1 1L8 5L1 9" fill="none" stroke="#0F6E56" stroke-width="1.5"/></marker>
<marker id="arc" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M1 1L8 5L1 9" fill="none" stroke="#993C1D" stroke-width="1.5"/></marker>
<marker id="arp" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M1 1L8 5L1 9" fill="none" stroke="#534AB7" stroke-width="1.5"/></marker>
</defs>
"""


def header(title, subtitle, variant, number):
    s = text(f"Beyond Faster Coding  ·  Part 7  ·  One workflow in full: Pull-request verification  ·  Image {number} of 5", 80, 44, cls="tag")
    s += text(title, 80, 92, cls="t")
    s += text(subtitle, 80, 122, cls="sub")
    # variant badge top right
    if variant == "generic":
        lab, k = "GENERIC REFERENCE", "check"
    else:
        lab, k = "WORKED EXAMPLE: CUSTOMER-RECORD EXPORT", "agent"
    bw = 12 + len(lab) * 8.2
    s += rect(W - 80 - bw, 30, bw, 26, KIND[k]["bg"], KIND[k]["stroke"], r=13, sw=1.2)
    s += text(lab, W - 80 - bw / 2, 48, cls="badge", fill=KIND[k]["txt"], anchor="middle")
    return s


def legend(y=898):
    s = rect(80, y, W - 160, 76, "#fff", P["line"], r=10, sw=1)
    x = 100
    yy = y + 22
    items = [("agent", "Agent (probabilistic)"), ("check", "Deterministic check / kit mechanism"),
             ("human", "Human decision / blocked"), ("project", "Project-supplied meaning")]
    for k, lab in items:
        s += rect(x, yy - 11, 18, 14, KIND[k]["bg"], KIND[k]["stroke"], r=3, sw=1.2)
        s += text(lab, x + 26, yy, cls="leg")
        x += 26 + len(lab) * 6.6 + 28
    x += 10
    lines = [(None, "run order"), ("2 3", "reads or writes evidence"), ("7 4", "feedback, flows upstream")]
    for dash, lab in lines:
        s += line(x, yy - 4, x + 40, yy - 4, P["mute"], 1.6, dash)
        s += text(lab, x + 48, yy, cls="leg")
        x += 48 + len(lab) * 6.6 + 28
    s += text("Vendor-neutral terms.  Execution surface: where the agent runs.   Change host: where the pull request lives.   "
              "Pipeline runner: where checks run unattended.   Kit: the versioned Engineering Kit installed in the repository.",
              100, y + 56, cls="leg")
    return s


def page(body, title, subtitle, variant, number):
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>{STYLE}</style></head><body>
<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">
<rect width="{W}" height="{H}" fill="#fff"/>{DEFS}
{header(title, subtitle, variant, number)}
{body}
{legend()}
</svg></body></html>"""


def V(variant, generic, export):
    return generic if variant == "generic" else export

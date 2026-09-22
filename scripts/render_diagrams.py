"""Render every diagram in site/diagrams/*.svg to PNG, and build the Part 7 reference-sheet PDF.

The SVGs are the source of truth (content/diagrams/svg + the Part 7 generators); the PNGs are
the LinkedIn/OG-image variants and are build artefacts. Run after site/generate.py.

    python scripts/render_diagrams.py            # all diagrams
    python scripts/render_diagrams.py --only p7   # only Part 7 sheets

Requires playwright + chromium (see scripts/requirements.txt).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
DIAGRAMS = SITE / "diagrams"
DOWNLOADS = SITE / "downloads"


def svg_size(svg: str) -> tuple[int, int]:
    m = re.search(r'<svg[^>]*width="(\d+)"[^>]*height="(\d+)"', svg)
    return (int(m.group(1)), int(m.group(2))) if m else (1200, 628)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--scale", type=int, default=2, help="device scale factor for PNGs")
    args = ap.parse_args()
    from playwright.sync_api import sync_playwright

    svgs = sorted(p for p in DIAGRAMS.glob("*.svg") if args.only in p.name)
    if not svgs:
        print("No diagrams found. Run site/generate.py first.", file=sys.stderr)
        return 1
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for svg_path in svgs:
            svg = svg_path.read_text(encoding="utf-8")
            w, h = svg_size(svg)
            page = browser.new_page(viewport={"width": w, "height": h}, device_scale_factor=args.scale)
            page.set_content(f'<!DOCTYPE html><html><body style="margin:0;background:#fff">{svg}</body></html>')
            page.wait_for_timeout(100)
            out = svg_path.with_suffix(".png")
            page.screenshot(path=str(out), clip={"x": 0, "y": 0, "width": w, "height": h})
            page.close()
            print(f"  {out.name}  {w}x{h}@{args.scale}x")
        # OG image for the home page
        og_src = DIAGRAMS / "bottleneck.png"
        if og_src.exists():
            (SITE / "og-image.png").write_bytes(og_src.read_bytes())
        # Part 7 PDF: generic and worked-example pages interleaved
        order = ["p7-1-kit-touched-generic", "p7-1-kit-touched-export", "p7-2-run-generic", "p7-2-run-export",
                 "p7-3-exits-generic", "p7-3-exits-export", "p7-4-flows-generic", "p7-4-flows-export", "p7-5-measures-generic"]
        pages_html = "".join(
            f'<div style="{"page-break-before:always;" if i else ""}width:1600px;height:1000px;overflow:hidden">{(DIAGRAMS / f"{n}.svg").read_text(encoding="utf-8")}</div>'
            for i, n in enumerate(order) if (DIAGRAMS / f"{n}.svg").exists())
        if pages_html:
            DOWNLOADS.mkdir(exist_ok=True)
            page = browser.new_page(viewport={"width": 1600, "height": 1000})
            page.set_content(f'<!DOCTYPE html><html><head><style>@page{{size:1600px 1000px;margin:0}} body{{margin:0}}</style></head><body>{pages_html}</body></html>')
            page.pdf(path=str(DOWNLOADS / "pr-verification-reference-sheet.pdf"), width="1600px", height="1000px", print_background=True, margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
            page.close()
            print("  downloads/pr-verification-reference-sheet.pdf")
        browser.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

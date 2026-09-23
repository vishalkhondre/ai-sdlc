"""Browser regressions. Build first; requires Playwright Chromium.

Run explicitly (also required by CI): python scripts/check_browser.py
The ordinary unit suite remains runnable without a browser installation.
"""
from __future__ import annotations

import functools
import http.server
import os
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


def main():
    handler = functools.partial(QuietHandler, directory=str(ROOT / "site"))
    with http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler) as server:
        threading.Thread(target=server.serve_forever, daemon=True).start()
        base = f"http://127.0.0.1:{server.server_port}"
        try:
            with sync_playwright() as p:
                options = {}
                if os.environ.get("PLAYWRIGHT_CHROMIUM_EXECUTABLE"):
                    options["executable_path"] = os.environ["PLAYWRIGHT_CHROMIUM_EXECUTABLE"]
                browser = p.chromium.launch(**options)
                page = browser.new_page()
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.add_init_script("""Object.defineProperty(navigator, 'clipboard', {
                  value: {writeText: async text => {window.copiedText = text;}}
                });""")
                page.goto(base + "/index.html")
                assert page.locator("article.chapter-card").count() == 7
                page.locator("article.chapter-card h3 a").first.click()
                assert page.url.endswith("/faster-coding-is-only-part.html")

                page.goto(base + "/workflow-catalog.html")
                for label, visible in [("Table", "wf-table"), ("Traditional map", "wf-trad"), ("Map", "wf-map")]:
                    page.get_by_role("tab", name=label, exact=True).click()
                    for panel in ("wf-map", "wf-table", "wf-trad"):
                        assert page.locator("#" + panel).is_visible() == (panel == visible), (label, panel)

                page.goto(base + "/engineering-kit.html")
                expected = page.locator(".prose pre code").first.text_content()
                page.locator(".prose pre .copybtn").first.click()
                assert page.evaluate("window.copiedText") == expected

                page.goto(base + "/pull-request-verification.html")
                page.locator(".diagram .zoom").first.click()
                image = page.locator("#lightbox img")
                image.wait_for(state="visible")
                page.wait_for_function("document.querySelector('#lightbox img').complete")
                assert image.evaluate("img => img.naturalWidth > 0")
                assert page.evaluate("""() => {
                  const ids = [...document.querySelectorAll('[id]')].map(el => el.id);
                  return ids.length === new Set(ids).size;
                }""")
                page.keyboard.press("Escape")
                assert page.locator("#lightbox").is_hidden()
                assert not errors, errors
                browser.close()
        finally:
            server.shutdown()
    print("Browser checks passed: chapter navigation, catalog views, code copy, diagram isolation.")


if __name__ == "__main__":
    main()

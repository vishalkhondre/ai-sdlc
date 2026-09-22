from common import *


def box(x, y, w, h, kind, title, body, size=13, lh=17, title_cls="h", dash=None):
    k = KIND[kind]
    s = rect(x, y, w, h, k["bg"], k["stroke"], r=10, sw=1.5, dash=dash)
    s += text(title, x + 16, y + 26, cls=title_cls, fill=k["txt"])
    s += tspans(wrap(body, w - 32, size), x + 16, y + 48, lh, cls="s", fill=P["ink"])
    return s


def build(variant):
    s = ""
    # ---------- top row: hand-offs ----------
    s += text("Hand-offs: what this run reads, and what it leaves behind", 80, 168, cls="s", fill=P["faint"], weight=600)
    ty, th = 186, 150
    # left: readiness record
    s += box(80, ty, 340, th, "project", "Readiness record (upstream)",
             V(variant, "Supplies the risk tier and the change categories, which select the rule set and the gate.",
               "Tier 2 · categories API + Data. Unchanged since revision 1, so the same rule set applies."))
    # centre: the run
    cx, cw = 500, 600
    s += rect(cx, ty, cw, th, P["teal_bg"], P["teal"], r=10, sw=2)
    s += text(V(variant, "Pull-request verification, next revision", "Pull-request verification, revision 2"),
              cx + 18, ty + 28, cls="h", fill=P["teal_dk"])
    s += tspans(wrap(V(variant,
                       "Every gate-routed check passed. Every judgment finding resolved with a logged decision. Approvals match the tier. Merged.",
                       "R-042 passed · coverage 86% · 50k-row load scenario passed (streamed, 4.1 s) · dependency direction passed (runner image fixed) · R-017 resolved: volume guard added · one approval · merged"),
                    cw - 36, 13.5), cx + 18, ty + 52, 18, cls="s", fill=P["teal_dk"])
    s += text("steps 1 to 7 of image 2, exit E of image 3", cx + 18, ty + th - 14, cls="xs", fill=P["teal"])
    # right: verification record + release readiness
    s += box(1180, ty, 340, th, "check", "Verification record (downstream)",
             V(variant, "Closed for this revision. Read by release readiness. Expires the moment a new revision is pushed.",
               "Revision 2 · kit 1.4.0 · 4 rules, all passed · 1 finding resolved · 1 approval. Read by release readiness."))
    # arrows in / out (dotted = evidence)
    s += line(420, ty + th / 2, cx - 4, ty + th / 2, P["mute"], 1.6, "2 3", "ar")
    s += line(cx + cw, ty + th / 2, 1176, ty + th / 2, P["mute"], 1.6, "2 3", "ar")
    # release readiness below right
    ry = ty + th + 30
    s += rect(1180, ry, 340, 48, P["gray_bg"], P["gray"], r=8, sw=1.2)
    s += text("Release readiness reads it", 1350, ry + 22, cls="b", anchor="middle", weight=600)
    s += text("valid for this revision only", 1350, ry + 40, cls="xs", fill=P["mute"], anchor="middle")
    s += line(1350, ty + th, 1350, ry - 4, P["mute"], 1.6, "2 3", "ar")

    # ---------- bottom: feedback ----------
    fy = 470
    s += text("Feedback: what flowed back upstream from revision 1, and where it landed", 80, fy, cls="s", fill=P["faint"], weight=600)
    bx = [80, 580, 1080]
    bw, bh, by = 440, 230, fy + 60
    targets = [
        ("Kit installation check (doctor)", "brittle behaviour  →  harness change", "check",
         "A could_not_run with a stable cause becomes an installation check. The next runner missing the tool fails at doctor, before any change reaches the gate.",
         "doctor now verifies the dependency-direction tool is present on the runner image.\n\nCause: the could_not_run at revision 1."),
        ("Readiness checklist", "misunderstood requirement  →  readiness question", "project",
         "A judgment finding the specification should have prevented becomes a mandatory readiness question for that change category. The next similar feature meets it before any code exists.",
         "Every feature that produces a file must now state a volume limit at readiness.\n\nCause: the specification for the date-range filter never mentioned volume, so R-017 was only caught at review."),
        ("Review-skill evaluation set", "accepted finding  →  eval case", "agent",
         "An accepted finding becomes an evaluation case. A model or prompt change that stops catching it fails the skill's evaluation before the skill is released again.",
         "New eval case: given the revision-1 diff and the rule set, does the skill flag R-017?\n\nCause: the finding was accepted, so it is worth keeping."),
    ]
    for i, (title, conv, kind, gen, exp) in enumerate(targets):
        k = KIND[kind]
        x = bx[i]
        s += rect(x, by, bw, bh, k["bg"], k["stroke"], r=10, sw=1.5)
        s += text(title, x + 16, by + 26, cls="h", fill=k["txt"])
        s += text(conv, x + 16, by + 48, cls="xs", fill=P["mute"], weight=600)
        s += tspans(wrap(V(variant, gen, exp), bw - 32, 13.5), x + 16, by + 74, 18, cls="s", fill=P["ink"])
        # dashed arrow from run box bottom to target top
        sx = cx + cw * (i + 1) / 4
        s += path(f"M{sx} {ty + th} C {sx} {ty + th + 90}, {x + bw / 2} {by - 90}, {x + bw / 2} {by - 4}",
                  k["stroke"], 1.6, "7 4", "ar" if kind == "project" else ("art" if kind == "check" else "arp"))
    # what did not flow back
    ny = by + bh + 16
    s += rect(80, ny, W - 160, 40, "#fff", P["line"], r=8, sw=1)
    s += text(V(variant,
                "Not every failure needs a conversion. A test that fails, gets fixed and passes has done its job; only failures that reveal a gap in the system flow back.",
                "What did not flow back: the load scenario failed, the code was fixed, the scenario passed. The test did its job. Nothing upstream needed to change for it."),
              100, ny + 25, cls="b", fill=P["mute"])
    return page(s, "4. The next revision passes, and what flowed where",
                V(variant, "One run reads upstream evidence, leaves downstream evidence, and sends what it learned back.",
                  "Revision 2 merged. Three things from revision 1 changed the system; one did not need to."),
                variant, 4)


if __name__ == "__main__":
    for v in ("generic", "export"):
        open(f"p7-4-flows-{v}.html", "w").write(build(v))

from common import *

BANDS = [
    ("Rules and knowledge", [("Rule registry", True), ("Risk tiers and lanes", True),
                             ("Constitution template", False), ("Readiness checklist", False)]),
    ("Skills", [("Review skill", True), ("Spec readiness skill", False),
                ("Incident triage skill", False), ("Documentation skill", False)]),
    ("Validators and evidence", [("Validator runner", True), ("Test harness hook", True),
                                 ("Evidence schema", True), ("Gate semantics", True)]),
    ("Adapters and commands", [("Execution-surface adapter", True), ("Change-host adapter", True),
                               ("Pipeline-runner adapter", True), ("verify command", True),
                               ("init / doctor commands", False)]),
]

ROWS = [
    ("Rule registry",
     "Identifiers, routes (gate / judgment / guidance), owners. Lookup by change category.",
     "Which rules are mandatory for this change's categories, and which route each takes.",
     "R-042 export honours row-level access (gate). R-017 file-producing endpoints declare a volume limit (judgment)."),
    ("Risk tiers",
     "Tier definitions: what blocks, how many approvals, what may be waived.",
     "Which tier this change was declared at plan.",
     "Tier 2: checks block, one human approval, no waivers on gate-routed rules."),
    ("Validator runner",
     "Runs each validator; returns passed / failed / skipped / could_not_run against a rule ID.",
     "Validators enabled, thresholds, scope.",
     "Coverage ≥ 80% on the export module. Dependency direction on domain/."),
    ("Test harness hook",
     "Runs the project's suites; reports results per rule, not per suite.",
     "The project's own test suites.",
     "Export suite, including the 50k-row load scenario."),
    ("Review skill",
     "Reads the diff and the applicable rules; produces findings tagged to rule IDs. Cannot block.",
     "The constitution and any category-specific review prompts.",
     "Constitution section on data exposure. API and Data review prompts."),
    ("Evidence schema",
     "Fixed record shape: kit version, revision, rules applied, each result, findings, decision.",
     "Nothing. The record shape is not customisable.",
     "Nothing. The record shape is not customisable."),
    ("Adapters",
     "Thin bindings to the execution surface, the change host and the pipeline runner.",
     "Which surface, host and runner this repository uses.",
     "Unnamed here. The run is the same on any of them."),
]


def build(variant):
    s = ""
    # ---------- left: kit map ----------
    lx, ly, lw = 80, 160, 560
    s += text("The kit, with this workflow's components lit", lx, ly, cls="h")
    y = ly + 22
    for band, chips in BANDS:
        n_rows = (len(chips) + 1) // 2
        bh = 34 + n_rows * 44
        s += rect(lx, y, lw, bh, "#fff", P["line"], r=10, sw=1)
        s += text(band, lx + 16, y + 24, cls="s", fill=P["mute"], weight=600)
        for i, (lab, on) in enumerate(chips):
            cx = lx + 16 + (i % 2) * 268
            cy = y + 36 + (i // 2) * 44
            s += chip(cx, cy, 252, 34, lab, "check", dimmed=not on)
        y += bh + 12
    s += para("11 of 17 components are used in a pull-request run. The rest sit idle for this workflow. "
              "No workflow consumes the kit whole.", lx, y + 14, lw, size=14, cls="b", fill=P["mute"])[0]

    # ---------- right: mechanism / meaning table ----------
    rx, ry = 690, 160
    c1, c2, c3 = 150, 320, 360
    g = 10
    s += text("Component", rx, ry, cls="h")
    s += text("Kit supplies (mechanism)", rx + c1 + g, ry, cls="h", fill=P["teal_dk"])
    s += text(V(variant, "Project supplies (meaning)", "This project supplies (meaning)"),
              rx + c1 + c2 + 2 * g, ry, cls="h", fill=P["gray_dk"])
    y = ry + 18
    rh = 96
    for name, mech, gen, exp in ROWS:
        meaning = V(variant, gen, exp)
        s += rect(rx, y, c1, rh - 8, "#fff", P["line"], r=8, sw=1)
        s += tspans(wrap(name, c1 - 20, 15), rx + 12, y + 30, 19, cls="b", weight=600)
        s += rect(rx + c1 + g, y, c2, rh - 8, P["teal_bg"], P["teal"], r=8, sw=1.2)
        s += tspans(wrap(mech, c2 - 24, 13), rx + c1 + g + 12, y + 24, 17, cls="s", fill=P["teal_dk"])
        empty = meaning.startswith("Nothing")
        s += rect(rx + c1 + c2 + 2 * g, y, c3, rh - 8, "#fff" if empty else P["gray_bg"], P["gray"], r=8, sw=1.2,
                  dash="5 4" if empty else None)
        s += tspans(wrap(meaning, c3 - 24, 13), rx + c1 + c2 + 2 * g + 12, y + 24, 17, cls="s",
                    fill=P["faint"] if empty else P["ink"])
        y += rh
    s += para(V(variant,
                "Read the right column as the template a project fills in. The left column never changes between projects, "
                "and the evidence row is the one thing a project cannot override.",
                "Same layout as the generic sheet. Only the right column changed, and the evidence row did not."),
              rx, y + 14, c1 + c2 + c3 + 2 * g, size=14, cls="b", fill=P["mute"])[0]
    return page(s, "1. What pull-request verification takes from the kit",
                V(variant, "Mechanism comes from the kit. Meaning comes from the project.",
                  "Mechanism comes from the kit. Meaning comes from the export feature's project."),
                variant, 1)


if __name__ == "__main__":
    for v in ("generic", "export"):
        open(f"p7-1-kit-touched-{v}.html", "w").write(build(v))

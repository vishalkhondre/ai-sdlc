from common import *

# (step name, actor kind, actor label, generic text, export text, kit element)
STEPS = [
    ("Trigger", "project", "Change host",
     "A pull request is opened, or a new revision is pushed to one already open.",
     "PR opened: a date-range filter on the customer-record export. Revision 1.",
     "Change-host adapter"),
    ("Read upstream", "check", "Kit",
     "The readiness record for this work item supplies the risk tier and the change categories. Together they select which rules apply and what the gate needs.",
     "Readiness record: tier 2, categories API + Data. Selects R-042 (gate), R-017 (judgment), coverage threshold and dependency direction.",
     "Evidence schema (read)"),
    ("Checks run", "check", "Deterministic checks",
     "Each validator and suite returns passed, failed, skipped or could_not_run against a rule ID. Skipped needs a stated reason. could_not_run is never a pass.",
     "R-042 row-level access: passed.  Coverage on export module: passed (84%).  50k-row load scenario: FAILED, timeout.  Dependency direction: COULD_NOT_RUN, tool missing on the runner image.",
     "Validator runner, test harness hook"),
    ("Agent review", "agent", "Review skill",
     "The skill reads the diff against the applicable rules and the constitution. It produces findings tagged to rule IDs. It cannot block and it cannot approve.",
     "One finding, tagged R-017: the endpoint streams a file and no volume guard or pagination is present. Route: judgment, so it goes to a person.",
     "Review skill"),
    ("Evidence assembled", "check", "Kit",
     "One record for this revision: kit version, rules applied, each result, each finding, and a decision field still empty.",
     "kit 1.4.0 · revision 1 · 4 rules · passed 2, failed 1, could_not_run 1 · findings 1 · decision: pending",
     "Evidence schema (write)"),
    ("Gate evaluated", "check", "Gate semantics",
     "Blocked if any gate-routed check failed or could not run. Otherwise the tier says how many approvals a pass needs and which findings must be resolved.",
     "BLOCKED. Two causes: the load scenario failed; the dependency check could not run. The R-017 finding is open but is not what blocked.",
     "Gate semantics"),
    ("Reviewer sees", "human", "Reviewer",
     "Decisions and exceptions, not the diff: what failed, what could not run, what the agent flagged, and what needs a call from a person.",
     "Three lines. Load scenario failed (author fixes). Dependency check could not run (runner owner notified). One R-017 finding to accept or dispute.",
     "Change-host adapter"),
]


def build(variant):
    s = ""
    x_step, x_actor, x_text, x_kit = 80, 330, 500, 1250
    w_text = 720
    y0 = 172
    rh = 96
    # column headers
    s += text("Step", x_step, y0 - 14, cls="s", fill=P["faint"], weight=600)
    s += text("Performed by", x_actor, y0 - 14, cls="s", fill=P["faint"], weight=600)
    s += text(V(variant, "What happens", "What happened on revision 1"), x_text, y0 - 14, cls="s", fill=P["faint"], weight=600)
    s += text("Kit element", x_kit, y0 - 14, cls="s", fill=P["faint"], weight=600)
    # spine
    s += line(x_step + 18, y0 + 8, x_step + 18, y0 + rh * (len(STEPS) - 1) + 20, P["line"], 2)
    for i, (name, kind, actor, gen, exp, kit) in enumerate(STEPS):
        y = y0 + i * rh
        k = KIND[kind]
        # number bubble
        s += f'<circle cx="{x_step + 18}" cy="{y + 14}" r="15" fill="{k["bg"]}" stroke="{k["stroke"]}" stroke-width="1.5"/>'
        s += text(str(i + 1), x_step + 18, y + 19, cls="s", fill=k["txt"], anchor="middle", weight=700)
        s += text(name, x_step + 44, y + 19, cls="h")
        # actor chip
        s += chip(x_actor, y, 150, 30, actor, kind)
        # body text
        body = V(variant, gen, exp)
        emphasise = variant == "export" and i in (2, 5)
        s += rect(x_text - 14, y - 8, w_text + 28, rh - 12,
                  P["coral_bg"] if emphasise else "#fff", P["coral"] if emphasise else P["line"], r=8, sw=1.2 if emphasise else 1)
        s += tspans(wrap(body, w_text, 14), x_text, y + 14, 18, cls="b", fill=P["coral_dk"] if emphasise else P["ink"])
        # kit element
        s += tspans(wrap(kit, 260, 13), x_kit, y + 14, 17, cls="s", fill=P["teal_dk"], weight=600)
    # outcome strip
    y = y0 + len(STEPS) * rh - 4
    s += rect(80, y, W - 160, 40, KIND["human"]["bg"] if variant == "export" else P["gray_bg"],
              KIND["human"]["stroke"] if variant == "export" else P["gray"], r=8, sw=1.2)
    s += text(V(variant,
                "Outcome: approved or blocked, and the record says which, why, on which revision, under which kit version. No human approval is spent before the checks have spoken.",
                "Outcome: blocked at revision 1. No human approval was spent. The reviewer's first look took three lines, not a diff."),
              100, y + 25, cls="b", fill=KIND["human"]["txt"] if variant == "export" else P["mute"])
    return page(s, "2. One run, step by step",
                V(variant, "What happens between 'opened' and 'merged', and who performs each step.",
                  "Revision 1 of the export change, blocked. Coral rows are where this run went wrong."),
                variant, 2)


if __name__ == "__main__":
    for v in ("generic", "export"):
        open(f"p7-2-run-{v}.html", "w").write(build(v))

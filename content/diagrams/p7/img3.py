from common import *

# (title, kind, condition, action, recorded/owner, export badge, taken?)
LANES = [
    ("A. Check failed", "human",
     "A gate-routed validator or test returned failed.",
     "Blocked. The author fixes and pushes a new revision. No human approval is asked for; nobody reads a diff that has already failed a rule.",
     "Result against the rule ID, in the evidence record. Owner: the author.",
     "Taken at revision 1: the 50k-row load scenario timed out.", True),
    ("B. Check could not run", "human",
     "A validator returned could_not_run: tool missing, runner misconfigured, harness timeout.",
     "Blocked, with a different cause. The runner owner is notified. Never treated as skipped, and never treated as passed. The gate stays a gate.",
     "Result could_not_run against the rule ID, with the cause. Owner: whoever owns the runner.",
     "Taken at revision 1: the dependency-direction tool was missing from the runner image.", True),
    ("C. Agent finding disputed", "agent",
     "The reviewer or author disagrees with a judgment-routed finding.",
     "A person decides. The decision and its reason are logged against the rule ID. Repeated disputes on one rule go to the rule owner, because the rule or the skill is wrong.",
     "Decision and reason on the finding, in the evidence record. Owner: the reviewer.",
     "Not taken: the author accepted the R-017 finding and added the volume guard.", False),
    ("D. Rule ambiguous", "project",
     "A check and a finding disagree, or a rule cannot be applied to this kind of change.",
     "Escalated to the rule owner. The route may change: guidance to judgment, judgment to gate, or the rule is split. The change waits or proceeds under a logged exception.",
     "Exception or route change, in the registry's history. Owner: the rule owner.",
     "Not taken.", False),
    ("E. Through", "check",
     "Every gate-routed check passed, every finding is resolved, approvals match the tier.",
     "Merged. The verification record is closed for this revision and becomes readable by release readiness.",
     "Closed record: revision, kit version, results, findings, decisions, approver.",
     "Taken at revision 2. See image 4.", True),
]


def build(variant):
    s = ""
    # source node
    nx, ny, nw, nh = 80, 440, 230, 90
    s += rect(nx, ny, nw, nh, P["teal_bg"], P["teal"], r=10, sw=1.5)
    s += text("Run reaches the gate", nx + nw / 2, ny + 38, cls="h", fill=P["teal_dk"], anchor="middle")
    s += text("after steps 1 to 6 of image 2", nx + nw / 2, ny + 62, cls="s", fill=P["teal"], anchor="middle")

    lx, ly, lw, lh, gap = 380, 168, 1140, 120, 10
    c1, c2, c3 = 320, 440, 300
    for i, (title, kind, cond, act, rec, badge, taken) in enumerate(LANES):
        y = ly + i * (lh + gap)
        k = KIND[kind]
        dimmed = variant == "export" and not taken
        s += rect(lx, y, lw, lh, "#fff" if dimmed else k["bg"], P["gray"] if dimmed else k["stroke"], r=10,
                  sw=1 if dimmed else 1.5, dash="5 4" if dimmed else None)
        tc = P["dim_txt"] if dimmed else k["txt"]
        bc = P["dim_txt"] if dimmed else P["ink"]
        s += text(title, lx + 18, y + 26, cls="h", fill=tc)
        s += text("When", lx + 18, y + 50, cls="xs", fill=P["faint"], weight=600)
        s += tspans(wrap(cond, c1 - 30, 13), lx + 18, y + 68, 17, cls="s", fill=bc)
        s += text("Then", lx + c1 + 10, y + 26, cls="xs", fill=P["faint"], weight=600)
        s += tspans(wrap(act, c2 - 20, 13.5), lx + c1 + 10, y + 46, 17, cls="s", fill=bc)
        s += text("Recorded, and who owns it", lx + c1 + c2 + 20, y + 26, cls="xs", fill=P["faint"], weight=600)
        s += tspans(wrap(rec, c3 - 40, 13), lx + c1 + c2 + 20, y + 46, 17, cls="s", fill=bc)
        # connector from node
        mid = y + lh / 2
        s += path(f"M{nx + nw} {ny + nh / 2} C {nx + nw + 40} {ny + nh / 2}, {lx - 40} {mid}, {lx} {mid}",
                  P["dim_txt"] if dimmed else k["stroke"], 1.5, marker=None)
        if variant == "export":
            # badge along bottom of lane
            bw = 14 + len(badge) * 6.4
            bx = lx + lw - bw - 14
            by = y + lh - 26
            s += rect(bx, by, bw, 20, "#fff", P["gray"] if dimmed else k["stroke"], r=10, sw=1)
            s += text(badge, bx + bw / 2, by + 14, cls="xs", fill=P["dim_txt"] if dimmed else k["txt"], anchor="middle", weight=600)
    cy = ly + 5 * (lh + gap) + 12
    s += para(V(variant,
                "Every exit has a destination and an owner. B is the one most teams do not model. Without it, a broken runner quietly turns the gate into a suggestion.",
                "Revision 1 left by A and B at once. Two owners were notified, and neither needed to read the diff to know what to do."),
              80, cy, W - 160, size=15, cls="b", fill=P["mute"])[0]
    return page(s, "3. Four ways out, and one through",
                V(variant, "What happens when the gate is reached, exit by exit.",
                  "Which exits revision 1 took, and which it did not. Dimmed lanes were not used."),
                variant, 3)


if __name__ == "__main__":
    for v in ("generic", "export"):
        open(f"p7-3-exits-{v}.html", "w").write(build(v))

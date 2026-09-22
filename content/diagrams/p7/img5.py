from common import *

ROWS = [
    ("Escaped defects per merged change",
     "Whether the checks and the findings are catching what matters. The only measure that says the workflow works, rather than that it runs.",
     "Rising while merge volume rises. The gate is passing things it should not.",
     "Incident and defect records that link back to a verification record by revision.", "human"),
    ("Reviewer minutes per pull request",
     "Whether human attention is spent on decisions or on reading. Read it against escaped defects, never alone.",
     "Falling while escaped defects rise: reviewers are skimming. Rising with volume: the reviewer is the bottleneck again.",
     "Change-host timestamps between 'ready for review' and decision.", "human"),
    ("Blocks by checks versus blocks by people",
     "Whether the rules the team has been hurt by have become gates. Each human block is a candidate rule.",
     "People block most of the time. Rules exist as comments, not as validators.",
     "Gate outcome and cause in the evidence record.", "check"),
    ("Agent finding acceptance rate",
     "Whether the review skill is worth reading. Findings that are accepted are signal; findings that are dismissed are noise.",
     "Very low: the skill is noise and will be ignored. Near 100%: reviewers are rubber-stamping, not deciding.",
     "Decisions logged against findings, per rule ID.", "agent"),
    ("could_not_run frequency",
     "Whether the gate is real. Every could_not_run is a run where a rule was not enforced.",
     "Rising, or tolerated. The gate is turning into a suggestion one broken runner at a time.",
     "Check results in the evidence record, with cause.", "check"),
]


def build(variant):
    s = ""
    x0, y0 = 80, 172
    c = [300, 440, 400, 300]
    g = 12
    heads = ["Measure", "What it tells you", "A bad trend looks like", "Where it comes from"]
    x = x0
    for i, h in enumerate(heads):
        s += text(h, x, y0 - 14, cls="s", fill=P["faint"], weight=600)
        x += c[i] + g
    rh = 118
    for r, (m, tells, bad, src, kind) in enumerate(ROWS):
        y = y0 + r * rh
        k = KIND[kind]
        x = x0
        s += rect(x, y, c[0], rh - 12, k["bg"], k["stroke"], r=8, sw=1.2)
        s += tspans(wrap(m, c[0] - 28, 16), x + 14, y + 30, 21, cls="h", fill=k["txt"])
        x += c[0] + g
        s += rect(x, y, c[1], rh - 12, "#fff", P["line"], r=8, sw=1)
        s += tspans(wrap(tells, c[1] - 28, 14), x + 14, y + 26, 19, cls="b")
        x += c[1] + g
        s += rect(x, y, c[2], rh - 12, P["coral_bg"], P["coral"], r=8, sw=1, dash="5 4")
        s += tspans(wrap(bad, c[2] - 28, 14), x + 14, y + 26, 19, cls="b", fill=P["coral_dk"])
        x += c[2] + g
        s += rect(x, y, c[3], rh - 12, P["gray_bg"], P["gray"], r=8, sw=1)
        s += tspans(wrap(src, c[3] - 28, 13.5), x + 14, y + 26, 18, cls="s", fill=P["mute"])
    y = y0 + len(ROWS) * rh
    s += rect(80, y, W - 160, 60, "#fff", P["line"], r=8, sw=1)
    s += tspans(wrap("None of these needs a new tool. Every one is derivable from the evidence record and the change host, which is the point of "
                     "leaving a record. Read them in pairs: reviewer minutes with escaped defects, acceptance rate with finding volume. "
                     "A single number from this list, read alone, will justify whatever the reader already believed.",
                     W - 200, 14), 100, y + 24, 19, cls="b", fill=P["mute"])
    return page(s, "5. What to measure, and what a bad trend looks like",
                "Five measures the workflow produces as a by-product of running. Coral is the direction to worry about.",
                variant, 5)


if __name__ == "__main__":
    open("p7-5-measures-generic.html", "w").write(build("generic"))

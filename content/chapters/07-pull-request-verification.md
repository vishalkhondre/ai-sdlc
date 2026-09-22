# One workflow in full: Pull-request verification

*Part 7 of Beyond Faster Coding*

The first six parts of this series described a system. Faster coding moved the bottleneck. Harness engineering designs the environment around the agent. The Engineering Kit packages the parts of that environment worth sharing. A workflow puts the environment to work for one delivery decision. A software factory is what appears when enough workflows share rules, evidence and feedback.

Description has a limit. At some point a reader is entitled to ask what any of this looks like on an ordinary Tuesday, on one change, with one reviewer. This part takes a single workflow and draws it at the level of detail where the description can be checked.

The workflow is pull-request verification. The running example is the customer-record export feature from the earlier parts. The images that follow exist in two versions: the worked example shown here, and a generic reference sheet with the same layout and no story, for teams that want the template without the export.

## The moment in delivery

Every change reaches a point where someone has to decide whether it is safe to merge into the shared codebase. In most teams that point is the pull request. Something has to happen between "opened" and "merged", and that something is pull-request verification.

It is one of the oldest workflows in software delivery. In the traditional lifecycle it was a person reading a diff, plus whatever automated tests existed, plus a merge button. The outcome depended on how much attention the reviewer had that day.

When an agent writes a large share of the code, the volume of changes reaching that point rises, and the reviewer's knowledge of each change falls, because they did not write it. The old approach breaks in a specific way. Reviewers either read everything and become the bottleneck, or skim and become a formality. Part 2 called this the bottleneck moving downstream. Part 6 called the result review fatigue. Pull-request verification is the workflow sitting where that pressure lands.

The decision has not changed: is this safe to merge. What has changed is that it must be made many more times, on code nobody in the room wrote, without the reviewer's attention scaling to match.

## What the run takes from the kit

A workflow does not consume the kit whole. Pull-request verification uses eleven of the kit's seventeen components and leaves the rest idle. What it uses, and what the project has to supply for each, is the first thing worth drawing.

![What pull-request verification takes from the kit](diagram:p7-1-kit-touched-export)

The kit supplies mechanism. The rule registry gives every rule an identifier, a route and an owner, and a way to look rules up by change category. The validator runner executes each check and returns one of four results against a rule identifier. The test harness hook runs the project's own suites and reports per rule rather than per suite. The review skill reads a diff against the applicable rules and produces findings tagged to those rules[^bockeler-sensors]. Gate semantics decide what blocks and how many approvals a pass needs. The evidence schema fixes the shape of the record every run leaves. Three thin adapters bind all of this to wherever the agent runs, wherever the pull request lives, and wherever checks run unattended.

The project supplies meaning. For the export feature, the registry holds two rules that matter here. R-042 says the export honours row-level access, and it is routed to a gate: a validator checks it and a failure blocks. R-017 says any endpoint that produces a file declares a volume limit, and it is routed to judgment: the review skill looks for it and a person decides. The project sets a coverage threshold of eighty percent on the export module, a dependency-direction rule on the domain layer, and a test suite that includes a fifty-thousand-row load scenario. The change was declared tier 2 at planning: checks block, one human approval, no waivers on gate-routed rules.

One row in that table is empty on purpose. The evidence schema takes nothing from the project. The record shape is the one thing a project cannot customise, because the moment two projects leave different kinds of record, release readiness and incident review can no longer read across them.

## One run, step by step

The change is small. A date-range filter is added to the customer-record export. Revision 1 is pushed and a pull request opens.

![One run, step by step](diagram:p7-2-run-export)

Seven things happen, in order.

The change host fires the trigger. The kit reads the readiness record for this work item, which supplies the tier and the change categories, API and Data. Those select the rule set: R-042, R-017, the coverage threshold, the dependency check.

The deterministic checks run. R-042 passes. Coverage on the export module passes at eighty-four percent. The fifty-thousand-row load scenario fails with a timeout, because the new filter materialises the full result set before filtering it. The dependency-direction check returns could_not_run: the tool it needs is missing from the runner image.

The review skill reads the diff against the applicable rules and the constitution's section on data exposure. It produces one finding, tagged R-017: the endpoint streams a file and no volume guard or pagination is present. The finding is routed to judgment, so it is a question for a person, not a block.

The kit assembles the evidence record. Kit version 1.4.0, revision 1, four rules applied, two passed, one failed, one could not run, one finding, decision pending.

Gate semantics evaluate it. Blocked, for two causes: a gate-routed check failed, and another could not run. The R-017 finding is open but it is not what blocked.

The reviewer sees three lines. The load scenario failed, and the author fixes it. The dependency check could not run, and the runner's owner is notified. One R-017 finding to accept or dispute. No diff is read. No human approval is spent on a change that has already failed a rule.

The step most teams do not have is the fourth result. A check that could not run is not a check that passed, and it is not a check that was skipped with a reason. It is a run in which a rule was not enforced, and it blocks on its own cause. Without that state, the first broken runner image quietly turns every gate it hosts into a suggestion.

## Four ways out, and one through

When a run reaches the gate there are five things that can happen, and each has a destination and an owner.

![Four ways out, and one through](diagram:p7-3-exits-export)

A check failed. Blocked; the author fixes and pushes a new revision. Nobody is asked to approve and nobody reads the diff. Revision 1 took this exit on the load scenario.

A check could not run. Blocked, for a different cause; the runner's owner is notified. Never treated as skipped, never treated as passed. Revision 1 took this exit as well.

An agent finding is disputed. A person decides, and the decision and its reason are logged against the rule identifier. If one rule collects repeated disputes, the rule or the skill is wrong and the rule's owner hears about it. Revision 1 did not take this exit: the author accepted the R-017 finding and added the guard.

A rule is ambiguous. A check and a finding disagree, or a rule cannot be applied to this kind of change. The rule's owner is asked, and the route may change: guidance to judgment, judgment to gate, or the rule is split. The change waits, or proceeds under a logged exception.

Through. Every gate-routed check passed, every finding resolved, approvals match the tier. Merged, and the record closes for this revision.

The list is short because the workflow is narrow. That is a feature. A workflow with twelve exits is two workflows that have not been separated yet.

## The next revision, and what flowed where

Revision 2 streams the filtered rows instead of materialising them, adds the volume guard R-017 asked for, and lands on a runner image that now carries the dependency tool. Every check passes. The load scenario completes in a few seconds. One approval, and the change merges.

What matters more than the pass is what the failed revision sent back into the system.

![The next revision, and what flowed where](diagram:p7-4-flows-export)

Upstream, the run read the readiness record. Downstream, it left a verification record that release readiness will read, valid for this revision only; a new push invalidates it. Those two hand-offs are what make this a workflow in a system rather than a script in a pipeline.

Backwards, three conversions from Part 6 happened, each landing in a different place[^bockeler-harness].

The could_not_run had a stable cause, a missing tool on the runner image, so it became an installation check. The kit's doctor command now verifies that tool is present. The next runner without it fails at doctor, before any change reaches the gate. Brittle behaviour became a harness change.

The R-017 finding was something the specification should have prevented. The spec for the date-range filter never mentioned volume, so the rule was only met at review. It became a mandatory readiness question: any feature that produces a file must state a volume limit before it leaves specification. A misunderstood requirement became a readiness question, and the next export-like feature meets it before code exists.

The accepted finding became an evaluation case for the review skill: given the revision-1 diff and this rule set, does the skill flag R-017? A model or prompt change that stops catching it now fails the skill's evaluation before the skill is released again.

And one thing did not flow back. The load scenario failed, the code was fixed, the scenario passed. The test did its job. Nothing upstream needed to change for it. Not every failure reveals a gap in the system, and a feedback path that converts everything is as useless as one that converts nothing.

## What to measure

The workflow produces its own measures as a by-product of leaving a record. Five are worth watching, and none needs a new tool.

![What to measure](diagram:p7-5-measures-generic)

Escaped defects per merged change is the only one that says the workflow works rather than that it runs. Reviewer minutes per pull request says whether attention is spent on decisions or on reading, and it is only meaningful next to escaped defects: falling minutes with rising defects is skimming, rising minutes with rising volume is the bottleneck returning. Blocks by checks against blocks by people says whether the rules the team has been hurt by have become gates; every human block is a candidate rule. Agent finding acceptance rate says whether the review skill is worth reading, and both ends of the scale are bad: very low is noise, near total is rubber-stamping. The frequency of could_not_run says whether the gate is real.

Read them in pairs. A single number from that list, read alone, will justify whatever the reader already believed.

## Where this is ordinary, and where it is not

It is worth being plain about which parts of this picture are established practice and which are not.

Deterministic checks in a pipeline that block a merge are ordinary. Most teams with continuous integration have them. Coverage thresholds, dependency rules, test suites that gate: none of this is new, and a team that lacks it should build it before anything in this article that mentions an agent.

Rule identifiers that every check and every finding cite are less common. Most teams have rules as comments, wiki pages and the memory of the longest-serving reviewer. Giving each one an identifier, a route and an owner is not hard, but it is unusual, and it is the thing that makes findings, blocks and decisions comparable over time.

could_not_run as a first-class result is rare. Most pipelines report green, red, or skipped, and a missing tool typically produces a skipped or an error that someone waves through. Treating it as a block with its own cause is a small change with a large effect on whether the gate means anything.

An agent review whose findings are tagged to rules and cannot block is new, and its quality is unproven at the level of a whole team over a year. The evaluation case in the previous section is the mechanism for finding out.

Evidence that release readiness actually reads, with expiry by revision, is the least common of all. It is the difference between a workflow and a system, and it is where the earlier parts of this series have the least evidence to point to.

Someone reading this will say their checks are not that clean, or that no review skill can tell R-017 from a comment. Both objections may be right for a given team. The picture is not a claim that this is easy. It is a claim that this is what the pieces look like when they are all present, so that a team can see which ones it has.

## What remains open

Whether the review skill earns its place is the question this workflow cannot answer about itself. An acceptance rate and an evaluation set are the instruments, but a year of data from real teams does not exist yet, and until it does, treating agent findings as a helpful reader rather than a gate is the honest position.

How tiers should be set is unresolved. Tier 2 in this example means checks block and one person approves. Whether that person should be the author's peer, a designated owner, or anyone with the right permission, and whether the tier should be declared at plan or inferred from the change, are decisions the operating model has to make and the kit can only enforce.

Whether could_not_run should ever be waivable is a real argument. A strict reading says never: an unenforced rule is an unenforced rule. A practical reading says a tier-1 documentation change blocked by a broken security scanner is a cost with no benefit. The example takes the strict reading and logs the cost. Other teams will choose differently.

And the boundary of this workflow is a choice, not a fact. Pull-request verification here stops at the merge. Some teams would fold in the pre-merge deployment to a preview environment; others would split the agent review into its own workflow with its own owner. Where the lines go is less important than that they are drawn and that each side has evidence the other can read.

## Reference sheet

The five images above are the worked example. The same five, with the export story removed and every label made generic, are available as a reference sheet for teams that want to fill in their own rules, thresholds and tiers. The layout is identical, so a box in one has exactly one counterpart in the other.

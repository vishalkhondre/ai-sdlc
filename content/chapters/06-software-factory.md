# Software factory: Connecting workflows across delivery and operations

*Part 6 of Beyond Faster Coding*

Put a capable coding agent in front of every developer. Add a spec-driven flow. Connect the agent to the repository, the test runner and a few external systems. Add review automation, testing automation and CI. Draw the architecture diagram.

It looks like a software factory. It is a collection of tools.

![A collection of tools, or a connected system](diagram:sf-tools-vs-system)

The previous article ended with one workflow running well. Pull-request verification for the export feature had a trigger, checks that could block a merge, a reviewer with a specific question to answer, and a record of what happened. Then a second workflow appeared. Specification readiness started producing a record the verification workflow could read. A third followed at release. The incident review after the large-dataset failure read the release record and traced the gap back to a missing load scenario.

Somewhere in that sequence, something changed that no single tool or workflow accounts for. A decision made in production altered what the readiness check asked for the next time. Evidence from one phase configured the next. Nobody built that. It appeared when the workflows started sharing rules, evidence and feedback.

This series has used the term software factory for that state. The final article is about what it consists of, what it is not, and why it is better understood as something that emerges than as something that gets built.

## What the term is doing

"Software factory" is an old phrase with a new meaning attached. The industrial sense implied identical outputs from a fixed process, which describes almost no software work. The sense in use here is narrower: an operating model in which the delivery system, rather than any individual, carries the knowledge of what must be true, how it is checked, and what happens when a check fails.

A working definition: a connected engineering system in which human intent flows through structured artifacts, agent-assisted workflows, reusable harness capabilities, deterministic controls and human judgment, with production feedback continuously improving the system.

In that model the factory is the thing the team operates. The features it produces still vary. What stays fixed is the environment those features pass through.

Some large organizations have published accounts of running delivery this way at scale, with managed agents handling review, migration and repair across many repositories. Those accounts are useful for seeing the shape. They describe organizations with years of prior infrastructure investment, and their headline figures are self-reported. A team of ten should read them for the pattern, not the numbers.

## What it consists of

Looking back across the series, the factory is what the earlier parts add up to when they are connected.

**Shared rules.** One registry, with identifiers, routes and owners, that every workflow reads. The export access rule is checked at verification, referenced at release and cited in the incident review under the same identifier. When it changes, every workflow that depends on it is findable.

**Shared evidence.** One schema for what a run leaves behind, so the readiness record, the verification record and the release record are the same kind of thing. A release decision can read a verification result and know which revision it covered.

**Explicit hand-offs.** Defined rules for when evidence from one workflow supports a decision in another, and when it has expired. A verification result from a previous revision is not release evidence. An approval under the old access policy does not carry forward.

**One feedback path.**[^steering-note] What the system learns has a defined place to go. A defect becomes a regression test. A recurring review comment becomes a rule. A rule that keeps being violated becomes a deterministic gate. A production failure becomes an evaluation case. A misunderstood requirement improves the clarification step. A procedure the team keeps repeating becomes a skill. A brittle agent behavior becomes a change to the harness. The conversion chosen determines which workflow changes, and the change lands upstream of where the problem appeared.

**Ownership across workflows.** Someone owns each workflow. Someone also owns the connections between them, resolves conflicts when two workflows want different things, and judges whether the system as a whole is improving. That second role is the one most teams do not have yet.

**System-level measures.** Each workflow has its own metrics. The factory adds the ones that only make sense across the lifecycle: time from agreed requirement to usable release, escaped defects against throughput, reviewer load against volume, cost per change including agent and evaluation cost.

None of these is new to this article. What makes them a factory is that they are shared. Two workflows with separate registries, separate evidence formats and separate feedback paths are two workflows. The same two sharing all three are the beginning of something else.

## Two kinds of machinery

One distinction from the earlier articles is worth restating once, because the factory depends on it more than any single workflow does[^machinery-note].

Probabilistic machinery is good at understanding intent, exploring unfamiliar code, proposing designs, generating implementation, reviewing for patterns, reasoning through trade-offs and summarizing evidence. Deterministic machinery is good at compiling, running tests, enforcing dependency rules, validating schemas, checking policies, measuring thresholds and blocking invalid builds.

A factory needs both, and it fails when either is asked to do the other's job. If the architecture says the domain layer must never depend on infrastructure, an agent can be reminded, a reviewer can look, and a constitution can state it. But a tool can verify dependency direction on every change, and that is where final enforcement belongs. The point is not to remove human judgment. It is to stop spending it on things a machine checks perfectly well, so it is available for the questions a linter cannot answer: is this the right problem, is this trade-off acceptable, does this behavior match what the business meant, is this safe enough to release.

## What it is not

The term attracts three misreadings, and the series has argued against each.

It is not full autonomy. The seductive version is a requirement on Monday and production software on Friday, with nothing in between requiring a person. Some classes of work may get close to that. But treating the entire lifecycle as one autonomous workflow hides too much uncertainty: requirements contain ambiguity, brownfield systems contain undocumented assumptions, architecture contains trade-offs, testing contains judgment, and production contains reality. Humans set intent, define acceptance, make architectural decisions, resolve ambiguity and approve releases. The agent implements inside gates it cannot move. Where an organization permits automated merging for narrow, well-tested classes of change, the authority comes from an approved policy and configured permissions, not from the agent having run successfully. Autonomy that outruns controls is not maturity. It is exposure.

It is not a product to buy or a platform to build up front. The kit is a package. The workflows are units. The factory is the relationship between them once enough exist. A team that sets out to build the factory first will design connections between workflows it does not yet have, and get most of them wrong.

It is not a replacement for the operating model. Policies, risk tiers and decision rights still come from the organization's delivery framework. The factory is how those policies become enforceable and evidenced. When the two disagree, the policy wins and the disagreement is logged as a decision to make.

## The boundary is wider than the merge

A fourth misreading deserves its own section, because it is the one that makes the factory metaphor actively harmful.

Requirement goes in. Code comes out. That is the boundary most diagrams draw, and it is too narrow. A delivery system does not know whether it worked until the software meets reality. Production supplies the best engineering data a team has: escaped defects, incidents, rollbacks, performance regressions, security findings, support tickets, unexpected user behavior, operational toil.

If the factory boundary stops at the merge, none of that data has anywhere to go. It gets discussed in a retrospective and forgotten. If the boundary includes operations, the same data feeds the conversions listed above, and the system captures what the organization learns rather than relying on the people who happened to be in the room.

![The boundary is wider than the merge](diagram:sf-boundary-and-feedback)

That is what makes the factory improve over time. Not a model that is continuously learning, but an engineering system that keeps what its people find out.

## The condition that makes it real

The series has proposed one test: a defect found at operate changes what the specify check looks for next time.

That condition is harder than it sounds. It requires the incident review to produce a finding in a form the readiness workflow can consume. It requires the readiness workflow to have a place to put a new mandatory question or a new risk trigger. It requires someone to make the connection, and it requires the next specification for a similar feature to actually encounter the new check.

For the export feature: the large-dataset failure becomes a load scenario in the project's tests, a performance question in the readiness checklist for any feature that produces files, and possibly an evaluation case that gives the agent a specification with no stated volume limit and checks whether it asks. When all three exist and the next export-like feature meets them, the loop has closed.

A team can check this directly. Take the last three production incidents. For each, ask which upstream check changed as a result. If the answer is none, the workflows are running but the factory is not.

## How roles shift

Connecting workflows changes what people spend their time on. The pattern is consistent enough to state plainly.

Product roles move from writing requirements to owning a living specification and the decisions it leaves open. The readiness workflow makes those decisions visible earlier and attaches an owner to each.

Developers move from writing most of the code to directing an agent, verifying its output, and turning what they learn into gates and evaluation cases. The scarce skill becomes judgment about what to check, not fluency in writing the check.

QA moves from late validation to curating the scenarios that verification runs against: acceptance criteria that can be tested, evaluation cases for agent behavior, and the reference set of past defects that tells the team whether a workflow is catching anything.

Architecture moves from reviewing after the fact to writing rules that can be enforced mechanically, and from a serial gate to a registry owner.

Platform roles own the kit: its releases, its adapters, its installation checks, and the connections between workflows.

None of these is a new title. They are shifts in where existing roles spend their attention, and they happen whether or not anyone plans them. Planning them is better. The work does not disappear; it moves, and knowing whether generated software is correct, appropriate and safe becomes worth more than producing it quickly.

## Two risks that scale with the factory

The first is review fatigue. More workflows, more evidence and more agent output land on the same few people who approve things. The factory's answer is to move every mechanical check into a gate so reviewers see only decisions and exceptions, to budget and rotate review work, and to watch review latency and reviewer concentration as leading indicators. If the same names appear on every approval and comments get shorter, the system is failing quietly.

The second is skill erosion. A team that lets agents do all the implementation and all the first drafts stops getting the unaided repetitions that keep judgment sharp. The factory depends on that judgment at every human decision point. Deliberately keeping some core tasks unassisted, rotating who frames the problem and who checks the output, and treating agent output volume as never equivalent to capability are the controls. They are cheap to state and easy to skip.

## Sequence

The order this series has followed is also the order that works in practice.

Build the deterministic floor first: a quality command that runs the same way everywhere, a handful of validators for rules the team has already been hurt by, a rule registry, an evidence schema. Then one workflow, end to end, run enough times to have a metric. Then a second workflow, and the first hand-off between them, which will expose every assumption the first workflow made. Then the feedback path, tested against a real incident. Then more.

Starting with "we need to build a software factory" is the reverse of this. It invites architecture before evidence, platforms before workflows, tools before problems. The temptation at every step is to skip ahead to the interesting part: more skills, more agents, more automation. Each skip produces the same failure, a rich upper layer sitting on a floor that cannot hold it. The floor is dull. It is also the only part that makes the rest safe.

## What remains open

Whether the factory metaphor survives contact with reality is not certain. Factories imply repeatability of output, and software's value is in its variation. The metaphor is useful for the shared, fixed environment and misleading for everything that passes through it. A better name may emerge; the structure will outlast whichever word wins.

How much of this a small team can afford is unresolved. The published examples come from organizations with dedicated platform groups. A team of eight building a product while building its harness is making a trade-off every week, and the return arrives later than the cost. The honest answer is that the floor is affordable for almost anyone, the second workflow is affordable for most, and the full connected system may be a platform-team investment that smaller teams adopt rather than build.

Evaluation cost is the quiet constraint. Every skill needs an eval suite, every model change needs a rerun, and the number of things that count as a model change keeps growing. Whether that cost stays manageable, or whether it becomes the new verification bottleneck, will not be clear for a while.

And there is the question the whole series has circled: where human judgment stays essential, and for how long. The answer given here is intent, architecture, ambiguity, trade-offs and approval. That answer is right today. Whether it is right in three years depends on things no article can settle.

## Closing the loop

The first article in this series began with a claim: faster coding is only part of the software delivery problem. Implementation got fast. The phases around it did not, and the pressure moved to specification upstream and verification, review and operations downstream.

Five articles later, the response to that claim has a shape. Harness engineering designs the environment an agent works inside. The Engineering Kit packages the parts of that environment worth sharing. A workflow puts the environment to work for one delivery decision and leaves evidence behind. And the software factory is what appears when enough workflows share rules, evidence and feedback, so that what production teaches changes what specification asks.

![Six articles, one system, and where the evidence is](diagram:sf-series-evidence)

The parts of that picture with the most evidence behind them are the early ones: deterministic gates, specifications as the interface to the agent, evidence as a byproduct, the reviewer's attention spent on decisions rather than proofreading. The parts with the least are the late ones: full connection, sustained feedback, and the operating model that keeps it all honest as the volume rises. That is roughly where the industry is too. The floor is well understood. The upper layers are being built in public, by teams finding out what holds.

If there is one shift underneath all six articles, it is not from humans writing code to agents writing code. It is from optimizing the act of coding to engineering the system that produces software. The organizations with the most agents will not necessarily have the advantage. The ones with the best system around them might.

[^machinery-note]: This is the same distinction Böckeler makes between *computational* controls (deterministic and fast, run by the CPU) and *inferential* controls (semantic analysis, AI review, LLM-as-judge), with the same conclusion: the two are complementary, and the deterministic side is where final enforcement belongs. See [Harness Engineering for Coding Agent Users](https://martinfowler.com/articles/harness-engineering.html).

[^steering-note]: Böckeler calls the human practice of improving guides and sensors from recurring agent failures the *steering loop*. The feedback path here is that loop with its conversions named. See [Harness Engineering for Coding Agent Users](https://martinfowler.com/articles/harness-engineering.html).

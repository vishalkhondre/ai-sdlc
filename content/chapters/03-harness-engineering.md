# Harness engineering in the SDLC: Designing the environment around the agent

*Part 3 of Beyond Faster Coding*

"Follow the architecture. Write tests. Make sure it is secure."

These are reasonable instructions to give a coding agent. They also leave a lot unresolved.

Where is the architecture documented? Which tests should run? What does "secure" mean for this change? Can the agent inspect the application's behavior? What prevents it from skipping a check or working around a failure?

The quality of the result depends partly on how the working environment answers those questions.

The previous article explored where pressure can build when implementation accelerates. This article looks at how to design the environment that helps an agent work through those constraints.

## What harness engineering means here

An agent harness is the surrounding software and configuration that gives a model access to context, tools, execution and feedback[^bockeler-harness].

In this series, **harness engineering** means deliberately designing and maintaining that environment within the software lifecycle: what the agent can discover, what it can do, how its work is checked and when a person needs to decide.

The term comes from published engineering practice. OpenAI's account of harness engineering describes organizing repository knowledge, making application behavior accessible to agents and enforcing architectural constraints through automated checks[^openai-harness]. Böckeler's treatment on martinfowler.com supplies the vocabulary this series leans on most: the harness as everything except the model, and the split between controls that steer the agent before it acts and controls that observe it afterwards[^bockeler-harness].

Much of the underlying work will be familiar: documentation, development environments, tests, access controls and CI. The challenge is making those pieces work together for an agent that can act on the codebase.

![An agent is a model plus its surroundings](diagram:model-plus-surroundings)

A useful place to begin is the customer-record export feature from Part 2.

## Give the agent a usable starting point

Suppose the agent receives a specification for exporting customer records.

It needs more than the feature description. It may also need the access-control model, the approved data-access pattern, examples of existing endpoints and instructions for running relevant tests.

Those sources should be discoverable, current and consistent[^bockeler-context].

A short entry point can direct the agent to the relevant material. The export task can then reference its acceptance criteria and the particular constraints it must satisfy.

The same applies to execution. If starting the application requires undocumented steps, or test data must be assembled manually, the agent's ability to verify its work is limited.

For this hypothetical feature, a useful environment would provide:

* A repeatable way to start the application.
* Synthetic records belonging to different customers.
* Test identities with different permissions.
* Commands for running the relevant checks.
* Access to local logs when something fails.

These capabilities make it possible to investigate behavior while implementing the change.

## Separate instructions from permissions

Instructions describe how the agent should work. Permissions determine which actions the environment allows.

For the export feature, the agent might need to edit application code, run tests and inspect a local database. It does not automatically need production credentials or authority to deploy.

That distinction should be reflected in tool access and environment configuration.

The same principle applies to verification controls. If the agent can freely remove a required check and then report success, that check provides weak assurance. Changes to protected controls need their own review and enforcement.

Human decision points should also be specific. An unresolved question about which customer fields may be exported needs a decision from someone authorized to define that behavior.

"Ask when unsure" is helpful guidance. Naming the decisions that require escalation makes the boundary clearer.

## Decide how each rule will be checked

Consider the requirement: users must only export records they are permitted to access.

Several mechanisms can support it.

The specification describes the expected behavior. A reusable skill can guide the agent toward the established authorization pattern. Automated tests can attempt exports using different identities and customer records. A reviewer can examine whether the scenarios cover the relevant access boundaries.

Each contributes different evidence. An instruction asks; a gate refuses.[^guides-sensors-note]

Some architectural rules are more directly checkable. If route handlers must not import database models, a dependency check can detect prohibited imports and fail CI.

Other questions remain matters of judgment: is the access policy appropriate? Does the export expose a combination of fields that creates an unexpected risk?

The engineering task is to decide what can be checked reliably and what still needs an explicit judgment call. Applied to every rule a team cares about, that decision turns a constitution from a list of aspirations into an inventory. Each clause is either backed by a check or explicitly assigned to someone's judgment. The gap between the two is visible, and closing it is ordinary engineering work rather than a matter of writing better prose.

![One rule, four mechanisms, three different roles](diagram:one-rule-four-mechanisms)

An AI review can help identify concerns. Its conclusions should be assessed according to the evidence behind them; a confident response is not equivalent to a reproducible check.

## Make failures useful to the agent and the reviewer

A check that reports "policy violation" gives little direction.

A more useful result identifies the violated rule, the affected location and the relevant guidance. A failing export test should show which identity made the request, which records were expected and what was actually returned.

That feedback supports correction without requiring a person to reconstruct the failure.

The workflow also needs a stopping condition. If the agent repeatedly fails the same check, lacks a required environment or encounters contradictory requirements, it should surface the blocker.

A failed check, a skipped check and a check that could not run are different outcomes. The evidence should preserve that distinction.

For a pull request, the useful record might include the change identifier, checks executed, results, unresolved concerns and decisions still required. Reviewers can then see what has been established and what remains open.

## Evaluate the harness as well as the software

Application tests examine the software's behavior. Harness evaluations examine whether the agent and its environment handle representative tasks as intended.

For example, an evaluation could give the agent an export requirement with an unresolved access rule. Does it identify the missing decision before proceeding?

Another could present an architectural violation. Does the workflow detect it, provide useful feedback and retain evidence of the result?

These evaluations can be repeated when prompts, skills, tools or model versions change. They help reveal whether an environment update improves one behavior while weakening another.

A few successful runs provide limited evidence. The aim is to build a representative set of situations, including failures and cases where escalation is the correct outcome.

## The harness is not a phase

It is tempting to draw harness engineering as a step in the lifecycle, somewhere between planning and implementation. That is the wrong picture.

The harness surrounds every phase where an agent works. A specification-readiness check is harness. A quality command that runs before every push is harness. A release gate that requires evidence of a rollback path is harness. The review that turns an escaped defect into a regression test is harness.

What connects them is that they share the same rules, the same evidence format and the same feedback path. A rule added because of a production incident should be enforced at the point where it would have prevented the incident, which is usually far upstream of where the incident was discovered.

## Turn delivery lessons into maintained capabilities

Suppose an export defect reaches production because a background job applies different access rules from the interactive endpoint.

The immediate fix addresses the defect. The follow-up should examine why the delivery workflow missed it.

Perhaps the specification omitted background execution. Perhaps the tests covered only the endpoint. Perhaps the agent could not run the worker locally.

Those causes call for different improvements: clearer requirements, an additional test or a better development environment.

![One escaped defect, three causes, three different fixes](diagram:one-defect-three-fixes)

Adding another instruction to a growing document may help in some cases. In others, the useful change is an executable check or a capability the agent previously lacked.

Someone needs to own those improvements, review them and remove obsolete guidance. The harness is part of the engineering system and requires maintenance as that system changes.

A practical first step is to choose one recurring failure and ask what would have helped the agent or reviewer detect it earlier. Introduce that capability, exercise it on real changes and assess whether it reduces rework without creating excessive friction.

## What remains open

How much harness a small team can build while also shipping a product is not settled. Every hour spent on validators and evaluations competes with an hour on features, and the return arrives later than the cost.

Nor is it clear how much of the harness should live inside a particular coding tool. Rules and gates in CI are portable. Instructions and hooks configured in one agent's settings are not, and teams using more than one tool will feel that difference.

There is also a quieter question. The environment is already the difference between a team whose agent output can be trusted and one whose output cannot. Whether someone is explicitly responsible for that environment, or whether it remains an accident of who happens to care, is in most organizations still undecided.

As these capabilities prove useful, the next challenge is reuse: how do teams share them, version them and apply them consistently across different coding tools?

**Next: Engineering Kit — packaging the reusable engineering environment.**

[^guides-sensors-note]: Böckeler draws the same line as *guides* (feedforward controls that steer the agent before it acts) and *sensors* (feedback controls that observe after it acts), and further splits sensors into computational (deterministic, fast) and inferential (semantic, AI-based). The specification and the skill here are guides; the test is a computational sensor; the reviewer's question is judgment that no sensor replaces. See [Harness Engineering for Coding Agent Users](https://martinfowler.com/articles/harness-engineering.html).

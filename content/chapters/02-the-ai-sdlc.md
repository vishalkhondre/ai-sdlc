# The AI SDLC: Same phases, different bottleneck

*Part 2 of Beyond Faster Coding*

A pull request is ready. The feature runs locally. The agent has generated tests, and they pass.

Then the review begins.

What should happen if the request is submitted twice? Can a user access another customer's records? Will the database migration work with existing data? What happens if the deployment needs to be rolled back?

The implementation is available. The answers are still being worked out.

This is where the distinction between coding speed and delivery speed becomes practical. Time saved during implementation can be absorbed by clarification, verification and rework elsewhere.

The first article introduced the environment around AI coding agents: the rules, tools, checks and feedback that support their work. To understand where that environment needs attention, it helps to follow a change through the software lifecycle.

## The phases remain. The work within them changes.

Intent, specification, planning, implementation, verification, review, release and operations still serve distinct purposes.

These activities overlap and repeat. Testing can expose a specification gap. Operational feedback can change a design decision. They do not need to become a sequence of rigid handoffs.

AI can assist across all of them. But generating an artefact does not, by itself, establish that the purpose of the activity has been met.

A specification needs to express the right behavior. A test needs to challenge that behavior meaningfully. A release decision needs evidence about the version that will actually run.

![Same phases, different bottleneck](diagram:sdlc-pressure-shift)

## Before implementation: unresolved decisions become assumptions

Consider a hypothetical feature: allowing users to export customer records.

"Add an export button" sounds straightforward. An agent can produce a button, an endpoint and a downloadable file.

But the request leaves several decisions open:

* Which records may each user export?
* Which fields must be excluded?
* How should large exports behave?
* What should happen if the export fails?
* Does the action require an audit record?

When those decisions are missing, implementation can proceed through assumptions. The result may be technically coherent while differing from what stakeholders intended.

![Unresolved decisions become assumptions](diagram:export-open-decisions)

Spec-Driven Development[^spec-kit] helps by making expected behavior and constraints explicit before implementation. The useful question is whether the specification resolves the decisions that matter for this change.

That calls for proportionate detail. A small display adjustment and a customer-data export need different levels of scrutiny. Readiness means enough clarity to proceed responsibly, with remaining uncertainty made visible.

Planning has a similar responsibility. It should identify affected components, architectural boundaries, dependencies and how the change will be verified. A long task list is useful only if it captures the work required to deliver the intended result.

## During implementation: keep the change understandable

Faster code generation can make it tempting to implement an entire feature in one pass.

The resulting change may span the interface, API, database, permissions and deployment configuration. Even when each part appears reasonable, understanding how they interact takes effort.

For the export feature, a reviewer may need to trace access restrictions from the interface through the API to the database query. A large change makes that harder.

Small, coherent changes and clear explanations help preserve reviewability. An agent's summary can assist, but reviewers still need to check it against the actual changes. A useful implementation is one that can be inspected, tested and maintained.

Coding remains difficult work, particularly in unfamiliar or complex systems. The point is to examine what happens when implementation capacity increases faster than the capacity to evaluate it.

## After implementation: verification needs an independent basis

Passing tests are evidence about the scenarios those tests cover.

For the export feature, a test that confirms a file downloads says little about whether it contains only permitted records.

If an agent generates both the implementation and its tests from the same incomplete understanding, both may reflect the same mistaken assumption.

Verification therefore needs a basis beyond the implementation itself: acceptance criteria, access rules, interface contracts, representative data and relevant failure scenarios.

![Verification needs an independent basis](diagram:verification-independent-basis)

Different questions need different checks:

* Functional tests examine expected behavior.
* Security checks examine access boundaries and exposure.
* Performance tests examine behavior under defined loads.
* Human review considers design choices, missing scenarios and trade-offs.

An automated check can reliably enforce a specific rule. Engineering judgment helps determine whether the rules and scenarios are sufficient.

The distinction matters when deciding what "all checks passed" actually means.

## Release and operations: complete the delivery loop

A change can pass its tests and still be difficult to deploy or support.

The export feature might need configuration, resource limits, monitoring and a way to disable it if it causes problems. A database change might require a migration strategy that affects rollback.

Release readiness brings those concerns into the delivery decision.

Operations then provides evidence that earlier stages could not fully supply. Perhaps exports time out at a volume the tests never covered. Perhaps users interpret an option differently from the specification.

Resolving the immediate issue is one part of the response. The next question is which earlier assumption or check needs to change.

That might mean revising an acceptance criterion, adding a regression test, improving a performance scenario or updating a release check.

## Find where delivery actually slows down

When implementation gets faster, the pressure tends to move in two directions. Upstream, specification readiness decides more of the outcome, because an agent will build whatever the specification leaves open. Downstream, verification and review absorb more change than before, and each change arrives looking finished. Release and operations then determine whether anything learned in production makes its way back to the earlier phases.

That pattern is common, but it is not universal, and it is not a substitute for looking.

A team may be waiting for requirements decisions. Another may have a growing review queue. Another may spend most of its time repairing unreliable tests or coordinating deployments.

Useful signals include:

* Where changes spend time waiting.
* How often work returns for clarification or correction.
* How much reviewer effort each change requires.
* Which defects escape existing checks.
* How long it takes to move from an agreed requirement to a usable release.

These observations help identify a worthwhile next improvement. If review is overloaded, generating more code may increase the queue. If requirements repeatedly change during testing, the next investment may belong in specification readiness.

What is not yet clear is whether the downstream pressure is a transition cost that eases as more checks move into the pipeline, or a lasting feature of agent-assisted delivery. The answer probably differs by team, and the signals above are the way to find out.

The opportunity is to connect implementation speed with sufficient clarity, verification capacity and operational feedback across the lifecycle.

That leads to the next question: how do we deliberately build those capabilities around an AI agent?

**Next: Harness engineering in the SDLC — designing the environment around the agent.**

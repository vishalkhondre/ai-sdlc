# Workflows: Making one part of the SDLC repeatable, measurable and improvable

*Part 5 of Beyond Faster Coding*

A pull request arrives with an agent-generated summary: the feature is complete, tests pass, and the change is ready for review.

The reviewer still has to reconstruct what happened.

Which requirements were checked? Did the tests cover access restrictions? Did any checks fail to run? Does the evidence apply to the latest commit? Who needs to resolve the remaining questions?

An Engineering Kit can supply rules, validators, skills and evidence formats. A workflow brings those capabilities together for a specific delivery decision.

This is where the ideas in this series become testable. A team can run a workflow against an actual change, inspect what it produces, and find out whether it improves delivery.

## Start with a decision the workflow must support

"Automate code review" leaves a lot undefined.

A more useful starting point is:

> For this pull request, establish whether the required checks and reviews support merging the current revision, and make any remaining blockers explicit.

That statement gives the workflow a boundary. It starts when a pull request is ready for verification and produces a recorded outcome: ready for merge, changes required, or blocked by missing evidence or a decision.

A blocked change can return through the workflow once the issue is resolved. Each run preserves what was assessed and what happened.

Release readiness remains a separate question. Passing this workflow establishes that the agreed conditions for merging have been met. Deployment configuration, migration safety and operational readiness may require additional evidence.

A workflow can cross several SDLC activities. Pull-request verification may revisit specification, run tests and require design review. Its boundary comes from the decision it supports.

## Define what a run needs

Return to the customer-record export feature from the earlier articles.

Users can request a downloadable file of customer records. The agreed requirements define which records they may access, which fields must be excluded, and whether the export must be audited.

The verification workflow needs those requirements alongside the implementation.

| Element | Definition for this workflow |
|---|---|
| Trigger | A pull request is marked ready for review; relevant changes trigger reassessment |
| Inputs | Change and target revisions, agreed acceptance criteria, applicable rules and project test configuration |
| Agent task | Compare the change with the requirements, identify potential gaps and cite supporting locations |
| Automated checks | Run required tests and validators; establish whether required evidence is present and current |
| Guardrails | The reviewing agent has read-only access; check results come from the execution system |
| Human decision | Assess unresolved behavior, design choices and the adequacy of verification |
| Outputs | Check results, review findings, decisions and an aggregate status |
| Feedback | Route discovered gaps to the relevant requirement, test, validator or agent evaluation |
| Owner | A named role responsible for the workflow's behavior and maintenance |

Missing inputs should produce a visible outcome. If the export access policy has not been agreed, the workflow identifies that dependency and routes it to the responsible person.

Otherwise, an agent may fill the gap with a plausible interpretation, and subsequent checks may validate that interpretation.

Verification effort should reflect the change. Readiness or planning can assign an initial risk tier, while affected components and mandatory rules determine which checks apply. The assessment needs to be revisited if implementation expands the scope.

For example, an export access rule applies because the feature handles protected records. The risk tier helps determine the depth of verification; a low-risk label does not remove an applicable requirement.

The run records its expected checks before assessing the results. This makes a missing check visible, even when every check that actually ran reports success.

## Walk one change through the workflow

Consider a hypothetical implementation in which the export endpoint creates a background job. The endpoint checks the user's permissions, but the worker retrieves records using a broader query.

The interface behaves correctly. An ordinary test confirms that a file downloads.

The verification workflow needs to examine the access boundary across both parts.

**First, establish the scope.**

The run records the pull-request revision, the target revision used for verification, the Engineering Kit version and the applicable configuration. It identifies the acceptance criteria and rules being assessed.

A change to the worker brings the export access tests into scope. If applicability is uncertain, the workflow requests review or uses the broader agreed check set.

The agent can help identify affected areas. Required checks follow controlled selection rules, with any exclusions recorded and explained.

**Next, ask the agent to examine the change.**

The reviewing agent traces the request from the endpoint into the worker. It compares that path with the access policy and identifies a possible gap: the worker query may include records outside the requesting user's permitted scope.

A useful finding includes the code locations, the requirement involved and the reason for concern.

That gives the reviewer something to investigate. The finding itself does not establish whether the code is correct.

**Then, run the checks.**

A project-owned access test supplies records from two customers and requests an export as a user entitled to only one customer's records.

The expected result comes from the project's access policy. The Engineering Kit supplies the execution and reporting conventions.

In this example, the test detects an unauthorized record in the file. The required check fails, and the configured repository control blocks the merge.

The developer or implementation agent corrects the worker query and submits a new revision. The relevant checks run again.

The reviewing role remains separate: it examines the proposed correction without changing the implementation or its acceptance conditions.

**Finally, resolve the remaining questions.**

The tests now pass. A reviewer still examines whether the scenarios cover the intended behavior.

What happens if access is revoked after the job is queued but before it executes? Should the worker use current permissions or permissions captured at submission?

A passing test suite does not resolve an unspecified policy. The workflow records the question and assigns it to the responsible product and security owners.

Suppose they decide that the export must respect permissions at execution time.

That decision updates the acceptance criterion. A regression test queues an export, revokes access and then executes the job. It checks that the resulting behavior follows the agreed policy.

The implementation is assessed against the updated requirement. Once the required checks pass and the outstanding review decisions are completed, the workflow can report the current revision as ready for merge.

The run now tells a complete story: what failed, what changed, which decision was needed and what evidence supports the outcome.

![One change through the workflow](diagram:wf-one-change-walkthrough)

## Keep responsibilities explicit

The agent traces the change and proposes findings that can be inspected. Automated checks evaluate defined conditions and record their results. People resolve ambiguous requirements, assess trade-offs and challenge whether the verification is sufficient.

Each has limits. An agent can miss a path, a test can encode the wrong expectation, and a reviewer can overlook a scenario.

The workflow should make those limits visible and define how concerns are resolved.

![Three roles in every workflow](diagram:wf-three-roles)

Changes to tests, CI configuration, permissions or acceptance criteria may be legitimate parts of implementation. They need review before they alter the conditions used to accept the change.

An agent should not be able to make its own work acceptable simply by weakening a required check.

## Use the same structure upstream

A specification-readiness workflow fills the same roles differently.

The trigger is a specification marked ready for planning. The agent looks for ambiguity, missing edge cases, unstated constraints and acceptance criteria that cannot be tested.

Automated checks establish structural completeness: required sections are present, acceptance criteria have identifiers, and mandatory questions have recorded responses.

Those checks establish that information is present. Assessing whether the responses are adequate requires further review.

The product owner resolves intended behavior, while engineering or security owners assess relevant constraints. The output is a readiness record containing the decision, the requirement revision and any remaining conditions.

For the export feature, this is where "which records may each user export?" should be addressed before implementation.

The readiness record also captures an initial risk assessment. Together with the actual change scope, it informs later verification.

Workflows can be built one at a time while exchanging useful evidence. If implementation introduces a background worker that planning did not anticipate, the earlier assessment needs to be revisited.

## Design the failure paths as carefully as the successful path

A workflow becomes dependable when it handles interruptions predictably.

| Situation | Required response |
|---|---|
| A check detects a violation | Preserve the result, return it for correction and reassess the changed revision |
| A required check cannot run | Record the missing prerequisite and keep the run blocked |
| A requirement is ambiguous | Route the question to its owner and record the resulting decision |
| An agent finding is rejected | Retain the reviewer's reason so recurring false alarms can be investigated |
| An exception is requested | Follow the established approval policy and record its scope, rationale and expiry where applicable |

A test failure and an unavailable test environment need different responses. Treating both as a generic failure makes diagnosis harder. Treating either as a pass misrepresents the evidence.

Agent retries also need a boundary. A workflow might allow one attempted correction followed by another verification run, then escalate repeated failure to a person.

The appropriate limit depends on the task. It should live in the workflow definition, together with the conditions that require immediate escalation.

Exceptions need similar clarity. An approved exception records an authorized departure from a requirement; the underlying failed or missing check remains visible.

## Make the outcome easy to inspect

The reviewer should be able to understand the run without reading every log.

For the export feature, the record should show:

* Scope assessed: code, target, requirement and configuration revisions.
* Required checks: expected checks, actual results and supporting reports.
* Agent findings: concerns, references and their disposition.
* Human decisions: approvals, unresolved questions and any exceptions.
* Overall outcome: ready for merge, changes required or blocked, with reasons.

The underlying reports remain available for investigation.

Evidence also needs rules for continued validity. A new commit, a changed target branch, a revised requirement or a relevant configuration update may require checks or approvals to be repeated.

For example, an approval based on the old export access policy should not automatically carry forward after that policy changes.

The distinction from Part 4 still applies: a reported failure prevents a merge only when the repository enforces it. The workflow must establish whether that enforcement is active, or report that it could not be verified.

## Measure whether the workflow earns its place

Before introducing the workflow, observe how comparable changes are handled.

How long do they wait for review? How much time do reviewers spend finding missing information? How often does work return for clarification? Which problems are discovered after merging?

Then track a small set of measures.

| Measure | What it helps assess |
|---|---|
| Time from review-ready to merge-ready | Whether the workflow improves progress through verification |
| Reviewer effort per change | Whether evidence reduces investigation or creates more work |
| Confirmed findings and false alarms | Whether checks and agent findings are useful |
| Blocked time by reason | Whether delays come from defects, unclear requirements or infrastructure |
| Escaped defects relevant to the workflow | Where its coverage remains inadequate |
| Execution and maintenance cost | Whether the benefit justifies continued operation |

Interpret these alongside change size and risk. A display adjustment and a new export capability should not be treated as equivalent observations.

Faster review can coexist with weaker verification. More findings can mean better detection or excessive noise.

Repeated use helps reveal these differences. A successful demonstration establishes feasibility; subsequent runs expose reliability, friction and maintenance cost.

## Turn a discovered gap into a tested improvement

Suppose the export feature later fails when users request a much larger dataset.

The immediate response restores acceptable behavior. The workflow owner then examines what earlier verification missed.

Perhaps the project lacked a representative load scenario. Perhaps the test existed but was excluded by the selection rules. Perhaps it ran and its failure was incorrectly treated as optional.

Each explanation leads to a different change.

A new load scenario belongs with the project's requirements and tests. A faulty selection rule may belong in the shared Engineering Kit. A misleading result state may require a change to the workflow itself.

The follow-up should identify an owner, the proposed correction and how it will be validated. The revised check or workflow then needs to be exercised against the failure scenario and against valid behavior.

If the gap involved an agent repeatedly overlooking background execution, a corresponding evaluation case can test whether revised guidance improves that behavior.

Some lessons remain specific to one project. Others justify a shared update after validation. This preserves the boundary established in Part 4: shared capabilities support project intent, while each project remains responsible for its own expected behavior.

## Expand when there is evidence to support it

A functioning workflow can be tried on another repository, assessed by another reviewer and challenged with known failure cases.

That exposes hidden dependencies: an undocumented setup step, an assumption about the test environment, or a decision that only the original author knows how to make.

Expansion also introduces duplication. Specification readiness, pull-request verification and release readiness may request similar evidence or repeat the same approval.

Shared evidence formats help with compatibility. Ownership and explicit reuse rules are needed to decide whether an earlier result still supports a later decision.

A pull-request test result may support release readiness. It may also cover a different revision or omit a deployment-specific concern.

Connecting workflows requires those distinctions to remain visible.

![Workflows hand each other evidence](diagram:wf-evidence-handoff)

## What remains open

For small changes, how much verification is enough?

A lightweight path may reuse existing automation and require little additional review. Choosing that path still depends on impact: a two-line change can alter an access boundary.

Workflow boundaries also need to earn their place. Readiness and planning might work well together. Verification and review might share one coordinated flow. Separate workflows make sense when they support distinct decisions without adding unnecessary handoffs.

The practical question is whether people can make better delivery decisions with less reconstruction, while failures lead to specific, tested improvements.

As more workflows share evidence, controls and feedback, responsibility extends beyond any individual run. Someone must maintain the connections, resolve conflicting requirements and judge whether the overall delivery system is improving.

That is the operating model the final article will explore.

**Next: Software factory — connecting workflows across delivery and operations.**

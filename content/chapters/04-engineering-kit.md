# Engineering Kit: Packaging the reusable engineering environment

*Part 4 of Beyond Faster Coding*

Suppose a team has built an effective environment for AI-assisted development.

Its coding agent can find the architecture, follow an approved implementation pattern, run meaningful checks and produce evidence for review.

Now a second team wants the same setup.

The easiest handover is to copy the folder: instructions, skills, scripts and CI configuration. The second team adapts it. Over time, the copies diverge. A validator improves in one repository, but the other continues running the older version.

The question becomes practical: how do teams share this environment while keeping its behavior understandable and its updates manageable?

![Copy the folder, or install a version](diagram:kit-copy-vs-install)

In this series, **Engineering Kit** is the working name for a versioned, installable package of reusable engineering capabilities. What follows is a design proposal for that package.

The kit does not replace the specification process, which supplies the sequence from intent to tasks. It does not replace the coding tool. It supplies the environment around both.

## Package a complete capability

The previous articles used a customer-record export feature to explore specification, verification and agent behavior.

Take one requirement: users may export only records they are permitted to access.

Packaging that capability involves several connected parts:

* The rule and its scope.
* Guidance for applying the approved authorization pattern.
* Tests that exercise access boundaries.
* Commands for running those tests.
* CI integration and required-check configuration.
* A record of results and remaining gaps.
* Evaluations of how the agent uses the guidance.

Each part has a distinct purpose. A skill helps the agent implement the pattern. Tests examine particular behaviors. Review determines whether the policy and scenarios are appropriate. Repository controls determine whether a failed check prevents a merge.

A reusable capability keeps those relationships visible.

## Organize the kit around four layers

The package needs a structure that supports reuse without erasing project differences.

| Layer | What it contains | Example |
| --- | --- | --- |
| **Shared core** | Rule registry, command interfaces, evidence schemas and common utilities | Consistent result states and rule identifiers |
| **Technology profiles**[^harness-template] | Validators and guidance for supported stacks | Dependency checks for a Python API |
| **Tool adapters** | Bindings for coding agents, IDEs and CI systems | Instructions and integrations that invoke shared commands |
| **Project configuration** | Applicable rules, local paths, test bindings, thresholds and exceptions | The project's access-test suite and authorization fixtures |

Within those layers, the package contains standards, validators, skills, evaluation scenarios, integration assets and release information.

![Engineering Kit architecture: operating model above, process spine, the four-layer kit, execution surfaces below, and the kit's own loop](diagram:engineering-kit-architecture)

The shared core should have as little dependence on a particular coding tool as practical. Adapters handle the tool-specific behavior.

That separation makes portability testable. If a team changes agents, it can check whether the same validators still run and whether the new adapter supplies the required context and evidence. The effort will depend on the tools and integrations involved.

## Make the rule registry the connecting structure

A rule identifier connects policy, guidance, checks and evidence.

Without that connection, a constitution may contain one expectation, a skill may describe another and CI may enforce something narrower than either.

For the export feature, a registry entry looks like this:

```yaml
id: SEC-004
statement: Users may export only authorized records.
owner: security-lead

verification:
  gates:
    - check: export-access-tests
      implementation: project
  judgment:
    - decision: Approve export access policy and test scope
      owner: product-and-security

guidance:
  - skill: authorization-pattern

known_gaps:
  - Background-worker execution is not yet covered.
```

The examples in this article illustrate a package schema; they are not tied to an existing tool.

This entry deliberately combines automated checks, judgment and guidance. They address different aspects of the same requirement.

The known gap also matters. Passing the listed tests does not establish that every execution path applies the access policy correctly.

The registry gives the team somewhere to trace dependencies. A validator names the rules it checks. A skill names the rules it supports. Evidence identifies the checks executed against those rules.

![One identifier connects policy, guidance, checks and evidence](diagram:kit-rule-as-hub)

It also makes coverage visible: which rules have automated checks, which require judgment, which remain guidance-only and where coverage is incomplete.

Those counts help prioritize work, but they are not a maturity score. A critical access-control gap deserves more attention than several low-impact formatting rules, and some expectations appropriately remain matters of judgment.

## Give validators and skills different acceptance criteria

Validators and skills need different forms of verification[^bockeler-sensors].

For an executable check, the team needs known passing and failing cases, understandable failure messages and defined behavior when prerequisites are missing. A dependency validator should reject a prohibited import and accept a permitted one.

Repeatability also depends on the environment. Shared commands reduce differences between local execution and CI, but databases, dependencies and configuration can still affect results.

A skill shapes how an agent approaches a task. Its effect needs evaluation across representative scenarios.

A skill manifest makes those expectations explicit:

```yaml
name: authorization-pattern
version: 0.1.0
supports_rules:
  - SEC-004

activation:
  task_categories:
    - data-access
    - export-endpoint

evaluation_suite: authorization-pattern-v1
required_behaviors:
  - Identify unresolved access-policy decisions
  - Use the approved authorization mechanism
  - Preserve required checks
reports: eval-results/authorization-pattern/
```

The manifest describes intended behavior. The adapter and agent determine how activation actually works, so that behavior needs testing too.

Evaluation reports should identify the skill version, model, adapter, environment, scenarios and observed outcomes. Repeated trials help assess variability.

A headline result such as "11 of 12 passed" is insufficient without knowing which scenario failed. Missing a critical authorization requirement has different implications from producing an unnecessarily long explanation.

Evaluation history provides evidence for a release decision. It does not guarantee future performance. A new model or adapter needs assessment in the configuration the team intends to use.

## Leave project intent with the project

The kit supplies reusable mechanisms. The project supplies the meaning those mechanisms must preserve.

For the export feature, the project defines:

* Which identities may export which records.
* Which fields are excluded.
* What background processing is allowed to do.
* What audit information is required.
* Which workloads and performance limits matter.

The kit can supply an access-testing pattern, fixture utilities and a consistent runner. It cannot infer those product decisions merely because it has an authorization skill.

![The kit supplies the mechanism. The project supplies the meaning.](diagram:kit-mechanism-vs-meaning)

That is why the registry example binds the access check to a project implementation.

An architectural import check may be broadly reusable. A test of customer-specific permissions needs project-specific expectations. Both can use the same execution and evidence conventions.

## Make installation prove something

Installing files is the beginning of adoption.

A small command interface can make the rest explicit:

```text
engineering-kit init
engineering-kit doctor
engineering-kit verify
```

`init` selects profiles, records the kit version and prepares project bindings. It should make changes reviewable and preserve existing configuration.

`doctor` checks the setup: dependencies, paths, adapter compatibility, missing test bindings and CI integration.

It should also distinguish a configured check from an enforced gate. A CI job may fail while repository settings still permit a merge. Where access allows, `doctor` can inspect the relevant protection settings. Where it cannot, it should report enforcement as unverified.

`verify` runs applicable checks and produces evidence. Required checks that fail, lack prerequisites or have unresolved decisions must affect the overall outcome according to the configured policy.

A team should finish installation knowing what is active, what is enforced and what remains incomplete.

## Treat evidence as an output of execution

A verification run should create a record automatically. Human decisions should be linked from their authoritative source.

For example:

```yaml
change: PR-482
revision: a1b2c3d
kit_version: 0.2.0
profile: python-api
configuration_revision: d4e5f6a

checks:
  - rule: SEC-004
    check: export-access-tests
    status: passed
    report: reports/export-access.xml

  - rule: PERF-001
    check: export-load-test
    status: could_not_run
    reason: Load environment unavailable

decisions:
  - name: Approve excluded export fields
    status: pending
    owner: product

overall_status: blocked
```

The passing access test does not erase the missing performance result or pending product decision. The overall outcome reflects the outstanding requirements.

Results should come from the execution system, with links to detailed reports. An agent's summary can explain them, but should not replace them.

The code revision, configuration revision and kit version establish what was evaluated. Subsequent changes need an explicit decision about which evidence must be regenerated.

Evidence helps reviewers understand the basis of a decision. It does not establish that the checks themselves are complete or correct.

## Keep authority explicit and upgrades controlled

The operating model defines who may approve, waive, merge and release. The kit implements the checks and integrations supporting those decisions.

It does not acquire decision authority merely because it runs successfully.

Where an organization permits automated merging or deployment under defined conditions, the kit can support that automation. The authority comes from the approved policy and configured permissions.

The same boundary applies to exceptions and upgrades. A threshold change can alter the practical meaning of a policy. Its review should reflect that impact, even if the implementation is a one-line edit.

Projects should adopt explicit kit versions. Releases should describe behavior changes, compatibility limits, new dependencies and migration steps.

The kit also needs its own tests: validator fixtures, representative projects, adapter checks and evaluations for agent-facing capabilities.

A new check may first run in reporting mode to assess its findings before becoming a required gate. That rollout state should be visible, owned and reviewed.

There are responsibilities on both sides: maintainers own kit releases, and adopting teams own project configuration, exceptions and upgrades.

## Start with a dependable minimum

For this design, the first release starts with a small set of executable checks, a rule registry, an evidence schema and one supported integration path.

That release still needs tests for its validators and installation behavior.

Skills can follow as specific needs become clear, each with evaluation evidence. The order matters because it is usually reversed in practice: skills are where the demonstrations are, and validators are where the work is, so a rich skill library often ends up sitting on a repository where nothing the skills recommend is ever checked. A team with an already evaluated skill may include it earlier; the important point is that guidance should have a dependable verification environment around it.

Six questions can assess whether the package is ready for wider adoption:

1. Can a team trace a rule to its checks, guidance, responsible reviewers and known gaps?
2. Do known violations fail, and do valid examples pass?
3. Can the team verify whether required checks actually block progression?
4. Does each run record the relevant versions, configuration and code revision?
5. Can a second project install and upgrade without undocumented help or lost configuration?
6. Do measurements show useful results at an acceptable cost in setup, review and maintenance?

The second project is particularly revealing. It exposes assumptions that were invisible to the original authors.

## What remains open

The boundary between shared policy and project configuration will need adjustment. Too little flexibility creates unsuitable checks. Too much makes the shared package inconsistent.

Evaluation cost also needs measurement. It depends on scenario complexity, repetitions, model use and the environments required. A focused suite for a skill change and a broader suite for a model migration serve different purposes.

Then there is the question of what happens when the kit is wrong. A validator can block valid work. A passing test can miss a relevant failure. Teams need a controlled way to challenge a result, document an exception and improve the capability.

The open question is how much can be standardized while preserving the context that makes each check meaningful.

Repeated use will help answer it. The next article follows one workflow through agent actions, machine checks, human decisions and retained evidence.

**Next: Workflows — making one part of the SDLC repeatable, measurable and improvable.**

[^harness-template]: Böckeler proposes *harness templates*: bundles of guides and sensors standardised for common service topologies. A technology profile is that idea with a rule registry and an evidence schema underneath it. See [Harness Engineering for Coding Agent Users](https://martinfowler.com/articles/harness-engineering.html).

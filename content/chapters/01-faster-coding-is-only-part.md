# Faster coding is only part of the software delivery problem

*Part 1 of Beyond Faster Coding*

Over the last few years, teams have been changing the way they build software. Many have standardized a spec-driven development flow[^spec-kit], written a constitution for the repository, refined the prompts behind each command, and started experimenting with reusable skills and AI coding tools. Some have used this to build real applications.

It works well enough to expose the next problem.

Coding is no longer the part of the lifecycle most worth worrying about. An AI coding agent can generate a surprising amount of implementation in a short time. But faster implementation does not make the rest of the lifecycle faster, safer, or more predictable. The questions move elsewhere.

As coding gets faster, what needs to change around it?

![Faster coding. What happens around it?](diagram:bottleneck)

How does a team know the specification is ready before an agent starts building? How does it know architectural rules were followed, rather than simply written into a constitution? Which checks should run automatically in CI, and which still need engineering judgment? Where do QA, security, performance, release readiness and operational controls fit? How are those checks kept consistent across different coding tools? And when something goes wrong later, how does that failure improve the system for the next change?

This is where the thinking has to move beyond spec-driven development itself.

## Harness engineering

Looking at how other organizations approach AI-assisted delivery, two ideas help frame the problem: harness engineering[^bockeler-harness] and the software factory.

Harness engineering is a way of thinking about everything surrounding the model[^openai-harness]. The model generates the code; the environment around it decides how much its output can be trusted. That environment is rules, tools, tests, permissions, architecture constraints, CI gates, evaluations, feedback and human review.

One principle from spec-driven work captures it well: if a machine can reliably check a rule, that rule should move toward deterministic enforcement rather than stay as prose or a prompt.

A constitution can describe an architectural rule. A skill can help an agent apply it. A reviewer can notice when it has been violated. A deterministic gate can stop the violation from being merged at all. That distinction matters more as AI increases the volume of code moving through the system.

Adoption work tends to surface this gap early. Teams make good progress on specification and implementation discipline, while QA, DevOps, production-readiness signals and automated gates are still being integrated into the same flow.

## Engineering Kit

That is where another idea starts to make more sense. In this series it is called an Engineering Kit.

Engineering Kit is not an industry term. It is simply the working name for a capability teams may need: a versioned, installable package of the engineering environment they want their people and their AI coding tools to operate inside. Standards and constitutions, reusable skills, validators, commands, CI checks, evaluation assets, evidence formats, tool adapters.

The goal is not another developer framework. It is simpler than that: make the same engineering expectations travel with the team whether the developer is in one agentic IDE, another, a background coding agent, or a tool that has not been selected yet.

But building a kit on its own would not prove much. A folder of prompts, skills and rules can look sophisticated without changing how software is actually delivered.

## Workflows

The more useful unit of progress may be a workflow. Take one small part of the SDLC and make it work end to end: specification readiness, pull-request verification, acceptance-test generation, security verification, production readiness.

For each one, ask the same questions. What should the agent do? What should a machine check? What needs human judgment? What evidence is produced? What happens when it fails, and does that failure become a better rule, validator, test or evaluation next time?

## How they fit

Seen this way, harness engineering, the Engineering Kit and the software factory stop looking like competing ideas. They sit at different levels.

Harness engineering is the discipline: it shapes the environment around the agent. The Engineering Kit is the artefact: it packages the reusable parts of that environment. Workflows are where the environment gets exercised; they are small enough to run repeatedly, measure and improve. A software factory is what may eventually emerge when enough of those workflows operate across the lifecycle with shared rules, evidence and feedback.

That is also why "let us build a software factory" is the wrong starting point. It is too large and too abstract. A better one: pick one workflow, design the harness around it, package the reusable pieces into the kit, run it repeatedly, measure what happens, feed what is learned into the next workflow. Then repeat.

![The four concepts and where they sit in the lifecycle](diagram:explainer)

The image above is the model this series uses to organize that thinking. The SDLC has not disappeared. Teams still need intent, specification, planning, implementation, verification, review, release and operations. What has changed is the bottleneck. Implementation got dramatically faster. The surrounding system now has to catch up.

That is what this series explores.

**Next: The AI SDLC — same phases, different bottleneck.**

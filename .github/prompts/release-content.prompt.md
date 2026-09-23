---
description: Validate reviewed content and prepare its publishing pull request.
---
# Prepare a content release

Read the pending diff and the update-content procedure. Use an exact base commit.
Confirm the edition reflects reader-visible changes and the changelog describes them.
Require current citation/build/test output and the actual editorial ACCEPT report.
Run `python scripts/release_content.py check --base <base-commit>`; if the review is
missing or stale, return to the reviewer, never manufacture or refresh acceptance
without review. Regenerate the site and run the documented checks after final edits.
Open a PR with scope, edition, evidence and remaining limitations. Stop before merge
or deployment. Publication occurs only after human review and successful Pages deployment.

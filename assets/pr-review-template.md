# Code Review

Use this only when the user or host has not prescribed another format. Remove unused sections and replace placeholders. Use the priority definitions in [SKILL.md](../SKILL.md).

## Findings

### [P2] Short, actionable title

**Location:** `path/to/file:line`

Describe the concrete trigger, resulting failure, and affected caller or user. Explain the correction briefly, with a reproduction or supporting evidence when available.

Repeat only for independent findings. If there are none, write “No actionable findings found.”

## Open questions

Include only uncertainties that materially affect the review. Do not present them as confirmed defects.

## Scope and validation

State the reviewed comparison or files, checks run and results, and material areas that could not be checked. If asked for a merge recommendation, give one supported by those findings; do not imply a PR action was submitted.

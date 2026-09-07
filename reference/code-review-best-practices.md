# Review Practices

Use this reference when the user asks for review standards, process advice, or mentoring. The default code-review workflow and severity definitions live in [SKILL.md](../SKILL.md).

## Feedback that helps an author act

State demonstrated defects directly: “When the result is empty, this access throws before the response is sent.” Include the triggering input and a focused correction. Ask a question when the requirement is uncertain, not as a substitute for explaining a known failure.

Separate correctness from preferences. If a team convention matters, cite the convention and explain the consequence of diverging. Suggestions should identify a real benefit and acknowledge tradeoffs.

## Team process

- Agree on review ownership and response expectations with the team; avoid universal turnaround times or line-count gates.
- For large changes, identify cohesive review areas and track coverage. Suggest splitting only when it makes the change easier to understand or safely deliver.
- On re-review, inspect the updated diff and affected behavior. Recheck earlier findings without repeating resolved comments.
- Resolve disagreements using requirements, reproductions, measurements, and documented constraints. Escalation is a team decision, not an automatic review step.
- For mentoring, use one or two relevant explanations or examples rather than a general language tutorial.

## Improving the process

Use escaped defects and actual review outcomes to refine guidance. Review speed and finding counts alone do not measure quality; they can reward shallow reviews or noisy feedback.

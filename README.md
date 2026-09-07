# Code Review Skill

A shared agent skill for **Codex and Claude Code** that reviews code for actionable bugs, security issues, performance regressions, and compatibility problems.


## Install with npx skills

From the project where you want to use the skill:

```sh
npx skills add joynal/code-review-skill --skill code-review --agent codex claude-code
```

Add `--global` to install for your user across projects, or specify only one agent. Node.js/npm and Git are needed for this installer; the skill itself has no Node dependency or npm package to publish.

List the available skill before installing:

```sh
npx skills add joynal/code-review-skill --list
```

To try changes from a local checkout, run this from another project and replace the path:

```sh
npx skills add /absolute/path/to/code-review-skill --skill code-review --agent codex claude-code
```

The GitHub command installs the version pushed to GitHub, not uncommitted local changes. The root `SKILL.md` is directly discoverable by the [Skills CLI](https://github.com/vercel-labs/skills).

### Manual installation

Copy the skill folder, including `SKILL.md`, `reference/`, `assets/`, `scripts/`, and `agents/`, into one of these locations, naming the folder `code-review`:

| Agent       | Project                       | User                            |
| ----------- | ----------------------------- | ------------------------------- |
| Codex       | `.agents/skills/code-review/` | `~/.agents/skills/code-review/` |
| Claude Code | `.claude/skills/code-review/` | `~/.claude/skills/code-review/` |

These manual paths follow [Codex documentation](https://learn.chatgpt.com/docs/build-skills) and [Claude Code documentation](https://code.claude.com/docs/en/skills). The Skills CLI manages its own agent destinations, including Codex's `~/.codex/skills/` global destination. Avoid installing duplicate copies with the same name.

## Use

In Codex:

```text
Use $code-review to review my branch against origin/main.
```

In Claude Code:

```text
/code-review Review my branch against origin/main.
```

Or ask naturally: “Review my staged changes for bugs.” Replace the base branch with your actual target.

Other examples:

- “Review this React component for state and request races.”
- “Review this Python PR, focusing on cancellation and resource cleanup.”
- “Review this Go service's authorization.”
- “Review the architecture and migration compatibility of this change.”
- “Review these changes and fix confirmed issues.” (Also authorizes local fixes.)

The default review reports findings and validation limits. It does not submit a PR review or merge anything. References use the repository's actual language versions and tooling; they do not require migration to a newer stack.

## Contents

- [SKILL.md](SKILL.md): scope, workflow, evidence requirements, reference routing, and severity.
- `reference/`: React, TypeScript/JavaScript, Python, Java, Go, CSS, security, performance, architecture, and cross-language checks.
- [PR review template](assets/pr-review-template.md) and [checklist](assets/review-checklist.md): optional report assets.
- [agents/openai.yaml](agents/openai.yaml): Codex display metadata; not needed by Claude Code.
- [scripts/pr-analyzer.py](scripts/pr-analyzer.py): optional dependency-free diff inventory for Python 3.10+.
- [Upgrade assessment](docs/upgrade-assessment.md): dated ecosystem findings, sources, and maintenance advice.

## Optional analyzer

Resolve the intended base/head and the installed script's absolute path:

```sh
git diff --no-ext-diff --no-textconv --no-color --src-prefix=a/ --dst-prefix=b/ origin/main...HEAD | python3 /absolute/path/to/code-review/scripts/pr-analyzer.py --stats
```

Or pass a saved diff:

```sh
python3 scripts/pr-analyzer.py --diff-file /path/to/change.diff --stats
```

The score and estimated minutes are rough size-based heuristics, not measured complexity, coverage, or merge criteria. Standard Git unified diffs are supported; combined merge diffs are rejected. Binary and rename-only files can be listed but their contents are not reviewed.

## Development checks

```sh
python3 -m unittest discover -s tests -v
npx skills add . --list
```

The tests exercise diff parsing, CLI behavior, and bundled Markdown links. GitHub Actions runs them on Python 3.10 and 3.14. Installation can be smoke-tested in an empty temporary project with the local-path command above.

## License

[MIT](LICENSE)

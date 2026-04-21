### Overview

**Code Review** skill is a production-ready skill for [Claude Code](https://claude.ai/code) that transforms AI-assisted code review from vague suggestions into a **structured, consistent, and expert-level** process.

---

### &#10024; Key Features

- **Progressive Disclosure** — Core skill is ~190 lines; language guides (~200–1,000 lines each) load only when needed.
- **Four-Phase Review Process** — Structured workflow from understanding scope to delivering clear feedback.
- **Severity Labeling** — Every finding is categorized: `blocking` · `important` · `nit` · `suggestion` · `learning` · `praise`
- **Security-First** — Dedicated security checklists per language ecosystem.
- **Collaborative Tone** — Questions over commands, suggestions over mandates.
- **Automation Awareness** — Clearly separates what human review should catch vs. what linters handle.

---

### &#127760; Supported Languages & Frameworks

<table>
  <thead>
    <tr>
      <th>Category</th>
      <th>Technology</th>
      <th>Guide</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td rowspan="3"><strong>Frontend</strong></td>
      <td>&#9883;&#65039; React 19</td>
      <td><code>reference/react.md</code></td>
    </tr>
    <tr>
      <td>&#127912; CSS</td>
      <td><code>reference/css.md</code></td>
    </tr>
    <tr>
      <td>&#128311; TypeScript</td>
      <td><code>reference/typescript.md</code></td>
    </tr>
    <tr>
      <td rowspan="3"><strong>Backend</strong></td>
      <td>&#9749; Java</td>
      <td><code>reference/java.md</code></td>
    </tr>
    <tr>
      <td>&#128013; Python</td>
      <td><code>reference/python.md</code></td>
    </tr>
    <tr>
      <td>&#128057; Go</td>
      <td><code>reference/go.md</code></td>
    </tr>
    <tr>
      <td rowspan="2"><strong>Architecture</strong></td>
      <td>&#127963;&#65039; Architecture Design Review</td>
      <td><code>reference/architecture-review-guide.md</code></td>
    </tr>
    <tr>
      <td>&#9889; Performance Review</td>
      <td><code>reference/performance-review-guide.md</code></td>
    </tr>
  </tbody>
</table>

---

### &#128260; The Four-Phase Review Process

```
Phase 1 - Context Gathering
  Understand PR scope, linked issues, and intent
                    |
                    v
Phase 2 - High-Level Review
  Architecture - Performance impact - Test strategy
                    |
                    v
Phase 3 - Line-by-Line Analysis
  Logic - Security - Maintainability - Edge cases
                    |
                    v
Phase 4 - Summary & Decision
  Structured feedback - Approval status - Action items
```

---

### &#127991;&#65039; Severity Labels

| Label                  | Meaning                                         |
| ---------------------- | ----------------------------------------------- |
| &#128308; `blocking`   | Must be fixed before merge                      |
| &#128992; `important`  | Should be fixed; may block depending on context |
| &#128993; `nit`        | Minor style or preference issue                 |
| &#128309; `suggestion` | Optional improvement worth considering          |
| &#128218; `learning`   | Educational note for the author                 |
| &#127775; `praise`     | Explicitly highlight great work                 |

---

### &#128193; Repository Structure

```
code-review-skill/
|
+-- SKILL.md                              # Core skill - loaded on activation (~190 lines)
+-- README.md
+-- LICENSE
+-- CONTRIBUTING.md
|
+-- reference/                            # On-demand language guides
|   +-- react.md                          # React 19, Server Components, Suspense patterns
|   +-- typescript.md                     # TypeScript strict mode, generics, ESLint
|   +-- java.md                           # Java
|   +-- python.md                         # Python async, typing, pytest
|   +-- go.md                             # Go goroutines, channels, context, interfaces
|   +-- css.md                            # CSS variables, responsive design
|   +-- architecture-review-guide.md      # SOLID, anti-patterns, coupling/cohesion
|   +-- performance-review-guide.md       # Core Web Vitals, N+1, memory leaks
|   +-- security-review-guide.md          # Security checklist (all languages)
|   +-- common-bugs-checklist.md          # Language-specific bug patterns
|   +-- code-review-best-practices.md     # Communication & process guidelines
|
+-- assets/
|   +-- review-checklist.md               # Quick reference checklist
|   +-- pr-review-template.md             # PR review comment template
|
+-- scripts/
    +-- pr-analyzer.py                    # PR complexity analyzer
```

---

### &#128640; Installation

**Clone to your Claude Code skills directory:**

```bash
# macOS / Linux
git clone https://github.com/joynal/code-review-skill.git \
  ~/.claude/skills/code-review
```

**Or add to an existing plugin:**

```bash
cp -r code-review-skill ~/.claude/plugins/your-plugin/skills/code-review/
```

---

### &#128161; Usage

Once installed, activate the skill in your Claude Code session:

```
Use code-review to review this PR
```

Or create a custom slash command in `.claude/commands/`:

```markdown
<!-- .claude/commands/review.md -->

Use code-review to perform a thorough review of the changes in this PR.
Focus on: security, performance, and maintainability.
```

**Example prompts:**

| Prompt                               | What happens                                                          |
| ------------------------------------ | --------------------------------------------------------------------- |
| `Review this React component`        | Loads `react.md` - checks hooks, Server Components, Suspense patterns |
| `Review this Java PR`                | Loads `java.md` - checks virtual threads, JPA, Spring Boot 3 patterns |
| `Security review of this Go service` | Loads `go.md` + `security-review-guide.md`                            |
| `Architecture review`                | Loads `architecture-review-guide.md` - SOLID, anti-patterns, coupling |
| `Performance review`                 | Loads `performance-review-guide.md` - Web Vitals, N+1, complexity     |

---

### &#128196; License

MIT &copy; [Joynal](https://github.com/joynal)

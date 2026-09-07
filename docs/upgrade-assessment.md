# Compatibility and Upgrade Assessment

Reviewed on **2026-09-07**. This is a dated maintenance assessment, not a minimum-version policy for repositories reviewed by the skill.

## What this repository needs

This repository contains Markdown instructions and one optional Python helper. It has no React, TypeScript, Java, Go, or npm application dependencies to upgrade. The changes therefore update review guidance and helper validation rather than migrating an application.

The helper uses only the Python standard library and documents Python 3.10+ support. Installation through the Skills CLI requires Node.js/npm and Git; using the review instructions does not require Python.

## Ecosystem assessment

| Ecosystem                | Verified release baseline                                         | Guidance and upgrade implications                                                                                                                                                                                                                                                                                                                                                                            |
| ------------------------ | ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Python                   | 3.14.7 stable; 3.15 is prerelease                                 | Cover deferred annotation evaluation, multiprocessing start-method changes, and optional free-threaded builds. Python 3.10 reaches end of support in October 2026, so plan its retirement where it is still deployed. [Python releases](https://www.python.org/downloads/), [3.14 changes](https://docs.python.org/3.14/whatsnew/3.14.html)                                                                  |
| React                    | 19.2; versions page lists 19.2.7                                  | Add 19.2 Effect Events/Activity and compiler-aware review. Correct Actions, optimistic updates, Suspense Promise stability, and client/server boundaries. Check the framework and RSC package advisories for exact security patch requirements. [React versions](https://react.dev/versions), [19.2 release](https://react.dev/blog/2025/10/01/react-19-2)                                                   |
| TypeScript               | 7.0 released July 8, 2026                                         | Include 6.0 configuration migration and 7.0 native compiler compatibility. 7.0 has no compiler API; tools such as type-aware linters may need TypeScript 6 alongside it. A blanket compiler upgrade can break tooling. [7.0 announcement](https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/), [6.0 notes](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-6-0.html) |
| Java                     | 25 LTS and 26 feature release                                     | Keep review tied to the deployed JDK and compiler target. Refresh records, switch patterns, virtual threads, and annotation-processor compatibility. Latest feature release is not automatically the right deployment target. [Java downloads](https://www.oracle.com/java/technologies/downloads/)                                                                                                          |
| Spring Boot              | 4.1.1 stable                                                      | Account for Boot 4 migrations, including starters, Jackson, and testing modules. Its documented JDK range is 17–26; assess dependencies and deployment before migrating. [System requirements](https://docs.spring.io/spring-boot/system-requirements.html), [Boot 4 migration](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide)                                         |
| Go                       | 1.27.1; supported release families follow the latest two releases | Base language checks on go.mod, including loop-variable semantics. Cover newer APIs only when the declared baseline supports them. [Release history](https://go.dev/doc/devel/release)                                                                                                                                                                                                                       |
| CSS/Sass                 | Browser-targeted; no single CSS runtime version                   | Remove blanket IE guidance and automatic blockers for !important, animations, or selector depth. Sass import/global-function deprecations began in Dart Sass 1.80.0. [Sass migration](https://sass-lang.com/documentation/breaking-changes/import/)                                                                                                                                                          |
| ESLint/typescript-eslint | Follow the project's supported combination                        | Replace the copied legacy eslintrc tutorial with current flat-config and typed-linting guidance; verify compiler compatibility. [Typed linting](https://typescript-eslint.io/getting-started/typed-linting/)                                                                                                                                                                                                 |

These versions are a snapshot. Recheck primary release pages before future upgrades, and distinguish stable releases from previews.

## Compatibility changes

- Kept one root SKILL.md with shared name/description frontmatter for both agents.
- Removed Claude-specific allowed-tools metadata. In current Claude Code this field grants tool permissions rather than restricting availability; the skill now uses each agent's configured tools and permissions. [Claude skills](https://code.claude.com/docs/en/skills)
- Added optional Codex display metadata, relative resource routing, and documentation for both invocation forms. [Codex skills](https://learn.chatgpt.com/docs/build-skills)
- Documented direct installation from GitHub or a local path with npx skills. A standalone npm package is unnecessary. [Skills CLI](https://github.com/vercel-labs/skills)

## Review-quality corrections

The original references contained repeated sections, Markdown headings inside code fences, incomplete examples, and inconsistent severity schemes. The main entrypoint now owns workflow and severity; each language/topic reference owns its technical checks.

Specific corrections include:

- Fixed the missing CSS reference and removed references to nonexistent repository files.
- Replaced mandatory praise, question-only feedback, fixed review times, line-count gates, and blanket test requirements with concrete evidence and scope reporting.
- Removed automatic mutation commands from review guidance, including audit fixes and formatter write modes.
- Corrected claims that every async function needs a local catch, void handles Promise rejections, every Suspense needs its own error boundary, and all descendants of a client component become client modules.
- Replaced unsafe or incomplete security, cancellation, and performance examples with checks that name their assumptions.
- Reduced the duplicated general bug guide to cross-language, SQL, and API checks; language-specific checks live in their own guides.
- Fixed analyzer hunk counting, quoted filenames, test classification, empty/error handling, and unsupported combined-diff reporting. Its results are explicitly described as size heuristics.

## Validation performed

- 13 tests passed on Python 3.10.18 and 3.14.0, covering analyzer behavior and bundled Markdown links.
- The skill-creator frontmatter validator and Ruff checks passed.
- The Skills CLI discovered exactly one skill and installed it for both Codex and Claude Code in a temporary project, using both symlink and copy modes.
- Live model-driven reviews were not tested in either agent. The GitHub Actions workflow was added but has not run remotely.

## Maintenance

### Example restoration (2026-09-08)

Restored 12 focused good/bad example pairs across React, TypeScript, Python, Go, Java/Spring, and CSS. Each names the failure condition, correction, and relevant assumptions or version limits. Temporary checks executed the Python examples on 3.10 and 3.14, the TypeScript examples with Node's type stripping, and the React examples against React 19.2. These checks verified the documented failure/fix outcomes, not model review quality or static type checking. CSS browser execution was blocked by the sandbox; Go and Java runtimes were unavailable, so those examples received documentation-based review.

Run the analyzer regression tests on the minimum supported and current stable Python versions. Recheck installation discovery when changing frontmatter or layout. For agent behavior, exercise representative reviews that contain a real regression, no defect, and version-dependent code; installation validation alone does not establish review quality.

Keep release snapshots in this document and technical rules in the references. Upgrade recommendations for a specific application require that application's manifests, lockfiles, deployment targets, and tests.

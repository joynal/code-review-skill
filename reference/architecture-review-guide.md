# Architecture Review Guide

Evaluate the change against the system's existing boundaries, documented decisions, and actual requirements. SOLID, clean architecture, and design patterns are lenses, not mandatory architectures.

## Contracts and ownership

- Identify who owns state, invariants, persistence, and external side effects.
- Trace changes to public APIs, events, schemas, configuration, and error contracts through their consumers.
- Check whether dependency direction follows the project's chosen architecture. A framework import or concrete dependency alone does not establish a defect.
- Inspect cycles for an actual initialization, build, deployment, or testability problem.
- If an abstraction is proposed, identify the concrete variability it handles and the extra indirection it adds. Interfaces with one implementation can still serve a real contract.

## Consistency and failure boundaries

- Related state changes should preserve their invariants on partial failure. Trace transaction boundaries and when irreversible side effects occur.
- Retries need idempotency where duplicate execution is possible. Check timeouts after a remote operation may already have committed.
- Events can be duplicated, delayed, or reordered. Verify the guarantees of the actual transport and consumer.
- Local caches and process memory may not be shared across replicas. Check assumptions about session state, counters, and coordination.
- Background work needs ownership, shutdown semantics, and an observable failure path.

## Compatibility and rollout

- Can old and new application versions coexist during deployment?
- Are schema changes compatible with existing readers/writers and backfills?
- Does rollback remain possible after new data is written?
- Are defaults and configuration changes safe for existing deployments?
- Does a migration that adds constraints account for existing data?
- Are external consumers given the versioning or migration path the project promises?

## Maintainability

Use a concrete change scenario to explain coupling or duplicated logic. Prefer identifying a rule that can diverge over counting repeated lines. Do not demand a rewrite because a class is large, a function has several arguments, or a switch exists.

State tradeoffs when multiple designs satisfy the requirements. Broader redesign ideas belong in optional recommendations when requested, not among confirmed regressions.

## Validation

Trace a representative request, failure, and rollout sequence through the changed boundaries. Use existing integration/contract tests and deployment documentation. Escalate uncertainty about business invariants as a specific open question rather than assigning a severity based on a pattern name.

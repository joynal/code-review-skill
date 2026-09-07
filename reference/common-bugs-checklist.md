# Cross-Language Bug Checks

Use this for API, SQL, and cross-cutting behavior. Language details live in [React](react.md), [TypeScript/JavaScript](typescript.md), [Python](python.md), [Java](java.md), and [Go](go.md).

## Boundaries and state

- Empty, singleton, and maximum-size inputs; inclusive/exclusive ranges and off-by-one indexing.
- Missing versus null versus valid falsy values.
- Numeric overflow, truncation, precision, and unit conversions.
- Timezones, daylight-saving transitions, date-only values, and expiry comparisons.
- Encoding/normalization differences at boundaries.
- Shared mutable objects, shallow copies, stale reads, and updates based on old state.
- Partial writes, retries after uncertain outcomes, and duplicate operations.
- Cleanup when acquisition fails partway through or processing exits early.

## SQL semantics

- NULL uses three-valued logic; `= NULL`, `NOT IN` with nullable values, and predicates on outer-joined tables can produce unexpected results.
- Check join cardinality, missing parent rows, duplicates, and aggregate inflation.
- Pagination needs a stable ordering with a tie-breaker; concurrent writes can still affect offset pagination.
- Related updates may need a transaction, uniqueness constraint, or concurrency control. A prior existence check does not prevent concurrent inserts.
- Validate migration behavior for existing rows, defaults, backfills, and rollback.
- Query parameters represent values, not arbitrary identifiers or SQL syntax.

Use [security](security-review-guide.md) for injection and [performance](performance-review-guide.md) for query plans and data volume.

## API behavior

- Check request/response compatibility, validation, status codes, and error schemas against actual consumers.
- Enforce bounds on page sizes, uploads, batch operations, and expensive parameters.
- Verify object ownership and tenant isolation through every lookup, including caches and background work.
- Match retry behavior to the endpoint's idempotency contract. HTTP method alone does not prove duplicate execution is safe.
- Partial success should not silently look like complete success.
- Public payloads and caller-selected fields must not expose internal or sensitive properties.
- Missing client validation does not prove a server-side defect; inspect the actual trust boundary.

## Tests as evidence

Check whether the existing tests would distinguish the old and new behavior. Look for assertions that miss a failure, unawaited async work, uncontrolled clocks, shared state, or mocks that bypass the contract under review.

Tests may legitimately involve external dependencies in integration environments. Missing changed tests or a coverage percentage alone does not establish an untested regression.

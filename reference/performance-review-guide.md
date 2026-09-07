# Performance Review Guide

Tie performance findings to an actual workload, latency/resource requirement, measurement, or demonstrable growth bound. State estimates as estimates.

## Workload and evidence

- Establish input size, request rate, concurrency, critical path, and supported device/runtime.
- Compare with the base implementation and identify the added work.
- Distinguish CPU, I/O, memory retention, database contention, and network cost.
- Do not assign blocking severity to all nested loops, lists over a fixed length, or missing caches.
- Use profiles, traces, query plans, bundle reports, or focused benchmarks where available. Avoid universal API latency and bundle-size limits.

## Browser delivery and responsiveness

Core Web Vitals are LCP, INP, and CLS. The good thresholds are LCP ≤ 2.5 seconds, INP ≤ 200 milliseconds, and CLS ≤ 0.1, evaluated at the 75th percentile of page visits. FCP and TBT are useful diagnostics but are not Core Web Vitals. See [Web Vitals](https://web.dev/articles/vitals).

Check:

- Discovery and priority of the actual LCP resource; lazy-loading an above-the-fold LCP image can delay it.
- Responsive image sizing, transfer size, and reserved media space.
- Font loading and fallback metrics; `font-display: swap` does not by itself eliminate layout shift.
- Long tasks, repeated synchronous work, layout reads/writes, and costly event handlers.
- Code splitting against real route usage. Tree shaking depends on bundler/package side effects, not simply named exports.
- Rendering large data sets, with pagination or virtualization when useful and compatible with focus/accessibility needs.

Use [React](react.md) for rendering and Effects, and [CSS](css.md) for animation/cascade details.

## Resource lifetime

Identify the reference or owner that keeps a resource alive. Check subscriptions, sockets, timers, retained closures, growing maps, queues, and caches. Garbage collection does not close external resources reliably or bound application caches.

Inspect cleanup after failure and cancellation, not only the successful path. Streaming or generators help only if the upstream source also avoids materializing the full result.

## Database work

- Identify repeated queries and their count at representative cardinalities.
- Check fetch strategies against joins, duplicates, pagination, and payload size. In Django, `select_related` normally uses a SQL join; `prefetch_related` uses separate related queries.
- Use the actual database/version and a query plan before asserting index usage. Selectivity, expressions, collation, and index ordering matter.
- Additional indexes increase write/storage cost; indexing every filtered field is not a universal fix.
- Bound result sets where required and examine deep offset pagination.
- Check pool exhaustion, long transactions, lock contention, and retry amplification.
- `EXPLAIN ANALYZE` executes the query. Use a suitable test environment and avoid mutating live data as a review diagnostic.

## APIs, caches, and algorithms

- Bound concurrency and queued work, and propagate deadlines/cancellation to downstream operations.
- Retries need limits, backoff, and a safe duplicate-execution contract.
- Cache keys must include the dimensions affecting the result, especially authorization/tenant context. Verify invalidation, TTL, size bounds, and stampede behavior.
- ETags must track the representation; a fixed tag for changing data is incorrect.
- Field selection must enforce a server-side allowlist; smaller responses must not expose unauthorized attributes.
- When replacing loops with maps/sets, preserve order, equality, duplicate semantics, and memory constraints.
- Benchmark after warmup with representative inputs, and report environment and variability rather than a single unexplained timing.

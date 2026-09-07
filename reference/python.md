# Python Review Guide

Identify `requires-python`, lockfiles, deployment images, type-checker targets, and CI versions. Distinguish support for older Python versions from the latest interpreter available locally.

## Types and version boundaries

- Built-in generics (`list[str]`, `dict[str, int]`) are available in 3.9+; `X | None` in 3.10+. Prefer `collections.abc` for collection protocols in modern code, while retaining older forms where compatibility requires them.
- Type parameter syntax and the `type` alias statement require 3.12+. Do not introduce them into a project supporting 3.10/3.11.
- `TypedDict`, annotations, and `cast` do not validate external data. `@runtime_checkable` protocols do not check method signatures at runtime.
- In 3.14, annotations are evaluated lazily by default. Code introspecting `__annotations__`, unresolved forward references, or frameworks consuming annotations needs migration checks. See [Python 3.14 changes](https://docs.python.org/3.14/whatsnew/3.14.html).
- Follow the configured type-checker policy; missing annotations are not automatically runtime defects.

## State and data semantics

- Mutable defaults and class attributes are shared. Determine whether sharing is intentional before reporting it.
- Check late-bound closures in loops, mutation during iteration, shallow-copy aliasing, and iterator exhaustion.
- Use equality for value comparisons; object identity and integer interning are not value contracts.
- Distinguish a missing value from valid falsy values such as zero or an empty collection.
- Verify timezone-aware versus naive datetime handling and numeric precision where the domain needs exact arithmetic.
- `assert` can be removed by optimized execution; do not use it as the only validation of untrusted input.

## Async work and cleanup

- Blocking I/O or CPU work in an `async def` blocks the event loop unless offloaded. `asyncio.to_thread` can suit blocking I/O; cancelling the await does not stop a thread already running.
- An awaited operation normally propagates cancellation. Catching `CancelledError` is needed only when doing something useful such as cleanup; generally re-raise it. Prefer `finally` or context managers for resource release.
- `asyncio.TaskGroup` and `asyncio.timeout` require 3.11+. Task groups cancel siblings on failure and can raise exception groups; `gather` has different failure semantics. Choose according to the required behavior.
- Retain and supervise background tasks, and ensure shutdown waits or cancels appropriately.
- Bound outstanding tasks as well as active requests for large inputs. A semaphore around requests does not bound the number of eagerly created tasks.
- Reuse clients/pools with appropriate lifetimes; verify response handling, timeouts, and cleanup on exceptions.
- Queue shutdown must account for consumers and `task_done` calls, including sentinels when `join` is used.

See [asyncio tasks](https://docs.python.org/3/library/asyncio-task.html) for the target version's cancellation semantics.

## Exceptions and resources

- Locate the responsible error boundary. A broad catch can be valid there, but silently dropping failures can hide partial writes or report success incorrectly.
- `raise NewError(...) from exc` sets an explicit cause. Raising during exception handling already preserves implicit context; it does not automatically lose the original error.
- Check transaction commit/rollback, file/socket closure, and cleanup if acquisition succeeds only partially.
- Streaming must reach the data source. Yielding rows from `fetch_all()` still materializes the query results.

## Concurrency and Python 3.14

- Determine whether the runtime uses the conventional GIL build or a free-threaded build. Do not infer that compound shared-state operations are safe because of the GIL or container implementation.
- Verify native extension support before adopting free-threaded Python.
- Python 3.14 changes the default multiprocessing start method away from `fork` on affected Unix platforms; macOS and Windows retain `spawn`. Check importable workers, picklable arguments, main-module guards, and assumptions about inherited global state. See [3.14 migration notes](https://docs.python.org/3.14/whatsnew/3.14.html).

## Focused examples

### Mutable defaults accidentally share request state

The contract here is a fresh collection when the caller omits `items`; mutation of an explicitly supplied list is intentional.

```python
# Bad: Python creates the default list once, when defining the function.
def append_bad(item: str, items: list[str] = []) -> list[str]:
    items.append(item)
    return items

# Good: create a list for each call that omits it.
def append_good(item: str, items: list[str] | None = None) -> list[str]:
    if items is None:
        items = []
    items.append(item)
    return items
```

**Why:** calling `append_bad("a")` and then `append_bad("b")` returns the same list containing both values. With `append_good`, the second call returns only `["b"]`. This example uses Python 3.10+ annotations. Shared state is not inherently wrong, but must match the contract; for independent mutable dataclass fields, use `field(default_factory=list)`.

### Swallowing cancellation reports a successful task

These workers wait for a stop/cancel signal. The list records cleanup so that both resource release and cancellation can be observed.

```python
import asyncio

# Bad: catching cancellation and returning converts it into normal completion.
async def worker_bad(cleaned: list[bool]) -> None:
    try:
        await asyncio.Event().wait()
    except asyncio.CancelledError:
        cleaned.append(True)

# Good: cleanup runs while cancellation propagates to the owner.
async def worker_good(cleaned: list[bool]) -> None:
    try:
        await asyncio.Event().wait()
    finally:
        cleaned.append(True)
```

**Why:** start the worker, let it reach its await, then cancel it. Awaiting the bad task completes normally; awaiting the good one raises `CancelledError`. Both record cleanup. A worker with no owned cleanup can simply let cancellation propagate without either block. Intentional cancellation suppression needs a separate contract; see [asyncio cancellation](https://docs.python.org/3/library/asyncio-task.html).

## Validation

Use the repository's test, lint, formatting-check, and type-check commands. Ruff, Black, mypy, Pyright, and pytest are optional project choices, not required installations. Test independent mutable state, cleanup after exceptions, cancellation, and supported interpreter versions. Check pytest async plugin mode before changing async fixtures; patch names where the consuming code looks them up.

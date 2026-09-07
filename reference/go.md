# Go Review Guide

Read `go.mod`, its `go` directive, toolchain selection, build tags, and supported deployment targets. A newer locally installed compiler does not alone determine the package's language semantics.

## Errors and resources

- Check error handling where ignoring a failure can change observable behavior. Wrapping every error or logging and returning every error is not mandatory.
- Use `errors.Is`/`errors.As` when matching through wrapped errors. `%w` exposes an error chain as part of the API; choose intentionally.
- A typed nil stored in an interface is not a nil interface. Check error returns and optional dependencies.
- Close response bodies, files, rows, and other owned resources on all paths. Inspect `rows.Err()` and write/flush/close errors where durability depends on them.
- `defer` runs when the enclosing function returns. In large loops, extract per-item work if delayed cleanup exhausts resources.

## Concurrency and cancellation

- Trace who owns each goroutine and what lets it terminate, including blocked sends/receives and caller cancellation.
- Propagate the request context to I/O that should stop with the request. Release resources created by cancellation functions.
- Check channel closure ownership, sends after close, nil channels, and zero-value reads after closure.
- With `WaitGroup.Add/Done`, increment before starting work that a concurrent `Wait` must observe. `WaitGroup.Go` is available in Go 1.25+; do not require it for older supported versions. See [sync](https://pkg.go.dev/sync).
- Protect compound read/modify/write operations. Concurrent containers do not make sequences of operations atomic.
- Avoid copying mutexes or structs containing synchronization primitives after use.
- Bound workers, queues, and retained results according to workload and shutdown requirements.

## Language semantics and data

- Loop variables declared with `:=` have per-iteration semantics under Go 1.22+ language versions. Reused variables assigned with `=` can still be shared. Check the module's language version before reporting the historical closure bug. See [Go 1.22](https://go.dev/doc/go1.22).
- Nil maps support reads but panic on writes. Nil and empty slices may serialize differently.
- Slice subslicing and append can share backing storage. Verify ownership before assuming independence.
- Long-lived substrings/subslices can retain larger allocations; establish meaningful retention before recommending copies.
- Compare `time.Time` values with methods appropriate to instant ordering/equality; `==` also compares representation details.
- Check API-specific zero values, typed nils, and JSON field omission behavior.

## Contracts and performance

Prefer interfaces that express consumer needs when they improve substitution or testing, but concrete dependencies and interface-returning constructors can be valid. Do not report a defect based only on that design preference.

Verify hot paths with benchmarks or profiles. Preallocation, `sync.Pool`, and changing pointer receivers are not automatic improvements; pools may discard contents and pooled objects must not remain in use after return.

## Focused examples

The snippets below are package-level declarations; add `package main` when running them as standalone programs.

### Returning a typed nil as an error

```go
type LookupError struct{}

func (*LookupError) Error() string { return "lookup failed" }

// Bad: callers see a non-nil error even though no error was allocated.
func lookupBad() error {
    var err *LookupError
    return err
}

// Good: return the nil interface for the successful path.
func lookupGood() error {
    return nil
}
```

**Why:** `lookupBad() != nil` is true because the interface contains the dynamic type `*LookupError`. `lookupGood() == nil` is true. A real failure should still return its concrete error. The same issue can affect other optional interface values.

### Loop capture depends on declaration and language version

This example uses deferred callbacks instead of goroutines so the capture error is deterministic and introduces no data race.

```go
// Bad in all Go versions: "=" reuses the same variable on each iteration.
func callbacksBad(items []string) []func() string {
    var callbacks []func() string
    var item string
    for _, item = range items {
        callbacks = append(callbacks, func() string { return item })
    }
    return callbacks
}

// Good on both old and new language versions: capture a per-iteration copy.
func callbacksGood(items []string) []func() string {
    var callbacks []func() string
    for _, item := range items {
        captured := item
        callbacks = append(callbacks, func() string { return captured })
    }
    return callbacks
}
```

**Why:** after constructing callbacks for `[]string{"a", "b"}`, the bad callbacks both return `"b"`; the good ones return `"a"` and `"b"`. With Go 1.22+ language semantics, `for _, item := range items` already creates per-iteration variables, so the explicit copy is unnecessary. Do not report its absence as a bug in that case. Older language versions still need a capture strategy. See [Go 1.22](https://go.dev/doc/go1.22).

## Validation

Use applicable package tests and configured static checks; `go vet` and `go test -race` can add evidence when the environment supports them. Formatting checks should use listing/diff modes, not `gofmt -w` during review. See [Go review comments](https://go.dev/wiki/CodeReviewComments) and [release history](https://go.dev/doc/devel/release) for version-specific guidance.

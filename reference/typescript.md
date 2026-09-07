# TypeScript and JavaScript Review Guide

Inspect the resolved compiler version, effective tsconfig (including inherited settings), runtime version, module format, and build pipeline. TypeScript types do not validate runtime input or provide polyfills.

## Runtime boundaries and narrowing

- Trace external data through runtime validation before trusting it. Assertions, generics, `satisfies`, and `TypedResponse<T>` wrappers cannot establish that JSON has the advertised shape.
- Check custom type predicates against every property they promise. A property existing does not prove its value has the required type.
- Follow unsafe `any`, assertions, and non-null assertions to a concrete failure. Their presence alone is not a finding.
- Check null versus absent properties, optional values, indexed access, and exhaustive handling of discriminated unions.
- `readonly` and `as const` do not freeze objects at runtime. Copying an array does not copy its nested objects.

### Example: an assertion does not validate a response

Assume external data may contain `{ value: 42 }` and callers need a string:

```typescript
type Payload = { value: string };

// Bad: the asserted return type hides invalid data from downstream callers.
function parsePayloadBad(input: unknown): Payload {
  return input as Payload;
}

// Good: check the value before returning the advertised type.
function parsePayload(input: unknown): Payload {
  if (
    typeof input !== "object" ||
    input === null ||
    !("value" in input) ||
    typeof input.value !== "string"
  ) {
    throw new TypeError("Expected an object with a string value");
  }
  return { value: input.value };
}
```

**Why:** `parsePayloadBad({ value: 42 }).value.toUpperCase()` throws at the consumer. The validated parser rejects the payload at the boundary; `{ value: "ok" }` succeeds. The `in` narrowing requires TypeScript 4.9+. An assertion can be valid after a separately established invariant; do not flag every assertion. For larger schemas, use the repository's validation approach.

## Asynchronous behavior

- Trace rejection handling to the caller or framework boundary. Every `async` function does not need its own `try/catch`.
- `void save()` discards the value but does not handle rejection. Check intentional background operations for an actual error handler.
- `forEach(async ...)` does not await its callbacks. Verify sequencing, completion, and concurrency limits.
- `Promise.all` is correct for all-or-fail results; it rejects early without cancelling remaining work. `allSettled` suits partial success only when each rejection is handled.
- `fetch` resolves for HTTP error responses. Check `response.ok` or explicit status handling before processing a success payload.
- Cancellation, duplicate requests, retries, and stale results need semantics appropriate to the consumer. A signal must reach the operation to cancel it.
- Catch values can be non-`Error`; narrow them before accessing `message`. Preserve useful error context when translating errors.

### Example: discarding a Promise is not handling its rejection

These alternative wrappers receive an asynchronous save operation:

```typescript
// Bad: rejection escapes when used as a synchronous event callback.
function saveBad(save: () => Promise<void>): void {
  void save();
}

// Good: let an awaiting caller or framework error boundary own the failure.
async function saveAndWait(save: () => Promise<void>): Promise<void> {
  await save();
}

// Also good for intentional background work: supply an actual error handler.
function saveInBackground(
  save: () => Promise<void>,
  reportError: (error: unknown) => void,
): void {
  void save().catch(reportError);
}
```

**Why:** with a save operation that rejects, `saveBad` leaves the rejection unhandled. `saveAndWait` exposes it to the caller, which must await/catch it; `saveInBackground` reports it. Assume the background reporter does not throw and `save` returns a Promise rather than throwing synchronously. If successful saving is required before navigation, background execution is not a suitable correction.

## Runtime and module compatibility

- Confirm `target`, `lib`, `module`, and `moduleResolution` match the runtime/bundler. A DOM type being available does not make a browser API exist on the server.
- Check package `exports`, `type`, extension requirements, and type-only imports at ESM/CommonJS boundaries.
- For shared packages, validate declarations and emitted code against their promised consumer versions.
- New compiler errors from dependency declarations may require aligned library or `@types` versions, not a broad `skipLibCheck` change.

## Compiler migrations

Version-sensitive changes should be reviewed against their actual target release:

- TypeScript 6 changes defaults including `strict`, `types`, and `rootDir`; check ambient type availability and emitted directory layout. Deprecated options such as `baseUrl` and legacy module resolution need migration. See [6.0 release notes](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-6-0.html).
- TypeScript 7 uses the native compiler and 7.0 does not ship a compiler API. Check platform/tooling support and libraries that import the old API, use custom transformers, or integrate the language service. Some tools need TypeScript 6 alongside 7. CLI compilation compatibility does not imply compiler API compatibility. See [7.0 release announcement](https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/).
- `noUncheckedIndexedAccess` and `exactOptionalPropertyTypes` provide checks beyond `strict`. Evaluate enabling them as a scoped configuration change, not a prerequisite for every PR.

## Tooling and tests

Use configured typecheck, lint, and test commands. For new typescript-eslint configurations, consult [typed linting](https://typescript-eslint.io/getting-started/typed-linting/) for flat config, type-aware presets, and `projectService`; check supported compiler versions before adopting them. Avoid imposing a replacement linter setup during an unrelated review.

Prioritize tests at runtime boundaries: malformed data, missing optional fields, HTTP errors, partial failures, and operations finishing out of order.

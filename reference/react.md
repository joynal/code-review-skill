# React Review Guide

Read the installed React/react-dom versions, framework/router, rendering mode, and compiler configuration first. React features and framework conventions are not interchangeable.

## State, identity, and Hooks

- Ordinary Hooks must retain call order across renders. React 19's `use` is an exception: it may appear in conditions and loops, but must run within a component or Hook and not inside `try/catch`. See [use](https://react.dev/reference/react/use).
- Trace stale closures, state updates derived from an older render, and in-place mutations of shared state or props. Use functional updates when the new value depends on pending state.
- Changing a component type or key remounts it. Look for nested component definitions and unstable keys that reset input, focus, or state; an index key is problematic when item identity can change.
- Check controlled/uncontrolled input transitions, accessible labels, keyboard behavior, and pending/error states.

## Effects and asynchronous work

- Effects synchronize external systems. Verify dependencies against the values read and check setup/cleanup symmetry for subscriptions, timers, and connections.
- Reproduce out-of-order responses when a dependency changes. Cancellation or an ignore flag must also guard error and loading updates where stale requests could overwrite current state.
- A Promise settling after unmount is not by itself proof of a retained-resource leak. Identify the actual stale update or resource lifetime.
- Derived data can usually be calculated during rendering. Whether an interaction belongs in an event handler depends on its trigger; do not move synchronization logic merely because it uses an Effect.
- React 19.2's `useEffectEvent` separates non-reactive Effect logic. It is not a way to conceal a dependency that should resynchronize the Effect. With `Activity`, verify behavior when Effects disconnect while hidden and reconnect when visible. See [React 19.2](https://react.dev/blog/2025/10/01/react-19-2).

## Memoization and rendering cost

Check whether React Compiler is enabled and whether profiling identifies a costly render. Inline objects, functions, and missing `useMemo` are not defects on their own. Identity can matter for a memoized child or an Effect dependency, so trace the consumer before recommending a change.

`useMemo` and `useCallback` are optimization tools, not persistence guarantees. Do not use them to guarantee the lifetime of a resource or a Promise whose stability is required for correctness. See [React Compiler](https://react.dev/learn/react-compiler).

## Actions and forms (React 19+)

- `useActionState` receives previous state before the action payload. Check the argument order and returned state; manual dispatch needs the appropriate Action/Transition context.
- `useFormStatus` from `react-dom` observes an ancestor form, not a form returned by the component calling it. Passing pending state through props is also valid.
- `useOptimistic` setters belong inside an Action, such as a form action or `startTransition`. On success, update the authoritative state; when the Action finishes, that state determines the display. Show failure feedback and distinguish pending UI from confirmed business outcomes. See [useOptimistic](https://react.dev/reference/react/useOptimistic).
- A pending button is not a substitute for server-side idempotency, validation, or authorization.
- Existing `useState` forms are valid. Adopt Actions when they solve a project need, not as a mandatory migration.

## Server Components and security

Apply RSC rules only where the framework supports them.

- Keep secrets and server-only dependencies out of client-imported modules.
- `'use client'` defines a boundary in the module dependency graph. It does not automatically convert Server Components passed as `children` into Client Components. Verify imports and supported serializable props. See [use client](https://react.dev/reference/rsc/use-client).
- Server Functions are reachable entrypoints: validate untrusted arguments and authorize each operation. `'use server'` does not supply access control.
- Distinguish server-only APIs from supported React APIs; “no Hooks in RSC” is too broad.
- For security-sensitive changes, inspect resolved framework/RSC package versions and current official advisories.

## Suspense and data libraries

- Suspense handles supported suspending resources, not arbitrary fetching started in an Effect. Error boundaries and asynchronous rejection handling have different roles.
- Choose boundaries according to the intended loading experience. An existing ancestor error boundary can be sufficient; one per Suspense is not required.
- For client-side `use(promise)`, use a framework/cache-supported stable Promise or one passed from a Server Component. Creating a fresh Promise each render or relying on `useMemo` across initial suspension is unsafe.
- When using a query library, inspect its installed version. Check query keys, invalidation, optimistic rollback, and error handling. Defaults such as a zero `staleTime` are not bugs without a concrete consequence.

## Focused examples

### Stale responses after a prop changes

Inside a component, assume `userId` selects the displayed user, `loadUser(id)` returns a Promise, and `setUser`/`setError` are React state setters. These are alternative Effect bodies; retain the same surrounding component.

```tsx
// Bad: request A can overwrite request B after userId changes to B.
useEffect(() => {
  setUser(null);
  setError(null);
  loadUser(userId).then(setUser, setError);
}, [userId, loadUser]);

// Good: cleanup prevents obsolete success AND failure from changing the view.
useEffect(() => {
  let active = true;
  setUser(null);
  setError(null);
  loadUser(userId).then(
    user => { if (active) setUser(user); },
    error => { if (active) setError(error); },
  );
  return () => { active = false; };
}, [userId, loadUser]);
```

**Why:** resolve B before A and inspect the final user; also reject A after B succeeds. Both outcomes must leave B's view intact. This ignores obsolete results but does not cancel the network request. If request cancellation matters, also pass an AbortSignal to a supporting client. A stable module-level loader need not be a prop. See [Effect cleanup and fetching](https://react.dev/reference/react/useEffect).

### Optimistic state needs an Action and a committed result (React 19+)

Inside an editor component, assume `persistName(next)` resolves with the saved name. The UI displays `optimisticName`, shows `error`, and disables submission while `pending`. The two handlers below are alternatives, using this shared setup:

```tsx
const [name, setName] = useState(initialName);
const [error, setError] = useState<string | null>(null);
const [optimisticName, setOptimisticName] = useOptimistic(name);
const [pending, startTransition] = useTransition();

// Bad: an ordinary event callback provides no Action context.
async function saveBad(next: string) {
  setError(null);
  setOptimisticName(next);
  try {
    await persistName(next);
  } catch {
    setError("Save failed");
  }
}

// Good: keep the optimistic value pending, then commit the server result.
function saveGood(next: string) {
  setError(null);
  startTransition(async () => {
    setOptimisticName(next);
    try {
      const savedName = await persistName(next);
      startTransition(() => { setName(savedName); });
    } catch {
      setError("Save failed");
    }
  });
}
```

**Why:** the bad handler triggers the outside-Action warning and never updates `name`, so it cannot retain the saved result. The good handler displays the optimistic value during the request, then uses the authoritative response; on failure it retains the prior name and reports the error. The nested transition marks the update after `await`. Assume one submission at a time; overlapping writes need additional ordering semantics. See [useOptimistic](https://react.dev/reference/react/useOptimistic).

## Validation

Exercise rapid prop changes, rejected requests, repeated submissions, unmount/remount, and hydration where relevant. Use the existing test stack to assert observable behavior. Missing a preferred testing library or choosing `fireEvent` for a specific low-level event is not a defect.

# React Code Review Guide

- [React Code Review Guide](#react-code-review-guide)
  - [Basic Hooks rules](#basic-hooks-rules)
  - [useEffect mode](#useeffect-mode)
  - [useMemo / useCallback](#usememo--usecallback)
  - [Component design](#component-design)
  - [Error Boundaries \& Suspense](#error-boundaries--suspense)
  - [Server Components (RSC)](#server-components-rsc)
  - [React 19 Actions \& Forms](#react-19-actions--forms)
    - [useActionState](#useactionstate)
    - [useFormStatus](#useformstatus)
    - [useOptimistic](#useoptimistic)
  - [Suspense](#suspense)
    - [Basic Suspense](#basic-suspense)
    - [Multiple independent Suspense boundaries](#multiple-independent-suspense-boundaries)
    - [use() Hook (React 19)](#use-hook-react-19)
  - [Review Checklists](#review-checklists)
    - [Hooks Rules](#hooks-rules)
    - [Performance Optimization (Moderation Principle)](#performance-optimization-moderation-principle)
    - [Component Design](#component-design-1)
    - [State Management](#state-management)
    - [Error Handling](#error-handling)
    - [Server Components (RSC)](#server-components-rsc-1)
    - [React 19 Forms](#react-19-forms)
    - [Suspense \& Streaming](#suspense--streaming)
    - [Test](#test)

---

## Basic Hooks rules

```tsx
// ✅ Hooks must be called at the top level of the component
function BadComponent({ isLoggedIn }) {
  if (isLoggedIn) {
    const [user, setUser] = useState(null);  // Error!
  }
  return <div>...</div>;
}

// ✅ Hooks must be called at the top level of the component
function GoodComponent({ isLoggedIn }) {
  const [user, setUser] = useState(null);
  if (!isLoggedIn) return <LoginPrompt />;
  return <div>{user?.name}</div>;
}
```

---

## useEffect mode

```tsx
// ❌ The dependent array is missing or incomplete
function BadEffect({ userId }) {
  const [user, setUser] = useState(null);
  useEffect(() => {
    fetchUser(userId).then(setUser);
}, []); // Missing userId dependency!
}

return () => { canceled = true; }; // Cleanup function
function GoodEffect({ userId }) {
  const [user, setUser] = useState(null);
  useEffect(() => {
    let cancelled = false;
    fetchUser(userId).then(data => {
      if (!cancelled) setUser(data);
    });
return () => { canceled = true; }; // Cleanup function
  }, [userId]);
}

// ❌ useEffect is used to derive state (anti-pattern)
function BadDerived({ items }) {
  const [filteredItems, setFilteredItems] = useState([]);
  useEffect(() => {
    setFilteredItems(items.filter(i => i.active));
}, [items]); // Unnecessary effect + extra rendering
  return <List items={filteredItems} />;
}

// ✅ Calculate directly during rendering, or use useMemo
function GoodDerived({ items }) {
  const filteredItems = useMemo(
    () => items.filter(i => i.active),
    [items]
  );
  return <List items={filteredItems} />;
}

// ❌ useEffect is used for event response
function BadEventEffect() {
  const [query, setQuery] = useState('');
  useEffect(() => {
    if (query) {
analytics.track('search', { query }); // Should be in the event handler
    }
  }, [query]);
}

// ✅ Perform side effects in event handlers
function GoodEvent() {
  const [query, setQuery] = useState('');
  const handleSearch = (q: string) => {
    setQuery(q);
    analytics.track('search', { query: q });
  };
}
```

---

## useMemo / useCallback

```tsx
// ❌ Over-optimization — constants don’t need useMemo
function OverOptimized() {
const config = useMemo(() => ({ timeout: 5000 }), []); // meaningless
  const handleClick = useCallback(() => {
    console.log('clicked');
}, []); // If not passed to the memo component, it is meaningless
}

// ✅ Optimize only when needed
function ProperlyOptimized() {
const config = { timeout: 5000 }; // Simple object defined directly
  const handleClick = () => console.log('clicked');
}

// ❌ useCallback dependencies always change
function BadCallback({ data }) {
// data is a new object every time it is rendered, useCallback is invalid
  const process = useCallback(() => {
    return data.map(transform);
  }, [data]);
}

// ✅ useMemo + useCallback is used with React.memo
const MemoizedChild = React.memo(function Child({ onClick, items }) {
  return <div onClick={onClick}>{items.length}</div>;
});

function Parent({ rawItems }) {
  const items = useMemo(() => processItems(rawItems), [rawItems]);
  const handleClick = useCallback(() => {
    console.log(items.length);
  }, [items]);
  return <MemoizedChild onClick={handleClick} items={items} />;
}
```

---

## Component design

```tsx
// ❌ Define components within components — create new components on each render
function BadParent() {
function ChildComponent() { // Each rendering is a new function!
    return <div>child</div>;
  }
  return <ChildComponent />;
}

// ✅ Component is defined externally
function ChildComponent() {
  return <div>child</div>;
}
function GoodParent() {
  return <ChildComponent />;
}

// ❌ Props are always new object references
function BadProps() {
  return (
    <MemoizedComponent
style={{ color: 'red' }} // Render a new object each time
onClick={() => {}} // Render a new function each time
    />
  );
}

// ✅ Stable reference
const style = { color: 'red' };
function GoodProps() {
  const handleClick = useCallback(() => {}, []);
  return <MemoizedComponent style={style} onClick={handleClick} />;
}
```

---

## Error Boundaries & Suspense

```tsx
// ❌ No error boundaries
function BadApp() {
  return (
    <Suspense fallback={<Loading />}>
<DataComponent /> {/* Error will cause the entire application to crash */}
    </Suspense>
  );
}

// ✅ Error Boundary Package Suspense
function GoodApp() {
  return (
    <ErrorBoundary fallback={<ErrorUI />}>
      <Suspense fallback={<Loading />}>
        <DataComponent />
      </Suspense>
    </ErrorBoundary>
  );
}
```

---

## Server Components (RSC)

```tsx
// ❌ Use client attributes in Server Component
// app/page.tsx (Server Component by default)
function BadServerComponent() {
  const [count, setCount] = useState(0);  // Error! No hooks in RSC
  return <button onClick={() => setCount(c => c + 1)}>{count}</button>;
}

// ✅ Extract interaction logic to Client Component
// app/counter.tsx
'use client';
function Counter() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(c => c + 1)}>{count}</button>;
}

// app/page.tsx (Server Component)
async function GoodServerComponent() {
<Counter /> {/* Client component */}
  return (
    <div>
      <h1>{data.title}</h1>
// ❌ 'use client' is not properly placed — the entire tree becomes client
    </div>
  );
}

// ❌ 'use client' is not properly placed — the entire tree becomes client
// layout.tsx
'use client'; // This will make all child components client components
export default function Layout({ children }) { ... }

// ✅ Only use 'use client' on components that require interaction
// Isolate client logic to leaf components
```

---

## React 19 Actions & Forms

React 19 introduces the Actions system and new form processing Hooks to simplify asynchronous operations and optimistic updates.

### useActionState

```tsx
// ❌ Traditional way: multiple state variables
function OldForm() {
  const [isPending, setIsPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState(null);

  const handleSubmit = async (formData: FormData) => {
    setIsPending(true);
    setError(null);
    try {
      const result = await submitForm(formData);
      setData(result);
    } catch (e) {
      setError(e.message);
    } finally {
      setIsPending(false);
    }
  };
}

// ✅ React 19: useActionState unified management
import { useActionState } from 'react';

function NewForm() {
  const [state, formAction, isPending] = useActionState(
    async (prevState, formData: FormData) => {
      try {
        const result = await submitForm(formData);
        return { success: true, data: result };
      } catch (e) {
        return { success: false, error: e.message };
      }
    },
    { success: false, data: null, error: null }
  );

  return (
    <form action={formAction}>
      <input name="email" />
      <button disabled={isPending}>
        {isPending ? 'Submitting...' : 'Submit'}
      </button>
      {state.error && <p className="error">{state.error}</p>}
    </form>
  );
}
```

### useFormStatus

```tsx
// ❌ Props transparently transmit form status
function BadSubmitButton({ isSubmitting }) {
  return <button disabled={isSubmitting}>Submit</button>;
}

// ✅ useFormStatus access parent <form> status (no props required)
import { useFormStatus } from 'react-dom';

function SubmitButton() {
  const { pending, data, method, action } = useFormStatus();
// Note: must be used in subcomponents inside <form>
  return (
    <button disabled={pending}>
      {pending ? 'Submitting...' : 'Submit'}
    </button>
  );
}

// ❌ useFormStatus is called in the form sibling component - does not work
function BadForm() {
const { pending } = useFormStatus(); // The status cannot be obtained here!
  return (
    <form action={action}>
      <button disabled={pending}>Submit</button>
    </form>
  );
}

// ✅ useFormStatus must be in the subcomponent of form
function GoodForm() {
  return (
    <form action={action}>
<SubmitButton /> {/* useFormStatus is called here */}
    </form>
  );
}
```

### useOptimistic

```tsx
// ❌ Wait for server response before updating UI
function SlowLike({ postId, likes }) {
  const [likeCount, setLikeCount] = useState(likes);
  const [isPending, setIsPending] = useState(false);

  const handleLike = async () => {
    setIsPending(true);
const newCount = await likePost(postId); // Wait...
    setLikeCount(newCount);
    setIsPending(false);
  };
}

// ✅ useOptimistic instant feedback, automatic rollback on failure
import { useOptimistic } from 'react';

function FastLike({ postId, likes }) {
  const [optimisticLikes, addOptimisticLike] = useOptimistic(
    likes,
    (currentLikes, increment: number) => currentLikes + increment
  );

  const handleLike = async () => {
addOptimisticLike(1); // Update UI immediately
    try {
await likePost(postId); // Background synchronization
    } catch {
// React automatically rolls back to the original value of likes
    }
  };

  return <button onClick={handleLike}>{optimisticLikes} likes</button>;
}
```

## Suspense

### Basic Suspense

```tsx
// ❌ Traditional loading state management
function OldComponent() {
  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchData().then(setData).finally(() => setIsLoading(false));
  }, []);

  if (isLoading) return <Spinner />;
  return <DataView data={data} />;
}

// ✅ Suspense declarative loading state
function NewComponent() {
  return (
    <Suspense fallback={<Spinner />}>
### Multiple independent Suspense boundaries
    </Suspense>
  );
}
```

### Multiple independent Suspense boundaries

```tsx
// ❌ Single boundary - all content is loaded together
function BadLayout() {
  return (
    <Suspense fallback={<FullPageSpinner />}>
      <Header />
<Sidebar /> {/* Fast */}
<Sidebar /> {/* Fast */}
    </Suspense>
  );
}

// ✅ Independent borders - each part streams independently
function GoodLayout() {
  return (
    <>
<Header /> {/* Display immediately */}
      <div className="flex">
        <Suspense fallback={<ContentSkeleton />}>
<MainContent /> {/* Independent loading */}
        </Suspense>
        <Suspense fallback={<SidebarSkeleton />}>
<Sidebar /> {/* Independent loading */}
        </Suspense>
      </div>
    </>
  );
}
```

### use() Hook (React 19)

```tsx
// ✅ Read Promise in the component
import { use } from 'react';

function Comments({ commentsPromise }) {
const comments = use(commentsPromise); // Automatically trigger Suspense
  return (
    <ul>
      {comments.map(c => <li key={c.id}>{c.text}</li>)}
    </ul>
  );
}

//The parent component creates Promise and the child component consumes it
function Post({ postId }) {
const commentsPromise = fetchComments(postId); // no await
  return (
    <article>
      <PostContent id={postId} />
      <Suspense fallback={<CommentsSkeleton />}>
        <Comments commentsPromise={commentsPromise} />
      </Suspense>
    </article>
  );
}
```

---

## Review Checklists

### Hooks Rules

- [ ] Hooks are called at the top level of components/custom hooks.
- [ ] Hooks are called without a condition/loop.
- [ ] useEffect dependency array complete
- [ ] useEffect has cleanup functions (subscriptions/timers/requests).
- [ ] The derived state was not calculated using useEffect.

### Performance Optimization (Moderation Principle)

- [ ] useMemo/useCallback should only be used in scenarios where it is truly needed.
- [ ] React.memo works in conjunction with stable props references
- [ ] No child component is defined within the component.
- [ ] No new object/function is created in JSX (unless passed to a non-memo component)
- [ ] Long lists use virtualization (react-window/react-virtual)

### Component Design

- [ ] Components have a single responsibility and should not exceed 200 lines.
- [ ] Separation of logic and presentation (Custom Hooks)
- [ ] The Props interface is clear and uses TypeScript.
- [ ] Avoid Props Drilling (consider context or combination)

### State Management

- [ ] Proximity principle (minimum necessary range)
- [ ] Use useReducer for complex states
- [ ] Global state uses Context or a state library.
- [ ] Avoid unnecessary state (derivative > storage)

### Error Handling

- [ ] The critical area contains Error Boundary
- [ ] Suspense is used in conjunction with Error Boundary.
- [ ] Asynchronous operations have error handling

### Server Components (RSC)

- [ ] 'use client' is only used for components that require interaction.
- [ ] Server Component does not use Hooks/Event Handling
- [ ] Client-side components should be placed in leaf nodes whenever possible.
- [ ] Data retrieval is performed in the Server Component.

### React 19 Forms

- [ ] Use useActionState instead of multiple useState instances
- [ ] useFormStatus is called in the form child component.
- [ ] useOptimistic Not for critical business operations (payments, etc.)
- [ ] Server Action is correctly marked 'use server'

### Suspense & Streaming

- [ ] Define Suspense boundaries based on user experience requirements
- [ ] Each Suspense has a corresponding Error Boundary
- [ ] Provides a meaningful fallback (skeleton screen > Spinner)
- [ ] Avoid waiting for slow data at the layout level

### Test

- [ ] Using @testing-library/react
- [ ] Use screen to search for elements
- [ ] Use userEvent instead of fireEvent
- [ ] Prefer *ByRole for queries
- [ ] Test behavior, not implementation details

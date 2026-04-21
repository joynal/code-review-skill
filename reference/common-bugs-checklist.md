# Common Bugs Checklist

Language-specific bugs and issues to watch for during code review.

## Universal Issues

### Logic Errors
- [ ] Off-by-one errors in loops and array access
- [ ] Incorrect boolean logic (De Morgan's law violations)
- [ ] Missing null/undefined checks
- [ ] Race conditions in concurrent code
- [ ] Incorrect comparison operators (== vs ===, = vs ==)
- [ ] Integer overflow/underflow
- [ ] Floating point comparison issues

### Resource Management
- [ ] Memory leaks (unclosed connections, listeners)
- [ ] File handles not closed
- [ ] Database connections not released
- [ ] Event listeners not removed
- [ ] Timers/intervals not cleared

### Error Handling
- [ ] Swallowed exceptions (empty catch blocks)
- [ ] Generic exception handling hiding specific errors
- [ ] Missing error propagation
- [ ] Incorrect error types thrown
- [ ] Missing finally/cleanup blocks

## TypeScript/JavaScript

### Type Issues
```typescript
// ❌ Using any defeats type safety
function process(data: any) { return data.value; }

// ✅ Use proper types
interface Data { value: string; }
function process(data: Data) { return data.value; }
```

### Async/Await Pitfalls
```typescript
// ❌ Missing await
async function fetch() {
  const data = fetchData();  // Missing await!
  return data.json();
}

// ❌ Unhandled promise rejection
async function risky() {
  const result = await fetchData();  // No try-catch
  return result;
}

// ✅ Proper error handling
async function safe() {
  try {
    const result = await fetchData();
    return result;
  } catch (error) {
    console.error('Fetch failed:', error);
    throw error;
  }
}
```

### React Specific

#### Hooks rule violation
```tsx
// ❌ Conditionally calling Hooks — violates Hooks rules
function BadComponent({ show }) {
  if (show) {
    const [value, setValue] = useState(0);  // Error!
  }
  return <div>...</div>;
}

#### useEffect common mistakes
function GoodComponent({ show }) {
  const [value, setValue] = useState(0);
  if (!show) return null;
  return <div>{value}</div>;
}

// ❌ Call Hooks in the loop
function BadLoop({ items }) {
  items.forEach(item => {
    const [selected, setSelected] = useState(false);  // Error!
  });
}

// ✅ Improve status or use different data structures
function GoodLoop({ items }) {
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  return items.map(item => (
    <Item key={item.id} selected={selectedIds.has(item.id)} />
  ));
}
```

#### useEffect common mistakes
```tsx
// ❌ The dependency array is incomplete — stale closure
function StaleClosureExample({ userId, onSuccess }) {
  const [data, setData] = useState(null);
  useEffect(() => {
    fetchData(userId).then(result => {
      setData(result);
onSuccess(result); // onSuccess may be stale!
    });
}, [userId]); // Missing onSuccess dependency
}

// ✅ Complete dependency array
useEffect(() => {
  fetchData(userId).then(result => {
    setData(result);
    onSuccess(result);
  });
}, [userId, onSuccess]);

setCount(count + 1); // Trigger re-rendering and trigger effect
function InfiniteLoop() {
  const [count, setCount] = useState(0);
  useEffect(() => {
}, [count]); // Infinite loop!
}, [count]); // Infinite loop!
}

// ❌ Missing cleanup function — memory leak
function MemoryLeak({ userId }) {
  const [user, setUser] = useState(null);
  useEffect(() => {
fetchUser(userId).then(setUser); // setUser is still called after the component is uninstalled
  }, [userId]);
}

// ✅ Proper cleaning
function NoLeak({ userId }) {
  const [user, setUser] = useState(null);
  useEffect(() => {
    let cancelled = false;
    fetchUser(userId).then(data => {
      if (!cancelled) setUser(data);
    });
    return () => { cancelled = true; };
  }, [userId]);
}

// ❌ useEffect is used to derive state (anti-pattern)
function BadDerived({ items }) {
  const [total, setTotal] = useState(0);
  useEffect(() => {
    setTotal(items.reduce((a, b) => a + b.price, 0));
// ✅ Calculate directly or use useMemo
}

// ✅ Calculate directly or use useMemo
function GoodDerived({ items }) {
  const total = useMemo(
    () => items.reduce((a, b) => a + b.price, 0),
    [items]
  );
}

// ❌ useEffect is used for event response
function BadEvent() {
  const [query, setQuery] = useState('');
  useEffect(() => {
if (query) logSearch(query); // should be in event handler
  }, [query]);
}

#### useMemo / useCallback misuse
function GoodEvent() {
  const handleSearch = (q: string) => {
    setQuery(q);
    logSearch(q);
  };
}
```

#### useMemo / useCallback misuse
```tsx
// ❌ Over-optimization — constants don’t need memo
function OverOptimized() {
const config = useMemo(() => ({ api: '/v1' }), []); // meaningless
const noop = useCallback(() => {}, []); // meaningless
}

// ❌ useMemo with empty dependencies (may hide bugs)
function EmptyDeps({ user }) {
  const greeting = useMemo(() => `Hello ${user.name}`, []);
// greeting is not updated when user changes!
}

// ❌ useCallback dependencies always change
function UselessCallback({ data }) {
  const process = useCallback(() => {
    return data.map(transform);
}, [data]); // If data is a new reference every time, it is completely invalid
}

// ❌ useMemo/useCallback does not work with React.memo
function Parent() {
  const data = useMemo(() => compute(), []);
  const handler = useCallback(() => {}, []);
  return <Child data={data} onClick={handler} />;
// Child does not use React.memo, these optimizations are meaningless
}

// ✅ The right optimization combination
const MemoChild = React.memo(function Child({ data, onClick }) {
  return <button onClick={onClick}>{data}</button>;
});

function Parent() {
  const data = useMemo(() => expensiveCompute(), [dep]);
  const handler = useCallback(() => {}, []);
  return <MemoChild data={data} onClick={handler} />;
}
```

#### Component design issues
```tsx
// ❌ Define components within components
function Parent() {
// Create a new Child function for each render, resulting in a complete remount
  const Child = () => <div>child</div>;
  return <Child />;
}

// ✅ Component is defined externally
const Child = () => <div>child</div>;
function Parent() {
  return <Child />;
}

// ❌ Props are always new references — destroy memo
function BadProps() {
  return (
    <MemoComponent
style={{ color: 'red' }} // Render a new object each time
onClick={() => handle()} // Render a new function each time
items={data.filter(x => x)} // Render a new array each time
    />
  );
}

// ❌ Modify props directly
function MutateProps({ user }) {
user.name = 'Changed'; // Never do this!
  return <div>{user.name}</div>;
}
```

#### ❌ Server Component mistakes
```tsx
// ❌ Use client API in Server Component
// app/page.tsx (default is Server Component)
export default function Page() {
  const [count, setCount] = useState(0);  // Error!
  useEffect(() => {}, []);  // Error!
  return <button onClick={() => {}}>Click</button>;  // Error!
}

// ✅Move interaction logic to Client Component
// app/counter.tsx
'use client';
export function Counter() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(c => c + 1)}>{count}</button>;
}

// app/page.tsx
import { Counter } from './counter';
export default async function Page() {
const data = await fetchData(); // Server Component can await directly
  return <Counter initialCount={data.count} />;
}

// ❌ Mark 'use client' on the parent component, and the entire subtree becomes the client
// layout.tsx
'use client'; // Bad idea! All child components become client components
export default function Layout({ children }) { ... }
```

#### Common testing errors
```tsx
// ❌ Use container query
const { container } = render(<Component />);
const button = container.querySelector('button'); // Not recommended

// ✅ Use screen and semantic queries
render(<Component />);
const button = screen.getByRole('button', { name: /submit/i });

// ❌ Use fireEvent
fireEvent.click(button);

// ✅ Use userEvent
await userEvent.click(button);

// ❌ Test implementation details
expect(component.state.isOpen).toBe(true);

// ✅ Test behavior
expect(screen.getByRole('dialog')).toBeVisible();

// ✅ Use findBy asynchronously
await screen.getByText('Hello'); // getBy is synchronous

// ✅ Use findBy asynchronously
await screen.findByText('Hello'); // findBy will wait
```

### React Common Mistakes Checklist
- [ ] Hooks are not called at the top level (in conditions/loops)
- [ ] useEffect dependency array is incomplete
- [ ] useEffect missing cleanup function
- [ ] useEffect for derived state calculations
- [ ] useMemo/useCallback overuse
- [ ] useMemo/useCallback does not work with React.memo
- [ ] Define subcomponents within components
- [ ] Props are new object/function references (when passed to the memo component)
- [ ] directly modify props
- [ ] The list is missing the key or uses index as the key
- [ ] Server Component uses client API
- [ ] Test using container query instead of screen
- [ ] Test using container query instead of screen
- [ ] Test implementation details rather than behavior

### React 19 Actions & Forms Error

```tsx
// ❌ Directly setState in Action instead of returning the state

// ❌ Directly setState in Action instead of returning the state
const [state, action] = useActionState(async (prev, formData) => {
setSomeState(newValue); // Error! should return the new state
}, initialState);

// ✅ Return to new state
const [state, action] = useActionState(async (prev, formData) => {
  const result = await submitForm(formData);
return { ...prev, data: result }; // Return to new state
}, initialState);

// ❌ Forgot to handle isPending
const [state, action] = useActionState(submitAction, null);
return <button>Submit</button>; // User can click repeatedly

// ✅ Use isPending to disable the button
const [state, action, isPending] = useActionState(submitAction, null);
return <button disabled={isPending}>Submit</button>;

// === useFormStatus error ===

// ❌ Call useFormStatus at the same level as form
function Form() {
const { pending } = useFormStatus(); // Always undefined!
  return <form><button disabled={pending}>Submit</button></form>;
}

// ✅ Called in child components
function SubmitButton() {
  const { pending } = useFormStatus();
  return <button disabled={pending}>Submit</button>;
}
function Form() {
  return <form><SubmitButton /></form>;
}

// === useOptimistic error ===

// ❌ For critical business operations
function PaymentButton() {
  const [optimisticPaid, setPaid] = useOptimistic(false);
  const handlePay = async () => {
setPaid(true); // Danger: Shows paid but may fail
    await processPayment();
  };
}

// ❌ The UI state after rollback is not processed
const [optimisticLikes, addLike] = useOptimistic(likes);
// The UI rolls back after failure, but the user may be confused why the likes disappeared

// ✅ Provide failure feedback
const handleLike = async () => {
  addLike(1);
  try {
    await likePost();
  } catch {
toast.error('Like failed, please try again'); // Notify the user
  }
};
```

### React 19 Forms Checklist
- [ ] useActionState returns new state instead of setState
- [ ] useActionState correctly uses isPending to disable submission
- [ ] useFormStatus is called in the form subcomponent
- [ ] useOptimistic is not used for key operations (payment, deletion, etc.)
- [ ] User feedback when useOptimistic fails
- [ ] Server Action correctly tagged 'use server'

### Suspense & Streaming Error

```tsx
// === Suspense boundary error ===

// ❌ One Suspense for the entire page - slow content blocks fast content
function BadPage() {
  return (
    <Suspense fallback={<FullPageLoader />}>
<FastHeader /> {/* Fast */}
<SlowMainContent /> {/* Slow - blocking the entire page */}
<FastFooter /> {/* Fast */}
    </Suspense>
  );
}

// ✅ Independent boundaries, non-blocking each other
function GoodPage() {
  return (
    <>
      <FastHeader />
      <Suspense fallback={<ContentSkeleton />}>
        <SlowMainContent />
      </Suspense>
      <FastFooter />
    </>
  );
}

// ❌ No Error Boundary
function NoErrorHandling() {
  return (
    <Suspense fallback={<Loading />}>
<DataFetcher /> {/* Throwing an error causes a white screen */}
    </Suspense>
  );
}

// ✅ Error Boundary + Suspense
function WithErrorHandling() {
  return (
    <ErrorBoundary fallback={<ErrorFallback />}>
      <Suspense fallback={<Loading />}>
        <DataFetcher />
      </Suspense>
    </ErrorBoundary>
  );
}

// === use() Hook error ===

// ❌ Create Promise outside the component (new Promise each time it is rendered)
function BadUse() {
const data = use(fetchData()); // Create a new Promise every time you render!
  return <div>{data}</div>;
}

// ✅ Created in the parent component and passed through props
function Parent() {
  const dataPromise = useMemo(() => fetchData(), []);
  return <Child dataPromise={dataPromise} />;
}
function Child({ dataPromise }) {
  const data = use(dataPromise);
  return <div>{data}</div>;
}

// === Next.js Streaming Error ===

// ❌ await slow data in layout.tsx - block all subpages
// app/layout.tsx
export default async function Layout({ children }) {
const config = await fetchSlowConfig(); // Block the entire application!
  return <ConfigProvider value={config}>{children}</ConfigProvider>;
}

// ✅ Place slow data at page level or use Suspense
// app/layout.tsx
export default function Layout({ children }) {
  return (
    <Suspense fallback={<ConfigSkeleton />}>
      <ConfigProvider>{children}</ConfigProvider>
    </Suspense>
  );
}
```

### Suspense Checklist
- [ ] Slow content has independent Suspense boundary
- [ ] Each Suspense has a corresponding Error Boundary
- [ ] fallback is a meaningful skeleton screen (not a simple spinner)
- [ ] Promise for use() is not created at render time
- [ ] does not await slow data in layout
- [ ] Nesting level does not exceed 3 levels
- [ ] queryKey contains all parameters that affect the data
- [ ] sets a reasonable staleTime (not the default 0)
- [ ] useSuspenseQuery is not used enabled
- [ ] v5 uses single object argument syntax
- [ ] Optimistic updates have complete rollback logic
- [ ] v5 uses single object argument syntax
- [ ] Understand isPending vs isLoading vs isFetching

### TypeScript/JavaScript Common Mistakes
- [ ] `==` instead of `===`
- [ ] Modifying array/object during iteration
- [ ] `this` context lost in callbacks
- [ ] Missing `key` prop in lists
- [ ] Closure capturing loop variable
- [ ] parseInt without radix parameter

## Python

### Mutable Default Arguments
```python
# ❌ Bug: List shared across all calls
def add_item(item, items=[]):
    items.append(item)
    return items

# ✅ Correct
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

### Exception Handling
```python
# ❌ Catching everything, including KeyboardInterrupt
try:
    risky_operation()
except:
    pass

# ✅ Catch specific exceptions
try:
    risky_operation()
except ValueError as e:
    logger.error(f"Invalid value: {e}")
    raise
```

### Class Attributes
```python
# ❌ Shared mutable class attribute
class User:
    permissions = []  # Shared across all instances!

# ✅ Initialize in __init__
class User:
    def __init__(self):
        self.permissions = []
```

## SQL

### Injection Vulnerabilities
```sql
-- ❌ String concatenation (SQL injection risk)
query = "SELECT * FROM users WHERE id = " + user_id

-- ✅ Parameterized queries
query = "SELECT * FROM users WHERE id = ?"
cursor.execute(query, (user_id,))
```

### Performance Issues
- [ ] Missing indexes on filtered/joined columns
- [ ] SELECT * instead of specific columns
- [ ] N+1 query patterns
- [ ] Missing LIMIT on large tables
- [ ] Inefficient subqueries vs JOINs

### Common Mistakes
- [ ] Not handling NULL comparisons correctly
- [ ] Missing transactions for related operations
- [ ] Incorrect JOIN types
- [ ] Case sensitivity issues
- [ ] Date/timezone handling errors

## API Design

### REST Issues
- [ ] Inconsistent resource naming
- [ ] Wrong HTTP methods (POST for idempotent operations)
- [ ] Missing pagination for list endpoints
- [ ] Incorrect status codes
- [ ] Missing rate limiting

### Data Validation
- [ ] Missing input validation
- [ ] Incorrect data type validation
- [ ] Missing length/range checks
- [ ] Not sanitizing user input
- [ ] Trusting client-side validation

## Testing

### Test Quality Issues
- [ ] Testing implementation details instead of behavior
- [ ] Missing edge case tests
- [ ] Flaky tests (non-deterministic)
- [ ] Tests with external dependencies
- [ ] Missing negative tests (error cases)
- [ ] Overly complex test setup

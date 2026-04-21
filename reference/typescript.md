# TypeScript/JavaScript Code Review Guide

TypeScript code review guide, covering type system, generics, conditional types, strict mode, async/await patterns, and other core topics.

## Table of Contents

- [Type Safety Basics](#type-safety-basics)
- [Generic Patterns](#generic-patterns)
- [Advanced Types](#advanced-types)
- [Strict Mode Configuration](#strict-mode-configuration)
- [Asynchronous Handling](#asynchronous-handling)
- [Immutability](#immutability)
- [ESLint Rules](#eslint-rules)
- [Review Checklist](#review-checklist)

---

## Type Safety Basics

### Avoid using any

```typescript
// ❌ Using any defeats type safety
function processData(data: any) {
  return data.value;  // No type checking, may crash at runtime
}

// ✅ Use proper types
interface DataPayload {
  value: string;
}
function processData(data: DataPayload) {
  return data.value;
}

// ✅ For unknown types, use unknown + type guards
function processUnknown(data: unknown) {
  if (typeof data === 'object' && data !== null && 'value' in data) {
    return (data as { value: string }).value;
  }
  throw new Error('Invalid data');
}
```

// ❌ Unsafe type assertion

```typescript
// ❌ Unsafe type assertion
function getLength(value: string | string[]) {
return (value as string[]).length; // If it is string, an error will occur
}

// ✅ Use type guards
function getLength(value: string | string[]): number {
  if (Array.isArray(value)) {
    return value.length;
  }
  return value.length;
}

// ✅ Use in operator
interface Dog { bark(): void }
interface Cat { meow(): void }

function speak(animal: Dog | Cat) {
  if ('bark' in animal) {
    animal.bark();
  } else {
    animal.meow();
  }
}
```

### Literal type and as const

```typescript
// ❌ The type is too broad
const config = {
  endpoint: '/api',
method: 'GET' // type is string
};

// ✅ Use as const to get the literal type
const config = {
  endpoint: '/api',
  method: 'GET'
} as const; // method type is 'GET'

// ✅ for function parameters
function request(method: 'GET' | 'POST', url: string) { ... }
request(config.method, config.endpoint); // Correct!
```

---

// ❌ Repeat code

### Basic generics

```typescript
// ❌ Repeat code
function getFirstString(arr: string[]): string | undefined {
  return arr[0];
}
function getFirstNumber(arr: number[]): number | undefined {
  return arr[0];
}

// ✅ Use generics
function getFirst<T>(arr: T[]): T | undefined {
  return arr[0];
}
```

### Generic constraints

```typescript
// ❌ Generics have no constraints and cannot access properties
function getProperty<T>(obj: T, key: string) {
return obj[key]; // Error: cannot index
}

// ✅ Use keyof constraints
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}

const user = { name: 'Alice', age: 30 };
getProperty(user, 'name'); // The return type is string
getProperty(user, 'foo'); // Error: 'foo' is not in keyof User
getProperty(user, 'foo'); // Error: 'foo' is not in keyof User
```

### Generic default value

```typescript
// You can not specify generic parameters
interface ApiResponse<T = unknown> {
  data: T;
  status: number;
  message: string;
}

// You can not specify generic parameters
const response: ApiResponse = { data: null, status: 200, message: 'OK' };
// You can also specify
const userResponse: ApiResponse<User> = { ... };
```

### Common generic tool types

```typescript
// ✅ Make good use of built-in tool types
interface User {
  id: number;
  name: string;
  email: string;
}

type PartialUser = Partial<User>; // All attributes are optional
type RequiredUser = Required<User>; // All properties are required
type ReadonlyUser = Readonly<User>; // All properties are read-only
type UserKeys = keyof User;               // 'id' | 'name' | 'email'
type NameOnly = Pick<User, 'name'>;       // { name: string }
type WithoutId = Omit<User, 'id'>;        // { name: string; email: string }
type UserRecord = Record<string, User>;   // { [key: string]: User }
```

---

## Advanced types

### Condition type

```typescript
// ✅ Extract function return type (built-in ReturnType)
type IsString<T> = T extends string ? true : false;

type A = IsString<string>;  // true
type B = IsString<number>;  // false

// ✅ Extract function return type (built-in ReturnType)
type ElementType<T> = T extends (infer U)[] ? U : never;

type Elem = ElementType<string[]>;  // string

// ✅ Extract function return type (built-in ReturnType)
type MyReturnType<T> = T extends (...args: any[]) => infer R ? R : never;
```

### Mapping type

```typescript
// ✅ Convert all properties of the object type
type Nullable<T> = {
  [K in keyof T]: T[K] | null;
};

interface User {
  name: string;
  age: number;
}

type NullableUser = Nullable<User>;
// { name: string | null; age: number | null }

// ✅ API route type
type Getters<T> = {
  [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K];
};

type UserGetters = Getters<User>;
// { getName: () => string; getAge: () => number }
```

### Template literal type

```typescript
// ✅ Type-safe event name
type EventName = 'click' | 'focus' | 'blur';
type HandlerName = `on${Capitalize<EventName>}`;
// 'onClick' | 'onFocus' | 'onBlur'

// ✅ API route type
type ApiRoute = `/api/${string}`;
const route: ApiRoute = '/api/users';  // OK
const badRoute: ApiRoute = '/users';   // Error
```

### Discriminated Unions

```typescript
// ✅ Use discriminant properties to achieve type safety
type Result<T, E> =
  | { success: true; data: T }
  | { success: false; error: E };

function handleResult(result: Result<User, Error>) {
  if (result.success) {
console.log(result.data.name); // TypeScript knows that data exists
  } else {
console.log(result.error.message); // TypeScript knows error exists
  }
}

// ✅ Redux Action mode
type Action =
  | { type: 'INCREMENT'; payload: number }
  | { type: 'DECREMENT'; payload: number }
  | { type: 'RESET' };

function reducer(state: number, action: Action): number {
  switch (action.type) {
    case 'INCREMENT':
return 0; // No payload here
    case 'DECREMENT':
      return state - action.payload;
    case 'RESET':
return 0; // No payload here
  }
}
```

---

## Strict mode configuration

### Recommended tsconfig.json

```json
{
  "compilerOptions": {
// ✅ The strict option must be turned on
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "strictBindCallApply": true,
    "strictPropertyInitialization": true,
    "noImplicitThis": true,
    "useUnknownInCatchVariables": true,

// ✅ Additional recommended options
    "noUncheckedIndexedAccess": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "exactOptionalPropertyTypes": true,
    "noPropertyAccessFromIndexSignature": true
  }
}
```

### Impact of noUncheckedIndexedAccess

```typescript
// tsconfig: "noUncheckedIndexedAccess": true

const arr = [1, 2, 3];
const first = arr[0]; // type is number | undefined

// ❌ Direct use may cause errors
// ✅ Check first

// ✅ Check first
if (first !== undefined) {
  console.log(first.toFixed(2));
}

// ✅ Or use non-null assertion (when determined)
console.log(arr[0]!.toFixed(2));
```

---

### Promise error handling

// ❌ Promise.all If one fails, all fail

```typescript
// ❌ Not handling async errors
async function fetchUser(id: string) {
  const response = await fetch(`/api/users/${id}`);
return response.json(); // Network error not handled
}

// ✅ Handle errors properly
async function fetchUser(id: string): Promise<User> {
  try {
    const response = await fetch(`/api/users/${id}`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to fetch user: ${error.message}`);
    }
    throw error;
  }
}
```

### Promise.all vs Promise.allSettled

```typescript
// ❌ Promise.all If one fails, all fail
async function fetchAllUsers(ids: string[]) {
  const users = await Promise.all(ids.map(fetchUser));
return users; // If one fails, all fail
}

// ✅ Promise.allSettled Get all results
async function fetchAllUsers(ids: string[]) {
  const results = await Promise.allSettled(ids.map(fetchUser));

  const users: User[] = [];
  const errors: Error[] = [];

  for (const result of results) {
    if (result.status === 'fulfilled') {
      users.push(result.value);
    } else {
      errors.push(result.reason);
    }
  }

  return { users, errors };
}
```

### Race condition handling

```typescript
.then(setResults); // Old requests may be returned later!
function useSearch() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);

  useEffect(() => {
    fetch(`/api/search?q=${query}`)
      .then(r => r.json())
.then(setResults); // Old requests may be returned later!
  }, [query]);
}

// ✅ Use AbortController
function useSearch() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);

  useEffect(() => {
    const controller = new AbortController();

    fetch(`/api/search?q=${query}`, { signal: controller.signal })
      .then(r => r.json())
      .then(setResults)
      .catch(e => {
        if (e.name !== 'AbortError') throw e;
      });

    return () => controller.abort();
  }, [query]);
}
```

---

## Immutability

### Readonly and ReadonlyArray

```typescript
// ✅ Use readonly to prevent modifications
function processUsers(users: User[]) {
users.sort((a, b) => a.name.localeCompare(b.name)); // The original array has been modified!
  return users;
}

// ✅ Use readonly to prevent modifications
function processUsers(users: readonly User[]): User[] {
  return [...users].sort((a, b) => a.name.localeCompare(b.name));
}

// ✅ Depth read-only
type DeepReadonly<T> = {
  readonly [K in keyof T]: T[K] extends object ? DeepReadonly<T[K]> : T[K];
};
```

### Invariant function parameters

```typescript
// ✅ Use as const and readonly to protect data
function createConfig<T extends readonly string[]>(routes: T) {
  return routes;
}

const routes = createConfig(['home', 'about', 'contact'] as const);
// The type is readonly ['home', 'about', 'contact']
```

---

## ESLint rules

// ✅ Type safety

```javascript
// .eslintrc.js
module.exports = {
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:@typescript-eslint/recommended-requiring-type-checking',
    'plugin:@typescript-eslint/strict'
  ],
  rules: {
// ✅ Type safety
    '@typescript-eslint/no-explicit-any': 'error',
    '@typescript-eslint/no-unsafe-assignment': 'error',
    '@typescript-eslint/no-unsafe-member-access': 'error',
    '@typescript-eslint/no-unsafe-call': 'error',
    '@typescript-eslint/no-unsafe-return': 'error',

// ✅ Code style
    '@typescript-eslint/explicit-function-return-type': 'warn',
    '@typescript-eslint/no-floating-promises': 'error',
    '@typescript-eslint/await-thenable': 'error',
    '@typescript-eslint/no-misused-promises': 'error',

// ✅ Code style
    '@typescript-eslint/consistent-type-imports': 'error',
    '@typescript-eslint/prefer-nullish-coalescing': 'error',
    '@typescript-eslint/prefer-optional-chain': 'error'
  }
};
```

### Common ESLint bug fixes

```typescript
// ❌ no-floating-promises: Promise must be handled
async function save() { ... }
save(); // Error: Unhandled Promise

// ✅ Explicit processing
await save();
// Or explicitly ignore
save().catch(console.error);
// Or explicitly ignore
void save();

// ❌ no-misused-promises: Promises cannot be used in non-async locations
const items = [1, 2, 3];
items.forEach(async (item) => {  // Error!
  await processItem(item);
});

// ✅ Use for...of
for (const item of items) {
  await processItem(item);
}
// or Promise.all
await Promise.all(items.map(processItem));
```

---

## Review Checklist

### Type system
- [ ] No use of `any` (use `unknown` + type guards instead)
- [ ] Complete and meaningful naming of interfaces and types
- [ ] Use generics to improve code reusability
- [ ] union types have correct type narrowing
- [ ] Make good use of tool types (Partial, Pick, Omit, etc.)

### Generics
- [ ] Generics have appropriate constraints (extends)
- [ ] Generic parameters have sensible default values
- [ ] Avoid overgeneralization (KISS principle)

### Strict mode
- [ ] tsconfig.json enabled strict: true
- [ ] noUncheckedIndexedAccess enabled
- [ ] Do not use @ts-ignore (use @ts-expect-error instead)

### Asynchronous code
- [ ] async function has error handling
- [ ] Promise rejection is handled correctly
- [ ] No floating promises (unhandled Promise)
- [ ] Use Promise.all or Promise.allSettled for concurrent requests
- [ ] Race conditions are handled using AbortController

### Immutability
- [ ] Do not modify function parameters directly
- [ ] Create new objects/arrays using spread operator
- [ ] Consider using the readonly modifier

### ESLint
- [ ] Use @typescript-eslint/recommended
- [ ] No ESLint warnings or errors
- [ ] Use consistent-type-imports

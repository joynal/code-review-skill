# Performance Review Guide

## Table of contents

- [Front-end performance (Core Web Vitals)](#front-end-performance-core-web-vitals)
- [JavaScript Performance](#javascript-performance)
- [Memory Management](#memory-management)
- [Database Performance](#database-performance)
- [API Performance](#api-performance)
- [Algorithmic complexity](#algorithmic-complexity)
- [Performance Review Checklist](#performance-review-checklist)

---

## Front-end performance (Core Web Vitals)

### 2024 Core Indicators

| Indicator | Full name | Target value | Meaning |
|------|------|--------|------|
| **LCP** | Largest Contentful Paint | ≤ 2.5s | Maximum content painting time |
| **INP** | Interaction to Next Paint | ≤ 200ms | Interaction response time (2024 replacement FID) |
| **CLS** | Cumulative Layout Shift | ≤ 0.1 | Cumulative layout shift |
| **FCP** | First Contentful Paint | ≤ 1.8s | First Contentful Paint |
| **TBT** | Total Blocking Time | ≤ 200ms | Main thread blocking time |

// ❌ LCP image lazy loading - delay key content

```javascript
// ❌ LCP image lazy loading - delay key content
<img src="hero.jpg" loading="lazy" />

// ✅ LCP images load immediately
<img src="hero.jpg" fetchpriority="high" />

// ❌ Unoptimized image format
<img src="hero.png" /> // PNG file is too large

// ✅ Modern image format + responsive
<picture>
  <source srcset="hero.avif" type="image/avif" />
  <source srcset="hero.webp" type="image/webp" />
  <img src="hero.jpg" alt="Hero" />
</picture>
```

**Review Points:**
- [ ] Is the LCP element set with `fetchpriority="high"`?
- [ ] Use WebP/AVIF format?
- [ ] Is there server-side rendering or static generation?
- [ ] Is the CDN configured correctly?

### FCP Optimization Check

```html
<!-- ❌ Render-blocking CSS -->
<link rel="stylesheet" href="all-styles.css" />

<style>/* First screen key style */</style>
<style>/* First screen key style */</style>
<link rel="preload" href="styles.css" as="style" onload="this.onload=null;this.rel='stylesheet'" />

<!-- ❌ Render-blocking fonts -->
@font-face {
  font-family: 'CustomFont';
  src: url('font.woff2');
}

<!-- ✅ Font display optimization -->
@font-face {
  font-family: 'CustomFont';
  src: url('font.woff2');
  font-display: swap;  /* Use system font first, switch after loading */
}
```

### INP optimization check

```javascript
// ❌ Long tasks block the main thread
button.addEventListener('click', () => {
// Synchronization operation that takes 500ms
  processLargeData(data);
  updateUI();
});

// ✅ Split long tasks
button.addEventListener('click', async () => {
// Give up the main thread
  await scheduler.yield?.() ?? new Promise(r => setTimeout(r, 0));

// batch processing
  for (const chunk of chunks) {
    processChunk(chunk);
    await scheduler.yield?.();
  }
  updateUI();
});

// ✅ Use Web Workers to handle complex calculations
const worker = new Worker('heavy-computation.js');
worker.postMessage(data);
worker.onmessage = (e) => updateUI(e.data);
```

### CLS Optimization Check

```css
/* ❌ Media with unspecified size */
img { width: 100%; }

/* ✅ Reserve space */
img {
  width: 100%;
  aspect-ratio: 16 / 9;
}

/* ❌ Dynamically inserting content causes layout to shift */
.ad-container { }

/* ✅ Reserve a fixed height */
.ad-container {
  min-height: 250px;
}
```

**CLS Review Checklist:**
- [ ] Does the image/video have width/height or aspect-ratio?
- [ ] Does font loading use `font-display: swap`?
- [ ] Is space reserved for dynamic content?
- [ ] Avoid inserting content above existing content?

---

## JavaScript Performance

### Code splitting and lazy loading

```javascript
// ❌ Load all code at once
import { HeavyChart } from './charts';
import { PDFExporter } from './pdf';
import { AdminPanel } from './admin';

// ✅ Load on demand
const HeavyChart = lazy(() => import('./charts'));
const PDFExporter = lazy(() => import('./pdf'));

// ✅ Route-level code splitting
const routes = [
  {
    path: '/dashboard',
    component: lazy(() => import('./pages/Dashboard')),
  },
  {
    path: '/admin',
    component: lazy(() => import('./pages/Admin')),
  },
];
```

### Bundle size optimization

```javascript
// ❌ Import the entire library
import _ from 'lodash';
import moment from 'moment';

// ✅ Import on demand
import debounce from 'lodash/debounce';
import { format } from 'date-fns';

// ❌ Tree Shaking is not used
export default {
  fn1() {},
fn2() {}, // not used but packed
};

// ✅ Named export supports Tree Shaking
export function fn1() {}
export function fn2() {}
```

- [ ] Use dynamic import() for code splitting?
- [ ] Use dynamic import() for code splitting?
- [ ] Are large libraries imported on demand?
- [ ] Have you analyzed the bundle size? (webpack-bundle-analyzer)
- [ ] Are there any unused dependencies?

### List rendering optimization

```javascript
// ❌ Render large list
function List({ items }) {
  return (
    <ul>
      {items.map(item => <li key={item.id}>{item.name}</li>)}
    </ul>
); // 10000 pieces of data = 10000 DOM nodes
}

**Big Data Review Points:**
import { FixedSizeList } from 'react-window';

function VirtualList({ items }) {
  return (
    <FixedSizeList
      height={400}
      itemCount={items.length}
      itemSize={35}
    >
      {({ index, style }) => (
        <div style={style}>{items[index].name}</div>
      )}
    </FixedSizeList>
  );
}
```

**Big Data Review Points:**
- [ ] Use virtual scrolling for lists with more than 100 items?
- [ ] Does the table support paging or virtualization?
- [ ] Is there unnecessary full rendering?

---

## Memory management

### Common memory leaks

#### 1. Uncleaned event monitoring

```javascript
// ❌ The event is still listening after the component is uninstalled
useEffect(() => {
  window.addEventListener('resize', handleResize);
}, []);

// ✅ Clean up event monitoring
useEffect(() => {
  window.addEventListener('resize', handleResize);
  return () => window.removeEventListener('resize', handleResize);
}, []);
```

#### 2. Unclear timer

```javascript
// ❌ The timer is not cleared
useEffect(() => {
  setInterval(fetchData, 5000);
}, []);

// ✅ Clean up timer
useEffect(() => {
  const timer = setInterval(fetchData, 5000);
  return () => clearInterval(timer);
}, []);
```

#### 3. Closure reference

```javascript
// ❌ The closure holds a large object reference
function createHandler() {
  const largeData = new Array(1000000).fill('x');

  return function handler() {
// ✅ Only keep necessary data
    console.log(largeData.length);
  };
}

// ✅ Only keep necessary data
function createHandler() {
  const largeData = new Array(1000000).fill('x');
#### 4. Uncleaned subscriptions

  return function handler() {
    console.log(length);
  };
}
```

#### 4. Uncleaned subscriptions

```javascript
// ❌ WebSocket/EventSource is not closed
useEffect(() => {
  const ws = new WebSocket('wss://...');
  ws.onmessage = handleMessage;
}, []);

// ✅ Clean up the connection
useEffect(() => {
  const ws = new WebSocket('wss://...');
  ws.onmessage = handleMessage;
  return () => ws.close();
}, []);
```

### Memory Review Checklist

```markdown
- [ ] Does useEffect have a cleanup function?
- [ ] Is the timer cleared?
- [ ] Is the timer cleared?
- [ ] Is the WebSocket/SSE connection closed?
- [ ] Are large objects released in time?
### Detection Tools
```

### Detection Tools

| Tools | Purpose |
|------|------|
| Chrome DevTools Memory | Heap snapshot analysis |
| MemLab (Meta) | Automated memory leak detection |
| Performance Monitor | Real-time memory monitoring |

---

## Database performance

### N+1 query question

```python
# ❌ N+1 problem - 1 + N queries
users = User.objects.all() # 1 query
for user in users:
print(user.profile.bio) #N queries (one for each user)

# ✅ Eager Loading - 2 queries
users = User.objects.select_related('profile').all()
for user in users:
print(user.profile.bio) # No additional query

# ✅ Many-to-many relationships use prefetch_related
posts = Post.objects.prefetch_related('tags').all()
```

```javascript
// TypeORM example
// ❌ N+1 problem
const users = await userRepository.find();
for (const user of users) {
const posts = await user.posts; // Query every loop
}

// ✅ Eager Loading
const users = await userRepository.find({
  relations: ['posts'],
});
```

### Index optimization

```sql
-- ❌ Full table scan
SELECT * FROM orders WHERE status = 'pending';

-- ✅Add index
CREATE INDEX idx_orders_status ON orders(status);

-- ✅ Range query available indexes
SELECT * FROM users WHERE YEAR(created_at) = 2024;

-- ✅ Range query available indexes
SELECT * FROM users
WHERE created_at >= '2024-01-01' AND created_at < '2025-01-01';

-- ❌ Index failure: LIKE prefix wildcard
SELECT * FROM products WHERE name LIKE '%phone%';

-- ✅ Prefix matching available indexes
SELECT * FROM products WHERE name LIKE 'phone%';
```

### Query optimization

```sql
-- ❌ SELECT * Get unwanted columns
SELECT * FROM users WHERE id = 1;

-- ✅ Only query the required columns
SELECT id, name, email FROM users WHERE id = 1;

-- ❌ No LIMIT for large tables
SELECT * FROM logs WHERE type = 'error';

-- ✅ Paging query
SELECT * FROM logs WHERE type = 'error' LIMIT 100 OFFSET 0;

-- ❌ Execute query in loop
for id in user_ids:
    cursor.execute("SELECT * FROM users WHERE id = %s", (id,))

-- ✅ Batch query
cursor.execute("SELECT * FROM users WHERE id IN %s", (tuple(user_ids),))
```

🔴 Must check:

```markdown
🔴 Must check:
- [ ] Is there an N+1 query?
- [ ] Is the WHERE clause column indexed?
- [ ] Is SELECT * avoided?
- [ ] Is there LIMIT for large table queries?

🟡 Recommended checks:
- [ ] Did you use EXPLAIN to analyze the query plan?
- [ ] Is the composite index column order correct?
- [ ] Are there any unused indexes?
- [ ] Is there slow query log monitoring?
```

---

## API performance

### Pagination implementation

```javascript
// ❌ Return all data
app.get('/users', async (req, res) => {
const users = await User.findAll(); // 100000 items may be returned
  res.json(users);
});

// ✅ Pagination + limit the maximum number
app.get('/users', async (req, res) => {
  const page = parseInt(req.query.page) || 1;
const limit = Math.min(parseInt(req.query.limit) || 20, 100); // Maximum 100
  const offset = (page - 1) * limit;

  const { rows, count } = await User.findAndCountAll({
    limit,
    offset,
    order: [['id', 'ASC']],
  });

  res.json({
    data: rows,
    pagination: {
      page,
      limit,
      total: count,
      totalPages: Math.ceil(count / limit),
    },
  });
});
```

### Caching strategy

```javascript
// ✅ Redis cache example
async function getUser(id) {
  const cacheKey = `user:${id}`;

// 1. Check cache
  const cached = await redis.get(cacheKey);
  if (cached) {
    return JSON.parse(cached);
  }

// 2. Query the database
  const user = await db.users.findById(id);

// 3. Write to cache (set expiration time)
  await redis.setex(cacheKey, 3600, JSON.stringify(user));

  return user;
}

// ✅ HTTP cache header
app.get('/static-data', (req, res) => {
  res.set({
'Cache-Control': 'public, max-age=86400', // 24 hours
    'ETag': 'abc123',
  });
  res.json(data);
});
```

### Response compression

```javascript
// ✅ Enable Gzip/Brotli compression
const compression = require('compression');
app.use(compression());

// ✅ Only return necessary fields
// Request: GET /users?fields=id,name,email
app.get('/users', async (req, res) => {
  const fields = req.query.fields?.split(',') || ['id', 'name'];
  const users = await User.findAll({
    attributes: fields,
  });
  res.json(users);
});
```

### Current limiting protection

```javascript
// ✅ Rate Limit
const rateLimit = require('express-rate-limit');

const limiter = rateLimit({
windowMs: 60 * 1000, // 1 minute
max: 100, // Maximum 100 requests
  message: { error: 'Too many requests, please try again later.' },
});

app.use('/api/', limiter);
```

### API Review Checklist

```markdown
- [ ] Does the list interface have paging?
- [ ] Is there a limit to the maximum number per page?
- [ ] Is hotspot data cached?
- [ ] Is response compression enabled?
- [ ] Is there a rate limit?
- [ ] Return only necessary fields?
```

---

## Algorithm complexity

| Complexity | Name | 10 entries | 1000 entries | 1 million entries | Example |

| Complexity | Name | 10 entries | 1000 entries | 1 million entries | Example |
|--------|------|-------|---------|----------|------|
| O(1) | Constant | 1 | 1 | 1 | Hash lookup |
| O(log n) | Logarithm | 3 | 10 | 20 | Binary search |
| O(n) | Linear | 10 | 1000 | 1 million | Iterate array |
| O(n log n) | Linear logarithm | 33 | 10000 | 20 million | Quick sort |
| O(n²) | square | 100 | 1 million | 1 trillion | nested loops |
| O(2ⁿ) | Exponential | 1024 | ∞ | ∞ | Recursive Fibonacci |

### Identification in code review

```javascript
// ❌ O(n²) - nested loops
function findDuplicates(arr) {
  const duplicates = [];
  for (let i = 0; i < arr.length; i++) {
    for (let j = i + 1; j < arr.length; j++) {
      if (arr[i] === arr[j]) {
        duplicates.push(arr[i]);
      }
    }
  }
  return duplicates;
}

// ✅ O(n) - using Set
function findDuplicates(arr) {
  const seen = new Set();
  const duplicates = new Set();
  for (const item of arr) {
    if (seen.has(item)) {
      duplicates.add(item);
    }
    seen.add(item);
  }
  return [...duplicates];
}
```

```javascript
// ❌ O(n²) - calls includes every time through the loop
function removeDuplicates(arr) {
  const result = [];
  for (const item of arr) {
    if (!result.includes(item)) {  // includes is O(n)
      result.push(item);
    }
  }
  return result;
}

// ✅ O(n) - using Set
function removeDuplicates(arr) {
  return [...new Set(arr)];
}
```

```javascript
// ❌ O(n) search - iterate every time
const users = [{ id: 1, name: 'A' }, { id: 2, name: 'B' }, ...];

function getUser(id) {
  return users.find(u => u.id === id);  // O(n)
}

// ✅ O(1) lookup - using Map
const userMap = new Map(users.map(u => [u.id, u]));

function getUser(id) {
  return userMap.get(id);  // O(1)
}
```

### Space complexity considerations

```javascript
// ⚠️ O(n) space - create new array
const doubled = arr.map(x => x * 2);

// ✅ O(1) Space - Modify in-place (if allowed)
for (let i = 0; i < arr.length; i++) {
  arr[i] *= 2;
}

// ⚠️ If the recursion depth is too large, the stack may overflow.
function factorial(n) {
  if (n <= 1) return 1;
return n * factorial(n - 1); // O(n) stack space
}

// ✅ Iterative version O(1) space
function factorial(n) {
  let result = 1;
  for (let i = 2; i <= n; i++) {
    result *= i;
  }
  return result;
}
```

### Complexity Review Question

```markdown
💡 "The complexity of this nested loop is O(n²), and there will be performance problems when the amount of data is large"
🔴 "Use Array.includes() here in the loop, the overall cost is O(n²), it is recommended to use Set"
🟡 "This recursion depth may cause stack overflow, it is recommended to use iteration or tail recursion"
```

---

## Performance Review Checklist

### 🔴 Must be checked (blocking level)

- [ ] Are LCP images lazy loaded? (shouldn't)
- [ ] Are LCP images lazy loaded? (shouldn't)
- [ ] Is there `transition: all`?
- [ ] Whether to animate width/height/top/left?
- [ ] List >100 items virtualized?

**rear end:**
- [ ] Is there an N+1 query?
- [ ] Does the list interface have paging?
- [ ] Is there SELECT * to check the large table?

**General:**
- [ ] Are there nested loops that are O(n²) or worse?
- [ ] Is useEffect/event listening cleaned up?

### 🟡 Recommended inspection (important level)

**front end:**
- [ ] Are large libraries imported on demand?
- [ ] Are large libraries imported on demand?
- [ ] Do images use WebP/AVIF?
- [ ] Is the WHERE column indexed?

**rear end:**
- [ ] Is hotspot data cached?
- [ ] Is the WHERE column indexed?
- [ ] Is there slow query monitoring?

**API：**
- [ ] Enable response compression?
- [ ] Is there a rate limit?
- [ ] Return only necessary fields?

### 🟢 Optimization suggestions (recommendation level)

- [ ] Have you analyzed the bundle size?
- [ ] Are you using a CDN?
- [ ] Have you done any performance benchmarks?
- [ ] Have you done any performance benchmarks?

---

## Performance measurement threshold

### Front-end indicators

| Indicators | Good | Needs improvement | Poor |
|------|-----|--------|-----|
| LCP | ≤ 2.5s | 2.5-4s | > 4s |
| INP | ≤ 200ms | 200-500ms | > 500ms |
| CLS | ≤ 0.1 | 0.1-0.25 | > 0.25 |
| FCP | ≤ 1.8s | 1.8-3s | > 3s |
| Bundle Size (JS) | < 200KB | 200-500KB | > 500KB |

### Backend metrics

| Indicators | Good | Needs improvement | Poor |
|------|-----|--------|-----|
| API response time | < 100ms | 100-500ms | > 500ms |
| Database query | < 50ms | 50-200ms | > 200ms |
| Page Load | < 3s | 3-5s | > 5s |

---

## Tool recommendation

### Front-end performance

| Tools | Purpose |
|------|------|
| [Lighthouse](https://developer.chrome.com/docs/lighthouse/) | Core Web Vitals Test |
| [WebPageTest](https://www.webpagetest.org/) | Detailed performance analysis |
| [webpack-bundle-analyzer](https://github.com/webpack-contrib/webpack-bundle-analyzer) | Bundle analysis |
| [Chrome DevTools Performance](https://developer.chrome.com/docs/devtools/performance/) | Runtime performance analysis |

### Memory detection

| Tools | Purpose |
|------|------|
| [MemLab](https://github.com/facebookincubator/memlab) | Automated memory leak detection |
| Chrome Memory Tab | Heap snapshot analysis |

### Backend performance

| Tools | Purpose |
|------|------|
| EXPLAIN | Database query plan analysis |
| [pganalyze](https://pganalyze.com/) | PostgreSQL performance monitoring |
| [New Relic](https://newrelic.com/) / [Datadog](https://www.datadoghq.com/) | APM Monitoring |

---

## Reference resources

- [Core Web Vitals - web.dev](https://web.dev/articles/vitals)
- [Optimizing Core Web Vitals - Vercel](https://vercel.com/guides/optimizing-core-web-vitals-in-2024)
- [MemLab - Meta Engineering](https://engineering.fb.com/2022/09/12/open-source/memlab/)
- [Big O Cheat Sheet](https://www.bigocheatsheet.com/)
- [N+1 Query Problem - Stack Overflow](https://stackoverflow.com/questions/97197/what-is-the-n1-selects-problem-in-orm-object-relational-mapping)
- [API Performance Optimization](https://algorithmsin60days.com/blog/optimizing-api-performance/)

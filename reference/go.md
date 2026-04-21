# Go Code Review Guidelines

A code review checklist based on the official Go guidelines, Effective Go, and community best practices.

## Quick Review Checklist

### Required Search Items
- [ ] Whether the error was handled correctly (not ignored, with context)
Does the goroutine [ ] have an exit mechanism (to prevent leakage)?
- [ ] Whether the context was passed and canceled correctly
- [ ] Is the receiver type selection appropriate (value/pointer)?
- [ ] Whether to use `gofmt` for code formatting

### High-Frequency Issues
- [ ] Loop variable capture issue (Go < 1.22)
- [ ] nil Check for completeness
- [ ] Whether to use the map after initialization.
- The use of [ ] defer in loops
- [ ] Variable shadowing

---

## 1. Error handling

### 1.1 Never ignore errors

```go
// ❌ Error: ignore errors
result, _ := SomeFunction()

// ✅ Correct: handle errors
result, err := SomeFunction()
if err != nil {
    return fmt.Errorf("some function failed: %w", err)
}
```

### 1.2 Error packaging and context

```go
// ❌ Error: Lost context
if err != nil {
    return err
}

// ❌ Error: Missing error chain using %v
if err != nil {
    return fmt.Errorf("failed: %v", err)
}

// ✅ Correct: use %w to preserve the error chain
if err != nil {
    return fmt.Errorf("failed to process user %d: %w", userID, err)
}
```

### 1.3 Using errors.Is and errors.As

```go
// ❌ Error: direct comparison (cannot handle wrapping error)
if err == sql.ErrNoRows {
    // ...
}

// ✅ Correct: use errors.Is (supports error chaining)
if errors.Is(err, sql.ErrNoRows) {
    return nil, ErrNotFound
}

// ✅ Correct: use errors.As to extract specific types
var pathErr *os.PathError
if errors.As(err, &pathErr) {
    log.Printf("path error: %s", pathErr.Path)
}
```

### 1.4 Custom error types

```go
// ✅ Recommended: Define sentinel error
var (
    ErrNotFound     = errors.New("not found")
    ErrUnauthorized = errors.New("unauthorized")
)

// ✅ Recommended: Custom errors with context
type ValidationError struct {
    Field   string
    Message string
}

func (e *ValidationError) Error() string {
    return fmt.Sprintf("validation error on %s: %s", e.Field, e.Message)
}
```

### 1.5 Error handling is only done once

```go
// ❌ Error: both recording and returning (repeated processing)
if err != nil {
    log.Printf("error: %v", err)
    return err
}

// ✅ Correct: just return and let the caller decide
if err != nil {
    return fmt.Errorf("operation failed: %w", err)
}

// ✅ Or: just record and process (no return)
if err != nil {
    log.Printf("non-critical error: %v", err)
// Continue executing backup logic
}
```

---

## 2. Concurrency and Goroutine

### 2.1 Avoid Goroutine leaks

```go
// ❌ Error: goroutine can never exit
func bad() {
    ch := make(chan int)
    go func() {
val := <-ch // Blocked forever, no one sends
        fmt.Println(val)
    }()
// Function returns, goroutine leaks
}

// ✅ Correct: use context or done channel
func good(ctx context.Context) {
    ch := make(chan int)
    go func() {
        select {
        case val := <-ch:
            fmt.Println(val)
        case <-ctx.Done():
return // graceful exit
        }
    }()
}
```

### 2.2 Channel usage specifications

```go
ch <- 1 // permanently blocked
var ch chan int
ch <- 1 // permanently blocked

// ❌ Error: Send to closed channel (panic)
close(ch)
ch <- 1 // panic!

// ✅ Correct: sender closes channel
func producer(ch chan<- int) {
defer close(ch) // The sender is responsible for closing
    for i := 0; i < 10; i++ {
        ch <- i
    }
}

// ✅ Correct: Receiver detection is off
for val := range ch {
    process(val)
}
// or
val, ok := <-ch
if !ok {
// channel is closed
}
```

### 2.3 Using sync.WaitGroup

```go
wg.Add(1) // Race condition!
var wg sync.WaitGroup
for i := 0; i < 10; i++ {
    go func() {
wg.Add(1) // Race condition!
        defer wg.Done()
        work()
    }()
}
wg.Wait()

// ✅ Correct: Add before goroutine starts
var wg sync.WaitGroup
for i := 0; i < 10; i++ {
    wg.Add(1)
    go func() {
        defer wg.Done()
        work()
    }()
}
wg.Wait()
```

### 2.4 Avoid capturing variables in loops (Go < 1.22)

```go
// ❌ BUG (Go < 1.22): Capturing loop variables
for _, item := range items {
    go func() {
process(item) // All goroutines may use the same item
    }()
}

// ✅ Correct: pass parameters
for _, item := range items {
    go func(it Item) {
        process(it)
    }(item)
}

// ✅ Go 1.22+: Default behavior fixed, create new variables each iteration
```

### 2.5 Worker Pool mode

```go
// ✅ Recommendation: Limit the number of concurrencies
func processWithWorkerPool(ctx context.Context, items []Item, workers int) error {
    jobs := make(chan Item, len(items))
    results := make(chan error, len(items))

// start worker
    for w := 0; w < workers; w++ {
        go func() {
            for item := range jobs {
                results <- process(item)
            }
        }()
    }

//Send task
    for _, item := range items {
        jobs <- item
    }
    close(jobs)

// collect results
    for range items {
        if err := <-results; err != nil {
            return err
        }
    }
    return nil
}
```

---

## 3. Context usage

### 3.1 Context as the first parameter

```go
// ❌ Error: context is not the first parameter
func Process(data []byte, ctx context.Context) error

// ❌ Error: context is stored in struct
type Service struct {
// ✅ Correct: context as the first parameter, named ctx
}

// ✅ Correct: context as the first parameter, named ctx
func Process(ctx context.Context, data []byte) error
```

### 3.2 Propagate rather than create a new root Context

```go
// ❌ Error: creating a new root context in the call chain
func middleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
ctx := context.Background() // The requested context is lost!
        process(ctx)
        next.ServeHTTP(w, r)
    })
}

// ✅ Correct: get from request and propagate
func middleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        ctx := r.Context()
        ctx = context.WithValue(ctx, key, value)
        process(ctx)
        next.ServeHTTP(w, r.WithContext(ctx))
    })
}
```

### 3.3 Always call the cancel function

```go
// ❌ Error: cancel not called
ctx, cancel := context.WithTimeout(parentCtx, 5*time.Second)
// Missing cancel() call, possible resource leak

// ✅ Correct: use defer to ensure calling
ctx, cancel := context.WithTimeout(parentCtx, 5*time.Second)
defer cancel() // Called even if timeout occurs
```

### 3.4 Respond to Context Cancel

```go
// ✅ Recommended: check context during long operations
func LongRunningTask(ctx context.Context) error {
    for {
        select {
        case <-ctx.Done():
return ctx.Err() // Return context.Canceled or context.DeadlineExceeded
        default:
### 3.5 Distinguish reasons for cancellation
            if err := doChunk(); err != nil {
                return err
            }
        }
    }
}
```

### 3.5 Distinguish reasons for cancellation

```go
// ✅ Distinguish cancellation reasons based on ctx.Err()
if err := ctx.Err(); err != nil {
    switch {
    case errors.Is(err, context.Canceled):
        log.Println("operation was canceled")
    case errors.Is(err, context.DeadlineExceeded):
        log.Println("operation timed out")
    }
    return err
}
```

---

## 4. Interface design

### 4.1 Accept interface and return structure

```go
// ✅ Recommendation: Accept interface (decoupled, easy to test)
func SaveUser(db *sql.DB, user User) error

// ✅ Recommendation: Accept interface (decoupled, easy to test)
type UserStore interface {
    Save(ctx context.Context, user User) error
}

func SaveUser(store UserStore, user User) error

// ❌ Not recommended: return interface
func NewUserService() UserServiceInterface

// ✅ Recommendation: return specific type
func NewUserService(store UserStore) *UserService
```

### 4.2 Define the interface at the consumer

```go
// ❌ Not recommended: define the interface in the implementation package
// package database
type Database interface {
    Query(ctx context.Context, query string) ([]Row, error)
// ... 20 methods
}

// ✅ Recommendation: Define the minimum required interface in the consumer package
// package userservice
type UserQuerier interface {
    QueryUsers(ctx context.Context, filter Filter) ([]User, error)
}
```

### 4.3 Keep interfaces small and focused

```go
// ... more methods
type Repository interface {
    GetUser(id int) (*User, error)
    CreateUser(u *User) error
    UpdateUser(u *User) error
    DeleteUser(id int) error
    GetOrder(id int) (*Order, error)
    CreateOrder(o *Order) error
// ... more methods
}

// ✅ Recommendation: Small and focused interface
type UserReader interface {
    GetUser(ctx context.Context, id int) (*User, error)
}

type UserWriter interface {
    CreateUser(ctx context.Context, u *User) error
    UpdateUser(ctx context.Context, u *User) error
}

//Combined interface
type UserRepository interface {
    UserReader
    UserWriter
}
```

### 4.4 Avoid empty interface abuse

```go
// ❌ Not recommended: excessive use of interface{}
func Process(data interface{}) interface{}

// ✅ Recommendation: Use generics (Go 1.18+)
func Process[T any](data T) T

// ✅ Recommendation: Define specific interfaces
type Processor interface {
    Process() Result
}
```

---

## 5. Receiver type selection

### 5.1 Case of using pointer receiver

```go
// ✅ When you need to modify the receiver
func (u *User) SetName(name string) {
    u.Name = name
}

// ✅ The receiver contains synchronization primitives such as sync.Mutex
type SafeCounter struct {
    mu    sync.Mutex
    count int
}

func (c *SafeCounter) Inc() {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.count++
}

// ✅ Receivers are large structures (avoid copy overhead)
type LargeStruct struct {
    Data [1024]byte
    // ...
}

func (l *LargeStruct) Process() { /* ... */ }
```

### 5.2 Cases of using value receivers

```go
// ✅ The receiver is a small immutable structure
type Point struct {
    X, Y float64
}

func (p Point) Distance(other Point) float64 {
    return math.Sqrt(math.Pow(p.X-other.X, 2) + math.Pow(p.Y-other.Y, 2))
}

// ✅ Receiver is an alias of a basic type
type Counter int

func (c Counter) String() string {
    return fmt.Sprintf("%d", c)
}

// ✅ Receivers are map, func, chan (itself a reference type)
type StringSet map[string]struct{}

func (s StringSet) Contains(key string) bool {
    _, ok := s[key]
    return ok
}
```

### 5.3 Consistency Principle

```go
// ❌ Not recommended: Mixing receiver types
func (u User) GetName() string // value receiver
func (u *User) SetName(n string) // pointer receiver

## 6. Performance optimization
func (u *User) GetName() string { return u.Name }
func (u *User) SetName(n string) { u.Name = n }
```

---

## 6. Performance optimization

### 6.1 Preallocate Slice

```go
// ❌ Not recommended: dynamic growth
var result []int
for i := 0; i < 10000; i++ {
result = append(result, i) // multiple allocations and copies
}

// ✅ Recommended: Pre-allocate known size
result := make([]int, 0, 10000)
for i := 0; i < 10000; i++ {
    result = append(result, i)
}

// ✅ Or initialize directly
result := make([]int, 10000)
for i := 0; i < 10000; i++ {
    result[i] = i
}
```

// ❌ May escape to the heap

```go
// ❌ May escape to the heap
func NewUser() *User {
return &User{} // Escape to the heap
}

// ✅ Consider return value (if applicable)
func NewUser() User {
return User{} // may be allocated on the stack
}

// Check escape analysis
// go build -gcflags '-m -m' ./...
```

### 6.3 Use sync.Pool to reuse objects

```go
// ✅ Recommendation: Use sync.Pool for objects that are frequently created/destroyed.
var bufferPool = sync.Pool{
    New: func() interface{} {
        return new(bytes.Buffer)
    },
}

func ProcessData(data []byte) string {
    buf := bufferPool.Get().(*bytes.Buffer)
    defer func() {
        buf.Reset()
        bufferPool.Put(buf)
    }()

    buf.Write(data)
    return buf.String()
}
```

### 6.4 String splicing optimization

```go
// ❌ Not recommended: use + splicing in loops
var result string
for _, s := range strings {
result += s // Create a new string each time
}

// ✅ Recommendation: use strings.Builder
var builder strings.Builder
for _, s := range strings {
    builder.WriteString(s)
}
result := builder.String()

// ✅ Or use strings.Join
result := strings.Join(strings, "")
```

### 6.5 Avoid interface{} conversion overhead

```go
// ❌ Use interface{} in hot path
func process(data interface{}) {
    switch v := data.(type) { // Type assertion has overhead
    case int:
        // ...
    }
}

// ✅ Use generic or concrete types in hot paths
func process[T int | int64 | float64](data T) {
// Type determined at compile time, no runtime overhead
}
```

---

## 7. Test

### 7.1 Table-driven testing

```go
// ✅ Recommended: table-driven testing
func TestAdd(t *testing.T) {
    tests := []struct {
        name     string
        a, b     int
        expected int
    }{
        {"positive numbers", 1, 2, 3},
        {"with zero", 0, 5, 5},
        {"negative numbers", -1, -2, -3},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            result := Add(tt.a, tt.b)
            if result != tt.expected {
                t.Errorf("Add(%d, %d) = %d; want %d",
                    tt.a, tt.b, result, tt.expected)
            }
        })
    }
}
```

### 7.2 Parallel testing

```go
// ✅ Recommendation: parallel execution of independent test cases
func TestParallel(t *testing.T) {
    tests := []struct {
        name  string
        input string
    }{
        {"test1", "input1"},
        {"test2", "input2"},
    }

    for _, tt := range tests {
tt := tt // Go < 1.22 needs to be copied
        t.Run(tt.name, func(t *testing.T) {
t.Parallel() // Mark as parallelizable
            result := Process(tt.input)
            // assertions...
        })
    }
}
```

### 7.3 Mock using interfaces

```go
// ✅ Define interface for testing
type EmailSender interface {
    Send(to, subject, body string) error
}

//Production implementation
type SMTPSender struct { /* ... */ }

// Test Mock
type MockEmailSender struct {
    SendFunc func(to, subject, body string) error
}

func (m *MockEmailSender) Send(to, subject, body string) error {
    return m.SendFunc(to, subject, body)
}

func TestUserRegistration(t *testing.T) {
    mock := &MockEmailSender{
        SendFunc: func(to, subject, body string) error {
            if to != "test@example.com" {
                t.Errorf("unexpected recipient: %s", to)
            }
            return nil
        },
    }

    service := NewUserService(mock)
    // test...
}
```

### 7.4 Testing auxiliary functions

```go
// ✅ Use t.Helper() to mark helper functions
func assertEqual(t *testing.T, got, want interface{}) {
t.Helper() // Display the caller's location when reporting errors
    if got != want {
        t.Errorf("got %v, want %v", got, want)
    }
}

// ✅ Use t.Cleanup() to clean up resources
func TestWithTempFile(t *testing.T) {
    f, err := os.CreateTemp("", "test")
    if err != nil {
        t.Fatal(err)
    }
    t.Cleanup(func() {
        os.Remove(f.Name())
    })
    // test...
}
```

---

## 8. Common pitfalls

### 8.1 Nil Slice vs Empty Slice

```go
var nilSlice []int     // nil, len=0, cap=0
emptySlice := []int{}  // not nil, len=0, cap=0
made := make([]int, 0) // not nil, len=0, cap=0

// ✅ JSON encoding differences
json.Marshal(nilSlice)   // null
json.Marshal(emptySlice) // []

// ✅ Recommendation: Explicit initialization when an empty array JSON is required
if slice == nil {
    slice = []int{}
}
```

### 8.2 Map initialization

```go
// ❌ Error: uninitialized map
var m map[string]int
m["key"] = 1 // panic: assignment to entry in nil map

// ✅ Correct: use make to initialize
m := make(map[string]int)
m["key"] = 1

### 8.3 Defer in a loop
m := map[string]int{}
```

### 8.3 Defer in a loop

```go
// ❌ Potential problem: defer is not executed until the end of the function
func processFiles(files []string) error {
    for _, file := range files {
        f, err := os.Open(file)
        if err != nil {
            return err
        }
// ✅ Correct: use closures or extraction functions
        // process...
    }
    return nil
}

// ✅ Correct: use closures or extraction functions
func processFiles(files []string) error {
    for _, file := range files {
        if err := processFile(file); err != nil {
            return err
        }
    }
    return nil
}

func processFile(file string) error {
    f, err := os.Open(file)
    if err != nil {
        return err
    }
    defer f.Close()
    // process...
    return nil
}
```

### 8.4 Slice underlying array sharing

```go
// ❌ Potential problem: slices share the underlying array
original := []int{1, 2, 3, 4, 5}
slice := original[1:3] // [2, 3]
slice[0] = 100 // original modified!
// original becomes [1, 100, 3, 4, 5]

// ✅ Correct: Explicit copy when independent copy is required
slice := make([]int, 2)
copy(slice, original[1:3])
### 8.5 String substring memory leak
```

### 8.5 String substring memory leak

```go
// ❌ Potential problem: substring holds the entire underlying array
func getPrefix(s string) string {
return s[:10] // still refers to the entire underlying array of s
}

// ✅ Correct: Create independent copy (Go 1.18+)
func getPrefix(s string) string {
    return strings.Clone(s[:10])
}

// ✅ Before Go 1.18
func getPrefix(s string) string {
    return string([]byte(s[:10]))
}
```

### 8.6 Interface Nil Trap

```go
// ❌ Trap: nil judgment of interface
type MyError struct{}
func (e *MyError) Error() string { return "error" }

func returnsError() error {
    var e *MyError = nil
return e // The error returned is not nil!
}

func main() {
    err := returnsError()
    if err != nil { // true! interface{type: *MyError, value: nil}
        fmt.Println("error:", err)
    }
}

// ✅ Correct: explicitly return nil
func returnsError() error {
    var e *MyError = nil
    if e == nil {
return nil // Explicitly return nil
    }
    return e
}
```

### 8.7 Time comparison

```go
// ❌ Not recommended: use == directly to compare time.Time
if t1 == t2 { // May fail due to monotonic clock differences
    // ...
}

// ✅ Recommendation: Use the Equal method
if t1.Equal(t2) {
    // ...
}

## 9. Code organization
if t1.Before(t2) || t1.After(t2) {
    // ...
}
```

---

## 9. Code organization

// ❌ Not recommended

```go
// ❌ Not recommended
package common // too broad
package utils // too broad
package helpers // too broad
package models // group by type

// ✅ Recommendation: Name according to function
package user // User related functions
package order // Order related functions
package postgres // PostgreSQL implementation
```

### 9.2 Avoid circular dependencies

```go
// ❌ Circular dependency
// package a imports package b
// package b imports package a

// ✅ Solution 2: Use interface decoupling
// package types (shared types)
// package a imports types
// package b imports types

// package a defines the interface
// package a defines the interface
// package b implements the interface
```

### 9.3 Export identifier specification

```go
func (s *UserService) validate(u *User) error // private
type UserService struct {
db *sql.DB // private
}

func (s *UserService) GetUser(id int) (*User, error) // public
func (s *UserService) validate(u *User) error // private

// ✅ Internal package restricted access
// internal/database/... can only be imported by the same project code
```

---

## 10. Tools and Checks

### 10.1 Must-use tools

```bash
# Format (required)
gofmt -w .
goimports -w .

# Static analysis
go vet ./...

# Escape analysis
go test -race ./...

# Escape analysis
go build -gcflags '-m -m' ./...
```

### 10.2 Recommended Linter

```bash
# golangci-lint (integrate multiple linters)
golangci-lint run

# Commonly used check items
# - errcheck: Check for unhandled errors
# - gosec: security check
# - ineffassign: invalid assignment
# - staticcheck: static analysis
# - unused: unused code
```

### 10.3 Benchmark test

```go
// ✅ Performance Benchmarks
func BenchmarkProcess(b *testing.B) {
    data := prepareData()
b.ResetTimer() //Reset timer

    for i := 0; i < b.N; i++ {
        Process(data)
    }
}

// run benchmark
// go test -bench=. -benchmem ./...
```

---

## Reference resources

- [Effective Go](https://go.dev/doc/effective_go)
- [Go Code Review Comments](https://go.dev/wiki/CodeReviewComments)
- [Go Common Mistakes](https://go.dev/wiki/CommonMistakes)
- [100 Go Mistakes](https://100go.co/)
- [Go Proverbs](https://go-proverbs.github.io/)
- [Uber Go Style Guide](https://github.com/uber-go/guide/blob/master/style.md)

# Java Code Review Guide

## Table of contents

- [Java Code Review Guide](#java-code-review-guide)
  - [Table of contents](#table-of-contents)
  - [Modern Java Features (17/21+)](#modern-java-features-1721)
    - [Record (record class)](#record-record-class)
    - [Switch expression and pattern matching](#switch-expression-and-pattern-matching)
    - [Text Blocks](#text-blocks)
  - [Stream API \& Optional](#stream-api--optional)
    - [Avoid abusing Stream](#avoid-abusing-stream)
    - [Optional Correct usage](#optional-correct-usage)
  - [JPA and database performance](#jpa-and-database-performance)
    - [Transaction Management](#transaction-management)
    - [Entity Design](#entity-design)
    - [Virtual threads (Java 21+)](#virtual-threads-java-21)
    - [Thread safety](#thread-safety)
  - [Lombok usage specifications](#lombok-usage-specifications)
  - [Exception handling](#exception-handling)
    - [Global exception handling](#global-exception-handling)
  - [Test specifications](#test-specifications)
    - [Unit testing vs integration testing](#unit-testing-vs-integration-testing)
  - [Review Checklist](#review-checklist)
    - [Basics and Specifications](#basics-and-specifications)
    - [Spring Boot](#spring-boot)
    - [Database \& Transactions](#database--transactions)
    - [Concurrency and performance](#concurrency-and-performance)
    - [Maintainability](#maintainability)

---

## Modern Java Features (17/21+)

### Record (record class)

```java
// ❌ Traditional POJO/DTO: lots of boilerplate code
public class UserDto {
    private final String name;
    private final int age;

    public UserDto(String name, int age) {
        this.name = name;
        this.age = age;
    }
    // getters, equals, hashCode, toString...
}

// ✅ Use Record: concise, immutable, clear semantics
public record UserDto(String name, int age) {
// Compact constructor for verification
    public UserDto {
        if (age < 0) throw new IllegalArgumentException("Age cannot be negative");
    }
}
```

### Switch expression and pattern matching

```java
// ❌ Traditional Switch: easy to miss break, not only lengthy and error-prone
String type = "";
switch (obj) {
    case Integer i: // Java 16+
        type = String.format("int %d", i);
        break;
    case String s:
        type = String.format("string %s", s);
        break;
    default:
        type = "unknown";
}

// ✅ Switch expression: no penetration risk, forced return value
String type = switch (obj) {
    case Integer i -> "int %d".formatted(i);
    case String s  -> "string %s".formatted(s);
case null -> "null value"; // Java 21 handles null
    default        -> "unknown";
};
```

### Text Blocks

```java
// ❌ Concatenate SQL/JSON strings
String json = "{\n" +
              "  \"name\": \"Alice\",\n" +
              "  \"age\": 20\n" +
              "}";

// ✅ Use text blocks: what you see is what you get
String json = """
    {
      "name": "Alice",
      "age": 20
    }
    """;
```

---

## Stream API & Optional

### Avoid abusing Stream

```java
// ✅ Use for-each directly in simple scenarios
items.stream().forEach(item -> {
    process(item);
});

// ✅ Use for-each directly in simple scenarios
for (var item : items) {
    process(item);
}

// ❌ Extremely complex Stream chain
List<Dto> result = list.stream()
    .filter(...)
    .map(...)
    .peek(...)
    .sorted(...)
.collect(...); // Difficult to debug

// ✅ Split into meaningful steps
var filtered = list.stream().filter(...).toList();
// ...
```

### Optional Correct usage

```java
// ❌ Use Optional as a parameter or field (serialization problem, increase calling complexity)
public void process(Optional<String> name) { ... }
public class User {
private Optional<String> email; // Not recommended
}

// ✅ Optional is only used to return values
public Optional<User> findUser(String id) { ... }

// ❌ Now that Optional is used, still use isPresent() + get()
Optional<User> userOpt = findUser(id);
if (userOpt.isPresent()) {
    return userOpt.get().getName();
} else {
    return "Unknown";
}

// ✅ Use functional API
return findUser(id)
    .map(User::getName)
    .orElse("Unknown");
```

---

## JPA and database performance

// ❌ FetchType.EAGER or trigger lazy loading in a loop

```java
// ❌ FetchType.EAGER or trigger lazy loading in a loop
// Entity definition
@Entity
public class User {
@OneToMany(fetch = FetchType.EAGER) // Danger!
    private List<Order> orders;
}

//Business code
List<User> users = userRepo.findAll(); // 1 SQL
for (User user : users) {
// If it is Lazy, N SQLs will be triggered here
    System.out.println(user.getOrders().size());
}

// ✅ Use @EntityGraph or JOIN FETCH
@Query("SELECT u FROM User u JOIN FETCH u.orders")
List<User> findAllWithOrders();
```

### Transaction Management

```java
// ❌ Start transactions at the Controller layer (the database connection takes too long)
// ✅ Add @Transactional to the public method of the Service layer
@Transactional
private void saveInternal() { ... }

// ✅ Add @Transactional to the public method of the Service layer
// ✅ Read operations are explicitly marked readOnly = true (performance optimization)
@Service
public class UserService {
    @Transactional(readOnly = true)
    public User getUser(Long id) { ... }

    @Transactional
    public void createUser(UserDto dto) { ... }
}
```

### Entity Design

```java
// ❌ Use Lombok @Data in Entity
// The equals/hashCode generated by @Data contains all fields, which may trigger lazy loading and cause performance problems or exceptions.
@Entity
@Data
public class User { ... }

// ✅ Only use @Getter, @Setter
### Virtual threads (Java 21+)
@Entity
@Getter
@Setter
public class User {
    @Id
    private Long id;

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof User)) return false;
        return id != null && id.equals(((User) o).id);
    }

    @Override
    public int hashCode() {
        return getClass().hashCode();
    }
}
```

---

### Virtual threads (Java 21+)

```java
// ❌ Traditional thread pool handles a large number of I/O blocking tasks (resource exhaustion)
ExecutorService executor = Executors.newFixedThreadPool(100);

// ✅ Use virtual threads to handle I/O-intensive tasks (high throughput)
// Spring Boot 3.2+ enabled: spring.threads.virtual.enabled=true
ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor();

// In virtual threads, blocking operations (such as DB queries, HTTP requests) consume almost no OS thread resources
```

### Thread safety

```java
// ❌ HashMap may have an infinite loop or data loss in a multi-threaded environment
private static final SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd");

// ✅ Use DateTimeFormatter (Java 8+)
private static final DateTimeFormatter dtf = DateTimeFormatter.ofPattern("yyyy-MM-dd");

// ❌ HashMap may have an infinite loop or data loss in a multi-threaded environment
// ✅ Use ConcurrentHashMap
Map<String, String> cache = new ConcurrentHashMap<>();
```

---

## Lombok usage specifications

```java
// ❌ Abusing @Builder results in the inability to force verification of required fields
@Builder
public class Order {
private String id; // required
private String note; // optional
}
// Caller may miss id: Order.builder().note("hi").build();

// ✅ For key business objects, it is recommended to manually write the Builder or constructor to ensure invariants
// Or add verification logic (Lombok @Builder.Default, etc.) in the build() method
```

---

## Exception handling

### Global exception handling

```java
e.printStackTrace(); // Should not be used in production environments
try {
    userService.create(user);
} catch (Exception e) {
e.printStackTrace(); // Should not be used in production environments
// return null; // Swallow the exception, the upper layer does not know what happened
}

// ✅ Custom exception + @ControllerAdvice (Spring Boot 3 ProblemDetail)
public class UserNotFoundException extends RuntimeException { ... }

@RestControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler(UserNotFoundException.class)
    public ProblemDetail handleNotFound(UserNotFoundException e) {
        return ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND, e.getMessage());
    }
}
```

---

## Test specifications

### Unit testing vs integration testing

```java
@SpringBootTest // Start the entire Context, slow
@SpringBootTest // Start the entire Context, slow
public class UserServiceTest { ... }

// ✅ Unit testing uses Mockito
@ExtendWith(MockitoExtension.class)
class UserServiceTest {
    @Mock UserRepository repo;
    @InjectMocks UserService service;

    @Test
    void shouldCreateUser() { ... }
}

// ✅ Integration testing uses Testcontainers
@Testcontainers
@SpringBootTest
class UserRepositoryTest {
    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15");
    // ...
}
```

---

## Review Checklist

### Basics and Specifications
- [ ] Comply with Java 17/21 new features (Switch expressions, Records, text blocks)
- [ ] Avoid using obsolete classes (Date, Calendar, SimpleDateFormat)
- [ ] Are the Stream API or Collections methods preferred for collection operations?
- [ ] Configuration properties use @ConfigurationProperties

### Spring Boot
- [ ] Use constructor injection instead of @Autowired field injection
- [ ] Configuration properties use @ConfigurationProperties
- [ ] Controller has a single responsibility and business logic is transferred to Service
- [ ] Global exception handling uses @ControllerAdvice / ProblemDetail

### Database & Transactions
- [ ] The read operation transaction is marked `@Transactional(readOnly = true)`
- [ ] Check if N+1 query exists (EAGER fetch or loop call)
- [ ] Entity class does not use @Data and implements equals/hashCode correctly
- [ ] Whether the database index covers the query conditions

### Concurrency and performance
- [ ] Are virtual threads considered for I/O intensive tasks?
- [ ] Whether thread safety classes are used correctly (ConcurrentHashMap vs HashMap)
- [ ] Is the lock granularity reasonable? Avoid I/O operations inside locks

### Maintainability
- [ ] Key business logic has adequate unit testing
- [ ] Logging properly (use Slf4j, avoid System.out)
- [ ] Magic value extracted as constant or enumeration

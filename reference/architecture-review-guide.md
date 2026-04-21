# Architecture Review Guide

Architectural design review guide to help evaluate whether the code's architecture is reasonable and whether the design is appropriate.

## SOLID Principles Checklist

### S - Single Responsibility Principle (SRP)

- Do the methods in the class all serve the same purpose?
- Is there only one reason for this class/module to change?
- Do the methods in the class all serve the same purpose?
- If you want to describe this class to a non-technical person, can you explain it clearly in one sentence?

**Identifying Signs in Code Review:**
```
⚠️ The class name contains general words such as "And", "Manager", "Handler", and "Processor"
⚠️ A class exceeds 200-300 lines of code
⚠️ Different methods operate on completely different data
⚠️ Different methods operate on completely different data
```

**Review Questions:**
- "What is this class responsible for? Can it be split?"
- "If the requirements for X change, which methods need to be changed? What if the requirements for Y change?"

### O - Open-Closed Principle (OCP)

**Check Points:**
- Will existing code need to be modified when adding new functionality?
- Is it possible to add new behaviors through extension (inheritance, composition)?
- Are there lots of if/else or switch statements to handle different types?

⚠️ switch/if-else chain to handle different types
```
⚠️ switch/if-else chain to handle different types
⚠️ Adding new functions requires modifying the core class
⚠️ Type checks (instanceof, typeof) scattered throughout the code
```

**Review Questions:**
- "If I want to add a new X type, what files need to be modified?"
- "Will this switch statement grow as new types are added?"

### L - Liskov Substitution Principle (LSP)

**Check Points:**
- Can a subclass completely replace the parent class?
- Does the subclass change the expected behavior of the parent class method?
- Is there a subclass that throws an exception that is not declared by the parent class?

**Identifying Signs in Code Review:**
```
⚠️ Explicit type conversion (casting)
⚠️ Subclass method throws NotImplementedException
⚠️ The subclass method is empty or has only return
⚠️ Where base classes are used, specific types need to be checked
```

**Review Questions:**
- "If a parent class is replaced with a subclass, does the caller code need to be modified?"
- "Does the behavior of this method in the subclass comply with the contract of the parent class?"

### I - Interface Segregation Principle (ISP)

**Check Points:**
- Is the interface small and focused enough?
- Are implementing classes forced to implement methods they don't need?
- Does the client rely on methods it doesn't use?

**Identifying Signs in Code Review:**
```
⚠️Interface has more than 5-7 methods
⚠️ The implementation class has empty methods or throws NotImplementedException
⚠️ The interface name is too broad (IManager, IService)
⚠️ Different clients only use some methods of the interface
```

**Review Questions:**
- "Are all methods of this interface used by every implementing class?"
- "Can this large interface be split into smaller dedicated interfaces?"

### D - Dependency Inversion Principle (DIP)

**Check Points:**
- Do high-level modules rely on abstractions rather than concrete implementations?
- Should I use dependency injection instead of new objects directly?
- Are abstractions defined by higher-level modules rather than lower-level modules?

**Identifying Signs in Code Review:**
```
⚠️ High-level modules directly new the specific classes of low-level modules
⚠️ Import concrete implementation classes instead of interfaces/abstract classes
⚠️ Configuration and connection strings are hardcoded in the business logic
⚠️ Difficulty writing unit tests for a class
```

**Review Questions:**
- "Can the dependencies of this class be replaced by mocks during testing?"
## Architecture anti-pattern recognition

---

## Architecture anti-pattern recognition

### Fatal anti-pattern

| Anti-Patterns | Identifying Signals | Impact |
|--------|----------|------|
| **Big Ball of Mud** | Without clear module boundaries, any code may call any other code | Difficult to understand, modify, and test |
| **God Object** | A single class takes on too many responsibilities, knows too much and does too much | Highly coupled, difficult to reuse and test |
| **Spaghetti Code** | Confusing control flow, goto or deep nesting, making it difficult to trace the execution path | Difficult to understand and maintain |
| **Lava Flow** | Ancient code that no one dares to touch, lack of documentation and testing | Technical debt accumulation |

### Design anti-patterns

| Anti-Patterns | Recognizing Signs | Advice |
|--------|----------|------|
| **Golden Hammer** | Use the same technique/pattern for all problems | Choose the appropriate solution based on the problem |
| **Over-Engineering (Gas Factory)** | Solving simple problems with complex solutions and abusing design patterns | YAGNI principle, first simple and then complex |
### Review Questions
| **Copy-paste programming** | The same logic appears in multiple places | Extract public methods or modules |

### Review Questions

```markdown
🔴 [blocking] "This class has 2000 lines of code. It is recommended to split it into multiple dedicated classes"
🟡 [important] "This logic is repeated in 3 places. Consider extracting it as a public method?"
💡 [suggestion] "This switch statement can be replaced by strategy mode, which is easier to expand"
```

---

## Coupling and cohesion evaluation

### Coupling type (from best to worst)

| Type | Description | Example |
|------|------|------|
| **Message Coupling** ✅ | Pass data through parameters | `calculate(price, quantity)` |
| **Data Coupling** ✅ | Sharing simple data structures | `processOrder(orderDTO)` |
| **Imprint Coupling** ⚠️ | Share complex data structures but only use parts | Pass in the entire User object but only use name |
| **Public Coupling** ❌ | Shared global variables | Multiple modules can read and write the same global state |
| **Public Coupling** ❌ | Shared global variables | Multiple modules can read and write the same global state |
| **Content Coupling** ❌ | Directly access the internals of another module | Directly operate the private properties of another class |

### Cohesive types (from best to worst)

| Type | Description | Quality |
|------|------|------|
| **Functional Cohesion** | All elements accomplish a single task | ✅ Best |
| **Sequential Cohesion** | Output as input for next step | ✅ Good |
| **Time Cohesion** | Simultaneous Tasks | ⚠️ Poor |
| **Time Cohesion** | Simultaneous Tasks | ⚠️ Poor |
| **Logical Cohesion** | Logically related but functionally different | ❌ Poor |
| **accidental cohesion** | no apparent relationship | ❌ worst |

### Metric Reference

```yaml
Coupling indicator:
CBO (coupling between classes):
Good: < 5
Warning: 5-10
Danger: > 10

Description: How many external classes it depends on
Description: How many external classes it depends on
Good: < 7

Description: How many classes depend on it
Description: How many classes depend on it
A high value means: the modification has a large impact and needs to be stable

LCOM4 (lack of method cohesion):
LCOM4 (lack of method cohesion):
1: Single responsibility ✅
2-3: May need to be split ⚠️
>3: should be split ❌
```

### Review Questions

- "How many other modules does this module depend on? Can it be reduced?"
- "How many other places will be affected by modifying this class?"
- "Do the methods of this class all operate on the same data?"

---

## Layered Architecture Review

### Clean Architecture Hierarchy Check

```
┌─────────────────────────────────────┐
│ Frameworks & Drivers                │ ← Outermost layer: Web, DB, UI
├─────────────────────────────────────┤
│         Interface Adapters          │ ← Controllers、Gateways、Presenters
├─────────────────────────────────────┤
│          Application Layer          │ ← Use Cases、Application Services
├─────────────────────────────────────┤
│            Domain Layer             │ ← Entities、Domain Services
└─────────────────────────────────────┘
↑ The dependency direction can only be inward ↑
```

### Dependency rule checking

**Core rule: Source code dependencies can only point to inner layers**

```typescript
// ✅ Correct: Domain layer defines the interface, Infrastructure implements it
// domain/User.ts
import { MySQLConnection } from '../infrastructure/database';

// ✅ Correct: Domain layer defines the interface, Infrastructure implements it
// infrastructure/MySQLUserRepository.ts (implementation)
interface UserRepository {
  findById(id: string): Promise<User>;
}

// infrastructure/MySQLUserRepository.ts (implementation)
class MySQLUserRepository implements UserRepository {
  findById(id: string): Promise<User> { /* ... */ }
}
```

### Review Checklist

**Hierarchical boundary checking:**
- [ ] Does the Domain layer have external dependencies (database, HTTP, file system)?
- [ ] Does the Application layer directly operate the database or call external API?
- [ ] Does the Controller contain business logic?
- [ ] Is there a cross-layer call (UI calls Repository directly)?

**Separation of concerns check:**
- [ ] Is business logic separated from presentation logic?
- [ ] Is data access encapsulated in a dedicated layer?
- [ ] Is configuration and environment related code managed centrally?

### Review Questions

```markdown
🔴 [blocking] "Domain entity directly imports database connection, violating dependency rules"
🟡 [important] "Controller contains business calculation logic, it is recommended to move it to the Service layer"
💡 [suggestion] "Consider using dependency injection to decouple these components"
```

---

## Design pattern usage evaluation

### When to use design patterns

| Mode | Applicable Scenarios | Not Applicable Scenarios |
|------|----------|------------|
| **Factory** | Different types of objects need to be created, and the types are determined at runtime | There is only one type, or the type is fixed |
| **Strategy** | The algorithm needs to be switched at runtime, there are multiple interchangeable behaviors | There is only one algorithm, or the algorithm will not change |
| **Observer** | One-to-many dependency, multiple objects need to be notified of state changes | A simple direct call can meet the needs |
| **Singleton** | Do require globally unique instances, such as configuration management | Objects that can be passed via dependency injection |
| **Decorator** | Responsibilities need to be added dynamically to avoid inheritance explosion | Responsibilities are fixed, no dynamic combination is required |

### Warning signs of over-engineering

```
⚠️ Patternitis recognition signals:

1. Simple if/else is replaced by strategy pattern + factory + registry
2. Only one implemented interface
3. A layer of abstraction added for “what may be needed in the future”
4. The number of lines of code increases significantly due to pattern application
5. It takes a long time for new people to understand the code structure
```

### Review Principles

```markdown
✅ Correct usage mode:
- Fixed real scalability issues
- Code is easier to understand and test
- Adding new features becomes easier

❌ Excessive usage pattern:
- Adds unnecessary complexity
- Adds unnecessary complexity
- Violation of YAGNI principles
```

### Review Questions

- "What specific problem is solved using this pattern?"
- "What will happen to the code if this pattern is not used?"
- "Does the value this abstraction layer brings outweigh its complexity?"

---

## Scalability evaluation

**Function scalability:**

**Function scalability:**
- [ ] Does adding new features require modifying the core code?
- [ ] Are extension points (hooks, plugins, events) provided?
- [ ] Is the configuration externalized (configuration files, environment variables)?

**Data scalability:**
- [ ] Does the data model support new fields?
- [ ] Have you considered the scenario of data volume growth?
- [ ] Does the query have a suitable index?

- [ ] Is it possible to scale horizontally (adding more instances)?
- [ ] Is it possible to scale horizontally (adding more instances)?
- [ ] Are there state dependencies (session, local cache)?
### Extension point design check

### Extension point design check

```typescript
// ❌ Poor extension design: hard-code all behavior
class OrderService {
  private hooks: OrderHooks;

  async createOrder(order: Order) {
    await this.hooks.beforeCreate?.(order);
    const result = await this.save(order);
    await this.hooks.afterCreate?.(result);
    return result;
  }
}

// ❌ Poor extension design: hard-code all behavior
class OrderService {
  async createOrder(order: Order) {
await this.sendEmail(order); // Hardcoded
await this.updateInventory(order); // Hardcoded
await this.notifyWarehouse(order); // Hardcoded
    return await this.save(order);
  }
}
```

💡 [suggestion] "Is this design easily extensible if new payment methods need to be supported in the future?"

```markdown
💡 [suggestion] "Is this design easily extensible if new payment methods need to be supported in the future?"
🟡 [important] "The logic here is hardcoded, consider using configuration or strategy mode?"
## Code structure best practices
```

---

## Code structure best practices

### Directory Organization

**Organized by function/domain (recommended):**
```
src/
├── user/
│ ├── User.ts (entity)
│ ├── UserService.ts (Service)
**Organized by technical layer (not recommended):**
│   └── UserController.ts (API)
├── order/
│   ├── Order.ts
│   ├── OrderService.ts
│   └── ...
└── shared/
    ├── utils/
    └── types/
```

**Organized by technical layer (not recommended):**
```
src/
├── controllers/ ← Different fields mixed together
│   ├── UserController.ts
│   └── OrderController.ts
├── services/
├── repositories/
└── models/
```

### Naming convention check

| Type | Convention | Example |
|------|------|------|
| Class name | PascalCase, noun | `UserService`, `OrderRepository` |
| Method name | camelCase, verb | `createUser`, `findOrderById` |
| Interface name | I prefix or no prefix | `IUserService` or `UserService` |
| Constants | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| Private properties | underscore prefix or None | `_cache` or `#cache` |

### File Size Guidelines

```yaml
Recommended restrictions:
Single file: < 300 lines
Single function: < 50 lines
Single class: < 200 lines
Function parameters: < 4
Nesting depth: < 4 levels

When limit is exceeded:
- Consider splitting into smaller units
- Extract helper functions or classes
- Extract helper functions or classes
```

### Review Questions

```markdown
🟢 [nit] "This 500-line file can be split according to responsibilities"
🟡 [important] "It is recommended to organize the directory structure by functional areas rather than technical layers"
💡 [suggestion] "The function name `process` is not clear enough. Consider changing it to `calculateOrderTotal`?"
```

---

## Quick Reference Checklist

### Architecture Review 5 Minute Quick Check

```markdown
□ Is the dependency direction correct? (The outer layer depends on the inner layer)
□ Are there circular dependencies?
□ Are there obvious anti-patterns?
□ Are SOLID principles followed?
□ Are there obvious anti-patterns?
```

### Red flag signal (must be handled)

```markdown
🔴 God Object - a single class exceeds 1000 lines
🔴 Circular dependency - A → B → C → A
🔴 Domain layer contains framework dependencies
🔴 External service call without interface
🔴 External service call without interface
```

### Yellow flag signal (recommended to handle)

```markdown
🟡 Class Coupling (CBO) > 10
🟡 Method parameters exceed 5
🟡 Nesting depth exceeds 4 levels
🟡 Repeat code block > 10 lines
🟡 There is only one implemented interface
```

---

## Tool recommendation

| Tools | Purpose | Language Support |
|------|------|----------|
| **SonarQube** | Code quality, coupling analysis | Multi-language |
| **NDepend** | Dependency analysis, architectural rules | .NET |
| **JDepend** | Package dependency analysis | Java |
| **Madge** | Module dependency graph | JavaScript/TypeScript |
| **ESLint** | Code specification, complexity check | JavaScript/TypeScript |
| **CodeScene** | Technical debt, hot spot analysis | Multi-language |

---

## Reference resources

- [Clean Architecture - Uncle Bob](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [SOLID Principles in Code Review - JetBrains](https://blog.jetbrains.com/upsource/2015/08/31/what-to-look-for-in-a-code-review-solid-principles-2/)
- [Software Architecture Anti-Patterns](https://medium.com/@christophnissle/anti-patterns-in-software-architecture-3c8970c9c4f5)
- [Coupling and Cohesion in System Design](https://www.geeksforgeeks.org/system-design/coupling-and-cohesion-in-system-design/)
- [Design Patterns - Refactoring Guru](https://refactoring.guru/design-patterns)

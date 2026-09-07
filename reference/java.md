# Java Review Guide

Inspect the JDK runtime, compiler `--release`/toolchain, Maven or Gradle configuration, Spring/Boot version, and deployment baseline. Do not equate a local JDK upgrade with application compatibility.

## Language and API contracts

- Records have final component fields, but referenced collections can still be mutable. Check defensive copies where immutability is part of the contract.
- Pattern matching for `instanceof` became final in Java 16; pattern matching for `switch` became final in Java 21. Distinguish final and preview features and confirm build/runtime flags.
- Verify null handling in switches and exhaustiveness across sealed hierarchies.
- `Stream.toList()` produces an unmodifiable list. Check downstream mutation when replacing collection code.
- `Optional.orElse` evaluates its argument eagerly; use lazy fallback when the work or side effects should happen only if absent.
- Streams, conventional loops, POJOs, records, and constructor injection are design choices; identify behavioral or contractual consequences before reporting a defect.

## Spring, persistence, and transactions

- In proxy-based Spring transaction management, self-invocation bypasses the proxy. Verify interception and method visibility for the actual proxy/framework version.
- Check rollback rules for checked exceptions and any configured overrides. `readOnly = true` is a hint, not authorization or a universal prohibition on writes.
- Trace transactions across async work, network calls, and retries. Check connection lifetime and partial-commit behavior.
- Inspect actual ORM queries for N+1 behavior. Fetch joins and entity graphs can affect row cardinality and pagination; a join may omit parents without matching children.
- Entity equality/hash codes must remain valid for proxies, transient objects, and generated IDs. Generated methods traversing relationships can recurse or load data unexpectedly.
- Validate inbound DTOs and authorization separately from persistence constraints. Global handlers should not leak internal errors.

See [Spring transaction semantics](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/annotations.html) for version-specific interception and rollback behavior.

## Threads and resource lifetime

- Virtual threads are final in Java 21+. They help blocking workloads but do not make CPU work faster or increase database pool capacity.
- Limit access to scarce downstream resources even when creating virtual threads cheaply.
- Monitor pinning guidance is version-sensitive: Java 24's JEP 491 removes pinning for most `synchronized` blocking. Do not apply an old blanket prohibition to newer JDKs. See [JEP 491](https://openjdk.org/jeps/491).
- Preserve interruption or propagate it appropriately when catching `InterruptedException`.
- Check executor shutdown, try-with-resources, thread-local lifetime, and shared mutable state.
- `ConcurrentHashMap` does not automatically make multi-step business operations atomic.

## Focused examples

### Records are only shallowly immutable (Java 16+)

The contract here is a snapshot of role names. These declarations can be placed in separate files or nested in a test class.

```java
import java.util.List;

// Bad: the caller can change the record's roles through its original list.
record RolesBad(List<String> values) {}

// Good: store an unmodifiable snapshot of the supplied role names.
record RolesGood(List<String> values) {
    RolesGood {
        values = List.copyOf(values);
    }
}
```

**Why:** construct either record with a mutable list, then append a role to the original list. The bad record changes; the good one does not. The good accessor also rejects list mutation. `List.copyOf` rejects null elements and does not deep-copy them; this example's strings are immutable. If nulls or shared mutation are part of the API contract, this correction would change that contract. See [List.copyOf](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/List.html).

### A transactional method bypassed by self-invocation

Assume Spring's default proxy-based transaction management, no transaction on the external caller, and two repository writes that must commit together. These are alternative versions of the same Spring-managed service; `LedgerRepository` supplies the application's two write methods.

```java
// Bad: an external call to transfer reaches writeBoth through "this",
// bypassing the proxy advice on writeBoth.
@Service
class TransferServiceBad {
    private final LedgerRepository ledger;

    TransferServiceBad(LedgerRepository ledger) { this.ledger = ledger; }

    public void transfer() { writeBoth(); }

    @Transactional
    public void writeBoth() {
        ledger.debit();
        ledger.credit();
    }
}

// Good: the externally invoked entrypoint establishes the transaction.
@Service
class TransferServiceGood {
    private final LedgerRepository ledger;

    TransferServiceGood(LedgerRepository ledger) { this.ledger = ledger; }

    @Transactional
    public void transfer() {
        ledger.debit();
        ledger.credit();
    }
}
```

Use Spring's `org.springframework.stereotype.Service` and `org.springframework.transaction.annotation.Transactional` imports.

**Why:** an external call through the good service's proxy wraps both writes in one transaction. Verify rollback by making the second write throw a runtime exception against the actual transactional store. An already-transactional caller or AspectJ weaving changes the analysis; self-invocation alone is not proof of a partial commit. Checked exceptions may require explicit rollback rules. See [Spring transaction semantics](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/annotations.html).

## Upgrades and validation

For Spring Boot 3-to-4 changes, check the modularized starters, Jackson migration, removed deprecated APIs, and test dependencies against the [Boot 4 migration guide](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide). Confirm the chosen minor version's [system requirements](https://docs.spring.io/spring-boot/system-requirements.html); do not require the same JDK as the latest feature release.

Check dependency compatibility, bytecode targets, annotation processors (including Lombok), serialization, and integration-test images. Match database tests to supported deployment versions rather than an arbitrary sample image.

Java 25 is an LTS baseline and Java 26 is a later feature release; deployment support and framework compatibility determine the appropriate target. See [Java releases](https://www.oracle.com/java/technologies/downloads/). Test the affected behavior with the existing unit and integration setup; full-context tests are appropriate when wiring or transactions are the subject.

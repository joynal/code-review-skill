# Security Review Guide

Trace untrusted input to a sensitive operation and identify the missing or bypassed control. Explain attacker prerequisites and impact; a checklist mismatch alone is not a vulnerability.

## Identity and access

- Distinguish authentication from authorization. Validate object ownership, tenant scope, roles/capabilities, and permission changes at each relevant entrypoint.
- Inspect background jobs, file downloads, batch endpoints, and Server Functions as well as normal HTTP handlers.
- Verify token signatures and intended algorithms/keys, issuer, audience, expiry, and session lifecycle. Decoding a JWT does not authenticate it.
- Check password reset token lifetime, single use, identity binding, and abuse controls.
- Confirm caches and data access preserve authorization boundaries.

See [OWASP authorization guidance](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html).

## Input-to-sink checks

- SQL: use driver parameters for values. Dynamic identifiers/order clauses need appropriate allowlists or safe driver composition.
- HTML: use contextual escaping for text and a maintained sanitizer when intentionally accepting HTML. React text escaping does not protect arbitrary HTML injection or every URL sink.
- Commands: separate executable and arguments without a shell where possible. Argument arrays prevent shell interpretation but do not prevent the target program interpreting attacker-supplied options.
- Files: normalize against a trusted root and check path-component containment, not a raw string prefix. Account for absolute paths, alternate separators, symlinks, and filesystem races. `basename` is not an access-control check.
- Network requests: validate destinations and protocols against the intended service boundary. Recheck redirects and resolved addresses where SSRF could reach internal services.
- Deserialization and uploads: verify format, size, extraction paths, executable content, and parser behavior. Do not deserialize untrusted executable formats.

Prefer established framework/platform controls over a small “safe path” or “sanitize input” snippet that omits its assumptions.

## Sessions and browser boundaries

- Check cookie flags and CSRF defenses according to the actual authentication mechanism and cross-site requests.
- CORS controls browser access to responses; it is not authorization or a general CSRF defense. A wildcard can be appropriate for intentionally public, non-credentialed resources.
- CSP and related headers should reflect the application's needs and supported middleware version. Do not copy deprecated header options as universal requirements.
- Bound costly operations and protect abuse-sensitive endpoints without assuming an identical rate limit fits every service.

## Secrets and cryptography

- Inspect changed configuration, logs, exceptions, URLs, telemetry, and client bundles for sensitive data exposure.
- Use established password hashing and cryptographic libraries, adequate randomness, and appropriate key storage.
- Verify key type and algorithm match; RSA signing needs an appropriate private key, not an arbitrary shared-secret string.
- Check failure paths for plaintext fallback, disabled verification, or overly broad access.
- Do not reproduce live credentials in findings; identify the location and type of exposure.

## Dependencies and supply chain

Check resolved versions, applicable advisories, deployment reachability, and existing mitigations. Distinguish a scanner alert from a confirmed exploitable path, while reporting known affected dependencies accurately.

Use configured audit tooling in report-only mode. Do not run `npm audit fix`, install replacements, or rewrite lockfiles during a review unless fixes were requested. A missing scanner or inaccessible advisory is a validation limit.

## Findings

Use the severity scheme in [SKILL.md](../SKILL.md), calibrated to demonstrated impact and prerequisites. Separate confirmed vulnerabilities from optional hardening. Provide the affected path and a focused mitigation without claiming that a code review proves the system secure.

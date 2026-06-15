---
name: security-hardening
description: Procedure for passing security validation before commit — no hardcoded secrets, no sensitive data in logs, vetted dependencies, and authorization checks on sensitive operations. Invoke when changing production code (agentic_core/, apps_*/, system_learning/), adding or updating a dependency, modifying logging, touching auth/authorization logic, or before committing any security-sensitive change.
metadata:
  enforcement_layer: deterministic
  enforcement_timing: before_work
  enforcement_type: invariant_check
---

# Security Hardening

This skill operationalizes `security-hardening.md`. All production code changes must pass security
validation before commit, with no bypass exceptions. The four checks below are enforced by
pre-commit hooks and CI gates; this skill is the human-readable procedure for satisfying them and
for knowing when an Author-Gate is required.

**Sibling skills:** Use `boundary-enforcement` for layer/import hygiene, `ask-user-question-recommendation` for the Author-Gate prompt shape.
This skill is specifically about *secrets, logs, dependencies, and authorization*.

## When to Invoke

| User intent / trigger | Action |
|---|---|
| Editing production code (`agentic_core/`, `apps_*/`, `system_learning/`) or config | Run the four mandatory checks before commit |
| Adding / updating a dependency | Scan with `pip-audit`/`safety`; document the assessment; Author-Gate (Category A) |
| Adding or changing logging | Verify no secrets/PII/tokens/connection-strings in output; mask sensitive values |
| Changing auth/authorization logic | Author-Gate before the change; verify permission checks on sensitive ops |

## Hard Routing Rules (do not violate)

| Rule | Why |
|---|---|
| No hardcoded passwords/API keys/tokens/credentials/private keys in production | `check_secrets_scan.py` (T20) blocks the commit |
| No secrets/PII in log output — mask as `***`/`[REDACTED]` | `check_sensitive_logs.py`; static review required for logging changes |
| New external dependency requires a CVE scan + Author-Gate | `dependency_security_scan.py` blocks high/critical CVEs (`approval-exception-policy.md` Category A) |
| Sensitive operations require authorization checks | `check_authorization.py`; agent deletion / config / DB / FS writes gated |
| No `--no-verify` bypass for production-code anti-patterns | `security-hardening.md` — "No bypass exceptions" |

## Standard Procedure

1. **Classify the change** — does it touch production code, config, dependencies, logging, or auth? If none, the gates are advisory.
2. **Scan for secrets** — confirm only `os.environ.get(...)` / config refs, never literal credentials; test placeholders (`"test_api_key"`) and clearly-marked `"YOUR_KEY_HERE"` docs are allowed.
3. **Audit logs** — every new log line: no API keys, tokens, PII, financial data, session tokens, or connection strings; mask anything sensitive.
4. **Vet dependencies** — for any new package run `pip-audit`/`safety`, record the assessment, and raise an Author-Gate (Category A) before adding.
5. **Verify authorization** — sensitive ops (agent deletion, config/governance change, DB/schema, FS writes) carry explicit permission checks; raise the Author-Gate for auth-logic changes.

## Forbidden Patterns

- ❌ Committing a hardcoded secret "temporarily" (blocked; never permitted).
- ❌ Logging a token/PII unmasked because "it's just debug output".
- ❌ Adding a dependency without a CVE scan or Author-Gate approval.
- ❌ `git commit --no-verify` to bypass a production-code security anti-pattern.
- ❌ Changing authentication/authorization logic without Author-Gate review.

## References

- Rule: `.claude/rules/security-hardening.md`
- Policy: `.claude/rules/approval-exception-policy.md` (Category A/B/C)
- Gates: `ops_scripts/ci/check_secrets_scan.py`, `check_sensitive_logs.py`, `dependency_security_scan.py`, `check_authorization.py`, `run_contract_gates.py`
- Sibling skills: `boundary-enforcement`, `ask-user-question-recommendation`
- Author-Gate prompt: native `AskUserQuestion` (CLAUDE.md § Author-Gate)

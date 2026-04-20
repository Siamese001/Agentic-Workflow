---
trigger: model_decision
description: Use this rule when handling credentials, environment variables, secrets, API keys, or any code path that touches external service authentication.
---

> **Claude always-on discipline:** Keep this file lean and invariant-focused. Put durable boundaries, routing cues, and non-negotiable standards here. Move long procedures, examples, templates, and execution playbooks into skills or workflows.
>
> **Claude retrieval discipline:** When this rule affects research or synthesis, prefer local-first retrieval, exact or structural matches before broad semantic search, and evidence or quote extraction before final synthesis on high-risk tasks.
>
> **Claude enforcement split:** Advisory guidance lives here, but deterministic blocking, fail-closed checks, and audit capture belong in hooks and scripts rather than prompt prose.

# Security Hardening Rule

## Constitutional Rule

**All code changes MUST pass security validation before commit.**

## Scope

This rule applies to:
- All production code changes (`agentic_core/`, `apps_*/`, `system_learning/`)
- Configuration files
- Dependency additions or updates

## Mandatory Security Checks

### 1. No Hardcoded Secrets

**FORBIDDEN patterns in production code:**
- Hardcoded passwords, API keys, tokens, or credentials
- Hardcoded database connection strings with credentials
- Hardcoded private keys or certificates
- Secrets in environment variable assignments

**Allowed patterns:**
- References to environment variables: `os.environ.get("API_KEY")`
- References to config files: `config.get_api_key()`
- Placeholder values in tests: `"test_api_key"` or `"dummy_secret"`
- Documentation examples with clear `"YOUR_KEY_HERE"` markers

**CI Enforcement:**
- Pre-commit hook: `security-secrets-scan` (T20)
- Gate: `ops_scripts/ci/check_secrets_scan.py`

### 2. No Sensitive Data in Logs

**FORBIDDEN in log output:**
- API keys, tokens, passwords
- Personal identifiable information (PII)
- Credit card numbers or financial data
- Session tokens or cookies
- Database connection strings with credentials

**Required:**
- Mask sensitive values: `"API_KEY: ***"` or `"password: [REDACTED]"`
- Log only non-sensitive identifiers: user_id, request_id

**CI Enforcement:**
- Static analysis: `ops_scripts/ci/check_sensitive_logs.py`
- Manual review required for logging changes

### 3. Dependency Security

**Required before adding dependencies:**
- Scan package for known vulnerabilities: `pip-audit` or `safety`
- Check package maintainability score
- Verify package is actively maintained
- Document security assessment in PR

**CI Enforcement:**
- Gate: `ops_scripts/ci/dependency_security_scan.py`
- Blocks commits with high/critical CVE vulnerabilities

### 4. Authorization Checks

**Required for sensitive operations:**
- Agent deletion: `/agent-deletion-gate` workflow
- Config changes: MCP config SSOT validation
- Database operations: Permission checks
- File system writes: Path validation and authorization

**CI Enforcement:**
- Pre-commit hook: `guard-agent-deletion` (T15)
- Gate: `ops_scripts/ci/check_authorization.py`

## Failure Modes

| Check | Failure Action |
|-------|----------------|
| Hardcoded secrets detected | Block commit, require remediation |
| Sensitive data in logs | Block commit, require masking |
| Vulnerable dependencies | Block commit, require upgrade or justification |
| Missing authorization | Block commit, require HITL approval |

## Security Review Triggers

HITL approval required for:
- Adding new external dependencies
- Changing authentication/authorization logic
- Modifying security-related configuration
- Implementing new logging for sensitive data
- Database schema changes affecting security

## Enforcement

All security checks are enforced via:
- Pre-commit hooks (`.pre-commit-config.yaml`)
- CI gates (`python ops_scripts/ci/run_contract_gates.py`)
- Manual review for security-sensitive changes

**No bypass exceptions.** Security violations must be fixed before commit.

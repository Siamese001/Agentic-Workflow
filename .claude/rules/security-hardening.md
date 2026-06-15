# Security Hardening — stub

> On-demand when changing prod code / deps / logging (plan `always-on-rule-surface-cut-c7f3a1`); enforcement unchanged. No hardcoded secrets; no PII/secrets in logs (mask); CVE-scan new deps (Author-Gate); authz checks on sensitive ops (agent deletion, config/DB/schema). Detail: [`security-hardening`](../skills/security-hardening/SKILL.md) skill. Enforced: `check_secrets_scan.py` (T20), `check_sensitive_logs.py`, `dependency_security_scan.py`.

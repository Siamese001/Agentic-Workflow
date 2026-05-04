# apps_underwriting_ai — Threat Model

## Scope

`apps_underwriting_ai` ingests **externally-supplied documents** (JSON payloads, CSV exports, PDF underwriting packages) and produces risk-decision packets via a multi-engine pipeline. The document-parser boundary is the primary attack surface.

## Assets

| Asset | Sensitivity | Integrity requirement |
|---|---|---|
| Applicant PII (name, DOB, SSN, income) | Critical | Must not leak across runs; must not persist beyond packet |
| Uploaded documents (PDF/CSV/JSON) | High | Provenance (source, hash, timestamp) preserved in packet |
| Risk decision packet | Critical | Must be reproducible; must cite every input used |
| Decision-router policy tables | High | Versioned with code; tamper-evident |

## Threat actors

1. **Malicious applicant** — submits crafted documents designed to exploit parsers
2. **Compromised upstream doc source** — document-management system returns attacker-modified files
3. **Prompt injection via extracted text** — PDF/CSV fields contain jailbreak payloads
4. **Insider** — engineer with access to decision tables

## Threats and mitigations

### T1 — Malicious PDF / document parsing exploit

- **Mitigation**: `engines/parsers/` uses safe, library-scoped parsers (pypdf for text-only PDFs, stdlib `csv`, `json`). No shell-out, no macro execution, no embedded-script evaluation.
- **Residual risk**: Library vulnerabilities (e.g., pypdf CVEs) — mitigated by lockfile + dependency-update cadence.

### T2 — Prompt injection via extracted fields

- **Mitigation**: Every extracted field passes through `validators/` before reaching the decision-router. Injection-signature matcher flags/rejects suspicious content.
- **Residual risk**: Novel patterns — mitigated by rubric-based QA and the deterministic policy-table approach (HOP decisions are table-driven, not LLM-driven for core logic).

### T3 — PII leakage

- **Mitigation**: No applicant data persists in shared caches. Evidence packets are per-applicant with deterministic hashing. Log redaction for PII fields (SSN, DOB).
- **Residual risk**: Log aggregation may capture PII — addressed by log-redaction middleware.

### T4 — Policy-table tampering

- **Mitigation**: `validators/policy/` tables are version-controlled alongside code. CI enforces schema validation. Decision-router signatures every decision with table version.
- **Residual risk**: Insider modification — mitigated by code review + audit logs.

### T5 — SSRF via document URLs

- **Mitigation**: Documents are fetched via allow-listed storage backends only. No arbitrary URL fetch from document content.

### T6 — Decision drift

- **Mitigation**: Every decision packet records policy-table version, parser version, and input-document hashes. Decisions are auditable post-hoc.

## Trust boundaries

```
DOCUMENT ──[engines/parsers: safe-parse + size limits]──> EXTRACTED
                                                               ↓
                              [validators/]──> DECISION ROUTER ──> decision_packet_assembler ──> PACKET
```

## Non-goals

- Cryptographic verification of document authenticity (assumed via upstream channel)
- Protection against physical document-manipulation before ingestion
- Zero-trust for the decision-maker themselves

## References

- ADR-082 — folder taxonomy
- ADR-028 — publisher-boundary
- `TECHNICAL_SPEC.md`
- `config/cert_route_registry.yaml` — certified decision routes

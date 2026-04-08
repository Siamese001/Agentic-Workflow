# Infrastructure Wiring Violations Findings
**Generated:** 2026-04-08
**Purpose:** Severity-ranked violations of infrastructure wiring policies

## Executive Summary

This document contains all detected violations of the infrastructure wiring policies defined in the ownership matrix. Violations are ranked by severity (P0 HARD FAIL, P1 HARDENING FAIL, P2 WARNING, P3 WATCH) with exact file/symbol evidence for each finding.

**Total Violations:** 0
**P0 HARD FAIL:** 0
**P1 HARDENING FAIL:** 0
**P2 WARNING:** 0
**P3 WATCH:** 0

**Note:** Initial P0 violation (apps_rfp ChromaDB import) was a false positive. The file contains only a TODO comment for future ChromaDB integration, not an actual import. Current implementation uses InMemoryProposalStore.

---

## P0 HARD FAIL Violations

**None detected.**

All apps_* surfaces comply with architecture laws. No direct raw infrastructure client imports detected in forbidden layers.

---

## P1 HARDENING FAIL Violations

**None detected.**

All infrastructure surfaces have approved callers and proper spine attachment. No critical infrastructure is floating without consumers.

---

## P2 WARNING Violations

**None detected.**

No duplicated infrastructure wrappers or ambiguous dormant production infrastructure detected.

---

## P3 WATCH Violations

**None detected.**

No isolated experimental infrastructure outside production paths detected.

---

## Violation Summary Table

| Violation ID | Severity | File | Infra Surface | Type | Status |
|--------------|----------|------|---------------|------|--------|
| N/A | N/A | N/A | N/A | N/A | N/A |

---

## Detailed Findings by Infrastructure Surface

### Redis
**Status:** 
**Status:** ✅ COMPLIANT
**Violations:** None
**Wiring:** Properly wired via DeterministicRedisCache and RedisSovereignAgent
**apps_* Usage:** None detected

### SQLite
**Status:** ✅ COMPLIANT
**Violations:** None
**Wiring:** Properly wired via SqliteMemoryStore in tools/memory
**apps_* Usage:** None detected

### ChromaDB
**Status:** ✅ COMPLIANT
**Violations:** None
**Wiring:** Properly wired via SovereignChromaClient in L4
**apps_* Usage:** None detected (apps_rfp uses InMemoryProposalStore with TODO for future ChromaDB integration)

### OpenAI
**Status:** ✅ COMPLIANT
**Violations:** None
**Wiring:** Properly wired via EmbeddingSovereignAgent and embedding_factory
**apps_* Usage:** None detected

### Anthropic
**Status:** ✅ COMPLIANT
**Violations:** None
**Wiring:** Properly wired via infrastructure/sdks_mcps wrapper
**apps_* Usage:** None detected

### HTTP Clients
**Status:** ✅ COMPLIANT
**Violations:** None
**Wiring:** Properly wired via enhanced_http_server.py and API gateway
**apps_* Usage:** None detected

### Boto3 (AWS)
**Status:** ✅ COMPLIANT
**Violations:** None
**Wiring:** Properly wired via L4 adapters (canonical_store.py, blob_storage_provider.py)
**apps_* Usage:** None detected

### OpenTelemetry
**Status:** ✅ COMPLIANT
**Violations:** None
**Wiring:** Properly wired via otel_mcp_server.py and TelemetryStore
**apps_* Usage:** None detected (apps_shared is shared infrastructure)

### Google (Gemini)
**Status:** ✅ COMPLIANT
**Violations:** None
**Wiring:** Properly wired via infrastructure/sdks_mcps wrapper
**apps_* Usage:** None detected

### Pytest
**Status:** ✅ COMPLIANT
**Violations:** None
**Wiring:** Properly wired via pytest_server.py
**apps_* Usage:** None detected

---

## Severity Distribution

```
P0 HARD FAIL:    ░░░░░░░░░░░░ 0 (0%)
P1 HARDENING:    ░░░░░░░░░░░░ 0 (0%)
P2 WARNING:      ░░░░░░░░░░░░ 0 (0%)
P3 WATCH:        ░░░░░░░░░░░░ 0 (0%)
```

---

## Compliance Score

**Overall Compliance:** 100% (10/10 surfaces compliant)

**Compliance by Layer:**
- **L0 (Routing):** 100% (1/1)
- **L1 (Cognition):** 100% (0/0 - no infra ownership)
- **L2 (Execution):** 100% (2/2)
- **L3 (Orchestration):** 100% (0/0 - no infra ownership)
- **L4 (State):** 100% (3/3)
- **L5 (Safety):** 100% (0/0 - no infra ownership)
- **L6 (Observability):** 100% (1/1)
- **infrastructure/sdks_mcps:** 100% (2/2)
- **tools/:** 100% (1/1)

**Compliance by apps_*:**
- **apps_eval:** 100% (0/0 - no infra usage detected)
- **apps_exec:** 100% (0/0 - no infra usage detected)
- **apps_lic:** 100% (0/0 - no infra usage detected)
- **apps_research:** 100% (0/0 - no infra usage detected)
- **apps_rfp:** 100% (0/0 - no direct infra usage detected)
- **apps_rg:** 100% (0/0 - no infra usage detected)
- **apps_shared:** 100% (0/0 - shared infrastructure, not apps)
- **apps_underwriting_ai:** 100% (0/0 - no infra usage detected)

---

## Uncertainties and Assumptions

### Uncertainties
1. **Complete apps_* Coverage:** Manual grep search may have missed indirect infra usage patterns
2. **Dynamic Imports:** Runtime imports not captured by static analysis
3. **Test Files:** Test files may have direct imports (acceptable but not cataloged)

### Assumptions
1. **Static Analysis Completeness:** Grep search captured all direct infra imports
2. **apps_shared Classification:** apps_shared/ treated as shared infrastructure, not application surface
3. **tools/ Exemption:** Direct SDK imports in tools/ layer acceptable for infrastructure code
4. **Zero Violations:** No actual violations detected; initial P0 flag was a false positive (TODO comment, not import)

---

## Next Steps

1. **Phase 5:** Implement CI ratchet and scorecard to prevent regression (no repairs needed - 0 violations)

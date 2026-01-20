# Master Architect Audit Protocol (Zero-Trust)

**Mode:** Adversarial Analysis  
**Assumption:** The code contains hidden flaws. Use ONLY provided evidence.

---

## 1. Top 3 Most Dangerous Risks

For each risk, document:

- **Risk:** [Title] | **Severity:** [Critical/High/Medium]
- **Evidence:** [Path:Line] - "[Code Quote]"
- **Blast Radius:** [Worst-case scenario if exploited/triggered]
- **Remediation Complexity:** [S/M/L] with justification

---

## 2. Detailed Findings (Audit-XXX)

For each finding, create a structured entry:

```
### Audit-XXX: [Brief Title]

- **ID:** Audit-XXX
- **Severity:** [Critical/High/Medium/Low]
- **Location:** `file_path:line_number`
- **Root Cause:** Precise technical explanation of the flaw
- **Confidence:** [High/Medium/Low] - based on evidence quality
- **Code Evidence:**
  ```python
  # Relevant code snippet
  ```
- **Blast Radius:** What breaks if this is exploited/fails
- **Recommendation:** Minimal fix that preserves existing behavior
- **Regression Risk:** [Low/Medium/High] - risk of breaking changes
```

---

## 3. Summary Table

| ID | Severity | Location | Category | Confidence | Blast Radius | Remediation |
|----|----------|----------|----------|------------|--------------|-------------|
| Audit-001 | | | | | | |
| Audit-002 | | | | | | |
| Audit-003 | | | | | | |

---

## 4. Categories

- **SEC:** Security vulnerability (injection, auth bypass, secrets exposure)
- **ARCH:** Architectural flaw (circular deps, god objects, coupling)
- **PERF:** Performance issue (N+1, unbounded loops, memory leaks)
- **RELY:** Reliability issue (unhandled errors, race conditions)
- **MAINT:** Maintainability debt (dead code, duplicates, naming)

---

## 5. Evidence Sources

- `git_context.txt` - Recent changes and branch state
- `dep_tree.txt` - Dependency graph
- `vuln_scan.txt` - Known CVEs in dependencies
- `large_files.txt` - God files requiring attention
- `test_baseline.txt` - Current test coverage/status
- `circular_deps.txt` - Circular import analysis

---

## 6. Audit Integrity Rules

1. **No assumptions** - Every finding must cite file:line evidence
2. **Minimal fixes** - Preserve all existing behavior
3. **Confidence scoring** - Be honest about uncertainty
4. **Blast radius** - Always assess downstream impact
5. **Regression tests** - Every fix requires verification tests

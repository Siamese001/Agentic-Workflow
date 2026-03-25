# Fail-Closed Discipline

**Protocol for handling AST parsing failures per §2.3.**

## When AST parsing or graph construction fails:

1. **Record** exact parse errors (file, error type, line number, message)
2. **Identify** all blocked files that could not be parsed
3. **Mark** all analysis conclusions as PARTIAL with completeness percentage
4. **Reduce** confidence level (100% = HIGH, 90-99% = MEDIUM, <90% = LOW)
5. **Report** limitations explicitly — never omit
6. **STOP** — do NOT claim confidence on incomplete graph
7. **Do NOT** silently fall back to grep/regex as substitute

## Parse Failure Types

SyntaxError, UnicodeDecodeError, ImportError, RecursionError, MemoryError, TimeoutError, ModuleNotFoundError.

## Prohibited vs Permitted Claims

When graph is incomplete:
- **PROHIBITED**: "All dependencies identified", "Complete blast radius", "No other files affected"
- **PERMITTED**: "Known dependencies include...", "Partial analysis shows...", "At least these files..."

## Enforcement Checklist

- [ ] Exact parse errors recorded
- [ ] Blocked files identified
- [ ] Analysis marked as PARTIAL
- [ ] Confidence level reduced
- [ ] Limitation notice in output
- [ ] NO silent fallback to grep/regex
- [ ] NO high-confidence claims
- [ ] Remediation path provided

## Constitutional References

- **§2.3:** Fail-closed discipline — silent fallback = HARD FAIL

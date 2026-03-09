# Fail-Closed Discipline

**Protocol for handling AST parsing failures per §3.6.**

## Constitutional Requirement

If AST parsing or graph construction fails, Windsurf MUST fail closed.

**FORBIDDEN:** Silent fallback from AST graph analysis to text search.

## Step 1: Detect Parse Failures

Monitor for these failure modes:

```
PARSE_FAILURE_TYPES:
- SyntaxError (invalid Python syntax)
- UnicodeDecodeError (encoding issues)
- ImportError (missing dependencies)
- RecursionError (deeply nested structures)
- MemoryError (extremely large files)
- TimeoutError (parsing takes too long)
- ModuleNotFoundError (missing imports)
```

## Step 2: Record Exact Parse Errors

Document every parse failure with full details:

```
PARSE_ERRORS:
File: path/to/problematic_file.py
Error type: SyntaxError
Error message: invalid syntax (<string>, line 42)
Line number: 42
Column: 15
Traceback: <full traceback>
Timestamp: <ISO timestamp>
Parser version: <version>
```

## Step 3: Identify Blocked Files

List all files that could not be parsed:

```
BLOCKED_FILES:
1. path/to/file1.py (SyntaxError at line 42)
2. path/to/file2.py (UnicodeDecodeError)
3. path/to/file3.py (ImportError: missing module X)

Total blocked: 3 files
Percentage of scope: 15%
```

## Step 4: Mark Conclusions as PARTIAL

Explicitly mark all analysis conclusions as incomplete:

```
ANALYSIS_STATUS: PARTIAL

COMPLETENESS:
- Total files in scope: 20
- Successfully parsed: 17
- Parse failures: 3
- Completeness: 85%

IMPACT ON CONCLUSIONS:
- Dependency graph is INCOMPLETE
- Upstream dependencies may be missing
- Downstream dependents may be missing
- Call edges may be incomplete
- Test coverage may be underreported

CONFIDENCE LEVEL: LOW
```

## Step 5: Stop Short of Claiming Confidence

Do NOT make high-confidence claims when graph is incomplete:

```
PROHIBITED CLAIMS (when graph is incomplete):
❌ "All dependencies identified"
❌ "Complete blast radius analysis"
❌ "No other files affected"
❌ "Test coverage is complete"
❌ "No boundary violations detected"

PERMITTED CLAIMS (when graph is incomplete):
✅ "Known dependencies include..."
✅ "Partial blast radius analysis shows..."
✅ "At least these files are affected..."
✅ "Test coverage includes at least..."
✅ "No boundary violations detected in parsed files"
```

## Step 6: Do NOT Fall Back to Grep/Regex

**HARD FAIL if silent fallback occurs:**

```
FORBIDDEN FALLBACK SEQUENCE:
1. AST parsing fails for file.py
2. Silently switch to grep/regex to find "imports" or "calls"
3. Proceed with analysis as if graph is complete

This is a CONSTITUTIONAL VIOLATION per §3.6.
```

**REQUIRED BEHAVIOR:**

```
CORRECT FAIL-CLOSED SEQUENCE:
1. AST parsing fails for file.py
2. Record exact parse error
3. Mark file as BLOCKED
4. Mark analysis as PARTIAL
5. Reduce confidence level
6. Report limitation explicitly
7. Do NOT claim completeness
8. Do NOT silently use grep/regex as substitute
```

## Step 7: Report Limitation Explicitly

Include explicit limitation notice in all outputs:

```
⚠️ GRAPH INCOMPLETENESS WARNING ⚠️

This analysis is based on an INCOMPLETE dependency graph due to parse failures.

Parse failures: 3 files
Blocked files: [list]
Completeness: 85%
Confidence: LOW

KNOWN LIMITATIONS:
- Dependency edges from blocked files are MISSING
- Call edges to/from blocked files are MISSING
- Test coverage for blocked files is UNKNOWN
- Boundary violations in blocked files are UNDETECTED

RECOMMENDATIONS:
1. Fix parse errors in blocked files
2. Rebuild dependency graph
3. Re-run analysis with complete graph
4. Do NOT proceed with high-risk changes until graph is complete
```

## Step 8: Offer Remediation Path

Provide actionable steps to fix parse failures:

```
REMEDIATION_STEPS:
For SyntaxError in file1.py:
  1. Run: python -m py_compile path/to/file1.py
  2. Fix syntax error at line 42
  3. Verify: python -m ast path/to/file1.py
  4. Rebuild graph

For UnicodeDecodeError in file2.py:
  1. Check file encoding: file path/to/file2.py
  2. Convert to UTF-8 if needed
  3. Add encoding declaration: # -*- coding: utf-8 -*-
  4. Rebuild graph

For ImportError in file3.py:
  1. Identify missing dependency
  2. Install dependency or fix import path
  3. Verify: python -c "import file3"
  4. Rebuild graph
```

## Enforcement Checklist

When parse failures occur:

- [ ] Exact parse errors recorded
- [ ] Blocked files identified
- [ ] Analysis marked as PARTIAL
- [ ] Confidence level reduced
- [ ] Limitation notice included in output
- [ ] NO silent fallback to grep/regex
- [ ] NO high-confidence claims made
- [ ] Remediation path provided
- [ ] User notified of incompleteness

## Example: Correct Fail-Closed Behavior

```
[DEPENDENCY GRAPH ANALYSIS - PARTIAL]

PARSE FAILURES DETECTED:
- agentic_core/L5_safety/validators/complex_validator.py
  Error: SyntaxError at line 156 (invalid syntax)

IMPACT:
- Dependency graph is INCOMPLETE
- Cannot determine full upstream dependencies of complex_validator.py
- Cannot determine full downstream dependents of complex_validator.py
- Test coverage for complex_validator.py is UNKNOWN

ANALYSIS STATUS: PARTIAL (95% completeness)
CONFIDENCE LEVEL: MEDIUM

KNOWN DEPENDENCIES (from successfully parsed files):
- file1.py imports common/utils.py ✅
- file2.py imports file1.py ✅
- file2.py imports complex_validator.py ⚠️ (BLOCKED - cannot analyze further)

RECOMMENDATIONS:
1. Fix SyntaxError in complex_validator.py
2. Rebuild dependency graph
3. Re-run impact analysis
4. Do NOT proceed with changes to complex_validator.py until parse error fixed

⚠️ This analysis is INCOMPLETE. Do NOT make high-confidence decisions based on partial graph.
```

## Constitutional References

- **§3.6:** If AST parsing fails, MUST fail closed
- **§3.6:** Do NOT fall back to grep/regex as silent substitute
- **§3.6:** Record exact parse/graph errors
- **§3.6:** Identify blocked files
- **§3.6:** Mark conclusions as partial
- **§3.6:** Stop short of claiming confidence

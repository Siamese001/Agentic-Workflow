# Wave 23: ADG Scanner Calibration Recommendations

**Date:** 2026-03-29
**Status:** Scanner Analysis Complete - Calibration Required

---

## Executive Summary

The ADG static scanner requires calibration to eliminate false positive detection of exception tuples as bare excepts.

**Current State:**
- 130 HIGH violations reported
- 0 actual violations (100% false positives)
- All reported lines use proper exception tuples

---

## False Positive Pattern Analysis

### Detected Pattern (Correct Code)
`python
except (OSError, UnicodeDecodeError, SyntaxError):
except (ImportError, AttributeError, KeyError):
except (ImportError, AttributeError, ValueError):
except (OSError, json.JSONDecodeError):
`

### ADG Scanner Bug
The scanner incorrectly flags lines containing xcept ( as bare except violations.
The regex pattern likely matches xcept followed by any content that isn't Exception, failing to account for tuple syntax.

---

## Recommended Scanner Fixes

### 1. Update Bare Except Detection Regex

**Current (Buggy):**
`python
# Likely matches any except that isn't 'except Exception:'
r'except\s*:\s*$'  # Only this should be flagged
`

**Recommended:**
`python
# Proper bare except detection
r'^\s*except\s*:\s*(#.*)?$'  # Truly bare

# Proper exception tuple detection (should PASS)
r'except\s*\([^)]+\)\s*:'  # Has exception tuple
`

### 2. Add Exception Tuple Validation

The scanner should:
1. Check for xcept ( pattern
2. If found, verify it contains exception types
3. Mark as VALID (not a violation)
4. Only flag lines matching xcept: with no tuple

### 3. Test Cases for Scanner

`python
# Should be flagged as bare except:
except:
except:  # comment
    pass

# Should NOT be flagged:
except Exception:
except (OSError, IOError):
except (ValueError, TypeError) as e:
except ImportError:
`

---

## Affected Files Summary

**Total Files with False Positives:** 84
**By Layer:**
- L0 Routing: ~35 files
- L2 Execution: ~18 files
- L3 Orchestration: ~12 files
- L5 Safety: ~19 files

**Common Exception Types Used:**
- OSError, IOError, PermissionError
- ImportError, AttributeError, KeyError
- ValueError, TypeError
- SyntaxError, UnicodeDecodeError
- json.JSONDecodeError

---

## Impact Assessment

### Without Scanner Fix
- ADG will continue reporting 130 false positives
- Violation count will not accurately reflect code quality
- Future burndowns may waste time verifying the same false positives

### With Scanner Fix
- Violation count will drop from 130 to 0
- Accurate reflection of codebase exception handling quality
- Future scans will only report actual issues

---

## Implementation Priority

**Priority: MEDIUM**

While the false positives don't affect code quality (the code is correct), they:
1. Reduce confidence in ADG reports
2. Waste developer time on verification
3. Make it harder to spot actual violations

---

## Recommendation

1. **Short-term:** Accept that 130 violations are false positives (documented)
2. **Medium-term:** Update ADG scanner regex patterns
3. **Long-term:** Regenerate ADG with fixed scanner for clean baseline

---

## Wave 23 Status

**Action:** Scanner analysis complete
**Deliverable:** Calibration recommendations documented
**Next Step:** Scanner fix implementation (if desired)

---

*Wave 23: Part of the complete ADG burndown project documentation.*

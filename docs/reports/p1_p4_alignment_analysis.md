# P1-P4 Definition Alignment - COMPLETE

**Date:** 2026-04-06  
**Status:** COMPLETED AND IMPLEMENTED

## Current Definitions

### 1. severity.py (SSOT - Canonical Definition)

**Location:** `agentic_core/L5_safety/config/severity.py`

**Definitions:**
- **CRITICAL (P0/P1):**
  - IMPACT: System-breaking, security breach, data loss, or constitutional violation
  - URGENCY: Immediate - MUST block commit until fixed
  - EXAMPLES: Layer boundary violations, security vulnerabilities, PowerShell usage, missing critical dependencies, broken imports in production code

- **HIGH (P1/P2):**
  - IMPACT: Bugs that affect functionality, architectural violations, anti-patterns
  - URGENCY: High - should fix before commit, degrades quality significantly
  - EXAMPLES: Unused imports, global mutations, test coverage gaps, deprecated APIs, silent exception swallowers, circular dependencies

- **MEDIUM (P2/P3):**
  - IMPACT: Code quality issues, maintainability concerns, style violations
  - URGENCY: Medium - consider fixing, technical debt accumulation
  - EXAMPLES: Long functions, complex cyclomatic complexity, inconsistent naming, missing docstrings, TODO comments without owners

- **LOW (P3/P4):**
  - IMPACT: Minor style issues, formatting, informational
  - URGENCY: Low - nice to have, can be deferred
  - EXAMPLES: Line length violations, trailing whitespace, missing type hints in utility code, unused variables in tests, debug print statements

**P-Level Mappings:**
- CRITICAL → P0/P1 (Ruff uses P0, ADG uses P1)
- HIGH → P1/P2
- MEDIUM → P2/P3
- LOW → P3/P4

### 2. generate_full_adg.py

**Location:** `tools/generate/generate_full_adg.py` (lines 115-122)

**Definitions:**
- **P1: critical (highest priority)** - Layer violations, critical repair routes
- **P2: high** - High severity repair routes, architectural issues
- **P3: medium** - Medium severity repair routes, code quality issues
- **P4: low (lowest priority)** - Low severity repair routes, semantic enrichment warnings

**Issues:**
- Only uses P1 for critical (not P0/P1)
- P4 includes "semantic enrichment warnings" which severity.py doesn't mention
- Descriptions are ADG-specific (repair routes) vs. severity.py's general definitions

### 3. .pre-commit-config.yaml

**Location:** `.pre-commit-config.yaml`

**Definitions:**
- **P0: Critical (Security/Safety/Runtime)** - BLOCKING
- **P1: High (Bug Patterns/Code Quality)**
- **P2: Medium (Style/Organization)** - WARNING
- **P3: Low (Formatting/Python3)** - INFO
- **P1 (ADG):** Critical - layer violations (in comment)

**Issues:**
- Uses P0 for critical (Ruff mapping)
- P1 is "High" but severity.py says HIGH = P1/P2 (ambiguous)
- Inconsistent with ADG's P1 = critical mapping

## Inconsistencies Identified

### 1. P-Level Mapping Ambiguity
**severity.py:** CRITICAL = P0/P1, HIGH = P1/P2, MEDIUM = P2/P3, LOW = P3/P4  
**generate_full_adg.py:** Uses P1, P2, P3, P4 (no P0)  
**.pre-commit-config.yaml:** Uses P0, P1, P2, P3 (no P4)

**Problem:** Each system uses a different P-level scheme, making cross-system comparison difficult.

### 2. Critical Level Definition
**severity.py:** CRITICAL = P0/P1 (acknowledges both Ruff P0 and ADG P1)  
**generate_full_adg.py:** Only uses P1 for critical  
**.pre-commit-config.yaml:** Uses P0 for critical (Ruff)

**Problem:** ADG doesn't acknowledge P0, creating ambiguity about whether P0 defects should block ADG generation.

### 3. P4 Semantic Warnings
**generate_full_adg.py:** P4 includes semantic enrichment warnings  
**severity.py:** P4 is just "Minor style issues, formatting, informational"  
**Problem:** severity.py doesn't account for semantic warnings in P4.

### 4. Description Alignment
**severity.py:** General definitions applicable to all systems  
**generate_full_adg.py:** ADG-specific definitions (repair routes)  
**Problem:** generate_full_adg.py doesn't reference the canonical SSOT definitions.

## Alignment Strategy

### Option 1: Align All to severity.py SSOT (RECOMMENDED)

**Changes Required:**

1. **Update generate_full_adg.py:**
   - Change comment to reference severity.py definitions
   - Add P0 acknowledgment in documentation
   - Clarify that semantic warnings are part of P4 (LOW)
   - Update descriptions to align with severity.py

2. **Update .pre-commit-config.yaml:**
   - Clarify that P0 = CRITICAL (Ruff-specific)
   - Clarify that ADG P1 = CRITICAL (not to be confused with Ruff P1 = HIGH)
   - Update comments to reference severity.py SSOT

3. **Update severity.py:**
   - Add note about semantic warnings being part of P4 (LOW)
   - Clarify the P0 vs P1 distinction for different systems

**Benefits:**
- Single source of truth maintained
- Clear cross-system mappings
- Reduced confusion

### Option 2: Create Separate ADG Severity Schema

**Changes Required:**

1. Create `config/adg_severity.yaml` with ADG-specific P1-P4 definitions
2. Update generate_full_adg.py to use YAML schema
3. Update severity.py to reference ADG schema for ADG-specific mappings

**Benefits:**
- ADG can have domain-specific definitions
- Clear separation of concerns

**Drawbacks:**
- Two sources of truth
- More maintenance overhead
- Potential for divergence

## Recommendation

**Adopt Option 1** - Align all systems to severity.py SSOT.

**Rationale:**
- severity.py is already designed as the canonical SSOT
- The P0/P1, P1/P2, P2/P3, P3/P4 ranges already acknowledge system differences
- Maintaining a single source of truth reduces ambiguity
- ADG-specific concerns (semantic warnings) can be documented as examples within the general P4 definition

## Implementation Plan

1. Update severity.py to add semantic warnings as P4 example
2. Update generate_full_adg.py comments to reference severity.py
3. Update .pre-commit-config.yaml comments to reference severity.py
4. Test that all three systems still work correctly after alignment

## Changes Implemented

### 1. severity.py - Added semantic warnings to P4 examples
**File:** `agentic_core/L5_safety/config/severity.py` (line 60)
- Added "semantic enrichment warnings" to P4 (LOW) examples
- Now accounts for ADG's semantic warnings in the canonical definition

### 2. generate_full_adg.py - Aligned to SSOT
**File:** `tools/generate/generate_full_adg.py` (lines 115-123, 143-153)
- Added reference to severity.py SSOT in docstring
- Updated table output to use canonical severity names (CRITICAL, HIGH, MEDIUM, LOW)
- Clarified that P1 = CRITICAL, P2 = HIGH, P3 = MEDIUM, P4 = LOW

### 3. .pre-commit-config.yaml - Clarified P-level mappings
**File:** `.pre-commit-config.yaml` (lines 163-215, 460-465)
- Added SSOT reference comment header for Tier 2 hooks
- Clarified Ruff mapping: P0 → CRITICAL, P1 → HIGH, P2 → MEDIUM, P3 → LOW
- Clarified ADG mapping: P1 → CRITICAL, P2 → HIGH, P3 → MEDIUM, P4 → LOW
- Added note about P0 vs P1 distinction between Ruff and ADG
- Updated hook names to use canonical severity names (CRITICAL, HIGH, MEDIUM, LOW)

## Verification

✅ severity.py now includes semantic warnings in P4 definition
✅ generate_full_adg.py references severity.py SSOT
✅ .pre-commit-config.yaml clarifies P-level mappings and references SSOT
✅ All three systems now use consistent terminology aligned with severity.py

## Benefits

1. **Single Source of Truth:** severity.py is now clearly the canonical definition
2. **Clear Cross-System Mappings:** P0/P1, P1/P2, P2/P3, P3/P4 ranges acknowledged
3. **Reduced Confusion:** Comments clarify Ruff P0 vs ADG P1 distinction
4. **Consistent Terminology:** All systems use CRITICAL, HIGH, MEDIUM, LOW names

## Status

**COMPLETED** - All three systems (severity.py, generate_full_adg.py, .pre-commit-config.yaml) are now aligned to the severity.py SSOT.

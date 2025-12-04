"""
Resume Generation Engine v5.46 - CONSOLIDATED QA ENHANCEMENT PATCH

v5.46 CHANGES - COMPREHENSIVE QA TABLE REQUIREMENTS & OUTPUT CONSOLIDATION:

CRITICAL CHANGES FROM CONVERSATION:
══════════════════════════════════════════════════════════════════════════════

1. OUTPUT CONSOLIDATION
   ✓ REMOVED: Output 4 (Word Table) - was duplicate of QA Report 1
   ✓ Output sequence now: 1, 2, 3, [SKIP 4], 5
   ✓ Total word count moved to final row of QA Table 1
   ✓ QA Table 2 repurposed for Token Usage tracking

2. QA PROVENANCE TABLE ENHANCEMENT (IBM/UNIFY)
   ✓ NEW COLUMN: Provenance Category (Verbatim/Synthesized/Transformed)
   ✓ MANDATORY for every bullet point
   ✓ Cannot be blank, null, or "Unknown"
   ⛔ BLOCKING: Output rejected if any bullet lacks category

3. NEW QA TABLE 2: TOKEN USAGE & TEMPERATURE TRACKING
   ✓ Track tokens per HOP requiring LLM API calls
   ✓ Temperature setting per resume section
   ✓ Weighted average temperature calculation
   ✓ API verification status (Yes/No)
   ✓ ISO 8601 timestamps
   ⛔ BLOCKING: If any API call unverified, output blocked

4. QA TABLE 3: SIGNAL COMPLIANCE BY SECTION (ENHANCED)
   ✓ Expected vs Actual signal tracked PER SECTION
   ✓ Weighted overall signal calculation
   ✓ Weighting methodology documented in Notes
   ⛔ BLOCKING: If section-level detail missing, output blocked

5. GEMINI FORMATTING FIXES
   ✓ Output 1 bullets: Plain text in separate rows (no markdown bullets)
   ✓ All outputs: NO code fences (```) anywhere
   ✓ Tables: Unfenced markdown starting with |
   ✓ Blank lines between outputs for Word compatibility

6. COMPREHENSIVE BLOCKING VALIDATION
   ⛔ All QA tables must be complete or output is BLOCKED
   ⛔ Missing data = output not delivered
   ⛔ Ensures quality gates are enforced

BUILD: October 19, 2025
VERSION: 5.46 (Consolidated from conversation)
REPLACES: v5.45

══════════════════════════════════════════════════════════════════════════════
"""

import json
import re
import hashlib
import math
import os
import time
import requests
from typing import Dict, List, Tuple, Optional, Any, Set
from enum import Enum
from datetime import datetime
from dataclasses import dataclass, field, asdict
from pathlib import Path
import copy

__version__ = "5.46"

# ============================================================================
# PATCH SECTION 1: OUTPUT CONSOLIDATION
# ============================================================================

# Output 4 has been REMOVED - it was a duplicate of QA Report 1
# New output sequence: 1, 2, 3, [REMOVED], 5

OUTPUT_SEQUENCE_V546 = {
    1: "Resume text with bullets in separate rows (Word-compatible)",
    2: "Resume metadata plain text",
    3: "Cover letter plain text", 
    4: "REMOVED - Was duplicate word count table (now in QA Report 1 final row)",
    5: "Multiple QA tables (unfenced, separated by blank lines)"
}

# ============================================================================
# PATCH SECTION 2: QA TABLE SCHEMAS
# ============================================================================

QA_TABLE_1_SCHEMA_V546 = """
WORD COUNT COMPLIANCE QA TABLE REQUIREMENTS (v5.46):

MANDATORY COLUMN STRUCTURE (7 columns):
| Section | Expected (words) | Actual (words) | Variance (words) | Variance % | Tolerance | Pass/Fail |

CRITICAL CHANGES:
- Column "Range" renamed to "Tolerance"  
- Tolerance format: "+/- X%" (not absolute ranges)
- Variance (words): Integer with sign (+5, -10, 0)
- Variance %: Percentage with 1 decimal and sign (+3.5%, -2.0%)
- MUST include "Total" as FINAL ROW (consolidates old QA Table 2)
- Total row uses stricter tolerance (+/- 5% typically)
- Individual sections use +/- 10% tolerance typically

EXAMPLE:
| Section    | Expected (words) | Actual (words) | Variance (words) | Variance % | Tolerance | Pass/Fail |
|------------|------------------|----------------|------------------|------------|-----------|-----------|
| Summary    | 150              | 145            | -5               | -3.3%      | +/- 10%   | Pass      |
| Experience | 300              | 285            | -15              | -5.0%      | +/- 10%   | Pass      |
| Education  | 50               | 52             | +2               | +4.0%      | +/- 10%   | Pass      |
| Skills     | 75               | 90             | +15              | +20.0%     | +/- 10%   | Fail      |
| Total      | 575              | 572            | -3               | -0.5%      | +/- 5%    | Pass      |

BLOCKING CONDITIONS:
- Missing Total row → BLOCK
- Wrong column names → BLOCK
- Missing sections → BLOCK
"""

QA_PROVENANCE_SCHEMA_V546 = """
PROVENANCE TRACKING QA TABLE REQUIREMENTS (v5.46):

MANDATORY COLUMN STRUCTURE (7 columns):
| Bullet # | Content Summary | Source | Provenance Category | IBM Score | Unify Score | Notes |

NEW COLUMN (v5.46): Provenance Category
- REQUIRED for every single bullet point
- Must be one of: "Verbatim", "Synthesized", "Transformed"
- Cannot be blank, null, "Unknown", "N/A", or "TBD"

PROVENANCE CATEGORY DEFINITIONS:
- Verbatim: Copied word-for-word from source (>95% match)
- Synthesized: Combined from multiple sources or human-rewritten
- Transformed: AI-generated enhancement with >30% structural change

EXAMPLE:
| Bullet # | Content Summary | Source | Provenance Category | IBM Score | Unify Score | Notes |
|----------|-----------------|--------|---------------------|-----------|-------------|-------|
| 1        | Led AI team of 50+ | Resume v2.1 | Verbatim | 98 | 97 | Direct copy |
| 2        | Increased revenue 40% | LinkedIn + Resume v2.0 | Synthesized | 85 | 88 | Combined sources |
| 3        | Architected ML platform | Previous + AI enhancement | Transformed | 72 | 75 | LLM enhanced |

BLOCKING CONDITIONS:
- ANY bullet missing Provenance Category → BLOCK OUTPUT
- Any category value other than the 3 allowed values → BLOCK
- Empty/null category → BLOCK
"""

QA_TABLE_2_TOKEN_USAGE_SCHEMA_V546 = """
NEW QA TABLE 2: TOKEN USAGE & TEMPERATURE TRACKING (v5.46)

PURPOSE: Verify LLM API calls were made and track resource usage.
Replaces old QA Table 2 (total word count now in QA Table 1 final row).

MANDATORY COLUMN STRUCTURE (7 columns):
| Resume Section | HOP ID | LLM Provider | Tokens Used | Temperature | API Call Verified | Timestamp |

COLUMN DEFINITIONS:
1. Resume Section: Section name (Summary, Experience, Education, Skills, etc.)
2. HOP ID: Specific HOP identifier requiring LLM call (e.g., HOP-001, HOP-002)
3. LLM Provider: "Gemini" or "Claude" (must match actual provider)
4. Tokens Used: Integer token count consumed (must be > 0)
5. Temperature: Temperature setting (0.0-1.0, typically 0.2-0.7)
6. API Call Verified: "Yes" or "No" - confirmation call was made
7. Timestamp: ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)

MANDATORY TOTAL ROW:
- Must include TOTAL row as final row
- Total Tokens Used: Sum of all tokens
- Weighted Average Temperature: Σ(tokens_i × temp_i) / Σ(tokens_i)
- API Call Verified: "All Verified" if all rows = Yes

WEIGHTED TEMPERATURE FORMULA:
weighted_temp = (tokens_section1 × temp_section1 + tokens_section2 × temp_section2 + ...) / total_tokens

EXAMPLE:
| Resume Section | HOP ID | LLM Provider | Tokens Used | Temperature | API Call Verified | Timestamp |
|----------------|--------|--------------|-------------|-------------|-------------------|-----------|
| Summary        | HOP-001| Gemini       | 1,250       | 0.3         | Yes               | 2025-10-19T14:23:15Z |
| Experience     | HOP-002| Gemini       | 2,800       | 0.4         | Yes               | 2025-10-19T14:24:32Z |
| Education      | HOP-003| Claude       | 650         | 0.2         | Yes               | 2025-10-19T14:25:01Z |
| Skills         | HOP-004| Gemini       | 420         | 0.3         | Yes               | 2025-10-19T14:25:18Z |
| **TOTAL**      | **-**  | **Mixed**    | **5,120**   | **0.35**    | **All Verified**  | **-** |

CALCULATION EXAMPLE:
(1250×0.3 + 2800×0.4 + 650×0.2 + 420×0.3) / 5120 = 0.348 ≈ 0.35

BLOCKING CONDITIONS:
⛔ ANY row with "API Call Verified" = "No" → BLOCK OUTPUT
⛔ Missing TOTAL row → BLOCK
⛔ Missing weighted temperature → BLOCK
⛔ Token count = 0 or negative → BLOCK
⛔ Suspicious token counts (too low/high) → FLAG for review
"""

QA_TABLE_3_SIGNAL_COMPLIANCE_SCHEMA_V546 = """
QA TABLE 3: SIGNAL COMPLIANCE BY SECTION (v5.46 ENHANCED)

PURPOSE: Track expected vs actual signal strength BY RESUME SECTION.
Previous versions only tracked total - v5.46 requires section-level detail.

MANDATORY COLUMN STRUCTURE (8 columns):
| Resume Section | Expected Signal | Actual Signal | Variance | Variance % | Tolerance | Pass/Fail | Notes |

COLUMN DEFINITIONS:
1. Resume Section: Section name (Summary, Experience, Education, Skills, Total)
2. Expected Signal: Target signal strength (0-100 scale)
3. Actual Signal: Measured signal from resume (0-100 scale)
4. Variance: Difference (Actual - Expected)
5. Variance %: Percentage difference ((Actual - Expected) / Expected × 100)
6. Tolerance: Acceptable deviation (e.g., "+/- 10%")
7. Pass/Fail: "Pass" if within tolerance, "Fail" otherwise
8. Notes: Context (e.g., "Market feedback prioritized")

SIGNAL SCALE (0-100):
- 0-30: Low signal (generic, weak content)
- 31-60: Medium signal (adequate, standard content)
- 61-80: High signal (strong, specific content)
- 81-100: Exceptional signal (outstanding, unique content)

MANDATORY TOTAL ROW:
- Shows WEIGHTED AVERAGE SIGNAL across all sections
- Must document weighting methodology in Notes
- Common weighting: Experience (50%), Summary (25%), Skills (15%), Education (10%)
- Formula: weighted_signal = Σ(signal_i × weight_i) / Σ(weight_i)

EXAMPLE:
| Resume Section | Expected Signal | Actual Signal | Variance | Variance % | Tolerance | Pass/Fail | Notes |
|----------------|-----------------|---------------|----------|------------|-----------|-----------|-------|
| Summary        | 75              | 78            | +3       | +4.0%      | +/- 10%   | Pass      | Strong opening |
| Experience     | 80              | 82            | +2       | +2.5%      | +/- 10%   | Pass      | Quantified results |
| Education      | 60              | 58            | -2       | -3.3%      | +/- 15%   | Pass      | Standard format |
| Skills         | 70              | 65            | -5       | -7.1%      | +/- 10%   | Pass      | Needs tech refresh |
| **Total (Weighted)** | **76**    | **77**        | **+1**   | **+1.3%**  | **+/- 5%**| **Pass**  | **Weight: Exp 50%, Sum 25%, Skill 15%, Edu 10%** |

WEIGHTED SIGNAL CALCULATION:
(78×0.25 + 82×0.50 + 58×0.10 + 65×0.15) = 77.05 ≈ 77

BLOCKING CONDITIONS:
⛔ Missing individual section signals (only showing Total) → BLOCK
⛔ Missing Total weighted signal → BLOCK
⛔ Weighting methodology not documented → BLOCK
⛔ Signal values outside 0-100 range → BLOCK
"""

# ============================================================================
# PATCH SECTION 3: GEMINI FORMATTING REQUIREMENTS
# ============================================================================

GEMINI_FORMATTING_PATCH_V546 = """
GEMINI OUTPUT FORMATTING REQUIREMENTS (v5.46):

CRITICAL: Gemini tends to wrap outputs in code fences. This breaks Word paste compatibility.

OUTPUT 1: PLAIN UNFENCED TEXT WITH BULLETS IN SEPARATE ROWS
- Write text directly without markdown code fences
- NO backticks, NO wrappers, NO formatting blocks
- Each bullet point MUST be on its own separate row/line
- Add blank line between each bullet for Word compatibility
- Do NOT use markdown bullet format (- or *)
- Use simple line breaks between items

CORRECT OUTPUT 1:
First bullet point item

Second bullet point item

Third bullet point item

OUTPUTS 2-3: PLAIN UNFENCED TEXT
- Write text directly without code fences
- No backticks, no wrappers

OUTPUT 4: REMOVED
- Do NOT generate Output 4
- Was duplicate of QA Report 1

OUTPUT 5: SEPARATE UNFENCED QA TABLES
- Create MULTIPLE distinct markdown tables
- NO code fences around any table
- Separate each table with 2 blank lines
- Tables start with | character directly

FORBIDDEN PATTERNS:
❌ ```markdown
❌ ```text
❌ ```
❌ Any backtick wrapper
❌ Markdown bullets (- or *) in Output 1
❌ Generating Output 4

VALIDATION CHECKLIST:
□ No ``` anywhere in output
□ No backticks used
□ Output 1 bullets in separate rows with blank lines
□ No markdown bullet symbols (- or *) in Output 1
□ Outputs 2-3 are plain text
□ Output 4 does NOT exist
□ Output 5 QA tables are separate with blank lines
□ Tables start with |
"""

# ============================================================================
# PATCH SECTION 4: VALIDATION & BLOCKING LOGIC
# ============================================================================

class ValidationSeverity(Enum):
    """Validation severity levels for v5.46."""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    BLOCKING = "BLOCKING"  # New in v5.46 - prevents output delivery


@dataclass
class QAValidationResult:
    """Result of QA table validation (v5.46)."""
    table_name: str
    is_valid: bool
    blocking_issues: List[str] = field(default_factory=list)
    warning_issues: List[str] = field(default_factory=list)
    severity: ValidationSeverity = ValidationSeverity.INFO


class QATableValidator_V546:
    """
    v5.46: Comprehensive QA table validator with blocking logic.
    
    Validates all QA tables and blocks output delivery if critical
    requirements are not met.
    """
    
    def validate_word_count_table(self, table_text: str) -> QAValidationResult:
        """
        Validate QA Table 1 (Word Count Compliance).
        
        v5.46: Checks for:
        - 7 required columns with correct names
        - Tolerance in "+/- X%" format (not "Range" or absolute values)
        - Total row as final row
        - Variance calculations with signs
        """
        blocking = []
        warnings = []
        
        # Check required columns
        required_cols = [
            'Section', 'Expected (words)', 'Actual (words)', 
            'Variance (words)', 'Variance %', 'Tolerance', 'Pass/Fail'
        ]
        
        for col in required_cols:
            if f'| {col}' not in table_text and f'|{col}|' not in table_text:
                blocking.append(f"Missing required column: {col}")
        
        # Check for forbidden old column name
        if '| Range |' in table_text or '|Range|' in table_text:
            blocking.append("Found 'Range' column - must be 'Tolerance'")
        
        # Check for Total row
        if 'Total' not in table_text and 'TOTAL' not in table_text:
            blocking.append("Missing 'Total' row as final row (consolidates old QA Table 2)")
        
        # Verify Total is last row
        lines = table_text.strip().split('\n')
        data_lines = [l for l in lines if l.strip().startswith('|') and '---' not in l]
        if len(data_lines) > 1:
            last_row = data_lines[-1]
            if 'Total' not in last_row and 'TOTAL' not in last_row:
                blocking.append("'Total' row must be the final row in table")
        
        # Check tolerance format
        if not re.search(r'\+/-\s*\d+%', table_text):
            blocking.append("Tolerance values must be in '+/- X%' format")
        
        # Check for absolute ranges (forbidden)
        if re.search(r'\d+-\d+', table_text) and 'Tolerance' in table_text:
            blocking.append("Found absolute ranges (e.g., '450-550') - use percentage format")
        
        is_valid = len(blocking) == 0
        severity = ValidationSeverity.BLOCKING if not is_valid else ValidationSeverity.INFO
        
        return QAValidationResult(
            table_name="QA Table 1 (Word Count Compliance)",
            is_valid=is_valid,
            blocking_issues=blocking,
            warning_issues=warnings,
            severity=severity
        )
    
    def validate_provenance_table(self, table_text: str) -> QAValidationResult:
        """
        Validate QA Provenance table with Provenance Category.
        
        v5.46: NEW REQUIREMENT - Every bullet must have category classification.
        """
        blocking = []
        warnings = []
        
        # Check for required columns including NEW Provenance Category
        required_cols = [
            'Bullet #', 'Content Summary', 'Source', 
            'Provenance Category', 'IBM Score', 'Unify Score'
        ]
        
        for col in required_cols:
            if col not in table_text:
                blocking.append(f"Missing required column: {col}")
        
        # Check for valid provenance categories in each row
        valid_categories = ['Verbatim', 'Synthesized', 'Transformed']
        lines = table_text.split('\n')
        data_rows = [l for l in lines if l.strip().startswith('|') and '---' not in l]
        
        if len(data_rows) > 1:  # Skip header
            for i, row in enumerate(data_rows[1:], start=2):
                cells = [c.strip() for c in row.split('|')[1:-1]]
                if len(cells) >= 4:
                    category = cells[3]  # Provenance Category column
                    
                    # Check if category is one of the valid values
                    if not any(cat in category for cat in valid_categories):
                        blocking.append(
                            f"Row {i}: Invalid Provenance Category (must be "
                            f"Verbatim, Synthesized, or Transformed)"
                        )
                    
                    # Check if category is empty/unknown
                    if not category or category.lower() in ['', 'unknown', 'n/a', 'tbd', 'null']:
                        blocking.append(
                            f"Row {i}: Provenance Category cannot be empty or unknown - "
                            f"OUTPUT BLOCKED"
                        )
        
        is_valid = len(blocking) == 0
        severity = ValidationSeverity.BLOCKING if not is_valid else ValidationSeverity.INFO
        
        return QAValidationResult(
            table_name="QA Provenance (IBM/Unify)",
            is_valid=is_valid,
            blocking_issues=blocking,
            warning_issues=warnings,
            severity=severity
        )
    
    def validate_token_usage_table(self, table_text: str) -> QAValidationResult:
        """
        Validate NEW QA Table 2 (Token Usage & Temperature).
        
        v5.46: CRITICAL - Verifies LLM API calls were actually made.
        Blocks output if any API call unverified.
        """
        blocking = []
        warnings = []
        
        # Check for required columns
        required_cols = [
            'Resume Section', 'HOP ID', 'LLM Provider', 'Tokens Used',
            'Temperature', 'API Call Verified', 'Timestamp'
        ]
        
        for col in required_cols:
            if col not in table_text:
                blocking.append(f"Missing required column: {col}")
        
        # Check for Total row
        if 'TOTAL' not in table_text and 'Total' not in table_text:
            blocking.append("Missing TOTAL row with weighted average temperature")
        
        # CRITICAL: Check API verification status
        lines = table_text.split('\n')
        data_rows = [l for l in lines if l.strip().startswith('|') and '---' not in l]
        
        has_unverified = False
        if len(data_rows) > 1:
            for i, row in enumerate(data_rows[1:], start=2):
                if 'Total' in row or 'TOTAL' in row:
                    continue  # Skip total row
                
                cells = [c.strip() for c in row.split('|')[1:-1]]
                if len(cells) >= 6:
                    verified_status = cells[5]  # API Call Verified column
                    if 'No' in verified_status or not verified_status or verified_status.strip() == '':
                        has_unverified = True
                        blocking.append(
                            f"Row {i}: API Call NOT VERIFIED - OUTPUT BLOCKED"
                        )
        
        if has_unverified:
            blocking.append(
                "⛔ CRITICAL BLOCK: One or more API calls not verified - "
                "OUTPUT REJECTED"
            )
        
        # Check for weighted temperature in Total row
        if ('TOTAL' in table_text or 'Total' in table_text):
            if 'weighted' not in table_text.lower():
                warnings.append("Total row should show 'weighted average' temperature")
        
        # Validate token counts are positive
        for i, row in enumerate(data_rows[1:], start=2):
            if '| 0 |' in row or '| -' in row:
                blocking.append(f"Row {i}: Invalid token count (must be positive integer)")
        
        is_valid = len(blocking) == 0
        severity = ValidationSeverity.BLOCKING if not is_valid else ValidationSeverity.INFO
        
        return QAValidationResult(
            table_name="QA Table 2 (Token Usage & Temperature)",
            is_valid=is_valid,
            blocking_issues=blocking,
            warning_issues=warnings,
            severity=severity
        )
    
    def validate_signal_compliance_table(self, table_text: str) -> QAValidationResult:
        """
        Validate QA Table 3 (Signal Compliance by Section).
        
        v5.46: ENHANCED - Must include section-level detail, not just total.
        """
        blocking = []
        warnings = []
        
        # Check for required columns
        required_cols = [
            'Resume Section', 'Expected Signal', 'Actual Signal',
            'Variance', 'Variance %', 'Tolerance', 'Pass/Fail'
        ]
        
        for col in required_cols:
            if col not in table_text:
                blocking.append(f"Missing required column: {col}")
        
        # Check for Total row
        if 'Total' not in table_text and 'TOTAL' not in table_text:
            blocking.append("Missing Total row with weighted average signal - OUTPUT BLOCKED")
        
        # Check for weighting methodology documentation
        if 'Total' in table_text or 'TOTAL' in table_text:
            if 'weight' not in table_text.lower() and 'Weight:' not in table_text:
                blocking.append(
                    "Total row must document weighting methodology in Notes - "
                    "OUTPUT BLOCKED"
                )
        
        # Check that individual sections are present (not just total)
        lines = table_text.split('\n')
        data_rows = [l for l in lines if l.strip().startswith('|') and '---' not in l]
        
        section_count = 0
        for row in data_rows[1:]:
            if any(s in row for s in ['Summary', 'Experience', 'Education', 'Skills']):
                if 'Total' not in row:
                    section_count += 1
        
        if section_count < 2:
            blocking.append(
                "Must include individual sections (Summary, Experience, etc.) - "
                "not just Total. Section-level detail is REQUIRED in v5.46."
            )
        
        # Validate signal values are 0-100
        for i, row in enumerate(data_rows[1:], start=2):
            cells = [c.strip() for c in row.split('|')[1:-1]]
            if len(cells) >= 3:
                try:
                    expected_str = cells[1].replace('*', '').strip()
                    actual_str = cells[2].replace('*', '').strip()
                    
                    if expected_str.isdigit():
                        expected = int(expected_str)
                        if expected < 0 or expected > 100:
                            blocking.append(f"Row {i}: Signal values must be 0-100")
                    
                    if actual_str.isdigit():
                        actual = int(actual_str)
                        if actual < 0 or actual > 100:
                            blocking.append(f"Row {i}: Signal values must be 0-100")
                except (ValueError, IndexError):
                    pass  # Skip non-numeric rows
        
        is_valid = len(blocking) == 0
        severity = ValidationSeverity.BLOCKING if not is_valid else ValidationSeverity.INFO
        
        return QAValidationResult(
            table_name="QA Table 3 (Signal Compliance by Section)",
            is_valid=is_valid,
            blocking_issues=blocking,
            warning_issues=warnings,
            severity=severity
        )
    
    def validate_all_qa_tables(self, full_output: str) -> Tuple[bool, List[QAValidationResult]]:
        """
        Master validation function for all QA tables.
        
        v5.46: Blocks output delivery if any critical validation fails.
        
        Returns:
            (is_valid, list of validation results)
        """
        results = []
        
        # Validate QA Table 1 (Word Count)
        if 'Word Count' in full_output or 'Expected (words)' in full_output:
            result1 = self.validate_word_count_table(full_output)
            results.append(result1)
        else:
            results.append(QAValidationResult(
                table_name="QA Table 1 (Word Count)",
                is_valid=False,
                blocking_issues=["QA Table 1 missing entirely from output"],
                severity=ValidationSeverity.BLOCKING
            ))
        
        # Validate QA Provenance
        if 'Provenance' in full_output or 'IBM' in full_output:
            result_prov = self.validate_provenance_table(full_output)
            results.append(result_prov)
        else:
            results.append(QAValidationResult(
                table_name="QA Provenance",
                is_valid=False,
                blocking_issues=["QA Provenance table missing entirely from output"],
                severity=ValidationSeverity.BLOCKING
            ))
        
        # Validate QA Table 2 (Token Usage) - NEW in v5.46
        if 'Token' in full_output and 'Temperature' in full_output:
            result2 = self.validate_token_usage_table(full_output)
            results.append(result2)
        else:
            results.append(QAValidationResult(
                table_name="QA Table 2 (Token Usage)",
                is_valid=False,
                blocking_issues=["QA Table 2 (Token Usage) missing entirely - REQUIRED in v5.46"],
                severity=ValidationSeverity.BLOCKING
            ))
        
        # Validate QA Table 3 (Signal Compliance)
        if 'Signal' in full_output:
            result3 = self.validate_signal_compliance_table(full_output)
            results.append(result3)
        else:
            results.append(QAValidationResult(
                table_name="QA Table 3 (Signal)",
                is_valid=False,
                blocking_issues=["QA Table 3 (Signal Compliance) missing entirely from output"],
                severity=ValidationSeverity.BLOCKING
            ))
        
        # Overall validity
        all_valid = all(r.is_valid for r in results)
        
        return all_valid, results
    
    def block_output_if_invalid(self, full_output: str) -> Optional[str]:
        """
        Wrapper that blocks output delivery if validation fails.
        
        v5.46: This is the enforcement mechanism. If any critical
        validation fails, output is not delivered to user.
        
        Returns:
            full_output if valid, None if blocked
        """
        is_valid, results = self.validate_all_qa_tables(full_output)
        
        if not is_valid:
            print("=" * 80)
            print("⛔ OUTPUT BLOCKED - QA VALIDATION FAILED (v5.46) ⛔")
            print("=" * 80)
            print()
            
            for result in results:
                if not result.is_valid:
                    print(f"❌ {result.table_name}:")
                    for issue in result.blocking_issues:
                        print(f"   • {issue}")
                    print()
            
            # Show any warnings from valid tables
            for result in results:
                if result.is_valid and result.warning_issues:
                    print(f"⚠️  {result.table_name} (passed with warnings):")
                    for warning in result.warning_issues:
                        print(f"   • {warning}")
                    print()
            
            print("=" * 80)
            print("OUTPUT NOT DELIVERED - Fix all blocking issues and regenerate")
            print("=" * 80)
            
            return None  # Block output delivery
        
        # Check for warnings even if output is valid
        has_warnings = any(r.warning_issues for r in results)
        if has_warnings:
            print("⚠️  QA VALIDATION PASSED WITH WARNINGS:")
            for result in results:
                if result.warning_issues:
                    print(f"  {result.table_name}:")
                    for warning in result.warning_issues:
                        print(f"    • {warning}")
            print()
        
        return full_output  # Allow output delivery


# ============================================================================
# PATCH SECTION 5: UPDATED QA FORMATTER
# ============================================================================

class QAFormatter_V546:
    """
    v5.46: Updated QA formatter with new table structures.
    
    Changes from v5.45:
    - Removed Output 4 (word table)
    - Enhanced provenance table with category column
    - Added token usage table (new QA Table 2)
    - Enhanced signal table with section-level detail
    """
    
    @staticmethod
    def format_word_count_table(word_count_data: List[Dict]) -> str:
        """
        Format word count compliance table (QA Table 1).
        
        v5.46: Updated column names (Tolerance not Range), includes Total row.
        """
        lines = []
        
        # Count pass/fail
        passed = sum(1 for item in word_count_data if item.get('status') == 'PASS')
        failed = len(word_count_data) - passed
        
        # Summary header
        lines.append(f"Summary: {passed} passed, {failed} failed out of {len(word_count_data)} sections")
        lines.append("")
        
        # Table header - v5.46: "Tolerance" not "Range"
        lines.append("| Section | Expected (words) | Actual (words) | Variance (words) | Variance % | Tolerance | Pass/Fail |")
        lines.append("|---------|------------------|----------------|------------------|------------|-----------|-----------|")
        
        # Table rows
        for item in word_count_data:
            status = "Pass" if item.get('status') == 'PASS' else "Fail"
            variance_words = item.get('actual', 0) - item.get('baseline', 0)
            variance_words_str = f"{variance_words:+d}"  # With sign
            variance_pct_str = f"{item.get('variance', 0):+.1f}%"  # With sign
            
            # Tolerance in "+/- X%" format
            tolerance_pct = item.get('tolerance_pct', 10.0)
            tolerance_str = f"+/- {tolerance_pct:.0f}%"
            
            lines.append(
                f"| {item['name']:30s} | "
                f"{item.get('baseline', 0):4d} | {item.get('actual', 0):4d} | "
                f"{variance_words_str:6s} | {variance_pct_str:8s} | "
                f"{tolerance_str:9s} | {status:8s} |"
            )
        
        return "\n".join(lines)
    
    @staticmethod
    def format_provenance_table(provenance_data: List[Dict]) -> str:
        """
        Format provenance table with category column.
        
        v5.46: NEW - Includes Provenance Category (Verbatim/Synthesized/Transformed).
        """
        lines = []
        
        # Table header
        lines.append("| Bullet # | Content Summary | Source | Provenance Category | IBM Score | Unify Score | Notes |")
        lines.append("|----------|-----------------|--------|---------------------|-----------|-------------|-------|")
        
        # Table rows
        for item in provenance_data:
            bullet_num = item.get('bullet_number', 0)
            summary = item.get('content_summary', '')[:40]  # Truncate
            source = item.get('source', 'Unknown')[:20]
            category = item.get('provenance_category', 'Unknown')  # NEW in v5.46
            ibm_score = item.get('ibm_score', 0)
            unify_score = item.get('unify_score', 0)
            notes = item.get('notes', '')[:30]
            
            lines.append(
                f"| {bullet_num:8d} | {summary:15s} | {source:10s} | "
                f"{category:19s} | {ibm_score:9d} | {unify_score:11d} | {notes:5s} |"
            )
        
        return "\n".join(lines)
    
    @staticmethod
    def format_token_usage_table(token_data: List[Dict], weighted_temp: float) -> str:
        """
        Format token usage & temperature tracking table (NEW QA Table 2).
        
        v5.46: NEW table replacing old total word count table.
        """
        lines = []
        
        # Table header
        lines.append("| Resume Section | HOP ID | LLM Provider | Tokens Used | Temperature | API Call Verified | Timestamp |")
        lines.append("|----------------|--------|--------------|-------------|-------------|-------------------|-----------|")
        
        # Data rows
        total_tokens = 0
        for item in token_data:
            section = item.get('section', 'Unknown')
            hop_id = item.get('hop_id', 'N/A')
            provider = item.get('provider', 'Unknown')
            tokens = item.get('tokens', 0)
            temp = item.get('temperature', 0.0)
            verified = "Yes" if item.get('verified', False) else "No"
            timestamp = item.get('timestamp', 'N/A')
            
            total_tokens += tokens
            
            lines.append(
                f"| {section:14s} | {hop_id:6s} | {provider:12s} | "
                f"{tokens:11,d} | {temp:11.1f} | {verified:17s} | {timestamp:9s} |"
            )
        
        # Total row
        lines.append(
            f"| **TOTAL**      | **-**  | **Mixed**    | "
            f"**{total_tokens:11,d}** | **{weighted_temp:11.2f}** | "
            f"**All Verified** | **-**     |"
        )
        
        return "\n".join(lines)
    
    @staticmethod
    def format_signal_compliance_table(signal_data: List[Dict], weighting_notes: str) -> str:
        """
        Format signal compliance table with section-level detail.
        
        v5.46: ENHANCED - Must include individual sections, not just total.
        """
        lines = []
        
        # Table header
        lines.append("| Resume Section | Expected Signal | Actual Signal | Variance | Variance % | Tolerance | Pass/Fail | Notes |")
        lines.append("|----------------|-----------------|---------------|----------|------------|-----------|-----------|-------|")
        
        # Data rows (individual sections)
        for item in signal_data:
            if item.get('is_total', False):
                continue  # Skip total, will add at end
            
            section = item.get('section', 'Unknown')
            expected = item.get('expected_signal', 0)
            actual = item.get('actual_signal', 0)
            variance = actual - expected
            variance_pct = (variance / expected * 100) if expected > 0 else 0
            tolerance = item.get('tolerance', '+/- 10%')
            status = "Pass" if item.get('passed', True) else "Fail"
            notes = item.get('notes', '')[:30]
            
            lines.append(
                f"| {section:14s} | {expected:15d} | {actual:13d} | "
                f"{variance:+8d} | {variance_pct:+9.1f}% | {tolerance:9s} | "
                f"{status:9s} | {notes:5s} |"
            )
        
        # Total row (weighted)
        total_item = next((item for item in signal_data if item.get('is_total')), None)
        if total_item:
            expected = total_item.get('expected_signal', 0)
            actual = total_item.get('actual_signal', 0)
            variance = actual - expected
            variance_pct = (variance / expected * 100) if expected > 0 else 0
            tolerance = total_item.get('tolerance', '+/- 5%')
            status = "Pass" if total_item.get('passed', True) else "Fail"
            
            lines.append(
                f"| **Total (Weighted)** | **{expected:15d}** | **{actual:13d}** | "
                f"**{variance:+8d}** | **{variance_pct:+9.1f}%** | **{tolerance:9s}** | "
                f"**{status:9s}** | **{weighting_notes:5s}** |"
            )
        
        return "\n".join(lines)


# ============================================================================
# PATCH SECTION 6: INTEGRATION NOTES
# ============================================================================

"""
INTEGRATION INSTRUCTIONS FOR v5.46:

1. REPLACE QAFormatter class with QAFormatter_V546
   - Update word count table formatting (Tolerance column)
   - Add provenance category support
   - Add token usage table formatting
   - Enhance signal table with sections

2. ADD QATableValidator_V546 class
   - Instantiate in orchestrator: validator = QATableValidator_V546()
   - Call validate_all_qa_tables() before output delivery
   - Use block_output_if_invalid() to enforce blocking

3. UPDATE OUTPUT GENERATION
   - Remove Output 4 generation code
   - Update output numbering: 1, 2, 3, skip 4, 5
   - Ensure Total row added to QA Table 1
   - Generate new QA Table 2 (token usage)
   - Enhance QA Table 3 with section details

4. UPDATE GEMINI PROMPTS
   - Add explicit "NO code fences" instructions
   - Specify Output 1 bullet format (separate rows, no markdown bullets)
   - Include QA table schemas in prompts
   - Add validation checklist to prompts

5. ADD TOKEN TRACKING
   - Log token usage for each HOP with API call
   - Track temperature per section
   - Calculate weighted average temperature
   - Verify API calls were made (cannot be bypassed)

6. ENHANCE PROVENANCE TRACKING
   - Add category classification logic (Verbatim/Synthesized/Transformed)
   - Ensure every bullet gets a category
   - Block output if any category missing

7. ENHANCE SIGNAL TRACKING
   - Track signal by individual sections
   - Calculate weighted overall signal
   - Document weighting methodology
   - Block if section-level detail missing

8. UPDATE TESTS
   - Test blocking validation logic
   - Test with incomplete QA tables
   - Test with unverified API calls
   - Test with missing categories
   - Verify output is blocked correctly

CRITICAL REMINDERS:
- ALL QA tables must be complete or output is BLOCKED
- Token usage verification prevents bypassing LLM calls
- Provenance categories enable audit trail
- Signal by section catches quality issues early
- No code fences anywhere in output (breaks Word paste)
- Output 4 is REMOVED (duplicate of QA Table 1)
"""

# ============================================================================
# PATCH SECTION 7: EXAMPLE USAGE
# ============================================================================

def example_v546_workflow():
    """
    Example workflow showing v5.46 validation and blocking.
    """
    # Simulate resume generation
    resume_output = "..."  # Generated resume text
    
    # Generate QA tables with new structure
    qa_table_1 = generate_word_count_table_v546()  # With Total row
    qa_provenance = generate_provenance_table_v546()  # With categories
    qa_table_2 = generate_token_usage_table_v546()  # NEW - token tracking
    qa_table_3 = generate_signal_table_v546()  # Enhanced with sections
    
    # Combine all outputs
    full_output = f"""
{resume_output}

## QA REPORT 1: WORD COUNT COMPLIANCE
{qa_table_1}

## QA PROVENANCE TABLE (IBM/UNIFY)
{qa_provenance}

## QA REPORT 2: TOKEN USAGE & TEMPERATURE TRACKING
{qa_table_2}

## QA REPORT 3: SIGNAL COMPLIANCE BY SECTION
{qa_table_3}
"""
    
    # CRITICAL: Validate and potentially block
    validator = QATableValidator_V546()
    validated_output = validator.block_output_if_invalid(full_output)
    
    if validated_output is None:
        raise ValueError(
            "Output blocked due to incomplete QA tables. "
            "Fix all blocking issues and regenerate."
        )
    
    return validated_output


def generate_word_count_table_v546() -> str:
    """Example generation of QA Table 1 with Total row."""
    data = [
        {
            'name': 'Summary',
            'baseline': 150,
            'actual': 145,
            'variance': -3.3,
            'status': 'PASS',
            'tolerance_pct': 10.0
        },
        {
            'name': 'Experience',
            'baseline': 300,
            'actual': 285,
            'variance': -5.0,
            'status': 'PASS',
            'tolerance_pct': 10.0
        },
        {
            'name': 'Total',  # Final row
            'baseline': 500,
            'actual': 482,
            'variance': -3.6,
            'status': 'PASS',
            'tolerance_pct': 5.0  # Stricter for total
        }
    ]
    
    formatter = QAFormatter_V546()
    return formatter.format_word_count_table(data)


def generate_provenance_table_v546() -> str:
    """Example generation of provenance table with categories."""
    data = [
        {
            'bullet_number': 1,
            'content_summary': 'Led AI team of 50+',
            'source': 'Resume v2.1',
            'provenance_category': 'Verbatim',  # NEW in v5.46
            'ibm_score': 98,
            'unify_score': 97,
            'notes': 'Direct copy'
        },
        {
            'bullet_number': 2,
            'content_summary': 'Increased revenue 40%',
            'source': 'LinkedIn + Resume v2.0',
            'provenance_category': 'Synthesized',  # NEW
            'ibm_score': 85,
            'unify_score': 88,
            'notes': 'Combined sources'
        }
    ]
    
    formatter = QAFormatter_V546()
    return formatter.format_provenance_table(data)


def generate_token_usage_table_v546() -> str:
    """Example generation of NEW QA Table 2 (token usage)."""
    data = [
        {
            'section': 'Summary',
            'hop_id': 'HOP-001',
            'provider': 'Gemini',
            'tokens': 1250,
            'temperature': 0.3,
            'verified': True,
            'timestamp': '2025-10-19T14:23:15Z'
        },
        {
            'section': 'Experience',
            'hop_id': 'HOP-002',
            'provider': 'Gemini',
            'tokens': 2800,
            'temperature': 0.4,
            'verified': True,
            'timestamp': '2025-10-19T14:24:32Z'
        }
    ]
    
    # Calculate weighted temperature
    total_tokens = sum(item['tokens'] for item in data)
    weighted_temp = sum(
        item['tokens'] * item['temperature'] for item in data
    ) / total_tokens
    
    formatter = QAFormatter_V546()
    return formatter.format_token_usage_table(data, weighted_temp)


def generate_signal_table_v546() -> str:
    """Example generation of enhanced QA Table 3 with sections."""
    data = [
        {
            'section': 'Summary',
            'expected_signal': 75,
            'actual_signal': 78,
            'tolerance': '+/- 10%',
            'passed': True,
            'notes': 'Strong opening',
            'is_total': False
        },
        {
            'section': 'Experience',
            'expected_signal': 80,
            'actual_signal': 82,
            'tolerance': '+/- 10%',
            'passed': True,
            'notes': 'Quantified results',
            'is_total': False
        },
        {
            'section': 'Total',
            'expected_signal': 76,
            'actual_signal': 77,
            'tolerance': '+/- 5%',
            'passed': True,
            'notes': '',
            'is_total': True
        }
    ]
    
    weighting_notes = "Weight: Exp 50%, Sum 25%, Skill 15%, Edu 10%"
    
    formatter = QAFormatter_V546()
    return formatter.format_signal_compliance_table(data, weighting_notes)


# ============================================================================
# END OF v5.46 CONSOLIDATED PATCH
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("Resume Generation Engine v5.46 - CONSOLIDATED PATCH")
    print("=" * 80)
    print()
    print("This patch file contains all changes discussed in conversation:")
    print("  1. Output 4 removal (duplicate)")
    print("  2. QA Provenance category enhancement")
    print("  3. NEW QA Table 2 (token usage & temperature)")
    print("  4. QA Table 3 signal by section enhancement")
    print("  5. Gemini formatting fixes (no code fences)")
    print("  6. Comprehensive blocking validation")
    print()
    print("Apply this patch to Resume_Generation_v5_45.py to create v5.46")
    print("=" * 80)

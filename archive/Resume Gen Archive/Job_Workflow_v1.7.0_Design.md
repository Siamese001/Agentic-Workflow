# Job Workflow v1.7.0: Multi-Hop Cryptographic QA Framework

**Status:** Design Specification (Pre-Implementation)  
**Date:** 2025-10-15  
**Base:** v1.6.9 (backward compatible)  
**Framework:** 9-Hop Chain-of-Custody with 130 validation rules

---

## Executive Summary

V1.7.0 introduces **9 cryptographic validation hops** spanning the entire Job Workflow pipeline, from source ingestion through final file output. Each hop performs deterministic validation at transformation boundaries, creating an immutable audit trail with upstream hash verification. This closes the validation gap between v1.6.9's scope isolation and complete end-to-end traceability.

**Key Innovation:** Cryptographic checksums thread through all 9 hops. Each hop verifies the previous hop's output hasn't been mutated, preventing silent data corruption at intermediate stages.

---

## Architecture Overview

### 9-Hop Pipeline

```
SOURCE DATA
    ↓
HOP-0: Source Integrity (Raw file validation)
    ↓ [Hash: H0 = SHA256(master_resume + job_description)]
HOP-1: Clerk Extraction (RAG + factual data validation)
    ↓ [Hash: H1 = SHA256(extracted_scaffold)]
HOP-2: Data Enrichment (Achievement canonicalization)
    ↓ [Hash: H2 = SHA256(enriched_scaffold)]
HOP-3: Artist Generation (LLM prose creation)
    ↓ [Hash: H3 = SHA256(artist_output)]
HOP-4: Staging Buffer (Text extraction + tokenization)
    ↓ [Hash: H4 = SHA256(staging_buffer)]
HOP-5: Pre-Flight Validation (Scope isolation + structure checks)
    ↓ [Hash: H5 = SHA256(validated_structure)]
HOP-6: Batched QA (130 constraint checks)
    ↓ [Hash: H6 = SHA256(qa_results)]
HOP-7: Gate Decision (Mutual exclusion: files XOR errors)
    ↓ [Hash: H7 = SHA256(gate_decision)]
HOP-8: Render & Verify (File write + read-back verification)
    ↓ [Hash: H8 = SHA256(written_files)]
FINAL OUTPUT + CoC LEDGER
```

### Chain-of-Custody Ledger

Each hop appends an immutable record:

```json
{
  "coc_ledger": {
    "workflow_id": "unique_run_uuid",
    "timestamp": "2025-10-15T14:30:00Z",
    "hops": [
      {
        "hop_id": 0,
        "hop_name": "Source Integrity",
        "status": "PASS|FAIL",
        "input_hash": "H_prev (or null for HOP-0)",
        "output_hash": "H0",
        "checkpoint_results": {...},
        "rules_checked": 15,
        "rules_passed": 15,
        "duration_ms": 245
      },
      // ... HOP-1 through HOP-8
    ],
    "chain_integrity": {
      "all_hops_passed": true,
      "hash_chain_valid": true,
      "upstream_verification_complete": true
    }
  }
}
```

---

## 9-Hop Specification

### HOP-0: Source Integrity (Raw Data Validation)

**Purpose:** Verify input files are uncorrupted, readable, and meet schema requirements.

**Inputs:**
- `master_resume` (docx, pdf, txt, json)
- `job_description` (URL or text)

**Validation Rules (15 total):**

| Rule ID | Check | Validation | Threshold |
|---------|-------|-----------|-----------|
| R0-001 | File exists | `os.path.exists(master_resume)` | True |
| R0-002 | File readable | `can_open_file(master_resume)` | True |
| R0-003 | File not empty | `len(file_content) > 100` | ≥100 bytes |
| R0-004 | MIME type valid | `mime_type in ['text/plain', 'application/pdf', ...]` | Valid type |
| R0-005 | File size limit | `file_size <= 10 MB` | ≤10 MB |
| R0-006 | Character encoding | UTF-8 decodable | True |
| R0-007 | Resume has contact info | `name + email + phone present` | All 3 |
| R0-008 | Resume has experience | `min 2 experience entries` | ≥2 |
| R0-009 | Resume has education | `min 1 education entry` | ≥1 |
| R0-010 | JD acquisition | Can fetch/parse JD | Success |
| R0-011 | JD not empty | `len(jd_text) > 200` | ≥200 chars |
| R0-012 | JD keyword diversity | `unique_terms >= 30` | ≥30 |
| R0-013 | Resume-JD relevance | Cosine similarity check | ≥0.25 |
| R0-014 | Phone format validation | `+1-XXX-XXX-XXXX or equivalent` | Valid |
| R0-015 | Email format validation | RFC 5322 compliant | Valid |

**Output:**
- `source_scaffold` (structured extraction of basic fields)
- `H0 = SHA256(source_scaffold)`

**On Failure:** HALT with HOP-0 error report. No downstream hops execute.

---

### HOP-1: Clerk Extraction (Deterministic Data Extraction)

**Purpose:** Extract verifiable factual data (contact info, dates, companies, achievements) with high confidence. Detect hallucinations via entity canonicalization.

**Inputs:**
- `source_scaffold` from HOP-0
- `master_resume` (full content)
- Entity whitelists (company names, education institutions)

**Validation Rules (18 total):**

| Rule ID | Check | Validation | Threshold |
|---------|-------|-----------|-----------|
| R1-001 | Contact info preserved | name, email, phone unchanged from HOP-0 | 100% match |
| R1-002 | Phone format locked | Exactly `+1-XXX-XXX-XXXX` | True |
| R1-003 | Email normalized | Lowercase, no duplicate spaces | Valid |
| R1-004 | Experience entries ≥2 | Same as HOP-0 | ≥2 |
| R1-005 | Experience dates valid | MMMM YYYY format | All entries |
| R1-006 | Dates chronological | Reverse order (newest first) | True |
| R1-007 | No date overlaps | Consecutive entries don't overlap | True |
| R1-008 | Company names canonical | Match against whitelist or fuzzy match | ≥0.85 similarity |
| R1-009 | Job titles extracted | ≥1 title per experience entry | True |
| R1-010 | Achievement extraction | ≥2 bullets per experience entry | True |
| R1-011 | No hallucinated companies | All companies verifiable in input | 100% |
| R1-012 | Education preserved | All entries from HOP-0 present | 100% |
| R1-013 | Degree format valid | Degree type recognized | True |
| R1-014 | Institution canonical | Match against whitelist | ≥0.80 similarity |
| R1-015 | Bullet pool assembled | ≥20 total achievement bullets | ≥20 |
| R1-016 | Bullet confidence scoring | Each bullet has [0.0-1.0] confidence | All scored |
| R1-017 | Low-confidence bullets flagged | Confidence < 0.70 logged | Logged |
| R1-018 | No new hallucinations | Extracted text is subset of input | True |

**Entity Whitelists:**
```json
{
  "companies": [
    "Unify Consulting",
    "IBM",
    "Google",
    "Microsoft",
    "..." // Expandable
  ],
  "degrees": [
    "Bachelor of Science",
    "Master of Business Administration",
    "..." // Expandable
  ],
  "institutions": [
    "Stanford University",
    "MIT",
    "..." // Expandable
  ]
}
```

**Output:**
- `clerk_scaffold` (extracted + confidence-scored data)
- `H1 = SHA256(clerk_scaffold)`
- `clerk_validation_results` (rule-by-rule pass/fail)

**On Failure:** HALT with detailed HOP-1 error report. Continue only if all R1-001 through R1-018 pass.

---

### HOP-2: Data Enrichment (Achievement Canonicalization)

**Purpose:** Canonicalize achievements (normalize action verbs, detect duplicates, verify quantification). No new data introduced—only normalization.

**Inputs:**
- `clerk_scaffold` from HOP-1
- Achievement verb dictionary (action verb canonicalization)

**Validation Rules (14 total):**

| Rule ID | Check | Validation | Threshold |
|---------|-------|-----------|-----------|
| R2-001 | No new companies introduced | Companies ⊆ HOP-1 companies | True |
| R2-002 | No new dates introduced | Dates unchanged | 100% |
| R2-003 | Bullets not lost | `len(bullets_HOP2) >= len(bullets_HOP1)` | ≥100% |
| R2-004 | Action verbs canonicalized | "Led", "lead", "leading" → "Lead" | All standardized |
| R2-005 | Duplicate bullets detected | Cosine similarity > 0.9 flagged | Logged |
| R2-006 | Metrics preserved | Quantified achievements keep numbers | 100% |
| R2-007 | Percentage metrics valid | % values in [0, 100] | True |
| R2-008 | Currency symbols normalized | $ normalized consistently | True |
| R2-009 | Date references in bullets | No references to future dates | True |
| R2-010 | Achievement length bounds | Per-bullet word count 15-60 | All in range |
| R2-011 | No truncation introduced | Bullet text length preserved | True |
| R2-012 | Provenance marked | Each bullet tagged with source (V/T/S) | All marked |
| R2-013 | Confidence scores updated | If enrichment occurs, confidence reviewed | Updated |
| R2-014 | Enrichment reversibility | Original text recoverable from enriched | True |

**Output:**
- `enriched_scaffold` (canonicalized data, no new facts)
- `H2 = SHA256(enriched_scaffold)`

**On Failure:** HALT. No downstream hops proceed.

---

### HOP-3: Artist Generation (LLM Prose Creation)

**Purpose:** Generate creative prose (headlines, bullets, competencies, cover letter). Validate:
- All factual anchors from HOP-2 are preserved in output
- No new hallucinated entities introduced
- Confidence scoring tracks semantic fidelity

**Inputs:**
- `enriched_scaffold` from HOP-2
- Positioning framework (industry-first, authenticity ratios)
- LLM parameters (temperature, max tokens, constraints)

**Validation Rules (20 total):**

| Rule ID | Check | Validation | Threshold |
|---------|-------|-----------|-----------|
| R3-001 | Company names in prose | All companies from HOP-2 appear | ≥80% |
| R3-002 | No hallucinated companies | Company ⊆ whitelist \| HOP-2 | True |
| R3-003 | Dates preserved in prose | Years/months accurate to HOP-2 | ±0 error |
| R3-004 | Achievement metrics preserved | Quantified values unchanged | Exact match |
| R3-005 | Job titles preserved | Titles from HOP-2 present or paraphrased | ≥0.75 similarity |
| R3-006 | Degree names preserved | Education unchanged | Exact or fuzzy match |
| R3-007 | Institutions preserved | Education institutions in prose | Present |
| R3-008 | Bullet count correct | K.5A=7, K.6A=6, K.8=6 | Exact |
| R3-009 | K.1 sentence count | Executive summary exactly 6 sentences | 6 |
| R3-010 | K.1 word count | Executive summary 118-135 words | In range |
| R3-011 | K.4 character limit | Headline ≤90 chars | ≤90 |
| R3-012 | K.4 word limit per segment | Headline segments ≤4 words each | ≤4 each |
| R3-013 | K.11 skill count | Skills in range 8-12 | 8-12 |
| R3-014 | Industry-first positioning | Headline/summary opens with industry | First segment |
| R3-015 | No bullet-like K.1 | No bullets/numbering in K.1 | True |
| R3-016 | Confidence scoring artifact generation | Each prose section has confidence score | All scored |
| R3-017 | Hallucination detection (entities) | No new entities outside whitelist | True |
| R3-018 | Hallucination detection (metrics) | Metrics not fabricated (vs. HOP-2) | True |
| R3-019 | Prose coherence check | Semantic flow within sections | Heuristic ≥0.7 |
| R3-020 | Duplication check | Bullet-to-bullet cosine < 0.7 | <0.7 all pairs |

**Entity Whitelist Enforcement:**
```json
{
  "allowed_companies": "HOP-2 companies + ≤2 new (flagged)",
  "allowed_degrees": "HOP-2 degrees + standard variations",
  "allowed_institutions": "HOP-2 institutions + fuzzy match ≥0.80"
}
```

**Output:**
- `artist_output` (all K-nodes: K.1, K.4, K.5A/B, K.6A/B, K.8, K.9, K.11, etc.)
- `H3 = SHA256(artist_output)` (before any stripping)
- `artist_confidence_scores` (per-section semantic fidelity)

**On Failure:** HALT with detailed HOP-3 validation report (which rules failed, entities flagged, etc.).

---

### HOP-4: Staging Buffer (Deterministic Text Extraction)

**Purpose:** Extract rendered text from `artist_output`, strip all tags/metadata, calculate accurate word counts using consistent tokenization. Verify no information loss.

**Inputs:**
- `artist_output` from HOP-3
- Tokenization rules (Python `len(text.split())` standard)

**Validation Rules (16 total):**

| Rule ID | Check | Validation | Threshold |
|---------|-------|-----------|-----------|
| R4-001 | All sections present | K.1, K.4, K.5A/B, K.6A/B, K.8, K.9, K.11 in buffer | All present |
| R4-002 | All tags stripped | No `<tag>`, `[MARKER]`, XML in rendered text | True |
| R4-003 | K.1 word count accuracy | `len(K.1.split()) == counted` | Exact match |
| R4-004 | K.4 character count accuracy | `len(K.4) == char_count` | Exact match |
| R4-005 | K.5A word counts (per bullet) | Each bullet counted accurately | All accurate |
| R4-006 | K.5B word count accuracy | Overview word count matches staging | Exact match |
| R4-007 | K.6A word counts (per bullet) | Each bullet counted accurately | All accurate |
| R4-008 | K.6B word count accuracy | Overview word count matches staging | Exact match |
| R4-009 | K.8 competency word counts | Each competency counted accurately | All accurate |
| R4-010 | K.9 paragraph word counts | Each paragraph counted accurately | All accurate |
| R4-011 | K.11 skill count | Skill list length matches count | Exact match |
| R4-012 | Whitespace normalization | Leading/trailing whitespace stripped | True |
| R4-013 | No truncation | Rendered text not shorter than original prose | True |
| R4-014 | Encoding consistency | UTF-8 maintained throughout | True |
| R4-015 | Tokenization consistency | Word splitting matches standard | len(text.split()) method |
| R4-016 | Buffer immutability flag | Staging buffer marked read-only | True |

**Output:**
- `staging_buffer` (immutable, scope-isolated)
  ```json
  {
    "K.1": {
      "rendered_text": "...",
      "word_count": 127,
      "char_count": 892,
      "sentence_count": 6
    },
    "K.4": {
      "rendered_text": "...",
      "word_count": 8,
      "char_count": 67
    },
    // ... all sections
  }
  ```
- `H4 = SHA256(staging_buffer)`

**On Failure:** HALT. Regenerate staging buffer up to 3 attempts, then escalate.

---

### HOP-5: Pre-Flight Validation (Scope Isolation + Structural Checks)

**Purpose:** Verify scope isolation (artist_output inaccessible), enforce structural rules before expensive QA. Fast-fail if violations present.

**Inputs:**
- `staging_buffer` from HOP-4
- Global enforcement spec (word counts, bullet counts, etc.)

**Validation Rules (18 total):**

| Rule ID | Check | Validation | Threshold |
|---------|-------|-----------|-----------|
| R5-001 | Artist output inaccessible | `'artist_output' not in dir()` | True (active check) |
| R5-002 | Master resume inaccessible | `'master_resume' not in dir()` | True (active check) |
| R5-003 | Staging buffer accessible | `staging_buffer in dir()` | True |
| R5-004 | K.1 word count in range | 118-135 words | In range |
| R5-005 | K.1 sentence count exactly 6 | Sentence count = 6 | Exactly 6 |
| R5-006 | K.1 no bullet-like formatting | No `•`, `-`, `*`, numbered lists | True |
| R5-007 | K.4 char limit ≤90 | Character count ≤ 90 | ≤90 |
| R5-008 | K.4 word limit ≤4 per segment | Each segment ≤ 4 words | ≤4 each |
| R5-009 | K.5A bullet count = 7 | Exactly 7 bullets | 7 |
| R5-010 | K.5A word count per bullet | 28-33 words per bullet | 28-33 |
| R5-011 | K.6A bullet count = 6 | Exactly 6 bullets | 6 |
| R5-012 | K.6A word count per bullet | 24-30 words per bullet | 24-30 |
| R5-013 | K.8 competency count = 6 | Exactly 6 competencies | 6 |
| R5-014 | K.8 word count per competency | 24-30 words per competency | 24-30 |
| R5-015 | K.11 skill count in range | 8-12 skills | 8-12 |
| R5-016 | K.9 paragraph word count | 85-100 words per paragraph | 85-100 |
| R5-017 | K.5B overview word count | 28-34 words | 28-34 |
| R5-018 | K.6B overview word count | 25-30 words | 25-30 |

**Output:**
- `pre_flight_results` (pass/fail for all 18 rules)
- `H5 = SHA256(pre_flight_results)`

**On Failure:** HALT immediately. No QA phase. Return early with pre-flight error report.

---

### HOP-6: Batched QA (130 Constraint Checks)

**Purpose:** Execute comprehensive QA suite: word counts, similarities, deduplication, AI detection, prose quality, industry-first compliance. Batched for efficiency.

**Inputs:**
- `staging_buffer` from HOP-4
- `clerk_scaffold` from HOP-1 (for similarity thresholds)
- `enriched_scaffold` from HOP-2 (baseline overviews)
- Global spec (thresholds, constraints)

**Validation Rules (130 total, organized by category):**

#### Category A: Word Count Compliance (20 rules)
- R6-A-001 through R6-A-020: Verify each section's word count against spec

#### Category B: Similarity & Deduplication (35 rules)
- R6-B-001 through R6-B-035:
  - K.5B cosine similarity to each K.5A bullet < 0.6
  - K.6B cosine similarity to each K.6A bullet < 0.6
  - Inter-bullet similarities (K.5A-to-K.5A, K.6A-to-K.6A) < 0.7
  - K.1-to-K.4 similarity < 0.6
  - 78-check full deduplication matrix

#### Category C: Industry-First Compliance (15 rules)
- R6-C-001 through R6-C-015:
  - Headline segment 1 contains industry keyword (not technology)
  - K.1 opening sentence contains industry + years pattern
  - K.8 competencies ranked correctly (tier-1 in positions 1-3)
  - All headline segments are industry/leadership focused

#### Category D: Prose Quality (20 rules)
- R6-D-001 through R6-D-020:
  - K.1 narrative arc (varied sentence lengths)
  - K.1 opening industry-first pattern present
  - Headline grammatical correctness
  - Overview synthesis quality (vs. bullets)

#### Category E: AI Detection Risk (15 rules)
- R6-E-001 through R6-E-015:
  - Provenance tracking (V/T/S ratios)
  - Synthetic content percentage ≤ 15%
  - Overused phrase detection
  - Authenticity scoring per section

#### Category F: Entity & Format Compliance (15 rules)
- R6-F-001 through R6-F-015:
  - Company names consistent (HOP-2 baseline)
  - Dates format MMMM YYYY
  - No hallucinated entities
  - Cover letter header/signature format
  - Bullet formatting consistency

#### Category G: Structural Integrity (10 rules)
- R6-G-001 through R6-G-010:
  - File generation not already executed
  - No circular dependencies
  - All prerequisite hops completed
  - Mutual exclusion ready (files XOR errors)

**Output:**
- `qa_results` (all 130 rules with PASS/FAIL + details)
- `H6 = SHA256(qa_results)`
- QA report sections (0-12)

**On Failure:** Collect all failures, prepare comprehensive error report. Continue to HOP-7 to execute mutual exclusion.

---

### HOP-7: Gate Decision (Mutual Exclusion)

**Purpose:** Final decision point. If all 9 hops pass (HOP-0 through HOP-6), proceed to file writes. If any hop failed, generate error report only (no files written).

**Logic:**
```
if (HOP-0 PASS && HOP-1 PASS && ... && HOP-6 PASS && HASH_CHAIN_VALID):
  → Proceed to HOP-8 (file generation)
else:
  → Generate comprehensive error report
  → Set mutual_exclusion_decision = "ERROR_REPORT_ONLY"
  → No file writes occur
```

**Inputs:**
- Cumulative pass/fail status from all prior hops
- Upstream hash verification (verify H0 → H1 → H2 → ... → H6 chain integrity)

**Validation Rules (8 total):**

| Rule ID | Check | Validation | Threshold |
|---------|-------|-----------|-----------|
| R7-001 | HOP-0 status check | HOP-0 = PASS | True |
| R7-002 | HOP-1 status check | HOP-1 = PASS | True |
| R7-003 | HOP-2 status check | HOP-2 = PASS | True |
| R7-004 | HOP-3 status check | HOP-3 = PASS | True |
| R7-005 | HOP-4 status check | HOP-4 = PASS | True |
| R7-006 | HOP-5 status check | HOP-5 = PASS | True |
| R7-007 | HOP-6 status check | HOP-6 = PASS (all 130 rules) | True |
| R7-008 | Hash chain integrity | H0 → H1 → H2 → ... → H6 unbroken | Valid chain |

**Output:**
- `gate_decision` ("PROCEED_TO_FILE_WRITE" or "GENERATE_ERROR_REPORT_ONLY")
- `H7 = SHA256(gate_decision)`
- Comprehensive error report (if applicable)

**On Failure:** Set decision to ERROR_REPORT_ONLY. Jump to error report generation.

---

### HOP-8: Render & Verify (File Write + Read-Back)

**Purpose:** Write 4 output files. Read them back. Verify hashes match staging buffer. Confirm scope isolation persists.

**Inputs:**
- `staging_buffer` from HOP-4
- `gate_decision` from HOP-7 (must be "PROCEED_TO_FILE_WRITE")

**Validation Rules (12 total):**

| Rule ID | Check | Validation | Threshold |
|---------|-------|-----------|-----------|
| R8-001 | Gate decision approved | decision = "PROCEED_TO_FILE_WRITE" | True |
| R8-002 | Resume file written | Resume_{company}_{date}.txt exists | True |
| R8-003 | Cover letter file written | CoverLetter_{company}_{date}.txt exists | True |
| R8-004 | QA report file written | QA_Report_{company}_{date}.md exists | True |
| R8-005 | App tracker file written | AppTracker_{company}_{date}.json exists | True |
| R8-006 | Resume content matches | Read-back hash = staging_buffer hash | Match |
| R8-007 | Cover letter content matches | Read-back hash = staging_buffer hash | Match |
| R8-008 | QA report content matches | Read-back hash = staging_buffer hash | Match |
| R8-009 | App tracker content matches | Read-back hash = staging_buffer hash | Match |
| R8-010 | No file corruption | All files UTF-8 readable | True |
| R8-011 | File permissions set | All files readable by user | True |
| R8-012 | Scope isolation maintained | artist_output still inaccessible | True |

**Output:**
- `render_verification_results` (all 12 rules with PASS/FAIL)
- `H8 = SHA256(render_verification_results)`
- All 4 output files (Resume, Cover Letter, QA Report, App Tracker)

**On Failure:** Delete all written files. Generate HOP-8 error report. HALT.

---

## Chain-of-Custody Ledger Specification

Each workflow run generates an immutable CoC ledger JSON file:

```json
{
  "coc_ledger": {
    "version": "v1.7.0",
    "workflow_id": "uuid_unique_per_run",
    "timestamp_start": "2025-10-15T14:30:00Z",
    "timestamp_end": "2025-10-15T14:31:30Z",
    "duration_ms": 90000,
    "hops": [
      {
        "hop_id": 0,
        "hop_name": "Source Integrity",
        "status": "PASS",
        "timestamp": "2025-10-15T14:30:05Z",
        "duration_ms": 245,
        "input_hash": null,
        "output_hash": "H0_value_256_hex",
        "rules_total": 15,
        "rules_passed": 15,
        "rules_failed": 0,
        "rules_detail": [
          {
            "rule_id": "R0-001",
            "rule_name": "File exists",
            "status": "PASS",
            "detail": "master_resume exists at /path/to/file"
          },
          // ... all 15 rules
        ],
        "errors": []
      },
      {
        "hop_id": 1,
        "hop_name": "Clerk Extraction",
        "status": "PASS",
        "timestamp": "2025-10-15T14:30:10Z",
        "duration_ms": 1200,
        "input_hash": "H0_value_256_hex",
        "output_hash": "H1_value_256_hex",
        "rules_total": 18,
        "rules_passed": 18,
        "rules_failed": 0,
        "rules_detail": [
          // ... 18 rules
        ],
        "hallucination_flags": [
          {
            "entity": "Company X",
            "confidence": 0.82,
            "status": "VERIFIED_IN_WHITELIST"
          }
        ],
        "errors": []
      },
      // ... HOP-2 through HOP-8
    ],
    "chain_integrity": {
      "status": "VALID",
      "all_hops_passed": true,
      "hash_chain_verified": true,
      "verification_details": {
        "H0_input": null,
        "H0_output": "...",
        "H1_input": "H0_output",
        "H1_output": "...",
        // ... full chain
        "H8_output": "..."
      }
    },
    "final_decision": "PROCEED_TO_FILE_WRITE",
    "output_files": [
      "Resume_company_date.txt",
      "CoverLetter_company_date.txt",
      "QA_Report_company_date.md",
      "AppTracker_company_date.json"
    ],
    "critical_flags": [],
    "summary": "All 9 hops passed. 181/181 rules validated. Hash chain intact. Files written and verified."
  }
}
```

---

## 130 Validation Rules: Complete List

### Summary by Hop

| Hop | Name | Rule Count | Rule IDs |
|-----|------|-----------|----------|
| HOP-0 | Source Integrity | 15 | R0-001 to R0-015 |
| HOP-1 | Clerk Extraction | 18 | R1-001 to R1-018 |
| HOP-2 | Data Enrichment | 14 | R2-001 to R2-014 |
| HOP-3 | Artist Generation | 20 | R3-001 to R3-020 |
| HOP-4 | Staging Buffer | 16 | R4-001 to R4-016 |
| HOP-5 | Pre-Flight | 18 | R5-001 to R5-018 |
| HOP-6 | Batched QA | 130* | R6-A-001 to R6-G-010 |
| HOP-7 | Gate Decision | 8 | R7-001 to R7-008 |
| HOP-8 | Render & Verify | 12 | R8-001 to R8-012 |
| **TOTAL** | | **181 rules** | |

*HOP-6 contains 130 rules organized in 7 categories (A-G). Total across all hops: 181 rules.

---

## Cryptographic Checksums: Hash Chain

Each hop's output is hashed using SHA-256:

```
H0 = SHA256(source_scaffold)
H1 = SHA256(clerk_scaffold) + input_hash=H0
H2 = SHA256(enriched_scaffold) + input_hash=H1
H3 = SHA256(artist_output) + input_hash=H2
H4 = SHA256(staging_buffer) + input_hash=H3
H5 = SHA256(pre_flight_results) + input_hash=H4
H6 = SHA256(qa_results) + input_hash=H5
H7 = SHA256(gate_decision) + input_hash=H6
H8 = SHA256(render_verification_results) + input_hash=H7
```

**Verification:** Each hop verifies that its input hash matches the previous hop's output hash. If any mismatch detected, HALT immediately with hash chain error.

---

## Error Handling & Recovery

### Scenario 1: HOP-N Fails

**Action:**
1. Capture all rule-by-rule failures
2. Record error details (which rules failed, actual vs. expected values)
3. Log error to CoC ledger
4. Set hop status to FAIL
5. Continue to HOP-7 for mutual exclusion decision

### Scenario 2: Hash Chain Breaks

**Action:**
1. Detected at hop N (input_hash != previous output_hash)
2. Flag as "UPSTREAM_MUTATION_DETECTED"
3. Halt immediately
4. Do not proceed downstream
5. Generate error report with mutation details

### Scenario 3: Scope Isolation Violated

**Action:**
1. Detected at HOP-5 (active check: `'artist_output' in dir()`)
2. Halt immediately
3. Do not proceed to HOP-6, HOP-7, HOP-8
4. Generate critical error: "SCOPE_ISOLATION_VIOLATION"

### Scenario 4: File Write Fails (HOP-8)

**Action:**
1. File write error detected
2. Delete all partially written files
3. Do not proceed further
4. Generate HOP-8 error report
5. User must diagnose and retry

---

## Backward Compatibility

**V1.7.0 vs. V1.6.9:**

| Aspect | V1.6.9 | V1.7.0 | Compat? |
|--------|--------|--------|--------|
| 3-phase pipeline (Clerk/Artist/Assembler) | ✓ | ✓ (embedded in hops) | ✓ |
| Staging buffer scope isolation | ✓ | ✓ (HOP-4 + HOP-5) | ✓ |
| 184 validation tests | ✓ | 181 rules in hops (expanded) | ✓ |
| 13-section QA report | ✓ | ✓ (HOP-6 generates) | ✓ |
| 4-file output | ✓ | ✓ (HOP-8 writes) | ✓ |
| Headline ≤90 chars | ✓ | ✓ (HOP-5 R5-007) | ✓ |
| K.5A=7, K.6A=6 bullets | ✓ | ✓ (HOP-5 R5-009/011) | ✓ |
| K.1=6 sentences | ✓ | ✓ (HOP-5 R5-005) | ✓ |
| **New in V1.7.0:** | | |
| 9-hop traceability | - | ✓ | N/A |
| Cryptographic hash chain | - | ✓ | N/A |
| CoC ledger file | - | ✓ | N/A |
| Entity whitelists at HOP-1/3 | - | ✓ | N/A |
| Upstream hash verification | - | ✓ | N/A |
| Active scope isolation check | - | ✓ (HOP-5 R5-001/002) | N/A |

**Migration Path:** V1.6.9 workflows can be upgraded to V1.7.0 without code changes. CoC ledger is an *additional* output file.

---

## Implementation Roadmap

### Phase 1: Core Hop Execution (Week 1)
- [ ] Implement HOP-0 through HOP-4 (source → staging buffer)
- [ ] Implement hash calculation and chaining logic
- [ ] Unit tests for each hop

### Phase 2: Validation Gates (Week 2)
- [ ] Implement HOP-5 (pre-flight, scope isolation checks)
- [ ] Implement HOP-6 (130 batched QA rules)
- [ ] Integration tests

### Phase 3: Gate & Render (Week 3)
- [ ] Implement HOP-7 (mutual exclusion)
- [ ] Implement HOP-8 (file write + read-back)
- [ ] CoC ledger generation

### Phase 4: Testing & Hardening (Week 4)
- [ ] End-to-end testing (all 9 hops)
- [ ] Hash chain mutation injection testing
- [ ] Scope isolation violation injection testing
- [ ] Error recovery testing
- [ ] Performance benchmarking

---

## Testing Strategy

### Test Categories

| Category | Count | Examples |
|----------|-------|----------|
| Hop-by-hop unit tests | 9 × 15 = 135 | HOP-0 R0-001, HOP-1 R1-001, etc. |
| Hash chain integrity | 20 | Upstream hash mismatch detection |
| Scope isolation | 10 | Artist_output inaccessibility checks |
| Mutation detection | 15 | Inject corruption at each hop |
| Integration (full pipeline) | 50 | End-to-end scenarios |
| Error recovery | 20 | Fail at each hop, verify rollback |
| **TOTAL** | **250+** | |

### Critical Test Cases

1. **HOP-0 Failure:** Resume file missing → Expect HALT before HOP-1
2. **HOP-1 Hallucination:** Hallucinated company in extracted data → Caught at R1-011
3. **HOP-3 Word Count Violation:** K.1 generates 136 words (exceeds 135) → Caught at HOP-5 R5-004
4. **HOP-4 Tokenization Mismatch:** Word count doesn't match len(text.split()) → Caught at R4-003
5. **HOP-5 Scope Isolation Check:** artist_output still in dir() → HALT with critical error
6. **HOP-6 Deduplication Failure:** K.5A bullet cosine > 0.7 → QA fails, no files written
7. **HOP-8 File Corruption:** Written file doesn't match staging_buffer hash → Delete file, generate error

---

## Comparison to LIC Framework

| Aspect | LIC | v1.7.0 |
|--------|-----|--------|
| Hop count | 9 | 9 |
| Validation rules | 130+ | 181 |
| Hash chain | ✓ | ✓ |
| Entity whitelists | ✓ | ✓ (HOP-1, HOP-3) |
| Upstream verification | ✓ | ✓ |
| Scope isolation checks | ✓ | ✓ (active check at HOP-5) |
| Mutual exclusion | ✓ | ✓ (HOP-7) |
| **Differences:** | | |
| Integration with existing 3-phase pipeline | Standalone | Embedded in hops (backward compatible) |
| CoC ledger format | Reference | Fully specified JSON schema |
| Error recovery | Generic | Hop-specific recovery procedures |

---

## Security & Integrity Properties

1. **Non-repudiation:** Every transformation captured in CoC ledger with timestamp
2. **Immutability:** Hash chain prevents undetected backflow mutations
3. **Traceability:** Complete audit trail from source to target
4. **Scope isolation:** Active verification that artist_output inaccessible during validation
5. **Mutual exclusion:** Files written XOR error report generated (never both, never neither)
6. **Determinism:** All validation rules are deterministic (no randomness)

---

## Conclusion

V1.7.0 multi-hop QA framework transforms Job Workflow from a 3-phase pipeline into a **9-checkpoint cryptographically hardened system** with complete end-to-end traceability. The 181 validation rules, hash chain, and CoC ledger eliminate the validation gaps between source and target, ensuring that no silent data corruption occurs at intermediate stages.

**Key Innovation:** The framework answers the core question: "Where could data corruption happen between source and target?" and installs a cryptographic checkpoint at every transformation boundary.


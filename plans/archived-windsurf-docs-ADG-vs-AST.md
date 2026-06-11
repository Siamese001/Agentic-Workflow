---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\ADG vs AST.md'
original_relative_path: 'ADG vs AST.md'
source_sha256: 0967f26f90403cf8b0650f17f6cd40025a8687a069bd0da761497887bc787596
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-25'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
+-----------------------------------------------------------------------------------+
|                         The Library (Target Codebase)                             |
|             (e.g., test_heal_telemetry.py, __init__.py, core_logic.py)            |
+-----------------------------------------+-----------------------------------------+
                                          |
              +---------------------------+---------------------------+
              |                                                       |
+-------------v--------------+                          +-------------v--------------+
|   Cataloging / ADG Persona |                          |  Execution / AST Persona   |
|      (Macro-Topology)      |                          |     (Micro-Semantics)      |
+----------------------------+                          +----------------------------+
| HIGH SIGNAL (The Index):   |                          | HIGH SIGNAL (The Reader):  |
| - Static import edges      |                          | - Live node evaluation     |
| - Cross-file dependencies  |                          | - Explicit FunctionDefs    |
| - Fast blast-radius scope  |                          | - Ground-truth structural  |
|                            |                          |   state of the file        |
| HIGH NOISE (The Flaws):    |                          |                            |
| - Blind to dynamic runtime |                          | HIGH NOISE-CANCELING:      |
|   executions/fixtures      |                          | - Bypasses dynamic mock    |
| - Flags structural markers |                          |   and fixture illusions    |
|   (__init__.py) as nodes   |                          | - Automatically filters    |
| - Vulnerable to cache      |                          |   out empty/import-only    |
|   drift and staleness      |                          |   files dynamically        |
+-------------+--------------+                          +-------------+--------------+
              |                                                       |
              | (Batch of Suspect Files)                              | (Node metadata)
              |                                                       |
+-------------v-------------------------------------------------------v-------------+
|                Governance / L5 Reconciliation Board (System Bus)                  |
|                                                                                   |
|  1. RECEIVE suspect file batch from Cataloging Persona.                           |
|  2. IF filename == '__init__.py', DISCARD (Filters Catalog structural noise).     |
|  3. TRIGGER Execution Persona on remaining files (Strict Authority Boundary).     |
|  4. IF Execution finds > 0 `ast.FunctionDef` matching 'test_*',                   |
|     OVERRIDE Catalog "import-only" flag -> Mark as "Behavioral Test".             |
|     (Corrects dynamic-execution blind spot via Single Mutation Authority).        |
|  5. IF Execution finds 0 test methods AND file is not an init,                    |
|     CONFIRM as legitimate target for enhancement.                                 |
|                                                                                   |
|  * All overrides and confirmations are logged for full auditability (Receipts).   |
+-----------------------------------------+-----------------------------------------+
                                          |
                            +-------------v-------------+
                            |       Ground Truth        |
                            |   (The True Target Files) |
                            +---------------------------+

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---


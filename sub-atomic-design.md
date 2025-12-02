
---

# **Agentic-Workflow — Phases 1–4 Consolidated Design Document**

---

# **PHASE 1 — STRUCTURAL ENFORCEMENT (SINGLE SOURCE OF TRUTH)**

### **One-sentence definition**

Phase 1 guarantees the repo’s physical directory tree is a perfect, byte-for-byte structural match to the YAML SSoT, with auto-repair and strict YAML-vs-YAML validation.

### **Purpose**

Create a deterministic filesystem that matches the Subatomic Architecture exactly before any content merge, history carry-over, or semantic mutation.

### **Objective**

Generate the tree from YAML → Snapshot the real tree → Canonicalize both → Diff → Overwrite if mismatch → Repeat until identical.

### **Key Actions**

* Load YAML SSoT
* Generate full directory tree
* Snapshot disk tree
* Canonical format both YAMLs
* Strict diff (0 lines == pass)
* Auto-repair by full regeneration
* Re-diff until clean

### **Completion Criteria**

| Key | Description                 |
| --- | --------------------------- |
| 1.1 | YAML SSoT parsed            |
| 1.2 | Tree generated              |
| 1.3 | Actual snapshot created     |
| 1.4 | YAMLs match exactly         |
| 1.5 | No extra files/folders      |
| 1.6 | Depth rules satisfied       |
| 1.7 | Auto-repair clean           |
| 1.8 | Zero-loss ready for Phase 2 |

---

# **PHASE 2 — ZERO-LOSS HISTORICAL MERGE (CONTENT RECONSTRUCTION)**

### **One-sentence definition**

Phase 2 merges all historical code/content from old branches, archives, and semantic caches into the Phase-1-verified directory structure with zero loss and strict placement rules.

### **Purpose**

Repopulate the freshly rebuilt tree with *all valid historical content*, reconstructed into the new Subatomic structure exactly where it belongs.

### **Objective**

Extract old code → Map to new structural locations → Inject content without altering structure → Ensure all legacy capabilities survive unchanged.

### **Key Actions**

* Load all historical sources (v10_7 → v10_11, archives, LIC, RG, etc.)
* Build a “content map” mapping old paths to new Subatomic paths
* Enforce: **no structural changes allowed** (Phase 1 owns structure)
* Move files into correct L1–L5 layers
* Auto-resolve collisions deterministically (SSoT rules)
* Verify every historical capability is present in the new tree
* Generate “Phase-2 content manifest” for traceability

### **Completion Criteria**

| Key | Description                                                |
| --- | ---------------------------------------------------------- |
| 2.1 | All legacy files identified                                |
| 2.2 | All files mapped to proper Subatomic paths                 |
| 2.3 | All content integrated with zero loss                      |
| 2.4 | No file breaks structure rules created in Phase 1          |
| 2.5 | Content manifest generated                                 |
| 2.6 | Imports smoke-testable (structure-only, no deep execution) |

### **Downstream Link**

Phase 3 depends on Phase 2’s fully reconstructed codebase for mutation, refactoring, and semantic upgrades.

---

# **PHASE 3 — SEMANTIC REWRITE & MUTATION (SMART REGENERATION)**

### **One-sentence definition**

Phase 3 semantically mutates the historical codebase using AI-assisted reconstruction, pattern rewriting, and cross-version semantic caching—while preserving exact execution semantics.

### **Purpose**

Convert legacy, inconsistent, or outdated code into clean Subatomic-compliant, atomic, layer-pure code using structured mutation rules.

### **Objective**

Parse → Analyze → Mutate → Regenerate → Validate semantics equivalence.

### **Key Actions**

* Load the semantic cache
* Compare each file with known patterns (L1 planners, L2 executors, L3 orchestrators, etc.)
* Identify violations: mixing layers, monolithic functions, cross-imports
* Rewrite into atomic units:

  * L1 = pure planning
  * L2 = execution only
  * L3 = orchestration
  * L4 = state
  * L5 = safety
* Apply multi-pass semantic upgrades:

  * fragmentation → atomic functions
  * strict dependency ordering
  * deterministic dataflows
* Mutate content to match SSoT code style and abstractions
* Validate semantic equivalence via unit transcript comparison

### **Completion Criteria**

| Key | Description                              |
| --- | ---------------------------------------- |
| 3.1 | All files parsed and analyzed            |
| 3.2 | Layer violations identified and resolved |
| 3.3 | Semantic caching applied                 |
| 3.4 | Atomicity rules enforced universally     |
| 3.5 | Semantic equivalence validated           |
| 3.6 | No new structural changes introduced     |
| 3.7 | Codebase ready for Phase 4 validation    |

### **Downstream Link**

Phase 4 assumes Phase 3 has produced a fully cleaned, atomic, L1–L5 layered codebase.

---

# **PHASE 4 — FULL VALIDATION (TESTS, IMPORTS, LINT, TYPES, SAFETY)**

### **One-sentence definition**

Phase 4 performs full-system validation: imports, pytest, ruff, mypy, safety rules, and architecture invariants; phase passes only when **everything** is green.

### **Purpose**

Guarantee the regenerated Subatomic codebase is:

* executable
* correct
* type-safe
* import-clean
* lint-clean
* structurally compliant
* safety-compliant

### **Objective**

Run every validator and fix violations until the codebase is production-grade.

### **Key Actions**

* Import graph smoke test
* Execute pytest end-to-end
* Run ruff lint (zero errors allowed)
* Run mypy type checker
* Enforce atomic layering:

  * L1 cannot import L2 or agents
  * L3 can import L1 and L2 but not vice versa
  * No cycles
* Validate safety:

  * policy boundaries
  * correct enforcement paths
* Validate prompt governance correctness
* Validate observability compliance
* Validate deterministic DAG orchestration

### **Completion Criteria**

| Key | Description                                             |
| --- | ------------------------------------------------------- |
| 4.1 | All imports succeed                                     |
| 4.2 | Pytest: 0 failures                                      |
| 4.3 | Ruff: 0 errors                                          |
| 4.4 | Mypy: 0 blockers                                        |
| 4.5 | No cyclic imports                                       |
| 4.6 | All L1–L5 boundaries intact                             |
| 4.7 | RAG, orchestration, and agents behave deterministically |
| 4.8 | Safety policies validated                               |
| 4.9 | All regressions resolved                                |

### **Downstream Link**

After Phase 4: codebase is **deployment-ready**; Phase 5+ can layer optimization, cost controls, AIS, or meta-learning.

---

# **Consolidated View (Phases 1–4)**

| Phase | Intent                   | Output                                                 |
| ----- | ------------------------ | ------------------------------------------------------ |
| **1** | Enforce structure        | Perfect SSoT tree                                      |
| **2** | Merge historical content | Zero-loss reconstructed codebase                       |
| **3** | Upgrade semantics        | Clean atomic subatomic architecture                    |
| **4** | Validate correctness     | Production-grade, import/lint/test/type clean codebase |

---

If you want, I can now:

* Generate the **official Windsurf execution prompt** for all four phases
* Expand each phase into a full implementation spec
* Produce the Phase-1/Phase-2/Phase-3/Phase-4 Python framework scaffolds

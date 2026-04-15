# Agentic Requirements Registry — Specification

**Version**: 1.0 · **Status**: Design · **Date**: 2026-07
**Companion**: `docs/requirements/agentic_source_authority_model.md`

---

## 1. Registry Format Decision

**Selected format**: YAML (one file per requirement, directory-based registry)

**Justification**:

| Criterion | YAML | JSON | Markdown + frontmatter |
|-----------|------|------|----------------------|
| Human-readable | ✅ | partial | ✅ |
| Multi-line requirement_statement | ✅ (literal block `\|`) | awkward | mixed (body vs frontmatter) |
| Programmatic validation | ✅ (jsonschema via PyYAML) | ✅ | ❌ (body is unstructured) |
| Git diff clarity | ✅ (line-based) | partial | partial |
| All fields first-class | ✅ | ✅ | ❌ (body escapes schema) |
| Key ordering stability | ✅ (`sort_keys=True`) | ✅ | ❌ |

YAML wins on multi-line readability + full structural validation. JSON is rejected because `requirement_statement` needs human authoring of multi-line prose.

**Registry location**: `docs/requirements/registry/<domain>/<requirement_id>.yaml`

---

## 2. Requirement Registry Schema

Every requirement file MUST conform to the following schema exactly.
All fields are mandatory unless marked `# optional`.

```yaml
# ── Identity ──────────────────────────────────────────────────────────────────
requirement_id: "AGEN-XXXX"          # format: AGEN-{4-digit zero-padded int}
domain: ""                           # query class: policy | best_practice | tool_contracts |
                                     #   architecture_pattern | normative_req | repo_gap |
                                     #   implementation | internal_arch
title: ""                            # ≤120 characters, imperative verb phrase

# ── Normative content ─────────────────────────────────────────────────────────
requirement_statement: |             # RFC 2119 MUST/SHOULD/MAY phrasing
  ...
rationale: |                         # why this requirement exists; cite evidence
  ...
normative_level: ""                  # MUST | SHOULD | MAY | MUST NOT | SHOULD NOT

# ── Source provenance (enforced by validity gate) ──────────────────────────────
source_collection: ""                # "curated_agent_docs" | "arch_docs" | "ext_knowledge"
source_doc: ""                       # relative path or URL of the source document
source_type: ""                      # "web" | "local"
authority_tier: ""                   # T1_vendor | T2_standard | T3_guidance |
                                     #   T4_repo_canonical | T4_implementation_evidence
normative_scope: ""                  # "external_authority" | "repo_internal" | "evidence_only"
invalid_for_normative_use: false     # MUST be false for any published requirement

# ── Linked evidence ───────────────────────────────────────────────────────────
linked_chunk_ids:                    # ChromaDB chunk IDs that ground this requirement
  - ""
topic_tags:                          # ≤6 lowercase kebab-case tags
  - ""

# ── Validation ────────────────────────────────────────────────────────────────
validation_eval_expectation: |       # # optional: expected retrieval behavior in eval harness
  ...
repo_mapping_notes: |                # optional: where/whether this is already implemented in repo
  ...

# ── Lifecycle ─────────────────────────────────────────────────────────────────
status: "draft"                      # draft | active | deprecated | superseded
last_verified: ""                    # YYYY-MM
superseded_by: ""                    # optional: requirement_id that replaces this one
```

---

## 3. Hard Validity Rules

These rules are machine-enforceable. Any requirement violating them is **invalid** and MUST NOT be published or used to drive implementation.

### Rule V-1 — arch_docs source is permanently invalid
```
if requirement.source_collection == "arch_docs":
    INVALID — reason: "arch_docs is implementation-evidence only"
```

### Rule V-2 — T4 implementation evidence is permanently invalid
```
if requirement.authority_tier == "T4_implementation_evidence":
    INVALID — reason: "T4_implementation_evidence cannot generate normative requirements"
```

### Rule V-3 — evidence_only normative_scope is invalid
```
if requirement.normative_scope == "evidence_only":
    INVALID — reason: "evidence_only scope cannot produce requirements"
```

### Rule V-4 — invalid_for_normative_use must be false
```
if requirement.invalid_for_normative_use == True:
    INVALID — reason: "chunk explicitly marked invalid for normative use"
```

### Rule V-5 — repo_internal scope cannot assert universal MUST
```
if requirement.normative_scope == "repo_internal" and requirement.normative_level == "MUST":
    WARNING — reason: "repo_internal scope MUST requirements are repo-binding only,
                       not universal agentic design authority"
    # does not invalidate; consumer must annotate universal vs repo scope
```

### Rule V-6 — MUST NOT emit from empty or arch_docs-only bundle
```
if evidence_bundle.all_chunks_invalid_for_normative_use():
    BLOCK — do not emit requirement artifact
    emit signal: LOW_NORMATIVE_COVERAGE
```

### Validity gate summary

| Check | Result |
|-------|--------|
| `source_collection == "arch_docs"` | ❌ INVALID |
| `authority_tier == "T4_implementation_evidence"` | ❌ INVALID |
| `normative_scope == "evidence_only"` | ❌ INVALID |
| `invalid_for_normative_use == True` | ❌ INVALID |
| `normative_scope == "repo_internal"` + `normative_level == "MUST"` | ⚠️ WARNING |
| All of the above pass | ✅ VALID |

---

## 4. Evidence-Shaping Normative Filter Contract

### Gate function: `filter_normative_sources()`

**Location**: `agentic_core/L3_orchestration/reasoning/engines/evidence_shaper.py`

**Signature** (design, not implementation):
```python
def filter_normative_sources(
    results: list[HybridSearchResult],
    allowed_collections: tuple[str, ...] = ("curated_agent_docs",),
    allowed_tiers: tuple[str, ...] = (
        "T1_vendor", "T2_standard", "T3_guidance", "T4_repo_canonical"
    ),
) -> tuple[list[HybridSearchResult], list[HybridSearchResult]]:
    """Return (accepted, rejected) partitioned by normative allowlist.

    A chunk is accepted if ALL of the following hold:
      1. metadata["source_collection"] in allowed_collections
      2. metadata["authority_tier"] in allowed_tiers
      3. metadata["invalid_for_normative_use"] is False (or absent → default True = reject)
    """
```

**Gate behavior**:
- `accepted`: chunks eligible for normative requirement generation
- `rejected`: chunks that may still be used for repo-gap analysis, not for requirements
- If `accepted` is empty: return `([], rejected)` and emit `LOW_NORMATIVE_COVERAGE` signal
- **Never fall back to rejected chunks** for normative use

### Gate placement

```
HybridSearchEngine.search()
    -> ranked_chunks (raw, may contain any collection)
    -> [GATE: filter_normative_sources() — for normative/policy/best_practice calls]
    -> accepted_chunks
    -> EvidenceBundle(ranked_chunks=accepted_chunks, ...)
    -> CitationAnchor construction (collection from chunk metadata["source_collection"])
    -> requirement generation
```

The gate MUST be applied **before** `CitationAnchor` construction when the calling context is any of:
`normative_req`, `policy`, `best_practice`, `tool_contracts`, `architecture_pattern`.

It MUST NOT be applied for: `repo_gap`, `implementation`, `internal_arch` — those may use arch_docs.

### CitationAnchor provenance fix

`CitationAnchor.collection` MUST be populated from `chunk.metadata["source_collection"]`, not from the routing-level `EvidenceBundle.collection`. This makes per-chunk provenance self-describing and independent of routing correctness.

```python
# Current (routing-dependent, fragile):
anchor = CitationAnchor(collection=evidence_bundle.collection, ...)

# Required (chunk-derived, self-describing):
anchor = CitationAnchor(
    collection=chunk.metadata.get("source_collection", "unknown"),
    ...
)
```

---

## 5. Example Requirement Entry

```yaml
requirement_id: "AGEN-0001"
domain: "policy"
title: "Agents MUST enforce constitutional hard constraints before any tool execution"

requirement_statement: |
  An agentic system MUST evaluate all active constitutional constraints before
  dispatching any tool call or external action. Constraints classified as
  safety-critical (guardian-level) MUST block execution if violated, with no
  fallback path that bypasses the evaluation.

rationale: |
  Constitutional constraints define the non-negotiable behavioral envelope of
  an autonomous agent. Evaluating them post-dispatch creates a race condition
  between agent action and safety enforcement. Pre-dispatch evaluation is the
  only pattern consistent with bounded autonomy (L2) and write-gate guarantees.

normative_level: "MUST"

source_collection: "curated_agent_docs"
source_doc: "docs/rules/constitutional.md"
source_type: "local"
authority_tier: "T4_repo_canonical"
normative_scope: "repo_internal"
invalid_for_normative_use: false

linked_chunk_ids:
  - "a1b2c3d4e5f6"
  - "f6e5d4c3b2a1"

topic_tags:
  - "policy"
  - "constitutional"
  - "safety"
  - "tool-execution"

validation_eval_expectation: |
  Query "constitutional constraints for agent behavior" must return this chunk
  in top-3 from curated_agent_docs. Must not return any arch_docs chunk
  as the winner.

repo_mapping_notes: |
  Currently enforced via .windsurf/rules/constitutional.md and
  ops_scripts/ci/run_contract_gates.py. Structural check: guardian_exemption_gate.py.

status: "active"
last_verified: "2026-07"
superseded_by: ""
```

---

## 6. Registry Directory Structure

```
docs/requirements/
├── agentic_source_authority_model.md     ← authority tier + allowlist model
├── agentic_requirements_registry_spec.md ← this document
└── registry/
    ├── policy/
    │   ├── AGEN-0001.yaml               ← constitutional constraints
    │   ├── AGEN-0002.yaml               ← safety boundary enforcement
    │   └── ...
    ├── best_practice/
    │   ├── AGEN-0050.yaml
    │   └── ...
    ├── tool_contracts/
    │   ├── AGEN-0100.yaml
    │   └── ...
    ├── architecture_pattern/
    │   ├── AGEN-0150.yaml
    │   └── ...
    └── repo_gap/
        ├── AGEN-0200.yaml               ← arch_docs allowed as source here
        └── ...
```

Only `repo_gap/` and `implementation/` subdirectories allow `source_collection: "arch_docs"`.
All other subdirectories reject arch_docs at the validity gate.

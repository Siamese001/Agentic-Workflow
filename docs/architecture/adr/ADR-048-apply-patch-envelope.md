# ADR-048 — Apply-Patch Multi-File Envelope Format

**Status**: Accepted

| Field | Value |
|---|---|
| **Status** | Accepted |
| **Decision Date** | 2026-04-24 |
| **Deciders** | Author (Author-Gate 2026-04-24, 3 questions resolved) |
| **Supersedes** | — |
| **Related** | ADR-023 (runtime HITL), ADR-024 (SURFACE_OVERRIDE), constitutional §4 (UWG write authority) |
| **Wave** | W14.a (post-Wave-10 roadmap, plan `post-wave10-roadmap-a1e7f2`) |
| **Impact Layers** | L2_execution, L4_state (UWG), L5_safety (write guards) |

## Context

Wave 10 backlog triage surfaced **EQ-12b.1 — Apply-patch multi-file batching** as genuine new T2 work: zero `apply_patch` / `multi_file_batch` / `batch_apply` infrastructure exists in the repo. Today, every code-edit operation Codex or any agent issues is a single-file `edit` / `multi_edit` call with no transactional grouping across files.

Three failure modes motivate a multi-file envelope:

1. **Cross-file refactor atomicity** — renaming a symbol that lives in file A and is imported by files B…N requires either all changes to land or none to land. Today: partial application leaves the working tree broken between calls.
2. **Author-Gate scope visibility** — Codex currently presents a wall of edits that the user cannot inspect as a single change-set before approval. A patch envelope is the natural artifact for one-shot review.
3. **Replayability and audit** — without a structured envelope, re-running an edit sequence (e.g., after a rebase) requires re-running the full LLM turn. A persisted envelope is replayable.

## Decision Drivers

- **Standards alignment**: Existing tools (Aider, legacy editor, Anthropic's `apply_patch`, OpenAI Codex CLI) have converged on a small family of envelope formats. Inventing a fourth would be a net cost.
- **Tooling compatibility**: GitHub PR view, `git apply`, IDE diff renderers — these all understand unified diff. JSON Patch (RFC 6902) is structured but only well-suited to JSON/YAML data, not source files.
- **Anchor robustness**: Line-number-based patches break on any upstream edit. Anchor-based (before/after context) patches survive minor drift.
- **UWG integration**: All file writes MUST flow through `agentic_core/L4_state/utils/write_gateway.py` (`write_gateway` SSOT). The envelope executor must call UWG, not bypass it.
- **Rollback**: Mid-batch failure must restore every file touched in the same batch.

## Options Considered

### Option 1 — Unified diff (`git apply`-compatible)

```diff
--- a/agentic_core/L0_routing/foo.py
+++ b/agentic_core/L0_routing/foo.py
@@ -42,3 +42,5 @@
 def existing():
     pass
+
+def added():
+    return 42
```

**Pros**: Universal toolchain support; renders natively in GH/IDEs; `git apply --check` validates pre-commit; well-defined semantics.
**Cons**: Line-number-anchored — fragile under concurrent edits; no native multi-file rollback; verbose for large insertions; needs context lines that LLMs sometimes truncate.
**Score (1-5)**: tooling 5 · robustness 2 · LLM-friendliness 2 · UWG fit 3 · rollback 2 = **14/25**

### Option 2 — JSON Patch (RFC 6902)

```json
{"op": "replace", "path": "/agentic_core/L0_routing/foo.py#L42", "value": "..."}
```

**Pros**: Strict schema; trivial to validate; well-supported in Python (`jsonpatch` lib).
**Cons**: Designed for JSON documents, not text files; awkward path syntax for line ranges; no native context-anchor concept; loses readability advantage.
**Score (1-5)**: tooling 2 · robustness 2 · LLM-friendliness 2 · UWG fit 3 · rollback 3 = **12/25**

### Option 3 — Anthropic `apply_patch` envelope (anchor-based, custom)

```
*** Begin Patch
*** Update File: agentic_core/L0_routing/foo.py
@@ def existing():
     pass
+
+def added():
+    return 42
*** End Patch
```

Per-file blocks delimited by `*** Update File:` / `*** Add File:` / `*** Delete File:`. Within each block, hunks anchored by the **`@@` symbol-context line** (the nearest enclosing function/class signature) — not line numbers. Lines prefixed `+` are added, `-` are removed, unprefixed are context.

**Pros**: Anchor-based — survives upstream drift; battle-tested in Anthropic's own apply_patch tool (Claude Code, Sonnet 4.5); LLM-friendly format; natural multi-file boundary; explicit Add/Update/Delete operations; envelope is a single string (easy to persist + replay); Python parser is ~150 LOC.
**Cons**: Non-standard outside Anthropic ecosystem; no native `git apply` interop (must implement parser); requires per-file rollback discipline in executor.
**Score (1-5)**: tooling 3 · robustness 5 · LLM-friendliness 5 · UWG fit 4 · rollback 4 = **21/25**

### Option 4 — Aider-style SEARCH/REPLACE blocks

```
agentic_core/L0_routing/foo.py
<<<<<<< SEARCH
def existing():
    pass
=======
def existing():
    pass

def added():
    return 42
>>>>>>> REPLACE
```

**Pros**: Maximum LLM-friendliness; widely adopted by Aider users; very simple parser.
**Cons**: No multi-file envelope (each block is independent); no Add/Delete-file primitive; no atomicity guarantee in the format itself; ambiguous on whitespace; no schema.
**Score (1-5)**: tooling 2 · robustness 3 · LLM-friendliness 5 · UWG fit 2 · rollback 1 = **13/25**

## Decision (Recommended)

**Adopt Option 3 — Anthropic apply_patch envelope** as the canonical multi-file patch format.

Rationale:
1. **Already proven** at Anthropic-scale on Claude Code/Sonnet 4.5; the format has survived 18+ months of production use.
2. **Anchor-based hunks** are demonstrably more robust than line-number patches for LLM-generated edits where intervening edits often happen between generation and apply.
3. **Native multi-file boundary** matches our atomicity requirement — one envelope = one transaction.
4. **LLM friendliness** matters more than `git apply` interop here, because the producer is always an LLM and the consumer is always our executor (not a human running `git apply` by hand).
5. **Persisted envelope** is naturally replayable and naturally fits an audit ledger row.

## Consequences

### Positive

- Single SSOT format for all multi-file edits across Codex, harness scripts, and agent-issued refactors.
- Audit trail: every applied envelope persists to `artifacts/apply_patch/<sha>.patch` with timestamp, author, and outcome.
- Future-proofs Wave 14.b/c: parser, validator, and UWG-integrated executor have a stable contract to build against.

### Negative

- ~150 LOC of net-new parser + ~100 LOC executor + ~50 LOC rollback — non-trivial first delivery.
- Needs a CI gate to ensure NO direct `Path.write_text` / `open(..., 'w')` bypass once the envelope path lands.
- Loses GH PR diff rendering — partially mitigated by `apply_patch_to_unified_diff.py` companion converter (deferred to W14.c).

### Neutral

- Existing single-file `edit` / `multi_edit` tools continue to work — the envelope is additive, not replacement. Author-Gate decides per-task whether to use envelope or direct edit.

## Implementation Plan (W14.b + W14.c outline)

1. **W14.b — Parser + validator** (`agentic_core/L2_execution/writers/patch_envelope.py`, ~4k tokens)
   - `parse_envelope(text: str) -> EnvelopeAST`
   - `validate_envelope(ast: EnvelopeAST, working_tree: Path) -> list[ValidationError]` (anchor matches exist, no conflicting hunks, no path traversal)
   - Pure function; no I/O.

2. **W14.c — Executor + rollback + tests** (~4k tokens)
   - `apply_envelope(ast: EnvelopeAST, *, dry_run: bool = False) -> ApplyResult`
   - All file writes through `write_gateway.write_text()` — UWG-mediated.
   - Pre-write snapshot → restore on any failure.
   - ≥10 tests: happy path, mid-batch failure rollback, anchor-mismatch detection, Add+Update+Delete in one envelope, idempotency replay, path-traversal rejection.
   - CI gate: `check_no_persistent_write_bypass.py` — staged `*.py` files importing `pathlib.Path.write_text` or `open(..., 'w')` outside the allowed-list trigger a block.

## Resolved Decisions (Author-Gate 2026-04-24)

1. **Conflict resolution policy** — **Fail loudly**. Validator detects any anchor mismatch or content-hash drift on ANY file in envelope BEFORE writing first byte → abort entire batch. No three-way merge. (confidence 0.88, gap 0.43)
2. **Maximum envelope size** — **50 files / 200 hunks per envelope**, configurable via `config/apply_patch.yaml::max_files` / `max_hunks`. Hard limits enforced in W14.b validator. (confidence 0.82, gap 0.42)
3. **`*Agent.py` deletion gating** — **Refuse without AGENT-DELETION-AUTHORIZED marker**. W14.b validator scans for `Delete File: **/*Agent.py` operations; if present, requires `*** AGENT-DELETION-AUTHORIZED: <90-day-deprecation-start-date>` line in envelope preamble AND zero-references check via ADG `adg_edge_fanin` query. Either missing → abort. (confidence 0.91, gap 0.53)

## References

- Constitutional §4 — UWG write authority
- ADR-023 — runtime HITL exit control (envelope failures may need to escalate to runtime HITL, not just author-gate)
- Plan: `.codex/plans/post-wave10-roadmap-a1e7f2.md` — W14.a row
- Notion row: Wave/Phase Convergence INDEX `[INDEX] Post-Wave-10 Roadmap — W11 through W18` (`34c27693-f55c-813a-a19a-d052c901b8d5`)
- Anthropic apply_patch reference — Claude Code public docs (format definition)
- RFC 6902 — JSON Patch (Option 2 reference)

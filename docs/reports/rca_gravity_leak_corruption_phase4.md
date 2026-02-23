# Root Cause Analysis: GravityLeakRepairAgent Corruption Incident

**Classification:** Catastrophic Write Amplification + Infinite Mutation Retry Loop
**Severity:** P0 — Data Corruption, Service Unavailability
**Layers Implicated:** L0, L2, L4, L5
**Status:** Remediated (commit `48cd790b1799cf559cc6530cae7e33fb1701d977`)

---

## 1. Scope

This document is a formal Root Cause Analysis of the incident in which
`GravityLeakRepairAgent.apply_fix()` caused a source file to balloon to
approximately 5.2 GB via catastrophic string replacement, followed by an
infinite retry loop that continued to attempt the same prohibited write
every ~20 seconds until the process was killed.

No production code changes are introduced by this document.

---

## 2. Phase 1 — Incident Reconstruction

### 2.1 Timeline

| Step | Event | Layer |
|------|-------|-------|
| T+0 | `execute_ssot.py` (`_legacy_main`) invokes `GravityLeakRepairAgent.heal_repository(execute=True, dry_run=False)` | L0 |
| T+1 | `heal_repository` calls `StructuralValidatorAgent.validate_structure()`, receives N gravity violations | L5 |
| T+2 | For each violation, `analyze_violation()` produces a `GravityFix` with `old_import` derived from the raw import statement string | L5 |
| T+3 | `apply_fix(fix, dry_run=False)` is called; the pre-fix code path reaches `content.replace(old_import, new_import)` | L5 |
| T+4 | `old_import` is a single character (e.g., `"*"` or `"."`) extracted from a malformed import statement | L5 |
| T+5 | `str.replace(old_import, new_import)` replaces every occurrence of that single character in the entire file content, producing output N× larger than the original | L5 |
| T+6 | The inflated content (5.2 GB) is written to a temp file via `tempfile.NamedTemporaryFile` | L5 |
| T+7 | `os.replace(temp_name, state_path)` attempts to atomically swap the temp file into the target path | L5 |
| T+8 | `assert_no_persistent_write("L0", "json.dump")` inside `RuntimeStateManager.save()` raises `PermissionError("MUTATION_PROHIBITED:layer=L0|op=json.dump")` | L0 |
| T+9 | The pre-fix `save()` exception handler catches the generic `Exception`, logs the error, and returns silently | L0 |
| T+10 | The agent loop in `_legacy_main` continues to the next agent; `RuntimeStateManager.update_agent()` calls `save()` again | L0 |
| T+11 | Steps T+8–T+10 repeat every ~20 seconds for each agent invocation, producing a continuous stream of `MUTATION_PROHIBITED` log lines | L0 |
| T+12 | No circuit breaker, no latch, no downgrade path existed in `RuntimeStateManager.save()` to stop the loop | L0 |
| T+13 | Process runs until external kill or timeout | — |

### 2.2 Fault Injection Point: Catastrophic `str.replace`

The pre-fix `apply_fix` code path used:

```python
new_content = content.replace(old_import, new_import)
```

**Amplification math:**

Let `F` = file size in bytes, `k` = length of `old_import`, `m` = number of
occurrences of `old_import` in `F`, `n` = length of `new_import`.

Output size = `F - (m * k) + (m * n)`

When `k = 1` (single character, e.g., `"*"`, `"."`, `" "`) and `new_import`
is a full import statement of length ~60 characters:

- A 50 KB source file containing 90,000 single-character occurrences of `"."`
  produces: `50,000 - (90,000 × 1) + (90,000 × 60)` = **5,310,000 bytes ≈ 5.1 MB per file**
- Across a repository scan of ~1,000 files, cumulative output approaches **5.1 GB**

The amplification factor is `O(F / k × n)`. When `k → 1`, the factor is
unbounded by file size and replacement string length alone.

**Classification of this defect:**

| Defect Type | Present |
|---|---|
| Algorithmic defect | YES — `str.replace` is a global, unstructured text operation |
| Input validation failure | YES — no minimum token length check on `old_import` before replace |
| Missing invariant enforcement | YES — no pre-write size delta check, no write amplification detector |

### 2.3 Loop Persistence Mechanism

The retry loop persisted because of three independent missing controls:

**2.3.1 No deterministic prohibition recognition in `RuntimeStateManager.save()`**

The pre-fix `save()` method called `assert_no_persistent_write("L0", "json.dump")`
inside the `with tempfile.NamedTemporaryFile(...)` block. This raised
`PermissionError` on every call. The outer `except Exception` handler caught
it, logged `"Failed to save runtime state"`, and returned. The caller
(`update_agent`, `complete_agent`, `finish_mission`) did not inspect the
return value and continued execution unconditionally.

**2.3.2 No circuit breaker**

`RuntimeStateManager.save()` had no state variable to record that a
prohibition had already fired. Each invocation re-entered the same code path
and re-raised the same `PermissionError`. The loop had no memory of prior
failures.

**2.3.3 No layer-aware downgrade logic**

The agent orchestration loop in `_legacy_main` had no mechanism to detect
that `save()` was repeatedly failing with a prohibition error and downgrade
to a PLAN-ONLY or no-persistence mode. The loop continued to invoke agents,
each of which triggered `save()`, which triggered the prohibition, which was
swallowed, which allowed the next agent to run.

**Violated invariants:**

| Invariant | Violation |
|---|---|
| G-12-1: L0 MUST NOT perform persistent writes | Violated: `save()` attempted write on every agent transition |
| Fail-closed on prohibition | Violated: prohibition was caught and swallowed, not propagated |
| Idempotent retry ceiling | Violated: no ceiling; loop ran until process kill |
| PLAN-ONLY fallback on L0 targets | Violated: no downgrade path existed in `save()` |

---

## 3. Phase 2 — Causal Classification

### 3.1 Primary Causes

**PC-1: Global string replacement without structural guard**

`content.replace(old_import, new_import)` is a global, unstructured text
operation. It does not operate on AST nodes, import statements, or line
boundaries. It replaces every occurrence of `old_import` in the entire file
content, including occurrences inside string literals, comments, identifiers,
and multi-line expressions. This is the direct cause of the 5.2 GB file.

Layer: L5 (GravityLeakRepairAgent, `apply_fix`)

**PC-2: Absence of minimum token length invariant on `old_import`**

No guard existed to reject `old_import` values shorter than a meaningful
import token (minimum 3 characters for any valid Python import keyword
fragment). A single-character `old_import` is always a catastrophic replace
candidate on any non-trivial source file.

Layer: L5 (GravityLeakRepairAgent, `apply_fix`)

### 3.2 Enabling Causes

**EC-1: L0 mutation prohibition independent from `RuntimeStateManager` persistence path**

The `assert_no_persistent_write("L0", ...)` guard was placed inside the
`with tempfile.NamedTemporaryFile(...)` block in `save()`. This means the
temp file was created before the prohibition check fired. The prohibition
raised `PermissionError`, but the temp file was already on disk. The
exception handler did not reliably clean up the temp file (it attempted
cleanup inside a nested `try/except` that could itself fail silently).

Layer: L0 (`RuntimeStateManager.save`)

**EC-2: Agent lacked downgrade path to PLAN-ONLY**

The pre-fix `GravityLeakRepairAgent.apply_fix()` had no circuit breaker and
no `_emit_plan_only()` fallback. When a write failed for any reason, the
agent returned `{"status": "error"}` and the caller continued to the next
violation. There was no mechanism to recognize a prohibition error as
distinct from a transient I/O error.

Layer: L5 (GravityLeakRepairAgent, `apply_fix`)

**EC-3: Runtime persistence attempted from L0 on every agent transition**

`RuntimeStateManager.save()` was called by `start_mission`, `update_agent`,
`complete_agent`, `add_event`, `finish_mission`, and `update_meta_learning`.
Each of these is invoked on every agent transition in the orchestration loop.
With N agents in a full-domain scan, `save()` is called O(N) times. Each
call re-triggered the prohibition, producing O(N) identical error log lines.

Layer: L0 (`RuntimeStateManager`)

### 3.3 Systemic Causes

**SC-1: No static guardrail against `replace()` on source files**

No pre-commit hook, no AST-based linter rule, and no CI check prevented the
use of `str.replace` on file content in agent code. The anti-pattern
landmine detector did not classify global string replacement on source files
as a prohibited pattern.

**SC-2: No write-amplification detection**

No pre-write check compared the size of the proposed new content against the
size of the original file. A 2× growth ratio threshold would have caught the
5.2 GB case at the point of the `tempfile.NamedTemporaryFile` write, before
the atomic swap.

**SC-3: No size delta threshold enforcement**

The write gateway (`write_gateway.write_text`) did not enforce a maximum
write size or a maximum growth ratio. Any content, regardless of size, was
accepted for write.

**SC-4: No mutation entropy cap**

No mechanism existed to count the number of substitutions a single `replace`
call would make. A substitution count > 1 for an import rewrite is always a
defect (each import statement appears exactly once per file). A substitution
count > 10 should be a hard block.

---

## 4. Phase 3 — Prevention Design

### 4.1 Structural Invariants (Must-Haves)

**INV-1: No global `str.replace` on source file content**

Any call to `content.replace(old, new)` where `content` is the full text of
a source file is prohibited. Import rewrites MUST use line-level or
AST-level replacement only.

Enforcement: Anti-pattern landmine rule `global_source_replace` targeting
`content.replace(` in agent files.

**INV-2: Minimum token length ≥ 3 for import rewrites**

`old_import.strip()` MUST have `len >= 3` before any replacement is
attempted. Values of length 0, 1, or 2 MUST raise `ValueError` and emit
PLAN-ONLY.

Enforcement: Guard in `_apply_import_replacement_ast` (already present
post-fix at `len(stripped) <= 1`; tighten to `len(stripped) < 3`).

**INV-3: Maximum file growth ratio ≤ 2× original**

Before writing new content to a file, compute:
`growth_ratio = len(new_content) / max(len(original_content), 1)`
If `growth_ratio > 2.0`, raise `WriteAmplificationError` and emit PLAN-ONLY.

Enforcement: Pre-write check in `write_gateway.write_text`.

**INV-4: Maximum write size cap**

No single write operation may produce more than `MAX_WRITE_BYTES = 10 MB`
of content. Enforcement: Pre-write check in `write_gateway.write_text`.

**INV-5: Mandatory PLAN-ONLY fallback on L0 targets**

Any agent operating on a file whose resolved path is under an L0 immutable
root MUST emit PLAN-ONLY without attempting any write. The circuit breaker
check MUST precede all I/O, not follow it.

Enforcement: Pre-write layer check in `apply_fix` (already present
post-fix; must be the first check, before `tempfile.mkstemp`).

### 4.2 Runtime Guardrails

**RG-1: Write amplification detector**

```
def check_write_amplification(original: str, proposed: str, path: Path) -> None:
    ratio = len(proposed) / max(len(original), 1)
    if ratio > 2.0:
        raise WriteAmplificationError(
            f"Write amplification detected: {ratio:.1f}x growth on {path} "
            f"(original={len(original)} bytes, proposed={len(proposed)} bytes)"
        )
```

Must be called in `write_gateway.write_text` before any I/O.

**RG-2: Mutation entropy scoring**

Before executing any `replace`-based rewrite, count the number of
substitutions that would be made:

```
substitution_count = original_content.count(old_token)
if substitution_count > 1:
    raise MutationEntropyError(
        f"Import rewrite would make {substitution_count} substitutions "
        f"for token {old_token!r}; expected exactly 1."
    )
```

**RG-3: Retry ceiling enforcement**

`RuntimeStateManager.save()` MUST latch `_persistence_disabled = True` on
the first `MUTATION_PROHIBITED` error and become a no-op for all subsequent
calls in the same process lifetime. This is the fix implemented in
`48cd790b1`. The ceiling is 1: after the first prohibition, all future
`save()` calls are silently skipped.

**RG-4: Deterministic prohibition classifier**

Exception handlers that catch `PermissionError` MUST inspect the error
message for `"MUTATION_PROHIBITED"` before deciding whether to swallow,
propagate, or latch. A generic `except Exception` that swallows prohibition
errors is a systemic defect.

Pattern:

```python
except PermissionError as e:
    if "MUTATION_PROHIBITED" in str(e):
        self._handle_prohibition(e)  # latch + log + return
    else:
        raise  # re-raise non-prohibition permission errors
```

### 4.3 Architectural Hardening

**AH-1: Separate proposal generation from mutation execution**

`GravityLeakRepairAgent.analyze_violation()` (proposal) and
`apply_fix()` (execution) are already separate methods. The architectural
requirement is that proposal generation MUST be callable without any I/O
side effects, and execution MUST be explicitly gated by a mutation budget
check before any file is opened.

**AH-2: AST-only transformations for import rewrites**

All import rewrites MUST use `ast.parse` + `ast.unparse` (or `libcst`) to
locate and replace import nodes. String-based replacement on source text is
prohibited for import rewrites. The line-level replacement in the post-fix
`_apply_import_replacement_ast` is an acceptable intermediate step but
should be superseded by full AST transformation.

**AH-3: Mutation risk scoring before write**

Before any write is executed, compute a risk score:

```
risk = (substitution_count > 1) * 10
      + (growth_ratio > 1.5) * 5
      + (file_layer == "L0") * 20
      + (len(old_token) < 3) * 15
```

If `risk > 0`, emit PLAN-ONLY. Only `risk == 0` permits execution.

**AH-4: Global mutation budget counter per run**

Each `execute_ssot` run MUST maintain a `MutationBudget` counter:

```
MAX_MUTATIONS_PER_RUN = 50  # hard ceiling
mutations_this_run: int = 0
```

Before each write, increment the counter. If `mutations_this_run >=
MAX_MUTATIONS_PER_RUN`, block all further writes for the run and emit a
budget-exhausted warning. This prevents a single run from making unbounded
changes.

---

## 5. Phase 4 — Risk Model Update

### 5.1 Failure Mode Taxonomy

| ID | Failure Mode | Layer | Severity | Trigger |
|----|---|---|---|---|
| FM-1 | Catastrophic write amplification | L5 | P0 | `str.replace` with `len(old) <= 1` on source file |
| FM-2 | Infinite mutation retry loop | L0 | P0 | `save()` prohibition swallowed; no latch |
| FM-3 | Sovereignty boundary violation attempt | L0/L5 | P1 | Agent writes to immutable root without PLAN-ONLY gate |
| FM-4 | State persistence violation | L0 | P1 | `RuntimeStateManager.save()` called from L0 without prohibition awareness |
| FM-5 | Temp file leak on prohibition | L0 | P2 | Temp file created before prohibition check; cleanup path unreliable |
| FM-6 | Silent prohibition swallow | L0/L5 | P1 | `except Exception` catches `PermissionError("MUTATION_PROHIBITED...")` |

### 5.2 Detection Signals

**DS-1: Rapid file growth**

Telemetry signal: `WRITE_AMPLIFICATION_DETECTED`

Emit when: `len(proposed_content) / len(original_content) > 2.0`

Fields: `file`, `original_bytes`, `proposed_bytes`, `growth_ratio`, `agent`

**DS-2: Repeated `MUTATION_PROHIBITED` log lines**

Telemetry signal: `MUTATION_PROHIBITION_LOOP`

Emit when: The same `(layer, op, path)` tuple appears in `MUTATION_PROHIBITED`
log lines more than once within a single process lifetime.

Threshold: 2 occurrences of the same tuple = loop detected.

Fields: `layer`, `op`, `path`, `occurrence_count`, `elapsed_seconds`

**DS-3: High-frequency identical error logs**

Telemetry signal: `ERROR_SPAM_DETECTED`

Emit when: The same error message string appears more than 5 times within
60 seconds.

Fields: `message_hash`, `count`, `window_seconds`, `first_seen`, `last_seen`

### 5.3 Governance Update Recommendations

#### 5.3.1 Mutation Policy Additions

Add the following rules to the mutation policy (`.windsurfrules` §5 or
equivalent):

```
MP-NEW-1: str.replace on source file content is PROHIBITED.
          Use line-level or AST-level replacement only.

MP-NEW-2: Any write where len(proposed) / len(original) > 2.0 is PROHIBITED.
          Emit PLAN-ONLY and log WRITE_AMPLIFICATION_DETECTED.

MP-NEW-3: Any import rewrite token with len(token.strip()) < 3 is PROHIBITED.
          Raise ValueError before any I/O is attempted.

MP-NEW-4: Any agent operating on an L0 immutable root MUST emit PLAN-ONLY
          before attempting any write. The layer check MUST precede
          tempfile creation.

MP-NEW-5: RuntimeStateManager.save() MUST latch _persistence_disabled=True
          on first MUTATION_PROHIBITED and become a no-op thereafter.
          This is a hard invariant, not a best-effort behavior.
```

#### 5.3.2 Agent Development Guidelines Additions

```
ADG-NEW-1: Never use str.replace(old, new) where old is derived from
           user input, violation data, or any string that may be
           shorter than 3 characters.

ADG-NEW-2: All file mutation methods must call the write amplification
           detector before writing. This is not optional.

ADG-NEW-3: All exception handlers that catch PermissionError must
           explicitly check for "MUTATION_PROHIBITED" in the error
           message and handle it as a latch event, not a transient error.

ADG-NEW-4: Proposal generation (analyze_violation) and mutation execution
           (apply_fix) must remain separate methods. Proposal generation
           must have zero I/O side effects.

ADG-NEW-5: Every agent that can write files must implement a circuit
           breaker keyed on (file_path, op). The circuit breaker must
           raise a typed exception (not return an error dict) on the
           second hit.
```

#### 5.3.3 Code Review Checklist Additions

```
CR-NEW-1: [ ] Does any method call content.replace(x, y) where x is
              derived from external data? If yes, BLOCK.

CR-NEW-2: [ ] Is there a pre-write size delta check before any
              tempfile.NamedTemporaryFile or open(..., 'w') call?
              If no, BLOCK.

CR-NEW-3: [ ] Does any except Exception block swallow a PermissionError
              without checking for "MUTATION_PROHIBITED"? If yes, BLOCK.

CR-NEW-4: [ ] Does any agent write to a file before checking the layer
              of the target path? If yes, BLOCK.

CR-NEW-5: [ ] Is there a mutation budget counter for the run? If no,
              REQUIRE before merge.
```

---

## 6. Summary

### Primary Causes

1. `str.replace(old_import, new_import)` with `len(old_import) == 1` on full
   source file content — direct cause of 5.2 GB file (L5, `apply_fix`).
2. No minimum token length invariant on `old_import` before replacement (L5).

### Enabling Causes

1. `assert_no_persistent_write` placed inside `tempfile` block — temp file
   created before prohibition check (L0, `save`).
2. No PLAN-ONLY downgrade path in pre-fix `apply_fix` (L5).
3. `save()` called O(N) times per run with no prohibition awareness (L0).

### Systemic Causes

1. No anti-pattern rule against `str.replace` on source files.
2. No write amplification detector in write gateway.
3. No size delta threshold in write gateway.
4. No mutation entropy cap (substitution count check).

### Remediation Status

| Fix | Commit | Status |
|---|---|---|
| `RuntimeStateManager._persistence_disabled` latch | `48cd790b1` | Merged |
| `GravityLeakRepairAgent` circuit breaker | `48cd790b1` | Merged |
| `_apply_import_replacement_ast` line-level replacement | `48cd790b1` | Merged |
| `len(stripped) <= 1` guard in `apply_fix` | `48cd790b1` | Merged |
| Write amplification detector in write gateway | Not yet implemented | Pending |
| AST-only import rewrite | Not yet implemented | Pending |
| Mutation budget counter per run | Not yet implemented | Pending |
| Anti-pattern rule for `str.replace` on source | Not yet implemented | Pending |

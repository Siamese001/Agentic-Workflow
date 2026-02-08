# RCA: Mixin + Agent Compound Suffix Butchering

**Date:** 2026-02-07
**Severity:** Medium (naming corruption + classification gap)
**Scope:** 2 files fixed, 7 compound patterns added, FCA hardened

---

## Symptoms

1. `neuralautoimmuneagent_mixin.py` — filename contains "agent" embedded in stem + `_mixin` suffix
2. `autonomy_mixin_agent_mixin.py` — filename has TRIPLE suffixes: `_mixin` + `_agent` + `_mixin`

---

## Root Causes

### RC-1: `_agent` NOT in `KNOWN_ARCHITECTURAL_SUFFIXES` (PRIMARY)

The `validate_single_suffix()` method in `FileClassificationAgent.py` iteratively strips trailing architectural suffixes to detect compound violations. **But `_agent` was never in the `KNOWN_ARCHITECTURAL_SUFFIXES` list.**

For `autonomy_mixin_agent_mixin.py`:
```
stem: "autonomy_mixin_agent_mixin"
Iteration 1: strip "_mixin" → "autonomy_mixin_agent"
Iteration 2: check "_agent" → NOT IN LIST → stop
Result: 1 suffix found → COMPLIANT (false negative!)
```

The triple suffix was invisible to the validator.

### RC-2: No MIXIN compound patterns in `COMPOUND_SUFFIX_CONFLICTS`

The `_detect_filename_tag_conflicts()` method checks the `COMPOUND_SUFFIX_CONFLICTS` list for known bad patterns. **No `_mixin_agent`, `_agent_mixin`, or `_mixin_agent_mixin` patterns existed.**

Result: dual-tag detection returned empty set → no conflict flagged → no folder-context resolution triggered.

### RC-3: `"mixins"` missing from FCA `folder_to_filetype` mapping

Even IF a dual-tag conflict were detected for a file in `mixins/`, the folder-context resolution at PRIORITY 2.3 didn't include `"mixins"` in its lookup table. It could resolve `types/`, `config/`, `validators/`, etc. — but not `mixins/`.

### RC-4: Healing-pass suffix accumulation (autonomy_mixin_agent_mixin.py)

The butchered name was created by successive healing passes:
1. Original file: `autonomy_mixin.py` (correct)
2. A healing pass detected the file inherits from `SovereignBaseAgent` → appended `_agent` suffix → `autonomy_mixin_agent.py`
3. Another healing pass detected the file is in `mixins/` → appended `_mixin` suffix → `autonomy_mixin_agent_mixin.py`
4. The correct `autonomy_mixin.py` also still existed → creating an **exact duplicate**

### RC-5: Run-together PascalCase in filename (neuralautoimmuneagent_mixin.py)

The class name `NeuralAutoImmuneAgent` was converted to a snake_case filename but without proper word separation: `neuralautoimmuneagent` instead of `neural_autoimmune_agent`. This embedded "agent" in the stem without an underscore, making it undetectable by suffix patterns.

The file also contains a `SovereignBaseAgent` subclass, meaning it's actually an AGENT file misplaced in `mixins/`.

---

## Fixes Applied

### Hardening (preventive)

| Change | File | Detail |
|--------|------|--------|
| Added 7 MIXIN compound patterns | `structure_blueprint_config.py` | `_mixin_agent_mixin`, `_mixin_agent`, `_agent_mixin`, `_mixin_types`, `_mixin_config`, `_mixin_util`, `_mixin_validator` |
| Added `"mixins": "MIXIN"` to folder_to_filetype | `FileClassificationAgent.py` | Enables folder-context resolution for dual-tagged files in `mixins/` |

### File fixes

| Action | File | Detail |
|--------|------|--------|
| **Deleted** | `autonomy_mixin_agent_mixin.py` | Exact duplicate of `autonomy_mixin.py` (identical 79 lines) |
| **Renamed** | `neuralautoimmuneagent_mixin.py` → `neural_autoimmune_mixin.py` | Dropped embedded "agent", added proper word separation |
| **Updated** | `_import_map.json` | Updated import mapping for renamed file |

### Note on `domain_agent_mixin.py` and `feature_flagged_agent_mixin.py`

These files also have `_agent_mixin` compound suffix but are **legitimately named** — "AgentMixin" is a semantic unit (mixin designed for agents). They have 3 and 4 external import references respectively. The new `_agent_mixin$` compound pattern in `COMPOUND_SUFFIX_CONFLICTS` will now flag them as dual-tagged, and the FCA's folder-context resolution (`"mixins": "MIXIN"`) will correctly classify them as MIXIN. **No rename needed.**

---

## Why NOT add `_agent` to `KNOWN_ARCHITECTURAL_SUFFIXES`?

Adding `_agent` would cause `validate_single_suffix()` to flag ALL `*_agent_mixin.py` files as compound violations — including the legitimate `feature_flagged_agent_mixin.py` and `domain_agent_mixin.py`. The iterative stripping approach can't distinguish domain descriptors from classification suffixes. The `COMPOUND_SUFFIX_CONFLICTS` regex approach is more precise: it flags the pattern, and folder context resolves the ambiguity.

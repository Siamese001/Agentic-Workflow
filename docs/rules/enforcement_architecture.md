# Enforcement Architecture: Windsurf Rules + CI Gates

**Last Updated**: 2026-03-11
**Status**: Canonical Contract
**Purpose**: Define the two-layer enforcement architecture with clear responsibility boundaries

---

## The Two-Layer Contract

```
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 1: WINDSURF RULES (AI-time enforcement)                 │
│  Responsibility: BEHAVIOURAL — HOW the AI must work            │
│  Timing: BEFORE any work begins                                │
│  Enforcement: Mandatory pre-conditions block tool calls        │
│  ─────────────────────────────────────────────────────────────  │
│  Examples:                                                      │
│  ✅ Build ADG BEFORE investigating code                        │
│  ✅ Declare scope BEFORE editing files                         │
│  ✅ Record checkpoint BEFORE multi-file phase                  │
│  ✅ Search for duplicates BEFORE creating symbol               │
│  ✅ Answer 4 litmus questions BEFORE repair edit               │
│                                                                 │
│  These are PROCESS rules — cannot be verified at commit time   │
└─────────────────────────────────────────────────────────────────┘
                         ↓ work happens ↓
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 2: PRE-COMMIT CI GATES (commit-time enforcement)        │
│  Responsibility: STRUCTURAL — WHAT ended up in code            │
│  Timing: AFTER work is done, at commit                         │
│  Enforcement: Hard block on git commit                         │
│  ─────────────────────────────────────────────────────────────  │
│  Examples:                                                      │
│  ✅ Dead imports present (observable in file)                  │
│  ✅ Layer violations present (observable in imports)           │
│  ✅ Plan in wrong directory (observable in path)               │
│  ✅ New script file created (observable in git diff)           │
│  ✅ Shim missing deprecation warning (observable in content)   │
│                                                                 │
│  These are STRUCTURAL rules — verifiable by inspecting files   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Decision Tree: Where Does This Rule Belong?

Use this decision tree when adding a new rule or reviewing an existing one:

```
START: New rule to enforce

├─ Can it be verified by inspecting files or git diff?
│  ├─ YES → Is it about code structure/content?
│  │  ├─ YES → PRE-COMMIT GATE ONLY
│  │  │         Examples: import hygiene, layer violations, anti-patterns
│  │  │
│  │  └─ NO → Is it about process artifacts (checkpoints, evidence)?
│  │     ├─ YES → BOTH LAYERS
│  │     │        Windsurf: enforce creation BEFORE work
│  │     │        Pre-commit: verify artifact exists AFTER work
│  │     │        Examples: rollback checkpoints, dedup search evidence
│  │     │
│  │     └─ NO → WINDSURF ONLY
│  │              Examples: rare edge cases
│  │
│  └─ NO → Is it about HOW the AI should work?
│     ├─ YES → WINDSURF ONLY
│     │        Examples: AST-first, scope declaration, repair protocol
│     │
│     └─ NO → Re-evaluate the rule (may not be enforceable)
│
END
```

---

## Rule Classification Matrix

| Rule | Layer | Timing | Type | Rationale |
|------|-------|--------|------|-----------|
| **AST-First Gate** | Windsurf | Before work | Behavioural | Process rule — must build graph BEFORE investigation |
| **Scope Guard** | Windsurf | Before work | Behavioural | Process rule — must declare scope BEFORE edits |
| **Rollback Gate** | Both | Before work (primary) | Behavioural + Structural | Windsurf enforces checkpoint creation; CI verifies artifact exists |
| **Dedup Guard** | Both | Before work (primary) | Behavioural + Structural | Windsurf enforces 4-step search; CI flags new symbols as proxy |
| **ADG Repair Discipline** | Windsurf | Before work | Behavioural | Process rule — must answer litmus questions BEFORE edit |
| **Script Sprawl Guard** | Both | Before work (primary) | Behavioural + Structural | Windsurf enforces decision tree; CI detects new scripts |
| **Shim Discipline** | Both | Before work (primary) | Behavioural + Structural | Windsurf enforces protocol; CI validates shim content |
| **Import Hygiene** | Pre-commit | After work | Structural | Observable in file — dead/forbidden imports detectable |
| **Layer Boundary Guard** | Pre-commit | After work | Structural | Observable in imports — GV edges detectable |
| **Plan Location** | Pre-commit | After work | Structural | Observable in path — file location verifiable |
| **Pytest Integrity** | Pre-commit | After work | Structural | Observable in markers — pytest.skip detectable |
| **Anti-Pattern Landmines** | Pre-commit | After work | Structural | Observable in code — patterns detectable |
| **Test Rigor** | Pre-commit | After work | Structural | Observable in test files — coverage verifiable |

---

## Enforcement Mechanisms

### Windsurf Layer (Behavioural)

**Mechanism**: Mandatory pre-condition blocks in skill `SKILL.md` files

**Format**:
```markdown
## MANDATORY PRE-CONDITION (Constitutional — no bypass)

**BEFORE [specific action]:**

1. **Execute**: [specific command or check]
2. **Write output to**: [specific evidence section]
3. **Verify**: [specific validation]

**IF any step fails → STOP. Do not proceed.**
```

**Example** (AST-First Gate):
```markdown
## MANDATORY PRE-CONDITION (Constitutional — no bypass)

**BEFORE any tool call involving code analysis:**

1. **Execute**: Build AST dependency graph using `tools/generate_full_adg.py`
2. **Write output to**: Evidence section titled `## DEPENDENCY_GRAPH`
3. **Document**: Graph node count, edge count, edge types, blast radius
4. **Verify**: Graph contains >0 nodes and >0 edges

**IF any step fails → STOP. Do not proceed with code investigation.**
```

**Enforcement Strength**: Soft (AI must voluntarily follow)
**Coverage**: Process rules that cannot be verified at commit time
**Bypass**: Only if user explicitly requests bypass (with constitutional warning)

### Pre-Commit Layer (Structural)

**Mechanism**: Python scripts in `ops_scripts/ci/` called by `.pre-commit-config.yaml`

**Format**:
```python
#!/usr/bin/env python3
"""[Rule Name] — [One-line description]

Constitutional Rule: [Reference to rule document]

This gate enforces that:
1. [Observable fact 1]
2. [Observable fact 2]
...

BLOCKS commits that:
- [Violation pattern 1]
- [Violation pattern 2]

PASSES commits that:
- [Compliance pattern 1]
- [Compliance pattern 2]
"""

def main() -> int:
    """Enforce [rule name] — [observable structural check]."""
    # 1. Get staged files
    # 2. Check observable facts
    # 3. Return 0 (pass) or 1 (fail)
```

**Enforcement Strength**: Hard (blocks git commit)
**Coverage**: Structural rules verifiable by inspecting files/diffs
**Bypass**: `git commit --no-verify` (emergency only, requires justification)

---

## Dual-Layer Rules (Both)

Some rules have enforcement in BOTH layers:

| Rule | Windsurf Enforcement | Pre-Commit Enforcement |
|------|---------------------|----------------------|
| **Rollback Gate** | BEFORE phase: record checkpoint | AFTER phase: verify checkpoint artifact exists |
| **Dedup Guard** | BEFORE creation: 4-step search | AFTER creation: flag new symbols (proxy) |
| **Script Sprawl** | BEFORE creation: decision tree | AFTER creation: detect new scripts |
| **Shim Discipline** | BEFORE move: protocol | AFTER move: validate shim content |

**Key Principle**: Windsurf is PRIMARY (prevents), pre-commit is SECONDARY (detects if it slipped through).

---

## Common Mistakes to Avoid

### ❌ Mistake 1: Putting Process Rules in Pre-Commit

**Wrong**:
```yaml
- id: check-ast-first-gate
  entry: python ops_scripts/ci/check_ast_first_gate.py
```

**Why Wrong**: AST-first is a PROCESS rule (must build graph BEFORE investigation). At commit time, the investigation is already done. Pre-commit cannot reverse bad decisions.

**Correct**: Enforce in Windsurf skill with mandatory pre-condition block.

### ❌ Mistake 2: Relying Only on Windsurf for Structural Rules

**Wrong**: Only documenting import hygiene in Windsurf skills, no pre-commit gate.

**Why Wrong**: Windsurf enforcement is soft (AI can make mistakes). Structural rules MUST have hard pre-commit enforcement as safety net.

**Correct**: Enforce in BOTH layers — Windsurf guides, pre-commit blocks.

### ❌ Mistake 3: Confusing Proxy Checks with Full Enforcement

**Wrong**: Believing `check_dedup_violations.py` prevents all duplicates.

**Why Wrong**: Pre-commit can only detect NEW symbols, not semantic duplicates. Full dedup requires AST-backed search BEFORE creation (Windsurf layer).

**Correct**: Understand pre-commit dedup is a PROXY flag, not full enforcement.

---

## Maintenance Protocol

### Adding a New Rule

1. **Classify the rule** using the decision tree above
2. **Choose enforcement layer(s)**:
   - Behavioural/process → Windsurf only
   - Structural/observable → Pre-commit only
   - Both aspects → Both layers (Windsurf primary, pre-commit secondary)
3. **Create artifacts**:
   - Windsurf: Add skill to `.windsurf/skills/[skill-name]/` with `MANDATORY PRE-CONDITION` block
   - Pre-commit: Add script to `ops_scripts/ci/check_[rule].py`
4. **Add metadata** to skill `SKILL.md`:
   ```yaml
   enforcement_layer: windsurf | pre-commit | both
   enforcement_timing: before_work | after_work
   enforcement_type: behavioural | structural | behavioural_primary_structural_secondary
   ```
5. **Update `.pre-commit-config.yaml`** if adding CI gate
6. **Update `RULES_INDEX.md`** with new rule entry
7. **Test** the enforcement mechanism
8. **Document** in this file

### Reviewing an Existing Rule

1. **Check classification**: Is it in the correct layer?
2. **Verify enforcement**: Does the mechanism match the rule type?
3. **Test effectiveness**: Does it actually prevent/detect violations?
4. **Check for redundancy**: Is it duplicated across layers unnecessarily?
5. **Update if misplaced**: Move to correct layer per decision tree

---

## Examples

### Example 1: Pure Windsurf Rule (AST-First Gate)

**Rule**: Build AST dependency graph BEFORE any code investigation

**Classification**:
- Can it be verified at commit time? NO (investigation already done)
- Is it about HOW the AI works? YES (process rule)
- **Decision**: Windsurf only

**Enforcement**:
- Windsurf skill: `.windsurf/skills/ast-first-gate/SKILL.md` with mandatory pre-condition
- Pre-commit gate: None (would be too late)

**Metadata**:
```yaml
enforcement_layer: windsurf
enforcement_timing: before_work
enforcement_type: behavioural
```

### Example 2: Pure Pre-Commit Rule (Import Hygiene)

**Rule**: No dead imports (ruff F401)

**Classification**:
- Can it be verified at commit time? YES (observable in file)
- Is it about code structure? YES (import statements)
- **Decision**: Pre-commit only

**Enforcement**:
- Windsurf skill: Optional guidance (not mandatory)
- Pre-commit gate: Ruff F401 check (hard block)

**Metadata**:
```yaml
enforcement_layer: pre-commit
enforcement_timing: after_work
enforcement_type: structural
```

### Example 3: Dual-Layer Rule (Rollback Gate)

**Rule**: Record checkpoint BEFORE multi-file phase; verify artifact exists AFTER phase

**Classification**:
- Can it be verified at commit time? PARTIALLY (artifact observable, but process not)
- Is it about HOW the AI works? YES (process rule for checkpoint creation)
- **Decision**: Both layers (Windsurf primary, pre-commit secondary)

**Enforcement**:
- Windsurf skill: `.windsurf/skills/rollback-gate/SKILL.md` with mandatory pre-condition (PRIMARY)
- Pre-commit gate: `ops_scripts/ci/check_rollback_checkpoints.py` verifies artifact exists (SECONDARY)

**Metadata**:
```yaml
enforcement_layer: both
enforcement_timing: before_work
enforcement_type: behavioural_primary_structural_secondary
```

---

## FAQ

### Q: Why not enforce everything in pre-commit?

**A**: Pre-commit runs AFTER work is done. Process rules (like "build ADG first") cannot be enforced at commit time because the investigation/refactoring is already complete. Pre-commit cannot reverse bad decisions.

### Q: Why not rely only on Windsurf rules?

**A**: Windsurf enforcement is soft — the AI must voluntarily follow the rules. For structural checks (dead imports, layer violations), we need hard pre-commit enforcement as a safety net. Also, non-Windsurf contributors (humans, other AI tools) won't see Windsurf rules.

### Q: What if a rule fits both categories?

**A**: Use BOTH layers with clear primary/secondary roles. Windsurf enforces the PROCESS (prevents), pre-commit verifies the RESULT (detects if it slipped through). Example: Rollback gate — Windsurf enforces checkpoint creation, pre-commit verifies checkpoint artifact exists.

### Q: How do I know if a pre-commit gate is misplaced?

**A**: Ask: "Can this gate reverse a bad decision made during work?" If NO, it's likely misplaced. Example: AST-first gate at commit time cannot force the AI to rebuild the graph and redo the investigation.

### Q: Can I bypass Windsurf rules?

**A**: Only if user explicitly requests bypass. The AI must warn about constitutional violation and reduced confidence. Bypass should be rare and documented.

### Q: Can I bypass pre-commit gates?

**A**: Yes, with `git commit --no-verify`, but only for emergencies. Requires justification in commit message. Frequent bypasses indicate the gate is too strict or misplaced.

---

## Revision History

| Date | Change | Author |
|------|--------|--------|
| 2026-03-11 | Initial architecture document created | Cursor Agent AI |
| 2026-03-11 | Removed AST-first gate from pre-commit (misplaced) | Cursor Agent AI |
| 2026-03-11 | Added mandatory pre-condition blocks to 5 Windsurf skills | Cursor Agent AI |
| 2026-03-11 | Tightened dedup and rollback CI gates to proxy/artifact checks | Cursor Agent AI |
| 2026-03-11 | Added enforcement_layer metadata to all skills | Cursor Agent AI |

---

## References

- `.windsurf/RULES_INDEX.md` — Master index of all rules and gates
- `.windsurf/rules/adg-repair-discipline.md` — ADG repair protocol
- `.windsurf/skills/` — All Windsurf skill definitions
- `ops_scripts/ci/` — All pre-commit gate scripts
- `.pre-commit-config.yaml` — Pre-commit hook configuration

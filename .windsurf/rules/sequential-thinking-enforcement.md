# Sequential Thinking Enforcement Rule

**Trigger**: always_on
**Layer**: Windsurf (AI-time behavioral)
**Type**: Behavioural
**Priority**: High

---

## §ST-0: Core Principle

**For all T2/T3 tasks (multi-file, architecture, planning, debugging), Cascade MUST invoke `mcp7_sequentialthinking` before proceeding with the actual work.**

Sequential thinking is a model-agnostic reasoning tool available to ALL models in Windsurf (Phoenix, SWE, and future models). This rule applies to any model — enforcement is based on task complexity, not model name.

---

## §ST-1: When Sequential Thinking is REQUIRED

**MANDATORY for T2/T3 tasks:**

- **Planning phases** — creating execution plans, wave breakdowns, task decomposition
- **Architecture decisions** — design choices, layer placement, technology selection
- **Debugging complex issues** — multi-file bugs, state bugs, integration failures
- **Refactoring** — structural changes affecting multiple files
- **Analysis tasks** — ADG graph analysis, dependency tracing, impact assessment
- **Test strategy** — designing test suites, coverage planning, test architecture
- **Multi-step reasoning** — any task requiring systematic decomposition

**Tier reference:** See `.windsurfrules` §0 DEFAULT ANALYSIS MODE for T2/T3 classification:
- **T2 — Scoped**: 2–5 files, single layer
- **T3 — Architectural**: >5 files, cross-layer, governance, or new feature

---

## §ST-2: When Sequential Thinking is NOT Required

**EXEMPT for T0/T1 tasks:**

- **T0 — Question**: No code changes (explain, review, advise)
- **T1 — Trivial**: ≤1 file, ≤20 lines, obvious scope (typo, docstring, config value, add assertion)

**Examples of exempt tasks:**
- Fixing a typo in a string
- Adding a docstring
- Changing a single config value
- Adding a single import
- Formatting changes
- Simple variable rename within one file

---

## §ST-3: How to Invoke

**Required pattern at start of T2/T3 task:**

```python
mcp7_sequentialthinking(
    thought="Initial problem decomposition and approach planning",
    nextThoughtNeeded=True,
    thoughtNumber=1,
    totalThoughts=<estimated_thoughts_for_task>
)
```

**Guidance for `totalThoughts`:**
- Simple T2: 5–10 thoughts
- Complex T2: 10–15 thoughts
- T3 architectural: 15–25 thoughts

---

## §ST-4: Integration with Existing Rules

This rule complements but does not replace:
- **§0 DEFAULT ANALYSIS MODE** — still classify tier first, then apply this rule
- **§1 TESTING FRAMEWORK** — still require tests, use sequential thinking for test strategy design
- **§2 ADG FRAMEWORK** — still use ADG for scope, use sequential thinking for analysis approach
- **§HITL-0 HITL Enforcement** — still present options for decisions, use sequential thinking to reason through options

---

## §ST-5: Enforcement

This is a **behavioral rule** enforced during AI execution. No pre-commit hook can verify compliance.

**Audit trail:** When sequential thinking is invoked, evidence files and plans should reference the sequential thinking output as part of the reasoning process.

---

## §ST-6: Quick Reference

| Task Type | Tier | Sequential Thinking Required? |
|---|---|---|
| Explain code | T0 | ❌ NO |
| Fix typo | T1 | ❌ NO |
| Add docstring | T1 | ❌ NO |
| Debug multi-file bug | T2 | ✅ YES |
| Refactor 3 files | T2 | ✅ YES |
| Plan architecture | T3 | ✅ YES |
| Design test strategy | T3 | ✅ YES |
| ADG graph analysis | T3 | ✅ YES |

---

## MAXIM

- **Complexity triggers, not model names.** Use sequential thinking when the task requires it, regardless of which model is active.
- **Think before act.** For T2/T3 work, always decompose the problem systematically before making changes.
- **Model-agnostic benefit.** Phoenix, SWE, or future models — all get the same structured reasoning discipline.

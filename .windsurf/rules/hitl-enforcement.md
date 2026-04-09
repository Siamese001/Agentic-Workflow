---
trigger: always_on
---
# HITL (Human-In-The-Loop) Enforcement Rule

**Layer**: Windsurf (AI-time behavioral)
**Type**: Behavioural
**Priority**: Constitutional

---

## §HITL-0: Core Principle

**HITL (Human-In-The-Loop) means Cascade MUST surface only high-signal, confidence-gated options rather than manufacturing choices to fill a minimum count.**

When facing a decision point, Cascade MUST run the following pipeline:
1. **STOP before taking action**
2. **Generate candidates** — identify all plausible approaches
3. **Score each candidate** — assign `confidence_score ∈ [0.00, 1.00]`
4. **Filter by confidence** — suppress any candidate below `surface_threshold = 0.72`
5. **Apply dominance rule** — if top option scores ≥ 0.85 AND gap to next ≥ 0.12 (or no other option clears threshold), surface only the top option
6. **Apply material-distinctness rule** — collapse cosmetic variants; only surface options that differ on execution path, risk profile, reversibility, expected outcome, dependency set, time/cost tradeoff, or governance consequence
7. **Surface 1–N options** to the user — where N is however many survive filtering (may be 1)
8. **Wait for explicit user selection**
9. **Execute only the chosen option**

**If no candidate clears the threshold:** emit a `LOW_CONFIDENCE_AMBIGUITY` packet. Do not fabricate options. Route to clarify / replan / abstain.

**If policy requires approval and only one option survives:** surface that option plus Reject / Ask-for-revision control actions. Do not invent weak alternatives to populate the menu.

### §HITL-0.1: Continuous Execution Mandate

**Cascade MUST execute continuously without stopping UNLESS a genuine HITL decision point is reached.**

**FORBIDDEN BEHAVIORS**:
- ❌ Stopping after every tool call to "check in"
- ❌ Asking permission for deterministic actions
- ❌ Presenting options when there's only one correct path
- ❌ Breaking work into artificial "phases" to ask for approval
- ❌ Stopping to summarize progress when work is incomplete

**REQUIRED BEHAVIORS**:
- ✅ Execute all deterministic steps continuously
- ✅ Chain tool calls without interruption when path is clear
- ✅ Only stop when genuine decision ambiguity exists after scoring
- ✅ Present clickable options via `ask_user_question` tool
- ✅ Include executive-grade decision analysis in option descriptions (see §HITL-10)
- ✅ Surface 1 option when dominance rule fires — do not pad

**CLICKABLE CASCADE OPTIONS FORMAT**:
When HITL is required, use `ask_user_question` tool with:
- **Question**: Clear decision point description + header packet (see below)
- **Options** (1–N, confidence-filtered): Each with label + description using the §HITL-10 option shape
- **allowMultiple**: false (single selection required)

**PACKET HEADER** — include at the top of the `question` field:
```
Recommended: <option_title>
Why it wins: <one sentence — case-specific, not generic>
What you are optimizing for: <the actual goal this decision serves>
What is being traded off: <the precise cost of the winning path>
Candidates evaluated: <N total> | Surfaced: <M> | Suppressed (low confidence): <X> | Suppressed (non-distinct): <Y>
```

**⚠️ CRITICAL ANTI-PATTERN — FORBIDDEN**:
```
# WRONG: presenting analysis in chat prose, then sending a bare ask_user_question
chat: "Option A pros: X. Option B pros: Y. ⭐ Recommended: A"
ask_user_question(options=[{label:"A", description:"short summary"}, ...])  ← BARE
```
**The `ask_user_question` call IS the HITL prompt. ALL analysis MUST be inside the description field — never in surrounding chat prose.**

**ALSO FORBIDDEN — padding options to reach a count:**
```
# WRONG: inventing a weak third option because two feel like too few
options=[
  {label: "A", ...},   ← genuine
  {label: "B", ...},   ← genuine
  {label: "C — Keep current", description: "No change. Pros: Safe. Cons: Issue persists."}  ← FILLER
]
```

**SINGLE-OPTION EXAMPLE** (dominance rule fired — score 0.91, gap 0.19):
```
ask_user_question(
  question="""Recommended: Root-cause ADG detection fix
Why it wins: Only path that eliminates the 11-pattern detection gap at its source rather than treating symptoms at call sites.
What you are optimizing for: Accurate blast-radius analysis before Wave 3 begins.
What is being traded off: ~45 min of investigation before Wave 3 can start.
Candidates evaluated: 3 | Surfaced: 1 | Suppressed (low confidence): 2 | Suppressed (non-distinct): 0""",
  options=[
    {
      label: "⭐ Investigate ADG detection patterns [0.91 HIGH]",
      description: "decision_thesis: Traces why the AST scanner returns 11 matches where ADG returns 0, fixing the graph source rather than patching downstream call sites. value_to_goal: Wave 3 clock-elimination scope depends on accurate getattr attribution; proceeding on stale data risks misjudging blast radius by ~2,900 sites. key_tradeoffs: Gains accurate dependency graph for all subsequent waves, but delays Wave 3 start by one investigation session. execution_impact: Read-only analysis phase; no production edits until root cause confirmed. risk_profile: Primary failure mode is inconclusive probe — blast radius is zero because no code changes occur until root cause is established; fully reversible. time_to_value: Immediate graph quality improvement; Wave 3 scope becomes trustworthy within one session. ⭐ RECOMMENDED"
    }
  ],
  allowMultiple=false
)
```

**TWO-OPTION EXAMPLE** (both above threshold, materially distinct, no dominance):
```
ask_user_question(
  question="""Recommended: Filter-only refactor
Why it wins: Delivers user-visible HITL quality improvement in one session without touching the planner or candidate generator.
What you are optimizing for: Immediate review-surface quality with minimal regression surface.
What is being traded off: Candidate over-generation upstream persists; threshold tuning will require a second pass.
Candidates evaluated: 3 | Surfaced: 2 | Suppressed (low confidence): 1 | Suppressed (non-distinct): 0""",
  options=[
    {
      label: "⭐ Filter-only refactor [0.84 HIGH]",
      description: "decision_thesis: Inserts confidence filtering and new option shape at packet-build time only, leaving the candidate generator and planner untouched. value_to_goal: Suppresses weak HITL options immediately with no upstream risk. key_tradeoffs: Gains immediate review-surface improvement but leaves upstream generation overhead in place; minimizes blast radius to serializer + tests only but delays full pipeline cleanness. execution_impact: Changes limited to HITL packet assembly; planner, routing, and L1 inference untouched. risk_profile: Primary failure mode is partial compliance where scores are assigned but threshold logic has an off-by-one; blast radius is one file plus its test; detectable via acceptance test suite. time_to_value: Immediate — surfaced within one coding session. ⭐ RECOMMENDED"
    },
    {
      label: "Full pipeline refactor [0.76 HIGH]",
      description: "decision_thesis: Restructures the entire candidate path into generate → score → filter → surface stages, eliminating over-generation at the source. value_to_goal: Creates a clean, auditable pipeline where threshold tuning in §HITL-9 config propagates automatically to all generation sites. key_tradeoffs: Gains architectural cleanliness and future tunability, but requires touching planner, scorer, serializer, and tests in one session — higher regression surface. execution_impact: Cross-cutting change affecting candidate generation, scoring, filtering, and packet serialization; requires schema migration for new option fields. risk_profile: Primary failure mode is partial refactor leaving some generation sites unpatched; blast radius spans 4–6 files; regression detectable via existing HITL tests. time_to_value: Near-term — requires a full session plus test updates before improvement is visible. recommendation_delta: Ranks below the filter-only option because the architectural cleanness gain does not justify the wider blast radius in a single session; cleanest as a follow-on wave."
    }
  ],
  allowMultiple=false
)
```

---

## §HITL-1: Mandatory HITL Decision Points

### 1.1 Code Architecture Decisions

**TRIGGER**: When multiple architectural approaches are viable AND at least one candidate clears `surface_threshold = 0.72`

**REQUIRED PIPELINE**:
1. Generate candidate architectural approaches
2. Score each: weigh SVP priorities (operational simplicity, dependency hygiene, zero-regression) against blast radius, reversibility, and test surface
3. Filter by `surface_threshold = 0.72`; apply dominance rule
4. Present surviving options using the §HITL-10 option shape with §HITL-0 packet header

**If only one approach survives scoring:** surface it alone. Do not append a strawman "keep current" option.

**Example of correctly scored single-option HITL (dominance rule fired)**:

```
ask_user_question(
  question="""Recommended: Composition over inheritance for <component>
Why it wins: Inheritance would couple <SubClass> to <BaseClass> internal state, which is mutated by three other callers in L3; composition isolates the change to one new wrapper.
What you are optimizing for: Zero blast-radius addition that does not touch existing callers.
What is being traded off: Slightly more boilerplate in the new wrapper vs a one-line subclass declaration.
Candidates evaluated: 2 | Surfaced: 1 | Suppressed (low confidence): 1 | Suppressed (non-distinct): 0""",
  options=[
    {
      label: "⭐ Composition — new wrapper class [0.88 HIGH]",
      description: "decision_thesis: Wraps <target> without modifying its interface, leaving all three existing callers in L3 untouched. value_to_goal: Implements the feature in one file with zero ripple to existing routing logic. key_tradeoffs: Gains full caller isolation, but adds one new class to maintain; the class will be trivial if <target> interface is stable. execution_impact: One new file in L<X>; no changes to existing callers; test surface is the wrapper only. risk_profile: Primary failure mode is interface drift in <target> breaking the wrapper silently; detectable via wrapper unit tests; fully reversible by deleting the wrapper. time_to_value: Immediate — single session. ⭐ RECOMMENDED"
    }
  ],
  allowMultiple=false
)
```

**EXAMPLES**:
- Choosing between inheritance vs composition
- Deciding layer placement (L0-L6) for new module
- Selecting between factory pattern vs direct instantiation
- Choosing test strategy (unit vs integration vs both)

### 1.2 Refactoring Scope

**TRIGGER**: When refactoring could affect multiple files and scope genuinely varies in risk/coverage

**REQUIRED PIPELINE**:
1. Generate scope candidates (minimal / moderate / comprehensive) only where each is a *genuinely different risk profile*
2. Score each by: blast radius, reversibility, test surface change, dependencies to update, and time to validate
3. Filter and apply dominance rule — if minimal scope clearly dominates (score ≥ 0.85, gap ≥ 0.12), surface only minimal
4. Do not fabricate a "keep current" option — if refactoring is already decided, the scope question is between real candidates only

**Scoring guidance for scope candidates**:
- Minimal scope: penalize if it leaves the root cause intact; reward if blast radius is verifiably contained
- Comprehensive scope: penalize proportionally to cross-layer coupling and test surface expansion
- If two scope options have the same risk profile with different file counts, collapse into one — they are not materially distinct

**EXAMPLES**:
- Renaming widely-used function (scope = single call site vs all callers vs full rename + shim)
- Moving module between layers (scope = move only vs move + update all imports vs move + shim + update)
- Consolidating duplicate code (scope = one instance vs all instances in one layer vs all instances cross-layer)

### 1.3 Anti-Pattern Introduction

**TRIGGER**: Before introducing any anti-pattern instance (pre_write_gate has already blocked; this HITL determines the resolution path)

**REQUIRED PIPELINE**:
1. Assess whether the specific anti-pattern can be narrowed without a guardian comment (e.g., replace `except Exception` with the 1-2 actual exception types that can occur here)
2. If narrowing is feasible — score it at ≥ 0.85 (no guardian debt, no ratchet impact, passes scanner) — dominance rule will fire; surface only that option
3. If narrowing is genuinely infeasible (e.g., third-party interface raises undocumented exceptions) — then `guardian: allow-*` becomes a scored candidate
4. Do NOT generate all four historical options reflexively; generate only the candidates that are actually viable for this specific call site

**If narrowing is feasible** (dominance rule fires — score 0.90, next best 0.62): surface only the narrow-exception option.

**If narrowing is not feasible** (two candidates above threshold): surface guardian-comment vs restructure, with restructure scored lower if it requires significant redesign that is out of scope.

**EXAMPLES**:
- New `except Exception` block at a specific call site
- New `os.path.*` call in a module that already uses `pathlib`
- Silent exception swallower in a utility function

### 1.4 Test Modification Strategy

**TRIGGER**: When a test failure has two or more genuinely credible repair paths with different correctness implications

**REQUIRED PIPELINE**:
1. Identify the failure root cause first (read the test, read the production code, read the diff)
2. Classify the root cause — is this a production bug, a stale reference, a semantic test update, or a policy regression?
3. In most cases, root cause classification resolves the ambiguity — only one repair class will be correct; surface only that one
4. HITL is only warranted when two repair classes are *both* plausible given the evidence (e.g., assertion mismatch where the correct value is genuinely ambiguous)
5. Score each plausible repair class: weight by correctness confidence, regression risk, and reversibility

**If root cause is unambiguous:** do not HITL. Fix it. One correct answer does not warrant a choice menu.

**If two repair classes are both plausible** (e.g., score 0.81 vs 0.77): surface both with the §HITL-10 shape, explaining precisely why the ambiguity exists for *this specific test and failure*.

**EXAMPLES**:
- Assertion mismatch where expected value change may reflect intentional behavior change vs regression
- Import path changed: update callers vs restore old path (only ambiguous if the rename was undocumented)
- Threshold drift where the old value may have been wrong to begin with

### 1.5 Dependency Addition

**TRIGGER**: Before adding a new external dependency where in-house implementation is non-trivial or where an existing alternative may serve

**REQUIRED PIPELINE**:
1. Check whether an existing dependency or in-repo utility already covers the need
2. If an existing alternative fully covers the need — that is the answer; no HITL required
3. If the capability gap is genuine, score: external package vs in-house implementation
4. Score external package lower if: the feature surface used is narrow (wrapping a 3-line call), the package introduces transitive dependencies, or version conflicts exist
5. Score in-house lower if: the capability requires cryptographic, protocol, or ML complexity that would take >1 session to implement safely
6. Surface only the candidates that survive the `surface_threshold`; if in-house clearly dominates, surface only that

**EXAMPLES**:
- New PyPI package where only one function is used (in-house likely dominates)
- New MCP server where existing MCP already partially covers the capability
- New system dependency where the alternative requires significant in-house work (both may survive threshold)

### 1.6 File/Module Deletion

**TRIGGER**: Before deleting or archiving any production file

**REQUIRED PIPELINE**:
1. Run reference check: any import, mention in CI gate, test fixture, or shim pointing to this file?
2. Check deprecation status: has a 90-day deprecation period elapsed?
3. Score disposition candidates based on reference count and deprecation state:
   - If references remain: archive-with-shim or deprecate-first will score higher than immediate delete
   - If zero references and deprecation elapsed: immediate archive/delete will score ≥ 0.85 (dominance likely fires)
   - If zero references but no deprecation period: archive scores higher than delete (SVP archival priority)
4. Do not generate all four dispositions reflexively — only generate the candidates that are plausible given reference count and deprecation state

**If zero references + deprecation elapsed:** dominance rule will typically fire for archive. Surface only that option.

**If active references remain:** HITL between deprecate-first and keep-as-shim; delete is not a credible candidate and should not be generated.

**EXAMPLES**:
- Agent deletion (§1.6 requirements — additional authorization gate applies)
- Utility module consolidation after migration
- Dead code removal post-refactor

### 1.7 Configuration Changes

**TRIGGER**: Before modifying governance/policy configuration where the change scope is genuinely ambiguous

**REQUIRED PIPELINE**:
1. Determine if the change is already decided (user specified the new value) — if so, no HITL; just apply it
2. If the scope or value is ambiguous, generate only the candidates that represent materially different values or rollout strategies
3. Do not add a reflexive "keep current" option — if config change is the stated goal, keeping current is not a credible candidate
4. Score by: gate coverage impact, backward compatibility, test surface affected, and rollback complexity

**EXAMPLES**:
- Confidence threshold change where the optimal value is unclear from available data
- Retry limit change where two values have different operational tradeoffs
- Layer boundary rule addition that may affect existing imports

### 1.8 Error Handling Strategy

**TRIGGER**: When the error handling strategy is genuinely ambiguous (fail-closed vs retry vs escalate each have credible arguments for this specific call site)

**REQUIRED PIPELINE**:
1. Classify the error type: transient infrastructure error, invalid input, missing configuration, resource exhaustion, or external API fault
2. Apply the constitutional default: fail-closed scores highest by default unless the specific error type is demonstrably transient
3. Transient errors (network timeouts, rate limits): retry-with-backoff becomes a credible second candidate — score both, surface if both clear threshold
4. Invalid input / missing config: fail-closed dominates; do not generate retry or escalate as candidates
5. Do not generate all four options reflexively — only generate candidates that are credible for this specific error type

**EXAMPLES**:
- External API failure: transient (retry credible) vs permanent (fail-closed dominates)
- Missing configuration at startup: fail-closed dominates; single option HITL or no HITL
- Resource exhaustion: fail-closed vs escalate (both credible if human intervention has value)

### 1.9 Performance Optimization Trade-offs

**TRIGGER**: Only when a performance optimization materially changes correctness risk or operational complexity, AND when two approaches have meaningfully different risk profiles

**REQUIRED PIPELINE**:
1. Check whether the optimization is already clearly superior (measured speedup with no correctness risk) — if so, no HITL; implement it
2. Generate candidates only when: trade-offs are non-trivial (e.g., caching introduces staleness risk, parallelism introduces ordering risk)
3. Score by: speedup magnitude, correctness risk, added complexity, reversibility, and test surface change
4. Do not generate "keep current" as a candidate unless deferring the optimization is a genuinely credible choice for the session

**EXAMPLES**:
- Caching a computation that is called ×1000/request: cache vs recompute (staleness risk is the differentiator)
- Parallelizing a pipeline stage: parallel vs sequential (ordering correctness is the differentiator)
- Index optimization: only HITL if two index strategies have meaningfully different read/write tradeoffs

### 1.10 ADG Regeneration Timing

**TRIGGER**: When ADG staleness creates a genuine risk of incorrect blast-radius analysis for the current task

**REQUIRED PIPELINE**:
1. Check staleness: compare `adg_indexed_*.sqlite` mtime against most recent `git commit` mtime
2. If ADG is fresh (newer than HEAD): no HITL — proceed
3. If ADG is stale AND the current task requires accurate blast-radius analysis (T2/T3 refactoring, cross-layer scope): regenerate now without HITL — this is the only correct answer
4. HITL is only warranted if regeneration would consume significant time AND the task can proceed safely with a known-stale graph (e.g., adding a new leaf file with no existing fanout)
5. Do not generate "Skip" as a candidate — skip is not an acceptable option for T2/T3 work

**Default behavior**: If ADG is stale during T2/T3 work, regenerate immediately. No HITL.

**EXAMPLES**:
- After refactoring imports across multiple files (stale → regenerate now, no HITL)
- After adding a single new leaf file with no callers (stale → may defer, HITL only if regeneration cost > 5 min)

---

## §HITL-2: Option Presentation Format

### 2.1 Required Elements

Every HITL prompt MUST include:
1. **Packet header** — recommended option, why it wins, optimization target, cost of winning path, suppression telemetry
2. **Options**: 1 to N surviving candidates (N is confidence-gated, NOT a fixed floor)
3. **Executive-grade analysis** for each option using the §HITL-10 shape (not generic pros/cons)
4. **Confidence score and band** on every option label

### 2.2 Forbidden Patterns

**NEVER**:
- Generate a minimum of 2, 3, or 4 options to satisfy a count
- Add a "keep current" option when the action is already decided
- Pad with options that are cosmetically different but operationally identical
- Use generic pros/cons ("more flexible", "higher risk", "easier to maintain") without tying the claim to the specific code path, architecture, or governance consequence
- Proceed with "default" option without user selection (when HITL is required by policy)
- Make the decision and then ask for approval
- Use the same tradeoff language across multiple options
- Label multiple options as Recommended

### 2.3 Option Quality Standards

Each surfaced option MUST:
- Clear `surface_threshold = 0.72`
- Be **materially distinct** from every other surfaced option (different on ≥1 of: execution path, risk profile, reversibility, expected outcome, dependency set, time/cost tradeoff, governance consequence)
- Use the **§HITL-10 option shape** — no generic pros/cons
- Have **case-specific analysis** — every claim tied to this repo, this packet, this routing path, or this specific decision

### 2.4 LOW\_CONFIDENCE\_AMBIGUITY Packet

When no candidate clears `surface_threshold = 0.72`:

```
LOW_CONFIDENCE_AMBIGUITY
Best candidate: <option_title> [<score> <band>]
Rationale: <why no option is surfaced>
Recommended action: clarify / replan / abstain
Blocking question: <what information would resolve the ambiguity>
```

Do not fabricate options to fill this packet. Do not surface the best candidate as a real option. Route to clarify/replan/abstain.

---

## §HITL-3: Execution Discipline

### 3.1 Wait for Selection

After presenting options:
1. **STOP** — do not proceed with any option
2. **WAIT** — user must explicitly select A, B, C, or D
3. **CONFIRM** — acknowledge selection before executing
4. **EXECUTE** — only the chosen option

### 3.2 No Assumptions

**FORBIDDEN**:
- "I'll proceed with Option A unless you object"
- "Option B seems best, so I'll do that"
- "Let me know if you want something different"
- Implementing multiple options "to give you choices"

### 3.3 Clarification Protocol

If user response is ambiguous:
1. Restate the options
2. Ask for explicit A/B/C/D selection
3. Do not guess intent

---

## §HITL-4: Bypass Conditions

HITL may be bypassed ONLY when:

1. **Trivial changes** — fixing typos, formatting, whitespace
2. **Deterministic fixes** — single correct solution (syntax errors, import errors)
3. **Explicit user directive** — user said "just do X" with no ambiguity
4. **Emergency rollback** — reverting broken commit
5. **Auto-fixable violations** — ruff, trailing whitespace, etc.
6. **Dominance rule fires** — one candidate scores ≥ 0.85 with gap ≥ 0.12 to next; surface that single option, do not treat as bypass (still requires user acknowledgment if policy-required)

**HITL is NOT required when**: scoring produces one clear answer. In that case, surface a single-option HITL packet rather than proceeding without user acknowledgment (if the decision has meaningful governance or irreversibility consequences), or proceed directly (if the action is low-risk and reversible).

---

## §HITL-5: Evidence Requirements

When HITL is invoked, evidence file MUST include:

```markdown
## HITL_DECISION_RECORD

**Decision Point**: <description>
**Options Presented**: A, B, C, D
**User Selection**: <A|B|C|D>
**Rationale**: <user's stated reason, if provided>
**Executed Action**: <what Cascade did>
```

---

## §HITL-6: Enforcement

### 6.1 Windsurf Layer

This is a **behavioral rule** enforced during AI execution. No pre-commit hook can verify HITL compliance.

### 6.2 Audit Trail

All HITL decisions MUST be recorded with:
- **Decision Point**: Clear description of the decision
- **Timestamp**: ISO8601 timestamp of decision
- **Options Presented**: All options A/B/C/D with pros/cons
- **User Selection**: Which option was selected
- **Rationale**: User's stated rationale (if provided)
- **Impact**: Expected impact of the decision
- **Evidence File**: Path to evidence file containing this record

Audit trail MUST be stored in evidence files under `docs/reports/plans/`.
Missing audit trail = constitutional violation.
- Evidence files (`docs/reports/plans/`)
- Commit messages (when applicable)
- Plan updates (when scope changes)

### 6.3 Violation Consequences

Proceeding without HITL when required:
- Violates user trust
- May result in wasted work
- Requires rollback and re-execution with HITL

---

## §HITL-7: Quick Reference

| Scenario | HITL Required? | Bypass Allowed? |
|----------|----------------|-----------------|
| Multiple architectural approaches | ✅ YES | ❌ NO |
| Refactoring >3 files | ✅ YES | ❌ NO |
| Adding anti-pattern | ✅ YES | ❌ NO |
| Test failure with multiple fixes | ✅ YES | ❌ NO |
| Adding external dependency | ✅ YES | ❌ NO |
| Deleting production file | ✅ YES | ❌ NO |
| Changing governance config | ✅ YES | ❌ NO |
| Error handling strategy | ✅ YES | ❌ NO |
| Performance vs complexity | ✅ YES | ❌ NO |
| ADG regeneration timing | ✅ YES | ✅ YES (if clearly no impact) |
| Fixing typo | ❌ NO | ✅ YES |
| Auto-formatting | ❌ NO | ✅ YES |
| Syntax error fix | ❌ NO | ✅ YES (if single correct solution) |
| User said "just do X" | ❌ NO | ✅ YES (if unambiguous) |

---

## §HITL-8: Integration with Existing Rules

HITL complements but does not replace:
- **§0 DEFAULT ANALYSIS MODE** — still build ADG first, then present options
- **§1 TESTING FRAMEWORK** — still require tests, but let user choose test strategy
- **§2 ADG FRAMEWORK** — still use graph, but let user choose scope
- **§9 EXECUTION MODALITY** — still work in phases, but let user choose phase boundaries

**HITL adds**: User choice at decision points
**HITL does not remove**: Technical requirements and quality gates

---

## §HITL-9: Confidence Policy Configuration

All HITL thresholds are centralized here. Do not hardcode these values elsewhere.

```yaml
hitl_option_policy:
  surface_threshold: 0.72          # minimum confidence to surface any option
  high_confidence_band: 0.85       # threshold for HIGH band label
  medium_confidence_band: 0.72     # threshold for MEDIUM band label (>= 0.72 and < 0.85)
  low_confidence_band: 0.00        # anything below surface_threshold is suppressed
  dominance_score_threshold: 0.85  # top option must score >= this to trigger dominance rule
  dominance_delta: 0.12            # top - next_best must be >= this for dominance to fire
  max_surface_options: 4           # hard cap; never show more than this
  require_material_distinctness: true
  allow_single_option_hitl: true   # single-option surface is explicitly allowed
  telemetry_emission: true         # emit scoring/suppression stats in packet header
```

### Confidence Band Labels

| Score | Band | Label in option title |
|-------|------|-----------------------|
| ≥ 0.85 | HIGH | `[0.87 HIGH]` |
| 0.72–0.84 | MEDIUM | `[0.76 MEDIUM]` |
| < 0.72 | LOW | suppressed — do not surface |

### Scoring Guidance

Confidence scores are not arbitrary. Anchor them to concrete evidence:
- **≥ 0.85**: The approach is clearly correct for this situation, reversible, blast radius is contained, and SVP priorities align
- **0.72–0.84**: The approach is credible and defensible but has non-trivial tradeoffs or unknowns
- **< 0.72**: The approach has significant unknowns, high blast radius, or conflicts with constitutional constraints
- **0.50 and below**: Do not generate this as a surfaced option; include in suppression telemetry only

---

## §HITL-10: Option Shape Contract

Every surfaced HITL option MUST use the following fields. Generic pros/cons are FORBIDDEN.

```
option_title: <short imperative title>
confidence_score: <float, e.g. 0.84>
confidence_band: HIGH | MEDIUM
recommendation_status: RECOMMENDED | ALTERNATIVE

decision_thesis:
  One sentence. What this option actually does and why someone would rationally choose it.
  Must reference the actual system, component, or workflow being changed.

value_to_goal:
  What concrete value does this create for the stated objective?
  Tie it to the current request, repo state, or execution path.

key_tradeoffs:
  3 to 5 precise tradeoffs, each framed as:
  - Gains X, but increases Y because Z
  - Reduces A, but constrains B in this part of the workflow
  - Improves C now, but creates D follow-on work later
  Every claim must be tied to this specific architecture, code path, or governance consequence.

execution_impact:
  What changes operationally if this option is chosen:
  - which files/layers are touched
  - localized vs cross-cutting
  - test surface expansion
  - config migration requirement
  - backward compatibility considerations

risk_profile:
  Do not say only low/medium/high. State:
  - primary failure mode (what specifically breaks or degrades)
  - blast radius (which files, layers, callers are affected)
  - detectability (how quickly would a regression surface)
  - reversibility (what it takes to undo)

dependencies_and_prereqs:
  Only list prerequisites that materially matter:
  - schema migration
  - config centralization
  - packet serializer change
  - eval telemetry update
  - backward-compat handling
  No filler.

time_to_value:
  State whether value is immediate, near-term, or delayed and why:
  - immediate: visible in this session
  - near-term: requires test/consumer updates before improvement is live
  - delayed: requires evaluation data before the change pays off

why_not_default:
  (Required for non-top options only)
  Why this option should not automatically be chosen if it is not the top recommendation.

recommendation_delta:
  (Required for non-top options only)
  Relative to the top option, explain precisely why this option ranks lower.
  Do not repeat the same wording from the top option's analysis.
```

### Banned Weak Phrasing

Do not use any of the following unless immediately followed by a *concrete, architecture-specific explanation*:
- more flexible, more scalable, simpler, more robust, easier to maintain
- higher effort, lower risk, better long-term, more extensible, cleaner
- faster to implement (without specifying what implementation it replaces and why)

**Instead, force specificity:**
- centralizes threshold policy in one config surface, which reduces drift across hook generators
- preserves backward compatibility for existing HITL packet consumers, but delays schema cleanup by one wave
- minimizes code churn by changing only the option-filtering stage, but leaves candidate-generation inefficiency untouched

---

## §HITL-11: Telemetry for Evaluation Spine

Every HITL invocation MUST emit structured telemetry in the packet header (not stored externally; included in the `question` field so it is visible in the audit trail):

```
Candidates evaluated: <N>
Suppressed (low confidence): <X> (scored below 0.72)
Suppressed (non-distinct): <Y> (collapsed into surviving option)
Surfaced: <M>
Top confidence score: <score>
Confidence delta (top vs next): <delta or N/A if single option>
```

This telemetry is for future threshold tuning. It is logged but does not mutate live policy.

---

## MAXIM

- **Signal over count.** One strong option beats three padded alternatives.
- **Dominance fires cleanly.** When the answer is clear, surface it and say so.
- **Threshold gates confidence.** Below 0.72 means clarify, replan, or abstain — not fabricate.
- **Distinctness is required.** Cosmetic variants do not warrant separate options.
- **Analysis is executive-grade.** Every claim tied to the actual architecture, not generic software advice.
- **Wait for choice.** When HITL fires, do not proceed without user selection.

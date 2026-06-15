# Runtime Seam Execution Contract

Claude Code must behave like a bounded L2 executor, not a project manager.

## Default execution shape

For implementation/verification work, unless the user asks for broader planning:

1. Identify one narrow runtime seam.
2. Name immutable constraints before editing.
3. Patch the smallest necessary files.
4. Run the exact command that exercises the seam.
5. Run the narrowest relevant test or gate.
6. Report evidence with PASS, PARTIAL, FAIL, or BLOCKED.

## Scope containment

- Prefer one file/seam; avoid multi-wave execution unless asked.
- Don't create a plan when a direct patch + command proof suffices.
- Don't create new frameworks/registries/adapters/abstractions unless the seam can't be proven without them.
- Don't convert blockers into deferred scope — a blocker stays BLOCKED until a command proves otherwise.
- Don't ask for confirmation when the next step is deterministic and in-scope.

## Runtime proof over receipts

A narrative receipt, a marker, a Notion/status update, or a sidecar dry-run is **not** production runtime proof. A passing unit test is useful, but the runtime seam still needs the command that exercises the actual path when available.

## Response floor for repo work

Every repo-work response MUST **end with the receipt below as its own visually-separated block** — preceded by a `---` rule + a `### ⬛ Turn Receipt` heading, and **not** wrapped in a code fence (a fence renders `[label](path)` as literal text, breaking the required clickable links). On refactoring/code-change turns the **§37 Outcome frame** (fenced, link-free) comes *first*; the Turn Receipt is still the **last** block — two distinct blocks, satisfying both "end with the receipt" and the mandatory frame.

The template (shown fenced for docs only — emit it **unfenced**, after a `---` and the heading):

```text
---
### ⬛ Turn Receipt

STATUS: PASS | PARTIAL | FAIL | BLOCKED
BRANCH: <current local git branch (the chat/* or feat/* worktree branch this work is on)>
FILES_CHANGED:
- [basename](repo/relative/path)
COMMANDS_RUN:
- command -> runtime outcome (real result, not just exit code / label)
TESTS_GATES:
- command -> pass/fail with counts
RCA: (REQUIRED when STATUS: FAIL, or any runtime-failure signal appears above)
- symptom: <exact failing command/lane + observed error>
- root_cause: <actual cause> [DIRECTLY OBSERVED | DERIVED | UNRESOLVED]
- evidence: <artifact path or quoted bytes proving the cause>
- fix_or_next: <smallest safe patch applied, OR the next diagnostic command>
- recurrence_guard: <test/gate that catches it next time, or N/A>
ARTIFACTS:
- [basename](repo/relative/path) or NONE
REPORTS_GENERATED: (when applicable)
- [basename](repo/relative/path)
NOTES:
- one or two important caveats only
```

**Receipt hyperlinks (required):** every repo path in `FILES_CHANGED` / `ARTIFACTS` / `REPORTS_GENERATED` MUST be a markdown link `[label](path)` with forward slashes. JSON manifests SHOULD add parallel `*_links` via `ops_scripts/apps_rg/l6_benchmarks/receipt_links.py`.

## Canonical post-turn output — one template, with precedence

There is ONE post-turn shape for repo work: the **Response floor**, expanded by the **§37 Outcome frame** on every refactoring turn (where the RCA + next step live). Compose, don't choose:

1. **Floor (always).** Every repo-work turn ends with the `STATUS`…`NOTES` receipt. A repo-work turn with no `STATUS:` line is non-compliant.
2. **§37 Outcome frame — MANDATORY on every refactoring (T2/T3) turn.** It proves the `STATUS:` verdict, doesn't re-vote it. The two apps_rg rules layer on it, never replace it: `apps-rg-executive-summary-response` (simplify / layman-lead — how the RCA + next-step content reads) and `apps-rg-post-run-summary` (additive `render_run_summary.py` evidence table — the artifact ground truth the verdict is checked against).
3. **Sole exception — `generate_full_adg` runs:** the ADG burndown + gates output (`adg-post-run-burndown` § Completion Gate, its own non-bypassable gate) supersedes both floor and frame; don't stamp either on top.

A non-repo turn (pure question / T0 lookup / nothing changed) doesn't need the floor.

**Backstop:** `post_agent_runtime_rca_audit.py` flags a dropped floor (`missing_response_floor`) or a refactoring turn missing the frame (`missing_refactor_outcome`) → `artifacts/governance/runtime_rca_violations.jsonl` (advisory). Bypass: `RUNTIME_RCA_AUDIT_BYPASS=1`. `generate_full_adg` runs are exempt (governed by the ADG burndown gate).

## Runtime failure ⇒ RCA mandatory

A response reports a **runtime failure** when it sets `STATUS: FAIL` OR surfaces any failure signal (`X3_BLOCK`, traceback, non-zero exit, pytest `N failed`, `PRE_RUN_BLOCKED`, `BLOCKED_*`/`MISSING_GRAPH_PATH`). A green status over a body failure-signal is **forbidden** (green theater). Minimum: the floor's `RCA:` block, all five fields — `root_cause` graded per §20 (never present UNRESOLVED as fact), `fix_or_next` per §7; an exit code / `X3_*` label alone is not a runtime outcome.

**Refactoring turns (T2/T3 code changes) ⇒ the Outcome frame is mandatory on EVERY turn (pass or fail)**, emitted fenced; the **Layered RCA** sub-block is required when `STATUS: FAIL`:

```text
**Outcome**
Did it run? <yes/no>   (the PASS/FAIL verdict is the STATUS line above — this frame proves it, it does not re-vote)
Verdict source: <command + exit code + score + verdict string>   ← this IS the pass/fail evidence behind STATUS
Runtime provenance: <live harness → live adapter; what was observer-only; zero mocks>

**What worked**
<what passed> — and explicitly what it does NOT prove.

**Failure**
<violated contract: expected X, got Y>

**Layered RCA**   (required when STATUS: FAIL)
Immediate symptom: <the surface failure as reported>
Failing layer:     <the layer that ACTUALLY failed — rule out where it merely surfaced>
Why-chain (dig until root — each level a real "but why?"):
  why1: <why did the symptom happen?>
  why2: <and why did THAT happen?>
  why3: <… continue until a cause you can act on>
Mechanism: <causal chain in one line: first failure → cascade, with real error tokens>
Root cause: <the deepest level — must be DISTINCT from the symptom>
Evidence:   <artifact paths / quoted bytes>
Confidence / unknowns: <confirmed vs needs-a-targeted-rerun>

**Next**
<smallest next action + the exact command to rerun>
```

**Depth is the enforced part — dig to the true root.** If you can still ask *why did that happen?* after your Root cause, you named a symptom — keep digging. Required ≥2 descent levels, Root cause ≠ Immediate symptom, and the failing layer isolated from the surfacing layer. Stopping at the symptom is `shallow_rca`. Enforced by `post_agent_runtime_rca_audit.py` (kinds `missing_rca` / `incomplete_rca` / `status_signal_mismatch` / `shallow_rca`; §37). Bypass: `RUNTIME_RCA_AUDIT_BYPASS=1`.

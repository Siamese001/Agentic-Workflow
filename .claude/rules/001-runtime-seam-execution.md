
# Runtime Seam Execution Contract

Claude Code must behave like a bounded L2 executor, not a project manager.

## Default execution shape

For implementation or verification work, use this shape unless the user explicitly asks for broader planning:

1. Identify one narrow runtime seam.
2. Name immutable constraints before editing.
3. Patch the smallest necessary files.
4. Run the exact command that exercises the seam.
5. Run the narrowest relevant test or gate.
6. Report evidence with PASS, PARTIAL, FAIL, or BLOCKED.

## Scope containment

- Prefer one file or one seam. Avoid multi-wave execution unless the user explicitly asks for it.
- Do not create a plan when a direct patch plus command proof is possible.
- Do not create new frameworks, registries, adapters, prompts, or broad abstractions unless the seam cannot be proven without them.
- Do not convert blockers into deferred scope. A blocker remains BLOCKED until a command proves otherwise.
- Do not ask for confirmation when the next step is deterministic and already inside the user’s requested scope.

## Runtime proof over receipts

- A narrative receipt is not proof.
- A marker is not proof.
- A Notion/status update is not proof.
- A sidecar dry run is not production runtime proof.
- A passing unit test is useful, but the runtime seam still needs the command that exercises the actual path when available.

## Response floor for repo work

Every repo-work response must include:

```text
STATUS: PASS | PARTIAL | FAIL | BLOCKED
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

**Receipt hyperlinks (required):** In chat responses and companion `*_receipt.md` / manifest JSON, every repo path in `FILES_CHANGED`, `ARTIFACTS`, and `REPORTS_GENERATED` MUST be a markdown link `[label](path)` using forward slashes (e.g. `[human_benchmark_plan.md](artifacts/apps_rg/plans/human_benchmark_plan.md)`). JSON manifests SHOULD also include parallel `*_links` objects via `ops_scripts/apps_rg/l6_benchmarks/receipt_links.py` (`path` + `markdown` fields).

## Canonical post-turn output — one template, with precedence

> ⛔ There is **ONE** post-turn shape for repo work: the **Response floor**, expanded by the **§37
> Outcome frame** on every refactoring turn (the frame is where the RCA + next step live). The apps_rg
> "run-summary" / "layman-lead" guidance is about *simplifying* that RCA + next-step content — it is
> **not** a separate post-turn template. The **sole exception** is a `generate_full_adg` run, where the
> BCG-grade ADG burndown + gates template is enforced instead. Picking a different shape per turn — or
> dropping the floor/frame for free-form prose — is the inconsistency this section exists to stop.

**The base is non-optional.** Every repo-work turn ends with the **Response floor** above
(`STATUS` … `NOTES`). It is the base template — not one option among several. A repo-work turn
(files changed, commands run, tests/gates exercised) that wraps up in plain prose **with no
`STATUS:` line** is non-compliant, even when the prose is correct.

**Precedence — compose, don't choose:**

1. **Floor (base, always).** Every repo-work turn starts from the `STATUS` … `NOTES` receipt.
2. **§37 Outcome frame — MANDATORY on every refactoring (T2/T3 code-change) turn.** It is the floor's
   runtime-evidence expansion and the home of the **RCA and the next step** (see "Runtime failure ⇒
   RCA mandatory" below). It proves the `STATUS:` verdict; it does not re-vote it. Two apps_rg rules
   layer on this frame for apps_rg runs and never replace it:
   - `apps-rg-executive-summary-response.md` is a **simplify / layman-lead** standard — it shapes *how
     the RCA + next-step content reads* (plain English first, jargon later).
   - `apps-rg-post-run-summary.md` is an **additive evidence** specialization — the tool-rendered
     `render_run_summary.py` provenance table (the artifact-derived ground truth the frame's verdict is
     checked against), not a simplification.
   Neither is a separate post-turn template.
3. **Sole exception — `generate_full_adg` runs.** On a `generate_full_adg` / `run_full_adg_audit` /
   `adg_gates/run.py` run, the BCG-grade ADG burndown + gates output (`adg-post-run-burndown.md`
   § Completion Gate, its own non-bypassable gate + own audit `post_agent_adg_burndown_inline_audit.py`)
   is enforced — **and only that.** It supersedes both the floor and the Outcome frame; do not stamp
   either on top of it. The backstop below defers ADG runs to that gate entirely.

A non-repo turn (a pure question, a T0 lookup, a chat that changed nothing) does not need the floor.

**Backstop.** `post_agent_runtime_rca_audit.py` flags a repo-work turn that drops the floor
(`missing_response_floor` — a floor signal `FILES_CHANGED:` / `COMMANDS_RUN:` / `TESTS_GATES:` /
`ARTIFACTS:` / `REPORTS_GENERATED:` or an edit-tool invocation but **no `STATUS:` line**) or a
refactoring turn missing the Outcome frame (`missing_refactor_outcome`), logged to
`artifacts/governance/runtime_rca_violations.jsonl`. Advisory (never blocks). Bypass:
`RUNTIME_RCA_AUDIT_BYPASS=1`. **`generate_full_adg` runs are fully exempt** — their output is governed
by the BCG/ADG burndown completion gate (point 3), not by this floor or the Outcome-frame check.

## Runtime failure ⇒ RCA mandatory

A response reports a **runtime failure** when it sets `STATUS: FAIL` **or** surfaces any
runtime-failure signal in its receipt — `X3_BLOCK`, a Python traceback, a non-zero exit, a pytest
`N failed`, `PRE_RUN_BLOCKED`, or a `BLOCKED_*` / `MISSING_GRAPH_PATH` verdict. A green/optimistic
status (`PASS` / `PARTIAL`) over a body that carries a runtime-failure signal is **forbidden** — the
green-theater pattern this contract exists to stop.

**Minimum (any runtime failure).** The floor's `RCA:` block, all five fields:

- `root_cause` graded per §20 (DIRECTLY OBSERVED / DERIVED / UNRESOLVED) — never present UNRESOLVED as fact.
- `fix_or_next` honours §7 (RCA auto-closure): apply the safe in-scope fix this turn; else name the exact next command.
- An exit code or an `X3_*` label alone is **not** a runtime outcome — `COMMANDS_RUN` / `TESTS_GATES` show the real result.
- `BLOCKED` (missing key / service / permission) names its blocker; it needs an `RCA:` block only when a failure signal is also present.

**Refactoring turns (T2/T3 code changes) ⇒ the Outcome frame is mandatory on EVERY turn (pass or fail)**, emitted as a fenced block — its absence is `missing_refactor_outcome`. The frame is the **runtime-evidence expansion of the `STATUS:` disposition**, not a second verdict: the `STATUS:` line (above, on every repo turn) is the single `PASS/PARTIAL/FAIL/BLOCKED` verdict, and the frame *proves* it via the verdict source — it does not re-vote pass/fail. The **Layered RCA** sub-block is required when `STATUS: FAIL` (the verdict source shows failure):

```text
**Outcome**
Did it run? <yes/no>   (the PASS/FAIL verdict is the STATUS line above — this frame proves it, it does not re-vote)
Verdict source: <command + exit code + score + verdict string>   ← this IS the pass/fail evidence behind STATUS
Runtime provenance: <live harness → live adapter; what was observer-only; zero mocks>

**What worked**
<what passed> — and explicitly what it does NOT prove.

**Failure**
<violated contract: expected X, got Y>

**Layered RCA**   (required when STATUS: FAIL — the verdict source shows failure)
Immediate symptom: <the surface failure as reported>
Failing layer:     <the layer that ACTUALLY failed — rule out the layer where it merely surfaced>
Why-chain (dig until root — each level a real "but why?", keep going even if many levels):
  why1: <why did the symptom happen?>
  why2: <and why did THAT happen?>
  why3: <… continue until a cause you can act on>
Mechanism: <causal chain in one line: first failure → cascade, with real error tokens>
Root cause: <the deepest level — must be DISTINCT from the symptom>
Evidence:   <artifact paths / quoted bytes proving the layer, the why-chain, and the cause>
Confidence / unknowns: <confirmed vs needs-a-targeted-rerun>

**Next**
<smallest next action + the exact command to rerun>
```

**Depth is the enforced part — dig to the true root, even across many levels.** The *"but why?"*
test: if you can still ask *why did that happen?* after your Root cause, you named a **symptom** —
keep digging. Required descent ≥ 2 levels (Failing-layer / Mechanism / `whyN` lines), Root cause ≠
Immediate symptom, and the **failing layer isolated from the surfacing layer** — *where it showed up
≠ where it broke ≠ why it broke*. Stopping at the symptom is non-compliant (`shallow_rca`).

Enforced by `post_agent_runtime_rca_audit.py` → `artifacts/governance/runtime_rca_violations.jsonl`
(advisory; kinds `missing_rca` / `incomplete_rca` / `status_signal_mismatch` / `shallow_rca`;
constitutional §37). Bypass: `RUNTIME_RCA_AUDIT_BYPASS=1`.

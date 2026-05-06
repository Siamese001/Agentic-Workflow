---
trigger: model_decision
description: Apply when about to invoke `python -m apps_rg`, when the user mentions running apps_rg, or when discussing apps_rg target-company / target-role / JD / briefing inputs. Enforces Cascade behavioral discipline that complements the in-app interactive wizard and cross-company contamination guard.
---

# apps_rg Interactive Discipline — Cascade Must Not Auto-Fill the 3 Mandatory Inputs

> ⛔ When the user invokes `python -m apps_rg` (or asks Cascade to run it), Cascade MUST NOT pre-fill `--target-company`, `--target-role`, `--jd`, or `--manual-brief` from inferred context. The in-app interactive wizard owns those decisions.

Sibling to `scope-containment.md` (no gold-plating, no scope expansion). That rule says "don't widen scope"; this one says "don't substitute Cascade's pattern-match for an explicit user decision on which company to target".

## Why this rule exists

`apps_rg` produces a generated resume. Three inputs determine which company / role / framing the resume targets:

1. **Company** — `--target-company` (e.g. "Brown & Brown")
2. **JD** — `--target-role` + `--jd` (title + full description)
3. **Briefing** — `--manual-brief` path or `--auto-research-tavily` to delegate to apps_research

If Cascade auto-fills any of these from prior turns, scrollback filenames, or `apps_rg/scripts/` artifacts, the result can be a resume targeting the *wrong company* — a cross-company contamination defect. The repo's history of 60+ stale `generated_resume_*.json` files in `apps_rg/scripts/` shows this has occurred repeatedly.

The in-app fix: `apps_rg/__main__.py::main()` now runs `_interactive_wizard(args)` when stdin is a TTY and any mandatory input is missing. The wizard prompts the user explicitly for each of the 3 items and writes them to dedicated `_interactive_*.json` files (which the cross-company contamination guard then validates).

This rule is the **behavioral complement**: prevent Cascade from circumventing the wizard by pre-filling the flags before the wizard ever runs.

## Hard rules

### 1. Default invocation is verbatim

When the user types `python -m apps_rg` (or "run apps_rg", "generate a resume with apps_rg", etc.) without explicitly naming a company/role/JD in the SAME turn:

- Cascade MUST run the command exactly as typed.
- Cascade MUST NOT add `--target-company`, `--target-role`, `--jd`, or `--manual-brief` flags.
- The in-app wizard will prompt the user for the 3 mandatory inputs.

### 2. Cascade MAY surface available context

Before/after running the command, Cascade MAY observe what files exist in `apps_rg/scripts/` (e.g. "the wizard will prompt; if helpful, `jd_brown_brown_svp_it_strategy.json` and `job_description_brownandbrown.json` are on disk"). This is informational — it does NOT pre-fill flags.

### 3. Explicit in-turn authorization is the only override

Cascade MAY auto-fill the flags ONLY when the user, in the SAME turn, explicitly names ALL of company + role. Examples:

- ✅ "Run apps_rg for Brown & Brown SVP IT Strategy" → Cascade MAY add `--target-company "Brown & Brown" --target-role "SVP IT Strategy"`. The JD and briefing still go through the wizard unless the user names a specific file path.
- ❌ "Run apps_rg" (no company/role) → Cascade MUST NOT infer from prior turn or file listings.
- ❌ "Run apps_rg again" → Cascade MUST NOT reuse target-company from prior session memory.

### 4. Stale-file scan is forbidden as a flag source

Cascade MUST NOT scan `apps_rg/scripts/` for `jd_*.json`, `company_research*.json`, or any other artifact and use a discovered filename as a `--jd` or `--manual-brief` value without explicit user authorization. The wizard's `@path/to/file` syntax is the user-facing path for this.

### 5. Non-TTY contexts (CI, piped, automation) are different

When apps_rg runs non-interactively (CI scripts, batch runs), the wizard does NOT fire — `parser.error()` hard-fails on missing flags. In those contexts, the operator scripting the run MUST supply the flags explicitly. This rule does not apply to scripted automation; it applies to Cascade-mediated interactive sessions.

## Forbidden patterns

- ❌ `python -m apps_rg --target-company "<inferred from filename>" --target-role "<inferred from filename>"` when the user did not name the company/role in the current turn.
- ❌ Reading `apps_rg/scripts/jd_<x>.json` to extract a title and using it as `--target-role`.
- ❌ Reading `apps_rg/scripts/company_research.json` and using its `company` field as `--target-company`.
- ❌ Reusing a `target-company` value from prior conversation context.
- ❌ "Helpfully" running apps_rg with the most recent JD file's company while the user is still framing what they want.

## Defense-in-depth layers

| Layer | Mechanism | Where |
|---|---|---|
| 1. Code-side wizard | TTY-only `_interactive_wizard()` prompts for the 3 inputs | `apps_rg/__main__.py` |
| 2. Cross-company guard | `_assert_artifact_matches_company()` raises if JD/briefing company ≠ `--target-company` | `apps_rg/__main__.py` |
| 3. Test guard | `tests/_apps_contract/test_apps_rg_cross_company_contamination_guard.py` | tests/ |
| 4. **Cascade behavioral rule** | This file — Cascade does not pre-fill the 3 flags | `.windsurf/rules/` |

Layers 1–3 are runtime/test enforcement. This rule is the pre-emptive layer: stop the wrong command from being constructed in the first place.

## Sibling apps

When `apps_underwriting_ai`, `apps_qna`, `apps_rfp`, `apps_research`, `apps_lic`, `apps_exec` adopt similar wizard patterns for their target/scope inputs, extend the rule scope to cover them. Today (2026-05-06) the rule scope is `apps_rg` only because only `apps_rg` has the wizard.

## Empirical incident — why this rule was written (2026-05-06)

User typed `python -m apps_rg`. Cascade auto-filled `--target-company "Brown & Brown" --target-role "SVP IT Strategy" --jd apps_rg/scripts/jd_brown_brown_svp_it_strategy.json` based on:

- A JD file committed earlier in the same session
- Brown & Brown context from prior C0 brief synthesis testing

The cross-company contamination guard caught the mismatch (the auto-loaded `apps_rg/scripts/company_research.json` was Blend360-targeted, not Brown & Brown). Hard-fail prevented contamination, but only because the stale brief was for a different company. If both stale files had matched the same wrong prior company, the resume would have shipped silently.

User RCA: "this is not working — always mandatory interactive to prompt three items — can mention what it loaded but cannot auto run". Wizard added in `apps_rg/__main__.py` (commit `d613a5c18a`); this rule is the behavioral complement.

## References

- Constitutional §6 (Author-Gate for ambiguous decisions)
- Constitutional §18 (no hidden scope expansion)
- `scope-containment.md` (sibling — no gold-plating, no scope creep)
- `apps_rg/__main__.py::_interactive_wizard` (the prompt this rule defers to)
- `apps_rg/__main__.py::_assert_artifact_matches_company` (the runtime guard)
- `tests/_apps_contract/test_apps_rg_cross_company_contamination_guard.py`

# Cross-App Integration Patterns

> **Status**: documented 2026-05-01; expanded same day with pattern (3) after follow-up scan revealed bare-subprocess consumers
> **Scope**: how `apps_*` apps integrate with each other without direct coupling
> **Three patterns documented**: (2) typed facade, (3) bare subprocess CLI; (1) direct cross-app imports remain forbidden

## Why these patterns exist

Cross-app direct imports (e.g. `apps_eval` directly importing from `apps_rg`) are forbidden by the layer-gravity invariants in this repo's architecture. Every `apps_*` is a peer; none owns another. But real workflows sometimes require one app to invoke another's capabilities — `apps_eval` running scenarios that exercise `apps_rg`, `apps_rg` consuming a company brief produced by `apps_research`, etc.

The repo solves this with **two complementary patterns**:

- **Pattern (2): typed facade** in `apps_shared/adapters/`. Narrow, app-agnostic adapter that one peer app imports to invoke another peer's entrypoint with a typed contract. Wraps subprocess-CLI invocation with input/output validation.
- **Pattern (3): bare subprocess CLI**. Consumer directly calls `subprocess.run([sys.executable, "-m", "apps_<producer>", ...])` and parses the resulting JSON artifact. No facade abstraction; loosest possible coupling.

Both patterns leave the target app structurally isolated from its consumers — there's no `imports` edge into the producer's tree. The consumer's `imports` edge goes into either `apps_shared/` (pattern 2) or just standard library (`subprocess`) (pattern 3). Layer-gravity holds.

Which pattern to choose:

| Need | Use |
|---|---|
| Stable typed contract; consumer wants `CompanyBrief`, not raw JSON | Pattern (2) |
| Cache management, retries, fallback chains | Pattern (2) |
| One-shot or experimental wiring; producer's JSON is the contract | Pattern (3) |
| Many consumers calling the same producer | Pattern (2) (DRY the subprocess + parsing logic into the facade) |
| Single consumer with bespoke parsing | Pattern (3) |

## Pattern (2) examples — typed facade

### 2.1 `rg_orchestrator_facade.py` — apps_eval ↔ apps_rg scenario runner

**Path**: `apps_shared/adapters/rg_orchestrator_facade.py`

**Producer**: `apps_rg`'s orchestrator surface (resume generation pipeline)

**Consumer**: `apps_eval/engines/scenario_runner.py` (2 imports per ADG snapshot 05012026_0632)

**Shape** (typical for this pattern):

- The facade exposes a thin contract (function or class) that the consumer can import.
- Internally, the facade resolves apps_rg's orchestrator and dispatches the work.
- The consumer never imports from `apps_rg.*` directly.

**Why it works**: scenario evaluation is a one-way dependency (eval needs to drive rg, never the reverse). The facade encodes that direction.

### 2.2 `research_facade.py` — apps_rg ↔ apps_research subprocess CLI

**Path**: `apps_shared/adapters/research_facade.py` (164 lines)

**Producer**: `apps_research` invoked as a subprocess CLI (`python -m apps_research --mode company`)

**Consumer**: `apps_rg/integrations/company_research_loader.py` (mode 2 of the 4-mode CompanyBrief loader; see HOP-0.6-COMPANY-RESEARCH in `.claude/plans/apps-rg-narrative-and-company-research-e3f8c1.md`)

**Shape**:

```python
# In the consumer:
def _try_apps_research(opts) -> Optional[CompanyBrief]:
    try:
        from apps_shared.adapters.research_facade import fetch_company_brief
    except ImportError as exc:
        _log.warning(...)
        return None
    try:
        return fetch_company_brief(
            company=opts.target_company,
            jd_path=opts.jd_path,
            depth=opts.depth,
            cache_max_age_days=opts.cache_max_age_days,
        )
    except CompanyBriefMissingError as exc:
        _log.warning(...)
        return None
```

```python
# In the facade:
def fetch_company_brief(*, company, jd_path=None, depth="standard",
                       cache_max_age_days=30, cache_root=None):
    """Synchronous invocation of apps_research --mode company.

    Returns a validated CompanyBrief or raises CompanyBriefMissingError.
    Caches results under artifacts/apps_research/runs/<ts>/.
    """
    # 1. Try cache (artifacts/apps_research/runs/*/company_research.json)
    # 2. subprocess.run(["python", "-m", "apps_research", "--topic", company, ...])
    # 3. Parse the resulting artifact and return CompanyBrief.model_validate(...)
```

**Why it works**: the facade owns the subprocess invocation, cache-management, and contract validation. The consumer doesn't know whether the brief came from cache, a fresh subprocess run, or a hypothetical future producer — it just gets a `CompanyBrief`.

## Pattern (3) examples — bare subprocess CLI

More common in this repo than pattern (2). The producer app exposes itself via `apps_<x>/__main__.py`; consumers invoke `python -m apps_<x>` directly with `subprocess.run(...)` and parse the producer's JSON artifact.

### 3.1 `apps_qna/integrations/from_apps_research.py` — apps_qna ↔ apps_research

**Producer**: `apps_research` invoked as `python -m apps_research --mode <x>`

**Consumer**: dedicated integration module `apps_qna/integrations/from_apps_research.py` plus `apps_qna/integrations/wizard.py`

**Shape**:

```python
# Conceptual (consult source for current shape):
import subprocess, sys, json
from pathlib import Path

def pull_research_artifact(topic: str, out_dir: Path) -> dict:
    cmd = [sys.executable, "-m", "apps_research", "--topic", topic, "--out", str(out_dir)]
    completed = subprocess.run(cmd, capture_output=True, text=True, timeout=300, shell=False)
    if completed.returncode != 0:
        raise RuntimeError(f"apps_research exit={completed.returncode}: {completed.stderr}")
    artifact = sorted(out_dir.glob("runs/*/research.json"), key=lambda p: p.stat().st_mtime)[-1]
    return json.loads(artifact.read_text(encoding="utf-8"))
```

**Why it works**: apps_qna doesn't need a stable typed contract — the JSON shape is the contract. No facade indirection; the integration module is self-contained.

### 3.2 `apps_eval/engines/scenario_runner.py` — apps_eval ↔ apps_exec

**Producer**: `apps_exec` invoked as `python -m apps_exec`

**Consumer**: `apps_eval/engines/scenario_runner.py` (the same scenario runner that uses `rg_orchestrator_facade` for apps_rg uses bare subprocess for apps_exec).

### 3.3 `apps_qna/integrations/wizard.py` — apps_qna ↔ apps_exec

**Producer**: `apps_exec` invoked as `python -m apps_exec`

**Consumer**: `apps_qna/integrations/wizard.py`

## Cross-app consumption matrix (corrected 2026-05-01)

Includes both pattern (2) and pattern (3) consumers — the bare-subprocess pattern is the easy one to miss in graph queries because it leaves no `imports` edge.

| Producer | Consumer apps | Mechanism(s) |
|---|---|---|
| `apps_research` | `apps_rg`, `apps_qna` | (2) `research_facade` for apps_rg; (3) bare subprocess for apps_qna |
| `apps_exec` | `apps_eval`, `apps_qna` | (3) bare subprocess for both |
| `apps_rg` | `apps_eval` | (2) `rg_orchestrator_facade` |
| `apps_lic`, `apps_rfp`, `apps_eval` | (none today) | n/a |

**Implication**: `apps_research` and `apps_exec` are **producer apps with multiple consumers**. They are not dormant or redundant despite zero `imports`-edge fan-in. Anyone proposing to delete or merge them is reading the wrong slice of the ADG.

## When to use which pattern

**Pattern (2) — typed facade in `apps_shared/adapters/`** — use when:

1. **Cross-app data flow is genuine** — one app produces a typed artifact another app needs.
2. **Multiple consumers** — DRY the subprocess + cache + parse logic into one place.
3. **The contract is stable** — the typed return shape (e.g. `CompanyBrief`) lives somewhere both apps can import without circular dependency.
4. **Cache management or fallback chains** are part of the integration.

**Pattern (3) — bare subprocess CLI** — use when:

1. **Single consumer**, bespoke parsing.
2. **JSON artifact is the contract** — no need for a typed Pydantic shape.
3. **Experimental or one-shot wiring** that may not justify a facade yet.

Don't use either pattern when:

- The "integration" would require importing across multiple producer-app modules. That's a sign the contract isn't well-defined; refactor the producer first.
- The data flow is bidirectional. Two facades / two integrations, one per direction, is acceptable; one facade with both call shapes is not.
- The producer doesn't exist yet. Don't scaffold for hypothetical future code; the scaffold-without-callers anti-pattern wastes review attention. (Note: `research_facade` was a scaffold for ~2 weeks before the apps_rg consumer landed 2026-05-01 — that's the boundary case.)

## Contract shape (template)

A facade module should:

- Live at `apps_shared/adapters/<name>_facade.py`.
- Expose **one public function or class** as the entrypoint.
- Type-hint its inputs and outputs explicitly.
- Validate output through a Pydantic model owned by either the producer's `apps_<x>/types/` or `apps_shared/types/`.
- Raise a typed exception (e.g. `CompanyBriefMissingError`) on failure rather than returning `None` ambiguously.
- Use `subprocess.run(..., timeout=<reasonable>, shell=False)` for CLI-mode producers (constitutional §14, §0).
- Be importable without side effects. Lazy-import heavy dependencies inside the function body if needed (the consumer guards `ImportError` and falls through).

## Verifying a producer / facade is in active use (ADG queries)

To verify a facade is alive (not scaffold debt), query the ADG snapshot:

```python
import sqlite3, glob
snap = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"))[-1]
con = sqlite3.connect(snap)
cur = con.cursor()

# Count callers anywhere in the repo (production)
cur.execute("""
    SELECT source_file, COUNT(*) AS c
    FROM edges
    WHERE relation_type = 'imports'
      AND symbol LIKE '%research_facade%'
    GROUP BY source_file
    ORDER BY c DESC
""")
for src, c in cur.fetchall():
    print(f"  {c:>4}  {src}")
```

**Critical caveat #1 (snapshot staleness, learned 2026-05-01)**: ADG snapshots reflect *the moment they were generated*. If a facade was wired up after the snapshot, the query will incorrectly show zero callers. Before declaring a facade "dormant" based on ADG evidence, also:

1. Verify the snapshot is fresh: `ls -la artifacts/adg/adg_indexed_*.sqlite | tail -1` — should be within hours, not days.
2. Read the source files and grep for the facade's import path: `grep -r "from apps_shared.adapters.<name>_facade" apps_*/` (allowed for literal-string verification, not for dependency analysis).
3. If in doubt, regenerate: `python tools/generate_full_adg.py`.

**Critical caveat #2 (subprocess invocation invisibility, learned 2026-05-01)**: pattern (3) consumers leave **no `imports` edge** into the producer. They reference the producer as a string literal (`"apps_research"`, `"-m"`, `"apps_exec"`) inside `subprocess.run()` arg lists. Querying for fan-in via `imports` edges undercounts pattern (3) consumers to zero. Always also query:

```python
# Find pattern (3) consumers — string-literal mentions of the producer
cur.execute("""
    SELECT DISTINCT source_file FROM edges
    WHERE symbol LIKE ?
      AND source_file LIKE 'apps_%/%'
      AND source_file NOT LIKE ?
""", (f"%{producer_app}%", f"{producer_app}/%"))
```

The producer's `__main__.py` is the entrypoint; consumers invoke it via `subprocess.run([sys.executable, "-m", "<producer_app>", ...])`. The ADG records this in the `symbol` column but creates no inter-app `imports` edge.

A scaffold-with-zero-callers is real (it has happened in this repo). A fresh-integration-not-yet-indexed is real (2026-05-01). A producer-with-only-pattern-(3)-consumers is real and the most common case (apps_research, apps_exec). All three look identical in a naive `imports`-only ADG query. Source-of-truth reads + the symbol-mention query above break the tie.

## Failure precedents (2026-05-01)

**Save #1 (snapshot staleness)**: The cleanup plan that produced this doc almost archived `research_facade.py` based on a stale-snapshot "zero callers" reading. Source-of-truth read of `apps_rg/integrations/company_research_loader.py` revealed a live import added earlier the same day, after the snapshot. Lesson in §"Verifying ... caveat #1" above.

**Save #2 (subprocess invisibility)**: A subsequent question "are apps_research / apps_exec really needed?" almost concluded "no, delete them" based on zero `imports`-edge fan-in. The symbol-mention query revealed pattern (3) consumers in `apps_qna/integrations/from_apps_research.py`, `apps_qna/integrations/wizard.py`, and `apps_eval/engines/scenario_runner.py`. Both apps have multiple active consumers. Lesson in §"Verifying ... caveat #2" above.

Captured as memory patterns:

- `ProceduralPattern:CrossAppFacadeIsTheCorrectIntegrationShape` — the three-pattern typology
- `ProceduralPattern:ADGSnapshotStalenessVerificationProtocol` — caveat #1 mitigation
- `ProceduralPattern:WorkspaceLayoutSnapshotIsPartial` — broader staleness pattern (3 instances by 2026-05-01)

## References

- `apps_shared/adapters/rg_orchestrator_facade.py`
- `apps_shared/adapters/research_facade.py`
- `apps_rg/integrations/company_research_loader.py` (consumer of `research_facade`)
- `apps_eval/engines/scenario_runner.py` (consumer of `rg_orchestrator_facade`)
- `.claude/plans/apps-rg-narrative-and-company-research-e3f8c1.md` (HOP-0.6 design)
- `.claude/plans/dormant-facade-cleanup-b2d4f7.md` (the plan that produced this doc)
- `.claude/plans/apps-portfolio-integrated-evaluation-7d3a91.md` (closed; established that no producer→consumer integration existed pre-2026-05-01)
- Constitutional §22 (ADG graph layer is primary for refactoring)
- Constitutional §28 (SQLite-direct fallback supersedes grep)

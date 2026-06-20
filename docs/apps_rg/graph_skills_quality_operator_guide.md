# Graph Skills Quality — Operator Guide (W9)

> **Plan SSOT:** [.codex/plans/graph-skills-quality-enhancement-c4e8a1.md](../../.codex/plans/graph-skills-quality-enhancement-c4e8a1.md)
> **Related:** [graph_skills_graph_v2_rollback.md](graph_skills_graph_v2_rollback.md) · [executive_summary_operator_guide.md](executive_summary_operator_guide.md)

This guide is the **canonical CLI surface** for graph-skills quality proof (W0–W10). Use these commands for product behavior proof — not ad-hoc orchestration helpers.

---

## Brown fixture identity (pinned — W0 / W10)

| Fixture | Path (repo-relative) | SHA-256 (W0 pin) |
|---------|----------------------|------------------|
| JD | `apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt` | `3701dd5b1d6e0c92db394d6bf1879574e4ad638094d9b453f6d35e264e8e573f` |
| Briefing (all lanes) | `apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md` | `9d0b63db755cce713bce35aa7c9089453a0e2ffb5060a3ed7bef8da483843e5d` |

**Targeting flags (all lanes):**

```text
--target-company "Brown & Brown"
--target-role "SVP IT Strategy & Innovation"
--jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt
--provider qwen_vllm
```

**Briefing path note:** [lane_registry.py](../../apps_rg/runtime/rigor/lane_registry.py) still references `.txt` briefing paths for rigor specs; on-disk SSOT for operators is **`.md`** (table above). W10 closeout asserts byte-identical digests for the `.md` files.

---

## Canonical per-lane CLI (`REAL_LLM_RUNTIME_PROOF`)

All product lane proof MUST use:

```bash
python -m apps_rg --section <lane> \
  --target-company "Brown & Brown" \
  --target-role "SVP IT Strategy & Innovation" \
  --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt \
  --manual-brief <briefing.md> \
  --provider qwen_vllm
```

| Lane | `--manual-brief` |
|------|------------------|
| All generated lanes | `apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md` |

**Example (executive_summary):**

```bash
python -m apps_rg --section executive_summary \
  --target-company "Brown & Brown" \
  --target-role "SVP IT Strategy & Innovation" \
  --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt \
  --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md \
  --provider qwen_vllm
```

Stdout includes `artifact_dir=...` under `artifacts/apps_rg/runs/`. W10 closeout requires seven REAL_LLM lanes with distinct proof trees — no mixed proof-class PASS.

---

## Canonical whole-resume CLI (`REAL_LLM_RUNTIME_PROOF`)

Full R4 product run (no `--section`) — **only** this entry for whole-resume proof:

```bash
python -m apps_rg \
  --target-company "Brown & Brown" \
  --target-role "SVP IT Strategy & Innovation" \
  --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt \
  --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md
```

Artifact root is an integrated whole-run directory (e.g. `full_resume_<id>/` under `artifacts/apps_rg/runs/`). Emits `full_run_section_status` when the run completes. Do **not** substitute `run_*_execution`, `wire_spine_c0_fec_for_section`, or dispatch smoke scripts as product proof.

---

## Proof classes (do not mix PASS)

| Class | When | Examples |
|-------|------|----------|
| `CONTRACT_TEST_PROOF` | Unit/contract tests, emitters, scorer fixtures | `pytest tests/unit/apps_rg/test_graph_skills_*.py`, `emit_graph_skills_quality_w*.py` |
| `DETERMINISTIC_TEST_PROOF` | Ledger migration, validators without LLM | W3 `graph_v2_quality_migration.py` |
| `REAL_LLM_RUNTIME_PROOF` | Live `python -m apps_rg` lane or whole-run with `qwen_vllm` | Brown lane matrix, W8 utilization on live output |
| `LIVE_X3_RUNTIME_PROOF` | W10 only — full disposition matrix | Seven lanes + closeout JSON |

**Forbidden as product proof**

- `--provider mock` (removed from CLI)
- Calling runtime helpers directly to claim PASS
- Fixture-only scripts without CLI invocation
- `proof_source=broad_skills_ledger` or SRFS-as-proof
- Phrase overlap alone for utilization (see D8 scorer)

---

## Authority separation (constitutional)

| Input | Role |
|-------|------|
| `augmented_skills_graph` | Evidence authority — hops, phrases, graph-bound facts |
| `candidate_fact_ledger` / SRFS | Claim text substrate only |
| JD / briefing | Targeting — weights, reorder; never new `fact_id`s |
| C0.2 hybrid | Reorder resolver-allowed facts only (NEG-3) |
| Skill phrase capsule | Lexical guidance only (NEG-2, NEG-6) |
| `allowed_phrases` / `forbidden_phrases` | Lexical constraints — not proof authority |

Utilization scoring: [graph_skills_utilization_scorer.py](../../apps_rg/runtime/graph_skills_utilization_scorer.py) — phrase **and** cited `fact_id` required (D8).

---

## Wave emitters (CONTRACT receipts — re-run anytime)

From repo root:

```bash
python ops_scripts/apps_rg/emit_graph_skills_quality_w0_baseline.py
python ops_scripts/apps_rg/emit_graph_skills_quality_w1.py
python ops_scripts/apps_rg/emit_graph_skills_quality_w2.py
python ops_scripts/apps_rg/emit_graph_skills_quality_w3.py
python ops_scripts/apps_rg/emit_graph_skills_quality_w4.py
python ops_scripts/apps_rg/emit_graph_skills_quality_w5.py
python ops_scripts/apps_rg/emit_graph_skills_quality_w6.py
python ops_scripts/apps_rg/emit_graph_skills_quality_w7.py
python ops_scripts/apps_rg/emit_graph_skills_quality_w8.py
python ops_scripts/apps_rg/emit_graph_skills_quality_w9.py
```

Wave receipts: `docs/reports/apps_rg/graph_skills_quality_w<N>_receipt.json`. Closeout (W10): `graph_skills_quality_enhancement_closeout.json`.

---

## CI ratchet

```bash
python ops_scripts/ci/check_graph_skills_agentic_core_boundary.py
```

Workflow: [.github/workflows/graph-skills-authority-ratchet.yml](../../.github/workflows/graph-skills-authority-ratchet.yml) (PR + nightly). No `agentic_core/` diffs unless `GRAPH_SKILLS_ALLOW_AGENTIC_CORE=1` (W10-AG only).

---

## W8 utilization receipt

After live Brown `executive_summary` + `competencies` runs, score output with the utilization scorer and refresh:

```bash
python ops_scripts/apps_rg/emit_graph_skills_quality_w8.py
```

Artifact: `docs/reports/apps_rg/graph_skills_utilization_receipt.json`.

---

## Rollback (graph v2)

See [graph_skills_graph_v2_rollback.md](graph_skills_graph_v2_rollback.md).

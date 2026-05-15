# Runtime signoff evidence — apps_rg P3.1 & P3.2

**Scope:** Contract and governance tests aligned with:

- **P3.1** — `.cursor/plans/p3.1_apps-rg-l1-contract-wiring-3e7f92.md` (L1 contract wiring, U0 profile digest path, shims, AG-2 consumption).
- **P3.2** — `.cursor/plans/p3.2_apps-rg-l0-critical-gaps-remediation-a3f8e1.md` (L0 DoD-1–DoD-7 surfaces: canonical `route_profiles.yaml`, spine fields, typed gate receipts, cache bypass for personalization).

**Git commit (capture):** `d5408f5d2115b2520d91df7c1522eeb21b7c6fad` — see `git_head.txt`.

**Disclaimer:** This folder is **plan-scoped runtime proof** (pytest + report-only L0 scan + `apps_rg` CLI dry-run). It is **not** `artifacts/certification/final_requirement_signoff_report.json` / Fort Knox RTC-REQ signoff. For RTC-REQ claims, run `python scripts/compile_requirement_signoff.py` and `python scripts/verify_final_requirement_signoff_bundle.py` per `.cursor/skills/fortknox-evidence/SKILL.md`.

---

## 1. Pytest (primary evidence)

**Command:**

```bash
python -m pytest tests/_apps_contract/test_apps_rg_app_payload_consumption.py tests/_apps_contract/test_l0_canonical_profile_path.py tests/_apps_contract/test_l0_execution_form.py tests/_apps_contract/test_l0_gate_verdicts.py tests/_apps_contract/test_l0_cache_bypass.py tests/_apps_contract/test_apps_rg_l1_binding.py tests/_apps_contract/test_apps_rg_l1_profile_wiring.py tests/governance/test_apps_rg_l1_core_boundary.py --override-ini="addopts=" -v --tb=line --junit-xml=docs/reports/runtime_cert/apps_rg_p31_p32_runtime/junit_p31_p32.xml
```

**Outcome:** `78 passed`, `1 skipped`, `0 failed`, exit code **0**.

**Artifacts:**

| File | Role |
|------|------|
| `junit_p31_p32.xml` | Machine-readable JUnit (`errors=0` `failures=0` `skipped=1` `tests=79`). |
| `pytest_p31_p32_signoff.log` | Full verbose pytest transcript. |

**Skipped test:** `tests/governance/test_apps_rg_l1_core_boundary.py::test_no_apps_rg_literals_outside_shims` — intentional on this snapshot (see skip message in log / XML).

---

## 2. P3.2 advisory proof surface (DoD-9 direction)

**Command:**

```bash
python ops_scripts/ci/check_l0_app_agnostic.py
```

**Outcome:** Exit code **0** (script is **report-only** per header). Log lists **7** files under `agentic_core/L0_routing/` with apps_rg-ish literals (expected while deprecation shims exist).

**Artifact:** `check_l0_app_agnostic.log`

---

## 3. P3.2 DoD-11 smoke (CLI validation path)

**Command:**

```bash
python -m apps_rg --dry-run --target-company "EvidenceCo" --target-role "VP Engineering"
```

**Outcome:** Exit code **0**; stdout: `DRY RUN: apps_rg pipeline validation complete (no LLM call).`

**Artifact:** `apps_rg_dry_run.log`

---

## 4. Integrity index

SHA-256 of artifacts in this directory are recorded in **`runtime_signoff_manifest.json`** under `artifact_sha256`. Re-verify after copy with:

```bash
python -c "import hashlib, pathlib; p=pathlib.Path('docs/reports/runtime_cert/apps_rg_p31_p32_runtime/junit_p31_p32.xml'); print(hashlib.sha256(p.read_bytes()).hexdigest())"
```

---

## 5. Plan DoD mapping (quick traceability)

| Plan | DoD / surface | Test / gate |
|------|----------------|-------------|
| P3.2 | DoD-1 canonical profile | `test_l0_canonical_profile_path.py` |
| P3.2 | DoD-2 / DoD-3 spine + grounding | `test_l0_execution_form.py`, AG-2 L0 tests in `test_apps_rg_app_payload_consumption.py` |
| P3.2 | DoD-4 / DoD-5 typed receipts | `test_l0_gate_verdicts.py` |
| P3.2 | DoD-7 cache bypass | `test_l0_cache_bypass.py` |
| P3.1 | U0→L1 profile ref + digest | `test_apps_rg_l1_profile_wiring.py` |
| P3.1 | L1 binding / NAA / work-shape | `test_apps_rg_l1_binding.py` |
| P3.1 | Core shim discipline | `tests/governance/test_apps_rg_l1_core_boundary.py` |
| Both | AG-2 app_payload consumption + dispatch | `test_apps_rg_app_payload_consumption.py` |

"""Tests for ``tools/adg/run_full_adg_audit.py`` (wrapper).

Plan: ``docs/archive/windsurf/legacy-tree/plans/adg-audit-pipeline-integration-7f2c93.md`` W4.1.

Strategy: mock ``subprocess.run`` inside ``run_full_adg_audit`` so we
exercise manifest discovery + required-gate cross-check + certification
classification without launching real subprocesses. A single shared
fixture paints the manifests the wrapper expects to read.
"""

from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import pytest

from tools.adg import consume_adg_repair_handoff
from tools.adg import run_full_adg_audit as wrapper
from tools.generate._required_gates import required_gate_names

SNAPSHOT_COMMIT_SHA = "a" * 40
SNAPSHOT_REPO_STATE_HASH = "b" * 40


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def temp_artifacts(tmp_path, monkeypatch):
    """Redirect the wrapper's manifest/receipt paths into a sandbox."""
    monkeypatch.setattr(wrapper, "ARTIFACTS_ADG", tmp_path / "artifacts" / "adg")
    monkeypatch.setattr(wrapper, "RECEIPT_PATH", tmp_path / "docs" / "receipt.json")
    monkeypatch.setattr(wrapper, "HANDOFF_CONTRACT_PATH", tmp_path / "missing-automation.toml")
    wrapper.ARTIFACTS_ADG.mkdir(parents=True, exist_ok=True)

    import tools.adg.integration.enforcement_report as enforcement_mod
    import tools.reports.adg_burndown_report as burndown_mod

    monkeypatch.setattr(enforcement_mod, "ARTIFACTS_ADG", wrapper.ARTIFACTS_ADG)
    monkeypatch.setattr(
        burndown_mod, "BURNDOWN_TABLE_DEFAULT", wrapper.ARTIFACTS_ADG / "adg_burndown_table.json"
    )
    monkeypatch.setattr(
        burndown_mod,
        "BURNDOWN_REPORT_OUTPUTS",
        (
            wrapper.ARTIFACTS_ADG / "adg_burndown_report.md",
            tmp_path / "docs" / "reports" / "adg" / "adg_burndown_report.md",
        ),
    )
    return tmp_path


def _make_snapshot(
    path: Path,
    *,
    with_runtime_view: bool,
    attested: int,
    commit_sha: str = SNAPSHOT_COMMIT_SHA,
    repo_state_hash: str = SNAPSHOT_REPO_STATE_HASH,
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(path))
    try:
        con.execute(
            "CREATE TABLE nodes (id INTEGER PRIMARY KEY, resolved_path TEXT, file_path TEXT, adg_name TEXT)"
        )
        con.execute(
            "CREATE TABLE edges (id INTEGER PRIMARY KEY, src_id INT, dst_id INT, relation_type TEXT, authority TEXT)"
        )
        con.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        con.executemany(
            "INSERT INTO meta(key, value) VALUES (?, ?)",
            (
                ("commit_sha", commit_sha),
                ("repo_state_hash", repo_state_hash),
            ),
        )
        if with_runtime_view:
            con.execute("CREATE TABLE v_runtime_proof (static_edge_id INT, attesting_trace_count INT)")
            for _ in range(attested):
                con.execute(
                    "INSERT INTO v_runtime_proof(static_edge_id, attesting_trace_count) VALUES (NULL, 1)"
                )
        con.commit()
    finally:
        con.close()
    return path


def _write_manifests(
    artifacts_dir: Path,
    *,
    ts: str = "06292026_0101",
    snapshot: Path,
    runtime_proof_status: str = "attested",
    runtime_attested: int = 5,
    generation_exit_code: int = 0,
    gates: list[dict] | None = None,
) -> tuple[Path, Path]:
    """Write a (gate_manifest, generation_manifest) pair."""
    if gates is None:
        # Include every required gate with status=pass so the wrapper
        # cross-check passes.
        gates = [
            {
                "name": name,
                "phase": "preflight",
                "kind": "python_function",
                "blocking_mode": "hard_fail",
                "status": "pass",
                "exit_code": 0,
                "duration_s": 0.01,
                "started_at_utc": "2026-01-01T00:00:00Z",
                "finished_at_utc": "2026-01-01T00:00:00Z",
                "script_rel": None,
                "message": None,
            }
            for name in sorted(required_gate_names())
        ]
    manifest_failed = generation_exit_code != 0 or any(
        gate.get("status") not in {"pass", "invoked"} for gate in gates
    )
    gate_manifest = {
        "timestamp": "2026-01-01T00:00:00Z",
        "generator_entrypoint": "tools/generate/generate_full_adg.py",
        "sqlite_path": str(snapshot),
        "generation_exit_code": generation_exit_code,
        "certification_status": "failed" if manifest_failed else "clean",
        "gates": gates,
        "unexpected_skips": [],
        "failed_gates": [],
        "deferred_failures": [],
    }
    gate_manifest_path = artifacts_dir / f"adg_gate_invocation_manifest_{ts}.json"
    gate_manifest_path.write_text(json.dumps(gate_manifest), encoding="utf-8")

    gen_manifest = {
        "timestamp": "2026-01-01T00:00:01Z",
        "sqlite_path": str(snapshot),
        "snapshot_path": str(snapshot),
        "snapshot_sha256": wrapper._sha256(snapshot),
        "commit_sha": SNAPSHOT_COMMIT_SHA,
        "repo_state_hash": SNAPSHOT_REPO_STATE_HASH,
        "generation_exit_code": generation_exit_code,
        "p0_status": "pass",
        "gate_manifest_path": str(gate_manifest_path),
        "runtime_proof_status": runtime_proof_status,
        "runtime_attested_edge_count": runtime_attested,
        "registry_bucket_edge_count": 0,
        "created_at_utc": "2026-01-01T00:00:01Z",
        "certification_status": "failed" if manifest_failed else "clean",
    }
    gen_manifest_path = artifacts_dir / f"adg_generation_manifest_{ts}.json"
    gen_manifest_path.write_text(json.dumps(gen_manifest), encoding="utf-8")
    return gate_manifest_path, gen_manifest_path


def _gate_result(
    gate_id: str,
    *,
    band: str = "P0",
    enforcement: str = "block",
    classification: str = "blocked",
    violation_count: int = 1,
    baseline_count: int | None = None,
) -> dict:
    return {
        "gate_id": gate_id,
        "band": band,
        "enforcement": enforcement,
        "classification": classification,
        "violation_count": violation_count,
        "baseline_count": baseline_count,
        "status": "fail" if classification in {"blocked", "regressed"} else "pass",
    }


def _write_handoff_inputs(
    root: Path,
    *,
    run_id: str = "06252026_0101",
    gates: list[dict] | None = None,
    include_snapshot_paths: bool = True,
    final_exit_code: int = 0,
) -> tuple[Path, Path, Path]:
    artifacts = wrapper.ARTIFACTS_ADG
    snap = _make_snapshot(
        artifacts / f"adg_indexed_{run_id}.sqlite",
        with_runtime_view=True,
        attested=1,
    )
    gate_manifest = artifacts / f"adg_gate_invocation_manifest_{run_id}.json"
    gate_manifest.write_text(
        json.dumps(
            {
                "timestamp": "2026-06-25T01:01:00Z",
                "sqlite_path": str(snap) if include_snapshot_paths else None,
                "gates": [],
            }
        ),
        encoding="utf-8",
    )
    snapshot_value = str(snap) if include_snapshot_paths else None
    gen_manifest = artifacts / f"adg_generation_manifest_{run_id}.json"
    gen_manifest.write_text(
        json.dumps(
            {
                "timestamp": "2026-06-25T01:01:00Z",
                "sqlite_path": snapshot_value,
                "snapshot_path": snapshot_value,
                "snapshot_sha256": wrapper._sha256(snap),
                "commit_sha": SNAPSHOT_COMMIT_SHA,
                "repo_state_hash": SNAPSHOT_REPO_STATE_HASH,
                "gate_manifest_path": str(gate_manifest),
                "runtime_proof_status": "attested",
                "runtime_attested_edge_count": 1,
                "certification_status": "failed" if gates else "clean",
            }
        ),
        encoding="utf-8",
    )
    gate_results = artifacts / "adg_gate_results_20260625_010101.json"
    gate_results.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "timestamp": "2026-06-25T01:01:01+00:00",
                "snapshot": snap.name,
                "snapshot_path": str(snap),
                "snapshot_sha256": wrapper._sha256(snap),
                "overall_exit_code": 1 if gates else 0,
                "gates": gates or [],
            }
        ),
        encoding="utf-8",
    )
    burndown_table = artifacts / f"adg_burndown_table_{run_id}.json"
    burndown_table.write_text(
        json.dumps(
            {
                "schema_version": "2.2",
                "summary": {"P0": {}, "P1": {}},
                "bands": {},
                "provenance": {
                    "sqlite_source_path": str(snap),
                    "sqlite_source_sha256": wrapper._sha256(snap),
                },
            }
        ),
        encoding="utf-8",
    )
    burndown_report = artifacts / f"adg_burndown_report_{run_id}.md"
    burndown_report.write_text("# ADG CI Burndown Report\n", encoding="utf-8")
    action_queue, action_errors = wrapper._ensure_action_queue_for_handoff(
        gate_results_path=gate_results,
        burndown_table_path=burndown_table,
        snapshot_path=snap,
        adg_run_id=run_id,
    )
    assert action_queue is not None and action_errors == []
    _write_valid_output_bundle_fixture(
        artifacts=artifacts,
        run_id=run_id,
        snapshot=snap,
        gate_results=gate_results,
        burndown_table=burndown_table,
        burndown_report=burndown_report,
        action_queue=action_queue,
        final_exit_code=final_exit_code,
    )
    return gen_manifest, gate_manifest, snap


def _write_valid_output_bundle_fixture(
    *,
    artifacts: Path,
    run_id: str,
    snapshot: Path,
    gate_results: Path,
    burndown_table: Path,
    burndown_report: Path,
    action_queue: Path,
    final_exit_code: int = 0,
) -> Path:
    adapter = artifacts / f"adg_bcg_adapter_{run_id}.json"
    adapter.write_text(json.dumps({"source": {"run_id": run_id}}), encoding="utf-8")
    adapter.with_suffix(".md").write_text("# Adapter\n", encoding="utf-8")
    review = artifacts / f"adg_review_template_{run_id}.json"
    review.write_text(json.dumps({"run_id": run_id}), encoding="utf-8")
    review.with_suffix(".yaml").write_text(f"run_id: {run_id}\n", encoding="utf-8")
    executive = artifacts / f"adg_bcg_executive_summary_{run_id}.json"
    executive.write_text(json.dumps({"run": {"run_id": run_id}}), encoding="utf-8")
    executive.with_suffix(".yaml").write_text(f"run:\n  run_id: {run_id}\n", encoding="utf-8")
    executive_md = executive.with_suffix(".md")
    executive_md.write_text(
        "## ADG Executive Brief\n\n"
        "### Impact Inventory\n\nNone.\n\n"
        "- **Decision gate:** PASS\n"
        "- **Fix now:** none\n",
        encoding="utf-8",
    )
    terminal = artifacts / f"adg_run_terminal_summary_{run_id}.md"
    terminal.write_text(
        executive_md.read_text(encoding="utf-8")
        + f"\n## Final disposition\n\n- **Process exit code:** `{final_exit_code}`\n",
        encoding="utf-8",
    )
    published = [
        adapter,
        adapter.with_suffix(".md"),
        burndown_report,
        action_queue,
        review,
        review.with_suffix(".yaml"),
        executive,
        executive.with_suffix(".yaml"),
        executive_md,
    ]
    publication = artifacts / f"adg_output_publication_{run_id}.json"
    publication.write_text(
        json.dumps(
            {
                "schema_version": "adg-output-publication/v1",
                "run_id": run_id,
                "published_at_utc": "2026-06-25T01:01:02Z",
                "mutable_report_aliases_published": False,
                "artifacts": [
                    {"path": str(path.resolve()), "sha256": wrapper._sha256(path)} for path in published
                ],
            }
        ),
        encoding="utf-8",
    )

    def _gate(key: str, paths: list[Path]) -> dict:
        return {
            "key": key,
            "required": True,
            "status": "pass",
            "producer_exit_code": 0,
            "paths": [str(path.resolve()) for path in paths],
            "diagnostic": "",
        }

    gates = [
        _gate("bcg_gate_adapter", [adapter, adapter.with_suffix(".md")]),
        _gate("burndown_report", [burndown_report]),
        _gate("action_queue", [action_queue]),
        _gate("review_template", [review, review.with_suffix(".yaml")]),
        _gate(
            "bcg_executive_summary",
            [executive, executive.with_suffix(".yaml"), executive_md],
        ),
        _gate("latest_publication", [publication]),
    ]
    inventory = [burndown_table, *published, publication, terminal]
    bundle = artifacts / f"adg_run_output_bundle_{run_id}.json"
    bundle.write_text(
        json.dumps(
            {
                "schema_version": "adg-run-output-bundle/v1",
                "run_id": run_id,
                "generated_at_utc": "2026-06-25T01:01:02Z",
                "status": "complete",
                "snapshot_path": str(snapshot.resolve()),
                "snapshot_sha256": wrapper._sha256(snapshot),
                "gate_results_path": str(gate_results.resolve()),
                "gate_results_sha256": wrapper._sha256(gate_results),
                "enforcement_report_path": None,
                "enforcement_report_sha256": None,
                "terminal_output_count": 1,
                "terminal_summary_path": str(terminal.resolve()),
                "terminal_finalized_at_utc": "2026-06-25T01:01:03Z",
                "final_exit_code": final_exit_code,
                "latest_promoted": True,
                "gates": gates,
                "artifacts": [
                    {"path": str(path.resolve()), "sha256": wrapper._sha256(path)} for path in inventory
                ],
            }
        ),
        encoding="utf-8",
    )
    return bundle


def _reseal_digest_bound_queue_and_gate_results(handoff: dict) -> None:
    """Refresh fixture digests after an adversarial queue/results rewrite."""
    artifacts = handoff["artifacts"]
    gate_results = Path(artifacts["gate_results"]["path"])
    action_queue = Path(artifacts["action_queue"]["path"])
    gate_digest = wrapper._sha256(gate_results)

    action_doc = json.loads(action_queue.read_text(encoding="utf-8"))
    for row in action_doc.get("provenance", {}).get("inputs", []):
        if isinstance(row, dict) and row.get("artifact_key") == "gate_results":
            row["digest_sha256"] = gate_digest
    action_queue.write_text(json.dumps(action_doc), encoding="utf-8")
    action_digest = wrapper._sha256(action_queue)

    bundle = Path(artifacts["output_bundle"]["path"])
    bundle_doc = json.loads(bundle.read_text(encoding="utf-8"))
    publication_row = next(
        row for row in bundle_doc["artifacts"] if Path(row["path"]).name.startswith("adg_output_publication_")
    )
    publication = Path(publication_row["path"])
    publication_doc = json.loads(publication.read_text(encoding="utf-8"))
    next(row for row in publication_doc["artifacts"] if Path(row["path"]) == action_queue)["sha256"] = (
        action_digest
    )
    publication.write_text(json.dumps(publication_doc), encoding="utf-8")
    publication_digest = wrapper._sha256(publication)

    bundle_doc["gate_results_sha256"] = gate_digest
    for row in bundle_doc["artifacts"]:
        row_path = Path(row["path"])
        if row_path == action_queue:
            row["sha256"] = action_digest
        elif row_path == publication:
            row["sha256"] = publication_digest
    bundle.write_text(json.dumps(bundle_doc), encoding="utf-8")

    artifacts["gate_results"] = wrapper._artifact_ref("gate_results", gate_results)
    artifacts["action_queue"] = wrapper._artifact_ref("action_queue", action_queue)
    artifacts["output_bundle"] = wrapper._artifact_ref("output_bundle", bundle)


def _write_receipt(
    path: Path,
    *,
    artifact_status: str,
    handoff: dict,
    run_id: str = "06252026_0101",
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema_version": wrapper.RECEIPT_SCHEMA_VERSION,
                "run_state": {
                    "certification_status": "clean" if artifact_status == "certified" else "failed",
                    "process_exit_code": 0 if artifact_status == "certified" else 1,
                    "generator_exit_code": 0 if artifact_status == "certified" else 1,
                    "report_exit_code": 1,
                    "runtime_proof_status": "attested",
                    "reasons": [],
                },
                "artifact_status": artifact_status,
                "artifact_status_source": "direct",
                "adg_run_id": run_id,
                "started_at_utc": "2026-06-25T01:00:00Z",
                "completed_at_utc": "2026-06-25T01:02:00Z",
                "repair_handoff": handoff,
            }
        ),
        encoding="utf-8",
    )
    return path


def _patch_generator(
    monkeypatch,
    *,
    return_code: int = 0,
    writes_manifests: bool = True,
    snapshot: Path | None = None,
    gate_kwargs: dict | None = None,
    runtime_proof_status: str = "attested",
    runtime_attested: int | None = None,
    dispatcher_gates: list[dict] | None = None,
    dispatcher_exit_code: int = 0,
) -> mock.Mock:
    """Patch ``_run_generator`` to simulate the generator writing manifests."""

    def _fake(extra_args, timeout_s, certification_mode):  # noqa: ARG001
        if writes_manifests and snapshot is not None:
            manifest_kwargs = gate_kwargs or {}
            manifest_runtime_attested = runtime_attested
            if manifest_runtime_attested is None:
                from tools.generate._gate_manifest import runtime_proof_from_sqlite

                _observed_status, manifest_runtime_attested = runtime_proof_from_sqlite(snapshot)
            _write_manifests(
                wrapper.ARTIFACTS_ADG,
                snapshot=snapshot,
                runtime_proof_status=runtime_proof_status,
                runtime_attested=manifest_runtime_attested,
                generation_exit_code=return_code,
                **manifest_kwargs,
            )
            if return_code == 0:
                run_id = manifest_kwargs.get("ts", "06292026_0101")
                gate_results = wrapper.ARTIFACTS_ADG / f"adg_gate_results_{run_id}.json"
                gate_results.write_text(
                    json.dumps(
                        {
                            "schema_version": 1,
                            "timestamp": "2026-06-29T01:01:01+00:00",
                            "snapshot": snapshot.name,
                            "snapshot_path": str(snapshot),
                            "snapshot_sha256": wrapper._sha256(snapshot),
                            "overall_exit_code": dispatcher_exit_code,
                            "total_gates": len(dispatcher_gates or [None]),
                            "gates": dispatcher_gates
                            or [
                                {
                                    "gate_id": "fixture_dispatcher_health",
                                    "band": "P3",
                                    "enforcement": "warn",
                                    "classification": "pass",
                                    "status": "pass",
                                    "exit_code": 0,
                                    "violation_count": 0,
                                    "baseline_count": 0,
                                }
                            ],
                        }
                    ),
                    encoding="utf-8",
                )
                empty_bands = {
                    band: {
                        "label": label,
                        "gross": 0,
                        "guardian": 0,
                        "net": 0,
                        "diff": 0,
                        "status": "clear",
                    }
                    for band, label in {
                        "P0": "Foundation Blockers",
                        "P1": "Ratchet / Regression Guards",
                        "P2": "Warning / Strategic Gaps",
                        "P3": "Hygiene / Advisory",
                    }.items()
                }
                burndown = wrapper.ARTIFACTS_ADG / f"adg_burndown_table_{run_id}.json"
                burndown.write_text(
                    json.dumps(
                        {
                            "schema_version": "2.2",
                            "status": "complete",
                            "degraded": False,
                            "summary": empty_bands,
                            "bands": empty_bands,
                            "p0_clean": True,
                            "p1_no_ratchet": True,
                            "provenance": {
                                "counting_mode": "fixture_current_run",
                                "sqlite_source_path": str(snapshot),
                                "sqlite_source_sha256": wrapper._sha256(snapshot),
                            },
                        }
                    ),
                    encoding="utf-8",
                )
        return return_code

    m = mock.Mock(side_effect=_fake)
    monkeypatch.setattr(wrapper, "_run_generator", m)
    # These wrapper-unit tests simulate Stage 1; plane 2 has its own focused
    # coverage and must not launch the real multi-gate subprocess suite from a
    # synthetic fixture snapshot.
    monkeypatch.setattr(wrapper, "_run_certification_plane2", lambda **_kwargs: [])
    return m


def _patch_report(monkeypatch, *, return_code: int = 0) -> mock.Mock:
    m = mock.Mock(return_value=return_code)
    monkeypatch.setattr(wrapper, "_run_report", m)

    def _capture(**kwargs):
        if return_code != 0:
            return [], [f"three-bucket report exit_code={return_code}"]
        run_id = kwargs.get("adg_run_id") or "unknown"
        path = wrapper.ARTIFACTS_ADG / f"adg_three_bucket_gap_report_{run_id}.json"
        path.write_text(json.dumps({"status": "complete"}), encoding="utf-8")
        return [path], []

    monkeypatch.setattr(wrapper, "_capture_three_bucket_report_paths", _capture)
    return m


# ---------------------------------------------------------------------------
# Tests (plan §10 cases 1..18)
# ---------------------------------------------------------------------------
def test_temp_artifacts_redirects_enforcement_report_writer(temp_artifacts):
    import tools.adg.integration.enforcement_report as enforcement_mod

    report_path = enforcement_mod.write_enforcement_report(
        {"certified_rollup": "CERTIFIED"},
        ts="06292026_0000",
    )

    assert report_path.parent == wrapper.ARTIFACTS_ADG
    assert report_path.is_relative_to(temp_artifacts)
    assert (wrapper.ARTIFACTS_ADG / "adg_enforcement_report_latest.json").is_file()


def test_exact_generation_manifest_must_be_newer_than_wrapper_spawn(
    temp_artifacts,
) -> None:
    run_id = "06292026_0101"
    stale = wrapper.ARTIFACTS_ADG / f"adg_generation_manifest_{run_id}.json"
    stale.write_text(json.dumps({"run_id": run_id}), encoding="utf-8")
    wrapper_start = time.time_ns()

    assert (
        wrapper._find_generation_manifest(
            wrapper_start,
            expected_run_id=run_id,
        )
        is None
    )

    time.sleep(0.01)
    stale.write_text(json.dumps({"run_id": run_id, "fresh": True}), encoding="utf-8")
    assert wrapper._find_generation_manifest(wrapper_start, expected_run_id=run_id) == stale


def test_certification_stops_when_generator_exit_nonzero(temp_artifacts, monkeypatch):
    snap = _make_snapshot(temp_artifacts / "snap.sqlite", with_runtime_view=True, attested=1)
    _patch_generator(monkeypatch, return_code=5, snapshot=snap)
    _patch_report(monkeypatch)
    result = wrapper.run_audit(mode="certification")
    assert result.certification_status == "failed"
    assert result.generator_exit_code == 5
    assert any("generator exit_code=5" in r for r in result.reasons)


def test_diagnostic_mode_continues_and_labels_output_diagnostic(temp_artifacts, monkeypatch):
    snap = _make_snapshot(temp_artifacts / "snap.sqlite", with_runtime_view=True, attested=1)
    _patch_generator(monkeypatch, return_code=5, snapshot=snap)
    _patch_report(monkeypatch)
    result = wrapper.run_audit(mode="diagnostic", diagnostic_allow_failed_generator=True)
    assert result.certification_status == "diagnostic_only"


def test_diagnostic_mode_fails_when_mandatory_output_bundle_is_blocked(
    temp_artifacts,
    monkeypatch,
):
    snap = _make_snapshot(temp_artifacts / "snap.sqlite", with_runtime_view=True, attested=1)
    _patch_generator(monkeypatch, snapshot=snap)
    _patch_report(monkeypatch)
    monkeypatch.setattr(
        wrapper,
        "_emit_mandatory_run_outputs",
        lambda **_kwargs: (["ADG output bundle status=blocked"], None, None),
    )
    monkeypatch.setattr(
        wrapper,
        "_build_repair_handoff",
        lambda **_kwargs: ("incomplete", {"status": "incomplete", "artifacts": {}}, []),
    )
    monkeypatch.setattr(wrapper, "_run_retention_sweep", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(wrapper, "_write_receipt", lambda *_args, **_kwargs: None)

    result = wrapper.run_audit(
        mode="diagnostic",
        diagnostic_allow_failed_generator=True,
    )

    assert result.certification_status == "diagnostic_only"
    assert result.process_exit_code == 1
    assert "ADG output bundle status=blocked" in result.reasons


def test_main_returns_run_result_exit_code_even_with_diagnostic_generator_opt_out(monkeypatch):
    result = wrapper.WrapperResult(
        certification_status="diagnostic_only",
        generator_exit_code=0,
        report_exit_code=0,
        generation_manifest_path=None,
        gate_manifest_path=None,
        runtime_proof_status="attested",
        reasons=["ADG output bundle status=blocked"],
        process_exit_code=1,
    )
    monkeypatch.setattr(wrapper, "run_audit", lambda **_kwargs: result)

    assert wrapper.main(["--mode", "diagnostic", "--diagnostic-allow-failed-generator"]) == 1


def test_wrapper_passes_explicit_snapshot_to_report(temp_artifacts, monkeypatch):
    snap = _make_snapshot(temp_artifacts / "snap.sqlite", with_runtime_view=True, attested=1)
    _patch_generator(monkeypatch, snapshot=snap)
    report_mock = _patch_report(monkeypatch)
    wrapper.run_audit(mode="certification")
    assert report_mock.call_count == 1
    # Snapshot passed as kwarg; verify the path matches.
    call_kwargs = report_mock.call_args.kwargs
    assert Path(call_kwargs["snapshot"]).resolve() == snap.resolve()


def test_three_bucket_outputs_are_captured_as_snapshot_bound_run_artifacts(
    temp_artifacts,
    monkeypatch,
):
    run_id = "06292026_0101"
    monkeypatch.setattr(wrapper, "REPO_ROOT", temp_artifacts)
    snap = _make_snapshot(
        wrapper.ARTIFACTS_ADG / f"adg_indexed_{run_id}.sqlite",
        with_runtime_view=True,
        attested=1,
    )
    report_dir = temp_artifacts / "docs" / "reports" / "adg"
    report_dir.mkdir(parents=True)
    (report_dir / "THREE_BUCKET_GAP_REPORT.json").write_text(
        json.dumps(
            {
                "source_snapshot_path": str(snap.resolve()),
                "source_snapshot_sha256": wrapper._sha256(snap),
            }
        ),
        encoding="utf-8",
    )
    (report_dir / "THREE_BUCKET_GAP_REPORT.md").write_text(
        f"# Three bucket\n\nSnapshot: `{snap.name}`\n",
        encoding="utf-8",
    )

    paths, errors = wrapper._capture_three_bucket_report_paths(
        fmt="both",
        adg_run_id=run_id,
        snapshot_path=snap,
        since_wall_start=time.time() - 1,
    )

    assert errors == []
    assert {path.name for path in paths} == {
        f"adg_three_bucket_gap_report_{run_id}.json",
        f"adg_three_bucket_gap_report_{run_id}.md",
    }


def test_existing_bundle_reuse_requires_exact_wrapper_certification_gates(
    temp_artifacts,
):
    report_path = wrapper.ARTIFACTS_ADG / "adg_three_bucket_gap_report_test.json"
    report_path.write_text(json.dumps({"status": "complete"}), encoding="utf-8")
    gate = SimpleNamespace(
        key="wrapper_three_bucket_report",
        required=True,
        status="pass",
        producer_exit_code=0,
        paths=[str(report_path)],
    )
    manifest = wrapper.ARTIFACTS_ADG / "bundle.json"
    manifest.write_text(
        json.dumps(
            {
                "gates": [
                    {
                        "key": gate.key,
                        "required": True,
                        "status": "pass",
                        "producer_exit_code": 0,
                        "paths": [str(report_path.resolve())],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    assert wrapper._bundle_matches_certification_gates(manifest, [gate])
    gate.paths = [str(wrapper.ARTIFACTS_ADG / "different.json")]
    assert not wrapper._bundle_matches_certification_gates(manifest, [gate])


def test_wrapper_renders_one_bundle_only_after_receipt(
    temp_artifacts,
    monkeypatch,
):
    snap = _make_snapshot(temp_artifacts / "snap.sqlite", with_runtime_view=True, attested=1)
    _patch_generator(monkeypatch, snapshot=snap)
    call_order: list[str] = []
    monkeypatch.setattr(
        wrapper,
        "_run_report",
        lambda **_kwargs: call_order.append("three_bucket_report") or 0,
    )
    stage2_artifact = wrapper.ARTIFACTS_ADG / "adg_three_bucket_gap_report_06292026_0101.json"
    stage2_artifact.write_text(json.dumps({"status": "complete"}), encoding="utf-8")
    monkeypatch.setattr(
        wrapper,
        "_capture_three_bucket_report_paths",
        lambda **_kwargs: ([stage2_artifact], []),
    )

    import tools.reports.adg_run_output_bundle as bundle_mod

    gate_results = wrapper.ARTIFACTS_ADG / "adg_gate_results_20260717_120000.json"
    gate_results.write_text(
        json.dumps({"overall_exit_code": 0, "snapshot_path": str(snap), "gates": []}),
        encoding="utf-8",
    )
    terminal = wrapper.ARTIFACTS_ADG / "adg_bcg_executive_summary_test.md"
    terminal.write_text("## ADG Executive Brief\n\n- **Decision gate:** PASS\n", encoding="utf-8")
    bundle = SimpleNamespace(
        run_id="06292026_0101",
        status="complete",
        required_exit_code=0,
        terminal_summary_path=terminal,
        gates=[],
    )
    enforcement = wrapper.ARTIFACTS_ADG / "adg_enforcement_report_06292026_0101.json"

    def _emit_bundle(**kwargs):
        assert kwargs["enforcement_report_path"] == enforcement
        assert [gate.key for gate in kwargs["certification_gates"]] == [
            "wrapper_three_bucket_report",
            "wrapper_enforcement",
        ]
        assert all(gate.status == "pass" for gate in kwargs["certification_gates"])
        call_order.append("bundle")
        return [], bundle, gate_results

    monkeypatch.setattr(
        wrapper,
        "_emit_mandatory_run_outputs",
        _emit_bundle,
    )
    monkeypatch.setattr(
        wrapper,
        "_run_certification_plane2",
        lambda **_kwargs: call_order.append("plane2") or [],
    )

    import tools.adg.integration.enforcement_report as enforcement_mod

    monkeypatch.setattr(
        enforcement_mod,
        "build_enforcement_report",
        lambda **_kwargs: {
            "certified_rollup": "CERTIFIED",
            "snapshot_path": str(snap),
            "p0_failed": [],
            "planes": {"plane1": [], "plane2": [], "plane3": {}},
        },
    )

    def _write_enforcement(_report, *, ts=None):  # noqa: ANN001, ARG001
        call_order.append("enforcement")
        enforcement.write_text(json.dumps(_report), encoding="utf-8")
        return enforcement

    monkeypatch.setattr(enforcement_mod, "write_enforcement_report", _write_enforcement)
    monkeypatch.setattr(
        wrapper,
        "_build_repair_handoff",
        lambda **_kwargs: (
            "certified",
            {"status": "certified", "artifacts": {}, "validation_errors": []},
            [],
        ),
    )
    monkeypatch.setattr(wrapper, "_run_retention_sweep", lambda *_args, **_kwargs: None)
    immutable_receipt = wrapper.ARTIFACTS_ADG / "handoffs" / "receipt.json"
    immutable_handoff = wrapper.ARTIFACTS_ADG / "handoffs" / "handoff.json"
    monkeypatch.setattr(
        wrapper,
        "_prepare_immutable_publication",
        lambda *_args, **_kwargs: (
            call_order.append("receipt")
            or wrapper.PublicationDocuments(
                receipt_path=immutable_receipt,
                handoff_path=immutable_handoff,
                latest_handoff_pointer={},
                receipt_text="{}\n",
            )
        ),
    )
    monkeypatch.setattr(
        wrapper,
        "_publish_result_snapshot_pointer",
        lambda *_args, **_kwargs: call_order.append("activation") or [],
    )
    monkeypatch.setattr(
        wrapper,
        "_publish_convenience_aliases",
        lambda *_args, **_kwargs: call_order.append("aliases") or [],
    )
    monkeypatch.setattr(
        bundle_mod,
        "print_adg_run_terminal_summary",
        lambda *_args, **kwargs: (
            call_order.append("terminal") if kwargs.get("print_terminal", True) else None
        ),
    )

    wrapper.run_audit(mode="certification")

    assert call_order == [
        "plane2",
        "three_bucket_report",
        "enforcement",
        "bundle",
        "receipt",
        "activation",
        "aliases",
    ]


def test_failed_generator_seals_degraded_bundle_but_blocks_handoff(
    temp_artifacts,
    monkeypatch,
    capsys,
):
    stamp = "06292026_0202"
    snap = _make_snapshot(
        wrapper.ARTIFACTS_ADG / f"adg_indexed_{stamp}.sqlite",
        with_runtime_view=True,
        attested=1,
    )
    _patch_generator(monkeypatch, return_code=1, snapshot=snap, gate_kwargs={"ts": stamp})
    _patch_report(monkeypatch)

    import tools.reports.adg_run_output_bundle as bundle_mod

    call_order: list[tuple[str, bool]] = []

    def _fake_bundle(**kwargs):
        call_order.append(("bundle", kwargs["print_terminal"]))
        terminal = wrapper.ARTIFACTS_ADG / f"adg_run_terminal_summary_{kwargs['run_id']}.md"
        terminal.write_text(
            "## ADG Executive Brief\n\n"
            "- **Impact Inventory:** unavailable\n"
            "- **Decision gate:** BLOCKED\n"
            "- **Fix now:** rerun the dispatcher\n",
            encoding="utf-8",
        )
        manifest = wrapper.ARTIFACTS_ADG / f"adg_run_output_bundle_{kwargs['run_id']}.json"
        manifest.write_text(json.dumps({"status": "blocked"}), encoding="utf-8")
        (wrapper.ARTIFACTS_ADG / "adg_burndown_report.md").write_text(
            "# ADG CI Burndown Report\n",
            encoding="utf-8",
        )
        return bundle_mod.ADGRunOutputBundleResult(
            run_id=kwargs["run_id"],
            status="blocked",
            required_exit_code=2,
            manifest_path=manifest,
            terminal_summary_path=terminal,
            gates=[],
            artifact_paths=[terminal, manifest],
        )

    monkeypatch.setattr(bundle_mod, "emit_adg_run_output_bundle", _fake_bundle)

    def _fake_terminal(
        result,
        *,
        final_exit_code,
        diagnostics=None,
        print_terminal=True,
        **_kwargs,
    ):  # noqa: ANN001
        markdown = result.terminal_summary_path.read_text(encoding="utf-8")
        markdown = markdown.split("\n## Final disposition", 1)[0].rstrip()
        markdown += f"\n## Final disposition\n\n- **Process exit code:** `{final_exit_code}`\n"
        for diagnostic in diagnostics or []:
            markdown += f"- **Diagnostic:** {diagnostic}\n"
        result.terminal_summary_path.write_text(markdown, encoding="utf-8")
        if print_terminal:
            print(markdown)

    monkeypatch.setattr(bundle_mod, "print_adg_run_terminal_summary", _fake_terminal)
    monkeypatch.setattr(wrapper, "_run_certification_plane2", lambda **_kwargs: [])

    def _fake_action_queue(**kwargs):
        path = wrapper.ARTIFACTS_ADG / f"adg_action_queue_{kwargs['adg_run_id']}.json"
        path.write_text(
            json.dumps({"sections": {}, "priority_rows": [], "report_only_rows": []}),
            encoding="utf-8",
        )
        return path, []

    monkeypatch.setattr(wrapper, "_ensure_action_queue_for_handoff", _fake_action_queue)

    result = wrapper.run_audit(mode="certification", continue_on_p0=True)

    assert result.certification_status == "failed"
    assert result.artifact_status == "incomplete"
    assert call_order == [("bundle", False)]
    for name in (
        f"adg_gate_results_{stamp}.json",
        f"adg_action_queue_{stamp}.json",
        f"adg_burndown_table_{stamp}.json",
        f"adg_run_output_bundle_{stamp}.json",
    ):
        assert (wrapper.ARTIFACTS_ADG / name).is_file()
    assert (wrapper.ARTIFACTS_ADG / "adg_burndown_report.md").is_file()
    rendered = capsys.readouterr().out
    assert rendered.count("## ADG Executive Brief") == 1
    assert "# ADG CI Burndown Report" not in rendered

    gate_results = json.loads((wrapper.ARTIFACTS_ADG / f"adg_gate_results_{stamp}.json").read_text())
    burndown_table = json.loads((wrapper.ARTIFACTS_ADG / f"adg_burndown_table_{stamp}.json").read_text())
    assert gate_results["fallback_status"] == "degraded_pre_dispatch_fallback"
    assert set(burndown_table["summary"]) == {"P0", "P1", "P2", "P3"}
    assert all(key in result.repair_handoff["artifacts"] for key in wrapper.REPAIR_ARTIFACT_KEYS)
    assert any(
        "degraded pre-dispatch fallback" in error for error in result.repair_handoff["validation_errors"]
    )


def test_certification_fails_when_gate_invocation_manifest_missing(temp_artifacts, monkeypatch):
    snap = _make_snapshot(temp_artifacts / "snap.sqlite", with_runtime_view=True, attested=1)

    # Generator runs but writes ONLY the generation manifest (simulate crash mid-finalize).
    def _fake(extra_args, timeout_s, certification_mode):  # noqa: ARG001
        gen = {
            "timestamp": "x",
            "sqlite_path": str(snap),
            "snapshot_path": str(snap),
            "commit_sha": None,
            "repo_state_hash": None,
            "generation_exit_code": 0,
            "p0_status": "pass",
            "gate_manifest_path": str(temp_artifacts / "artifacts" / "adg" / "nonexistent.json"),
            "runtime_proof_status": "attested",
            "runtime_attested_edge_count": 1,
            "registry_bucket_edge_count": 0,
            "created_at_utc": "x",
            "certification_status": "clean",
        }
        (wrapper.ARTIFACTS_ADG / "adg_generation_manifest_test.json").write_text(json.dumps(gen))
        return 0

    monkeypatch.setattr(wrapper, "_run_generator", mock.Mock(side_effect=_fake))
    _patch_report(monkeypatch)
    result = wrapper.run_audit(mode="certification")
    assert result.certification_status == "failed"
    assert any("gate manifest path declared but missing" in r for r in result.reasons)


def test_certification_fails_when_required_gate_absent_from_manifest(temp_artifacts, monkeypatch):
    snap = _make_snapshot(temp_artifacts / "snap.sqlite", with_runtime_view=True, attested=1)
    # Build manifest with ONLY a subset of required gates.
    partial_gates = [
        {
            "name": "mcp_config_drift",
            "phase": "preflight",
            "kind": "python_function",
            "blocking_mode": "hard_fail",
            "status": "pass",
            "exit_code": 0,
            "duration_s": 0.01,
            "started_at_utc": "x",
            "finished_at_utc": "x",
            "script_rel": None,
            "message": None,
        }
    ]
    _patch_generator(monkeypatch, snapshot=snap, gate_kwargs={"gates": partial_gates})
    _patch_report(monkeypatch)
    result = wrapper.run_audit(mode="certification")
    assert result.certification_status == "failed"
    assert any("absent from manifest" in r for r in result.reasons)


def test_certification_fails_when_required_gate_skip_without_diagnostic_mode(temp_artifacts, monkeypatch):
    snap = _make_snapshot(temp_artifacts / "snap.sqlite", with_runtime_view=True, attested=1)
    gates = []
    for name in sorted(required_gate_names()):
        gates.append(
            {
                "name": name,
                "phase": "preflight",
                "kind": "python_function",
                "blocking_mode": "hard_fail",
                "status": "missing_script" if name == "wiring" else "pass",
                "exit_code": None,
                "duration_s": 0.0,
                "started_at_utc": "x",
                "finished_at_utc": "x",
                "script_rel": "ops_scripts/ci/check_expected_wiring.py",
                "message": None,
            }
        )
    _patch_generator(monkeypatch, snapshot=snap, gate_kwargs={"gates": gates})
    _patch_report(monkeypatch)
    result = wrapper.run_audit(mode="certification")
    assert result.certification_status == "failed"
    assert any("wiring" in r and "missing_script" in r for r in result.reasons)


def test_missing_post_adg_hard_gate_script_fails_certification(temp_artifacts, monkeypatch):
    # Same as above but using any required gate — ensures categorical behavior.
    snap = _make_snapshot(temp_artifacts / "snap.sqlite", with_runtime_view=True, attested=1)
    gates = []
    for name in sorted(required_gate_names()):
        gates.append(
            {
                "name": name,
                "phase": "post-ADG-subprocess",
                "kind": "subprocess",
                "blocking_mode": "hard_fail",
                "status": "missing_script" if name == "test-coverage" else "pass",
                "exit_code": None,
                "duration_s": 0.0,
                "started_at_utc": "x",
                "finished_at_utc": "x",
                "script_rel": "ops_scripts/ci/check_test_harness_coverage.py",
                "message": None,
            }
        )
    _patch_generator(monkeypatch, snapshot=snap, gate_kwargs={"gates": gates})
    _patch_report(monkeypatch)
    result = wrapper.run_audit(mode="certification")
    assert result.certification_status == "failed"


def test_post_adg_subprocess_ci_failure_exits_nonzero(temp_artifacts, monkeypatch):
    snap = _make_snapshot(temp_artifacts / "snap.sqlite", with_runtime_view=True, attested=1)
    gates = []
    for name in sorted(required_gate_names()):
        gates.append(
            {
                "name": name,
                "phase": "post-ADG-subprocess",
                "kind": "subprocess",
                "blocking_mode": "hard_fail",
                "status": "fail" if name == "lifecycle" else "pass",
                "exit_code": 1,
                "duration_s": 0.0,
                "started_at_utc": "x",
                "finished_at_utc": "x",
                "script_rel": None,
                "message": None,
            }
        )
    _patch_generator(monkeypatch, snapshot=snap, gate_kwargs={"gates": gates})
    _patch_report(monkeypatch)
    result = wrapper.run_audit(mode="certification")
    assert result.certification_status == "failed"


def test_p0_failure_halts_in_normal_mode(temp_artifacts, monkeypatch):
    snap = _make_snapshot(temp_artifacts / "snap.sqlite", with_runtime_view=True, attested=1)
    _patch_generator(monkeypatch, return_code=1, snapshot=snap)
    _patch_report(monkeypatch)
    result = wrapper.run_audit(mode="certification")
    assert result.certification_status == "failed"


def test_p0_failure_with_continue_on_p0_completes_diagnostics_but_exits_nonzero(temp_artifacts, monkeypatch):
    snap = _make_snapshot(temp_artifacts / "snap.sqlite", with_runtime_view=True, attested=1)
    gen_mock = _patch_generator(monkeypatch, return_code=1, snapshot=snap)
    _patch_report(monkeypatch)
    result = wrapper.run_audit(mode="certification", continue_on_p0=True)
    # Generator was invoked with --continue-on-p0 in extra_args.
    assert "--continue-on-p0" in gen_mock.call_args.kwargs["extra_args"]
    assert result.certification_status == "failed"


def test_gate_invocation_manifest_is_written(temp_artifacts, monkeypatch):
    snap = _make_snapshot(temp_artifacts / "snap.sqlite", with_runtime_view=True, attested=1)
    _patch_generator(monkeypatch, snapshot=snap)
    _patch_report(monkeypatch)
    result = wrapper.run_audit(mode="certification")
    assert result.gate_manifest_path is not None
    assert result.gate_manifest_path.is_file()


@pytest.mark.parametrize(
    "gate_name", ["dead_production_imports", "structural_conformance", "witness_tier_gates", "p0_violations"]
)
def test_required_validation_gate_recorded_as_invoked(temp_artifacts, monkeypatch, gate_name):
    """Umbrella for: dead_production_imports, structural_conformance, witness_tier, closure (p0_violations)."""
    snap = _make_snapshot(temp_artifacts / "snap.sqlite", with_runtime_view=True, attested=1)
    _patch_generator(monkeypatch, snapshot=snap)
    _patch_report(monkeypatch)
    result = wrapper.run_audit(mode="certification")
    assert result.gate_manifest_path is not None
    manifest = json.loads(result.gate_manifest_path.read_text())
    names = {g["name"] for g in manifest["gates"]}
    assert gate_name in names


def test_subprocess_calls_use_sys_executable_and_shell_false_and_timeout(temp_artifacts, monkeypatch):
    """Verify the wrapper's real subprocess call enforces argv form + timeout (§14)."""
    snap = _make_snapshot(temp_artifacts / "snap.sqlite", with_runtime_view=True, attested=1)
    _write_manifests(wrapper.ARTIFACTS_ADG, snapshot=snap)

    captured: dict = {}

    def _fake_run(argv, **kwargs):
        captured["argv"] = argv
        captured["kwargs"] = kwargs
        return mock.Mock(returncode=0)

    # We call the internal helpers directly so we don't double-mock.
    with mock.patch("subprocess.run", side_effect=_fake_run):
        wrapper._run_report(snapshot=snap, fmt="json", require_runtime_proof=False, timeout_s=30)
    assert isinstance(captured["argv"], list)
    assert captured["argv"][0] == __import__("sys").executable
    assert captured["kwargs"].get("shell") is False
    assert captured["kwargs"].get("timeout") == 30


@pytest.mark.parametrize(
    "malformed_row",
    [
        None,
        {},
        {"name": []},
        {"name": "mcp_config_drift", "status": []},
    ],
)
def test_cross_check_required_gates_rejects_malformed_nonempty_rows(malformed_row):
    reasons = wrapper._cross_check_required_gates({"gates": [malformed_row]})

    assert any("gate manifest row 0 malformed" in reason for reason in reasons)


def test_no_hard_gate_failure_hidden_by_broad_exception(temp_artifacts, monkeypatch):
    """A failed required gate MUST surface in reasons; never silently discarded."""
    snap = _make_snapshot(temp_artifacts / "snap.sqlite", with_runtime_view=True, attested=1)
    gates = [
        {
            "name": name,
            "phase": "post-ADG-subprocess",
            "kind": "subprocess",
            "blocking_mode": "hard_fail",
            "status": "fail" if name == "wiring" else "pass",
            "exit_code": 1 if name == "wiring" else 0,
            "duration_s": 0.1,
            "started_at_utc": "x",
            "finished_at_utc": "x",
            "script_rel": None,
            "message": "intentional",
        }
        for name in sorted(required_gate_names())
    ]
    _patch_generator(monkeypatch, snapshot=snap, gate_kwargs={"gates": gates})
    _patch_report(monkeypatch)
    result = wrapper.run_audit(mode="certification")
    assert any("wiring" in r and "fail" in r for r in result.reasons)


def test_diagnostic_mode_certification_status_is_diagnostic_only(temp_artifacts, monkeypatch):
    snap = _make_snapshot(temp_artifacts / "snap.sqlite", with_runtime_view=True, attested=1)
    _patch_generator(monkeypatch, snapshot=snap)
    _patch_report(monkeypatch)
    result = wrapper.run_audit(mode="diagnostic")
    assert result.certification_status == "diagnostic_only"


def test_require_runtime_proof_fails_when_not_attested(temp_artifacts, monkeypatch):
    snap = _make_snapshot(temp_artifacts / "snap.sqlite", with_runtime_view=False, attested=0)
    _patch_generator(monkeypatch, snapshot=snap, runtime_proof_status="view_absent", runtime_attested=0)
    _patch_report(monkeypatch)
    result = wrapper.run_audit(mode="certification", require_runtime_proof=True)
    assert result.certification_status == "failed"
    assert any("runtime_proof_status" in r for r in result.reasons)


def test_runtime_proof_is_recomputed_from_snapshot_and_status_mismatch_blocks(
    temp_artifacts,
    monkeypatch,
):
    snap = _make_snapshot(temp_artifacts / "snap.sqlite", with_runtime_view=True, attested=0)
    _patch_generator(
        monkeypatch,
        snapshot=snap,
        runtime_proof_status="attested",
        runtime_attested=5,
    )
    _patch_report(monkeypatch)

    result = wrapper.run_audit(mode="certification", require_runtime_proof=True)

    assert result.runtime_proof_status == "view_present_zero_attested"
    assert result.certification_status == "failed"
    assert any(
        "runtime proof manifest mismatch" in reason
        and "declared status='attested' count=5" in reason
        and "observed status='view_present_zero_attested' count=0" in reason
        for reason in result.reasons
    )


def test_runtime_proof_attested_count_mismatch_blocks_even_when_status_matches(
    temp_artifacts,
    monkeypatch,
):
    snap = _make_snapshot(temp_artifacts / "snap.sqlite", with_runtime_view=True, attested=2)
    _patch_generator(
        monkeypatch,
        snapshot=snap,
        runtime_proof_status="attested",
        runtime_attested=5,
    )
    _patch_report(monkeypatch)

    result = wrapper.run_audit(mode="certification", require_runtime_proof=True)

    assert result.runtime_proof_status == "attested"
    assert result.certification_status == "failed"
    assert any(
        "runtime proof manifest mismatch" in reason
        and "declared status='attested' count=5" in reason
        and "observed status='attested' count=2" in reason
        for reason in result.reasons
    )


@pytest.mark.parametrize(
    ("manifest_digest", "expected"),
    [
        (None, "missing or malformed"),
        ("not-a-sha256", "missing or malformed"),
        ("0" * 64, "does not match exact snapshot bytes"),
    ],
)
def test_certification_blocks_missing_malformed_or_mismatched_snapshot_digest(
    temp_artifacts,
    monkeypatch,
    manifest_digest,
    expected,
):
    snap = _make_snapshot(temp_artifacts / "snap.sqlite", with_runtime_view=True, attested=1)
    original_run_generator = _patch_generator(monkeypatch, snapshot=snap)

    def _generate_then_tamper(*args, **kwargs):
        result = original_run_generator.side_effect(*args, **kwargs)
        manifest_path = wrapper.ARTIFACTS_ADG / "adg_generation_manifest_06292026_0101.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest_digest is None:
            manifest.pop("snapshot_sha256", None)
        else:
            manifest["snapshot_sha256"] = manifest_digest
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        return result

    monkeypatch.setattr(wrapper, "_run_generator", mock.Mock(side_effect=_generate_then_tamper))
    _patch_report(monkeypatch)

    result = wrapper.run_audit(mode="certification")

    assert result.certification_status == "failed"
    assert result.process_exit_code == 1
    assert result.artifact_status == "incomplete"
    assert result.repair_handoff is not None
    assert any("snapshot integrity:" in error for error in result.repair_handoff["validation_errors"])
    assert any(
        "generation manifest snapshot_sha256" in reason and expected in reason for reason in result.reasons
    )


def test_certification_detects_snapshot_tampering_after_manifest_write(
    temp_artifacts,
    monkeypatch,
):
    snap = _make_snapshot(temp_artifacts / "snap.sqlite", with_runtime_view=True, attested=1)
    original_run_generator = _patch_generator(monkeypatch, snapshot=snap)

    def _generate_then_tamper(*args, **kwargs):
        result = original_run_generator.side_effect(*args, **kwargs)
        con = sqlite3.connect(snap)
        try:
            con.execute("CREATE TABLE post_manifest_tamper (value TEXT)")
            con.commit()
        finally:
            con.close()
        return result

    monkeypatch.setattr(wrapper, "_run_generator", mock.Mock(side_effect=_generate_then_tamper))
    _patch_report(monkeypatch)

    result = wrapper.run_audit(mode="certification")

    assert result.certification_status == "failed"
    assert result.artifact_status == "incomplete"
    assert any(
        "generation manifest snapshot_sha256 does not match exact snapshot bytes" in reason
        for reason in result.reasons
    )


def test_certification_blocks_missing_snapshot_provenance_as_incomplete(
    temp_artifacts,
    monkeypatch,
):
    snap = _make_snapshot(temp_artifacts / "snap.sqlite", with_runtime_view=True, attested=1)
    original_run_generator = _patch_generator(monkeypatch, snapshot=snap)

    def _generate_then_tamper(*args, **kwargs):
        result = original_run_generator.side_effect(*args, **kwargs)
        manifest_path = wrapper.ARTIFACTS_ADG / "adg_generation_manifest_06292026_0101.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["commit_sha"] = None
        manifest["repo_state_hash"] = "moving-live-tree"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        return result

    monkeypatch.setattr(wrapper, "_run_generator", mock.Mock(side_effect=_generate_then_tamper))
    _patch_report(monkeypatch)

    result = wrapper.run_audit(mode="certification")

    assert result.certification_status == "failed"
    assert result.artifact_status == "incomplete"
    assert any("commit_sha missing or malformed" in reason for reason in result.reasons)
    assert any("repo_state_hash missing or malformed" in reason for reason in result.reasons)


def test_certification_blocks_manifest_provenance_mismatch_with_snapshot_meta(
    temp_artifacts,
    monkeypatch,
):
    snap = _make_snapshot(temp_artifacts / "snap.sqlite", with_runtime_view=True, attested=1)
    original_run_generator = _patch_generator(monkeypatch, snapshot=snap)

    def _generate_then_tamper(*args, **kwargs):
        result = original_run_generator.side_effect(*args, **kwargs)
        manifest_path = wrapper.ARTIFACTS_ADG / "adg_generation_manifest_06292026_0101.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["commit_sha"] = "c" * 40
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        return result

    monkeypatch.setattr(wrapper, "_run_generator", mock.Mock(side_effect=_generate_then_tamper))
    _patch_report(monkeypatch)

    result = wrapper.run_audit(mode="certification")

    assert result.certification_status == "failed"
    assert result.artifact_status == "incomplete"
    assert any(
        "generation manifest commit_sha differs from immutable snapshot meta" in reason
        for reason in result.reasons
    )


def test_diagnostic_mode_blocks_snapshot_integrity_failure_before_handoff_publication(
    temp_artifacts,
    monkeypatch,
):
    snap = _make_snapshot(temp_artifacts / "snap.sqlite", with_runtime_view=True, attested=1)
    original_run_generator = _patch_generator(monkeypatch, snapshot=snap)

    def _generate_then_tamper(*args, **kwargs):
        result = original_run_generator.side_effect(*args, **kwargs)
        manifest_path = wrapper.ARTIFACTS_ADG / "adg_generation_manifest_06292026_0101.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["snapshot_sha256"] = "0" * 64
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        return result

    monkeypatch.setattr(wrapper, "_run_generator", mock.Mock(side_effect=_generate_then_tamper))
    _patch_report(monkeypatch)

    result = wrapper.run_audit(mode="diagnostic")

    assert result.certification_status == "diagnostic_only"
    assert result.artifact_status == "incomplete"
    assert result.process_exit_code == 1
    assert wrapper._downstream_release_status(result) == "blocked"
    assert any(
        "generation manifest snapshot_sha256 does not match exact snapshot bytes" in reason
        for reason in result.reasons
    )


def test_unreadable_runtime_proof_publishes_blocked_receipt(
    temp_artifacts,
    monkeypatch,
):
    snap = _make_snapshot(temp_artifacts / "snap.sqlite", with_runtime_view=True, attested=1)
    _patch_generator(monkeypatch, snapshot=snap, runtime_attested=1)
    _patch_report(monkeypatch)

    import tools.generate._gate_manifest as gate_manifest_module

    monkeypatch.setattr(
        gate_manifest_module,
        "runtime_proof_from_sqlite",
        lambda _snapshot: ("snapshot_unreadable", 0),
    )

    result = wrapper.run_audit(mode="certification")

    assert result.runtime_proof_status == "snapshot_unreadable"
    assert result.certification_status == "failed"
    assert result.process_exit_code == 1
    assert result.artifact_status == "incomplete"
    assert any("runtime proof snapshot unreadable" in reason for reason in result.reasons)
    receipt = json.loads(wrapper.RECEIPT_PATH.read_text(encoding="utf-8"))
    assert receipt["run_state"]["runtime_proof_status"] == "snapshot_unreadable"
    assert receipt["artifact_status"] == "incomplete"
    assert wrapper._downstream_release_status(result) == "blocked"
    assert any("snapshot integrity:" in error for error in receipt["repair_handoff"]["validation_errors"])


def test_plane2_manifest_append_failure_is_explicit_and_non_destructive(
    tmp_path,
    monkeypatch,
):
    from tools.generate import _gate_manifest as gate_manifest_module

    manifest_path = tmp_path / "gate.json"
    manifest_path.write_text('{"gates": []}\n', encoding="utf-8")
    before = manifest_path.read_bytes()
    monkeypatch.setattr(
        gate_manifest_module,
        "_atomic_write_json",
        mock.Mock(side_effect=OSError("injected short-write guard")),
    )

    error = wrapper._append_manifest_gate_record(
        manifest_path,
        name="three_bucket_manifest_quick",
        status="pass",
        exit_code=0,
        message="test",
    )

    assert error == "gate manifest atomic plane-2 append failed: injected short-write guard"
    assert manifest_path.read_bytes() == before


@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        ([], "JSON document must be an object"),
        ({}, "gate manifest gates missing or malformed"),
        ({"gates": None}, "gate manifest gates missing or malformed"),
        ({"gates": {}}, "gate manifest gates missing or malformed"),
    ],
)
def test_plane2_manifest_append_rejects_wrong_json_shapes_without_mutation(
    tmp_path,
    payload,
    expected,
):
    manifest_path = tmp_path / "gate.json"
    manifest_path.write_text(json.dumps(payload), encoding="utf-8")
    before = manifest_path.read_bytes()

    error = wrapper._append_manifest_gate_record(
        manifest_path,
        name="three_bucket_manifest_quick",
        status="pass",
        exit_code=0,
        message="test",
    )

    assert error is not None and expected in error
    assert manifest_path.read_bytes() == before


def test_wrapper_writes_receipt(temp_artifacts, monkeypatch):
    snap = _make_snapshot(temp_artifacts / "snap.sqlite", with_runtime_view=True, attested=1)
    _patch_generator(monkeypatch, snapshot=snap)
    _patch_report(monkeypatch)
    wrapper.run_audit(mode="certification")
    assert wrapper.RECEIPT_PATH.is_file()
    payload = json.loads(wrapper.RECEIPT_PATH.read_text())
    assert payload["schema_version"] == wrapper.RECEIPT_SCHEMA_VERSION
    assert "run_state" in payload
    assert "artifact_status" in payload
    assert "repair_handoff" in payload


def test_certification_fails_when_dispatcher_block(temp_artifacts, monkeypatch):
    """DoD-3: plane-3 BLOCK fails certification via enforcement report."""
    snap = _make_snapshot(temp_artifacts / "snap.sqlite", with_runtime_view=True, attested=3)
    _patch_generator(
        monkeypatch,
        snapshot=snap,
        dispatcher_exit_code=1,
        dispatcher_gates=[
            {
                "gate_id": "3_write_sovereignty",
                "band": "P0",
                "enforcement": "block",
                "classification": "blocked",
                "status": "fail",
                "exit_code": 1,
                "violation_count": 1,
            }
        ],
    )
    _patch_report(monkeypatch)
    monkeypatch.setattr(wrapper, "_run_certification_plane2", lambda **_: [])

    result = wrapper.run_audit(mode="certification", require_runtime_proof=True)
    assert not result.ok
    assert result.certification_status == "failed"
    assert any("adg_gate_dispatcher" in r for r in result.reasons)


def test_derive_adg_run_stamp_falls_back_to_snapshot_filename():
    stamp = "06132026_0906"
    assert (
        wrapper._derive_adg_run_stamp(
            {"sqlite_path": f"artifacts/adg/adg_indexed_{stamp}.sqlite"},
            None,
            None,
        )
        == stamp
    )


def test_wrapper_runs_retention_from_recent_sqlite_when_manifest_missing(temp_artifacts, monkeypatch):
    stamp = "07012026_0354"
    snap = wrapper.ARTIFACTS_ADG / f"adg_indexed_{stamp}.sqlite"

    def _fake_generator(extra_args, timeout_s, certification_mode):  # noqa: ARG001
        _make_snapshot(snap, with_runtime_view=True, attested=1)
        return 1

    monkeypatch.setattr(wrapper, "_run_generator", mock.Mock(side_effect=_fake_generator))
    _patch_report(monkeypatch)
    retention = mock.Mock()
    monkeypatch.setattr(wrapper, "_run_retention_sweep", retention)

    result = wrapper.run_audit(mode="certification")

    retention.assert_called_once_with(stamp, adg_dir=wrapper.ARTIFACTS_ADG)
    assert result.certification_status == "failed"
    assert "generation manifest missing" in result.reasons[1]


def test_enforcement_report_uses_generation_manifest_run_stamp(temp_artifacts, monkeypatch):
    stamp = "06132026_0906"
    snap = _make_snapshot(
        wrapper.ARTIFACTS_ADG / f"adg_indexed_{stamp}.sqlite",
        with_runtime_view=True,
        attested=3,
    )
    _patch_generator(monkeypatch, snapshot=snap, gate_kwargs={"ts": stamp})
    _patch_report(monkeypatch)
    monkeypatch.setattr(wrapper, "_run_certification_plane2", lambda **_: [])

    captured: dict[str, str | None] = {}

    def _certified_report(**kwargs):  # noqa: ANN003
        captured["build_ts"] = kwargs.get("ts")
        return {
            "certified_rollup": "CERTIFIED",
            "snapshot_path": str(snap),
            "p0_failed": [],
            "planes": {"plane1": [], "plane2": [], "plane3": {}},
        }

    def _write_report(_report, *, ts=None):  # noqa: ANN001
        captured["write_ts"] = ts
        out = wrapper.ARTIFACTS_ADG / f"adg_enforcement_report_{ts}.json"
        out.write_text(json.dumps(_report), encoding="utf-8")
        return out

    import tools.adg.integration.enforcement_report as enforcement_mod

    monkeypatch.setattr(enforcement_mod, "build_enforcement_report", _certified_report)
    monkeypatch.setattr(enforcement_mod, "write_enforcement_report", _write_report)

    result = wrapper.run_audit(mode="certification", require_runtime_proof=True)

    assert result.ok
    assert captured == {"build_ts": stamp, "write_ts": stamp}


def test_clean_certification_run_returns_ok(temp_artifacts, monkeypatch):
    run_id = "06292026_0101"
    snap = _make_snapshot(
        wrapper.ARTIFACTS_ADG / f"adg_indexed_{run_id}.sqlite",
        with_runtime_view=True,
        attested=3,
    )
    _patch_generator(monkeypatch, snapshot=snap, gate_kwargs={"ts": run_id})
    _patch_report(monkeypatch)
    monkeypatch.setattr(wrapper, "_run_certification_plane2", lambda **_: [])

    def _certified_report(**_kwargs):  # noqa: ANN003
        return {
            "certified_rollup": "CERTIFIED",
            "snapshot_path": str(snap),
            "p0_failed": [],
            "planes": {"plane1": [], "plane2": [], "plane3": {}},
        }

    def _write_report(_report, ts=None):  # noqa: ANN001, ARG001
        out = wrapper.ARTIFACTS_ADG / "adg_enforcement_report_test.json"
        out.write_text(json.dumps(_report), encoding="utf-8")
        return out

    import tools.adg.integration.enforcement_report as enforcement_mod

    monkeypatch.setattr(enforcement_mod, "build_enforcement_report", _certified_report)
    monkeypatch.setattr(enforcement_mod, "write_enforcement_report", _write_report)

    result = wrapper.run_audit(mode="certification", require_runtime_proof=True)
    assert result.ok
    assert result.certification_status == "clean"
    assert result.reasons == []


def test_certification_generator_enables_three_bucket_env(monkeypatch):
    """ADR-079: CI certification must opt into three-bucket without changing default regen."""
    monkeypatch.delenv("ADG_THREE_BUCKET", raising=False)
    captured: dict[str, object] = {}

    def _fake_run(cmd, **kwargs):  # noqa: ANN001
        captured["env"] = dict(kwargs.get("env") or {})
        proc = mock.Mock()
        proc.returncode = 124
        return proc

    monkeypatch.setattr(wrapper.subprocess, "run", _fake_run)
    wrapper._run_generator(extra_args=[], timeout_s=10, certification_mode=True)
    env = captured["env"]
    assert env.get("ADG_CERTIFICATION_MODE") == "1"
    assert env.get("ADG_DEFER_OUTPUT_BUNDLE_TO_WRAPPER") == "1"
    assert env.get("ADG_THREE_BUCKET") == "1"
    assert env.get("ADG_THREE_BUCKET_SIGN") == "1"


def test_diagnostic_generator_does_not_force_three_bucket(monkeypatch):
    monkeypatch.delenv("ADG_THREE_BUCKET", raising=False)
    captured: dict[str, object] = {}

    def _fake_run(cmd, **kwargs):  # noqa: ANN001
        captured["env"] = dict(kwargs.get("env") or {})
        proc = mock.Mock()
        proc.returncode = 0
        return proc

    monkeypatch.setattr(wrapper.subprocess, "run", _fake_run)
    wrapper._run_generator(extra_args=[], timeout_s=10, certification_mode=False)
    env = captured["env"]
    assert env.get("ADG_DEFER_OUTPUT_BUNDLE_TO_WRAPPER") == "1"
    assert "ADG_THREE_BUCKET" not in env or env.get("ADG_THREE_BUCKET") != "1"


def _build_test_handoff(
    temp_artifacts: Path,
    *,
    gates: list[dict],
    certification_status: str,
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[str, dict, Path]:
    gen_manifest, gate_manifest, _snap = _write_handoff_inputs(
        temp_artifacts,
        gates=gates,
        final_exit_code=0 if certification_status == "clean" else 1,
    )
    status, handoff, errors = wrapper._build_repair_handoff(
        generation_manifest_path=gen_manifest,
        gate_manifest_path=gate_manifest,
        generation_manifest=json.loads(gen_manifest.read_text()),
        certification_status=certification_status,
        since_wall_start=time.time() - 1,
    )
    assert errors == []
    receipt = _write_receipt(temp_artifacts / "receipt.json", artifact_status=status, handoff=handoff)
    return status, handoff, receipt


def _wrapper_result_for_handoff(
    *,
    status: str,
    handoff: dict,
    run_id: str = "06252026_0101",
) -> wrapper.WrapperResult:
    return wrapper.WrapperResult(
        certification_status="clean" if status == "certified" else "failed",
        generator_exit_code=0 if status == "certified" else 1,
        report_exit_code=0,
        generation_manifest_path=None,
        gate_manifest_path=None,
        runtime_proof_status="attested",
        reasons=[] if status == "certified" else ["test failure"],
        artifact_status=status,
        artifact_status_source="direct",
        adg_run_id=run_id,
        started_at_utc="2026-06-25T01:00:00Z",
        completed_at_utc="2026-06-25T01:02:00Z",
        repair_handoff=handoff,
        process_exit_code=0 if status == "certified" else 1,
    )


def test_repair_counts_split_blockers_candidates_and_tracked_debt():
    action_queue = {
        "actions": [
            {"verdict_cluster": "FIX", "sort_band": "P0", "work_priority": "P0"},
            {"verdict_cluster": "CANDIDATE_BLOCKER_TRIAGE", "sort_band": "P0", "work_priority": "triage"},
            {
                "verdict_cluster": "CANDIDATE_BLOCKER_TRIAGE",
                "sort_band": "P0",
                "action_kind": "candidate_blocker_file",
                "source_artifact": "p0_wave_plan",
            },
            {"verdict_cluster": "FIX", "sort_band": "P1", "work_priority": "P0"},
        ]
    }
    gate_results = {
        "gates": [
            _gate_result(
                "G_REACH_l0_reachability",
                band="P0",
                enforcement="ratchet",
                classification="pass",
                violation_count=10,
                baseline_count=10,
            ),
            _gate_result(
                "O_tool_call_parity_ratchet",
                band="P1",
                enforcement="ratchet",
                classification="regressed",
                violation_count=2,
                baseline_count=1,
            ),
        ]
    }

    counts = wrapper._repair_counts(action_queue, gate_results)

    assert counts["open_blocker_fix_count"] == 2
    assert counts["critical_open_blocker_fix_count"] == 1
    assert counts["candidate_blocker_triage_count"] == 2
    assert counts["critical_tracked_debt_count"] == 1
    assert counts["high_open_blocker_fix_count"] == 1
    assert counts["high_ratchet_regression_count"] == 1


def test_repair_handoff_certified_status(temp_artifacts, monkeypatch):
    status, handoff, receipt = _build_test_handoff(
        temp_artifacts,
        gates=[],
        certification_status="clean",
        monkeypatch=monkeypatch,
    )

    assert status == "certified"
    assert handoff["counts"] == {
        "open_blocker_fix_count": 0,
        "critical_open_blocker_fix_count": 0,
        "candidate_blocker_triage_count": 0,
        "critical_tracked_debt_count": 0,
        "high_open_blocker_fix_count": 0,
        "high_ratchet_regression_count": 0,
        "high_ratchet_floor_tracked_debt_count": 0,
    }
    assert handoff["legacy_counts"]["P0_TRACKED_BACKLOG"] == 0
    _payload, counts, errors = wrapper.validate_repair_handoff_receipt(receipt)
    assert errors == []
    assert counts["open_blocker_fix_count"] == 0


def test_repair_handoff_repair_ready_status_and_counts(temp_artifacts, monkeypatch):
    gates = [
        _gate_result("10_infra_wiring", band="P0", enforcement="block", classification="blocked"),
        _gate_result(
            "O_tool_call_parity_ratchet",
            band="P1",
            enforcement="ratchet",
            classification="regressed",
            violation_count=2,
            baseline_count=1,
        ),
        _gate_result(
            "G_REACH_l0_reachability",
            band="P1",
            enforcement="ratchet",
            classification="pass",
            violation_count=10,
            baseline_count=10,
        ),
    ]
    status, handoff, receipt = _build_test_handoff(
        temp_artifacts,
        gates=gates,
        certification_status="failed",
        monkeypatch=monkeypatch,
    )

    assert status == "repair_ready"
    assert handoff["counts"] == {
        "open_blocker_fix_count": 2,
        "critical_open_blocker_fix_count": 1,
        "candidate_blocker_triage_count": 0,
        "critical_tracked_debt_count": 0,
        "high_open_blocker_fix_count": 1,
        "high_ratchet_regression_count": 1,
        "high_ratchet_floor_tracked_debt_count": 1,
    }
    assert handoff["legacy_counts"]["P0_FIX"] == 1
    assert handoff["legacy_counts"]["P1_FIX"] == 1
    _payload, counts, errors = wrapper.validate_repair_handoff_receipt(receipt)
    assert errors == []
    assert counts == handoff["counts"]


def test_receipt_rejects_nested_handoff_status_mismatch(temp_artifacts, monkeypatch):
    status, handoff, receipt = _build_test_handoff(
        temp_artifacts,
        gates=[_gate_result("10_infra_wiring")],
        certification_status="failed",
        monkeypatch=monkeypatch,
    )
    assert status == "repair_ready"
    handoff["status"] = "certified"
    _write_receipt(receipt, artifact_status=status, handoff=handoff)

    _payload, _counts, errors = wrapper.validate_repair_handoff_receipt(receipt)

    assert any("artifact_status differs from repair_handoff.status" in error for error in errors)


def test_receipt_recomputes_certified_status_for_clean_zero_blocker_run(
    temp_artifacts,
    monkeypatch,
):
    status, handoff, receipt = _build_test_handoff(
        temp_artifacts,
        gates=[],
        certification_status="clean",
        monkeypatch=monkeypatch,
    )
    assert status == "certified"
    payload = json.loads(receipt.read_text(encoding="utf-8"))
    payload["artifact_status"] = "repair_ready"
    payload["repair_handoff"]["status"] = "repair_ready"
    receipt.write_text(json.dumps(payload), encoding="utf-8")

    _payload, _counts, errors = wrapper.validate_repair_handoff_receipt(receipt)

    assert any("inconsistent with certification_status and recomputed blockers" in error for error in errors)


def test_receipt_cannot_relabel_clean_generation_as_failed_repair_ready(
    temp_artifacts,
    monkeypatch,
):
    status, handoff, receipt = _build_test_handoff(
        temp_artifacts,
        gates=[],
        certification_status="clean",
        monkeypatch=monkeypatch,
    )
    assert status == "certified"
    payload = json.loads(receipt.read_text(encoding="utf-8"))
    payload["run_state"]["certification_status"] = "failed"
    payload["artifact_status"] = "repair_ready"
    payload["repair_handoff"]["status"] = "repair_ready"
    receipt.write_text(json.dumps(payload), encoding="utf-8")

    _payload, _counts, errors = wrapper.validate_repair_handoff_receipt(receipt)

    assert any("receipt certification_status differs from generation_manifest" in error for error in errors)


def test_receipt_allows_governed_clean_generation_to_diagnostic_only_transition(
    temp_artifacts,
    monkeypatch,
):
    status, _handoff, receipt = _build_test_handoff(
        temp_artifacts,
        gates=[],
        certification_status="clean",
        monkeypatch=monkeypatch,
    )
    assert status == "certified"
    payload = json.loads(receipt.read_text(encoding="utf-8"))
    payload["run_state"]["certification_status"] = "diagnostic_only"
    payload["artifact_status"] = "repair_ready"
    payload["repair_handoff"]["status"] = "repair_ready"
    receipt.write_text(json.dumps(payload), encoding="utf-8")

    _payload, counts, errors = wrapper.validate_repair_handoff_receipt(receipt)

    assert counts["open_blocker_fix_count"] == 0
    assert errors == []


def test_receipt_recomputes_repair_ready_status_when_digest_bound_blockers_exist(
    temp_artifacts,
    monkeypatch,
):
    gen_manifest, gate_manifest, _snapshot = _write_handoff_inputs(
        temp_artifacts,
        gates=[_gate_result("10_infra_wiring")],
        final_exit_code=0,
    )
    generation = json.loads(gen_manifest.read_text(encoding="utf-8"))
    generation["certification_status"] = "clean"
    gen_manifest.write_text(json.dumps(generation), encoding="utf-8")
    status, handoff, build_errors = wrapper._build_repair_handoff(
        generation_manifest_path=gen_manifest,
        gate_manifest_path=gate_manifest,
        generation_manifest=generation,
        certification_status="failed",
        since_wall_start=time.time() - 1,
    )
    assert build_errors == []
    assert status == "repair_ready"
    handoff["status"] = "certified"
    receipt = _write_receipt(
        temp_artifacts / "receipt_blocker_status.json",
        artifact_status="certified",
        handoff=handoff,
    )

    _payload, counts, errors = wrapper.validate_repair_handoff_receipt(receipt)

    assert counts["open_blocker_fix_count"] == 1
    assert any("inconsistent with certification_status and recomputed blockers" in error for error in errors)


def test_failed_generation_status_does_not_invalidate_snapshot_authority(
    temp_artifacts,
    monkeypatch,
):
    gen_manifest, _gate_manifest, snapshot = _write_handoff_inputs(
        temp_artifacts,
        gates=[_gate_result("10_infra_wiring")],
    )
    manifest = json.loads(gen_manifest.read_text(encoding="utf-8"))

    reasons = wrapper._generation_snapshot_provenance_reasons(manifest, snapshot)

    assert manifest["certification_status"] == "failed"
    assert reasons == []


def test_repair_handoff_rejects_stale_recorded_counts(temp_artifacts, monkeypatch):
    gates = [
        _gate_result(
            "O_tool_call_parity_ratchet",
            band="P1",
            enforcement="ratchet",
            classification="regressed",
            violation_count=2,
            baseline_count=1,
        ),
    ]
    status, handoff, _receipt = _build_test_handoff(
        temp_artifacts,
        gates=gates,
        certification_status="failed",
        monkeypatch=monkeypatch,
    )
    handoff["counts"]["high_ratchet_regression_count"] = 0
    receipt = _write_receipt(
        temp_artifacts / "receipt_stale_counts.json", artifact_status=status, handoff=handoff
    )

    _payload, counts, errors = wrapper.validate_repair_handoff_receipt(receipt)

    assert counts["high_ratchet_regression_count"] == 1
    assert any("repair_handoff counts differ from digest-bound artifacts" in error for error in errors)


def test_repair_handoff_recovers_same_run_snapshot_when_manifest_paths_are_null(
    temp_artifacts,
    monkeypatch,
    capsys,
):
    gates = [
        _gate_result(
            "G_REACH_l0_reachability",
            band="P0",
            enforcement="ratchet",
            classification="regressed",
            violation_count=2799,
            baseline_count=2786,
        )
    ]
    gen_manifest, gate_manifest, snap = _write_handoff_inputs(
        temp_artifacts,
        run_id="06262026_2302",
        gates=gates,
        include_snapshot_paths=False,
        final_exit_code=1,
    )

    status, handoff, errors = wrapper._build_repair_handoff(
        generation_manifest_path=gen_manifest,
        gate_manifest_path=gate_manifest,
        generation_manifest=json.loads(gen_manifest.read_text(encoding="utf-8")),
        certification_status="failed",
        since_wall_start=time.time() - 1,
    )

    assert errors == []
    assert status == "repair_ready"
    assert Path(handoff["artifacts"]["snapshot"]["path"]).resolve() == snap.resolve()
    assert Path(handoff["artifacts"]["gate_results"]["path"]).is_file()
    assert Path(handoff["artifacts"]["action_queue"]["path"]).is_file()
    assert handoff["counts"]["candidate_blocker_triage_count"] >= 0
    assert handoff["counts"] | {"candidate_blocker_triage_count": 0} == {
        "open_blocker_fix_count": 1,
        "critical_open_blocker_fix_count": 1,
        "candidate_blocker_triage_count": 0,
        "critical_tracked_debt_count": 0,
        "high_open_blocker_fix_count": 0,
        "high_ratchet_regression_count": 0,
        "high_ratchet_floor_tracked_debt_count": 0,
    }

    receipt = _write_receipt(
        temp_artifacts / "receipt.json",
        artifact_status=status,
        handoff=handoff,
        run_id="06262026_2302",
    )
    _payload, counts, consumer_errors = wrapper.validate_repair_handoff_receipt(receipt)
    assert consumer_errors == []
    assert counts == handoff["counts"]

    rc = consume_adg_repair_handoff.main(["--receipt", str(receipt), "--json"])
    captured = capsys.readouterr()
    assert rc == 0
    assert '"ok": true' in captured.out
    assert '"artifact_status": "repair_ready"' in captured.out


def test_repair_handoff_pointer_validates_exact_receipt(temp_artifacts, monkeypatch, capsys):
    status, handoff, _receipt = _build_test_handoff(
        temp_artifacts,
        gates=[_gate_result("10_infra_wiring")],
        certification_status="failed",
        monkeypatch=monkeypatch,
    )
    wrapper._write_receipt(_wrapper_result_for_handoff(status=status, handoff=handoff))

    pointer = wrapper.ARTIFACTS_ADG / "handoffs" / "adg_repair_handoff_latest.json"
    receipt, counts, errors = wrapper.validate_repair_handoff_pointer(pointer)
    pointer_payload = json.loads(pointer.read_text(encoding="utf-8"))

    assert errors == []
    assert receipt is not None
    assert counts["open_blocker_fix_count"] == 1
    assert pointer_payload["downstream_release_status"] == "released"
    assert Path(pointer_payload["receipt_path"]).name == "adg_audit_pipeline_receipt_06252026_0101.json"
    assert Path(pointer_payload["receipt_path"]).is_file()
    assert Path(pointer_payload["receipt_path"]).resolve() != wrapper.RECEIPT_PATH.resolve()
    activation = json.loads((wrapper.ARTIFACTS_ADG / "adg_snapshot_repair.json").read_text(encoding="utf-8"))
    assert {
        "audit_receipt",
        "repair_handoff",
        "output_bundle",
    }.issubset(activation["source_artifacts"])

    rc = consume_adg_repair_handoff.main(["--handoff-pointer", str(pointer), "--json"])
    captured = capsys.readouterr()
    assert rc == 0
    assert '"ok": true' in captured.out
    assert '"dependency_status": "ready"' in captured.out
    assert '"handoff_pointer":' in captured.out


def test_pointer_rejects_digest_valid_immutable_handoff_status_source_drift(
    temp_artifacts,
    monkeypatch,
):
    status, handoff, _receipt = _build_test_handoff(
        temp_artifacts,
        gates=[_gate_result("10_infra_wiring")],
        certification_status="failed",
        monkeypatch=monkeypatch,
    )
    wrapper._write_receipt(_wrapper_result_for_handoff(status=status, handoff=handoff))
    pointer = wrapper.ARTIFACTS_ADG / "handoffs" / "adg_repair_handoff_latest.json"
    pointer_payload = json.loads(pointer.read_text(encoding="utf-8"))
    immutable_handoff = Path(pointer_payload["handoff_path"])
    handoff_payload = json.loads(immutable_handoff.read_text(encoding="utf-8"))
    handoff_payload["artifact_status"] = "certified"
    handoff_payload["artifact_status_source"] = "legacy"
    immutable_handoff.write_text(json.dumps(handoff_payload, indent=2) + "\n", encoding="utf-8")
    pointer_payload["handoff_sha256"] = wrapper._sha256(immutable_handoff)
    pointer.write_text(json.dumps(pointer_payload, indent=2) + "\n", encoding="utf-8")

    _receipt, _counts, errors = wrapper.validate_repair_handoff_pointer(pointer)

    assert any("immutable handoff artifact_status differs from receipt" in error for error in errors)
    assert any("immutable handoff artifact_status_source differs from receipt" in error for error in errors)


def test_pointer_rejects_envelope_drift_from_exact_immutable_documents(
    temp_artifacts,
    monkeypatch,
):
    status, handoff, _receipt = _build_test_handoff(
        temp_artifacts,
        gates=[_gate_result("10_infra_wiring")],
        certification_status="failed",
        monkeypatch=monkeypatch,
    )
    wrapper._write_receipt(_wrapper_result_for_handoff(status=status, handoff=handoff))
    pointer = wrapper.ARTIFACTS_ADG / "handoffs" / "adg_repair_handoff_latest.json"
    pointer_payload = json.loads(pointer.read_text(encoding="utf-8"))
    pointer_payload["artifact_status"] = "certified"
    pointer_payload["downstream_release_status"] = "blocked"
    pointer_payload["receipt_path"] = str(pointer.with_name("different_receipt.json"))
    pointer_payload["receipt_sha256"] = "0" * 64
    pointer.write_text(json.dumps(pointer_payload, indent=2) + "\n", encoding="utf-8")

    _receipt, _counts, errors = wrapper.validate_repair_handoff_pointer(pointer)

    assert any("pointer artifact_status differs from immutable handoff" in error for error in errors)
    assert any(
        "pointer downstream_release_status differs from immutable handoff" in error for error in errors
    )
    assert any("pointer receipt_path differs from immutable handoff" in error for error in errors)
    assert any("pointer receipt_sha256 differs from immutable handoff" in error for error in errors)


def test_receipt_rejects_process_exit_that_differs_from_output_bundle(
    temp_artifacts,
    monkeypatch,
):
    status, handoff, receipt = _build_test_handoff(
        temp_artifacts,
        gates=[_gate_result("10_infra_wiring")],
        certification_status="failed",
        monkeypatch=monkeypatch,
    )
    assert status == "repair_ready"
    payload = json.loads(receipt.read_text(encoding="utf-8"))
    payload["run_state"]["process_exit_code"] = 0
    receipt.write_text(json.dumps(payload), encoding="utf-8")

    _payload, _counts, errors = wrapper.validate_repair_handoff_receipt(receipt)

    assert any("process_exit_code differs from output_bundle final_exit_code" in error for error in errors)


def test_receipt_rejects_malformed_output_bundle_root(temp_artifacts, monkeypatch):
    status, handoff, receipt = _build_test_handoff(
        temp_artifacts,
        gates=[],
        certification_status="clean",
        monkeypatch=monkeypatch,
    )
    assert status == "certified"
    bundle = Path(handoff["artifacts"]["output_bundle"]["path"])
    bundle.write_text("[]\n", encoding="utf-8")

    _payload, _counts, errors = wrapper.validate_repair_handoff_receipt(receipt)

    assert any("output_bundle malformed" in error for error in errors)


def test_pointer_exception_after_atomic_replace_is_verified_as_committed(
    temp_artifacts,
    monkeypatch,
):
    status, handoff, _receipt = _build_test_handoff(
        temp_artifacts,
        gates=[_gate_result("10_infra_wiring")],
        certification_status="failed",
        monkeypatch=monkeypatch,
    )
    result = _wrapper_result_for_handoff(status=status, handoff=handoff)
    receipt = wrapper.ARTIFACTS_ADG / "handoffs" / "receipt.json"
    handoff_path = wrapper.ARTIFACTS_ADG / "handoffs" / "handoff.json"
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_text("{}\n", encoding="utf-8")
    handoff_path.write_text("{}\n", encoding="utf-8")

    from tools.adg.shared_modules import snapshot_registry

    real_publish = snapshot_registry.publish_snapshot_pointer

    def _publish_then_raise(**kwargs):
        real_publish(**kwargs)
        raise OSError("directory fsync failed after replace")

    monkeypatch.setattr(snapshot_registry, "publish_snapshot_pointer", _publish_then_raise)

    errors = wrapper._publish_result_snapshot_pointer(
        result,
        artifacts_adg=wrapper.ARTIFACTS_ADG,
        receipt_path=receipt,
        handoff_path=handoff_path,
    )

    assert errors == []
    pointer = snapshot_registry.load_snapshot_pointer(
        wrapper.ARTIFACTS_ADG,
        "repair",
        verify_digest=True,
    )
    assert pointer.path.name == "adg_indexed_06252026_0101.sqlite"


def test_older_run_cannot_roll_back_newer_role_pointer(temp_artifacts):
    from tools.adg.shared_modules import snapshot_registry

    def _publication(run_id: str) -> tuple[wrapper.WrapperResult, Path, Path]:
        snapshot = _make_snapshot(
            wrapper.ARTIFACTS_ADG / f"adg_indexed_{run_id}.sqlite",
            with_runtime_view=True,
            attested=1,
        )
        refs: dict[str, dict[str, str]] = {
            "snapshot": {
                "artifact_key": "snapshot",
                "path": str(snapshot.resolve()),
                "sha256": wrapper._sha256(snapshot),
            }
        }
        for key in ("generation_manifest", "gate_manifest", "gate_results", "output_bundle"):
            source = wrapper.ARTIFACTS_ADG / f"{key}_{run_id}.json"
            source.write_text("{}\n", encoding="utf-8")
            refs[key] = {
                "artifact_key": key,
                "path": str(source.resolve()),
                "sha256": wrapper._sha256(source),
            }
        receipt = wrapper.ARTIFACTS_ADG / "handoffs" / f"receipt_{run_id}.json"
        handoff = wrapper.ARTIFACTS_ADG / "handoffs" / f"handoff_{run_id}.json"
        receipt.parent.mkdir(parents=True, exist_ok=True)
        receipt.write_text("{}\n", encoding="utf-8")
        handoff.write_text("{}\n", encoding="utf-8")
        result = wrapper.WrapperResult(
            certification_status="clean",
            generator_exit_code=0,
            report_exit_code=0,
            generation_manifest_path=None,
            gate_manifest_path=None,
            runtime_proof_status="attested",
            reasons=[],
            artifact_status="certified",
            artifact_status_source="direct",
            adg_run_id=run_id,
            repair_handoff={
                "status": "certified",
                "artifacts": refs,
                "validation_errors": [],
            },
            process_exit_code=0,
        )
        return result, receipt, handoff

    newer, newer_receipt, newer_handoff = _publication("06252026_0102")
    older, older_receipt, older_handoff = _publication("06252026_0101")

    assert (
        wrapper._publish_result_snapshot_pointer(
            newer,
            artifacts_adg=wrapper.ARTIFACTS_ADG,
            receipt_path=newer_receipt,
            handoff_path=newer_handoff,
        )
        == []
    )
    older_errors = wrapper._publish_result_snapshot_pointer(
        older,
        artifacts_adg=wrapper.ARTIFACTS_ADG,
        receipt_path=older_receipt,
        handoff_path=older_handoff,
    )

    assert any("equal or newer run is reserved" in error for error in older_errors)
    pointer = snapshot_registry.load_snapshot_pointer(
        wrapper.ARTIFACTS_ADG,
        "certified",
        verify_digest=True,
    )
    assert pointer.snapshot_id == "06252026_0102"


def test_blocked_current_run_replaces_stale_success_latest_state(
    temp_artifacts,
):
    stale_pointer = wrapper.ARTIFACTS_ADG / "handoffs" / "adg_repair_handoff_latest.json"
    stale_pointer.parent.mkdir(parents=True, exist_ok=True)
    wrapper.RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
    wrapper.RECEIPT_PATH.write_text(
        json.dumps({"artifact_status": "certified", "adg_run_id": "06242026_0101"}),
        encoding="utf-8",
    )
    stale_pointer.write_text(
        json.dumps(
            {
                "artifact_status": "certified",
                "downstream_release_status": "released",
                "adg_run_id": "06242026_0101",
            }
        ),
        encoding="utf-8",
    )
    (wrapper.ARTIFACTS_ADG / "adg_run_output_bundle_latest.json").write_text(
        json.dumps({"status": "complete", "run_id": "06242026_0101"}),
        encoding="utf-8",
    )
    result = wrapper.WrapperResult(
        certification_status="failed",
        generator_exit_code=1,
        report_exit_code=None,
        generation_manifest_path=None,
        gate_manifest_path=None,
        runtime_proof_status="view_absent",
        reasons=["generator failed"],
        artifact_status="incomplete",
        artifact_status_source="direct",
        adg_run_id="06252026_0101",
        repair_handoff={
            "status": "incomplete",
            "artifacts": {},
            "validation_errors": ["bundle unavailable"],
        },
        process_exit_code=1,
    )

    errors = wrapper._publish_blocked_latest_state(
        result,
        producer_artifacts=wrapper.ARTIFACTS_ADG,
        diagnostics=["bundle unavailable"],
    )

    assert errors == []
    receipt = json.loads(wrapper.RECEIPT_PATH.read_text(encoding="utf-8"))
    pointer = json.loads(stale_pointer.read_text(encoding="utf-8"))
    bundle = json.loads(
        (wrapper.ARTIFACTS_ADG / "adg_run_output_bundle_latest.json").read_text(encoding="utf-8")
    )
    assert receipt["artifact_status"] == "incomplete"
    assert receipt["adg_run_id"] == "06252026_0101"
    assert pointer["downstream_release_status"] == "blocked"
    assert pointer["adg_run_id"] == "06252026_0101"
    assert bundle["status"] == "blocked"
    assert bundle["run_id"] == "06252026_0101"
    _receipt, _counts, consumer_errors = wrapper.validate_repair_handoff_pointer(stale_pointer)
    assert consumer_errors
    assert any("not consumable" in error for error in consumer_errors)


def test_two_run_id_less_failures_publish_distinct_blocked_documents(temp_artifacts):
    result = wrapper.WrapperResult(
        certification_status="failed",
        generator_exit_code=73,
        report_exit_code=None,
        generation_manifest_path=None,
        gate_manifest_path=None,
        runtime_proof_status="view_absent",
        reasons=["run id collision"],
        artifact_status="incomplete",
        artifact_status_source="direct",
        adg_run_id=None,
        process_exit_code=1,
    )

    first = wrapper._publish_blocked_latest_state(
        result,
        producer_artifacts=wrapper.ARTIFACTS_ADG,
        diagnostics=["first failure"],
    )
    second = wrapper._publish_blocked_latest_state(
        result,
        producer_artifacts=wrapper.ARTIFACTS_ADG,
        diagnostics=["second failure"],
    )

    assert first == []
    assert second == []
    blocked_receipts = list(
        (wrapper.ARTIFACTS_ADG / "handoffs").glob("adg_audit_pipeline_receipt_*_blocked.json")
    )
    assert len(blocked_receipts) == 2
    latest = json.loads(wrapper.RECEIPT_PATH.read_text(encoding="utf-8"))
    assert latest["artifact_status"] == "incomplete"
    assert "second failure" in latest["run_state"]["reasons"]


def test_repair_handoff_pointer_publishes_to_contract_producer_root(temp_artifacts, monkeypatch):
    producer_root = temp_artifacts / "producer-root"
    producer_root.mkdir()
    contract = temp_artifacts / "automation.toml"
    contract.write_text(
        "\n".join(
            [
                "[handoff]",
                'handoff_pointer_base = "producer_repo_root"',
                f"producer_repo_root = {json.dumps(str(producer_root))}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(wrapper, "HANDOFF_CONTRACT_PATH", contract)
    status, handoff, _receipt = _build_test_handoff(
        temp_artifacts,
        gates=[_gate_result("10_infra_wiring")],
        certification_status="failed",
        monkeypatch=monkeypatch,
    )

    # Optional P7 inputs are provenance dependencies, not report-gate outputs,
    # so they are intentionally absent from the bundle inventory.  The
    # cross-root transport must still discover and carry every present input.
    p7_source = wrapper.ARTIFACTS_ADG / "p7" / "p0_wave_plan_06252026_0101.json"
    p7_source.parent.mkdir(parents=True)
    p7_source.write_text(json.dumps({"run_id": "06252026_0101", "waves": []}), encoding="utf-8")
    source_action = Path(handoff["artifacts"]["action_queue"]["path"])
    source_action_doc = json.loads(source_action.read_text(encoding="utf-8"))
    p7_row = next(
        row for row in source_action_doc["provenance"]["inputs"] if row["artifact_key"] == "p0_wave_plan"
    )
    p7_row.update(
        {
            "path": str(p7_source.resolve()),
            "digest_sha256": wrapper._sha256(p7_source),
            "status": "present",
        }
    )
    source_action.write_text(json.dumps(source_action_doc), encoding="utf-8")
    handoff["artifacts"]["action_queue"] = wrapper._artifact_ref("action_queue", source_action)
    publication_path = wrapper.ARTIFACTS_ADG / "adg_output_publication_06252026_0101.json"
    publication = json.loads(publication_path.read_text(encoding="utf-8"))
    next(row for row in publication["artifacts"] if Path(row["path"]) == source_action)["sha256"] = (
        wrapper._sha256(source_action)
    )
    publication_path.write_text(json.dumps(publication), encoding="utf-8")
    source_bundle = Path(handoff["artifacts"]["output_bundle"]["path"])
    source_bundle_doc = json.loads(source_bundle.read_text(encoding="utf-8"))
    for row in source_bundle_doc["artifacts"]:
        if Path(row["path"]) == source_action:
            row["sha256"] = wrapper._sha256(source_action)
        elif Path(row["path"]) == publication_path:
            row["sha256"] = wrapper._sha256(publication_path)
    source_bundle.write_text(json.dumps(source_bundle_doc), encoding="utf-8")
    handoff["artifacts"]["output_bundle"] = wrapper._artifact_ref("output_bundle", source_bundle)

    wrapper._write_receipt(_wrapper_result_for_handoff(status=status, handoff=handoff))

    pointer = producer_root / "artifacts" / "adg" / "handoffs" / "adg_repair_handoff_latest.json"
    pointer_payload = json.loads(pointer.read_text(encoding="utf-8"))
    handoff_path = Path(pointer_payload["handoff_path"])
    receipt_path = Path(pointer_payload["receipt_path"])
    handoff_payload = json.loads(handoff_path.read_text(encoding="utf-8"))
    receipt_payload = json.loads(receipt_path.read_text(encoding="utf-8"))

    assert pointer_payload["artifact_status"] == "repair_ready"
    assert pointer_payload["downstream_release_status"] == "released"
    assert handoff_path.parent == producer_root / "artifacts" / "adg" / "handoffs"
    assert receipt_path.parent == producer_root / "artifacts" / "adg" / "handoffs"
    assert receipt_payload["repair_handoff"] == handoff_payload["repair_handoff"]
    for ref in handoff_payload["repair_handoff"]["artifacts"].values():
        artifact_path = Path(ref["path"])
        assert artifact_path.parent == producer_root / "artifacts" / "adg"
        assert wrapper._sha256(artifact_path) == ref["sha256"]
    generation_manifest = json.loads(
        Path(handoff_payload["repair_handoff"]["artifacts"]["generation_manifest"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    assert Path(generation_manifest["sqlite_path"]).parent == producer_root / "artifacts" / "adg"
    assert Path(generation_manifest["snapshot_path"]).parent == producer_root / "artifacts" / "adg"
    assert Path(generation_manifest["gate_manifest_path"]).parent == producer_root / "artifacts" / "adg"

    transported = handoff_payload["repair_handoff"]["artifacts"]
    producer_adg = producer_root / "artifacts" / "adg"
    snapshot_path = Path(transported["snapshot"]["path"])
    bundle_path = Path(transported["output_bundle"]["path"])
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    from tools.reports.adg_run_output_bundle import validate_existing_adg_run_output_bundle

    bundle_valid, bundle_reason = validate_existing_adg_run_output_bundle(
        adg_artifacts_dir=producer_adg,
        run_id="06252026_0101",
        sqlite_path=snapshot_path,
    )
    assert bundle_valid, bundle_reason
    sealed_paths = [Path(row["path"]) for row in bundle["artifacts"]]
    sealed_paths.extend(Path(path) for gate in bundle["gates"] for path in gate["paths"])
    assert all(path.resolve().is_relative_to(producer_adg.resolve()) for path in sealed_paths)

    gate_results_path = Path(transported["gate_results"]["path"])
    gate_results = json.loads(gate_results_path.read_text(encoding="utf-8"))
    assert Path(gate_results["snapshot_path"]).resolve() == snapshot_path.resolve()
    burndown_path = Path(transported["burndown_table"]["path"])
    burndown = json.loads(burndown_path.read_text(encoding="utf-8"))
    assert Path(burndown["provenance"]["sqlite_source_path"]).resolve() == snapshot_path.resolve()
    action_path = Path(transported["action_queue"]["path"])
    action = json.loads(action_path.read_text(encoding="utf-8"))
    action_inputs = {
        row["artifact_key"]: row
        for row in action["provenance"]["inputs"]
        if row["artifact_key"] in {"gate_results", "burndown"}
    }
    assert Path(action_inputs["gate_results"]["path"]).resolve() == gate_results_path.resolve()
    assert action_inputs["gate_results"]["digest_sha256"] == wrapper._sha256(gate_results_path)
    assert Path(action_inputs["burndown"]["path"]).resolve() == burndown_path.resolve()
    assert action_inputs["burndown"]["digest_sha256"] == wrapper._sha256(burndown_path)
    transported_p7 = next(
        row for row in action["provenance"]["inputs"] if row["artifact_key"] == "p0_wave_plan"
    )
    transported_p7_path = Path(transported_p7["path"])
    assert transported_p7_path.resolve().is_relative_to(producer_adg.resolve())
    assert transported_p7_path.is_file()
    assert transported_p7["digest_sha256"] == wrapper._sha256(transported_p7_path)

    _receipt, _counts, errors = wrapper.validate_repair_handoff_pointer(pointer)
    assert errors == []


def test_run_generator_passes_validated_producer_snapshot_to_phase_d(
    temp_artifacts,
    monkeypatch,
):
    prior = _make_snapshot(
        wrapper.ARTIFACTS_ADG / "adg_indexed_06292026_0001.sqlite",
        with_runtime_view=False,
        attested=0,
    )
    subprocess_run = mock.Mock(return_value=mock.Mock(returncode=0))
    monkeypatch.setattr(wrapper, "_validated_producer_prior_snapshot", lambda _path: prior)
    monkeypatch.setattr(wrapper.subprocess, "run", subprocess_run)

    rc = wrapper._run_generator(
        extra_args=["--continue-on-p0"],
        timeout_s=30,
        certification_mode=True,
    )

    assert rc == 0
    assert subprocess_run.call_args.kwargs["env"]["ADG_PHASE_D_PRIOR_SNAPSHOT"] == str(prior)


def test_run_audit_uses_pre_resolved_producer_root_when_contract_disappears(
    temp_artifacts,
    monkeypatch,
):
    producer_root = temp_artifacts / "producer-root"
    producer_root.mkdir()
    contract = temp_artifacts / "automation.toml"
    contract.write_text(
        "\n".join(
            [
                "[handoff]",
                'handoff_pointer_base = "producer_repo_root"',
                f"producer_repo_root = {json.dumps(str(producer_root))}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(wrapper, "HANDOFF_CONTRACT_PATH", contract)

    stamp = "06292026_0303"
    snap = _make_snapshot(
        wrapper.ARTIFACTS_ADG / f"adg_indexed_{stamp}.sqlite",
        with_runtime_view=True,
        attested=1,
    )

    def _fake_generator(extra_args, timeout_s, certification_mode):  # noqa: ARG001
        _write_manifests(wrapper.ARTIFACTS_ADG, ts=stamp, snapshot=snap)
        contract.unlink()
        return 0

    monkeypatch.setattr(wrapper, "_run_generator", mock.Mock(side_effect=_fake_generator))
    monkeypatch.setattr(wrapper, "_run_certification_plane2", lambda **_: [])
    monkeypatch.setattr(wrapper, "_emit_mandatory_run_outputs", lambda **_: ([], None, None))
    monkeypatch.setattr(wrapper, "_run_retention_sweep", lambda adg_run_id, **_: None)
    _patch_report(monkeypatch)

    result = wrapper.run_audit(mode="certification")

    pointer = producer_root / "artifacts" / "adg" / "handoffs" / "adg_repair_handoff_latest.json"
    local_pointer = wrapper.ARTIFACTS_ADG / "handoffs" / "adg_repair_handoff_latest.json"
    pointer_payload = json.loads(pointer.read_text(encoding="utf-8"))

    assert result.adg_run_id == stamp
    assert pointer_payload["adg_run_id"] == stamp
    assert Path(pointer_payload["handoff_path"]).parent == producer_root / "artifacts" / "adg" / "handoffs"
    assert Path(pointer_payload["receipt_path"]).parent == producer_root / "artifacts" / "adg" / "handoffs"
    assert not local_pointer.exists()


def test_repair_handoff_pointer_rejects_legacy_ready_release_status(temp_artifacts, monkeypatch):
    status, handoff, _receipt = _build_test_handoff(
        temp_artifacts,
        gates=[_gate_result("10_infra_wiring")],
        certification_status="failed",
        monkeypatch=monkeypatch,
    )
    wrapper._write_receipt(_wrapper_result_for_handoff(status=status, handoff=handoff))
    pointer = wrapper.ARTIFACTS_ADG / "handoffs" / "adg_repair_handoff_latest.json"
    pointer_payload = json.loads(pointer.read_text(encoding="utf-8"))
    handoff_path = Path(pointer_payload["handoff_path"])
    handoff_payload = json.loads(handoff_path.read_text(encoding="utf-8"))
    handoff_payload["downstream_release_status"] = "ready"
    handoff_path.write_text(json.dumps(handoff_payload, indent=2) + "\n", encoding="utf-8")
    pointer_payload["handoff_sha256"] = wrapper._sha256(handoff_path)
    pointer.write_text(json.dumps(pointer_payload, indent=2) + "\n", encoding="utf-8")

    _receipt, _counts, errors = wrapper.validate_repair_handoff_pointer(pointer)

    assert any("downstream_release_status not released" in error for error in errors)


def test_repair_handoff_pointer_ignores_overwritten_latest_receipt(temp_artifacts, monkeypatch):
    status, handoff, _receipt = _build_test_handoff(
        temp_artifacts,
        gates=[_gate_result("10_infra_wiring")],
        certification_status="failed",
        monkeypatch=monkeypatch,
    )
    wrapper._write_receipt(_wrapper_result_for_handoff(status=status, handoff=handoff))
    receipt_payload = json.loads(wrapper.RECEIPT_PATH.read_text(encoding="utf-8"))
    receipt_payload["adg_run_id"] = "06252026_9999"
    wrapper.RECEIPT_PATH.write_text(json.dumps(receipt_payload), encoding="utf-8")

    pointer = wrapper.ARTIFACTS_ADG / "handoffs" / "adg_repair_handoff_latest.json"
    _receipt, counts, errors = wrapper.validate_repair_handoff_pointer(pointer)

    assert errors == []
    assert counts["open_blocker_fix_count"] == 1


def test_repair_handoff_pointer_rejects_overwritten_immutable_receipt(temp_artifacts, monkeypatch):
    status, handoff, _receipt = _build_test_handoff(
        temp_artifacts,
        gates=[_gate_result("10_infra_wiring")],
        certification_status="failed",
        monkeypatch=monkeypatch,
    )
    wrapper._write_receipt(_wrapper_result_for_handoff(status=status, handoff=handoff))
    pointer = wrapper.ARTIFACTS_ADG / "handoffs" / "adg_repair_handoff_latest.json"
    pointer_payload = json.loads(pointer.read_text(encoding="utf-8"))
    immutable_receipt = Path(pointer_payload["receipt_path"])
    receipt_payload = json.loads(immutable_receipt.read_text(encoding="utf-8"))
    receipt_payload["adg_run_id"] = "06252026_9999"
    immutable_receipt.write_text(json.dumps(receipt_payload), encoding="utf-8")

    _receipt, _counts, errors = wrapper.validate_repair_handoff_pointer(pointer)

    assert any("receipt sha256 mismatch" in error for error in errors)
    assert any("receipt adg_run_id" in error for error in errors)


def test_repair_handoff_pointer_rejects_missing_timestamped_artifact(temp_artifacts, monkeypatch):
    status, handoff, _receipt = _build_test_handoff(
        temp_artifacts,
        gates=[_gate_result("10_infra_wiring")],
        certification_status="failed",
        monkeypatch=monkeypatch,
    )
    wrapper._write_receipt(_wrapper_result_for_handoff(status=status, handoff=handoff))
    action_queue = Path(handoff["artifacts"]["action_queue"]["path"])
    action_queue.unlink()

    pointer = wrapper.ARTIFACTS_ADG / "handoffs" / "adg_repair_handoff_latest.json"
    _receipt, _counts, errors = wrapper.validate_repair_handoff_pointer(pointer)

    assert any("action_queue path does not exist" in error for error in errors)


def test_handoff_pointer_cli_reports_dependency_not_ready(temp_artifacts, monkeypatch, capsys):
    status, handoff, _receipt = _build_test_handoff(
        temp_artifacts,
        gates=[_gate_result("10_infra_wiring")],
        certification_status="failed",
        monkeypatch=monkeypatch,
    )
    wrapper._write_receipt(_wrapper_result_for_handoff(status=status, handoff=handoff))
    action_queue = Path(handoff["artifacts"]["action_queue"]["path"])
    action_queue.unlink()

    pointer = wrapper.ARTIFACTS_ADG / "handoffs" / "adg_repair_handoff_latest.json"
    rc = consume_adg_repair_handoff.main(["--handoff-pointer", str(pointer), "--json"])
    captured = capsys.readouterr()

    assert rc == 1
    assert '"ok": false' in captured.out
    assert '"dependency_status": "dependency_not_ready"' in captured.out


def test_repair_handoff_incomplete_when_required_artifact_stale(temp_artifacts, monkeypatch):
    gen_manifest, gate_manifest, _snap = _write_handoff_inputs(
        temp_artifacts,
        gates=[_gate_result("10_infra_wiring")],
    )
    status, handoff, errors = wrapper._build_repair_handoff(
        generation_manifest_path=gen_manifest,
        gate_manifest_path=gate_manifest,
        generation_manifest=json.loads(gen_manifest.read_text()),
        certification_status="failed",
        since_wall_start=time.time() + 60,
    )

    assert status == "incomplete"
    assert handoff["validation_errors"]
    assert any("stale" in error or "no timestamped gate_results" in error for error in errors)


def test_repair_handoff_incomplete_when_action_queue_missing(temp_artifacts, monkeypatch):
    gen_manifest, gate_manifest, _snap = _write_handoff_inputs(
        temp_artifacts,
        gates=[_gate_result("10_infra_wiring")],
    )
    monkeypatch.setattr(
        wrapper,
        "_ensure_action_queue_for_handoff",
        lambda **_kwargs: (None, ["action_queue intentionally missing"]),
    )

    status, handoff, errors = wrapper._build_repair_handoff(
        generation_manifest_path=gen_manifest,
        gate_manifest_path=gate_manifest,
        generation_manifest=json.loads(gen_manifest.read_text()),
        certification_status="failed",
        since_wall_start=time.time() - 1,
    )

    assert status == "incomplete"
    assert any("action_queue" in error for error in errors)
    assert "action_queue" not in handoff["artifacts"]


def test_repair_handoff_consumer_rejects_latest_only_artifact(temp_artifacts, monkeypatch):
    _status, handoff, receipt = _build_test_handoff(
        temp_artifacts,
        gates=[_gate_result("10_infra_wiring")],
        certification_status="failed",
        monkeypatch=monkeypatch,
    )
    queue_path = Path(handoff["artifacts"]["action_queue"]["path"])
    latest_path = queue_path.with_name("adg_action_queue_latest.json")
    latest_path.write_text(queue_path.read_text(encoding="utf-8"), encoding="utf-8")
    handoff["artifacts"]["action_queue"] = wrapper._artifact_ref("action_queue", latest_path)
    _write_receipt(receipt, artifact_status="repair_ready", handoff=handoff)

    _payload, _counts, errors = wrapper.validate_repair_handoff_receipt(receipt)
    assert any("latest-only" in error for error in errors)


def test_repair_handoff_consumer_rejects_digest_mismatch(temp_artifacts, monkeypatch):
    _status, handoff, receipt = _build_test_handoff(
        temp_artifacts,
        gates=[_gate_result("10_infra_wiring")],
        certification_status="failed",
        monkeypatch=monkeypatch,
    )
    gate_results_path = Path(handoff["artifacts"]["gate_results"]["path"])
    gate_results_path.write_text(gate_results_path.read_text(encoding="utf-8") + "\n", encoding="utf-8")

    _payload, _counts, errors = wrapper.validate_repair_handoff_receipt(receipt)
    assert any("sha256 mismatch" in error for error in errors)


@pytest.mark.parametrize("artifact_key", ["action_queue", "gate_results"])
def test_consumer_rejects_digest_valid_malformed_action_or_gate_rows_without_crashing(
    temp_artifacts,
    monkeypatch,
    artifact_key,
):
    status, handoff, receipt = _build_test_handoff(
        temp_artifacts,
        gates=[_gate_result("10_infra_wiring")],
        certification_status="failed",
        monkeypatch=monkeypatch,
    )
    artifact_path = Path(handoff["artifacts"][artifact_key]["path"])
    document = json.loads(artifact_path.read_text(encoding="utf-8"))
    row_key = "actions" if artifact_key == "action_queue" else "gates"
    document[row_key] = [None]
    artifact_path.write_text(json.dumps(document), encoding="utf-8")
    _reseal_digest_bound_queue_and_gate_results(handoff)
    _write_receipt(receipt, artifact_status=status, handoff=handoff)

    _payload, _counts, errors = wrapper.validate_repair_handoff_receipt(receipt)

    assert any(f"{artifact_key} {row_key} row 0 malformed" in error for error in errors)


def test_consumer_revalidates_generation_manifest_snapshot_digest_authority(
    temp_artifacts,
    monkeypatch,
):
    status, handoff, receipt = _build_test_handoff(
        temp_artifacts,
        gates=[_gate_result("10_infra_wiring")],
        certification_status="failed",
        monkeypatch=monkeypatch,
    )
    manifest_path = Path(handoff["artifacts"]["generation_manifest"]["path"])
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["snapshot_sha256"] = "0" * 64
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    handoff["artifacts"]["generation_manifest"] = wrapper._artifact_ref(
        "generation_manifest",
        manifest_path,
    )
    _write_receipt(receipt, artifact_status=status, handoff=handoff)

    _payload, _counts, errors = wrapper.validate_repair_handoff_receipt(receipt)

    assert any(
        "generation manifest snapshot_sha256 does not match exact snapshot bytes" in error for error in errors
    )


def test_consumer_revalidates_manifest_provenance_against_snapshot_meta(
    temp_artifacts,
    monkeypatch,
):
    status, handoff, receipt = _build_test_handoff(
        temp_artifacts,
        gates=[_gate_result("10_infra_wiring")],
        certification_status="failed",
        monkeypatch=monkeypatch,
    )
    manifest_path = Path(handoff["artifacts"]["generation_manifest"]["path"])
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["repo_state_hash"] = "c" * 40
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    handoff["artifacts"]["generation_manifest"] = wrapper._artifact_ref(
        "generation_manifest",
        manifest_path,
    )
    _write_receipt(receipt, artifact_status=status, handoff=handoff)

    _payload, _counts, errors = wrapper.validate_repair_handoff_receipt(receipt)

    assert any(
        "generation manifest repo_state_hash differs from immutable snapshot meta" in error
        for error in errors
    )


def test_consumer_rejects_snapshot_sidecars_even_when_main_file_digest_matches(
    temp_artifacts,
    monkeypatch,
):
    _status, handoff, receipt = _build_test_handoff(
        temp_artifacts,
        gates=[_gate_result("10_infra_wiring")],
        certification_status="failed",
        monkeypatch=monkeypatch,
    )
    snapshot_path = Path(handoff["artifacts"]["snapshot"]["path"])
    Path(str(snapshot_path) + "-wal").write_bytes(b"unsealed-wal")

    _payload, _counts, errors = wrapper.validate_repair_handoff_receipt(receipt)

    assert any("SQLite snapshot sidecars present" in error for error in errors)
    assert any("runtime proof snapshot unreadable" in error for error in errors)


def test_consumer_rechecks_snapshot_readability(temp_artifacts, monkeypatch):
    _status, _handoff, receipt = _build_test_handoff(
        temp_artifacts,
        gates=[_gate_result("10_infra_wiring")],
        certification_status="failed",
        monkeypatch=monkeypatch,
    )
    import tools.generate._gate_manifest as gate_manifest_module

    monkeypatch.setattr(
        gate_manifest_module,
        "runtime_proof_from_sqlite",
        lambda _snapshot: ("snapshot_unreadable", 0),
    )

    _payload, _counts, errors = wrapper.validate_repair_handoff_receipt(receipt)

    assert any("runtime proof snapshot unreadable" in error for error in errors)


def test_consumer_fails_closed_for_incomplete_receipt(temp_artifacts, monkeypatch, capsys):
    receipt = _write_receipt(
        temp_artifacts / "receipt.json",
        artifact_status="incomplete",
        handoff={"status": "incomplete", "artifacts": {}, "counts": {}, "validation_errors": ["missing"]},
    )

    rc = consume_adg_repair_handoff.main(["--receipt", str(receipt), "--json"])
    captured = capsys.readouterr()
    assert rc == 1
    assert '"ok": false' in captured.out

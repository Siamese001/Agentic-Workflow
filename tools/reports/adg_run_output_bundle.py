"""Seal the post-generation ADG report set exactly once.

The full ADG pipeline has several report producers with different return
contracts.  This module gives them one orchestration boundary: inputs are
bound to the current SQLite snapshot, required outputs fail closed, producer
noise is captured in a machine-readable manifest, and one terminal summary is
printed after every output gate has reached a terminal state.
"""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import yaml

SCHEMA_VERSION = "adg-run-output-bundle/v1"
REPO_ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS_ADG = REPO_ROOT / "artifacts" / "adg"
DOCS_ADG = REPO_ROOT / "docs" / "reports" / "adg"
REQUIRED_OUTPUT_KEYS = frozenset(
    {
        "bcg_gate_adapter",
        "burndown_report",
        "action_queue",
        "review_template",
        "bcg_executive_summary",
        "latest_publication",
    }
)


@dataclass
class OutputGate:
    """One report producer's normalized terminal state."""

    key: str
    required: bool
    status: str
    producer_exit_code: int | None = None
    paths: list[str] = field(default_factory=list)
    diagnostic: str = ""


@dataclass
class ADGRunOutputBundleResult:
    """Result returned to the generator and audit wrapper."""

    run_id: str
    status: str
    required_exit_code: int
    manifest_path: Path
    terminal_summary_path: Path | None
    gates: list[OutputGate]
    artifact_paths: list[Path]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        temporary.write_text(text, encoding="utf-8")
        os.replace(temporary, path)
    finally:
        try:
            temporary.unlink(missing_ok=True)
        except OSError:
            pass


@contextlib.contextmanager
def _publication_lock(adg_artifacts_dir: Path, *, timeout_s: float = 30.0):
    """Serialize publication without relying on platform-specific file locks."""
    adg_artifacts_dir.mkdir(parents=True, exist_ok=True)
    lock_path = adg_artifacts_dir / ".adg_run_output_bundle_publish.lock"
    deadline = time.monotonic() + timeout_s
    descriptor: int | None = None
    while descriptor is None:
        try:
            descriptor = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            os.write(descriptor, f"pid={os.getpid()} acquired={_utc_now()}\n".encode())
        except FileExistsError:
            try:
                stale = time.time() - lock_path.stat().st_mtime > max(timeout_s * 4, 120.0)
            except OSError:
                stale = False
            if stale:
                try:
                    lock_path.unlink()
                except OSError:
                    pass
                continue
            if time.monotonic() >= deadline:
                raise TimeoutError(f"timed out waiting for publication lock: {lock_path}")
            time.sleep(0.05)
    try:
        yield
    finally:
        if descriptor is not None:
            os.close(descriptor)
        try:
            lock_path.unlink()
        except OSError:
            pass


def _run_order(run_id: str) -> tuple[int, str]:
    """Return a comparable order for both generator and dispatcher stamps."""
    for pattern in ("%m%d%Y_%H%M", "%Y%m%d_%H%M%S"):
        try:
            return int(datetime.strptime(run_id, pattern).strftime("%Y%m%d%H%M%S")), run_id
        except ValueError:
            continue
    return 0, run_id


def _reserve_latest_publication(adg_artifacts_dir: Path, run_id: str) -> None:
    """Advance a monotonic high-water mark before mutating any latest alias."""
    high_water_path = adg_artifacts_dir / ".adg_run_output_bundle_high_water.json"
    existing: dict[str, Any] = {}
    if high_water_path.is_file():
        try:
            existing = _load_object(high_water_path)
        except (OSError, json.JSONDecodeError, TypeError) as exc:
            raise RuntimeError(f"publication high-water mark is invalid: {exc}") from exc
    existing_run = existing.get("run_id")
    if isinstance(existing_run, str) and existing_run != run_id:
        if _run_order(existing_run) >= _run_order(run_id):
            raise RuntimeError(
                "latest publication rejected because an equal or newer run is reserved: "
                f"current={run_id} reserved={existing_run}"
            )
    _atomic_write_text(
        high_water_path,
        json.dumps({"run_id": run_id, "reserved_at_utc": _utc_now()}, indent=2, sort_keys=True) + "\n",
    )


def _run_owns_latest_reservation(adg_artifacts_dir: Path, run_id: str) -> bool:
    path = adg_artifacts_dir / ".adg_run_output_bundle_high_water.json"
    try:
        return _load_object(path).get("run_id") == run_id
    except (OSError, json.JSONDecodeError, TypeError):
        return False


def _load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON document must be an object: {path}")
    return value


def _resolve_declared_path(raw: object, *, repo_root: Path) -> Path | None:
    if not isinstance(raw, str) or not raw.strip():
        return None
    candidate = Path(raw)
    return (candidate if candidate.is_absolute() else repo_root / candidate).resolve()


def _same_file(left: Path, right: Path) -> bool:
    try:
        return left.samefile(right)
    except OSError:
        return os.path.normcase(str(left.resolve())) == os.path.normcase(str(right.resolve()))


def _validate_current_run_inputs(
    *,
    sqlite_path: Path,
    gate_results_path: Path,
    burndown_path: Path,
    repo_root: Path,
) -> list[str]:
    errors: list[str] = []
    sqlite_path = sqlite_path.resolve()
    if not sqlite_path.is_file():
        errors.append(f"snapshot missing: {sqlite_path}")

    gates_doc: dict[str, Any] | None = None
    if not gate_results_path.is_file():
        errors.append(f"gate results missing: {gate_results_path}")
    else:
        try:
            gates_doc = _load_object(gate_results_path)
        except (OSError, json.JSONDecodeError, TypeError) as exc:
            errors.append(f"gate results invalid: {exc}")

    if gates_doc is not None:
        if not isinstance(gates_doc.get("gates"), list) or not gates_doc["gates"]:
            errors.append("gate results must contain a non-empty gates[]")
        if not isinstance(gates_doc.get("timestamp"), str) or not gates_doc.get("timestamp"):
            errors.append("gate results missing timestamp")
        if not isinstance(gates_doc.get("overall_exit_code"), int) or isinstance(
            gates_doc.get("overall_exit_code"), bool
        ):
            errors.append("gate results missing integer overall_exit_code")
        declared_snapshot = _resolve_declared_path(gates_doc.get("snapshot_path"), repo_root=repo_root)
        if declared_snapshot is None:
            errors.append("gate results missing snapshot_path")
        elif not _same_file(declared_snapshot, sqlite_path):
            errors.append(
                f"gate results snapshot mismatch: declared={declared_snapshot} expected={sqlite_path}"
            )
        if sqlite_path.is_file() and gates_doc.get("snapshot_sha256") != _sha256(sqlite_path):
            errors.append("gate results snapshot_sha256 does not match current snapshot")

    burndown_doc: dict[str, Any] | None = None
    if not burndown_path.is_file():
        errors.append(f"burndown table missing: {burndown_path}")
    else:
        try:
            burndown_doc = _load_object(burndown_path)
        except (OSError, json.JSONDecodeError, TypeError) as exc:
            errors.append(f"burndown table invalid: {exc}")

    if burndown_doc is not None:
        if not isinstance(burndown_doc.get("summary"), dict):
            errors.append("burndown table missing summary object")
        provenance = burndown_doc.get("provenance")
        if not isinstance(provenance, dict):
            errors.append("burndown table missing provenance object")
        else:
            declared_sqlite = _resolve_declared_path(
                provenance.get("sqlite_source_path"),
                repo_root=repo_root,
            )
            if declared_sqlite is None:
                errors.append("burndown provenance missing sqlite_source_path")
            elif not _same_file(declared_sqlite, sqlite_path):
                errors.append(
                    f"burndown snapshot mismatch: declared={declared_sqlite} expected={sqlite_path}"
                )
            if sqlite_path.is_file() and provenance.get("sqlite_source_sha256") != _sha256(sqlite_path):
                errors.append("burndown provenance sqlite_source_sha256 does not match current snapshot")
    return errors


def _captured_call(call: Callable[[], tuple[int, Path | None]]) -> tuple[int, Path | None, str]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    try:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            rc, path = call()
    except (Exception, SystemExit) as exc:  # guardian: allow-broad-exception -- normalize producer exits
        detail = "\n".join(part for part in (stdout.getvalue(), stderr.getvalue(), repr(exc)) if part).strip()
        return 2, None, detail
    detail = "\n".join(part for part in (stdout.getvalue(), stderr.getvalue()) if part).strip()
    return int(rc), Path(path) if path is not None else None, detail


def _captured_rc_call(call: Callable[[], int]) -> tuple[int, str]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    try:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            rc = int(call())
    except (Exception, SystemExit) as exc:  # guardian: allow-broad-exception -- normalize producer exits
        detail = "\n".join(part for part in (stdout.getvalue(), stderr.getvalue(), repr(exc)) if part).strip()
        return 2, detail
    detail = "\n".join(part for part in (stdout.getvalue(), stderr.getvalue()) if part).strip()
    return rc, detail


def _path_gate(
    *,
    key: str,
    required: bool,
    rc: int,
    path: Path | None,
    diagnostic: str,
) -> OutputGate:
    emitted = path is not None and path.is_file() and path.stat().st_size > 0
    passed = emitted and rc == 0
    return OutputGate(
        key=key,
        required=required,
        status="pass" if passed else "fail",
        producer_exit_code=rc,
        paths=[str(path.resolve())] if emitted and path is not None else [],
        diagnostic=diagnostic,
    )


def _validate_json_object(path: Path) -> str | None:
    try:
        _load_object(path)
    except (OSError, json.JSONDecodeError, TypeError) as exc:
        return f"invalid JSON object {path}: {exc}"
    return None


def _validate_yaml_mapping(path: Path) -> str | None:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise TypeError("YAML document must be a mapping")
    except (OSError, TypeError, ValueError, yaml.YAMLError) as exc:
        return f"invalid YAML mapping {path}: {exc}"
    return None


def _paths_gate(
    *,
    key: str,
    required: bool,
    rc: int,
    paths: list[Path],
    diagnostic: str,
    validators: dict[Path, Callable[[Path], str | None]] | None = None,
) -> OutputGate:
    errors: list[str] = []
    emitted: list[Path] = []
    if not paths:
        errors.append("producer did not return a primary artifact path")
    for path in paths:
        if not path.is_file() or path.stat().st_size <= 0:
            errors.append(f"required format missing or empty: {path}")
            continue
        emitted.append(path.resolve())
        validator = (validators or {}).get(path)
        if validator is not None:
            error = validator(path)
            if error:
                errors.append(error)
    details = "\n".join(part for part in (diagnostic, *errors) if part).strip()
    passed = rc == 0 and len(emitted) == len(paths) and not errors
    return OutputGate(
        key=key,
        required=required,
        status="pass" if passed else "fail",
        producer_exit_code=rc,
        paths=[str(path) for path in emitted],
        diagnostic=details,
    )


def _validate_executive_markdown(path: Path) -> str | None:
    try:
        markdown = path.read_text(encoding="utf-8")
    except OSError as exc:
        return f"executive markdown unreadable: {exc}"
    errors: list[str] = []
    header_count = sum(line.strip().casefold() == "## adg executive brief" for line in markdown.splitlines())
    if header_count != 1:
        errors.append(f"ADG Executive Brief header count={header_count}")
    for marker in ("Impact Inventory", "Decision gate", "Fix now"):
        if marker.casefold() not in markdown.casefold():
            errors.append(f"missing {marker}")
    if "# ADG CI Burndown Report" in markdown:
        errors.append("contains standalone burndown report")
    return "; ".join(errors) if errors else None


def _validate_burndown_markdown(path: Path) -> str | None:
    try:
        markdown = path.read_text(encoding="utf-8")
    except OSError as exc:
        return f"burndown markdown unreadable: {exc}"
    return None if "# ADG CI Burndown Report" in markdown else "burndown markdown header missing"


def _p7_paths(adg_artifacts_dir: Path, run_id: str) -> dict[str, Path | None]:
    def existing(name: str) -> Path | None:
        candidate = adg_artifacts_dir / name
        return candidate if candidate.is_file() else None

    return {
        "structural_outputs": existing(f"adg_structural_outputs_{run_id}.json"),
        "refactor_accelerator": existing(f"adg_refactor_accelerator_{run_id}.json"),
        "graphdb_queries": existing(f"adg_graphdb_queries_{run_id}.json"),
        "runtime_spine": existing(f"adg_runtime_spine_{run_id}.json"),
        "graphdb_projection": existing(f"adg_graphdb_projection_{run_id}.json"),
        "graphdb_metadata": existing(f"adg_graphdb_metadata_{run_id}.json"),
        "graphdb_index": existing(f"adg_graphdb_index_{run_id}.json"),
        "graph_watchlist": existing(f"adg_graph_watchlist_{run_id}.json"),
        "p0_wave_plan": existing(f"issues/p0_remediation_wave_plan_{run_id}.json"),
        "dead_code_report": existing(f"dead_code_zone_control_report_{run_id}.json"),
    }


def _blocked_gates(reason: str) -> list[OutputGate]:
    return [
        OutputGate(key=key, required=required, status="blocked", diagnostic=reason)
        for key, required in (
            ("bcg_gate_adapter", True),
            ("burndown_report", True),
            ("action_queue", True),
            ("review_template", True),
            ("dead_code_report", False),
            ("cleanup_queue", False),
            ("bcg_executive_summary", True),
            ("latest_publication", True),
        )
    ]


def _artifact_inventory(paths: list[Path]) -> list[dict[str, str]]:
    inventory: list[dict[str, str]] = []
    for path in dict.fromkeys(path.resolve() for path in paths):
        if path.is_file() and path.stat().st_size > 0:
            inventory.append({"path": str(path), "sha256": _sha256(path)})
    return inventory


def _publish_required_artifact_set(
    *,
    adg_artifacts_dir: Path,
    run_id: str,
    adapter_path: Path,
    burndown_report_path: Path,
    action_path: Path,
    review_path: Path,
    executive_path: Path,
) -> Path:
    """Commit one immutable, digest-bound report set without mutable mirrors."""
    sources: list[Path] = [
        adapter_path,
        adapter_path.with_suffix(".md"),
        burndown_report_path,
        action_path,
        review_path,
        review_path.with_suffix(".yaml"),
    ]
    for suffix in ("json", "yaml", "md"):
        sources.append(executive_path.with_suffix(f".{suffix}"))

    receipt_path = adg_artifacts_dir / f"adg_output_publication_{run_id}.json"
    rows: list[dict[str, Any]] = []
    with _publication_lock(adg_artifacts_dir):
        _reserve_latest_publication(adg_artifacts_dir, run_id)
        for source in sources:
            if not source.is_file() or source.stat().st_size <= 0:
                raise FileNotFoundError(f"publication source missing or empty: {source}")
            rows.append(
                {
                    "path": str(source.resolve()),
                    "sha256": _sha256(source),
                }
            )
        _atomic_write_text(
            receipt_path,
            json.dumps(
                {
                    "schema_version": "adg-output-publication/v1",
                    "run_id": run_id,
                    "published_at_utc": _utc_now(),
                    "artifacts": rows,
                    "mutable_report_aliases_published": False,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )
    return receipt_path


def _failure_markdown(run_id: str, sqlite_path: Path, gates: list[OutputGate]) -> str:
    lines = [
        "## ADG Executive Brief",
        "",
        f"- **Run:** `{run_id}`",
        "- **Status:** `BLOCKED`",
        f"- **Snapshot:** `{sqlite_path}`",
        "- **Impact Inventory:** unavailable because required output production did not complete",
        "- **Decision gate:** BLOCKED",
        "- **Fix now:** resolve every failed required output gate below, then rerun this snapshot",
        "",
        "| Output gate | Policy | Result |",
        "|---|---|---|",
    ]
    for gate in gates:
        policy = "required" if gate.required else "advisory"
        lines.append(f"| `{gate.key}` | {policy} | {gate.status.upper()} |")
    lines.extend(
        [
            "",
            "Required report output is incomplete. Inspect the timestamped output-bundle manifest for the captured root cause.",
        ]
    )
    return "\n".join(lines) + "\n"


def _write_manifest(
    *,
    manifest_path: Path,
    run_id: str,
    sqlite_path: Path,
    gate_results_path: Path | None,
    enforcement_report_path: Path | None,
    status: str,
    terminal_summary_path: Path | None,
    gates: list[OutputGate],
    artifact_paths: list[Path],
) -> None:
    payload = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "generated_at_utc": _utc_now(),
        "status": status,
        "snapshot_path": str(sqlite_path.resolve()),
        "snapshot_sha256": _sha256(sqlite_path) if sqlite_path.is_file() else None,
        "gate_results_path": str(gate_results_path.resolve()) if gate_results_path is not None else None,
        "gate_results_sha256": (
            _sha256(gate_results_path)
            if gate_results_path is not None and gate_results_path.is_file()
            else None
        ),
        "enforcement_report_path": (
            str(enforcement_report_path.resolve()) if enforcement_report_path is not None else None
        ),
        "enforcement_report_sha256": (
            _sha256(enforcement_report_path)
            if enforcement_report_path is not None and enforcement_report_path.is_file()
            else None
        ),
        "terminal_output_count": 1,
        "terminal_summary_path": str(terminal_summary_path.resolve()) if terminal_summary_path else None,
        "gates": [asdict(gate) for gate in gates],
        "artifacts": _artifact_inventory(artifact_paths),
        "latest_promoted": False,
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    _atomic_write_text(manifest_path, rendered)


def _emit_adg_run_output_bundle_impl(
    *,
    adg_artifacts_dir: Path,
    run_id: str,
    sqlite_path: Path,
    gate_results_path: Path | None,
    burndown_path: Path | None = None,
    enforcement_report_path: Path | None = None,
    certification_gates: list[OutputGate] | None = None,
    print_terminal: bool = True,
    repo_root: Path = REPO_ROOT,
) -> ADGRunOutputBundleResult:
    """Emit and seal one current-run report bundle.

    Required output gates are adapter, burndown, action queue, review template,
    and executive summary.  Dead-code and cleanup reports remain advisory, but
    their failures are explicit in the manifest instead of being silently
    converted to success.
    """
    adg_artifacts_dir = adg_artifacts_dir.resolve()
    repo_root = repo_root.resolve()
    sqlite_path = sqlite_path.resolve()
    burndown_path = (
        burndown_path.resolve()
        if burndown_path is not None
        else adg_artifacts_dir / "adg_burndown_table.json"
    )
    manifest_path = adg_artifacts_dir / f"adg_run_output_bundle_{run_id}.json"
    resolved_gate_results = gate_results_path.resolve() if gate_results_path is not None else None
    resolved_enforcement = enforcement_report_path.resolve() if enforcement_report_path is not None else None

    preflight_errors = (
        ["current-run gate results path is unavailable"]
        if gate_results_path is None
        else _validate_current_run_inputs(
            sqlite_path=sqlite_path,
            gate_results_path=resolved_gate_results,  # type: ignore[arg-type]
            burndown_path=burndown_path,
            repo_root=repo_root,
        )
    )
    if resolved_enforcement is not None and not resolved_enforcement.is_file():
        preflight_errors.append(f"enforcement report missing: {resolved_enforcement}")
    if preflight_errors:
        reason = "; ".join(preflight_errors)
        gates = _blocked_gates(reason)
        terminal_path = adg_artifacts_dir / f"adg_run_terminal_summary_{run_id}.md"
        markdown = _failure_markdown(run_id, sqlite_path, gates)
        _atomic_write_text(terminal_path, markdown)
        _write_manifest(
            manifest_path=manifest_path,
            run_id=run_id,
            sqlite_path=sqlite_path,
            gate_results_path=resolved_gate_results,
            enforcement_report_path=resolved_enforcement,
            status="blocked",
            terminal_summary_path=terminal_path,
            gates=gates,
            artifact_paths=[terminal_path],
        )
        result = ADGRunOutputBundleResult(
            run_id=run_id,
            status="blocked",
            required_exit_code=2,
            manifest_path=manifest_path,
            terminal_summary_path=terminal_path,
            gates=gates,
            artifact_paths=[terminal_path, manifest_path],
        )
        if print_terminal:
            print_adg_run_terminal_summary(result, final_exit_code=2)
        return result

    assert resolved_gate_results is not None
    docs_dir = repo_root / "docs" / "reports" / "adg"
    gates: list[OutputGate] = list(certification_gates or [])
    artifact_paths: list[Path] = [burndown_path]
    for certification_gate in gates:
        artifact_paths.extend(Path(path) for path in certification_gate.paths)

    from tools.reports.adg_bcg_adapter import emit_bcg_gate_adapter

    adapter_rc, adapter_path, detail = _captured_call(
        lambda: emit_bcg_gate_adapter(
            adg_artifacts_dir=adg_artifacts_dir,
            ts=run_id,
            gate_results_path=resolved_gate_results,
            burndown_path=burndown_path,
            docs_dir=docs_dir,
            expected_snapshot_path=sqlite_path,
            print_inline=False,
            fail_closed=True,
            publish_latest=False,
        )
    )
    adapter_paths = [
        adapter_path,
        adapter_path.with_suffix(".md") if adapter_path is not None else None,
    ]
    adapter_gate = _paths_gate(
        key="bcg_gate_adapter",
        required=True,
        rc=adapter_rc,
        paths=[path for path in adapter_paths if path is not None],
        diagnostic=detail,
        validators={adapter_path: _validate_json_object} if adapter_path is not None else None,
    )
    gates.append(adapter_gate)
    if adapter_path is not None:
        artifact_paths.extend([adapter_path, adapter_path.with_suffix(".md")])

    from tools.reports.adg_burndown_report import emit_mandatory_adg_burndown_report

    timestamped_burndown_report = adg_artifacts_dir / f"adg_burndown_report_{run_id}.md"
    burndown_rc, detail = _captured_rc_call(
        lambda: emit_mandatory_adg_burndown_report(
            gate_results=resolved_gate_results,
            burndown=burndown_path,
            fail_closed=True,
            print_inline=False,
            output_paths=(timestamped_burndown_report,),
            emit_canvas=False,
        )
    )
    burndown_outputs = (
        [timestamped_burndown_report]
        if timestamped_burndown_report.is_file() and timestamped_burndown_report.stat().st_size > 0
        else []
    )
    gates.append(
        _paths_gate(
            key="burndown_report",
            required=True,
            rc=burndown_rc,
            paths=[timestamped_burndown_report],
            diagnostic=detail,
            validators={timestamped_burndown_report: _validate_burndown_markdown},
        )
    )
    artifact_paths.extend(burndown_outputs)

    from tools.reports.adg_action_queue import emit_adg_action_queue

    action_output = adg_artifacts_dir / f"adg_action_queue_{run_id}.json"
    action_rc, action_path, detail = _captured_call(
        lambda: emit_adg_action_queue(
            gate_results=resolved_gate_results,
            burndown=burndown_path,
            sqlite_snapshot=sqlite_path,
            output_path=action_output,
            ts=run_id,
            fail_closed=True,
            repo_root=repo_root,
            allow_latest_fallback=False,
            **{
                "p0_wave_plan": _p7_paths(adg_artifacts_dir, run_id)["p0_wave_plan"],
                "refactor_accelerator": _p7_paths(adg_artifacts_dir, run_id)["refactor_accelerator"],
                "structural_outputs": _p7_paths(adg_artifacts_dir, run_id)["structural_outputs"],
                "graphdb_queries": _p7_paths(adg_artifacts_dir, run_id)["graphdb_queries"],
            },
        )
    )
    action_gate = _paths_gate(
        key="action_queue",
        required=True,
        rc=action_rc,
        paths=[action_path] if action_path is not None else [],
        diagnostic=detail,
        validators={action_path: _validate_json_object} if action_path is not None else None,
    )
    gates.append(action_gate)
    if action_path is not None:
        artifact_paths.append(action_path)

    from tools.reports.adg_review_template import emit_mandatory_adg_review_template

    review_rc, review_path, detail = _captured_call(
        lambda: emit_mandatory_adg_review_template(
            adg_artifacts_dir=adg_artifacts_dir,
            ts=run_id,
            gate_results=resolved_gate_results,
            burndown=burndown_path,
            action_queue=action_path,
            generation_manifest=adg_artifacts_dir / f"adg_generation_manifest_{run_id}.json",
            enforcement_report=resolved_enforcement,
            print_inline=False,
            fail_closed=True,
            write_latest=False,
            allow_latest_fallback=False,
        )
    )
    review_paths = [
        review_path,
        review_path.with_suffix(".yaml") if review_path is not None else None,
    ]
    review_gate = _paths_gate(
        key="review_template",
        required=True,
        rc=review_rc,
        paths=[path for path in review_paths if path is not None],
        diagnostic=detail,
        validators={
            path: (_validate_json_object if path.suffix == ".json" else _validate_yaml_mapping)
            for path in review_paths
            if path is not None
        },
    )
    gates.append(review_gate)
    if review_path is not None:
        artifact_paths.extend([review_path, review_path.with_suffix(".yaml")])

    from tools.reports.adg_dead_code_report import emit_mandatory_adg_dead_code_report

    dead_rc, dead_path, detail = _captured_call(
        lambda: emit_mandatory_adg_dead_code_report(
            adg_artifacts_dir=adg_artifacts_dir,
            ts=run_id,
            docs_dir=docs_dir,
            print_inline=False,
            fail_closed=True,
            write_latest=False,
        )
    )
    gates.append(
        _path_gate(
            key="dead_code_report",
            required=False,
            rc=dead_rc,
            path=dead_path,
            diagnostic=detail,
        )
    )
    if dead_path is not None:
        artifact_paths.append(dead_path)

    from tools.reports.adg_cleanup_queue_and_p2_blocker_trace import (
        emit_mandatory_adg_cleanup_queue_and_p2_blocker_trace,
    )

    cleanup_rc, cleanup_path, detail = _captured_call(
        lambda: emit_mandatory_adg_cleanup_queue_and_p2_blocker_trace(
            adg_artifacts_dir=adg_artifacts_dir,
            ts=run_id,
            docs_dir=docs_dir,
            print_inline=False,
            fail_closed=True,
            write_latest=False,
        )
    )
    gates.append(
        _path_gate(
            key="cleanup_queue",
            required=False,
            rc=cleanup_rc,
            path=cleanup_path,
            diagnostic=detail,
        )
    )
    if cleanup_path is not None:
        artifact_paths.extend([cleanup_path, cleanup_path.with_suffix(".md")])

    predecessor_keys = {"bcg_gate_adapter", "burndown_report", "action_queue", "review_template"}
    prerequisites_ok = all(gate.status == "pass" for gate in gates if gate.key in predecessor_keys)
    summary_path: Path | None = None
    if prerequisites_ok:
        from tools.reports.adg_bcg_executive_synthesis import emit_bcg_executive_summary

        summary_rc, summary_path, detail = _captured_call(
            lambda: emit_bcg_executive_summary(
                adg_artifacts_dir=adg_artifacts_dir,
                ts=run_id,
                sqlite_path=sqlite_path,
                gate_results_path=resolved_gate_results,
                action_queue_path=action_path,
                review_template_path=review_path,
                burndown_path=burndown_path,
                p7_paths=_p7_paths(adg_artifacts_dir, run_id),
                print_inline=False,
                fail_closed=True,
                docs_dir=docs_dir,
                burndown_report_path=timestamped_burndown_report,
                write_latest=False,
            )
        )
        summary_paths = [
            summary_path,
            summary_path.with_suffix(".yaml") if summary_path is not None else None,
            summary_path.with_suffix(".md") if summary_path is not None else None,
        ]
        summary_gate = _paths_gate(
            key="bcg_executive_summary",
            required=True,
            rc=summary_rc,
            paths=[path for path in summary_paths if path is not None],
            diagnostic=detail,
            validators={
                path: (
                    _validate_json_object
                    if path.suffix == ".json"
                    else _validate_yaml_mapping
                    if path.suffix == ".yaml"
                    else _validate_executive_markdown
                )
                for path in summary_paths
                if path is not None
            },
        )
        gates.append(summary_gate)
        if summary_path is not None:
            artifact_paths.extend(
                [summary_path, summary_path.with_suffix(".yaml"), summary_path.with_suffix(".md")]
            )
    else:
        gates.append(
            OutputGate(
                key="bcg_executive_summary",
                required=True,
                status="blocked",
                diagnostic="one or more required predecessor outputs failed",
            )
        )

    required_ok = all(gate.status == "pass" for gate in gates if gate.required)
    terminal_path = adg_artifacts_dir / f"adg_run_terminal_summary_{run_id}.md"
    if required_ok and summary_path is not None:
        executive_markdown_path = summary_path.with_suffix(".md")
        try:
            markdown = executive_markdown_path.read_text(encoding="utf-8")
            if not markdown.strip():
                raise ValueError("executive summary markdown is empty")
            _atomic_write_text(terminal_path, markdown)
            artifact_paths.append(terminal_path)
        except (OSError, ValueError) as exc:
            gates[-1].status = "fail"
            gates[-1].diagnostic = f"{gates[-1].diagnostic}\n{exc}".strip()
            required_ok = False
            markdown = _failure_markdown(run_id, sqlite_path, gates)
            _atomic_write_text(terminal_path, markdown)
            artifact_paths.append(terminal_path)
    else:
        markdown = _failure_markdown(run_id, sqlite_path, gates)
        _atomic_write_text(terminal_path, markdown)
        artifact_paths.append(terminal_path)

    publication_path: Path | None = None
    if required_ok and adapter_path is not None and review_path is not None and summary_path is not None:
        try:
            publication_path = _publish_required_artifact_set(
                adg_artifacts_dir=adg_artifacts_dir,
                run_id=run_id,
                adapter_path=adapter_path,
                burndown_report_path=timestamped_burndown_report,
                action_path=action_path,
                review_path=review_path,
                executive_path=summary_path,
            )
            publication_gate = _paths_gate(
                key="latest_publication",
                required=True,
                rc=0,
                paths=[publication_path],
                diagnostic="",
                validators={publication_path: _validate_json_object},
            )
        except (OSError, RuntimeError, TimeoutError, ValueError) as exc:
            publication_gate = OutputGate(
                key="latest_publication",
                required=True,
                status="fail",
                producer_exit_code=2,
                diagnostic=f"latest publication failed: {exc}",
            )
    else:
        publication_gate = OutputGate(
            key="latest_publication",
            required=True,
            status="blocked",
            diagnostic="required output formats did not all pass",
        )
    gates.append(publication_gate)
    if publication_path is not None:
        artifact_paths.append(publication_path)
    required_ok = all(gate.status == "pass" for gate in gates if gate.required)

    status = "complete" if required_ok else "blocked"
    _write_manifest(
        manifest_path=manifest_path,
        run_id=run_id,
        sqlite_path=sqlite_path,
        gate_results_path=resolved_gate_results,
        enforcement_report_path=resolved_enforcement,
        status=status,
        terminal_summary_path=terminal_path,
        gates=gates,
        artifact_paths=artifact_paths,
    )
    artifact_paths.append(manifest_path)
    result = ADGRunOutputBundleResult(
        run_id=run_id,
        status=status,
        required_exit_code=0 if required_ok else 2,
        manifest_path=manifest_path,
        terminal_summary_path=terminal_path,
        gates=gates,
        artifact_paths=list(dict.fromkeys(path for path in artifact_paths if path.is_file())),
    )
    if print_terminal:
        print_adg_run_terminal_summary(
            result,
            final_exit_code=result.required_exit_code,
        )
    return result


def emit_adg_run_output_bundle(
    *,
    adg_artifacts_dir: Path,
    run_id: str,
    sqlite_path: Path,
    gate_results_path: Path | None,
    burndown_path: Path | None = None,
    enforcement_report_path: Path | None = None,
    certification_gates: list[OutputGate] | None = None,
    print_terminal: bool = True,
    repo_root: Path = REPO_ROOT,
) -> ADGRunOutputBundleResult:
    """Fail-closed boundary around all report imports and producers."""
    try:
        return _emit_adg_run_output_bundle_impl(
            adg_artifacts_dir=adg_artifacts_dir,
            run_id=run_id,
            sqlite_path=sqlite_path,
            gate_results_path=gate_results_path,
            burndown_path=burndown_path,
            enforcement_report_path=enforcement_report_path,
            certification_gates=certification_gates,
            print_terminal=print_terminal,
            repo_root=repo_root,
        )
    except (
        Exception,
        SystemExit,
    ) as exc:  # guardian: allow-broad-exception -- terminal boundary always seals
        adg_artifacts_dir = adg_artifacts_dir.resolve()
        sqlite_path = sqlite_path.resolve()
        reason = f"output bundle producer crashed: {type(exc).__name__}: {exc}"
        gates = _blocked_gates(reason)
        terminal_path = adg_artifacts_dir / f"adg_run_terminal_summary_{run_id}.md"
        manifest_path = adg_artifacts_dir / f"adg_run_output_bundle_{run_id}.json"
        markdown = _failure_markdown(run_id, sqlite_path, gates)
        _atomic_write_text(terminal_path, markdown)
        _write_manifest(
            manifest_path=manifest_path,
            run_id=run_id,
            sqlite_path=sqlite_path,
            gate_results_path=gate_results_path.resolve() if gate_results_path is not None else None,
            enforcement_report_path=(
                enforcement_report_path.resolve() if enforcement_report_path is not None else None
            ),
            status="blocked",
            terminal_summary_path=terminal_path,
            gates=gates,
            artifact_paths=[terminal_path],
        )
        result = ADGRunOutputBundleResult(
            run_id=run_id,
            status="blocked",
            required_exit_code=2,
            manifest_path=manifest_path,
            terminal_summary_path=terminal_path,
            gates=gates,
            artifact_paths=[terminal_path, manifest_path],
        )
        if print_terminal:
            print_adg_run_terminal_summary(result, final_exit_code=2)
        return result


def validate_existing_adg_run_output_bundle(
    *,
    adg_artifacts_dir: Path,
    run_id: str,
    sqlite_path: Path,
    enforcement_report_path: Path | None = None,
) -> tuple[bool, str]:
    """Validate a timestamped bundle before a wrapper reuses it."""
    manifest_path = adg_artifacts_dir / f"adg_run_output_bundle_{run_id}.json"
    if not manifest_path.is_file():
        return False, f"output bundle missing: {manifest_path}"
    try:
        payload = _load_object(manifest_path)
        if payload.get("schema_version") != SCHEMA_VERSION:
            return False, "output bundle schema mismatch"
        if payload.get("run_id") != run_id:
            return False, "output bundle run_id mismatch"
        if payload.get("status") != "complete":
            return False, f"output bundle status={payload.get('status')}"
        if payload.get("terminal_output_count") != 1:
            return False, "output bundle terminal_output_count must equal 1"
        if not isinstance(payload.get("final_exit_code"), int):
            return False, "output bundle final_exit_code missing"
        if not isinstance(payload.get("terminal_finalized_at_utc"), str):
            return False, "output bundle terminal finalization timestamp missing"
        declared_snapshot = _resolve_declared_path(payload.get("snapshot_path"), repo_root=REPO_ROOT)
        if declared_snapshot is None or not _same_file(declared_snapshot, sqlite_path.resolve()):
            return False, "output bundle snapshot mismatch"
        if payload.get("snapshot_sha256") != _sha256(sqlite_path):
            return False, "output bundle snapshot digest mismatch"
        declared_gate_results = _resolve_declared_path(payload.get("gate_results_path"), repo_root=REPO_ROOT)
        if declared_gate_results is None or not declared_gate_results.is_file():
            return False, "output bundle gate results missing"
        if payload.get("gate_results_sha256") != _sha256(declared_gate_results):
            return False, "output bundle gate results digest mismatch"
        gate_doc = _load_object(declared_gate_results)
        gate_snapshot = _resolve_declared_path(gate_doc.get("snapshot_path"), repo_root=REPO_ROOT)
        if gate_snapshot is None or not _same_file(gate_snapshot, sqlite_path.resolve()):
            return False, "output bundle gate results snapshot mismatch"
        if gate_doc.get("snapshot_sha256") != _sha256(sqlite_path):
            return False, "output bundle gate results snapshot digest mismatch"
        declared_enforcement = _resolve_declared_path(
            payload.get("enforcement_report_path"), repo_root=REPO_ROOT
        )
        if enforcement_report_path is not None:
            expected_enforcement = enforcement_report_path.resolve()
            if declared_enforcement is None or not _same_file(declared_enforcement, expected_enforcement):
                return False, "output bundle enforcement report mismatch"
        if declared_enforcement is not None:
            if not declared_enforcement.is_file():
                return False, "output bundle enforcement report missing"
            if payload.get("enforcement_report_sha256") != _sha256(declared_enforcement):
                return False, "output bundle enforcement report digest mismatch"
        gates = payload.get("gates")
        if not isinstance(gates, list):
            return False, "output bundle gates missing"
        gate_keys: list[str] = []
        gate_fields = {"key", "required", "status", "producer_exit_code", "paths", "diagnostic"}
        for gate in gates:
            if not isinstance(gate, dict) or set(gate) != gate_fields:
                return False, "output bundle gate row invalid"
            if not isinstance(gate.get("key"), str) or not gate["key"]:
                return False, "output bundle gate key invalid"
            if not isinstance(gate.get("required"), bool):
                return False, f"output bundle gate required flag invalid: {gate['key']}"
            if gate.get("status") not in {"pass", "fail", "blocked"}:
                return False, f"output bundle gate status invalid: {gate['key']}"
            exit_code = gate.get("producer_exit_code")
            if exit_code is not None and (not isinstance(exit_code, int) or isinstance(exit_code, bool)):
                return False, f"output bundle gate producer exit invalid: {gate['key']}"
            if not isinstance(gate.get("paths"), list) or not all(
                isinstance(path, str) and path for path in gate["paths"]
            ):
                return False, f"output bundle gate paths invalid: {gate['key']}"
            if not isinstance(gate.get("diagnostic"), str):
                return False, f"output bundle gate diagnostic invalid: {gate['key']}"
            gate_keys.append(gate["key"])
        if len(gate_keys) != len(set(gate_keys)):
            return False, "output bundle contains duplicate gate keys"
        gate_by_key = {gate["key"]: gate for gate in gates}
        if not REQUIRED_OUTPUT_KEYS.issubset(gate_by_key):
            return False, "output bundle required gate set incomplete"
        required_gate_paths: set[Path] = set()
        expected_path_counts = {
            "bcg_gate_adapter": 2,
            "burndown_report": 1,
            "action_queue": 1,
            "review_template": 2,
            "bcg_executive_summary": 3,
            "latest_publication": 1,
        }
        for key, gate in gate_by_key.items():
            if gate.get("required") is not True:
                continue
            if gate.get("status") != "pass":
                return False, f"output bundle required gate not passed: {key}"
            if gate.get("producer_exit_code") != 0:
                return False, f"output bundle required gate has nonzero producer exit: {key}"
            paths = gate.get("paths")
            if not isinstance(paths, list) or not paths:
                return False, f"output bundle required gate has no artifact path: {key}"
            expected_count = expected_path_counts.get(key)
            if expected_count is not None and len(paths) != expected_count:
                return False, f"output bundle required gate format count mismatch: {key}"
            for raw_path in paths:
                path = _resolve_declared_path(raw_path, repo_root=REPO_ROOT)
                if path is None:
                    return False, f"output bundle required gate path invalid: {key}"
                required_gate_paths.add(path.resolve())
        artifacts = payload.get("artifacts")
        if not isinstance(artifacts, list) or not artifacts:
            return False, "output bundle artifact inventory missing"
        inventory_paths: set[Path] = set()
        for row in artifacts:
            if not isinstance(row, dict):
                return False, "output bundle artifact row invalid"
            path = _resolve_declared_path(row.get("path"), repo_root=REPO_ROOT)
            if path is None or not path.is_file() or path.stat().st_size == 0:
                return False, f"output bundle artifact missing: {row.get('path')}"
            if not path.resolve().is_relative_to(adg_artifacts_dir.resolve()):
                return False, f"output bundle artifact escaped run directory: {path}"
            if row.get("sha256") != _sha256(path):
                return False, f"output bundle artifact digest mismatch: {path}"
            inventory_paths.add(path.resolve())
        if not required_gate_paths.issubset(inventory_paths):
            return False, "output bundle required gate artifact is not digest-inventoried"
        publication_gate = gate_by_key["latest_publication"]
        publication_path = _resolve_declared_path(publication_gate["paths"][0], repo_root=REPO_ROOT)
        if publication_path is None:
            return False, "output bundle publication receipt path invalid"
        publication = _load_object(publication_path)
        if publication.get("schema_version") != "adg-output-publication/v1":
            return False, "output bundle publication receipt schema mismatch"
        if publication.get("run_id") != run_id:
            return False, "output bundle publication receipt run mismatch"
        if publication.get("mutable_report_aliases_published") is not False:
            return False, "output bundle publication unexpectedly used mutable aliases"
        publication_artifacts = publication.get("artifacts")
        if not isinstance(publication_artifacts, list) or not publication_artifacts:
            return False, "output bundle publication artifact set missing"
        published_paths: set[Path] = set()
        for row in publication_artifacts:
            if not isinstance(row, dict) or set(row) != {"path", "sha256"}:
                return False, "output bundle publication artifact row invalid"
            path = _resolve_declared_path(row.get("path"), repo_root=REPO_ROOT)
            if path is None or path.resolve() not in inventory_paths:
                return False, "output bundle publication artifact not inventoried"
            if row.get("sha256") != _sha256(path):
                return False, "output bundle publication artifact digest mismatch"
            published_paths.add(path.resolve())
        expected_published_paths = {
            _resolve_declared_path(raw_path, repo_root=REPO_ROOT).resolve()
            for key in (
                "bcg_gate_adapter",
                "burndown_report",
                "action_queue",
                "review_template",
                "bcg_executive_summary",
            )
            for raw_path in gate_by_key[key]["paths"]
            if _resolve_declared_path(raw_path, repo_root=REPO_ROOT) is not None
        }
        if published_paths != expected_published_paths:
            return False, "output bundle publication artifact set mismatch"
        terminal_path = _resolve_declared_path(payload.get("terminal_summary_path"), repo_root=REPO_ROOT)
        if terminal_path is None or not terminal_path.is_file() or terminal_path.stat().st_size == 0:
            return False, "output bundle terminal summary missing"
        if terminal_path.resolve() not in inventory_paths:
            return False, "output bundle terminal summary is not digest-inventoried"
        terminal_markdown = terminal_path.read_text(encoding="utf-8")
        header_count = sum(
            line.strip().casefold() == "## adg executive brief" for line in terminal_markdown.splitlines()
        )
        if header_count != 1:
            return False, f"output bundle terminal summary header count={header_count}"
        if terminal_markdown.count("## Final disposition") != 1:
            return False, "output bundle terminal summary final disposition count mismatch"
        if "**Process exit code:**" not in terminal_markdown:
            return False, "output bundle terminal summary missing process exit code"
        if "# ADG CI Burndown Report" in terminal_markdown:
            return False, "output bundle terminal summary contains standalone burndown report"
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
        return False, f"output bundle invalid: {exc}"
    return True, "complete current-run bundle"


def load_existing_adg_run_output_bundle(
    *,
    adg_artifacts_dir: Path,
    run_id: str,
    sqlite_path: Path,
) -> ADGRunOutputBundleResult:
    """Load a bundle only after its paths and digests validate."""
    valid, reason = validate_existing_adg_run_output_bundle(
        adg_artifacts_dir=adg_artifacts_dir,
        run_id=run_id,
        sqlite_path=sqlite_path,
    )
    if not valid:
        raise ValueError(reason)
    manifest_path = adg_artifacts_dir / f"adg_run_output_bundle_{run_id}.json"
    payload = _load_object(manifest_path)
    gates = [OutputGate(**row) for row in payload.get("gates", [])]
    artifact_paths = [Path(row["path"]) for row in payload.get("artifacts", [])]
    terminal_raw = payload.get("terminal_summary_path")
    terminal_path = Path(terminal_raw) if isinstance(terminal_raw, str) and terminal_raw else None
    return ADGRunOutputBundleResult(
        run_id=run_id,
        status=str(payload["status"]),
        required_exit_code=0,
        manifest_path=manifest_path,
        terminal_summary_path=terminal_path,
        gates=gates,
        artifact_paths=[*artifact_paths, manifest_path],
    )


def print_adg_run_terminal_summary(
    result: ADGRunOutputBundleResult,
    *,
    final_exit_code: int,
    diagnostics: list[str] | None = None,
    print_terminal: bool = True,
    publish_latest: bool = True,
) -> None:
    """Finalize and optionally print the sole report after all gates finish."""
    if not isinstance(final_exit_code, int) or isinstance(final_exit_code, bool):
        raise TypeError("final_exit_code must be an integer")
    if result.terminal_summary_path is None or not result.terminal_summary_path.is_file():
        markdown = _failure_markdown(result.run_id, Path("snapshot-unavailable"), result.gates)
    else:
        markdown = result.terminal_summary_path.read_text(encoding="utf-8")
    markdown = markdown.split("\n## Final disposition", 1)[0].rstrip()
    lines = [
        markdown,
        "",
        "## Final disposition",
        "",
        f"- **Process exit code:** `{final_exit_code}`",
        f"- **Output bundle:** `{result.status.upper()}`",
    ]
    for diagnostic in diagnostics or []:
        sanitized = " ".join(str(diagnostic).splitlines()).strip()
        sanitized = sanitized.replace("## ADG Executive Brief", "ADG Executive Brief")
        sanitized = sanitized.replace("## Final disposition", "Final disposition")
        if sanitized:
            lines.append(f"- **Diagnostic:** {sanitized[:1000]}")
    finalized = "\n".join(lines).rstrip() + "\n"
    header_count = sum(line.strip().casefold() == "## adg executive brief" for line in finalized.splitlines())
    if header_count != 1 or finalized.count("## Final disposition") != 1:
        raise ValueError("final terminal summary must contain exactly one brief and disposition")
    if "# ADG CI Burndown Report" in finalized:
        raise ValueError("final terminal summary must not contain the standalone burndown report")

    terminal_path = result.terminal_summary_path
    if terminal_path is not None:
        try:
            existing_payload = _load_object(result.manifest_path)
        except (OSError, json.JSONDecodeError, TypeError):
            existing_payload = {}
        if (
            terminal_path.read_text(encoding="utf-8") == finalized
            and existing_payload.get("final_exit_code") == final_exit_code
            and isinstance(existing_payload.get("terminal_finalized_at_utc"), str)
            and (not publish_latest or existing_payload.get("latest_promoted") is True)
        ):
            if print_terminal:
                sys.stdout.write("\n" + finalized)
            return
        _atomic_write_text(terminal_path, finalized)
        try:
            payload = _load_object(result.manifest_path)
            if payload.get("run_id") != result.run_id:
                raise ValueError("output bundle manifest run_id changed before finalization")
            payload["final_exit_code"] = final_exit_code
            payload["terminal_finalized_at_utc"] = _utc_now()
            artifacts = payload.get("artifacts")
            if isinstance(artifacts, list):
                terminal_resolved = terminal_path.resolve()
                terminal_row = next(
                    (
                        row
                        for row in artifacts
                        if isinstance(row, dict)
                        and _resolve_declared_path(row.get("path"), repo_root=REPO_ROOT) == terminal_resolved
                    ),
                    None,
                )
                if terminal_row is None:
                    artifacts.append(
                        {
                            "path": str(terminal_resolved),
                            "sha256": _sha256(terminal_path),
                        }
                    )
                else:
                    terminal_row["sha256"] = _sha256(terminal_path)
            adg_artifacts_dir = result.manifest_path.parent.resolve()
            if not publish_latest:
                payload["latest_promoted"] = False
                rendered_manifest = json.dumps(payload, indent=2, sort_keys=True) + "\n"
                _atomic_write_text(result.manifest_path, rendered_manifest)
            else:
                with _publication_lock(adg_artifacts_dir):
                    owns_latest = _run_owns_latest_reservation(adg_artifacts_dir, result.run_id)
                    if not owns_latest:
                        try:
                            _reserve_latest_publication(adg_artifacts_dir, result.run_id)
                            owns_latest = True
                        except RuntimeError:
                            owns_latest = False
                    payload["latest_promoted"] = owns_latest
                    rendered_manifest = json.dumps(payload, indent=2, sort_keys=True) + "\n"
                    _atomic_write_text(result.manifest_path, rendered_manifest)
                    if owns_latest:
                        _atomic_write_text(
                            result.manifest_path.with_name("adg_run_output_bundle_latest.json"),
                            rendered_manifest,
                        )
        except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
            raise RuntimeError(f"could not finalize output bundle manifest: {exc}") from exc

    if print_terminal:
        sys.stdout.write("\n" + finalized)


__all__ = [
    "ADGRunOutputBundleResult",
    "OutputGate",
    "emit_adg_run_output_bundle",
    "load_existing_adg_run_output_bundle",
    "print_adg_run_terminal_summary",
    "validate_existing_adg_run_output_bundle",
]

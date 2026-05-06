"""P7 (W3) — PreloadedInputContextManifest for apps_rg R4 pipeline.

apps_rg bypasses C0 corpus retrieval.  The JD, master resume, and company
brief are loaded from disk as preloaded inputs.  Since C0 is bypassed, this
manifest IS the deterministic context contract — it records hashes, origin
labels, freshness, lineage, policy_hash, blueprint_hash, replay_key,
manifest_hash, and audit references so the Exit V6 pipeline and downstream
auditors have a single, sealed, hash-verifiable record of every input that
influenced the generated résumé.

Usage
-----
From the R4 entrypoint (or any L2 step that needs the context record)::

    from apps_rg.integrations.preloaded_input_context_manifest import (
        build_preloaded_input_context_manifest,
        PreloadedInputContextManifest,
    )

    manifest = build_preloaded_input_context_manifest(
        jd_path=Path("apps_rg/scripts/_interactive_jd.json"),
        brief_path=Path("apps_rg/scripts/_interactive_brief.json"),
        master_resume_path=Path("apps_shared/data/master_resume.json"),
        run_id=run_id,
        policy_hash=policy_hash,
        blueprint_hash=blueprint_hash,
        replay_key=replay_key,
    )
    manifest.write(artifact_dir)

Plan: apps-rg-canonical-wireup-c8a4f2 W3 P7.
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_SCHEMA_VERSION = "preloaded_input_context_manifest/v1"
_MANIFEST_FILENAME = "preloaded_input_context_manifest.json"


# ---------------------------------------------------------------------------
# Immutable per-file provenance record
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class InputFileRecord:
    """Provenance record for a single preloaded input file."""

    origin_label: str
    path: str
    sha256: str
    size_bytes: int
    loaded_at_utc: str
    exists: bool


# ---------------------------------------------------------------------------
# Top-level manifest
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PreloadedInputContextManifest:
    """Sealed context manifest for an apps_rg R4 run.

    Attributes
    ----------
    schema_version:
        Stable schema identifier for forward-compat checks.
    run_id:
        UUID4 identifying the run; matches R4IntegratedRunResult.run_id.
    manifest_hash:
        SHA-256 of the canonical JSON representation of this manifest
        (excluding manifest_hash itself).  Computed by
        ``_compute_manifest_hash`` after construction.
    replay_key:
        Stable deterministic key computed from input hashes; matches the
        replay_key in R4IntegratedRunResult.
    policy_hash:
        Opaque policy blob hash threaded from the entrypoint caller.
    blueprint_hash:
        Opaque blueprint hash threaded from the entrypoint caller.
    created_at_utc:
        ISO-8601 UTC timestamp of manifest construction.
    c0_bypass_reason:
        Reason code for the C0 bypass receipt (always
        GROUNDING_NOT_REQUIRED for apps_rg).
    inputs:
        Dict of ``origin_label → InputFileRecord`` for each preloaded file.
    audit_refs:
        Free-form dict of provenance cross-references (plan slugs, ADR refs,
        pipeline-component IDs, etc.).
    """

    schema_version: str
    run_id: str
    manifest_hash: str
    replay_key: str
    policy_hash: str
    blueprint_hash: str
    created_at_utc: str
    c0_bypass_reason: str
    inputs: dict[str, InputFileRecord]
    audit_refs: dict[str, str] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serialisable dict."""
        d = asdict(self)
        return d

    def write(self, artifact_dir: Path) -> Path:
        """Write the manifest to *artifact_dir/preloaded_input_context_manifest.json*.

        Creates *artifact_dir* if it does not exist.  Returns the path written.
        """
        artifact_dir = Path(artifact_dir)
        artifact_dir.mkdir(parents=True, exist_ok=True)
        out = artifact_dir / _MANIFEST_FILENAME
        out.write_text(
            json.dumps(self.to_dict(), indent=2, sort_keys=True),
            encoding="utf-8",
        )
        return out


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _sha256_file(path: Path) -> tuple[str, int]:
    """Return (hex-digest, size_bytes) for *path*, or ('', 0) if missing."""
    if not path.exists():
        return ("", 0)
    data = path.read_bytes()
    return (hashlib.sha256(data).hexdigest(), len(data))


def _sha256_str(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _compute_manifest_hash(d: dict[str, Any]) -> str:
    """SHA-256 of the stable JSON representation, manifest_hash excluded."""
    payload = {k: v for k, v in d.items() if k != "manifest_hash"}
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True).encode("utf-8")
    ).hexdigest()


def _utc_iso() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Public builder
# ---------------------------------------------------------------------------

def build_preloaded_input_context_manifest(
    *,
    jd_path: Path,
    brief_path: Path,
    master_resume_path: Path,
    run_id: str,
    replay_key: str = "",
    policy_hash: str = "",
    blueprint_hash: str = "",
    extra_inputs: dict[str, Path] | None = None,
    audit_refs: dict[str, str] | None = None,
) -> PreloadedInputContextManifest:
    """Build and seal a ``PreloadedInputContextManifest`` for a single run.

    Parameters
    ----------
    jd_path:
        Path to the job-description JSON (U0 E4 input).
    brief_path:
        Path to the company-research / company-brief JSON.
    master_resume_path:
        Path to the master résumé JSON (apps_shared/data/master_resume.json).
    run_id:
        UUID4 run identifier (from R4IntegratedRunResult.run_id).
    replay_key:
        Deterministic replay key computed from input hashes.  If empty,
        derived from the three core file hashes.
    policy_hash:
        Opaque policy-blob hash (pass-through from entrypoint caller).
    blueprint_hash:
        Opaque blueprint hash (pass-through from entrypoint caller).
    extra_inputs:
        Optional additional ``{origin_label: Path}`` entries.
    audit_refs:
        Optional cross-reference dict (plan slugs, ADR refs, etc.).

    Returns
    -------
    PreloadedInputContextManifest
        Frozen, hash-verified manifest.  Call ``.write(artifact_dir)`` to
        persist.
    """
    jd_path = Path(jd_path)
    brief_path = Path(brief_path)
    master_resume_path = Path(master_resume_path)

    now = _utc_iso()

    def _record(label: str, p: Path) -> InputFileRecord:
        sha, size = _sha256_file(p)
        return InputFileRecord(
            origin_label=label,
            path=str(p),
            sha256=sha,
            size_bytes=size,
            loaded_at_utc=now,
            exists=p.exists(),
        )

    inputs: dict[str, InputFileRecord] = {
        "jd": _record("jd", jd_path),
        "company_brief": _record("company_brief", brief_path),
        "master_resume": _record("master_resume", master_resume_path),
    }
    if extra_inputs:
        for label, path in extra_inputs.items():
            inputs[label] = _record(label, path)

    if not replay_key:
        replay_key = _sha256_str(
            "|".join(
                inputs[k].sha256
                for k in ("jd", "company_brief", "master_resume")
            )
        )[:16]

    base: dict[str, Any] = {
        "schema_version": _SCHEMA_VERSION,
        "run_id": run_id,
        "manifest_hash": "",
        "replay_key": replay_key,
        "policy_hash": policy_hash,
        "blueprint_hash": blueprint_hash,
        "created_at_utc": now,
        "c0_bypass_reason": "GROUNDING_NOT_REQUIRED",
        "inputs": {k: asdict(v) for k, v in inputs.items()},
        "audit_refs": audit_refs or {
            "plan": "apps-rg-canonical-wireup-c8a4f2",
            "phase": "W3_P7",
            "entrypoint": "integrated_r4_deterministic_pipeline_run",
        },
    }
    manifest_hash = _compute_manifest_hash(base)
    base["manifest_hash"] = manifest_hash

    return PreloadedInputContextManifest(
        schema_version=_SCHEMA_VERSION,
        run_id=run_id,
        manifest_hash=manifest_hash,
        replay_key=replay_key,
        policy_hash=policy_hash,
        blueprint_hash=blueprint_hash,
        created_at_utc=now,
        c0_bypass_reason="GROUNDING_NOT_REQUIRED",
        inputs=inputs,
        audit_refs=audit_refs or {
            "plan": "apps-rg-canonical-wireup-c8a4f2",
            "phase": "W3_P7",
            "entrypoint": "integrated_r4_deterministic_pipeline_run",
        },
    )


__all__ = [
    "InputFileRecord",
    "PreloadedInputContextManifest",
    "build_preloaded_input_context_manifest",
]

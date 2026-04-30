"""Probe — BGE-M3 live operational load (W1 phase 3 blocker #1 closure).

Attempts to load BAAI/bge-m3 via the existing ``bge_runtime`` surface with
``BGE_ALLOW_MODEL_DOWNLOAD=false`` semantics (local-files-only). On success,
performs ONE live embedding to measure dimension end-to-end. On failure,
records remediation plan and emits a status ladder consumed by the model
probe + composer.

Anti-cheat rules honored (user 2026-04-30):
  Rule 2 — no silent fallback PASS. This probe NEVER falls back to MiniLM
           or OpenAI. If BGE-M3 cannot load, we emit a specific BLOCKED
           status, not a downgraded MATCH against a different model.
  Rule 4 — the load process does not mutate cache / does not write UWG.

Environment contract:
  - Reads EMBEDDING_ENABLED, BGE_ALLOW_MODEL_DOWNLOAD from os.environ
  - Does NOT modify env vars
  - Does NOT trigger download (local_files_only enforced via bge_runtime
    default BGE_ALLOW_MODEL_DOWNLOAD=false)
  - Imports ``bge_runtime`` lazily to avoid paying the import cost when
    the probe is not invoked

Output: ``artifacts/certification/bge_m3_operational_proof.json``

Status ladder:
  - OPERATIONAL   -> model loaded + live embed succeeded + dimension matches
  - CACHE_MISSING -> model files absent (remediation: download to HF cache)
  - DEPS_MISSING  -> FlagEmbedding / sentence_transformers / torch missing
  - LOAD_ERROR    -> deps + cache present but load raised unexpected error
  - DISABLED      -> EMBEDDING_ENABLED != 'true'
"""

from __future__ import annotations

import importlib.util
import os
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from tools.certification.evidence import write_evidence, rel  # noqa: E402

EXPECTED_MODEL_HF = "BAAI/bge-m3"
EXPECTED_DIMENSION = 1024
REQUIRED_DEPS = (
    "FlagEmbedding",
    "sentence_transformers",
    "torch",
    "transformers",
    "huggingface_hub",
    "numpy",
)
REMEDIATION_DOWNLOAD_CMD = (
    "huggingface-cli download BAAI/bge-m3  "
    "# or: BGE_ALLOW_MODEL_DOWNLOAD=true python -c "
    "'from agentic_core.embeddings.bge_runtime import bge_embed_query; "
    "bge_embed_query(\"warmup\")'"
)


def _check_deps() -> dict:
    """Return which required deps are importable."""
    status: dict[str, bool] = {}
    for dep in REQUIRED_DEPS:
        try:
            status[dep] = importlib.util.find_spec(dep) is not None
        except ValueError:
            status[dep] = False
    return status


def _hf_cache_probe() -> dict:
    """Locate the HuggingFace hub cache and check for BGE-M3 model folder."""
    candidates = [
        os.environ.get("HF_HOME"),
        os.environ.get("HUGGINGFACE_HUB_CACHE"),
        str(Path.home() / ".cache" / "huggingface" / "hub"),
        str(Path.home() / ".cache" / "huggingface"),
    ]
    hits: list[dict] = []
    for cand in candidates:
        if not cand:
            continue
        p = Path(cand)
        if not p.exists():
            continue
        bge_dirs = [d for d in p.rglob("models--BAAI--bge-m3") if d.is_dir()]
        if bge_dirs:
            hits.append({
                "cache_root": str(p),
                "bge_m3_dirs": [str(d) for d in bge_dirs],
            })
    return {
        "candidates_probed": [c for c in candidates if c],
        "hits": hits,
        "bge_m3_cached": bool(hits),
    }


def _attempt_live_load() -> dict:
    """Attempt to import bge_runtime and perform one live embed.

    Does NOT set BGE_ALLOW_MODEL_DOWNLOAD — honors whatever the env has
    (default: false = local_files_only). Does NOT set EMBEDDING_ENABLED.
    """
    try:
        from agentic_core.embeddings import bge_runtime  # noqa: PLC0415
    except ImportError as exc:
        return {
            "load_attempted": False,
            "load_error": f"IMPORT_FAILED: {type(exc).__name__}: {exc}",
            "dimension_actual": None,
            "device": None,
            "load_ms": None,
        }

    # Perform one live embed to measure end-to-end operation
    try:
        t0 = time.time()
        vec = bge_runtime.bge_embed_query("certification probe warmup")
        elapsed_ms = int((time.time() - t0) * 1000)
    except Exception as exc:  # noqa: BLE001 - probe reports any load error
        return {
            "load_attempted": True,
            "load_error": f"{type(exc).__name__}: {exc}",
            "dimension_actual": None,
            "device": None,
            "load_ms": None,
        }

    dimension = len(vec) if vec else None
    # Resolve the device without re-importing
    try:
        device = bge_runtime._resolve_device()
    except Exception:  # noqa: BLE001
        device = "unknown"

    return {
        "load_attempted": True,
        "load_error": None,
        "dimension_actual": dimension,
        "device": device,
        "load_ms": elapsed_ms,
        "sample_vector_head_3": [float(v) for v in list(vec[:3])] if vec else None,
        "model_slug": bge_runtime.BGE_MODEL,
        "download_allowed_env": bge_runtime.BGE_ALLOW_MODEL_DOWNLOAD,
    }


def _classify(
    embedding_enabled: bool,
    deps_ok: bool,
    cache_present: bool,
    load_result: dict,
) -> tuple[str, str]:
    """Decide status + rationale from gathered evidence."""
    if not embedding_enabled:
        return ("DISABLED",
                "EMBEDDING_ENABLED is not 'true'. Probe did not attempt live load. "
                "Per user Rule 2: identifier parity without live embed is not PASS.")

    if not deps_ok:
        return ("DEPS_MISSING",
                "One or more BGE-M3 runtime deps are not importable. "
                "Remediation: pip install FlagEmbedding sentence-transformers torch transformers huggingface_hub numpy")

    if not cache_present and (load_result.get("load_error") or "").startswith(("OSError", "FileNotFoundError")):
        return ("CACHE_MISSING",
                f"BGE-M3 model files not found in HuggingFace cache. "
                f"Remediation: {REMEDIATION_DOWNLOAD_CMD}")

    if load_result.get("load_error"):
        return ("LOAD_ERROR",
                f"BGE-M3 load raised an unexpected error: {load_result['load_error']}. "
                f"Remediation: inspect bge_runtime._get_model() and check "
                f"BGE_ALLOW_MODEL_DOWNLOAD / HF_HOME env state.")

    if load_result.get("dimension_actual") != EXPECTED_DIMENSION:
        return ("LOAD_ERROR",
                f"BGE-M3 loaded but produced dimension "
                f"{load_result.get('dimension_actual')} != expected "
                f"{EXPECTED_DIMENSION}. Model or config corruption suspected.")

    return ("OPERATIONAL",
            f"BGE-M3 loaded from HF cache; live embed produced "
            f"{EXPECTED_DIMENSION}-dim vector in {load_result.get('load_ms')}ms; "
            f"device={load_result.get('device')}; fallback_used=false.")


def main() -> int:
    embedding_enabled = os.environ.get("EMBEDDING_ENABLED", "").lower() == "true"
    bge_download_allowed = os.environ.get("BGE_ALLOW_MODEL_DOWNLOAD", "").lower() == "true"
    dep_status = _check_deps()
    deps_ok = all(dep_status.values())
    cache_info = _hf_cache_probe()

    if embedding_enabled and deps_ok:
        load_result = _attempt_live_load()
    else:
        load_result = {
            "load_attempted": False,
            "load_error": "precondition_not_met",
            "dimension_actual": None,
            "device": None,
            "load_ms": None,
        }

    status, rationale = _classify(embedding_enabled, deps_ok, cache_info["bge_m3_cached"], load_result)

    payload = {
        "probe": "bge_m3_operational",
        "phase": "W1p3",
        "blocker": "1_approved_model_proof_live_load",
        "subclaim_target": "R1B_APPROVED_MODEL_PROOF",
        "expected": {
            "model_hf_id": EXPECTED_MODEL_HF,
            "dimension": EXPECTED_DIMENSION,
            "fallback_used": False,
        },
        "actual": {
            "embedding_enabled_env": embedding_enabled,
            "bge_allow_download_env": bge_download_allowed,
            "deps_status": dep_status,
            "deps_ok": deps_ok,
            "cache_info": cache_info,
            "load_result": load_result,
            "fallback_used": False,  # this probe never falls back — that's Rule 2
        },
        "status": status,
        "rationale": rationale,
        "remediation_plan": (
            REMEDIATION_DOWNLOAD_CMD if status in ("CACHE_MISSING", "DEPS_MISSING")
            else ("set EMBEDDING_ENABLED=true before invoking the probe"
                  if status == "DISABLED" else None)
        ),
        "anti_cheat_rules_honored": {
            "rule_2_no_silent_fallback_pass": True,
            "probe_never_sets_env_vars": True,
            "probe_never_downloads_model": not bge_download_allowed,
            "probe_did_not_write_sidecar": True,
        },
    }

    path = write_evidence("bge_m3_operational_proof.json", payload)
    print(f"[probe_bge_m3_op] status={status}")
    print(f"[probe_bge_m3_op] embedding_enabled={embedding_enabled} deps_ok={deps_ok} cache_present={cache_info['bge_m3_cached']}")
    if status == "OPERATIONAL":
        print(f"[probe_bge_m3_op] dimension={load_result['dimension_actual']} device={load_result['device']} load_ms={load_result['load_ms']}")
    print(f"[probe_bge_m3_op] wrote: {rel(path)}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"[probe_bge_m3_op] HARNESS_ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(3)

"""W1 Phase 5 — Wave A.2: Local cross-encoder availability probe.

This probe inspects the local environment to determine whether a cross-encoder
model is available for use as the primary safety veto (Option B). It does NOT
download models — only checks whether they're already cached and whether
sufficient VRAM is available for inference.

Output: artifacts/certification/cross_encoder_availability_report.json
"""

from __future__ import annotations

from agentic_core.config.model_catalog import (
    BGE_RERANKER_MODEL_ID,
)

import json
import os
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
ARTIFACT_DIR = REPO_ROOT / "artifacts" / "certification"
ARTIFACT_PATH = ARTIFACT_DIR / "cross_encoder_availability_report.json"

# Models we support as primary veto candidates
SUPPORTED_MODELS = {
    BGE_RERANKER_MODEL_ID: {
        "params": "568M",
        "disk_gb": 1.4,
        "vram_gb_min": 2.0,
        "vram_gb_recommended": 4.0,
        "latency_ms_est": 50,
    },
    "cross-encoder/ms-marco-MiniLM-L-12-v2": {
        "params": "33M",
        "disk_gb": 0.13,
        "vram_gb_min": 1.0,
        "vram_gb_recommended": 2.0,
        "latency_ms_est": 30,
    },
}

# HuggingFace cache directory (where models would be if cached)
HF_CACHE_DIR = Path.home() / ".cache" / "huggingface" / "hub"


def _get_gpu_info() -> dict[str, Any]:
    """Probe CUDA availability and GPU memory."""
    info = {
        "cuda_available": False,
        "cuda_version": None,
        "gpu_count": 0,
        "gpu_names": [],
        "vram_total_gb": 0.0,
        "vram_free_gb": 0.0,
    }
    try:
        import torch
        info["cuda_available"] = torch.cuda.is_available()
        if info["cuda_available"]:
            info["cuda_version"] = torch.version.cuda
            info["gpu_count"] = torch.cuda.device_count()
            for i in range(info["gpu_count"]):
                props = torch.cuda.get_device_properties(i)
                info["gpu_names"].append(props.name)
                # VRAM in bytes -> GB
                total_gb = props.total_memory / (1024 ** 3)
                info["vram_total_gb"] += total_gb
            # Free memory (approximate — may include cached allocations)
            free_bytes = torch.cuda.mem_get_info()[0] if hasattr(torch.cuda, "mem_get_info") else 0
            info["vram_free_gb"] = free_bytes / (1024 ** 3)
    except Exception:
        pass
    return info


def _check_model_cached(model_id: str) -> dict[str, Any]:
    """Check if model weights exist in HuggingFace cache."""
    result = {
        "model_id": model_id,
        "cached": False,
        "cache_path": None,
        "cache_size_gb": 0.0,
    }
    # HF cache organizes as: models--<org>--<repo>/snapshots/<hash>/
    safe_name = model_id.replace("/", "--")
    model_cache_dir = HF_CACHE_DIR / f"models--{safe_name}"
    
    if not model_cache_dir.exists():
        return result
    
    # Check for snapshots directory (indicates actual download, not just metadata)
    snapshots_dir = model_cache_dir / "snapshots"
    if snapshots_dir.exists() and any(snapshots_dir.iterdir()):
        result["cached"] = True
        result["cache_path"] = str(model_cache_dir.relative_to(Path.home()))
        # Estimate size (rough)
        try:
            total_size = sum(f.stat().st_size for f in model_cache_dir.rglob("*") if f.is_file())
            result["cache_size_gb"] = round(total_size / (1024 ** 3), 2)
        except Exception:
            pass
    
    return result


def _check_sentence_transformers() -> dict[str, Any]:
    """Check if sentence-transformers library is available (common CE loader)."""
    result = {
        "available": False,
        "version": None,
    }
    try:
        import sentence_transformers as st
        result["available"] = True
        result["version"] = st.__version__
    except Exception:
        pass
    return result


def _check_transformers() -> dict[str, Any]:
    """Check if transformers library is available (alternative CE loader)."""
    result = {
        "available": False,
        "version": None,
    }
    try:
        import transformers as trf
        result["available"] = True
        result["version"] = trf.__version__
    except Exception:
        pass
    return result


def _compute_recommendation(
    gpu_info: dict[str, Any],
    model_checks: list[dict[str, Any]],
    st_info: dict[str, Any],
    trf_info: dict[str, Any],
) -> dict[str, Any]:
    """Compute the final recommendation based on probe results."""
    
    # Can we run ANY cross-encoder?
    can_run_ce = gpu_info["cuda_available"] and gpu_info["vram_total_gb"] >= 1.0
    
    # Is any supported model cached?
    cached_models = [m for m in model_checks if m["cached"]]
    has_cached_model = len(cached_models) > 0
    
    # Do we have the libraries?
    has_loader = st_info["available"] or trf_info["available"]
    
    # Determine recommendation
    if not can_run_ce:
        return {
            "primary_veto_path": "C_PRIMARY",
            "reason": "No CUDA GPU available or insufficient VRAM for cross-encoder inference",
            "fallback": "LLM-judge veto (Option C) via local Qwen or hosted endpoint",
            "confidence": "high",
        }
    
    if not has_cached_model:
        return {
            "primary_veto_path": "C_PRIMARY",
            "reason": f"GPU available ({gpu_info['vram_total_gb']:.1f} GB) but no supported cross-encoder cached locally",
            "fallback": "Option C (LLM-judge) or download CE first (adds ~1.4 GB disk, W1p5 Wave C-B optional)",
            "confidence": "high",
            "note": "To enable Option B, run: python -c \"from sentence_transformers import CrossEncoder; CrossEncoder(BGE_RERANKER_MODEL_ID)\"",
        }
    
    if not has_loader:
        return {
            "primary_veto_path": "C_PRIMARY",
            "reason": "Cross-encoder cached but no loader library (sentence-transformers or transformers) available",
            "fallback": "Install: pip install sentence-transformers",
            "confidence": "high",
        }
    
    # We have GPU + cached model + loader — recommend B-primary
    best_model = cached_models[0]  # Prefer first in SUPPORTED_MODELS order
    model_spec = SUPPORTED_MODELS.get(best_model["model_id"], {})
    
    vram_sufficient = gpu_info["vram_total_gb"] >= model_spec.get("vram_gb_min", 2.0)
    
    if vram_sufficient:
        return {
            "primary_veto_path": "B_PRIMARY",
            "reason": f"GPU sufficient ({gpu_info['vram_total_gb']:.1f} GB), {best_model['model_id']} cached ({best_model['cache_size_gb']:.2f} GB), loader available",
            "recommended_model": best_model["model_id"],
            "expected_latency_ms": model_spec.get("latency_ms_est", 50),
            "vram_headroom_gb": round(gpu_info["vram_total_gb"] - model_spec.get("vram_gb_min", 2.0), 1),
            "confidence": "high",
        }
    else:
        return {
            "primary_veto_path": "C_PRIMARY",
            "reason": f"GPU VRAM ({gpu_info['vram_total_gb']:.1f} GB) below minimum for {best_model['model_id']} ({model_spec.get('vram_gb_min', 2.0)} GB)",
            "fallback": "Option C (LLM-judge) or smaller CE (ms-marco-MiniLM-L-12-v2, 1 GB VRAM min)",
            "confidence": "high",
        }


def main() -> int:
    """Run the probe and emit the availability report."""
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Gather evidence
    gpu_info = _get_gpu_info()
    model_checks = [_check_model_cached(m) for m in SUPPORTED_MODELS.keys()]
    st_info = _check_sentence_transformers()
    trf_info = _check_transformers()
    recommendation = _compute_recommendation(gpu_info, model_checks, st_info, trf_info)
    
    # Build payload
    payload = {
        "probe": "cross_encoder_availability",
        "phase": "W1p5",
        "timestamp": None,  # ISO format added below
        "gpu_info": gpu_info,
        "model_cache_status": {m["model_id"]: m for m in model_checks},
        "loader_libraries": {
            "sentence_transformers": st_info,
            "transformers": trf_info,
        },
        "recommendation": recommendation,
        "anti_cheat_invariants": {
            "probe_did_not_download_models": True,
            "probe_did_not_modify_cache": True,
            "probe_read_only_inspection": True,
        },
    }
    
    # Add timestamp
    from datetime import datetime, timezone
    payload["timestamp"] = datetime.now(timezone.utc).isoformat()
    
    # Write artifact
    ARTIFACT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    
    # Console summary
    print(f"[probe_ce_availability] recommendation={recommendation['primary_veto_path']}")
    print(f"[probe_ce_availability] reason={recommendation['reason'][:80]}...")
    print(f"[probe_ce_availability] wrote: {ARTIFACT_PATH.relative_to(REPO_ROOT)}")
    
    # Exit code: 0 for success (probe completed), 2 for advisory if no CE available
    if recommendation["primary_veto_path"] == "C_PRIMARY":
        print("[probe_ce_availability] advisory: cross-encoder not available locally")
        return 2  # Advisory exit — CE not available, but probe succeeded
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

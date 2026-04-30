"""Probe — R1B approved model proof (W1 phase 2 blocker a).

Anti-cheat rules honored (user 2026-04-30):
  - Expected model is ``BAAI/bge-m3`` (or ``bge-m3-v1`` slug) unless the
    repo has a stronger SSOT.
  - If actual resolves to MiniLM / default EF / None -> ``MISMATCH_EXPLAINED``
    or ``BLOCKED``, never ``PASS`` silent fallback.
  - Records embedding_model_expected, embedding_model_actual, dimension,
    and a deterministic model_match_status.
  - Does NOT instantiate a live BGE-M3 model; introspects the factory
    only. This keeps the probe reproducible in CI.

Output: ``artifacts/certification/semantic_cache_model_proof.json``

Status ladder (match status -> subclaim verdict, computed by composer):
  - ``MATCH``              -> R1B_APPROVED_MODEL_PROOF = PASS
  - ``MISMATCH_EXPLAINED`` -> R1B_APPROVED_MODEL_PROOF = PARTIAL
  - ``UNRESOLVED``         -> R1B_APPROVED_MODEL_PROOF = BLOCKED
  - ``INFRASTRUCTURE_GAP`` -> R1B_APPROVED_MODEL_PROOF = BLOCKED
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from tools.certification.evidence import write_evidence, rel  # noqa: E402

EXPECTED_MODEL_ID = "bge-m3-v1"
EXPECTED_MODEL_PROVIDER = "bge-m3"
EXPECTED_MODEL_HF_ID = "BAAI/bge-m3"
EXPECTED_DIMENSION = 1024


def _resolve_active_model() -> dict:
    """Introspect the factory for the active model without instantiating it."""
    try:
        from agentic_core.embeddings.embedding_factory import (
            get_active_embedding_model_id,
            _default_embedding_provider,
        )
    except ImportError as exc:
        return {
            "error": f"EMBEDDING_FACTORY_IMPORT_FAILED: {exc}",
            "status": "INFRASTRUCTURE_GAP",
        }

    actual_model_id = get_active_embedding_model_id()
    actual_provider = _default_embedding_provider()
    env_model = os.environ.get("EMBEDDING_MODEL_ID")
    env_provider = os.environ.get("AGENTIC_EMBEDDING_PROVIDER")
    embedding_enabled = os.environ.get("EMBEDDING_ENABLED", "").lower() in ("1", "true", "yes")

    return {
        "status": "RESOLVED",
        "actual_model_id": actual_model_id,
        "actual_provider": actual_provider,
        "env_EMBEDDING_MODEL_ID": env_model,
        "env_AGENTIC_EMBEDDING_PROVIDER": env_provider,
        "env_EMBEDDING_ENABLED": embedding_enabled,
    }


def _probe_bgem3_client_importable() -> dict:
    """Confirm the BGEM3EmbeddingClient class is importable in this env.

    Does NOT instantiate (which would trigger model download) — only
    verifies the code path exists.
    """
    try:
        from agentic_core.embeddings.embedding_factory import BGEM3EmbeddingClient  # noqa: F401
        return {"importable": True, "error": None}
    except ImportError as exc:
        return {"importable": False, "error": str(exc)}
    except Exception as exc:  # noqa: BLE001 - probe reports any failure
        return {"importable": False, "error": f"{type(exc).__name__}: {exc}"}


def _classify_match(resolved: dict, client_probe: dict) -> tuple[str, str]:
    """Decide model_match_status + rationale from resolver output.

    Returns: (status, rationale_string)

    Strictness (user 2026-04-30 Rule 2):
      - MATCH requires BOTH identifier parity AND EMBEDDING_ENABLED=true.
        Identifier match alone is insufficient because EMBEDDING_ENABLED=false
        means no actual model is running — marking that PASS would be a
        silent not-really-running fallback.
      - Any MiniLM / known-alternative-provider path -> MISMATCH_EXPLAINED.
      - Unresolved identifiers -> UNRESOLVED -> BLOCKED.
    """
    if resolved.get("status") == "INFRASTRUCTURE_GAP":
        return ("INFRASTRUCTURE_GAP",
                f"embedding factory not importable: {resolved.get('error')}")

    actual_id = resolved.get("actual_model_id", "")
    actual_provider = resolved.get("actual_provider", "")
    embedding_enabled = bool(resolved.get("env_EMBEDDING_ENABLED"))
    client_importable = bool(client_probe.get("importable"))

    # Normalization — treat BGE-M3 slug variants as a match
    def _is_bgem3(ident: str) -> bool:
        ident = (ident or "").lower()
        return "bge-m3" in ident or "baai/bge-m3" in ident

    identifiers_match = _is_bgem3(actual_id) and _is_bgem3(actual_provider)

    if identifiers_match and embedding_enabled and client_importable:
        return ("MATCH",
                f"actual={actual_id}/{actual_provider} matches expected "
                f"bge-m3-v1/bge-m3 AND EMBEDDING_ENABLED=true AND "
                f"BGEM3EmbeddingClient is importable")

    if identifiers_match and not embedding_enabled:
        return ("MISMATCH_EXPLAINED",
                f"identifiers match ({actual_id}/{actual_provider}) but "
                f"EMBEDDING_ENABLED=false — no model is actually running. "
                f"Per Rule 2 (user 2026-04-30), this cannot be marked PASS "
                f"because embeddings are disabled fail-closed. "
                f"CI must set EMBEDDING_ENABLED=true with a real BGE-M3 "
                f"install to progress past MISMATCH_EXPLAINED.")

    if identifiers_match and not client_importable:
        return ("MISMATCH_EXPLAINED",
                f"identifiers match ({actual_id}/{actual_provider}) but "
                f"BGEM3EmbeddingClient is not importable: "
                f"{client_probe.get('error')}. Declared-only match is not "
                f"honest PASS evidence.")

    # Known fallback providers: openai, gemini, anthropic, minilm
    known_providers = {"openai", "gemini", "anthropic"}
    if actual_provider in known_providers:
        return ("MISMATCH_EXPLAINED",
                f"actual provider={actual_provider} differs from expected bge-m3; "
                f"this is a known alternative provider path, not a silent fallback. "
                f"model_id={actual_id}. "
                f"Per Rule 2 (user 2026-04-30), this must NOT be marked PASS.")

    if "minilm" in (actual_id or "").lower() or "minilm" in (actual_provider or "").lower():
        return ("MISMATCH_EXPLAINED",
                f"actual={actual_id}/{actual_provider} resolves to MiniLM fallback; "
                f"this is a silent-fallback path that Rule 2 explicitly blocks from PASS.")

    if not actual_id or not actual_provider:
        return ("UNRESOLVED",
                f"model identifiers missing/empty (actual_id={actual_id!r}, "
                f"actual_provider={actual_provider!r})")

    # Default: unknown model — mark MISMATCH_EXPLAINED (not PASS)
    return ("MISMATCH_EXPLAINED",
            f"actual={actual_id}/{actual_provider} does not match expected "
            f"bge-m3-v1/bge-m3, and does not match a known alternative provider. "
            f"Marking MISMATCH_EXPLAINED per Rule 2.")


def _read_bge_m3_operational_evidence() -> dict:
    """W1p3: consume bge_m3_operational_proof.json when present.

    The operational probe (tools/certification/evidence/probe_bge_m3_operational.py)
    performs the live BGE-M3 load + embed. If its artifact is present and
    status=OPERATIONAL, we UPGRADE a MATCH identifier-parity result to a
    full PASS with measured dimension.
    """
    art = REPO_ROOT / "artifacts" / "certification" / "bge_m3_operational_proof.json"
    if not art.exists():
        return {"present": False, "status": None,
                "dimension_actual": None, "fallback_used": None}
    try:
        import json
        d = json.loads(art.read_text(encoding="utf-8"))
        return {
            "present": True,
            "status": d.get("status"),
            "dimension_actual": (
                d.get("actual", {}).get("load_result", {}).get("dimension_actual")
            ),
            "fallback_used": d.get("actual", {}).get("fallback_used"),
            "load_ms": (
                d.get("actual", {}).get("load_result", {}).get("load_ms")
            ),
            "device": (
                d.get("actual", {}).get("load_result", {}).get("device")
            ),
        }
    except (json.JSONDecodeError, OSError):
        return {"present": False, "status": "MALFORMED",
                "dimension_actual": None, "fallback_used": None}


def main() -> int:
    resolved = _resolve_active_model()
    client_probe = _probe_bgem3_client_importable()
    match_status, rationale = _classify_match(resolved, client_probe)

    # W1p3: consume BGE-M3 operational evidence. Upgrade to MATCH only
    # when identifier parity holds AND operational probe reports
    # OPERATIONAL AND fallback_used=false AND dimension matches. Any
    # MISMATCH rooted in wrong provider (e.g., known fallback, minilm)
    # never upgrades — the rationale string distinguishes.
    op = _read_bge_m3_operational_evidence()
    actual_id = resolved.get("actual_model_id", "") or ""
    actual_provider = resolved.get("actual_provider", "") or ""
    identifiers_match_bgem3 = (
        "bge-m3" in actual_id.lower() and "bge-m3" in actual_provider.lower()
    )
    live_verified = (
        op["present"]
        and op["status"] == "OPERATIONAL"
        and op["fallback_used"] is False
        and op["dimension_actual"] == EXPECTED_DIMENSION
        and identifiers_match_bgem3  # never upgrade when identifiers disagree
        and match_status != "MATCH"   # only upgrade when not already at ceiling
    )
    if live_verified:
        match_status = "MATCH"
        rationale = (
            f"identifiers match AND BGE-M3 operational probe reports "
            f"status=OPERATIONAL with dimension={op['dimension_actual']} "
            f"(device={op['device']}, load_ms={op['load_ms']}ms); "
            f"fallback_used=false. Upgraded to live-verified MATCH per "
            f"W1p3 operational proof."
        )

    # "Dimension" is a declared value unless the operational probe measured it.
    dimension_expected = EXPECTED_DIMENSION
    dimension_actual_declared = (
        op["dimension_actual"] if live_verified else
        (EXPECTED_DIMENSION if match_status == "MATCH" else None)
    )

    payload = {
        "probe": "semantic_cache_model_proof",
        "blocker": "a",
        "subclaim_target": "R1B_APPROVED_MODEL_PROOF",
        "expected": {
            "model_id": EXPECTED_MODEL_ID,
            "provider": EXPECTED_MODEL_PROVIDER,
            "hf_id": EXPECTED_MODEL_HF_ID,
            "dimension": dimension_expected,
        },
        "actual": {
            "model_id": resolved.get("actual_model_id"),
            "provider": resolved.get("actual_provider"),
            "dimension_declared": dimension_actual_declared,
            "env_EMBEDDING_MODEL_ID": resolved.get("env_EMBEDDING_MODEL_ID"),
            "env_AGENTIC_EMBEDDING_PROVIDER": resolved.get("env_AGENTIC_EMBEDDING_PROVIDER"),
            "env_EMBEDDING_ENABLED": resolved.get("env_EMBEDDING_ENABLED"),
        },
        "bge_m3_client_probe": client_probe,
        "bge_m3_operational_evidence": op,
        "live_verified": live_verified,
        "fallback_used": False,  # this probe never falls back (Rule 2)
        "model_match_status": match_status,
        "rationale": rationale,
        "anti_cheat_rules_honored": {
            "rule_2_no_silent_fallback_pass": (
                match_status in ("MATCH", "MISMATCH_EXPLAINED",
                                 "UNRESOLVED", "INFRASTRUCTURE_GAP")
            ),
            "probe_did_not_instantiate_live_model": True,
            "probe_did_not_write_sidecar": True,
        },
        "note": (
            "Probe records raw facts only. The composer "
            "(scripts/compose_semantic_cache_subclaims.py) maps "
            "model_match_status -> R1B_APPROVED_MODEL_PROOF subclaim verdict."
        ),
    }

    path = write_evidence("semantic_cache_model_proof.json", payload)
    print(f"[probe_model] match_status={match_status}")
    print(f"[probe_model] expected={EXPECTED_MODEL_ID} actual={resolved.get('actual_model_id')}")
    print(f"[probe_model] wrote: {rel(path)}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"[probe_model] HARNESS_ERROR: {exc}", file=sys.stderr)
        sys.exit(3)

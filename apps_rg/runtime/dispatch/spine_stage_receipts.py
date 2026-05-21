"""Stage receipt filenames for apps_rg whole-run spine (R3R4 + draft leg)."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

STAGE_RECEIPT_SCHEMA_VERSION = "apps_rg.stage_receipt.v1"

FILENAME_INGRESS_RAW = "ingress_raw.json"
FILENAME_U0_RECEIPT = "u0_receipt.json"
FILENAME_L1_PLAN = "l1_plan_contract.json"
FILENAME_ROUTE_CONTRACT = "route_contract.json"
FILENAME_ROUTE_PRE_RESEARCH = "route_contract_pre_research.json"
FILENAME_RESEARCH_BRIDGE_REQUEST = "research_bridge_request.json"
FILENAME_RESEARCH_BRIDGE_RESPONSE = "research_bridge_response.json"
FILENAME_RESEARCH_EVIDENCE_CONTRACT = "research_final_evidence_contract.json"
FILENAME_DELEGATED_BRIEFING = "research/delegated_briefing.txt"
FILENAME_SPINE_MANIFEST = "spine_run_manifest.json"
FILENAME_MOCK_ELIMINATION_PROOF = "mock_elimination_proof.json"
FILENAME_DRAFT_LEG_MANIFEST = "r4_run_manifest.json"


def _canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def sha256_digest(payload: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def write_stage_receipt(path: Path, payload: Mapping[str, Any]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(payload), indent=2, sort_keys=True, default=str), encoding="utf-8")
    return str(path)


__all__ = [
    "FILENAME_DELEGATED_BRIEFING",
    "FILENAME_DRAFT_LEG_MANIFEST",
    "FILENAME_INGRESS_RAW",
    "FILENAME_L1_PLAN",
    "FILENAME_MOCK_ELIMINATION_PROOF",
    "FILENAME_RESEARCH_BRIDGE_REQUEST",
    "FILENAME_RESEARCH_BRIDGE_RESPONSE",
    "FILENAME_RESEARCH_EVIDENCE_CONTRACT",
    "FILENAME_ROUTE_CONTRACT",
    "FILENAME_ROUTE_PRE_RESEARCH",
    "FILENAME_SPINE_MANIFEST",
    "FILENAME_U0_RECEIPT",
    "STAGE_RECEIPT_SCHEMA_VERSION",
    "sha256_digest",
    "write_stage_receipt",
]

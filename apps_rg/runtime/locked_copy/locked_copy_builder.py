"""Build deterministic locked-copy proof artifacts (no LLM / provider)."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apps_rg.runtime.locked_copy.locked_copy_manifest import (
    LOCKED_SECTION_IDS,
    build_manifest,
    find_repo_root,
    load_base_resume,
)
from apps_rg.runtime.locked_copy.locked_copy_x2 import run_locked_copy_x2_gates, write_x2_gate_outputs

ARTIFACT_REL = Path("artifacts/apps_rg/runtime_proofs/locked_copy")


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def build_locked_copy(repo: Path | None = None) -> dict[str, Any]:
    root = repo or find_repo_root()
    artifact_dir = root / ARTIFACT_REL
    artifact_dir.mkdir(parents=True, exist_ok=True)

    base, base_path, base_hash = load_base_resume(root)
    manifest = build_manifest(base, base_path, base_hash)
    manifest_path = artifact_dir / "locked_copy_manifest.json"
    write_json(manifest_path, manifest)

    gates = run_locked_copy_x2_gates(manifest=manifest, artifact_dir=artifact_dir, repo_root=root)
    x2_payload = write_x2_gate_outputs(artifact_dir / "locked_copy_x2_gate_outputs.json", gates)

    receipt = {
        "receipt_id": f"locked_copy_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "artifact_dir": str(artifact_dir.relative_to(root)).replace("\\", "/"),
        "manifest_path": str(manifest_path.relative_to(root)).replace("\\", "/"),
        "x2_gate_outputs_path": str(
            (artifact_dir / "locked_copy_x2_gate_outputs.json").relative_to(root)
        ).replace("\\", "/"),
        "locked_section_ids": list(LOCKED_SECTION_IDS),
        "section_count": len(manifest.get("sections") or []),
        "llm_generated": False,
        "rewrite_allowed": False,
        "provider_calls_made": False,
        "qwen_calls_made": False,
        "x2_passed": x2_payload["x2_passed"],
        "x2_failed": x2_payload["x2_failed"],
        "x2_failed_gate_ids": x2_payload["failed_gates"],
        "all_x2_passed": x2_payload["x2_failed"] == 0,
    }
    write_json(artifact_dir / "locked_copy_receipt.json", receipt)

    return {
        "manifest": manifest,
        "x2": x2_payload,
        "receipt": receipt,
        "artifact_dir": artifact_dir,
    }


def main(argv: list[str] | None = None) -> int:
    _ = argv if argv is not None else sys.argv[1:]
    result = build_locked_copy()
    receipt = result["receipt"]
    print(f"Wrote {receipt['manifest_path']}")
    print(f"Wrote {receipt['x2_gate_outputs_path']}")
    print(f"Wrote {receipt['artifact_dir']}/locked_copy_receipt.json")
    print(f"LOCKED_COPY_X2: {receipt['x2_passed']}/{receipt['x2_failed']}/{receipt['x2_passed'] + receipt['x2_failed']}")
    if receipt["x2_failed"]:
        print(f"FAILED_GATES: {', '.join(receipt['x2_failed_gate_ids'])}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

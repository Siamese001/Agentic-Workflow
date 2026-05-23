"""Compile-time proof: executive_summary E0 hydrates YAML gold (no LLM).

Writes artifacts/apps_rg/plans/pa_e0_compile_proof_receipt.json
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps_rg.prompt_assembly.e0_examples import example_after_text
from apps_rg.runtime.dispatch.executive_summary_pa import compile_executive_summary_prompt
from apps_rg.runtime.validators.executive_summary_sentence_utils import split_sentences

OUT = ROOT / "artifacts" / "apps_rg" / "plans" / "pa_e0_compile_proof_receipt.json"
GOLD_ID = "exec_summary_gold_base_resume_001"


def _extract_e0_segment(compiled_content: str) -> str:
    start = compiled_content.find("<!-- SLOT: E0 -->")
    if start < 0:
        return ""
    end = compiled_content.find("<!-- SLOT:", start + 16)
    return compiled_content[start:end] if end > start else compiled_content[start:]


def main() -> int:
    payload = {
        "product_visible": False,
        "run_id": "pa_e0_compile_proof",
        "target_title": "SVP Engineering",
        "target_company": "Proof Corp",
        "jd_text": "enterprise AI platform",
        "briefing": "regulated enterprise",
        "selected_fact_plan": {
            "facts": [
                {
                    "fact_id": "proof_fact_001",
                    "claim_text": "Delivered governed agentic AI platforms.",
                },
            ],
            "required_fact_ids": ["proof_fact_001"],
        },
    }
    out = compile_executive_summary_prompt(payload, run_id=payload["run_id"])
    content = out.artifact.messages[0]["content"]
    e0_seg = _extract_e0_segment(content)
    gold = example_after_text("executive_summary", GOLD_ID)
    gold_sents = len(split_sentences(gold))
    e0_has_gold = "productized AI revenue" in e0_seg
    stub_absent = "runtime architecture spanning orchestration, retrieval, policy enforcement" not in e0_seg

    receipt = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "section": "executive_summary",
        "gold_example_id": GOLD_ID,
        "yaml_gold_sentence_count": gold_sents,
        "compiled_e0_contains_yaml_gold_marker": e0_has_gold,
        "compiled_e0_missing_template_stub": stub_absent,
        "pass": bool(e0_has_gold and stub_absent and gold_sents >= 4),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(receipt, indent=2), encoding="utf-8")

    if not receipt["pass"]:
        print(json.dumps(receipt, indent=2))
        return 1
    print(f"PA-E0-COMPILE-PROOF PASS -> {OUT.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""One-shot audit: who actually triggers Qwen MEDIUM-tier dispatch in production?

Prints fan-in/callers for the canonical Qwen seam-points so we can verify
adoption vs the topology promised by routing-unification + qwen-adoption plans.

Run: python tools/analysis/_qwen_adoption_audit.py
"""
from __future__ import annotations

# W6 ADG consumer mode declaration (per .codex/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"


import glob
import sqlite3
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SNAP = sorted(glob.glob(str(REPO_ROOT / "artifacts/adg/adg_indexed_*.sqlite")))[-1]
print(f"snapshot: {SNAP}\n")

conn = sqlite3.connect(SNAP)
cur = conn.cursor()


# Schema note (verified 2026-04-25): nodes(id, adg_name, entity_type, layer,
# resolved_path, ...), edges(src_id, dst_id, relation_type, source_file, ...).
# We use edges.source_file as the calling file (most reliable), join nodes by
# id only when we need the symbol name on either end.


def section(title: str) -> None:
    print(f"\n{'=' * 78}\n{title}\n{'=' * 78}")


def run(label: str, sql: str, params: tuple = ()) -> None:
    section(label)
    rows = cur.execute(sql, params).fetchall()
    if not rows:
        print("  (no rows)")
        return
    for r in rows:
        print("  " + " | ".join(str(x) for x in r))


# 1) HealingRouter — who imports it?
run(
    "1) HealingRouter — module fan-in (imports)",
    """
    SELECT DISTINCT t.adg_name AS target, e.source_file AS caller_file
    FROM edges e
    JOIN nodes t ON t.id = e.dst_id
    WHERE t.adg_name LIKE '%HealingRouter%' AND e.relation_type = 'imports'
    ORDER BY e.source_file
    LIMIT 80
    """,
)

# 2) dispatch_to_executor — who calls it?
run(
    "2) HealingRouter.dispatch_to_executor — call sites",
    """
    SELECT DISTINCT t.adg_name AS target, e.source_file AS caller_file, e.line_no
    FROM edges e
    JOIN nodes t ON t.id = e.dst_id
    WHERE t.adg_name LIKE '%.dispatch_to_executor' AND e.relation_type = 'calls'
    ORDER BY e.source_file
    LIMIT 80
    """,
)

# 3) get_qwen_inference_gateway — actual gateway acquisition
run(
    "3) get_qwen_inference_gateway — call sites (direct Qwen invocation)",
    """
    SELECT DISTINCT t.adg_name AS target, e.source_file AS caller_file, e.line_no
    FROM edges e
    JOIN nodes t ON t.id = e.dst_id
    WHERE t.adg_name LIKE '%.get_qwen_inference_gateway' AND e.relation_type IN ('calls','imports')
    ORDER BY e.source_file
    LIMIT 80
    """,
)

# 4) QwenInferenceGateway / AppsQwenGateway — class fan-in
run(
    "4) QwenInferenceGateway / AppsQwenGateway — class fan-in (imports)",
    """
    SELECT DISTINCT t.adg_name AS target, e.source_file AS caller_file
    FROM edges e
    JOIN nodes t ON t.id = e.dst_id
    WHERE (t.adg_name LIKE '%.QwenInferenceGateway' OR t.adg_name LIKE '%.AppsQwenGateway')
      AND e.relation_type = 'imports'
    ORDER BY e.source_file
    LIMIT 80
    """,
)

# 5) LocalVLLMProvider / QwenJudgeProvider — Wave A consumers
run(
    "5) LocalVLLMProvider / QwenJudgeProvider — fan-in (Wave A consumers)",
    """
    SELECT DISTINCT t.adg_name AS target, e.source_file AS caller_file
    FROM edges e
    JOIN nodes t ON t.id = e.dst_id
    WHERE (t.adg_name LIKE '%.LocalVLLMProvider' OR t.adg_name LIKE '%.QwenJudgeProvider')
      AND e.relation_type = 'imports'
    ORDER BY e.source_file
    LIMIT 80
    """,
)

# 6) ConfidenceScorer — fan-in (where confidence-tier decisions ORIGINATE)
run(
    "6) ConfidenceScorer — fan-in (origin of MEDIUM/LOW routing decisions)",
    """
    SELECT DISTINCT t.adg_name AS target, e.source_file AS caller_file
    FROM edges e
    JOIN nodes t ON t.id = e.dst_id
    WHERE t.adg_name LIKE '%.ConfidenceScorer' AND e.relation_type = 'imports'
    ORDER BY e.source_file
    LIMIT 80
    """,
)

# 7) Apps that touch Qwen tier — fan-in via TIER_QWEN_LOCAL or QWEN_LOCAL_MODEL_ID
run(
    "7) QWEN_LOCAL_MODEL_ID / TIER_QWEN_LOCAL — fan-in (apps acknowledging local tier)",
    """
    SELECT DISTINCT t.adg_name AS target, e.source_file AS caller_file
    FROM edges e
    JOIN nodes t ON t.id = e.dst_id
    WHERE (t.adg_name LIKE '%.QWEN_LOCAL_MODEL_ID' OR t.adg_name LIKE '%.TIER_QWEN_LOCAL' OR t.adg_name LIKE '%.VLLM_BASE_URL')
      AND e.relation_type = 'imports'
    ORDER BY e.source_file
    LIMIT 80
    """,
)

# 8) Provider enum LOCAL_VLLM — actual provider routing
run(
    "8) ProviderType.LOCAL_VLLM / Provider.LOCAL_VLLM — fan-in",
    """
    SELECT DISTINCT t.adg_name AS target, e.source_file AS caller_file, e.relation_type
    FROM edges e
    JOIN nodes t ON t.id = e.dst_id
    WHERE t.adg_name LIKE '%LOCAL_VLLM%'
      AND e.relation_type IN ('imports','reads_from')
    ORDER BY e.source_file
    LIMIT 80
    """,
)

# 9) Anti-evidence: apps_* that call SovereignLLMGateway WITHOUT routing through HealingRouter
run(
    "9) SovereignLLMGateway — direct fan-in (potential confidence-routing bypass)",
    """
    SELECT DISTINCT t.adg_name AS target, e.source_file AS caller_file
    FROM edges e
    JOIN nodes t ON t.id = e.dst_id
    WHERE t.adg_name LIKE '%.SovereignLLMGateway' AND e.relation_type = 'imports'
    ORDER BY e.source_file
    LIMIT 80
    """,
)

# 10) Files with hardcoded gemini / claude / openai model strings
run(
    "10) Files referencing GEMINI_FLASH_MODEL_ID / GEMINI_PRO_MODEL_ID — fan-in",
    """
    SELECT DISTINCT t.adg_name AS target, e.source_file AS caller_file
    FROM edges e
    JOIN nodes t ON t.id = e.dst_id
    WHERE (t.adg_name LIKE '%.GEMINI_FLASH_MODEL_ID' OR t.adg_name LIKE '%.GEMINI_PRO_MODEL_ID')
      AND e.relation_type = 'imports'
    ORDER BY e.source_file
    LIMIT 80
    """,
)

conn.close()
print("\nDone.")

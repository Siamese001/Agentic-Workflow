"""Shared constants for the heal-classifier offline training pipeline.

FEATURE_ORDER must stay in sync with ClassifierFeatures field declaration order
in agentic_core/L2_execution/healers/heal_classifier_model.py.
"""

# Feature vector order — must exactly match ClassifierFeatures.__dataclass_fields__
FEATURE_ORDER: list[str] = [
    "failure_class",
    "retry_count",
    "error_code_hash",
    "lineage_hash_prefix",
    "budget_remaining",
    "source_layer_id",
]

# Files that form the complete artifact package
ARTIFACT_FILES: list[str] = [
    "model.pkl",
    "ood_detector.pkl",
    "feature_schema.json",
    "calibration_meta.json",
    "training_meta.json",
    "ood_meta.json",
    "hash_manifest.json",
    "model_version_hash",
]

# Files whose bytes are concatenated to derive model_version_hash
HASH_INPUT_FILES: list[str] = [
    "model.pkl",
    "ood_detector.pkl",
    "feature_schema.json",
]

# Offline evaluation thresholds — all must pass for promotion readiness
MACRO_F1_MIN: float = 0.72
PER_CLASS_F1_MIN: float = 0.60
ECE_MAX: float = 0.05
AUROC_MIN: float = 0.80
FALLBACK_RATE_MAX: float = 0.20
OOD_FPR_MAX: float = 0.01
INFERENCE_LATENCY_US_BUDGET: int = 1_000  # 1 ms hard budget

# Failure class names — index must match HealFailureClass enum declaration order
FAILURE_CLASS_NAMES: list[str] = [
    "DRIFT_DETECTION",   # index 0
    "IMPORT_BOUNDARY",   # index 1
    "LAYER_INVERSION",   # index 2
    "SSOT_DRIFT",        # index 3
    "UNKNOWN",           # index 4 — excluded from training
]

NON_UNKNOWN_CLASSES: list[str] = FAILURE_CLASS_NAMES[:4]
UNKNOWN_CLASS_INDEX: int = 4

# Repair outcome label classes
REPAIR_OUTCOME_CLASSES: list[str] = [
    "FAILED",
    "HEALED_HITL",
    "HEALED_LLM",
    "HEALED_LOCAL",
]

# Dataset exclusion sentinels
OOD_BUDGET_SENTINEL: float = 1.0
MAX_RETRY_COUNT: int = 5

# Artifact versioning
SCHEMA_VERSION: str = "1.0"
ARTIFACT_VERSION: str = "v1"

# Promotion packet required files
PROMOTION_PACKET_FILES: list[str] = [
    "artifact",
    "offline_eval_report.md",
    "shadow_divergence_report.md",
    "hitl_cohort_review.md",
    "promotion_record.json",
    "uwg_proposal.json",
]

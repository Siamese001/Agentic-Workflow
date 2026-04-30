"""Shared binding scope for the 10C ledger proof-evidence pipeline.

This module is the SINGLE source of truth for two scope-sensitive artifacts:

  - ``CRITICAL_REQ_IDS`` — the canonical set of CRITICAL requirement IDs that
    are subject to the proof-evidence pipeline (5 W4d-4/W4d-5 pilot rows +
    24 Wave 1 CRITICAL rows = 29).
  - ``CRITICAL_BINDING_SCOPE`` — the pathspec tuple passed to
    ``git status --porcelain --`` to detect dirt in files that materially
    affect proof-bundle binding integrity (test sources, fixtures, the
    validator, the bundle emitter, the CI gate, the ledger CSV, the bundle
    directory, and the test generator).

Both are imported by:

  - ``tools/requirements/emit_proof_bundles.py``
  - ``tools/requirements/update_pilot_ledger.py``
  - ``ops_scripts/ci/check_10c_pilot_proof_evidence.py`` (CRITICAL_REQ_IDS only)

When extending this scope (adding Wave 2+ rows), append to BOTH tuples
deterministically and re-run ``emit_proof_bundles.py`` to refresh bundles.
"""

from __future__ import annotations

# Canonical set of CRITICAL requirement IDs covered by the proof-evidence
# pipeline. Order is meaningful for deterministic iteration in reports.
CRITICAL_REQ_IDS: tuple[str, ...] = (
    # --- W4d-4/W4d-5 pilot (5) ---
    "10C-REQ-049",  # U0 ingress invariant
    "10C-REQ-167",  # L5 policy plane
    "10C-REQ-086",  # PA.2 slot composition
    "10C-REQ-089",  # L2 sealed envelope
    "10C-REQ-122",  # UWG single-writer
    # --- Wave 1 (24) ---
    "10C-REQ-005",  # Ingest: ChunkSealedEnvelope metadata-bound-before-embedding
    "10C-REQ-064",  # L1: PlanContract no-execution
    "10C-REQ-074",  # L1: PlanContract output contract
    "10C-REQ-075",  # L0: RouteContract pre-routing gate
    "10C-REQ-099",  # Exit: X3DispositionPacket explicit dispositions
    "10C-REQ-103",  # L5: certification result chain
    "10C-REQ-116",  # L5: certification result
    "10C-REQ-119",  # L5: certification result
    "10C-REQ-140",  # UWG: CommitRequest write admission
    "10C-REQ-153",  # UWG: CommitRequest write admission
    "10C-REQ-160",  # L5: certification result
    "10C-REQ-163",  # Ingest: ChunkSealedEnvelope
    "10C-REQ-164",  # L2: ExecutionResult sealed
    "10C-REQ-165",  # OTEL: replay-key audit
    "10C-REQ-166",  # OTEL: replay-key audit
    "10C-REQ-175",  # L2: ExecutionResult sealed
    "10C-REQ-177",  # UWG: CommitRequest write admission
    "10C-REQ-182",  # L5: certification result
    "10C-REQ-185",  # UWG: CommitRequest write admission
    "10C-REQ-187",  # L5: certification result
    "10C-REQ-191",  # L6: shadow eval record
    "10C-REQ-192",  # L5: certification result
    "10C-REQ-195",  # L5: certification result
    "10C-REQ-199",  # L5: certification result
    # --- Wave 2 (30 HIGH severity rows) ---
    # L5 Governance / Safety (21):
    "10C-REQ-100", "10C-REQ-101", "10C-REQ-102", "10C-REQ-110", "10C-REQ-111",
    "10C-REQ-112", "10C-REQ-113", "10C-REQ-114", "10C-REQ-115", "10C-REQ-117",
    "10C-REQ-120", "10C-REQ-139", "10C-REQ-155", "10C-REQ-156", "10C-REQ-157",
    "10C-REQ-158", "10C-REQ-159", "10C-REQ-161", "10C-REQ-176", "10C-REQ-179",
    "10C-REQ-193",
    # Offline Ingestion / Index Build (9):
    "10C-REQ-001", "10C-REQ-002", "10C-REQ-006", "10C-REQ-007", "10C-REQ-012",
    "10C-REQ-014", "10C-REQ-015", "10C-REQ-016", "10C-REQ-017",
    # --- Wave 3 (30 HIGH severity rows) ---
    # C0 Context Engine (19):
    "10C-REQ-031", "10C-REQ-032", "10C-REQ-033", "10C-REQ-034", "10C-REQ-043",
    "10C-REQ-044", "10C-REQ-045", "10C-REQ-046", "10C-REQ-047", "10C-REQ-048",
    "10C-REQ-081", "10C-REQ-082", "10C-REQ-083", "10C-REQ-084", "10C-REQ-141",
    "10C-REQ-142", "10C-REQ-143", "10C-REQ-144", "10C-REQ-145",
    # L1 Reasoning Plan (11):
    "10C-REQ-056", "10C-REQ-060", "10C-REQ-061", "10C-REQ-065", "10C-REQ-066",
    "10C-REQ-068", "10C-REQ-069", "10C-REQ-070", "10C-REQ-169", "10C-REQ-174",
    "10C-REQ-180",
    # --- Wave 4 (30 HIGH severity rows) ---
    # UWG / L4 State (17):
    "10C-REQ-008", "10C-REQ-010", "10C-REQ-018", "10C-REQ-019", "10C-REQ-020",
    "10C-REQ-029", "10C-REQ-030", "10C-REQ-042", "10C-REQ-123", "10C-REQ-124",
    "10C-REQ-125", "10C-REQ-126", "10C-REQ-127", "10C-REQ-149", "10C-REQ-150",
    "10C-REQ-152", "10C-REQ-154",
    # L6 Shadow Eval / System Learning (13):
    "10C-REQ-106", "10C-REQ-107", "10C-REQ-108", "10C-REQ-121", "10C-REQ-131",
    "10C-REQ-132", "10C-REQ-133", "10C-REQ-146", "10C-REQ-147", "10C-REQ-148",
    "10C-REQ-151", "10C-REQ-173", "10C-REQ-190",
    # --- Final sweep W5+W6+W7 (79 rows: 52 HIGH + 27 MEDIUM) ---
    # 01_U0_Request_Intake (7):
    "10C-REQ-050", "10C-REQ-051", "10C-REQ-052", "10C-REQ-053", "10C-REQ-054",
    "10C-REQ-055", "10C-REQ-168",
    # 02_L1_Reasoning_Plan (11):
    "10C-REQ-057", "10C-REQ-058", "10C-REQ-059", "10C-REQ-062", "10C-REQ-063",
    "10C-REQ-067", "10C-REQ-071", "10C-REQ-072", "10C-REQ-073", "10C-REQ-183",
    "10C-REQ-184",
    # 03B_PA_Prompt_Assembly (4):
    "10C-REQ-035", "10C-REQ-085", "10C-REQ-087", "10C-REQ-088",
    # 03_L0_Route_Decision (6):
    "10C-REQ-076", "10C-REQ-077", "10C-REQ-078", "10C-REQ-079", "10C-REQ-080",
    "10C-REQ-170",
    # 03_L3_Orchestration (8):
    "10C-REQ-135", "10C-REQ-136", "10C-REQ-137", "10C-REQ-138", "10C-REQ-181",
    "10C-REQ-188", "10C-REQ-189", "10C-REQ-198",
    # 04_L2_Execute (9):
    "10C-REQ-090", "10C-REQ-091", "10C-REQ-092", "10C-REQ-093", "10C-REQ-094",
    "10C-REQ-171", "10C-REQ-186", "10C-REQ-196", "10C-REQ-197",
    # 05_Exit_Evaluation_and_Control (5):
    "10C-REQ-095", "10C-REQ-096", "10C-REQ-097", "10C-REQ-098", "10C-REQ-172",
    # 06_L6_Shadow_Evaluation_System_Learning (9):
    "10C-REQ-104", "10C-REQ-105", "10C-REQ-109", "10C-REQ-128", "10C-REQ-129",
    "10C-REQ-130", "10C-REQ-134", "10C-REQ-178", "10C-REQ-200",
    # Cross_Cutting_Observability_Replay_Audit (2):
    "10C-REQ-118", "10C-REQ-194",
    # Offline_Ingestion_Index_Build (18):
    "10C-REQ-003", "10C-REQ-004", "10C-REQ-009", "10C-REQ-013", "10C-REQ-021",
    "10C-REQ-022", "10C-REQ-023", "10C-REQ-024", "10C-REQ-025", "10C-REQ-026",
    "10C-REQ-027", "10C-REQ-028", "10C-REQ-036", "10C-REQ-037", "10C-REQ-038",
    "10C-REQ-039", "10C-REQ-040", "10C-REQ-041",
)


# Pathspec tuple for git-status scope check. Files OUTSIDE this scope can be
# dirty without invalidating the binding (per the W4d-5 binding policy).
CRITICAL_BINDING_SCOPE: tuple[str, ...] = (
    # --- Shared fixtures (all 5 pilot + 24 wave1 tests use these) ---
    "tests/fixtures/proof_evidence/",
    "tests/fixtures/__init__.py",
    # --- 5 pilot test files ---
    "tests/unit/agentic_core/L1_cognition/intake/test_10c_req_049.py",
    "tests/unit/agentic_core/L1_cognition/intake/__init__.py",
    "tests/unit/agentic_core/L1_cognition/prompt_assembly/test_10c_req_086.py",
    "tests/unit/agentic_core/L1_cognition/prompt_assembly/__init__.py",
    "tests/unit/agentic_core/L2_execution/test_10c_req_089.py",
    "tests/unit/agentic_core/L4_state/test_10c_req_122.py",
    "tests/unit/agentic_core/L5_safety/test_10c_req_167.py",
    # --- 24 Wave 1 test files ---
    "tests/unit/agentic_core/L1_cognition/c0_context/ingestion/test_10c_req_005.py",
    "tests/unit/agentic_core/L1_cognition/c0_context/ingestion/test_10c_req_163.py",
    "tests/unit/agentic_core/L1_cognition/c0_context/ingestion/__init__.py",
    "tests/unit/agentic_core/L1_cognition/c0_context/__init__.py",
    "tests/unit/agentic_core/L1_cognition/test_10c_req_064.py",
    "tests/unit/agentic_core/L1_cognition/test_10c_req_074.py",
    "tests/unit/agentic_core/L1_cognition/__init__.py",
    "tests/unit/agentic_core/L0_routing/test_10c_req_075.py",
    "tests/unit/agentic_core/L0_routing/__init__.py",
    "tests/unit/agentic_core/L5_safety/exit_control/test_10c_req_099.py",
    "tests/unit/agentic_core/L5_safety/exit_control/__init__.py",
    "tests/unit/agentic_core/L5_safety/test_10c_req_103.py",
    "tests/unit/agentic_core/L5_safety/test_10c_req_116.py",
    "tests/unit/agentic_core/L5_safety/test_10c_req_119.py",
    "tests/unit/agentic_core/L5_safety/test_10c_req_160.py",
    "tests/unit/agentic_core/L5_safety/test_10c_req_182.py",
    "tests/unit/agentic_core/L5_safety/test_10c_req_187.py",
    "tests/unit/agentic_core/L5_safety/test_10c_req_192.py",
    "tests/unit/agentic_core/L5_safety/test_10c_req_195.py",
    "tests/unit/agentic_core/L5_safety/test_10c_req_199.py",
    "tests/unit/agentic_core/L5_safety/__init__.py",
    "tests/unit/agentic_core/L4_state/test_10c_req_140.py",
    "tests/unit/agentic_core/L4_state/test_10c_req_153.py",
    "tests/unit/agentic_core/L4_state/test_10c_req_177.py",
    "tests/unit/agentic_core/L4_state/test_10c_req_185.py",
    "tests/unit/agentic_core/L4_state/__init__.py",
    "tests/unit/agentic_core/L2_execution/test_10c_req_164.py",
    "tests/unit/agentic_core/L2_execution/test_10c_req_175.py",
    "tests/unit/agentic_core/L2_execution/__init__.py",
    "tests/unit/agentic_core/L6_observability/test_10c_req_165.py",
    "tests/unit/agentic_core/L6_observability/test_10c_req_166.py",
    "tests/unit/agentic_core/L6_observability/test_10c_req_191.py",
    "tests/unit/agentic_core/L6_observability/__init__.py",
    "tests/unit/agentic_core/__init__.py",
    # --- Wave 2: 21 L5 + 9 Ingestion HIGH rows ---
    "tests/unit/agentic_core/L5_safety/test_10c_req_100.py",
    "tests/unit/agentic_core/L5_safety/test_10c_req_101.py",
    "tests/unit/agentic_core/L5_safety/test_10c_req_102.py",
    "tests/unit/agentic_core/L5_safety/test_10c_req_110.py",
    "tests/unit/agentic_core/L5_safety/test_10c_req_111.py",
    "tests/unit/agentic_core/L5_safety/test_10c_req_112.py",
    "tests/unit/agentic_core/L5_safety/test_10c_req_113.py",
    "tests/unit/agentic_core/L5_safety/test_10c_req_114.py",
    "tests/unit/agentic_core/L5_safety/test_10c_req_115.py",
    "tests/unit/agentic_core/L5_safety/test_10c_req_117.py",
    "tests/unit/agentic_core/L5_safety/test_10c_req_120.py",
    "tests/unit/agentic_core/L5_safety/test_10c_req_139.py",
    "tests/unit/agentic_core/L5_safety/test_10c_req_155.py",
    "tests/unit/agentic_core/L5_safety/test_10c_req_156.py",
    "tests/unit/agentic_core/L5_safety/test_10c_req_157.py",
    "tests/unit/agentic_core/L5_safety/test_10c_req_158.py",
    "tests/unit/agentic_core/L5_safety/test_10c_req_159.py",
    "tests/unit/agentic_core/L5_safety/test_10c_req_161.py",
    "tests/unit/agentic_core/L5_safety/test_10c_req_176.py",
    "tests/unit/agentic_core/L5_safety/test_10c_req_179.py",
    "tests/unit/agentic_core/L5_safety/test_10c_req_193.py",
    "tests/unit/agentic_core/L1_cognition/c0_context/ingestion/test_10c_req_001.py",
    "tests/unit/agentic_core/L1_cognition/c0_context/ingestion/test_10c_req_002.py",
    "tests/unit/agentic_core/L1_cognition/c0_context/ingestion/test_10c_req_006.py",
    "tests/unit/agentic_core/L1_cognition/c0_context/ingestion/test_10c_req_007.py",
    "tests/unit/agentic_core/L1_cognition/c0_context/ingestion/test_10c_req_012.py",
    "tests/unit/agentic_core/L1_cognition/c0_context/ingestion/test_10c_req_014.py",
    "tests/unit/agentic_core/L1_cognition/c0_context/ingestion/test_10c_req_015.py",
    "tests/unit/agentic_core/L1_cognition/c0_context/ingestion/test_10c_req_016.py",
    "tests/unit/agentic_core/L1_cognition/c0_context/ingestion/test_10c_req_017.py",
    # --- Wave 3: 19 C0 Context + 11 L1 Plan HIGH rows ---
    "tests/unit/agentic_core/L1_cognition/c0_context/test_10c_req_031.py",
    "tests/unit/agentic_core/L1_cognition/c0_context/test_10c_req_032.py",
    "tests/unit/agentic_core/L1_cognition/c0_context/test_10c_req_033.py",
    "tests/unit/agentic_core/L1_cognition/c0_context/test_10c_req_034.py",
    "tests/unit/agentic_core/L1_cognition/c0_context/test_10c_req_043.py",
    "tests/unit/agentic_core/L1_cognition/c0_context/test_10c_req_044.py",
    "tests/unit/agentic_core/L1_cognition/c0_context/test_10c_req_045.py",
    "tests/unit/agentic_core/L1_cognition/c0_context/test_10c_req_046.py",
    "tests/unit/agentic_core/L1_cognition/c0_context/test_10c_req_047.py",
    "tests/unit/agentic_core/L1_cognition/c0_context/test_10c_req_048.py",
    "tests/unit/agentic_core/L1_cognition/c0_context/test_10c_req_081.py",
    "tests/unit/agentic_core/L1_cognition/c0_context/test_10c_req_082.py",
    "tests/unit/agentic_core/L1_cognition/c0_context/test_10c_req_083.py",
    "tests/unit/agentic_core/L1_cognition/c0_context/test_10c_req_084.py",
    "tests/unit/agentic_core/L1_cognition/c0_context/test_10c_req_141.py",
    "tests/unit/agentic_core/L1_cognition/c0_context/test_10c_req_142.py",
    "tests/unit/agentic_core/L1_cognition/c0_context/test_10c_req_143.py",
    "tests/unit/agentic_core/L1_cognition/c0_context/test_10c_req_144.py",
    "tests/unit/agentic_core/L1_cognition/c0_context/test_10c_req_145.py",
    "tests/unit/agentic_core/L1_cognition/test_10c_req_056.py",
    "tests/unit/agentic_core/L1_cognition/test_10c_req_060.py",
    "tests/unit/agentic_core/L1_cognition/test_10c_req_061.py",
    "tests/unit/agentic_core/L1_cognition/test_10c_req_065.py",
    "tests/unit/agentic_core/L1_cognition/test_10c_req_066.py",
    "tests/unit/agentic_core/L1_cognition/test_10c_req_068.py",
    "tests/unit/agentic_core/L1_cognition/test_10c_req_069.py",
    "tests/unit/agentic_core/L1_cognition/test_10c_req_070.py",
    "tests/unit/agentic_core/L1_cognition/test_10c_req_169.py",
    "tests/unit/agentic_core/L1_cognition/test_10c_req_174.py",
    "tests/unit/agentic_core/L1_cognition/test_10c_req_180.py",
    # --- Wave 4: 17 UWG + 13 L6 Shadow Eval HIGH rows ---
    "tests/unit/agentic_core/L4_state/test_10c_req_008.py",
    "tests/unit/agentic_core/L4_state/test_10c_req_010.py",
    "tests/unit/agentic_core/L4_state/test_10c_req_018.py",
    "tests/unit/agentic_core/L4_state/test_10c_req_019.py",
    "tests/unit/agentic_core/L4_state/test_10c_req_020.py",
    "tests/unit/agentic_core/L4_state/test_10c_req_029.py",
    "tests/unit/agentic_core/L4_state/test_10c_req_030.py",
    "tests/unit/agentic_core/L4_state/test_10c_req_042.py",
    "tests/unit/agentic_core/L4_state/test_10c_req_123.py",
    "tests/unit/agentic_core/L4_state/test_10c_req_124.py",
    "tests/unit/agentic_core/L4_state/test_10c_req_125.py",
    "tests/unit/agentic_core/L4_state/test_10c_req_126.py",
    "tests/unit/agentic_core/L4_state/test_10c_req_127.py",
    "tests/unit/agentic_core/L4_state/test_10c_req_149.py",
    "tests/unit/agentic_core/L4_state/test_10c_req_150.py",
    "tests/unit/agentic_core/L4_state/test_10c_req_152.py",
    "tests/unit/agentic_core/L4_state/test_10c_req_154.py",
    "tests/unit/agentic_core/L6_observability/test_10c_req_106.py",
    "tests/unit/agentic_core/L6_observability/test_10c_req_107.py",
    "tests/unit/agentic_core/L6_observability/test_10c_req_108.py",
    "tests/unit/agentic_core/L6_observability/test_10c_req_121.py",
    "tests/unit/agentic_core/L6_observability/test_10c_req_131.py",
    "tests/unit/agentic_core/L6_observability/test_10c_req_132.py",
    "tests/unit/agentic_core/L6_observability/test_10c_req_133.py",
    "tests/unit/agentic_core/L6_observability/test_10c_req_146.py",
    "tests/unit/agentic_core/L6_observability/test_10c_req_147.py",
    "tests/unit/agentic_core/L6_observability/test_10c_req_148.py",
    "tests/unit/agentic_core/L6_observability/test_10c_req_151.py",
    "tests/unit/agentic_core/L6_observability/test_10c_req_173.py",
    "tests/unit/agentic_core/L6_observability/test_10c_req_190.py",
    # --- Final sweep W5+W6+W7: 79 remaining rows ---
    "tests/unit/agentic_core/L3_orchestration/__init__.py",
    "tests/unit/agentic_core/L0_routing/test_10c_req_076.py",
    "tests/unit/agentic_core/L0_routing/test_10c_req_077.py",
    "tests/unit/agentic_core/L0_routing/test_10c_req_078.py",
    "tests/unit/agentic_core/L0_routing/test_10c_req_079.py",
    "tests/unit/agentic_core/L0_routing/test_10c_req_080.py",
    "tests/unit/agentic_core/L0_routing/test_10c_req_170.py",
    "tests/unit/agentic_core/L1_cognition/c0_context/ingestion/test_10c_req_003.py",
    "tests/unit/agentic_core/L1_cognition/c0_context/ingestion/test_10c_req_004.py",
    "tests/unit/agentic_core/L1_cognition/c0_context/ingestion/test_10c_req_009.py",
    "tests/unit/agentic_core/L1_cognition/c0_context/ingestion/test_10c_req_013.py",
    "tests/unit/agentic_core/L1_cognition/c0_context/ingestion/test_10c_req_021.py",
    "tests/unit/agentic_core/L1_cognition/c0_context/ingestion/test_10c_req_022.py",
    "tests/unit/agentic_core/L1_cognition/c0_context/ingestion/test_10c_req_023.py",
    "tests/unit/agentic_core/L1_cognition/c0_context/ingestion/test_10c_req_024.py",
    "tests/unit/agentic_core/L1_cognition/c0_context/ingestion/test_10c_req_025.py",
    "tests/unit/agentic_core/L1_cognition/c0_context/ingestion/test_10c_req_026.py",
    "tests/unit/agentic_core/L1_cognition/c0_context/ingestion/test_10c_req_027.py",
    "tests/unit/agentic_core/L1_cognition/c0_context/ingestion/test_10c_req_028.py",
    "tests/unit/agentic_core/L1_cognition/c0_context/ingestion/test_10c_req_036.py",
    "tests/unit/agentic_core/L1_cognition/c0_context/ingestion/test_10c_req_037.py",
    "tests/unit/agentic_core/L1_cognition/c0_context/ingestion/test_10c_req_038.py",
    "tests/unit/agentic_core/L1_cognition/c0_context/ingestion/test_10c_req_039.py",
    "tests/unit/agentic_core/L1_cognition/c0_context/ingestion/test_10c_req_040.py",
    "tests/unit/agentic_core/L1_cognition/c0_context/ingestion/test_10c_req_041.py",
    "tests/unit/agentic_core/L1_cognition/intake/test_10c_req_050.py",
    "tests/unit/agentic_core/L1_cognition/intake/test_10c_req_051.py",
    "tests/unit/agentic_core/L1_cognition/intake/test_10c_req_052.py",
    "tests/unit/agentic_core/L1_cognition/intake/test_10c_req_053.py",
    "tests/unit/agentic_core/L1_cognition/intake/test_10c_req_054.py",
    "tests/unit/agentic_core/L1_cognition/intake/test_10c_req_055.py",
    "tests/unit/agentic_core/L1_cognition/intake/test_10c_req_168.py",
    "tests/unit/agentic_core/L1_cognition/prompt_assembly/test_10c_req_035.py",
    "tests/unit/agentic_core/L1_cognition/prompt_assembly/test_10c_req_085.py",
    "tests/unit/agentic_core/L1_cognition/prompt_assembly/test_10c_req_087.py",
    "tests/unit/agentic_core/L1_cognition/prompt_assembly/test_10c_req_088.py",
    "tests/unit/agentic_core/L1_cognition/test_10c_req_057.py",
    "tests/unit/agentic_core/L1_cognition/test_10c_req_058.py",
    "tests/unit/agentic_core/L1_cognition/test_10c_req_059.py",
    "tests/unit/agentic_core/L1_cognition/test_10c_req_062.py",
    "tests/unit/agentic_core/L1_cognition/test_10c_req_063.py",
    "tests/unit/agentic_core/L1_cognition/test_10c_req_067.py",
    "tests/unit/agentic_core/L1_cognition/test_10c_req_071.py",
    "tests/unit/agentic_core/L1_cognition/test_10c_req_072.py",
    "tests/unit/agentic_core/L1_cognition/test_10c_req_073.py",
    "tests/unit/agentic_core/L1_cognition/test_10c_req_183.py",
    "tests/unit/agentic_core/L1_cognition/test_10c_req_184.py",
    "tests/unit/agentic_core/L2_execution/test_10c_req_090.py",
    "tests/unit/agentic_core/L2_execution/test_10c_req_091.py",
    "tests/unit/agentic_core/L2_execution/test_10c_req_092.py",
    "tests/unit/agentic_core/L2_execution/test_10c_req_093.py",
    "tests/unit/agentic_core/L2_execution/test_10c_req_094.py",
    "tests/unit/agentic_core/L2_execution/test_10c_req_171.py",
    "tests/unit/agentic_core/L2_execution/test_10c_req_186.py",
    "tests/unit/agentic_core/L2_execution/test_10c_req_196.py",
    "tests/unit/agentic_core/L2_execution/test_10c_req_197.py",
    "tests/unit/agentic_core/L3_orchestration/test_10c_req_135.py",
    "tests/unit/agentic_core/L3_orchestration/test_10c_req_136.py",
    "tests/unit/agentic_core/L3_orchestration/test_10c_req_137.py",
    "tests/unit/agentic_core/L3_orchestration/test_10c_req_138.py",
    "tests/unit/agentic_core/L3_orchestration/test_10c_req_181.py",
    "tests/unit/agentic_core/L3_orchestration/test_10c_req_188.py",
    "tests/unit/agentic_core/L3_orchestration/test_10c_req_189.py",
    "tests/unit/agentic_core/L3_orchestration/test_10c_req_198.py",
    "tests/unit/agentic_core/L5_safety/exit_control/test_10c_req_095.py",
    "tests/unit/agentic_core/L5_safety/exit_control/test_10c_req_096.py",
    "tests/unit/agentic_core/L5_safety/exit_control/test_10c_req_097.py",
    "tests/unit/agentic_core/L5_safety/exit_control/test_10c_req_098.py",
    "tests/unit/agentic_core/L5_safety/exit_control/test_10c_req_172.py",
    "tests/unit/agentic_core/L6_observability/test_10c_req_104.py",
    "tests/unit/agentic_core/L6_observability/test_10c_req_105.py",
    "tests/unit/agentic_core/L6_observability/test_10c_req_109.py",
    "tests/unit/agentic_core/L6_observability/test_10c_req_118.py",
    "tests/unit/agentic_core/L6_observability/test_10c_req_128.py",
    "tests/unit/agentic_core/L6_observability/test_10c_req_129.py",
    "tests/unit/agentic_core/L6_observability/test_10c_req_130.py",
    "tests/unit/agentic_core/L6_observability/test_10c_req_134.py",
    "tests/unit/agentic_core/L6_observability/test_10c_req_178.py",
    "tests/unit/agentic_core/L6_observability/test_10c_req_194.py",
    "tests/unit/agentic_core/L6_observability/test_10c_req_200.py",
    # --- Tooling (proof-binding pipeline) ---
    "tools/requirements/emit_proof_bundles.py",
    "tools/requirements/validate_10c_proof_ledger.py",
    "tools/requirements/update_pilot_ledger.py",
    "tools/requirements/generate_wave1_tests.py",
    "tools/requirements/_binding_scope.py",
    "ops_scripts/ci/check_10c_pilot_proof_evidence.py",
    # --- Writeback target (expected-dirty during binding) ---
    "docs/reports/design/10c_reconciliation/10c_semantic_requirement_ledger.csv",
    "artifacts/requirements/proof_bundles/",
)

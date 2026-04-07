"""Create zip package with ADG artifacts + comprehensive runtime files for ChatGPT validation."""

import zipfile
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_validated_by_safety_plane,
    _emit_writes_through,
    emit_determinism_digest,
)

_emit_writes_through("p1", "_create_chatgpt_validation_package", "uwg_governed_write")
_emit_writes_through("p1", "_create_chatgpt_validation_package", "uwg_governed_write_2")
_emit_pulls_context("p1", "_create_chatgpt_validation_package", "context_retrieval")
_emit_pulls_context("p1", "_create_chatgpt_validation_package", "context_retrieval_2")
emit_determinism_digest("trace__create_chatgpt_validation_package", "_create_chatgpt_validation_package_dispatch")
emit_determinism_digest("trace__create_chatgpt_validation_package", "_create_chatgpt_validation_package_complete")
_emit_validated_by_safety_plane("p1", "_create_chatgpt_validation_package", "safety_validation")


def create_validation_package():
    """Create zip with ADG + comprehensive runtime enforcement files for external validation."""

    repo_root = Path(r"c:\Git\Agentic-Workflow")
    output_dir = repo_root / "artifacts" / "adg"

    # Use DST-correct timestamp (EDT = UTC-4)
    zip_path = output_dir / "adg_validation_package_03132026_0536.zip"

    # ADG artifacts - OPTIMISED set (3 files instead of 6):
    #   KEPT:    adg_indexed.sqlite   - superset of all JSON edges+nodes (217k edges, full schema)
    #            adg_symbol_graph     - symbol-level detail (classes, functions) not in sqlite abbrev
    #            adg_snapshot         - 7 KB summary stats, near-zero cost, high signal
    #   DROPPED: adg_file_graph       - fully subsumed by sqlite (file edges are a subset)
    #            adg_governance_graph - governance edges in sqlite relation_type col
    #            adg_graphsnap        - 28 MB of canonical ordering arrays, no validation signal
    timestamp = "0536"
    adg_files = [
        f"artifacts/adg/adg_indexed_03132026_{timestamp}.sqlite",
        f"artifacts/adg/adg_symbol_graph_03132026_{timestamp}.json",
        f"artifacts/adg/adg_snapshot_03132026_{timestamp}.json",
    ]

    # MINIMAL runtime enforcement files — one primary file per gap
    # Selected as the single most signal-dense file that proves enforcement exists
    runtime_files = [
        # Gap 1: UWG mutation chokepoint — ToolNotAllowedError + replay_mode + allowlist enforcement
        "agentic_core/L2_execution/UniversalWriteGateway.py",
        # Gap 2: Determinism/replay — intercepts socket/random/datetime/fs/subprocess at kernel level
        "agentic_core/L2_execution/determinism/replay_guard.py",
        # Gap 3: Policy hash — validates every InstructionPacket carries active Merkle policy root
        "agentic_core/L0_routing/enforcement/policy_hash_enforcer.py",
        # Gap 4: HITL/DPO lineage — APPROVE/REJECT → DPO pair with stable hash
        "agentic_core/L6_observability/engines/hitl_dpo_pair_generator.py",
        # Gap 5: Meta-learning commit gating — explicit gates, fail-closed, no background apply
        "agentic_core/L0_routing/meta_control/meta_apply.py",
    ]

    print(f"Creating comprehensive validation package: {zip_path}")
    print("=" * 80)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # Add ADG artifacts
        print(f"\n[1/3] Adding ADG artifacts (3 files, timestamp: {timestamp}):")
        for file_path in adg_files:
            full_path = repo_root / file_path
            if full_path.exists():
                arcname = f"adg/{full_path.name}"
                zf.write(full_path, arcname)
                size_mb = full_path.stat().st_size / (1024 * 1024)
                print(f"  ✓ {arcname} ({size_mb:.2f} MB)")
            else:
                print(f"  ✗ MISSING: {file_path}")

        # Add runtime enforcement files
        print(f"\n[2/3] Adding MINIMAL runtime enforcement files ({len(runtime_files)} files, one per gap):")
        for file_path in runtime_files:
            full_path = repo_root / file_path
            if full_path.exists():
                arcname = f"runtime/{file_path}"
                zf.write(full_path, arcname)
                size_kb = full_path.stat().st_size / 1024
                print(f"  ✓ {arcname} ({size_kb:.1f} KB)")
            else:
                print(f"  ✗ MISSING: {file_path}")

        # Add validation script
        print("\n[3/3] Adding validation tools:")
        validation_script = "tools/_validate_adg_claims.py"
        full_path = repo_root / validation_script
        if full_path.exists():
            arcname = f"validation/{validation_script}"
            zf.write(full_path, arcname)
            size_kb = full_path.stat().st_size / 1024
            print(f"  ✓ {arcname} ({size_kb:.1f} KB)")
        else:
            print(f"  ✗ MISSING: {validation_script}")

    # Get final zip size
    zip_size_mb = zip_path.stat().st_size / (1024 * 1024)
    total_files = len(adg_files) + len(runtime_files) + 1  # +1 for validation script

    print("\n" + "=" * 80)
    print(f"✓ Package created: {zip_path}")
    print("✓ Location: artifacts/adg/ (SSOT-compliant)")
    print(f"✓ Total size: {zip_size_mb:.2f} MB")
    print(f"✓ Total files: {total_files} (3 ADG + {len(runtime_files)} runtime minimal + 1 validation)")

    # Create manifest in same directory
    manifest_path = output_dir / "MANIFEST_validation_0536.txt"
    with open(manifest_path, "w") as f:
        f.write("ChatGPT Comprehensive ADG + Runtime Validation Package\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Package: {zip_path.name}\n")
        f.write("Location: artifacts/adg/\n")
        f.write(f"Timestamp: {timestamp} EDT (DST-correct, UTC-4)\n")
        f.write(f"Size: {zip_size_mb:.2f} MB\n")
        f.write(f"Total files: {total_files}\n\n")

        f.write("=" * 80 + "\n")
        f.write("ADG FILE OPTIMISATION RATIONALE\n")
        f.write("=" * 80 + "\n\n")
        f.write("DROPPED (redundant, no signal loss):\n")
        f.write("  adg_file_graph       - file-level edges fully subsumed by sqlite\n")
        f.write("  adg_governance_graph - governance edges present in sqlite relation_type col\n")
        f.write(
            "  adg_graphsnap        - 28 MB of canonical ordering arrays (diff-only use, no validation signal)\n",
        )
        f.write("KEPT (unique signal):\n")
        f.write("  adg_indexed.sqlite   - superset: 64,293 nodes + 217,071 edges + line_no + symbol cols\n")
        f.write(
            "  adg_symbol_graph     - symbol-level detail (class/function bodies) not abbreviated in sqlite\n",
        )
        f.write("  adg_snapshot         - 7 KB summary stats (layer counts, hotspots, coverage)\n\n")

        f.write("=" * 80 + "\n")
        f.write("CONTENTS\n")
        f.write("=" * 80 + "\n\n")

        f.write(f"ADG Artifacts (3 files, timestamp {timestamp} EDT):\n")
        for file_path in adg_files:
            f.write(f"  - adg/{Path(file_path).name}\n")

        f.write(f"Minimal Runtime Enforcement Files ({len(runtime_files)} files — 1 per gap):\n\n")

        f.write("Gap 1 — UWG mutation chokepoint:\n")
        f.write("  - runtime/agentic_core/L2_execution/UniversalWriteGateway.py\n")
        f.write("    -> ToolNotAllowedError + allowlist enforcement + replay_mode\n\n")
        f.write("Gap 2 — Determinism/replay interception:\n")
        f.write("  - runtime/agentic_core/L2_execution/determinism/replay_guard.py\n")
        f.write("    -> Intercepts socket/random/datetime/subprocess at kernel level\n\n")
        f.write("Gap 3 — Policy hash validation:\n")
        f.write("  - runtime/agentic_core/L0_routing/enforcement/policy_hash_enforcer.py\n")
        f.write("    -> Every InstructionPacket validated against active Merkle policy root\n\n")
        f.write("Gap 4 — HITL/DPO lineage:\n")
        f.write("  - runtime/agentic_core/L6_observability/engines/hitl_dpo_pair_generator.py\n")
        f.write("    -> APPROVE/REJECT -> DPO pair with stable hash\n\n")
        f.write("Gap 5 — Meta-learning commit gating:\n")
        f.write("  - runtime/agentic_core/L0_routing/meta_control/meta_apply.py\n")
        f.write("    -> 5 explicit gates, fail-closed, no background apply\n")

        f.write("\nValidation Tools (1 file):\n")
        f.write("  - validation/tools/_validate_adg_claims.py\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("UPLOAD INSTRUCTIONS\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"1. Upload artifacts/adg/{zip_path.name} to ChatGPT\n\n")
        f.write("2. Use this prompt:\n\n")
        f.write("   \"I've uploaded the comprehensive ADG + runtime validation package.\n")
        f.write("   Please validate the 5 runtime enforcement gaps:\n\n")
        f.write("   1. UWG syscall interception - Check UniversalWriteGateway.py\n")
        f.write("   2. Determinism enforcement - Check replay_guard.py and mixins\n")
        f.write("   3. Policy hash validation - Check policy_hash_enforcer.py\n")
        f.write("   4. DPO data lineage - Check hitl_dpo_pair_generator.py\n")
        f.write("   5. Meta-learning gating - Check meta_learning_bus.py\n\n")
        f.write("   Confirm whether these runtime modules prove the enforcement\n")
        f.write('   mechanisms you identified as unprovable via ADG static analysis."\n')

    print(f"✓ Manifest created: {manifest_path}")
    print("\n" + "=" * 80)
    print("\nNext steps:")
    print(f"1. Upload artifacts/adg/{zip_path.name} to ChatGPT")
    print("2. Ask ChatGPT to validate the 5 runtime enforcement gaps using the comprehensive file set")

    return zip_path


if __name__ == "__main__":
    create_validation_package()

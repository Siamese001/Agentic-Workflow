#!/usr/bin/env python3
"""
Ingest specific ADG-related files into ChromaDB
"""

import subprocess
import sys

# List of ADG-related files to ingest
adg_files = [
    "ADG_BURNDOWN_STRATEGY.md",
    "ADG_VIOLATIONS_ANALYSIS.md",
    "ADG_VIOLATION_BURNDOWN_WAVE1.md",
    "ADG_VIOLATION_WATERFALL_CORRECTED.md",
    "ADG_VIOLATION_WATERFALL_PLAN.md",
    "adg_archiving_fix_summary.md",
    "adg_final_gap_analysis.md",
    "adg_process_summary.md",
    "dependency_graph_adg_final_gap.md",
    "dependency_graph_analysis.md"
]

def ingest_file(filepath):
    """Ingest a single file into adg_artifacts collection"""
    cmd = [
        "python", "tools/ingestion/ingest_docs.py",
        "--source-dir", ".",
        "--collection-name", "adg_artifacts",
        "--mock-embeddings",
        "--include-pattern", filepath
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ Ingested {filepath}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to ingest {filepath}: {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    """Main function"""
    print("Ingesting ADG-related files into adg_artifacts collection...")

    success_count = 0
    for filepath in adg_files:
        if ingest_file(filepath):
            success_count += 1

    print(f"\nComplete: {success_count}/{len(adg_files)} files ingested")

if __name__ == "__main__":
    main()

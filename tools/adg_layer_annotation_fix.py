#!/usr/bin/env python3
"""ADG Layer Annotation Fix - Add layer comments to unknown modules."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Map directory patterns to layer annotations
LAYER_MAPPING = {
    "agentic_core/L_CONTRACTS/": "L0",
    "agentic_core/case_memory/": "L4",
    "agentic_core/cloud_native/": "L2",
    "agentic_core/core/": "L1",
    "agentic_core/dashboard/": "L3",
    "agentic_core/gateway/": "L2",
    "agentic_core/monitoring/": "L4",
    "agentic_core/planning/": "L3",
    "agentic_core/tracing/": "L4",
    "agentic_core/visualization/": "L3",
}


def infer_layer(path: str) -> str | None:
    """Infer layer from file path."""
    path_lower = path.lower().replace("\\", "/")
    for pattern, layer in LAYER_MAPPING.items():
        if pattern.lower() in path_lower:
            return layer
    return None


def add_layer_to_file(file_path: Path, layer: str) -> bool:
    """Add layer annotation to a Python file."""
    if not file_path.exists():
        return False

    content = file_path.read_text(encoding="utf-8")

    # Check if already has layer annotation
    if "# Layer:" in content:
        return False

    # Add layer annotation at the top after docstring if present
    lines = content.split("\n")

    # Find insertion point (after module docstring or at start)
    insert_idx = 0
    in_docstring = False
    docstring_quote = None

    for i, line in enumerate(lines):
        if i == 0 and line.startswith("#!/"):
            insert_idx = 1
            continue

        stripped = line.strip()

        # Handle docstrings
        if not in_docstring:
            if stripped.startswith('"""') or stripped.startswith("'''"):
                if stripped.count('"""') == 2 or stripped.count("'''") == 2:
                    # Single line docstring
                    insert_idx = i + 1
                else:
                    in_docstring = True
                    docstring_quote = '"""' if '"""' in stripped else "'''"
        else:
            if docstring_quote in stripped:
                in_docstring = False
                insert_idx = i + 1

    # Insert layer annotation
    layer_comment = f"# Layer: {layer}"
    if insert_idx < len(lines) and lines[insert_idx].strip():
        layer_comment += ""  # Will add newline

    lines.insert(insert_idx, layer_comment)

    # Write back
    file_path.write_text("\n".join(lines), encoding="utf-8")
    return True


def main():
    """Run layer fix on current ADG."""
    timestamp = "04012026_2215"

    # Load layer coverage report
    report_path = ROOT / "artifacts" / "adg" / f"layer_coverage_report_{timestamp}.json"

    if not report_path.exists():
        print(f"❌ Report not found: {report_path}")
        sys.exit(1)

    report = json.loads(report_path.read_text())
    unknown_modules = report.get("unknown_modules", [])

    print("=" * 80)
    print("ADG LAYER ANNOTATION FIX")
    print(f"Timestamp: {timestamp}")
    print(f"Unknown modules: {len(unknown_modules)}")
    print("=" * 80)

    fixed_count = 0
    skipped_count = 0
    error_count = 0

    for module in unknown_modules:
        resolved_path = module.get("resolved_path", "")
        if not resolved_path:
            continue

        # Infer layer
        layer = infer_layer(resolved_path)
        if not layer:
            print(f"  ⚠️ Cannot infer layer: {resolved_path}")
            skipped_count += 1
            continue

        # Handle both file paths and symbol paths (e.g., file.py::ClassName)
        file_part = resolved_path.split("::")[0]
        file_path = ROOT / file_part

        try:
            if add_layer_to_file(file_path, layer):
                print(f"  ✅ Added # Layer: {layer} to {file_part}")
                fixed_count += 1
            else:
                if file_path.exists():
                    print(f"  ⏭️ Skipped (already has layer or no file): {file_part}")
                else:
                    print(f"  ⚠️ File not found: {file_path}")
                skipped_count += 1
        except Exception as e:
            print(f"  ❌ Error processing {file_part}: {e}")
            error_count += 1

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Fixed: {fixed_count}")
    print(f"Skipped: {skipped_count}")
    print(f"Errors: {error_count}")

    if fixed_count > 0:
        print("\n📝 Next step: Regenerate ADG to pick up layer annotations")
        print("   python tools/generate_full_adg.py")


if __name__ == "__main__":
    main()

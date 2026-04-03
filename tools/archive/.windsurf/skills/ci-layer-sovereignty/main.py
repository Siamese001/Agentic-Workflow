#!/usr/bin/env python3
"""
Windsurf Skill: CI Layer Sovereignty
Enforces layer sovereignty import checking.
"""

import sys
from pathlib import Path

# guardian: allow-silent-swallower -- Exception handling for CI script execution
# guardian: allow-magic-configuration -- CI script path and argument configuration


def validate_layer_sovereignty(file_path: str) -> tuple[bool, str, str]:
    """Simple layer sovereignty validation for single file."""
    path = Path(file_path)

    # Convert to absolute path if needed
    if not path.is_absolute():
        path = Path.cwd() / path

    # Only check Python files in agentic_core/ or apps_*/ directories
    if not (path.suffix == '.py' and
            (str(path).startswith(str(Path.cwd() / "agentic_core")) or
             any(str(path).startswith(str(Path.cwd() / d)) for d in Path.cwd().glob("apps_*")))):
        return True, "File not in layer sovereignty scope", ""

    try:
        content = path.read_text(encoding='utf-8')
        lines = content.split('\n')

        # Determine source layer
        source_layer = None
        relative_path = path.relative_to(Path.cwd())
        path_parts = relative_path.parts

        if 'agentic_core' in path_parts:
            idx = path_parts.index('agentic_core')
            if idx + 1 < len(path_parts):
                layer_part = path_parts[idx + 1]
                # Extract L1 from L1_cognition, L2 from L2_execution, etc.
                if '_' in layer_part:
                    source_layer = layer_part.split('_')[0]
                elif layer_part.startswith('L'):
                    source_layer = layer_part
        elif any(p.startswith('apps_') for p in path_parts):
            source_layer = 'apps'

        if not source_layer:
            return True, "Could not determine layer", ""

        violations = []

        for line_num, line in enumerate(lines, 1):
            line = line.strip()

            # Check import statements
            if line.startswith('from ') or line.startswith('import '):
                # Extract the import path
                if line.startswith('from '):
                    parts = line.split()
                    if len(parts) >= 2:
                        import_path = parts[1]
                    else:
                        continue
                else:
                    parts = line.split()
                    if len(parts) >= 2:
                        import_path = parts[1]
                    else:
                        continue

                # Check for agentic_core imports
                if 'agentic_core.L' in import_path:
                    # Extract target layer
                    try:
                        agentic_idx = import_path.index('agentic_core.L')
                        remaining = import_path[agentic_idx + len('agentic_core.L'):]
                        # Extract just the L2 from L2_execution
                        layer_part = remaining.split('_')[0] if '_' in remaining else remaining.split('.')[0]
                        target_layer = f"L{layer_part}"

                        # Check violation rules
                        if source_layer == 'L1' and target_layer in ['L2', 'L3', 'L4', 'L5', 'L6']:
                            violations.append(f"Line {line_num}: L1 importing from {target_layer}")
                        elif source_layer == 'L2' and target_layer in ['L5', 'L6']:
                            violations.append(f"Line {line_num}: L2 importing from {target_layer}")
                        elif source_layer == 'L3' and target_layer in ['L5', 'L6']:
                            violations.append(f"Line {line_num}: L3 importing from {target_layer}")
                        elif source_layer == 'apps' and target_layer.startswith('L'):
                            violations.append(f"Line {line_num}: apps importing from {target_layer}")
                    except (IndexError, ValueError):
                        continue

        if violations:
            return False, "Layer sovereignty violations found:\n" + "\n".join(violations), ""

        return True, "No layer sovereignty violations", ""

    except Exception as e:
        return False, "", f"Error checking layer sovereignty: {e}"


def main():
    """Main entry point for the skill."""
    if len(sys.argv) != 2:
        print("Usage: python main.py <file>")
        print("Enforces layer sovereignty import checking in the specified file")
        sys.exit(1)

    # Health check
    if len(sys.argv) == 2 and sys.argv[1] == "--health-check":
        print("[PASS] CI layer sovereignty health check")
        sys.exit(0)

    file_path = sys.argv[1]

    # Check if file exists
    if not Path(file_path).exists():
        print(f"[ERROR] File not found: {file_path}")
        sys.exit(1)

    success, stdout, stderr = validate_layer_sovereignty(file_path)

    if success:
        print("[PASS] Layer sovereignty validation passed")
        if stdout:
            print(stdout)
        sys.exit(0)
    else:
        print("[FAIL] Layer sovereignty validation failed")
        if stdout:
            print(stdout)
        if stderr:
            print(f"Errors: {stderr}")
        print("\n💡 Layer sovereignty requirements:")
        print("  1. L1 must NOT import L2, L3, L4, L5, L6")
        print("  2. L2 must NOT import L5, L6")
        print("  3. L3 must NOT import L5, L6")
        print("  4. apps_* must NOT import directly from agentic_core.L* layers")
        print("  5. Lower layers can import from higher layers")
        sys.exit(1)


if __name__ == "__main__":
    main()

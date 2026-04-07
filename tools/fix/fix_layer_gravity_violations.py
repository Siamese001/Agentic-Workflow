#!/usr/bin/env python3
"""
Fix layer gravity violations by creating L_CONTRACTS layer.

Problem: 817 L0-L6 modules importing from L_RUNTIME layer
Solution: Move lifecycle_trace_contract to L_CONTRACTS layer for cross-layer interfaces
"""

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class LayerGravityFixer:
    """Fix layer gravity violations by creating L_CONTRACTS layer."""

    def __init__(self):
        self.contracts_dir = PROJECT_ROOT / "agentic_core" / "L_CONTRACTS"
        self.violations_fixed = 0
        self.errors = 0

    def create_contracts_layer(self):
        """Create the L_CONTRACTS layer directory structure."""
        print("🏗️  Creating L_CONTRACTS layer...")

        self.contracts_dir.mkdir(exist_ok=True)

        # Create __init__.py
        init_file = self.contracts_dir / "__init__.py"
        if not init_file.exists():
            init_file.write_text('"""L_CONTRACTS - Cross-layer interfaces and contracts."""\n')

        print(f"✅ Created L_CONTRACTS layer at: {self.contracts_dir}")

    def move_lifecycle_contract(self):
        """Move lifecycle_trace_contract to L_CONTRACTS layer."""
        print("📦 Moving lifecycle_trace_contract to L_CONTRACTS...")

        # Source file
        source = PROJECT_ROOT / "agentic_core" / "runtime" / "lifecycle_trace_contract.py"

        # Destination file
        dest = self.contracts_dir / "lifecycle_trace_contract.py"

        if source.exists() and not dest.exists():
            # Read source content
            content = source.read_text(encoding='utf-8')

            # Update docstring to reflect new location
            content = content.replace(
                'agentic_core/runtime/lifecycle_trace_contract.py',
                'agentic_core/L_CONTRACTS/lifecycle_trace_contract.py',
            )

            # Write to destination
            dest.write_text(content, encoding='utf-8')

            print("✅ Moved lifecycle_trace_contract to L_CONTRACTS")
            return True
        elif dest.exists():
            print("⚠️  lifecycle_trace_contract already exists in L_CONTRACTS")
            return True
        else:
            print(f"❌ Source file not found: {source}")
            return False

    def fix_import_statements(self):
        """Fix all import statements that reference the old location."""
        print("🔧 Fixing import statements...")

        # Pattern to find imports from old location
        patterns = [
            r'from agentic_core.runtime.contracts.lifecycle_trace_contract import',
            r'import agentic_core.runtime.lifecycle_trace_contract',
            r'from agentic_core\.runtime import lifecycle_trace_contract',
        ]

        # Find all Python files
        python_files = list(PROJECT_ROOT.rglob("*.py"))

        # Skip certain directories
        skip_dirs = {'.git', '__pycache__', '.pytest_cache', 'venv', '.venv', 'node_modules', 'archives'}

        for file_path in python_files:
            if any(skip_dir in file_path.parts for skip_dir in skip_dirs):
                continue

            self._fix_file_imports(file_path, patterns)

        print(f"✅ Fixed {self.violations_fixed} import statements")
        if self.errors > 0:
            print(f"⚠️  {self.errors} files had errors")

    def _fix_file_imports(self, file_path: Path, patterns: list):
        """Fix imports in a single file."""
        try:
            content = file_path.read_text(encoding='utf-8')
            original_content = content

            # Fix each pattern
            for pattern in patterns:
                # Replace with L_CONTRACTS location
                new_content = re.sub(
                    pattern,
                    pattern.replace('runtime', 'L_CONTRACTS'),
                    content,
                )
                content = new_content

            # Write back if changed
            if content != original_content:
                file_path.write_text(content, encoding='utf-8')
                self.violations_fixed += 1

                if self.violations_fixed % 100 == 0:
                    print(f"  Fixed {self.violations_fixed} files...")

        except Exception as e:
            self.errors += 1
            print(f"  Error fixing {file_path}: {e}")

    def update_layer_assignments(self):
        """Update layer assignments in ADG scanner."""
        print("🔄 Updating layer assignments...")

        # Update static scanner to recognize L_CONTRACTS
        scanner_file = PROJECT_ROOT / "agentic_core" / "adg" / "extraction" / "static_scanner.py"

        if scanner_file.exists():
            content = scanner_file.read_text(encoding='utf-8')

            # Look for layer assignment logic
            if '_infer_layer' in content:
                # Add L_CONTRACTS to layer inference
                new_content = content.replace(
                    'elif "tools" in rel_path:\n        return "TOOLS"',
                    'elif "tools" in rel_path:\n        return "TOOLS"\n    elif "L_CONTRACTS" in rel_path:\n        return "L_CONTRACTS"',
                )

                if new_content != content:
                    scanner_file.write_text(new_content, encoding='utf-8')
                    print("✅ Updated layer assignments in static scanner")

            # Look for layer constants
            if 'L_RUNTIME' in content:
                # Add L_CONTRACTS to layer definitions
                new_content = content.replace(
                    'L_RUNTIME',
                    'L_CONTRACTS\nL_RUNTIME',
                )

                if new_content != content:
                    scanner_file.write_text(new_content, encoding='utf-8')
                    print("✅ Added L_CONTRACTS to layer definitions")

    def verify_fixes(self):
        """Verify that layer violations are fixed."""
        print("✅ Verifying fixes...")

        # Check that L_CONTRACTS directory exists
        if not self.contracts_dir.exists():
            print("❌ L_CONTRACTS directory not created")
            return False

        # Check that lifecycle_trace_contract is in L_CONTRACTS
        contract_file = self.contracts_dir / "lifecycle_trace_contract.py"
        if not contract_file.exists():
            print("❌ lifecycle_trace_contract not moved to L_CONTRACTS")
            return False

        print("✅ Layer gravity fixes completed:")
        print("  - L_CONTRACTS layer created")
        print("  - lifecycle_trace_contract moved")
        print(f"  - {self.violations_fixed} import statements fixed")

        return True


def main():
    """Main entry point."""
    print("=" * 80)
    print("LAYER GRAVITY VIOLATIONS FIXER")
    print("=" * 80)
    print("Fixing 817 layer gravity violations...")
    print("Creating L_CONTRACTS layer for cross-layer interfaces")
    print("=" * 80)

    fixer = LayerGravityFixer()

    # Step 1: Create L_CONTRACTS layer
    fixer.create_contracts_layer()

    # Step 2: Move lifecycle_trace_contract
    if not fixer.move_lifecycle_contract():
        print("❌ Failed to move lifecycle_trace_contract")
        return

    # Step 3: Fix import statements
    fixer.fix_import_statements()

    # Step 4: Update layer assignments
    fixer.update_layer_assignments()

    # Step 5: Verify fixes
    if fixer.verify_fixes():
        print("\n🎉 LAYER GRAVITY FIXES COMPLETED SUCCESSFULLY!")
        print("Next step: Regenerate ADG to verify 0 layer violations")
    else:
        print("\n❌ LAYER GRAVITY FIXES FAILED")

    print("=" * 80)


if __name__ == "__main__":
    main()

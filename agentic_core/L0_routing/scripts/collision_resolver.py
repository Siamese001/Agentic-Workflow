r"""
File: scripts/CollisionResolver.py
Path: C:\Git\Agentic-Workflow\scripts/CollisionResolver.py
Status: Post-Migration Triage Tool
Rationale:
    The automated fixer cannot resolve collisions where two files want the same name.
    This tool finds these specific cases and reports them for manual adjudication.
"""

import ast
import sys
from collections import defaultdict
from pathlib import Path

# SSOT Integration
from agentic_core.L0_routing.enforcement.mutation_prohibition import (
    safe_os_remove,
)
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)

try:
    from agentic_core.utils.ssot_discovery_validator import get_python_files
except ImportError:

    def get_python_files(root: Path):
        return list(root.rglob("*.py"))


class CollisionResolver:
    def __init__(self, root: Path):
        self.root = root
        self.collisions: dict[str, list[Path]] = defaultdict(list)
        self.skip_dirs = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES

    def _get_target_name(self, path: Path) -> str | None:
        """Determine what name this file SHOULD have based on AST analysis."""
        if path.name in ["__init__.py", "__main__.py", "conftest.py"]:
            return None

        try:
            content = path.read_text(encoding="utf-8")
            tree = ast.parse(content)
        except:
            return None

        classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]

        if not classes:
            # Utility file - should be snake_case, no collision concern
            return None

        # Find primary class (matching stem or first)
        primary = classes[0]
        stem_clean = path.stem.replace("_", "").lower()

        for cls in classes:
            if cls.lower() == stem_clean:
                primary = cls
                break

        # Check if it's an Agent
        is_agent = any(c.endswith("Agent") for c in classes)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    if isinstance(base, ast.Name) and "Agent" in base.id:
                        is_agent = True
                    elif isinstance(base, ast.Attribute) and "Agent" in base.attr:
                        is_agent = True

        target = primary
        if is_agent and not target.endswith("Agent"):
            target += "Agent"

        return f"{target}.py"

    def find_collisions(self):
        """Find files that want the same target name within the same directory."""
        print(f"Scanning {self.root} for collision candidates...")

        # Group by directory -> target_name -> [source files]
        dir_targets: dict[Path, dict[str, list[Path]]] = defaultdict(lambda: defaultdict(list))

        for path in get_python_files(self.root):
            # Skip excluded directories
            if any(skip in path.parts for skip in self.skip_dirs):
                continue

            target = self._get_target_name(path)
            if target and target != path.name:
                # This file wants to rename to 'target'
                dir_targets[path.parent][target].append(path)

        # Now find actual collisions (multiple files wanting same target, or target already exists)
        for directory, targets in dir_targets.items():
            for target_name, sources in targets.items():
                target_path = directory / target_name

                # Collision case 1: Target file already exists
                if target_path.exists() and target_path not in sources:
                    key = str(target_path)
                    self.collisions[key].append(target_path)  # The existing file
                    for src in sources:
                        if src not in self.collisions[key]:
                            self.collisions[key].append(src)

                # Collision case 2: Multiple files want the same target
                elif len(sources) > 1:
                    key = str(target_path)
                    for src in sources:
                        if src not in self.collisions[key]:
                            self.collisions[key].append(src)

    def report(self):
        """Generate a detailed collision report."""
        if not self.collisions:
            print("\n✅ No collision violations found. Repository is clean.")
            return 0

        print(f"\n⚠️  Found {len(self.collisions)} collision groups requiring manual resolution.\n")
        print("=" * 80)

        for i, (target, sources) in enumerate(self.collisions.items(), 1):
            target_path = Path(target)
            print(f"\n[{i}] TARGET: {target_path.name}")
            print(f"    Directory: {target_path.parent.relative_to(self.root)}")
            print("    Contenders:")

            for src in sources:
                try:
                    size = src.stat().st_size
                    # Get first class name for context
                    content = src.read_text(encoding="utf-8")
                    tree = ast.parse(content)
                    classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
                    class_info = f"[Classes: {', '.join(classes[:3])}]" if classes else "[No classes]"
                # guardian: allow-silent-swallow
                except:
                    size = 0
                    class_info = "[Parse error]"

                marker = "✓ EXISTS" if src.name == target_path.name else "→ WANTS"
                print(f"      {marker}: {src.name} ({size} bytes) {class_info}")

        print("\n" + "=" * 80)
        print("\nRESOLUTION OPTIONS:")
        print("  1. Manually merge/delete duplicate files")
        print("  2. Rename one file's primary class to create a unique target")
        print("  3. Move one file to a different directory")
        print("=" * 80)

        return len(self.collisions)

    def interactive_resolve(self):
        """Interactive mode for resolving collisions one by one."""
        if not self.collisions:
            print("\n✅ No collisions to resolve.")
            return

        print("\n🔧 INTERACTIVE COLLISION RESOLVER")
        print(f"   {len(self.collisions)} groups to process")
        print("   Commands: [1-N] Keep file N, [S] Skip, [Q] Quit\n")

        resolved = 0
        for target, sources in list(self.collisions.items()):
            target_path = Path(target)

            print("\n" + "=" * 60)
            print(f"TARGET: {target_path.name}")
            print(f"DIR: {target_path.parent}")
            print("-" * 60)

            for i, src in enumerate(sources, 1):
                size = src.stat().st_size if src.exists() else 0
                status = "EXISTS" if src.name == target_path.name else "RENAME"
                print(f"  [{i}] {src.name} ({size} bytes) [{status}]")

            choice = input("\nKeep which file? [1-N/S/Q]: ").strip().upper()

            if choice == "Q":
                print("Exiting interactive mode.")
                break
            elif choice == "S" or not choice:
                print("Skipped.")
                continue
            elif choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(sources):
                    winner = sources[idx]
                    print(f"\n  KEEPING: {winner.name}")

                    for i, src in enumerate(sources):
                        if i != idx and src.exists():
                            print(f"  DELETING: {src.name}")
                            safe_os_remove(src, layer="L0")

                    # Rename winner to target if needed
                    if winner.name != target_path.name and winner.exists():
                        print(f"  RENAMING: {winner.name} -> {target_path.name}")
                        winner.rename(target_path)

                    resolved += 1
                    print("  ✓ Resolved")

        print(f"\n✅ Resolved {resolved} collision groups.")


if __name__ == "__main__":
    root = Path(__file__).parent.parent
    resolver = CollisionResolver(root)

    print("=" * 60)
    print("SOVEREIGNTY COLLISION RESOLVER")
    print("=" * 60)

    resolver.find_collisions()

    if "--interactive" in sys.argv or "-i" in sys.argv:
        resolver.interactive_resolve()
    else:
        count = resolver.report()
        if count > 0:
            print("\nRun with --interactive (-i) to resolve collisions one by one.")
        sys.exit(count)

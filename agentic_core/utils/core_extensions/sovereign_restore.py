import ast
import os
from pathlib import Path

ROOT = Path("C:/Git/Agentic-Workflow")
CORE = ROOT / "agentic_core"

def get_class_names(file_path):
    """Statically parse class names to avoid execution/circular imports."""
    classes = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            node = ast.parse(f.read())
        for n in node.body:
            if isinstance(n, ast.ClassDef):
                classes.append(n.name)
    except Exception as e:
        print(f"  [!] AST Error {file_path.name}: {e}")
    return classes

def sovereign_restore():
    print("[*] STARTING SOVEREIGN RESTORE (REBUILDING EXPORTS)...")
    
    # We only care about the L-layers (Depth 2)
    for layer_dir in CORE.iterdir():
        if not layer_dir.is_dir() or not layer_dir.name.startswith("L"):
            continue
            
        print(f"\n[LAYER] {layer_dir.name}")
        exports = []
        import_lines = []

        # Scan for Depth 4 files
        for stage_dir in layer_dir.iterdir():
            if not stage_dir.is_dir(): continue
            
            for py_file in stage_dir.glob("*.py"):
                if py_file.name == "__init__.py": continue
                
                classes = get_class_names(py_file)
                if classes:
                    # Create relative import: from .S1_stage.file import Class
                    module_path = f".{stage_dir.name}.{py_file.stem}"
                    import_lines.append(f"from {module_path} import {', '.join(classes)}")
                    exports.extend(classes)

        # Build the Layer-level __init__.py
        init_path = layer_dir / "__init__.py"
        with open(init_path, "w", encoding="utf-8") as f:
            f.write(f'"""Sovereign Layer: {layer_dir.name}"""\n\n')
            if import_lines:
                f.write("\n".join(import_lines) + "\n\n")
                f.write(f"__all__ = {exports}\n")
        
        print(f"  [✓] Restored {len(exports)} exports to {init_path.relative_to(ROOT)}")

    # Final touch: The Root agentic_core/__init__.py
    # This must remain near-empty to stop the Snake Loop.
    with open(CORE / "__init__.py", "w", encoding="utf-8") as f:
        f.write('"""agentic_core: Sovereign AI Architecture"""\n')
        f.write('# Root exports disabled to prevent circular death loops.\n')
        f.write('# Use: from agentic_core.L_layer import Component\n')
    
    print("\n[OK] SOVEREIGN RESTORE COMPLETE.")

if __name__ == "__main__":
    sovereign_restore()

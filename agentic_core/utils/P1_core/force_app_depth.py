import os
import shutil
from pathlib import Path

# --- CONFIGURATION ---
ROOT = Path("C:/Git/Agentic-Workflow")
CORE = ROOT / "agentic_core"
APPS = [ROOT / "apps_lic", ROOT / "apps_rg"]

def force_app_depth():
    print("[*] FORCING DEPTH-4 ON TERRITORIES...")

    for app_path in APPS:
        if not app_path.exists(): continue
        print(f"\n[HARDENING] {app_path.name}...")

        # 1. RESCUE THE ENGINES
        for engine_folder in app_path.glob("*_engine"):
            dest = CORE / "L2_execution" / "P3_engines" / engine_folder.name
            dest.mkdir(parents=True, exist_ok=True)
            
            for item in engine_folder.iterdir():
                # Avoid moving __pycache__ or system files
                if item.is_dir() and item.name.startswith("__"): continue
                shutil.move(str(item), str(dest / item.name))
            
            # Clean up empty engine shell
            try: shutil.rmtree(str(engine_folder))
            except: pass
            print(f"  [✓] ENGINE EXTRICATED: {engine_folder.name} -> Core/L2_execution/P3_engines")

        # 2. ANNEX THE L-LAYERS
        for layer_folder in app_path.glob("L*"):
            # Skip if it's a file, not a directory
            if not layer_folder.is_dir():
                continue
            
            # Map L0 to L1 or appropriate core layer
            layer_map = {"L0": "L1_cognition", "L1": "L1_cognition", "L2": "L2_execution", "L3": "L3_orchestration"}
            target_layer = layer_map.get(layer_folder.name, layer_folder.name)
            
            dest = CORE / target_layer / "P1_core"
            dest.mkdir(parents=True, exist_ok=True)
            
            for item in layer_folder.iterdir():
                if item.is_dir() and item.name.startswith("__"): continue
                shutil.move(str(item), str(dest / item.name))
            
            try: shutil.rmtree(str(layer_folder))
            except: pass
            print(f"  [✓] LAYER ANNEXED: {layer_folder.name} -> Core/{target_layer}/P1_core")

        # 3. FORCE DEPTH-4 MANDATE
        app_p1 = app_path / "P1_core"
        app_p1.mkdir(parents=True, exist_ok=True)
        if not (app_p1 / "__init__.py").exists():
            (app_p1 / "__init__.py").write_text('"""App Core Implementation"""\n')

        # Move all floating .py files into P1_core
        for py_file in app_path.glob("*.py"):
            if py_file.name == "__init__.py": continue
            # Avoid the lock script itself if it's in the root
            if "sovereign_lock" in py_file.name: continue
            
            shutil.move(str(py_file), str(app_p1 / py_file.name))
            print(f"  [!] DEPTH CORRECTION: {py_file.name} -> {app_path.name}/P1_core")

if __name__ == "__main__":
    force_app_depth()

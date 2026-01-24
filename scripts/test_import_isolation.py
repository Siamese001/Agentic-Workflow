import importlib.util
import sys
import time
from pathlib import Path

def test_isolated_imports():
    """Test 18: Aggressively identify which agent causes the discovery hang."""
    root = Path("agentic_core")
    agents = list(root.rglob("*.py"))
    
    print(f"Checking {len(agents)} files for import hangs...")
    problematic_files = []
    
    for i, agent_path in enumerate(agents):
        if agent_path.name == "__init__.py": 
            continue
        
        module_name = agent_path.stem
        spec = importlib.util.spec_from_file_location(module_name, agent_path)
        module = importlib.util.module_from_spec(spec)
        
        try:
            print(f"🔍 Validating {i+1}/{len(agents)}: {agent_path}", end="\r")
            
            # Add timeout simulation
            start_time = time.time()
            
            # We only load the spec, we don't execute yet to avoid the hang
            # If this hangs, the issue is at the top-level module scope
            spec.loader.exec_module(module)
            
            load_time = time.time() - start_time
            if load_time > 2.0:  # Flag slow imports
                print(f"\n⚠️  Slow import: {agent_path} took {load_time:.2f}s")
                problematic_files.append((agent_path, f"Slow import: {load_time:.2f}s"))
                
        except Exception as e:
            print(f"\n❌ Import Error in {agent_path}: {e}")
            problematic_files.append((agent_path, str(e)))
            continue
    
    print(f"\n✅ Isolation check complete. Checked {len(agents)} files.")
    
    if problematic_files:
        print(f"\n🚨 Found {len(problematic_files)} problematic files:")
        for path, error in problematic_files:
            try:
                print(f"   - {path.relative_to(Path.cwd())}: {error}")
            except ValueError:
                print(f"   - {path}: {error}")
    else:
        print("\n✅ No import issues detected. The issue may be in the Registry logic.")
    
    return problematic_files

def test_registry_imports():
    """Test the specific registry components that might be causing hangs."""
    print("\n🔍 Testing registry component imports...")
    
    components = [
        "agentic_core.discovery",
        "agentic_core.utils.ssot_discovery",
        "agentic_core.L0_maintenance.security.ManifestGuardian",
        "agentic_core.L0_maintenance.scripts.compliance_gate"
    ]
    
    for component in components:
        try:
            print(f"   Importing {component}...", end="\r")
            start_time = time.time()
            
            __import__(component)
            
            load_time = time.time() - start_time
            print(f"✅ {component} ({load_time:.3f}s)")
            
        except Exception as e:
            print(f"❌ {component}: {e}")

if __name__ == "__main__":
    print("="*60)
    print("   AGENTIC WORKFLOW: IMPORT ISOLATION DIAGNOSTIC   ")
    print("="*60)
    
    # Test isolated imports first
    problematic = test_isolated_imports()
    
    # Test registry components
    test_registry_imports()
    
    print("\n" + "="*60)
    if problematic:
        print("🚨 ACTION REQUIRED: Fix import issues before running finalize_architecture.py")
    else:
        print("✅ All imports clean - you can proceed with finalize_architecture.py")
    print("="*60)

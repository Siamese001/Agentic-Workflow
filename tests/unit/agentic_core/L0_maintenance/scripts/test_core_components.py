import sys
import time
from pathlib import Path


def test_core_components():
    """Test only the core components needed for finalize_architecture.py"""
    print("🔍 Testing core components for finalize_architecture.py...")

    core_components = [
        ("agentic_core.discovery", "AgentRegistry"),
        ("agentic_core.utils.ssot_discovery", "get_python_files"),
        ("agentic_core.L0_maintenance.security.ManifestGuardian", "ManifestGuardian"),
    ]

    success_count = 0
    for module_name, class_name in core_components:
        try:
            print(f"   Importing {module_name}...", end="\r")
            start_time = time.time()

            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)  # Verify the class exists

            load_time = time.time() - start_time
            print(f"✅ {module_name}.{class_name} ({load_time:.3f}s)")
            success_count += 1

        except Exception as e:
            print(f"❌ {module_name}.{class_name}: {e}")

    return success_count == len(core_components)


def test_simple_discovery():
    """Test a simple file discovery without full registry"""
    print("\n🔍 Testing simple file discovery...")

    try:
        from agentic_core.utils.ssot_discovery_validator import get_python_files

        start_time = time.time()

        files = get_python_files(Path("agentic_core"))
        load_time = time.time() - start_time

        print(f"✅ Found {len(files)} Python files ({load_time:.3f}s)")
        return True

    except Exception as e:
        print(f"❌ Simple discovery failed: {e}")
        return False


def test_manifest_guardian():
    """Test ManifestGuardian functionality"""
    print("\n🔍 Testing ManifestGuardian...")

    try:
        import json
        import os
        import tempfile

        # Create temp environment
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)

            # Create test manifest
            manifest = {"project": "test", "version": "1.0"}
            with open("manifest.json", "w") as f:
                json.dump(manifest, f)

            # Test ManifestGuardian
            sys.path.insert(0, "c:/Git/Agentic-Workflow")
            from agentic_core.L0_maintenance.security.ManifestGuardian import ManifestGuardian

            start_time = time.time()
            checksum = ManifestGuardian.seal_manifest()
            integrity = ManifestGuardian.verify_integrity()
            load_time = time.time() - start_time

            print(f"✅ ManifestGuardian working ({load_time:.3f}s)")
            print(f"   Checksum: {checksum[:8]}...")
            print(f"   Integrity: {integrity}")

            return True

    except Exception as e:
        print(f"❌ ManifestGuardian failed: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("   AGENTIC WORKFLOW: CORE COMPONENT DIAGNOSTIC   ")
    print("=" * 60)

    # Test core components
    core_ok = test_core_components()

    # Test simple discovery
    discovery_ok = test_simple_discovery()

    # Test ManifestGuardian
    guardian_ok = test_manifest_guardian()

    print("\n" + "=" * 60)
    print("RESULTS:")
    print(f"   Core Components: {'✅' if core_ok else '❌'}")
    print(f"   File Discovery:   {'✅' if discovery_ok else '❌'}")
    print(f"   ManifestGuardian: {'✅' if guardian_ok else '❌'}")

    if core_ok and discovery_ok and guardian_ok:
        print("\n✅ All core components working - finalize_architecture.py should run!")
    else:
        print("\n🚨 Issues detected - finalize_architecture.py may fail")

    print("=" * 60)

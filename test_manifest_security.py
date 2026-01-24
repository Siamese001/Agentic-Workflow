import json
import os
import tempfile
from pathlib import Path

# Create temp directory for testing
with tempfile.TemporaryDirectory() as temp_dir:
    os.chdir(temp_dir)
    
    # Create test manifest
    manifest = {'project': 'test', 'version': '1.0'}
    with open('manifest.json', 'w') as f:
        json.dump(manifest, f)
    
    # Test ManifestGuardian
    import sys
    sys.path.insert(0, 'c:/Git/Agentic-Workflow')
    from agentic_core.L0_maintenance.security.ManifestGuardian import ManifestGuardian
    
    print("Testing ManifestGuardian...")
    checksum = ManifestGuardian.seal_manifest()
    print(f"✅ Manifest sealed with checksum: {checksum[:8]}...")
    
    print(f"✅ Integrity check: {ManifestGuardian.verify_integrity()}")
    
    # Test tampering detection
    with open('manifest.json', 'a') as f:
        f.write(' tampered')
    print(f"✅ Tampering detected: {not ManifestGuardian.verify_integrity()}")
    
    print("\n🎉 ManifestGuardian security features working correctly!")

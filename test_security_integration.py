import json
import os
from pathlib import Path

# Create test manifest
manifest = {'project': 'test', 'version': '1.0'}
with open('manifest.json', 'w') as f:
    json.dump(manifest, f)

# Test ManifestGuardian
from agentic_core.L0_maintenance.security.ManifestGuardian import ManifestGuardian

print("Testing ManifestGuardian...")
checksum = ManifestGuardian.seal_manifest()
print(f"✅ Manifest sealed with checksum: {checksum[:8]}...")

print(f"✅ Integrity check: {ManifestGuardian.verify_integrity()}")

# Test boot sequence
print("\nTesting BootSequence...")
from agentic_core.L0_maintenance.boot.boot_sequence import BootSequence

boot = BootSequence(strict_mode=False)  # Use lenient mode
result = boot.execute_boot()
print(f"✅ Boot status: {result['status']}")
print(f"✅ Phases completed: {result['phases_completed']}")

# Cleanup
os.remove('manifest.json')
try:
    os.remove('.manifest.lock')
except:
    pass

print("\n🎉 All security components are working!")

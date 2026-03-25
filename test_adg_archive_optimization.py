#!/usr/bin/env python3
"""Test script to verify ADG archive optimization."""

import os
import sys
import tempfile
import zipfile
from pathlib import Path
from datetime import datetime

# Add project root to path
ROOT = Path(__file__).resolve().parents[0]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

def test_adg_archive_optimization():
    """Test that ADG archive only stores aggregate zip files."""
    
    # Create a temporary directory to simulate ADG artifacts
    with tempfile.TemporaryDirectory() as temp_dir:
        adg_dir = Path(temp_dir) / "adg"
        adg_dir.mkdir()
        
        # Create mock ADG artifacts (individual files)
        timestamp = datetime.now().strftime("%m%d%Y_%H%M")
        mock_files = [
            f"adg_snapshot_{timestamp}.json",
            f"adg_indexed_{timestamp}.sqlite", 
            f"adg_file_graph_{timestamp}.json",
            f"adg_symbol_graph_{timestamp}.json",
            f"adg_governance_graph_{timestamp}.json",
            f"layer_coverage_report_{timestamp}.json",
        ]
        
        # Create mock individual files
        for filename in mock_files:
            file_path = adg_dir / filename
            file_path.write_text(f"Mock content for {filename}")
        
        # Create mock zip file (aggregate)
        zip_path = adg_dir / f"adg_run_{timestamp}.zip"
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for filename in mock_files:
                zf.write(adg_dir / filename, f"adg/{filename}")
        
        print(f"✅ Created test environment with {len(mock_files)} individual files + 1 zip file")
        
        # Import and test the archive function
        try:
            from tools.generate_full_adg import _archive_old_artifacts
            
            # Run archive function with keep_runs=0 (should archive everything)
            print("🔄 Testing archive function...")
            _archive_old_artifacts(adg_dir, timestamp, keep_runs=0)
            
            # Check results
            archive_dir = adg_dir / "_archive"
            if archive_dir.exists():
                archived_files = list(archive_dir.rglob("*"))
                print(f"📦 Archive directory contains {len(archived_files)} files")
                
                # Should only have the compressed zip file, not individual files
                gz_files = [f for f in archived_files if f.name.endswith('.gz')]
                zip_gz_files = [f for f in gz_files if 'adg_run_' in f.name]
                individual_gz_files = [f for f in gz_files if 'adg_run_' not in f.name]
                
                print(f"  - Compressed zip files: {len(zip_gz_files)}")
                print(f"  - Compressed individual files: {len(individual_gz_files)}")
                
                if len(zip_gz_files) > 0 and len(individual_gz_files) == 0:
                    print("✅ SUCCESS: Only aggregate zip files are archived")
                    return True
                else:
                    print("❌ FAILURE: Individual files are still being archived")
                    return False
            else:
                print("❌ FAILURE: No archive directory created")
                return False
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            return False

def main():
    """Run the ADG archive optimization test."""
    print("🧪 Testing ADG Archive Optimization")
    print("=" * 50)
    
    success = test_adg_archive_optimization()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ ADG archive optimization test PASSED")
        print("📝 Summary: Only aggregate zip files are stored in archive")
        print("🗑️  Individual files are deleted instead of being archived")
    else:
        print("❌ ADG archive optimization test FAILED")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())

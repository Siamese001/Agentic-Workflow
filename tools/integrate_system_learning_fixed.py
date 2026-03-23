#!/usr/bin/env python3
"""
Integrate System Learning Components with Continuous Learning Pipeline
Actually modify the system_learning files to use the continuous learning pipeline
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import re

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

print("=" * 80)
print("INTEGRATING SYSTEM LEARNING COMPONENTS")
print("=" * 80)
print(f"Repository: {ROOT}")
print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

class SystemLearningIntegrator:
    """Integrate system_learning components with continuous learning pipeline."""
    
    def __init__(self):
        self.system_learning_dir = ROOT / "system_learning"
        self.integration_stats = {
            "total_components": 0,
            "integrated_components": 0,
            "failed_components": 0,
            "modifications": {}
        }
    
    def integrate_all_components(self):
        """Integrate all system_learning components."""
        print("\n🔧 INTEGRATING SYSTEM_LEARNING COMPONENTS")
        print("=" * 60)
        
        # Components to integrate
        components = {
            "stores": [
                "activator.py",
                "config_provider.py", 
                "telemetry_store.py",
                "version_store.py"
            ],
            "adapters": [
                "l1_meta_adapter.py",
                "l4_meta_prior_provider.py",
                "system_learning_memory_bridge.py"
            ],
            "engines": [
                "embedding_engine.py",
                "arbitration_engine.py", 
                "confidence_engine.py"
            ],
            "pipelines": [
                "meta_learning_pipeline.py",
                "live_run_pipeline_adapter.py"
            ]
        }
        
        for component_type, files in components.items():
            print(f"\n📁 {component_type.upper()}:")
            component_dir = self.system_learning_dir / component_type
            
            if not component_dir.exists():
                print(f"  ❌ Directory not found: {component_type}")
                continue
            
            for file_name in files:
                file_path = component_dir / file_name
                if file_path.exists():
                    self.integration_stats["total_components"] += 1
                    
                    try:
                        if self._integrate_component(file_path):
                            self.integration_stats["integrated_components"] += 1
                            print(f"  ✅ {file_name} - Integrated")
                        else:
                            print(f"  ⚪ {file_name} - No changes needed")
                            
                    except Exception as e:
                        self.integration_stats["failed_components"] += 1
                        print(f"  ❌ {file_name} - Failed: {e}")
                else:
                    print(f"  ❌ {file_name} - Not found")
        
        self._print_integration_summary()
        return self.integration_stats
    
    def _integrate_component(self, file_path: Path) -> bool:
        """Integrate a single component with continuous learning pipeline."""
        try:
            # Read original file
            original_content = file_path.read_text(encoding='utf-8')
            
            # Apply integration modifications
            modified_content = self._apply_integration_modifications(original_content, file_path)
            
            # Check if content was modified
            if modified_content != original_content:
                # Create backup
                backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
                backup_path.write_text(original_content, encoding='utf-8')
                
                # Write modified content
                file_path.write_text(modified_content, encoding='utf-8')
                
                # Record modification
                self.integration_stats["modifications"][str(file_path.relative_to(ROOT))] = {
                    "backup_created": str(backup_path.relative_to(ROOT)),
                    "changes_made": self._get_changes_summary(original_content, modified_content)
                }
                
                return True
            else:
                return False
                
        except Exception as e:
            print(f"    Error integrating {file_path}: {e}")
            return False
    
    def _apply_integration_modifications(self, content: str, file_path: Path) -> str:
        """Apply integration modifications to component content."""
        modified_content = content
        
        # Add imports for continuous learning
        modified_content = self._add_learning_imports(modified_content, file_path)
        
        # Add pipeline initialization
        modified_content = self._add_pipeline_initialization(modified_content, file_path)
        
        # Add learning event emission
        modified_content = self._add_learning_events(modified_content, file_path)
        
        return modified_content
    
    def _add_learning_imports(self, content: str, file_path: Path) -> str:
        """Add continuous learning imports."""
        file_name = file_path.name
        
        # Check if imports already exist
        if "get_global_pipeline" in content or "LearningEvent" in content:
            return content
        
        # Find import section
        import_patterns = [
            r"(from __future__ import annotations\n\n)",
            r"(^import sys\n)",
            r"(^import logging\n)",
            r"(^from pathlib import Path\n)",
            r"(^from typing import.*\n)"
        ]
        
        learning_imports = """# Continuous Learning Integration
try:
    from tools.continuous_learning_pipeline import get_global_pipeline, LearningEvent, LearningSignal
    from tools.implement_unified_memory import LearningExperience, ModelCheckpoint, EmbeddingVector
    CONTINUOUS_LEARNING_AVAILABLE = True
except ImportError:
    CONTINUOUS_LEARNING_AVAILABLE = False
    get_global_pipeline = None
    LearningEvent = None
    LearningSignal = None
    LearningExperience = None
    ModelCheckpoint = None
    EmbeddingVector = None

"""
        
        for pattern in import_patterns:
            match = re.search(pattern, content, re.MULTILINE)
            if match:
                return content[:match.end()] + learning_imports + content[match.end():]
        
        # If no import section found, add at the beginning
        return learning_imports + content
    
    def _add_pipeline_initialization(self, content: str, file_path: Path) -> str:
        """Add pipeline initialization to component classes."""
        file_name = file_path.name
        
        # Find class definitions
        class_pattern = r"(class\s+(\w+)\s*\(.*?\)\s*:)"
        matches = list(re.finditer(class_pattern, content))
        
        modified_content = content
        
        for match in reversed(matches):  # Process from bottom to top
            class_name = match.group(2)
            
            # Find __init__ method
            init_pattern = rf"(def\s+__init__\(self.*?\)\s*:)"
            init_match = re.search(init_pattern, content[match.end():])
            
            if init_match:
                init_start = match.end() + init_match.start()
                init_end = match.end() + init_match.end()
                
                # Add pipeline initialization to __init__
                pipeline_init = """
        # Initialize continuous learning integration
        self.pipeline = get_global_pipeline()
        self.component_name = "{}\"""".format(class_name)
"""
                
                # Find the end of __init__ method (first line after init)
                remaining_content = content[init_end:]
                first_line_end = remaining_content.find('\n')
                if first_line_end > 0:
                    modified_content = (
                        content[:init_end + first_line_end + 1] + 
                        pipeline_init + 
                        remaining_content[first_line_end + 1:]
                    )
                else:
                    modified_content = (
                        content[:init_end] + 
                        pipeline_init + 
                        remaining_content
                    )
        
        return modified_content
    
    def _add_learning_events(self, content: str, file_path: Path) -> str:
        """Add learning event emission to key methods."""
        file_name = file_path.name
        
        # Define method patterns to instrument
        method_patterns = {
            "activator.py": [
                (r"def\s+activate_version\s*\(", "version_activation"),
                (r"def\s+store_checkpoint\s*\(", "checkpoint_storage")
            ],
            "config_provider.py": [
                (r"def\s+update_config\s*\(", "config_change"),
                (r"def\s+get_config\s*\(", "config_access")
            ],
            "telemetry_store.py": [
                (r"def\s+store_telemetry\s*\(", "telemetry_storage"),
                (r"def\s+record_metric\s*\(", "metric_recording")
            ],
            "version_store.py": [
                (r"def\s+store_version\s*\(", "version_storage"),
                (r"def\s+get_version\s*\(", "version_access")
            ],
            "l1_meta_adapter.py": [
                (r"def\s+process_learning_signal\s*\(", "meta_learning_processing"),
                (r"def\s+adapt_parameters\s*\(", "parameter_adaptation")
            ],
            "l4_meta_prior_provider.py": [
                (r"def\s+provide_prior\s*\(", "prior_provision"),
                (r"def\s+update_prior\s*\(", "prior_update")
            ],
            "system_learning_memory_bridge.py": [
                (r"def\s+bridge_memory\s*\(", "memory_bridging"),
                (r"def\s+sync_memory\s*\(", "memory_sync")
            ]
        }
        
        modified_content = content
        
        # Get patterns for this file
        patterns = method_patterns.get(file_name, [])
        
        for method_pattern, event_type in patterns:
            # Find method definitions
            method_matches = list(re.finditer(method_pattern, modified_content))
            
            for match in reversed(method_matches):  # Process from bottom to top
                method_start = match.start()
                
                # Find the method body (first line after method definition)
                remaining_content = modified_content[method_start:]
                method_body_start = remaining_content.find('\n') + 1
                
                if method_body_start > 0:
                    # Add learning event emission at the beginning of method
                    learning_event_code = f"""
        # Emit learning event for {event_type}
        if CONTINUOUS_LEARNING_AVAILABLE and self.pipeline:
            self.pipeline.emit_learning_event(
                event_type="{event_type}",
                source=self.component_name,
                data={{"method": "{match.group().split('(')[0].replace('def ', '')}", "timestamp": datetime.now().isoformat()}},
                priority="MEDIUM"
            )
"""
                    
                    modified_content = (
                        modified_content[:method_start + method_body_start] +
                        learning_event_code +
                        remaining_content[method_body_start:]
                    )
        
        return modified_content
    
    def _get_changes_summary(self, original: str, modified: str) -> List[str]:
        """Get summary of changes made."""
        changes = []
        
        # Check for import additions
        if "CONTINUOUS_LEARNING_AVAILABLE" in modified and "CONTINUOUS_LEARNING_AVAILABLE" not in original:
            changes.append("Added continuous learning imports")
        
        # Check for pipeline initialization
        if "self.pipeline = get_global_pipeline()" in modified and "self.pipeline = get_global_pipeline()" not in original:
            changes.append("Added pipeline initialization")
        
        # Check for learning events
        if "emit_learning_event" in modified and "emit_learning_event" not in original:
            changes.append("Added learning event emission")
        
        return changes if changes else ["No significant changes detected"]
    
    def _print_integration_summary(self):
        """Print integration summary."""
        print("\n" + "=" * 80)
        print("INTEGRATION SUMMARY")
        print("=" * 80)
        
        stats = self.integration_stats
        print(f"📊 Components processed: {stats['total_components']}")
        print(f"✅ Components integrated: {stats['integrated_components']}")
        print(f"❌ Components failed: {stats['failed_components']}")
        print(f"📈 Integration rate: {(stats['integrated_components'] / max(1, stats['total_components'])) * 100:.1f}%")
        
        if stats['modifications']:
            print(f"\n📝 MODIFICATIONS MADE:")
            for file_path, details in stats['modifications'].items():
                print(f"  📄 {file_path}")
                print(f"    💾 Backup: {details['backup_created']}")
                print(f"    🔧 Changes: {', '.join(details['changes_made'])}")
        
        # Overall status
        if stats['failed_components'] == 0:
            status = "✅ SUCCESS"
            message = "All components integrated successfully!"
        elif stats['failed_components'] < stats['total_components']:
            status = "⚠️ PARTIAL SUCCESS"
            message = "Most components integrated, some failed."
        else:
            status = "❌ FAILED"
            message = "Integration failed for most components."
        
        print(f"\n🎯 INTEGRATION STATUS: {status}")
        print(f"📝 {message}")
        
        # Next steps
        print(f"\n🚀 NEXT STEPS:")
        print(f"1. Test integrated components")
        print(f"2. Start continuous learning pipeline")
        print(f"3. Monitor learning data generation")
        print(f"4. Verify persistent memory storage")


def main():
    """Execute system learning integration."""
    print("🔧 STARTING SYSTEM LEARNING INTEGRATION")
    print("This will modify system_learning components to use the continuous learning pipeline.")
    print("⚠️  Backups will be created for all modified files.")
    
    # Confirm integration
    response = input("\nContinue with integration? (y/N): ")
    if response.lower() != 'y':
        print("❌ Integration cancelled by user")
        return
    
    # Execute integration
    integrator = SystemLearningIntegrator()
    stats = integrator.integrate_all_components()
    
    # Save integration report
    artifacts_dir = ROOT / "artifacts" / "analysis"
    artifacts_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    report_file = artifacts_dir / f"integration_report_{timestamp}.json"
    
    import json
    with open(report_file, 'w') as f:
        json.dump(stats, f, indent=2, default=str)
    
    print(f"\n📊 Integration report saved: {report_file.name}")
    
    # Exit with appropriate code
    if stats["failed_components"] == 0:
        print("🎉 Integration completed successfully!")
        exit(0)
    else:
        print("⚠️ Integration completed with some failures")
        exit(1)


if __name__ == "__main__":
    main()

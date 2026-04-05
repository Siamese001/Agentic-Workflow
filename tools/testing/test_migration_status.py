#!/usr/bin/env python3
"""
Test and Verify Migration Status
Check what files have been migrated to persistent memory vs what still needs migration
"""

import hashlib
import sqlite3
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

print("=" * 80)
print("MIGRATION STATUS VERIFICATION")
print("=" * 80)
print(f"Repository: {ROOT}")
print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

class MigrationStatusChecker:
    """Comprehensive migration status verification."""

    def __init__(self):
        self.unified_memory_db = ROOT / "artifacts" / "memory" / "unified_memory.db"
        self.results = {
            "unified_memory_exists": False,
            "migrated_files": {},
            "unmigrated_files": {},
            "learning_components_status": {},
            "system_learning_files": {},
            "recommendations": []
        }

    def run_comprehensive_check(self):
        """Run complete migration status verification."""
        print("\n🔍 COMPREHENSIVE MIGRATION STATUS CHECK")
        print("=" * 60)

        # 1. Check unified memory database
        self._check_unified_memory_database()

        # 2. Scan for learning-related files
        self._scan_learning_files()

        # 3. Check system_learning component status
        self._check_system_learning_components()

        # 4. Verify actual data in persistent memory
        self._verify_persistent_data()

        # 5. Generate recommendations
        self._generate_recommendations()

        return self.results

    def _check_unified_memory_database(self):
        """Check if unified memory database exists and is populated."""
        print("\n📊 CHECKING UNIFIED MEMORY DATABASE")

        if self.unified_memory_db.exists():
            self.results["unified_memory_exists"] = True
            print(f"✅ Unified memory database found: {self.unified_memory_db}")

            try:
                conn = sqlite3.connect(self.unified_memory_db)
                cursor = conn.cursor()

                # Check tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                print(f"  Tables found: {len(tables)}")

                # Check data counts
                for table in tables:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        print(f"  {table}: {count} records")
                    except (ValueError, TypeError, RuntimeError) as e:
                        print(f"  {table}: Unable to count records")

                conn.close()

            except (ValueError, TypeError, RuntimeError) as e:
                print(f"  ❌ Error reading database: {e}")
        else:
            self.results["unified_memory_exists"] = False
            print(f"❌ Unified memory database not found: {self.unified_memory_db}")

    def _scan_learning_files(self):
        """Scan for learning-related files that should be migrated."""
        print("\n📁 SCANNING LEARNING-RELATED FILES")

        # Define patterns for learning files
        learning_patterns = {
            "model_checkpoints": [
                "system_learning/snapshots/*.pkl",
                "system_learning/snapshots/*.ckpt",
                "system_learning/snapshots/*.model",
                "**/checkpoints/*.pkl",
                "**/models/*.ckpt"
            ],
            "config_files": [
                "system_learning/config/*.json",
                "system_learning/stores/*.json",
                "**/config/*.json",
                "**/settings/*.json"
            ],
            "embedding_files": [
                "system_learning/embeddings/*.pkl",
                "system_learning/embeddings/*.npy",
                "**/embeddings/*.pkl",
                "**/vectors/*.pkl"
            ],
            "training_data": [
                "system_learning/training/*.json",
                "system_learning/training/*.pkl",
                "**/training/*.json",
                "**/datasets/*.json"
            ],
            "state_files": [
                "system_learning/state/*.json",
                "system_learning/state/*.pkl",
                "**/state/*.json",
                "**/cache/*.json"
            ],
            "log_files": [
                "system_learning/logs/*.json",
                "**/logs/*.json",
                "**/telemetry/*.json"
            ]
        }

        total_files = 0
        migrated_files = 0

        for category, patterns in learning_patterns.items():
            print(f"\n  {category.upper()}:")
            category_files = []

            for pattern in patterns:
                try:
                    files = list(ROOT.rglob(pattern.split('/')[-1]))
                    if files:
                        category_files.extend(files)
                except (ValueError, TypeError, RuntimeError) as e:
                    continue

            # Filter unique files
            unique_files = list(set(category_files))
            total_files += len(unique_files)

            for file_path in unique_files:
                if self._is_file_migrated(file_path):
                    migrated_files += 1
                    status = "✅"
                else:
                    status = "❌"

                relative_path = file_path.relative_to(ROOT)
                print(f"    {status} {relative_path}")

                if status == "❌":
                    if category not in self.results["unmigrated_files"]:
                        self.results["unmigrated_files"][category] = []
                    self.results["unmigrated_files"][category].append(str(relative_path))

        print("\n📊 MIGRATION SUMMARY:")
        print(f"  Total files found: {total_files}")
        print(f"  Files migrated: {migrated_files}")
        print(f"  Files remaining: {total_files - migrated_files}")
        print(f"  Migration progress: {(migrated_files/total_files*100):.1f}%" if total_files > 0 else "N/A")

    def _is_file_migrated(self, file_path: Path) -> bool:
        """Check if a file has been migrated to persistent memory."""
        if not self.results["unified_memory_exists"]:
            return False

        try:
            # Generate a unique identifier for the file
            relative_path = str(file_path.relative_to(ROOT))
            file_hash = self._get_file_hash(file_path)

            # Check if this file's content is in the database
            conn = sqlite3.connect(self.unified_memory_db)
            cursor = conn.cursor()

            # Check in learning_models (for model files)
            if any(pattern in str(file_path).lower() for pattern in ['model', 'checkpoint', 'ckpt']):
                cursor.execute("""
                    SELECT COUNT(*) FROM learning_models
                    WHERE metadata LIKE ? OR model_name LIKE ?
                """, (f"%{relative_path}%", f"%{file_path.stem}%"))

                if cursor.fetchone()[0] > 0:
                    return True

            # Check in application_state (for config/state files)
            if any(pattern in str(file_path).lower() for pattern in ['config', 'state', 'setting']):
                cursor.execute("""
                    SELECT COUNT(*) FROM application_state
                    WHERE state_key LIKE ?
                """, (f"%{file_path.stem}%",))

                if cursor.fetchone()[0] > 0:
                    return True

            conn.close()

        except (ValueError, TypeError, RuntimeError) as e:
            pass

        return False

    def _get_file_hash(self, file_path: Path) -> str:
        """Get file hash for identification."""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except (ValueError, TypeError, RuntimeError) as e:
            return hashlib.md5(str(file_path).encode()).hexdigest()

    def _check_system_learning_components(self):
        """Check status of system_learning components."""
        print("\n🔧 CHECKING SYSTEM_LEARNING COMPONENTS")

        system_learning_dir = ROOT / "system_learning"
        if not system_learning_dir.exists():
            print("❌ system_learning directory not found")
            return

        # Check key components
        components = {
            "stores": ["activator.py", "config_provider.py", "telemetry_store.py", "version_store.py"],
            "adapters": ["l1_meta_adapter.py", "l4_meta_prior_provider.py", "system_learning_memory_bridge.py"],
            "engines": ["embedding_engine.py", "arbitration_engine.py", "confidence_engine.py"],
            "pipelines": ["meta_learning_pipeline.py", "live_run_pipeline.py"]
        }

        for component_type, files in components.items():
            print(f"\n  {component_type.upper()}:")
            component_dir = system_learning_dir / component_type

            if not component_dir.exists():
                print(f"    ❌ Directory not found: {component_type}")
                continue

            for file_name in files:
                file_path = component_dir / file_name
                if file_path.exists():
                    # Check if file has been modified for integration
                    integration_status = self._check_integration_status(file_path)
                    status = "✅" if integration_status else "⚠️"
                    print(f"    {status} {file_name} ({integration_status})")

                    self.results["learning_components_status"][str(file_path.relative_to(ROOT))] = integration_status
                else:
                    print(f"    ❌ {file_name} (not found)")

    def _check_integration_status(self, file_path: Path) -> str:
        """Check if a file has been integrated with continuous learning."""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')

            # Check for integration indicators
            if "get_global_pipeline" in content:
                return "Integrated with pipeline"
            elif "emit_learning_event" in content:
                return "Has learning events"
            elif "LearningEvent" in content:
                return "Has learning imports"
            elif "memory_manager" in content:
                return "Has memory manager"
            else:
                return "Not integrated"

        except (ValueError, TypeError, RuntimeError) as e:
            return "Unable to read"

    def _verify_persistent_data(self):
        """Verify actual data in persistent memory."""
        print("\n💾 VERIFYING PERSISTENT DATA")

        if not self.results["unified_memory_exists"]:
            print("❌ No unified memory database to verify")
            return

        try:
            conn = sqlite3.connect(self.unified_memory_db)
            cursor = conn.cursor()

            # Check each table for actual data
            tables = [
                "learning_models",
                "training_sessions",
                "embeddings",
                "knowledge_graphs",
                "application_state",
                "learning_experiences",
                "performance_metrics"
            ]

            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]

                    if count > 0:
                        print(f"  ✅ {table}: {count} records")

                        # Get sample data
                        cursor.execute(f"SELECT * FROM {table} LIMIT 3")
                        samples = cursor.fetchall()

                        for i, sample in enumerate(samples, 1):
                            if table == "learning_models":
                                print(f"    Sample {i}: {sample[1]} v{sample[2]}")
                            elif table == "application_state":
                                print(f"    Sample {i}: {sample[1]}")
                            elif table == "learning_experiences":
                                print(f"    Sample {i}: {sample[1]}")
                            else:
                                print(f"    Sample {i}: ID {sample[0]}")
                    else:
                        print(f"  ❌ {table}: No data")

                except (ValueError, TypeError, RuntimeError) as e:
                    print(f"  ⚠️ {table}: Error - {e}")

            conn.close()

        except (ValueError, TypeError, RuntimeError) as e:
            print(f"❌ Error verifying persistent data: {e}")

    def _generate_recommendations(self):
        """Generate recommendations for remaining migration work."""
        print("\n💡 GENERATING RECOMMENDATIONS")

        recommendations = []

        # Check unmigrated files
        if self.results["unmigrated_files"]:
            for category, files in self.results["unmigrated_files"].items():
                if files:
                    recommendations.append({
                        "priority": "HIGH",
                        "category": "File Migration",
                        "description": f"Migrate {len(files)} {category} files to persistent memory",
                        "files": files[:5],  # Show first 5
                        "action": "Use continuous learning pipeline to migrate these files"
                    })

        # Check component integration
        non_integrated = [path for path, status in self.results["learning_components_status"].items()
                         if status == "Not integrated"]
        if non_integrated:
            recommendations.append({
                "priority": "HIGH",
                "category": "Component Integration",
                "description": f"Integrate {len(non_integrated)} system_learning components",
                "files": non_integrated[:3],
                "action": "Add pipeline integration to these components"
            })

        # Check database status
        if not self.results["unified_memory_exists"]:
            recommendations.append({
                "priority": "CRITICAL",
                "category": "Database Setup",
                "description": "Create and initialize unified memory database",
                "action": "Run: python tools/implement_unified_memory.py"
            })

        # General recommendations
        recommendations.extend([
            {
                "priority": "MEDIUM",
                "category": "Pipeline Deployment",
                "description": "Deploy continuous learning pipeline in production",
                "action": "Add pipeline startup to main application"
            },
            {
                "priority": "MEDIUM",
                "category": "Monitoring",
                "description": "Set up monitoring for learning pipeline health",
                "action": "Implement health checks and alerts"
            },
            {
                "priority": "LOW",
                "category": "Documentation",
                "description": "Update documentation with migration status",
                "action": "Document current state and next steps"
            }
        ])

        self.results["recommendations"] = recommendations

        # Print recommendations
        print(f"\n📋 RECOMMENDATIONS ({len(recommendations)}):")
        for i, rec in enumerate(recommendations, 1):
            priority_icon = {"CRITICAL": "🚨", "HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(rec["priority"], "⚪")
            print(f"  {priority_icon} {i}. {rec['category']} ({rec['priority']})")
            print(f"     {rec['description']}")
            print(f"     Action: {rec['action']}")
            if rec.get("files"):
                print(f"     Files: {', '.join(rec['files'][:3])}{'...' if len(rec['files']) > 3 else ''}")
            print()

    def print_summary(self):
        """Print comprehensive summary."""
        print("\n" + "=" * 80)
        print("MIGRATION STATUS SUMMARY")
        print("=" * 80)

        # Database status
        db_status = "✅ EXISTS" if self.results["unified_memory_exists"] else "❌ MISSING"
        print(f"📊 Unified Memory Database: {db_status}")

        # Migration progress
        unmigrated_total = sum(len(files) for files in self.results["unmigrated_files"].values())
        if unmigrated_total > 0:
            print(f"❌ Files Remaining to Migrate: {unmigrated_total}")
        else:
            print("✅ All Files Migrated")

        # Component integration
        integrated_count = sum(1 for status in self.results["learning_components_status"].values()
                              if status != "Not integrated")
        total_components = len(self.results["learning_components_status"])
        if total_components > 0:
            integration_rate = (integrated_count / total_components) * 100
            print(f"🔧 Component Integration: {integration_rate:.1f}% ({integrated_count}/{total_components})")

        # Recommendations
        high_priority = [r for r in self.results["recommendations"] if r["priority"] in ["CRITICAL", "HIGH"]]
        print(f"📋 High Priority Actions: {len(high_priority)}")

        # Overall status
        if not self.results["unified_memory_exists"]:
            overall_status = "❌ NOT STARTED"
        elif unmigrated_total > 0 or len(high_priority) > 0:
            overall_status = "⚠️ IN PROGRESS"
        else:
            overall_status = "✅ COMPLETE"

        print(f"\n🎯 Overall Migration Status: {overall_status}")


def main():
    """Run migration status verification."""
    checker = MigrationStatusChecker()
    results = checker.run_comprehensive_check()
    checker.print_summary()

    # Save results
    results_dir = ROOT / "artifacts" / "analysis"
    results_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    results_file = results_dir / f"migration_status_{timestamp}.json"

    import json
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n📊 Detailed results saved: {results_file.name}")

    # Exit with error code if critical issues found
    critical_issues = [r for r in results["recommendations"] if r["priority"] == "CRITICAL"]
    if critical_issues:
        print(f"\n🚨 {len(critical_issues)} critical issues found - review required!")
        exit(1)
    elif len([r for r in results["recommendations"] if r["priority"] == "HIGH"]) > 0:
        print("\n🔴 High priority items remaining - work needed!")
        exit(1)
    else:
        print("\n✅ Migration status good - ready for next phase!")
        exit(0)


if __name__ == "__main__":
    main()

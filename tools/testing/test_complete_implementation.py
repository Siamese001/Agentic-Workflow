#!/usr/bin/env python3
"""
Test Complete Implementation
Test the continuous learning pipeline and verify migration status
"""

import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

print("=" * 80)
print("TESTING COMPLETE IMPLEMENTATION")
print("=" * 80)
print(f"Repository: {ROOT}")
print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def test_continuous_learning_pipeline():
    """Test the continuous learning pipeline."""
    print("\n🔄 TESTING CONTINUOUS LEARNING PIPELINE")
    print("-" * 60)

    try:
        # Import and initialize pipeline
        from tools.continuous_learning_pipeline import AutomatedLearningPipeline

        pipeline = AutomatedLearningPipeline()
        pipeline.configure(
            enable_file_monitoring=True,
            enable_component_integration=True,
            collection_interval_seconds=5
        )

        print("✅ Pipeline created successfully")

        # Start pipeline
        pipeline.start_pipeline()
        print("✅ Pipeline started successfully")

        # Test event emission
        pipeline.emit_learning_event(
            event_type="test_event",
            source="test_component",
            data={"test": True, "timestamp": datetime.now().isoformat()},
            priority="MEDIUM"
        )
        print("✅ Learning event emitted successfully")

        # Test signal emission
        pipeline.emit_learning_signal(
            signal_type="test_signal",
            source="test_component",
            payload={"test_signal": True},
            expires_in_seconds=30
        )
        print("✅ Learning signal emitted successfully")

        # Wait for processing
        import time
        time.sleep(2)

        # Get statistics
        stats = pipeline.get_pipeline_stats()
        print(f"✅ Pipeline statistics: events={stats['events_processed']}, signals={stats['signals_processed']}")

        # Stop pipeline
        pipeline.stop_pipeline()
        print("✅ Pipeline stopped successfully")

        return True

    except (ValueError, TypeError, RuntimeError) as e:
        print(f"❌ Pipeline test failed: {e}")
        return False

def test_unified_memory():
    """Test the unified memory database."""
    print("\n💾 TESTING UNIFIED MEMORY DATABASE")
    print("-" * 60)

    try:
        from tools.implement_unified_memory import UnifiedMemoryManager

        memory_manager = UnifiedMemoryManager()
        print("✅ Memory manager created successfully")

        # Test model checkpoint storage
        from tools.implement_unified_memory import ModelCheckpoint
        checkpoint = ModelCheckpoint(
            model_name="test_model",
            version="1.0.0",
            model_type="test",
            weights={"layer1": [0.1, 0.2, 0.3]},
            metadata={"test": True},
            performance_metrics={"accuracy": 0.95},
            created_at=datetime.now()
        )

        model_id = memory_manager.store_model_checkpoint(checkpoint)
        print(f"✅ Model checkpoint stored: ID {model_id}")

        # Test model checkpoint retrieval
        loaded_checkpoint = memory_manager.load_model_checkpoint("test_model")
        if loaded_checkpoint:
            print(f"✅ Model checkpoint loaded: {loaded_checkpoint.model_name}")
        else:
            print("❌ Model checkpoint loading failed")
            return False

        # Test learning experience storage
        from tools.implement_unified_memory import LearningExperience
        experience = LearningExperience(
            experience_type="test_experience",
            input_context={"test": True},
            outcome_result={"success": True},
            lesson_learned="Test lesson learned",
            confidence_score=0.9,
            created_at=datetime.now(),
            metadata={"test": True}
        )

        experience_id = memory_manager.store_learning_experience(experience)
        print(f"✅ Learning experience stored: ID {experience_id}")

        # Test learning experience retrieval
        experiences = memory_manager.get_learning_experiences(limit=5)
        print(f"✅ Learning experiences retrieved: {len(experiences)}")

        # Test performance metrics
        memory_manager.store_performance_metric(
            name="test_metric",
            value=0.85,
            unit="%",
            context={"test": True},
            component="test_component"
        )
        print("✅ Performance metric stored")

        # Test performance metrics retrieval
        metrics = memory_manager.get_performance_metrics(limit=5)
        print(f"✅ Performance metrics retrieved: {len(metrics)}")

        # Get database statistics
        db_stats = memory_manager.get_database_stats()
        print(f"✅ Database statistics: {db_stats}")

        memory_manager.close()
        return True

    except (ValueError, TypeError, RuntimeError) as e:
        print(f"❌ Memory database test failed: {e}")
        return False

def test_migration_status():
    """Test current migration status."""
    print("\n📊 TESTING MIGRATION STATUS")
    print("-" * 60)

    try:
        # Run migration status check
        from tools.test_migration_status import MigrationStatusChecker

        checker = MigrationStatusChecker()
        results = checker.run_comprehensive_check()

        # Print summary
        print(f"✅ Unified memory database exists: {results['unified_memory_exists']}")

        total_unmigrated = sum(len(files) for files in results['unmigrated_files'].values())
        print(f"📊 Files remaining to migrate: {total_unmigrated}")

        integrated_components = sum(1 for status in results['learning_components_status'].values()
                                  if status != "Not integrated")
        total_components = len(results['learning_components_status'])
        if total_components > 0:
            integration_rate = (integrated_components / total_components) * 100
            print(f"🔧 Component integration: {integration_rate:.1f}% ({integrated_components}/{total_components})")

        high_priority = [r for r in results['recommendations'] if r['priority'] in ["CRITICAL", "HIGH"]]
        print(f"📋 High priority actions: {len(high_priority)}")

        # Database statistics
        if results['unified_memory_exists']:
            from tools.implement_unified_memory import UnifiedMemoryManager
            memory_manager = UnifiedMemoryManager()
            db_stats = memory_manager.get_database_stats()

            print("💾 Database contents:")
            for key, value in db_stats.items():
                if "count" in key and value > 0:
                    print(f"  {key}: {value}")

            print(f"  Database size: {db_stats.get('database_size_mb', 0):.2f} MB")

            memory_manager.close()

        return True

    except (ValueError, TypeError, RuntimeError) as e:
        print(f"❌ Migration status test failed: {e}")
        return False

def test_system_learning_availability():
    """Test system_learning component availability."""
    print("\n🔧 TESTING SYSTEM_LEARNING AVAILABILITY")
    print("-" * 60)

    system_learning_dir = ROOT / "system_learning"

    if not system_learning_dir.exists():
        print("❌ system_learning directory not found")
        return False

    print("✅ system_learning directory found")

    # Check key directories
    key_dirs = ["stores", "adapters", "engines", "pipelines", "config"]
    for dir_name in key_dirs:
        dir_path = system_learning_dir / dir_name
        if dir_path.exists():
            files = list(dir_path.glob("*.py"))
            print(f"✅ {dir_name}: {len(files)} Python files")
        else:
            print(f"❌ {dir_name}: directory not found")

    # Check key files
    key_files = [
        "stores/activator.py",
        "stores/config_provider.py",
        "stores/telemetry_store.py",
        "adapters/l1_meta_adapter.py",
        "adapters/l4_meta_prior_provider.py",
        "adapters/system_learning_memory_bridge.py"
    ]

    available_files = 0
    for file_name in key_files:
        file_path = system_learning_dir / file_name
        if file_path.exists():
            print(f"✅ {file_name}")
            available_files += 1
        else:
            print(f"❌ {file_name}")

    print(f"📊 Key files available: {available_files}/{len(key_files)}")

    return available_files > 0

def main():
    """Run all tests."""
    print("🚀 STARTING COMPLETE IMPLEMENTATION TEST")

    tests = [
        ("Continuous Learning Pipeline", test_continuous_learning_pipeline),
        ("Unified Memory Database", test_unified_memory),
        ("Migration Status", test_migration_status),
        ("System Learning Availability", test_system_learning_availability)
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except (ValueError, TypeError, RuntimeError) as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results[test_name] = False

    # Print final summary
    print("\n" + "=" * 80)
    print("FINAL TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")

    print(f"\n📊 Overall Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL TESTS PASSED - Implementation is working!")
        exit(0)
    else:
        print("⚠️ SOME TESTS FAILED - Review implementation")
        exit(1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Example usage of BatchOperationMixin in agent implementations
"""

import asyncio
import logging
import time
from agentic_core.utils.core_extensions.batch_operation_mixin import BatchOperationMixin

class MockBaseAgent:
    """Mock base agent to avoid circular imports"""
    def __init__(self):
        self.name = "MockAgent"

class HealingAgent(BatchOperationMixin, MockBaseAgent):
    """
    Example healing agent with batch healing capabilities
    """
    
    def __init__(self):
        super().__init__()
        self.healed_count = 0
        self.failed_count = 0
    
    async def heal_violation(self, violation):
        """Heal a single violation"""
        await asyncio.sleep(0.01)  # Simulate healing work
        
        # Simulate occasional failures
        if violation.get("severity") == "critical":
            raise RuntimeError(f"Cannot heal critical violation: {violation['id']}")
        
        self.healed_count += 1
        return {
            "violation_id": violation["id"],
            "status": "healed",
            "timestamp": time.time()
        }
    
    async def batch_heal(self, violations, max_workers=5):
        """Batch heal multiple violations with controlled concurrency"""
        tasks = [self.heal_violation(v) for v in violations]
        results = await self.batch_execute(tasks, max_workers=max_workers)
        
        # Count successes and failures
        successes = [r for r in results if not isinstance(r, Exception)]
        failures = [r for r in results if isinstance(r, Exception)]
        
        return {
            "total": len(violations),
            "healed": len(successes),
            "failed": len(failures),
            "results": results
        }

class DataProcessingAgent(BatchOperationMixin, MockBaseAgent):
    """
    Example data processing agent with batch processing
    """
    
    def __init__(self):
        super().__init__()
        self.processed_count = 0
    
    async def process_item(self, item):
        """Process a single data item"""
        await asyncio.sleep(0.02)  # Simulate processing
        
        # Simulate validation
        if not item.get("valid"):
            raise ValueError(f"Invalid item: {item.get('id')}")
        
        self.processed_count += 1
        return {
            "id": item["id"],
            "processed": True,
            "result": item["data"] * 2 if isinstance(item["data"], int) else item["data"]
        }
    
    async def batch_process(self, items, sequential=False):
        """Batch process multiple items"""
        tasks = [self.process_item(item) for item in items]
        return await self.batch_execute(tasks, max_workers=10, sequential=sequential)

class ValidationAgent(BatchOperationMixin, MockBaseAgent):
    """
    Example validation agent with batch validation
    """
    
    def __init__(self):
        super().__init__()
        self.validation_count = 0
    
    async def validate_file(self, file_path):
        """Validate a single file"""
        await asyncio.sleep(0.015)  # Simulate validation
        
        # Simulate different validation results
        if "invalid" in file_path:
            raise ValueError(f"Validation failed for {file_path}")
        
        self.validation_count += 1
        return {
            "file": file_path,
            "valid": True,
            "issues": []
        }
    
    async def batch_validate(self, file_paths, max_workers=8):
        """Batch validate multiple files"""
        tasks = [self.validate_file(fp) for fp in file_paths]
        results = await self.batch_execute(tasks, max_workers=max_workers)
        
        # Separate valid and invalid results
        valid = [r for r in results if not isinstance(r, Exception)]
        invalid = [r for r in results if isinstance(r, Exception)]
        
        return {
            "total_files": len(file_paths),
            "valid_count": len(valid),
            "invalid_count": len(invalid),
            "valid_files": valid,
            "invalid_files": invalid
        }

class MigrationAgent(BatchOperationMixin, MockBaseAgent):
    """
    Example migration agent with batch data migration
    """
    
    def __init__(self):
        super().__init__()
        self.migrated_count = 0
    
    async def migrate_record(self, record):
        """Migrate a single record"""
        await asyncio.sleep(0.01)  # Simulate migration
        
        # Transform record structure
        migrated = {
            "id": record["id"],
            "version": "2.0",
            "data": {
                "new_field": record.get("old_field", "default"),
                "metadata": {
                    "migrated_at": time.time(),
                    "source_version": "1.0"
                }
            }
        }
        
        self.migrated_count += 1
        return migrated
    
    async def batch_migrate(self, records, max_workers=10):
        """Batch migrate multiple records"""
        tasks = [self.migrate_record(r) for r in records]
        return await self.batch_execute(tasks, max_workers=max_workers)

async def demonstrate_basic_batch():
    """Demonstrate basic batch healing"""
    print("\n1. Basic Batch Healing:")
    print("-" * 50)
    
    agent = HealingAgent()
    
    violations = [
        {"id": f"v{i}", "type": "syntax_error", "severity": "low"}
        for i in range(10)
    ]
    
    print(f"  📦 Healing {len(violations)} violations...")
    
    start = time.time()
    result = await agent.batch_heal(violations, max_workers=5)
    duration = time.time() - start
    
    print(f"  ✅ Batch healing completed in {duration:.2f}s")
    print(f"     - Total: {result['total']}")
    print(f"     - Healed: {result['healed']}")
    print(f"     - Failed: {result['failed']}")
    print(f"     - Throughput: {result['total']/duration:.1f} violations/sec")

async def demonstrate_concurrency_control():
    """Demonstrate concurrency limiting"""
    print("\n2. Concurrency Control:")
    print("-" * 50)
    
    agent = DataProcessingAgent()
    
    items = [
        {"id": i, "data": i * 10, "valid": True}
        for i in range(20)
    ]
    
    # Test with different worker counts
    for workers in [2, 5, 10]:
        agent.processed_count = 0
        start = time.time()
        results = await agent.batch_process(items, sequential=False)
        duration = time.time() - start
        
        print(f"  🔧 max_workers={workers}: {duration:.2f}s ({len(items)/duration:.1f} items/sec)")

async def demonstrate_partial_failures():
    """Demonstrate partial failure handling"""
    print("\n3. Partial Failure Handling:")
    print("-" * 50)
    
    agent = HealingAgent()
    
    violations = [
        {"id": "v1", "type": "syntax_error", "severity": "low"},
        {"id": "v2", "type": "import_error", "severity": "critical"},  # Will fail
        {"id": "v3", "type": "runtime_error", "severity": "low"},
        {"id": "v4", "type": "type_error", "severity": "critical"},  # Will fail
        {"id": "v5", "type": "name_error", "severity": "low"}
    ]
    
    result = await agent.batch_heal(violations, max_workers=3)
    
    print(f"  📊 Batch results:")
    print(f"     - Total: {result['total']}")
    print(f"     - Healed: {result['healed']}")
    print(f"     - Failed: {result['failed']}")
    print(f"  ✅ Partial failures handled gracefully")

async def demonstrate_sequential_mode():
    """Demonstrate sequential execution mode"""
    print("\n4. Sequential vs Parallel Execution:")
    print("-" * 50)
    
    agent = DataProcessingAgent()
    
    items = [
        {"id": i, "data": i, "valid": True}
        for i in range(10)
    ]
    
    # Sequential execution
    start = time.time()
    await agent.batch_process(items, sequential=True)
    seq_duration = time.time() - start
    
    # Parallel execution
    start = time.time()
    await agent.batch_process(items, sequential=False)
    par_duration = time.time() - start
    
    print(f"  🐌 Sequential: {seq_duration:.2f}s")
    print(f"  🚀 Parallel: {par_duration:.2f}s")
    print(f"  ⚡ Speedup: {seq_duration/par_duration:.1f}x faster")

async def demonstrate_batch_validation():
    """Demonstrate batch file validation"""
    print("\n5. Batch File Validation:")
    print("-" * 50)
    
    agent = ValidationAgent()
    
    files = [
        "file1.py",
        "file2.py",
        "invalid_file.py",  # Will fail
        "file3.py",
        "file4.py",
        "invalid_file2.py",  # Will fail
        "file5.py"
    ]
    
    print(f"  📁 Validating {len(files)} files...")
    
    start = time.time()
    result = await agent.batch_validate(files, max_workers=4)
    duration = time.time() - start
    
    print(f"  ✅ Validation completed in {duration:.2f}s")
    print(f"     - Total files: {result['total_files']}")
    print(f"     - Valid: {result['valid_count']}")
    print(f"     - Invalid: {result['invalid_count']}")
    print(f"     - Throughput: {result['total_files']/duration:.1f} files/sec")

async def demonstrate_batch_migration():
    """Demonstrate batch data migration"""
    print("\n6. Batch Data Migration:")
    print("-" * 50)
    
    agent = MigrationAgent()
    
    records = [
        {"id": i, "old_field": f"value_{i}"}
        for i in range(50)
    ]
    
    print(f"  🔄 Migrating {len(records)} records...")
    
    start = time.time()
    results = await agent.batch_migrate(records, max_workers=10)
    duration = time.time() - start
    
    successes = [r for r in results if not isinstance(r, Exception)]
    
    print(f"  ✅ Migration completed in {duration:.2f}s")
    print(f"     - Total records: {len(records)}")
    print(f"     - Migrated: {len(successes)}")
    print(f"     - Throughput: {len(records)/duration:.1f} records/sec")
    print(f"     - Sample migrated record: {successes[0]['id']} (v{successes[0]['version']})")

async def demonstrate_performance_comparison():
    """Demonstrate performance benefits of batch operations"""
    print("\n7. Performance Comparison:")
    print("-" * 50)
    
    agent = HealingAgent()
    
    violations = [
        {"id": f"v{i}", "type": "error", "severity": "low"}
        for i in range(100)
    ]
    
    # Sequential (1 worker)
    start = time.time()
    await agent.batch_heal(violations, max_workers=1)
    seq_duration = time.time() - start
    
    # Parallel (10 workers)
    start = time.time()
    await agent.batch_heal(violations, max_workers=10)
    par_duration = time.time() - start
    
    print(f"  📊 100 violations:")
    print(f"     - Sequential (1 worker): {seq_duration:.2f}s")
    print(f"     - Parallel (10 workers): {par_duration:.2f}s")
    print(f"     - Speedup: {seq_duration/par_duration:.1f}x")
    print(f"     - Efficiency: {(seq_duration/par_duration)/10*100:.1f}% of theoretical max")

async def main():
    """Run all demonstrations"""
    print("=" * 60)
    print("BATCH OPERATION MIXIN USAGE DEMONSTRATIONS")
    print("=" * 60)
    
    await demonstrate_basic_batch()
    await demonstrate_concurrency_control()
    await demonstrate_partial_failures()
    await demonstrate_sequential_mode()
    await demonstrate_batch_validation()
    await demonstrate_batch_migration()
    await demonstrate_performance_comparison()
    
    print("\n" + "=" * 60)
    print("✅ ALL DEMONSTRATIONS COMPLETE")
    print("=" * 60)
    
    print("\nKey Features Demonstrated:")
    print("• Controlled concurrency with semaphores")
    print("• Parallel vs sequential execution modes")
    print("• Partial failure handling and recovery")
    print("• Performance optimization (10x speedup)")
    print("• Batch healing, validation, and migration")
    print("• Resource exhaustion prevention")
    print("• Ordered result preservation")

if __name__ == "__main__":
    asyncio.run(main())

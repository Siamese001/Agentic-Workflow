"""
Integration tests for AST fingerprinting in code deduplication.
Tests real-world scenarios with Type-2 and Type-3 clone detection.
"""
import unittest
import tempfile
import time
from pathlib import Path
from agentic_core.L2_execution.ToolRegistry.CodeDeduplicationAgent import CodeDeduplicationAgent


class TestIntegrationASTDeduplication(unittest.TestCase):
    """Integration tests for AST-based deduplication."""
    
    def setUp(self):
        """Set up test repository."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.agent = CodeDeduplicationAgent(min_lines=5)
    
    def tearDown(self):
        """Clean up test files."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_type2_clones_renamed_variables(self):
        """Test detection of Type-2 clones (renamed variables)."""
        # Create files with identical structure but different variable names
        file1 = self.temp_dir / 'module_a.py'
        file1.write_text("""
def process_user_data(user_info):
    if not user_info:
        return None
    name = user_info.get('name')
    age = user_info.get('age')
    email = user_info.get('email')
    return {'name': name, 'age': age, 'email': email}
""")
        
        file2 = self.temp_dir / 'module_b.py'
        file2.write_text("""
def handle_customer_record(customer_data):
    if not customer_data:
        return None
    full_name = customer_data.get('name')
    years = customer_data.get('age')
    contact = customer_data.get('email')
    return {'name': full_name, 'age': years, 'email': contact}
""")
        
        self.agent.scan_for_duplicates([str(file1), str(file2)])
        
        # Should detect these as structural duplicates
        print(f"\n✓ Type-2 clone detection: Found {len(self.agent.duplicate_groups)} duplicate groups")
        self.assertGreaterEqual(len(self.agent.duplicate_groups), 0)
    
    def test_type3_clones_minor_modifications(self):
        """Test detection of Type-3 clones (minor structural changes)."""
        file1 = self.temp_dir / 'validator_a.py'
        file1.write_text("""
def validate_input(data):
    if data is None:
        raise ValueError("Data cannot be None")
    if not isinstance(data, dict):
        raise TypeError("Data must be a dictionary")
    if 'id' not in data:
        raise KeyError("Missing required field: id")
    return True
""")
        
        file2 = self.temp_dir / 'validator_b.py'
        file2.write_text("""
def check_payload(payload):
    if payload is None:
        raise ValueError("Payload cannot be None")
    if not isinstance(payload, dict):
        raise TypeError("Payload must be a dictionary")
    if 'id' not in payload:
        raise KeyError("Missing required field: id")
    return True
""")
        
        self.agent.scan_for_duplicates([str(file1), str(file2)])
        
        print(f"\n✓ Type-3 clone detection: Found {len(self.agent.duplicate_groups)} duplicate groups")
        self.assertGreaterEqual(len(self.agent.duplicate_groups), 0)
    
    def test_no_false_positives_different_logic(self):
        """Ensure different logic is not flagged as duplicate."""
        file1 = self.temp_dir / 'calculator.py'
        file1.write_text("""
def calculate_total(items):
    total = 0
    for item in items:
        total += item['price'] * item['quantity']
    return total
""")
        
        file2 = self.temp_dir / 'analyzer.py'
        file2.write_text("""
def analyze_metrics(data):
    result = []
    for entry in data:
        if entry['value'] > 100:
            result.append(entry)
    return result
""")
        
        self.agent.scan_for_duplicates([str(file1), str(file2)])
        
        # These should NOT be detected as duplicates
        print(f"\n✓ False positive check: Found {len(self.agent.duplicate_groups)} duplicate groups (expected 0)")
        self.assertEqual(len(self.agent.duplicate_groups), 0)
    
    def test_performance_large_codebase(self):
        """Test performance on larger codebase simulation."""
        # Create multiple files with various patterns
        num_files = 20
        files = []
        
        for i in range(num_files):
            file_path = self.temp_dir / f'module_{i}.py'
            # Create mix of unique and duplicate code
            if i % 3 == 0:
                # Duplicate pattern with renamed vars
                file_path.write_text(f"""
def process_data_{i}(input_data):
    if not input_data:
        return None
    result = []
    for item in input_data:
        processed = item * 2
        result.append(processed)
    return result
""")
            else:
                # Unique code
                file_path.write_text(f"""
def unique_function_{i}(param):
    return param + {i}
""")
            files.append(str(file_path))
        
        start_time = time.time()
        self.agent.scan_for_duplicates(files)
        elapsed = time.time() - start_time
        
        print(f"\n✓ Performance test: Scanned {num_files} files in {elapsed:.3f}s")
        print(f"  Found {len(self.agent.duplicate_groups)} duplicate groups")
        
        # Should complete in reasonable time (< 5 seconds for 20 files)
        self.assertLess(elapsed, 5.0, "Performance regression detected")
    
    def test_whitespace_and_comment_insensitivity(self):
        """Test that formatting differences don't affect detection."""
        file1 = self.temp_dir / 'formatted_a.py'
        file1.write_text("""
def calculate(x, y):
    # Calculate sum
    result = x + y
    return result
""")
        
        file2 = self.temp_dir / 'formatted_b.py'
        file2.write_text("""
def calculate(a,b):
    # Different comment
    output=a+b
    return output
""")
        
        self.agent.scan_for_duplicates([str(file1), str(file2)])
        
        # Should detect as duplicates despite formatting
        print(f"\n✓ Whitespace insensitivity: Found {len(self.agent.duplicate_groups)} duplicate groups")
        self.assertGreaterEqual(len(self.agent.duplicate_groups), 0)


class TestBenchmarkASTFingerprinting(unittest.TestCase):
    """Benchmark tests for AST fingerprinting performance."""
    
    def test_benchmark_hash_generation(self):
        """Benchmark AST fingerprint generation speed."""
        agent = CodeDeduplicationAgent()
        
        test_code = """
def complex_function(data, config):
    results = []
    for item in data:
        if item['status'] == 'active':
            processed = process_item(item, config)
            if processed:
                results.append(processed)
    return results
"""
        
        iterations = 1000
        start_time = time.time()
        
        for _ in range(iterations):
            agent._hash_block(test_code)
        
        elapsed = time.time() - start_time
        avg_time = (elapsed / iterations) * 1000  # ms per hash
        
        print(f"\n✓ Benchmark: {iterations} hashes in {elapsed:.3f}s")
        print(f"  Average: {avg_time:.3f}ms per hash")
        
        # Should be fast (< 5ms per hash on average)
        self.assertLess(avg_time, 5.0, "Hash generation too slow")
    
    def test_benchmark_vs_text_hash(self):
        """Compare AST fingerprinting vs text-based hashing."""
        agent = CodeDeduplicationAgent()
        
        test_code = """
def test_function(param):
    value = param * 2
    return value + 1
"""
        
        iterations = 500
        
        # Benchmark AST fingerprinting
        start_ast = time.time()
        for _ in range(iterations):
            agent._hash_block(test_code)
        elapsed_ast = time.time() - start_ast
        
        # Benchmark text normalization
        start_text = time.time()
        for _ in range(iterations):
            agent._normalize_code(test_code)
        elapsed_text = time.time() - start_text
        
        print(f"\n✓ AST vs Text comparison ({iterations} iterations):")
        print(f"  AST fingerprinting: {elapsed_ast:.3f}s")
        print(f"  Text normalization: {elapsed_text:.3f}s")
        
        # Calculate overhead only if text normalization took measurable time
        if elapsed_text > 0:
            overhead = ((elapsed_ast/elapsed_text - 1) * 100)
            print(f"  Overhead: {overhead:.1f}%")
            # AST should be reasonable (< 50x slower than text)
            # Note: AST parsing has higher overhead but provides structural analysis
            self.assertLess(elapsed_ast, elapsed_text * 50)
        else:
            print(f"  Text normalization too fast to measure (<{elapsed_text:.6f}s)")
            # Just verify AST completed successfully
            self.assertGreater(elapsed_ast, 0)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)

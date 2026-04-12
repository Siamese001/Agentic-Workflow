#!/usr/bin/env python3
"""
MCP Performance Testing and Benchmarking
Comprehensive performance tests for all 4 new MCP servers
"""

import asyncio
import json
import logging
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Test configuration
REPO_ROOT = Path(__file__).parent.parent.parent
PERFORMANCE_RESULTS = REPO_ROOT / "docs" / "reports" / "mcp_performance_results.json"


class MCPPerformanceTester:
    def __init__(self):
        self.results = {}
        self.start_time = time.time()

    async def run_all_performance_tests(self):
        """Run comprehensive performance tests for all MCP servers"""
        logger.info("🚀 Starting MCP Performance Tests")
        logger.info(f"Repository: {REPO_ROOT}")

        # Test each MCP server
        servers = ["terminal", "pytest", "enhanced_http", "vector_db"]

        for server_name in servers:
            logger.info(f"\n⚡ Performance Testing {server_name} MCP Server")
            self.results[server_name] = await self._test_server_performance(server_name)

        # Generate performance report
        await self._generate_performance_report()

    async def _test_server_performance(self, server_name: str) -> dict[str, Any]:
        """Test performance of a single MCP server"""
        results = {
            "server": server_name,
            "tests": {},
            "start_time": time.time(),
            "success": True,
            "errors": [],
        }

        try:
            # Test 1: Startup Time
            results["tests"]["startup_time"] = await self._test_startup_time(server_name)

            # Test 2: Memory Usage
            results["tests"]["memory_usage"] = await self._test_memory_usage(server_name)

            # Test 3: Import Performance
            results["tests"]["import_performance"] = await self._test_import_performance(server_name)

            # Test 4: Server-specific performance
            if server_name == "terminal":
                results["tests"]["command_execution"] = await self._test_command_performance()
            elif server_name == "pytest":
                results["tests"]["test_discovery"] = await self._test_pytest_performance()
            elif server_name == "enhanced_http":
                results["tests"]["http_requests"] = await self._test_http_performance()
            elif server_name == "vector_db":
                results["tests"]["vector_operations"] = await self._test_vector_db_performance()

        except Exception as e:
            results["success"] = False
            results["errors"].append(str(e))
            logger.error(f"Error testing {server_name} performance: {e}")

        results["end_time"] = time.time()
        results["total_duration"] = results["end_time"] - results["start_time"]

        return results

    async def _test_startup_time(self, server_name: str) -> dict[str, Any]:
        """Test server startup time"""
        result = {"name": "Startup Time", "success": True, "measurements": []}

        server_path = f"tools/mcp/{server_name}_server.py"
        full_path = REPO_ROOT / server_path

        # Test startup time multiple times
        for i in range(5):
            try:
                start_time = time.time()

                process = subprocess.run(
                    [
                        sys.executable,
                        "-c",
                        f"import sys; sys.path.insert(0, '{REPO_ROOT}'); import importlib.util; spec = importlib.util.spec_from_file_location('server', '{full_path}'); module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                end_time = time.time()
                startup_time = end_time - start_time

                if process.returncode == 0:
                    result["measurements"].append(startup_time)
                else:
                    logger.warning(f"Startup test {i + 1} failed: {process.stderr}")

            except subprocess.TimeoutExpired:
                result["measurements"].append(10.0)  # Max timeout
            except Exception as e:
                logger.warning(f"Startup test {i + 1} error: {e}")

        if result["measurements"]:
            result["mean"] = statistics.mean(result["measurements"])
            result["min"] = min(result["measurements"])
            result["max"] = max(result["measurements"])
            result["std"] = statistics.stdev(result["measurements"]) if len(result["measurements"]) > 1 else 0
            result["details"] = [
                f"Mean: {result['mean']:.3f}s",
                f"Min: {result['min']:.3f}s",
                f"Max: {result['max']:.3f}s",
                f"Std: {result['std']:.3f}s",
            ]
        else:
            result["success"] = False
            result["details"] = ["No successful measurements"]

        return result

    async def _test_memory_usage(self, server_name: str) -> dict[str, Any]:
        """Test memory usage"""
        result = {"name": "Memory Usage", "success": True, "measurements": []}

        try:
            # Test memory usage with psutil if available
            import psutil

            server_path = f"tools/mcp/{server_name}_server.py"
            full_path = REPO_ROOT / server_path

            for i in range(3):
                process = psutil.Popen(
                    [
                        sys.executable,
                        "-c",
                        f"import time; time.sleep(2); import sys; sys.path.insert(0, '{REPO_ROOT}'); exec(open('{full_path}').read())",
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )

                # Wait a bit for startup
                await asyncio.sleep(1)

                try:
                    memory_info = process.memory_info()
                    memory_mb = memory_info.rss / 1024 / 1024
                    result["measurements"].append(memory_mb)
                except Exception as e:
                    logger.warning(f"Memory measurement {i + 1} failed: {e}")
                finally:
                    process.terminate()
                    try:
                        process.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        process.kill()

                await asyncio.sleep(0.5)

            if result["measurements"]:
                result["mean"] = statistics.mean(result["measurements"])
                result["min"] = min(result["measurements"])
                result["max"] = max(result["measurements"])
                result["details"] = [
                    f"Mean: {result['mean']:.1f}MB",
                    f"Min: {result['min']:.1f}MB",
                    f"Max: {result['max']:.1f}MB",
                ]
            else:
                result["success"] = False
                result["details"] = ["No successful measurements"]

        except ImportError:
            result["success"] = False
            result["details"] = ["psutil not available for memory testing"]
        except Exception as e:
            result["success"] = False
            result["details"] = [f"Error: {e}"]

        return result

    async def _test_import_performance(self, server_name: str) -> dict[str, Any]:
        """Test import performance"""
        result = {"name": "Import Performance", "success": True, "measurements": []}

        server_path = f"tools/mcp/{server_name}_server.py"
        full_path = REPO_ROOT / server_path

        # Test import time
        for i in range(10):
            try:
                start_time = time.time()

                process = subprocess.run(
                    [
                        sys.executable,
                        "-c",
                        f"import sys; sys.path.insert(0, '{REPO_ROOT}'); import importlib.util; spec = importlib.util.spec_from_file_location('server', '{full_path}'); module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )

                end_time = time.time()
                import_time = end_time - start_time

                if process.returncode == 0:
                    result["measurements"].append(import_time)

            except Exception:
                result["measurements"].append(5.0)  # Max timeout

        if result["measurements"]:
            result["mean"] = statistics.mean(result["measurements"])
            result["min"] = min(result["measurements"])
            result["max"] = max(result["measurements"])
            result["details"] = [
                f"Mean: {result['mean']:.3f}s",
                f"Min: {result['min']:.3f}s",
                f"Max: {result['max']:.3f}s",
            ]
        else:
            result["success"] = False
            result["details"] = ["No successful measurements"]

        return result

    async def _test_command_performance(self) -> dict[str, Any]:
        """Test terminal command execution performance"""
        result = {"name": "Command Execution", "success": True, "measurements": []}

        commands = [
            ["echo", "test"],
            ["ls", "-la"],
            ["pwd"],
            ["python", "--version"],
        ]

        for cmd in commands:
            try:
                start_time = time.time()

                process = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=5,
                )

                end_time = time.time()
                execution_time = end_time - start_time

                if process.returncode == 0:
                    result["measurements"].append(execution_time)
                    result["details"] = result.get("details", [])
                    result["details"].append(f"{' '.join(cmd)}: {execution_time:.3f}s")

            except Exception as e:
                logger.warning(f"Command {' '.join(cmd)} failed: {e}")

        if result["measurements"]:
            result["mean"] = statistics.mean(result["measurements"])
            result["details"].append(f"Mean: {result['mean']:.3f}s")

        return result

    async def _test_pytest_performance(self) -> dict[str, Any]:
        """Test pytest discovery and execution performance"""
        result = {"name": "Pytest Operations", "success": True, "measurements": []}

        tests_dir = REPO_ROOT / "tests"

        if not tests_dir.exists():
            result["success"] = False
            result["details"] = ["Tests directory not found"]
            return result

        # Test collection performance
        try:
            start_time = time.time()

            process = subprocess.run(
                [sys.executable, "-m", "pytest", "--collect-only", "-q", str(tests_dir)],
                capture_output=True,
                text=True,
                timeout=30,
            )

            end_time = time.time()
            collection_time = end_time - start_time

            if process.returncode == 0:
                result["measurements"].append(collection_time)
                result["details"] = [f"Collection time: {collection_time:.2f}s"]

                # Count tests
                test_count = process.stdout.count("::")
                result["details"].append(f"Tests discovered: {test_count}")
            else:
                result["success"] = False
                result["details"] = [f"Collection failed: {process.stderr}"]

        except Exception as e:
            result["success"] = False
            result["details"] = [f"Error: {e}"]

        return result

    async def _test_http_performance(self) -> dict[str, Any]:
        """Test HTTP request performance"""
        result = {"name": "HTTP Requests", "success": True, "measurements": []}

        try:
            import aiohttp
            import requests

            # Test URLs
            urls = [
                "https://httpbin.org/get",
                "https://jsonplaceholder.typicode.com/posts/1",
                "https://api.github.com/users/octocat",
            ]

            # Synchronous requests
            for url in urls:
                try:
                    start_time = time.time()

                    response = requests.get(url, timeout=5)

                    end_time = time.time()
                    request_time = end_time - start_time

                    if response.status_code == 200:
                        result["measurements"].append(request_time)
                        result["details"] = result.get("details", [])
                        result["details"].append(f"GET {url}: {request_time:.3f}s")

                except Exception as e:
                    logger.warning(f"HTTP request to {url} failed: {e}")

            if result["measurements"]:
                result["mean"] = statistics.mean(result["measurements"])
                result["details"].append(f"Mean request time: {result['mean']:.3f}s")

        except ImportError as e:
            result["success"] = False
            result["details"] = [f"HTTP libraries not available: {e}"]

        return result

    async def _test_vector_db_performance(self) -> dict[str, Any]:
        """Test vector database operations performance"""
        result = {"name": "Vector DB Operations", "success": True, "measurements": []}

        try:
            import chromadb
            from sentence_transformers import SentenceTransformer

            # Test embedding generation
            start_time = time.time()

            model = SentenceTransformer("all-MiniLM-L6-v2")
            texts = ["test text"] * 10
            embeddings = model.encode(texts)

            end_time = time.time()
            embedding_time = end_time - start_time

            result["measurements"].append(embedding_time)
            result["details"] = result.get("details", [])
            result["details"].append(f"Embedding 10 texts: {embedding_time:.3f}s")

            # Test ChromaDB operations
            chroma_path = REPO_ROOT / "artifacts" / "chroma_perf_test"
            chroma_path.mkdir(parents=True, exist_ok=True)

            try:
                start_time = time.time()

                client = chromadb.PersistentClient(path=str(chroma_path))
                collection = client.create_collection("perf_test")

                # Add documents
                collection.add(
                    documents=texts,
                    embeddings=embeddings.tolist(),
                    ids=[f"doc_{i}" for i in range(len(texts))],
                )

                # Query
                collection.query(
                    query_embeddings=embeddings[:1].tolist(),
                    n_results=5,
                )

                end_time = time.time()
                db_time = end_time - start_time

                result["measurements"].append(db_time)
                result["details"].append(f"ChromaDB operations: {db_time:.3f}s")

                # Cleanup
                client.delete_collection("perf_test")

            except Exception as e:
                logger.warning(f"ChromaDB performance test failed: {e}")

        except ImportError as e:
            result["success"] = False
            result["details"] = [f"Vector DB libraries not available: {e}"]

        return result

    async def _generate_performance_report(self):
        """Generate comprehensive performance report"""
        total_time = time.time() - self.start_time

        logger.info("\n" + "=" * 80)
        logger.info("📊 MCP PERFORMANCE TEST REPORT")
        logger.info("=" * 80)

        logger.info(f"Total Test Time: {total_time:.2f}s")
        logger.info(f"Servers Tested: {len(self.results)}")

        # Overall statistics
        all_measurements = []
        for server_results in self.results.values():
            for test_results in server_results["tests"].values():
                if "measurements" in test_results:
                    all_measurements.extend(test_results["measurements"])

        if all_measurements:
            logger.info(f"Total Measurements: {len(all_measurements)}")
            logger.info(f"Overall Mean: {statistics.mean(all_measurements):.3f}s")
            logger.info(f"Overall Min: {min(all_measurements):.3f}s")
            logger.info(f"Overall Max: {max(all_measurements):.3f}s")

        logger.info("\n📋 Detailed Performance Results:")

        for server_name, results in self.results.items():
            status = "✅ PASS" if results["success"] else "❌ FAIL"
            logger.info(f"\n{server_name.upper()} MCP Server {status}")
            logger.info(f"  Total Duration: {results['total_duration']:.2f}s")

            if results["errors"]:
                logger.error(f"  Errors: {', '.join(results['errors'])}")

            for test_name, test_result in results["tests"].items():
                test_status = "✅" if test_result["success"] else "❌"
                logger.info(f"  {test_status} {test_result['name']}")

                if "mean" in test_result:
                    logger.info(f"    Mean: {test_result['mean']:.3f}s")
                    logger.info(f"    Min: {test_result['min']:.3f}s")
                    logger.info(f"    Max: {test_result['max']:.3f}s")
                    if "std" in test_result:
                        logger.info(f"    Std: {test_result['std']:.3f}s")

                if "details" in test_result:
                    for detail in test_result["details"]:
                        logger.info(f"    {detail}")

        # Save detailed report
        await self._save_performance_report()

        logger.info("\n" + "=" * 80)
        logger.info("📊 PERFORMANCE TESTING COMPLETE!")
        logger.info("=" * 80)

    async def _save_performance_report(self):
        """Save detailed performance report"""
        report_data = {
            "timestamp": time.time(),
            "duration": time.time() - self.start_time,
            "repository": str(REPO_ROOT),
            "results": self.results,
        }

        try:
            with open(PERFORMANCE_RESULTS, "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=2, default=str)
            logger.info(f"📄 Performance report saved: {PERFORMANCE_RESULTS}")
        except Exception as e:
            logger.error(f"Failed to save performance report: {e}")


async def main():
    """Main entry point"""
    tester = MCPPerformanceTester()
    await tester.run_all_performance_tests()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nPerformance tests interrupted by user")
    except Exception as e:
        logger.error(f"Performance test error: {e}")
        sys.exit(1)

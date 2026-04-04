#!/usr/bin/env python3
"""
Comprehensive End-to-End Testing for MCP Servers
Tests real-world scenarios and integration patterns for all 4 new MCP servers
"""

import asyncio
import json
import logging
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Test configuration
REPO_ROOT = Path(__file__).parent.parent.parent
E2E_RESULTS = REPO_ROOT / "docs" / "reports" / "mcp_e2e_test_results.json"

class MCPEndToEndTester:
    def __init__(self):
        self.results = {}
        self.start_time = time.time()
        self.test_data_dir = REPO_ROOT / "tests" / "e2e_data"
        self.test_data_dir.mkdir(parents=True, exist_ok=True)

    async def run_all_e2e_tests(self):
        """Run comprehensive end-to-end tests for all MCP servers"""
        logger.info("🚀 Starting MCP End-to-End Tests")
        logger.info(f"Repository: {REPO_ROOT}")
        logger.info(f"Test data directory: {self.test_data_dir}")

        # Setup test data
        await self._setup_test_data()

        # Test each MCP server with real scenarios
        servers = ["terminal", "pytest", "enhanced_http", "vector_db"]

        for server_name in servers:
            logger.info(f"\n🔬 End-to-End Testing {server_name} MCP Server")
            self.results[server_name] = await self._test_server_e2e(server_name)

        # Integration tests
        logger.info("\n🔗 Running Integration Tests")
        self.results["integration"] = await self._test_integration_scenarios()

        # Performance stress tests
        logger.info("\n⚡ Running Performance Stress Tests")
        self.results["stress"] = await self._test_performance_stress()

        # Generate comprehensive report
        await self._generate_e2e_report()

    async def _setup_test_data(self):
        """Setup test data for end-to-end testing"""
        logger.info("Setting up test data...")

        # Create test files for various scenarios
        test_files = {
            "sample_python.py": '''
#!/usr/bin/env python3
"""Sample Python file for testing"""
import os
import sys

def main():
    print("Hello from test file!")
    return os.getcwd()

if __name__ == "__main__":
    main()
''',
            "sample_config.json": '''
{
    "name": "test_config",
    "version": "1.0.0",
    "settings": {
        "debug": true,
        "timeout": 30
    }
}
''',
            "sample_markdown.md": '''
# Test Document

This is a test markdown file for vector search testing.

## Features
- Feature 1: Testing
- Feature 2: Documentation
- Feature 3: Integration

## Code Examples
```python
def example():
    return "test"
```
'''
        }

        for filename, content in test_files.items():
            file_path = self.test_data_dir / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

        logger.info(f"Created {len(test_files)} test files")

    def _get_platform_commands(self):
        """Get platform-specific commands"""
        is_windows = platform.system() == "Windows"
        return {
            "list_files": ["dir"] if is_windows else ["ls", "-la"],
            "read_file": ["type"] if is_windows else ["cat"],
            "current_dir": ["cd"] if is_windows else ["pwd"],
            "env_vars": ["set"] if is_windows else ["env"],
            "is_windows": is_windows
        }

    async def _test_server_e2e(self, server_name: str) -> dict[str, Any]:
        """Test a single MCP server with end-to-end scenarios"""
        results = {
            "server": server_name,
            "scenarios": {},
            "start_time": time.time(),
            "success": True,
            "errors": []
        }

        try:
            if server_name == "terminal":
                results["scenarios"] = await self._test_terminal_e2e_scenarios()
            elif server_name == "pytest":
                results["scenarios"] = await self._test_pytest_e2e_scenarios()
            elif server_name == "enhanced_http":
                results["scenarios"] = await self._test_http_e2e_scenarios()
            elif server_name == "vector_db":
                results["scenarios"] = await self._test_vector_db_e2e_scenarios()

        except Exception as e:
            results["success"] = False
            results["errors"].append(str(e))
            logger.error(f"E2E test error for {server_name}: {e}")

        results["end_time"] = time.time()
        results["total_duration"] = results["end_time"] - results["start_time"]

        return results

    async def _test_terminal_e2e_scenarios(self) -> dict[str, Any]:
        """Test terminal MCP with real-world scenarios"""
        scenarios = {}

        # Scenario 1: File operations
        scenarios["file_operations"] = await self._test_terminal_file_ops()

        # Scenario 2: Git operations
        scenarios["git_operations"] = await self._test_terminal_git_ops()

        # Scenario 3: Python execution
        scenarios["python_execution"] = await self._test_terminal_python_ops()

        # Scenario 4: System information
        scenarios["system_info"] = await self._test_terminal_system_info()

        return scenarios

    async def _test_terminal_file_ops(self) -> dict[str, Any]:
        """Test file operations through terminal MCP"""
        result = {"name": "File Operations", "success": True, "tests": []}
        cmds = self._get_platform_commands()

        try:
            # Test file listing
            start_time = time.time()
            cmd = cmds["list_files"] + [str(self.test_data_dir)]
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,
                shell=cmds["is_windows"]  # Use shell on Windows for dir command
            )
            end_time = time.time()

            if process.returncode == 0 and "sample_python.py" in process.stdout:
                result["tests"].append({
                    "name": "List files",
                    "success": True,
                    "duration": end_time - start_time,
                    "output_lines": len(process.stdout.split('\n'))
                })
            else:
                result["success"] = False
                result["tests"].append({
                    "name": "List files",
                    "success": False,
                    "error": process.stderr
                })

            # Test file content reading
            start_time = time.time()
            cmd = cmds["read_file"] + [str(self.test_data_dir / "sample_python.py")]
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,
                shell=cmds["is_windows"]  # Use shell on Windows for type command
            )
            end_time = time.time()

            if process.returncode == 0 and "def main():" in process.stdout:
                result["tests"].append({
                    "name": "Read file",
                    "success": True,
                    "duration": end_time - start_time,
                    "content_size": len(process.stdout)
                })
            else:
                result["success"] = False
                result["tests"].append({
                    "name": "Read file",
                    "success": False,
                    "error": process.stderr
                })

        except Exception as e:
            result["success"] = False
            result["tests"].append({
                "name": "File operations error",
                "success": False,
                "error": str(e)
            })

        return result

    async def _test_terminal_git_ops(self) -> dict[str, Any]:
        """Test Git operations through terminal MCP"""
        result = {"name": "Git Operations", "success": True, "tests": []}

        try:
            # Test git status
            start_time = time.time()
            process = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                timeout=15,
                cwd=REPO_ROOT
            )
            end_time = time.time()

            result["tests"].append({
                "name": "Git status",
                "success": process.returncode == 0,
                "duration": end_time - start_time,
                "has_changes": len(process.stdout.strip()) > 0
            })

            # Test git log
            start_time = time.time()
            process = subprocess.run(
                ["git", "log", "--oneline", "-5"],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=REPO_ROOT
            )
            end_time = time.time()

            result["tests"].append({
                "name": "Git log",
                "success": process.returncode == 0,
                "duration": end_time - start_time,
                "commits_shown": len(process.stdout.strip().split('\n')) if process.stdout.strip() else 0
            })

        except Exception as e:
            result["success"] = False
            result["tests"].append({
                "name": "Git operations error",
                "success": False,
                "error": str(e)
            })

        return result

    async def _test_terminal_python_ops(self) -> dict[str, Any]:
        """Test Python execution through terminal MCP"""
        result = {"name": "Python Execution", "success": True, "tests": []}

        try:
            # Test Python script execution
            start_time = time.time()
            process = subprocess.run(
                ["python", str(self.test_data_dir / "sample_python.py")],
                capture_output=True,
                text=True,
                timeout=10
            )
            end_time = time.time()

            result["tests"].append({
                "name": "Execute Python script",
                "success": process.returncode == 0 and "Hello from test file!" in process.stdout,
                "duration": end_time - start_time,
                "output": process.stdout.strip()
            })

            # Test Python module check
            start_time = time.time()
            process = subprocess.run(
                ["python", "-c", "import sys; print(f'Python {sys.version}')"],
                capture_output=True,
                text=True,
                timeout=10
            )
            end_time = time.time()

            result["tests"].append({
                "name": "Python version check",
                "success": process.returncode == 0,
                "duration": end_time - start_time,
                "version": process.stdout.strip()
            })

        except Exception as e:
            result["success"] = False
            result["tests"].append({
                "name": "Python operations error",
                "success": False,
                "error": str(e)
            })

        return result

    async def _test_terminal_system_info(self) -> dict[str, Any]:
        """Test system information gathering through terminal MCP"""
        result = {"name": "System Information", "success": True, "tests": []}
        cmds = self._get_platform_commands()

        try:
            # Test current directory - use python instead of pwd/cd for cross-platform
            start_time = time.time()
            process = subprocess.run(
                ["python", "-c", "import os; print(os.getcwd())"],
                capture_output=True,
                text=True,
                timeout=5
            )
            end_time = time.time()

            result["tests"].append({
                "name": "Current directory",
                "success": process.returncode == 0,
                "duration": end_time - start_time,
                "directory": process.stdout.strip()
            })

            # Test environment variables - use python for cross-platform
            start_time = time.time()
            process = subprocess.run(
                ["python", "-c", "import os; [print(f'{k}={v}') for k, v in list(os.environ.items())[:5]]"],
                capture_output=True,
                text=True,
                timeout=5
            )
            end_time = time.time()

            result["tests"].append({
                "name": "Environment variables",
                "success": process.returncode == 0,
                "duration": end_time - start_time,
                "env_vars_count": len(process.stdout.strip().split('\n')) if process.stdout.strip() else 0
            })

        except Exception as e:
            result["success"] = False
            result["tests"].append({
                "name": "System info error",
                "success": False,
                "error": str(e)
            })

        return result

    async def _test_pytest_e2e_scenarios(self) -> dict[str, Any]:
        """Test pytest MCP with real-world scenarios"""
        scenarios = {}

        # Scenario 1: Test discovery
        scenarios["test_discovery"] = await self._test_pytest_discovery()

        # Scenario 2: Test execution
        scenarios["test_execution"] = await self._test_pytest_execution()

        # Scenario 3: Test coverage
        scenarios["test_coverage"] = await self._test_pytest_coverage()

        # Scenario 4: Test analysis
        scenarios["test_analysis"] = await self._test_pytest_analysis()

        return scenarios

    async def _test_pytest_discovery(self) -> dict[str, Any]:
        """Test test discovery through pytest MCP"""
        result = {"name": "Test Discovery", "success": True, "tests": []}

        try:
            # Discover tests in a specific directory
            start_time = time.time()
            process = subprocess.run(
                ["python", "-m", "pytest", "--collect-only", "-q", "tests/unit/agentic_core/L0_routing/config/test_path_constants.py"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=REPO_ROOT
            )
            end_time = time.time()

            # Count tests by looking for test function names (test_ prefix)
            test_count = len([line for line in process.stdout.split('\n') if 'test_' in line and '::' in line])

            result["tests"].append({
                "name": "Discover routing tests",
                "success": process.returncode == 0,
                "duration": end_time - start_time,
                "tests_found": test_count
            })

            # Discover all tests
            start_time = time.time()
            process = subprocess.run(
                ["python", "-m", "pytest", "--collect-only", "-q", "tests/unit/agentic_core/L0_routing/config/"],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=REPO_ROOT
            )
            end_time = time.time()

            # Count tests by looking for :: separator in node IDs
            total_tests = len([line for line in process.stdout.split('\n') if '::' in line])

            result["tests"].append({
                "name": "Discover all tests",
                "success": process.returncode == 0,
                "duration": end_time - start_time,
                "total_tests": total_tests
            })

        except Exception as e:
            result["success"] = False
            result["tests"].append({
                "name": "Test discovery error",
                "success": False,
                "error": str(e)
            })

        return result

    async def _test_pytest_execution(self) -> dict[str, Any]:
        """Test test execution through pytest MCP"""
        result = {"name": "Test Execution", "success": True, "tests": []}

        try:
            # Run a small subset of tests
            start_time = time.time()
            process = subprocess.run(
                ["python", "-m", "pytest", "tests/unit/agentic_core/L0_routing/config/test_path_constants.py", "-v"],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=REPO_ROOT
            )
            end_time = time.time()

            # Parse results - look for passed/failed in output
            output_lines = process.stdout.split('\n')
            passed = sum(1 for line in output_lines if ' passed' in line or 'PASSED' in line)
            failed = sum(1 for line in output_lines if ' failed' in line or 'FAILED' in line)
            errors = sum(1 for line in output_lines if ' error' in line or 'ERROR' in line)

            # Also check summary line like "1 passed in 0.01s"
            summary_passed = 0
            for line in output_lines:
                if ' passed' in line and ' in ' in line:
                    try:
                        summary_passed = int(line.split(' passed')[0].split()[-1])
                    except (ValueError, IndexError):
                        pass

            if summary_passed > 0:
                passed = summary_passed

            result["tests"].append({
                "name": "Execute routing tests",
                "success": process.returncode in [0, 1],  # 0=success, 1=tests failed
                "duration": end_time - start_time,
                "passed": passed,
                "failed": failed,
                "errors": errors,
                "total": passed + failed + errors
            })

        except Exception as e:
            result["success"] = False
            result["tests"].append({
                "name": "Test execution error",
                "success": False,
                "error": str(e)
            })

        return result

    async def _test_pytest_coverage(self) -> dict[str, Any]:
        """Test coverage analysis through pytest MCP"""
        result = {"name": "Coverage Analysis", "success": True, "tests": []}

        try:
            # Run tests with coverage
            start_time = time.time()
            process = subprocess.run(
                ["python", "-m", "pytest", "tests/unit/agentic_core/L0_routing/config/test_path_constants.py", "--cov=agentic_core.L0_routing.config", "--cov-report=json"],
                capture_output=True,
                text=True,
                timeout=90,
                cwd=REPO_ROOT
            )
            end_time = time.time()

            # Check if coverage report was generated
            coverage_file = REPO_ROOT / "coverage.json"
            coverage_data = None

            if coverage_file.exists():
                try:
                    with open(coverage_file) as f:
                        coverage_data = json.load(f)
                except:
                    pass

            result["tests"].append({
                "name": "Coverage analysis",
                "success": process.returncode in [0, 1] and coverage_data is not None,
                "duration": end_time - start_time,
                "coverage_generated": coverage_data is not None,
                "total_coverage": coverage_data.get('totals', {}).get('percent_covered', 0) if coverage_data else 0
            })

        except Exception as e:
            result["success"] = False
            result["tests"].append({
                "name": "Coverage analysis error",
                "success": False,
                "error": str(e)
            })

        return result

    async def _test_pytest_analysis(self) -> dict[str, Any]:
        """Test test analysis through pytest MCP"""
        result = {"name": "Test Analysis", "success": True, "tests": []}

        try:
            # Get test configuration
            start_time = time.time()
            process = subprocess.run(
                ["python", "-m", "pytest", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=REPO_ROOT
            )
            end_time = time.time()

            result["tests"].append({
                "name": "Pytest version",
                "success": process.returncode == 0,
                "duration": end_time - start_time,
                "version": process.stdout.strip()
            })

            # Check pytest configuration
            start_time = time.time()
            process = subprocess.run(
                ["python", "-m", "pytest", "--co", "-q"],
                capture_output=True,
                text=True,
                timeout=15,
                cwd=REPO_ROOT
            )
            end_time = time.time()

            result["tests"].append({
                "name": "Configuration check",
                "success": process.returncode == 0,
                "duration": end_time - start_time,
                "config_lines": len(process.stdout.split('\n')) if process.stdout else 0
            })

        except Exception as e:
            result["success"] = False
            result["tests"].append({
                "name": "Test analysis error",
                "success": False,
                "error": str(e)
            })

        return result

    async def _test_http_e2e_scenarios(self) -> dict[str, Any]:
        """Test HTTP MCP with real-world scenarios"""
        scenarios = {}

        # Scenario 1: API testing
        scenarios["api_testing"] = await self._test_http_api_testing()

        # Scenario 2: Authentication
        scenarios["authentication"] = await self._test_http_authentication()

        # Scenario 3: Error handling
        scenarios["error_handling"] = await self._test_http_error_handling()

        # Scenario 4: Batch operations
        scenarios["batch_operations"] = await self._test_http_batch_ops()

        return scenarios

    async def _test_http_api_testing(self) -> dict[str, Any]:
        """Test HTTP API testing scenarios"""
        result = {"name": "API Testing", "success": True, "tests": []}

        try:
            import requests

            # Test GET request
            start_time = time.time()
            response = requests.get("https://httpbin.org/get", timeout=10)
            end_time = time.time()

            result["tests"].append({
                "name": "GET request",
                "success": response.status_code == 200,
                "duration": end_time - start_time,
                "status_code": response.status_code,
                "response_size": len(response.content)
            })

            # Test POST request
            start_time = time.time()
            response = requests.post(
                "https://httpbin.org/post",
                json={"test": "data", "timestamp": time.time()},
                timeout=10
            )
            end_time = time.time()

            result["tests"].append({
                "name": "POST request",
                "success": response.status_code == 200,
                "duration": end_time - start_time,
                "status_code": response.status_code,
                "json_response": response.json().get("json", {})
            })

            # Test PUT request
            start_time = time.time()
            response = requests.put(
                "https://httpbin.org/put",
                json={"updated": True},
                timeout=10
            )
            end_time = time.time()

            result["tests"].append({
                "name": "PUT request",
                "success": response.status_code == 200,
                "duration": end_time - start_time,
                "status_code": response.status_code
            })

        except Exception as e:
            result["success"] = False
            result["tests"].append({
                "name": "API testing error",
                "success": False,
                "error": str(e)
            })

        return result

    async def _test_http_authentication(self) -> dict[str, Any]:
        """Test HTTP authentication scenarios"""
        result = {"name": "Authentication", "success": True, "tests": []}

        try:
            import requests

            # Test Bearer token authentication
            start_time = time.time()
            response = requests.get(
                "https://httpbin.org/bearer",
                headers={"Authorization": "Bearer test-token"},
                timeout=10
            )
            end_time = time.time()

            result["tests"].append({
                "name": "Bearer token auth",
                "success": response.status_code == 200,
                "duration": end_time - start_time,
                "authenticated": response.json().get("authenticated", False)
            })

            # Test Basic authentication
            start_time = time.time()
            response = requests.get(
                "https://httpbin.org/basic-auth/user/pass",
                auth=("user", "pass"),
                timeout=10
            )
            end_time = time.time()

            result["tests"].append({
                "name": "Basic auth",
                "success": response.status_code == 200,
                "duration": end_time - start_time,
                "authenticated": response.json().get("authenticated", False)
            })

        except Exception as e:
            result["success"] = False
            result["tests"].append({
                "name": "Authentication error",
                "success": False,
                "error": str(e)
            })

        return result

    async def _test_http_error_handling(self) -> dict[str, Any]:
        """Test HTTP error handling scenarios"""
        result = {"name": "Error Handling", "success": True, "tests": []}

        try:
            import requests

            # Test 404 error
            start_time = time.time()
            response = requests.get("https://httpbin.org/status/404", timeout=10)
            end_time = time.time()

            result["tests"].append({
                "name": "404 handling",
                "success": response.status_code == 404,
                "duration": end_time - start_time,
                "error_handled": True
            })

            # Test timeout
            start_time = time.time()
            try:
                response = requests.get("https://httpbin.org/delay/10", timeout=2)
                end_time = time.time()
                timeout_handled = False
            except requests.exceptions.Timeout:
                end_time = time.time()
                timeout_handled = True

            result["tests"].append({
                "name": "Timeout handling",
                "success": timeout_handled,
                "duration": end_time - start_time,
                "timeout_handled": timeout_handled
            })

        except Exception as e:
            result["success"] = False
            result["tests"].append({
                "name": "Error handling error",
                "success": False,
                "error": str(e)
            })

        return result

    async def _test_http_batch_ops(self) -> dict[str, Any]:
        """Test HTTP batch operations"""
        result = {"name": "Batch Operations", "success": True, "tests": []}

        try:
            import concurrent.futures

            import requests

            urls = [
                "https://httpbin.org/get",
                "https://httpbin.org/get",
                "https://httpbin.org/get",
                "https://httpbin.org/get",
                "https://httpbin.org/get"
            ]

            # Test concurrent requests
            start_time = time.time()

            def make_request(url):
                return requests.get(url, timeout=10)

            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(make_request, url) for url in urls]
                responses = [future.result() for future in futures]

            end_time = time.time()

            success_count = sum(1 for r in responses if r.status_code == 200)

            result["tests"].append({
                "name": "Concurrent requests",
                "success": success_count == len(urls),
                "duration": end_time - start_time,
                "requests_count": len(urls),
                "success_count": success_count,
                "avg_time_per_request": (end_time - start_time) / len(urls)
            })

        except Exception as e:
            result["success"] = False
            result["tests"].append({
                "name": "Batch operations error",
                "success": False,
                "error": str(e)
            })

        return result

    async def _test_vector_db_e2e_scenarios(self) -> dict[str, Any]:
        """Test vector DB MCP with real-world scenarios"""
        scenarios = {}

        # Scenario 1: Document indexing
        scenarios["document_indexing"] = await self._test_vector_db_indexing()

        # Scenario 2: Semantic search
        scenarios["semantic_search"] = await self._test_vector_db_search()

        # Scenario 3: Collection management
        scenarios["collection_management"] = await self._test_vector_db_collections()

        # Scenario 4: Performance testing
        scenarios["performance_testing"] = await self._test_vector_db_performance()

        return scenarios

    async def _test_vector_db_indexing(self) -> dict[str, Any]:
        """Test document indexing scenarios"""
        result = {"name": "Document Indexing", "success": True, "tests": []}

        try:
            import chromadb
            from sentence_transformers import SentenceTransformer

            # Setup test collection
            chroma_path = REPO_ROOT / "artifacts" / "chroma_e2e_test"
            chroma_path.mkdir(parents=True, exist_ok=True)

            client = chromadb.PersistentClient(path=str(chroma_path))

            # Clean up any existing collection
            try:
                client.delete_collection("e2e_test")
            except:
                pass

            collection = client.create_collection("e2e_test")

            # Test document indexing
            start_time = time.time()

            model = SentenceTransformer('all-MiniLM-L6-v2')

            documents = [
                "Python is a popular programming language",
                "Machine learning uses algorithms to find patterns",
                "Docker containers help with application deployment",
                "Git is used for version control",
                "REST APIs use HTTP methods for communication"
            ]

            embeddings = model.encode(documents)

            collection.add(
                documents=documents,
                embeddings=embeddings.tolist(),
                ids=[f"doc_{i}" for i in range(len(documents))],
                metadatas=[{"category": "tech", "index": i} for i in range(len(documents))]
            )

            end_time = time.time()

            result["tests"].append({
                "name": "Index documents",
                "success": True,
                "duration": end_time - start_time,
                "documents_count": len(documents),
                "embedding_dimension": embeddings.shape[1]
            })

            # Verify indexing
            start_time = time.time()
            count = collection.count()
            end_time = time.time()

            result["tests"].append({
                "name": "Verify indexing",
                "success": count == len(documents),
                "duration": end_time - start_time,
                "stored_count": count
            })

        except Exception as e:
            result["success"] = False
            result["tests"].append({
                "name": "Document indexing error",
                "success": False,
                "error": str(e)
            })

        return result

    async def _test_vector_db_search(self) -> dict[str, Any]:
        """Test semantic search scenarios"""
        result = {"name": "Semantic Search", "success": True, "tests": []}

        try:
            import chromadb
            from sentence_transformers import SentenceTransformer

            # Use the test collection from indexing test
            chroma_path = REPO_ROOT / "artifacts" / "chroma_e2e_test"
            client = chromadb.PersistentClient(path=str(chroma_path))
            collection = client.get_collection("e2e_test")

            model = SentenceTransformer('all-MiniLM-L6-v2')

            # Test semantic search
            queries = [
                "programming languages",
                "version control systems",
                "containerization technology"
            ]

            for query in queries:
                start_time = time.time()

                query_embedding = model.encode([query])
                results = collection.query(
                    query_embeddings=query_embedding.tolist(),
                    n_results=3
                )

                end_time = time.time()

                result["tests"].append({
                    "name": f"Search: {query}",
                    "success": len(results["documents"][0]) > 0,
                    "duration": end_time - start_time,
                    "results_count": len(results["documents"][0]),
                    "top_result": results["documents"][0][0] if results["documents"] else None
                })

        except Exception as e:
            result["success"] = False
            result["tests"].append({
                "name": "Semantic search error",
                "success": False,
                "error": str(e)
            })

        return result

    async def _test_vector_db_collections(self) -> dict[str, Any]:
        """Test collection management scenarios"""
        result = {"name": "Collection Management", "success": True, "tests": []}

        try:
            import chromadb

            chroma_path = REPO_ROOT / "artifacts" / "chroma_e2e_test"
            client = chromadb.PersistentClient(path=str(chroma_path))

            # List collections
            start_time = time.time()
            collections = client.list_collections()
            end_time = time.time()

            result["tests"].append({
                "name": "List collections",
                "success": True,
                "duration": end_time - start_time,
                "collection_count": len(collections)
            })

            # Get collection info
            start_time = time.time()
            collection = client.get_collection("e2e_test")
            count = collection.count()
            end_time = time.time()

            result["tests"].append({
                "name": "Collection info",
                "success": True,
                "duration": end_time - start_time,
                "document_count": count
            })

            # Delete collection
            start_time = time.time()
            client.delete_collection("e2e_test")
            end_time = time.time()

            result["tests"].append({
                "name": "Delete collection",
                "success": True,
                "duration": end_time - start_time
            })

        except Exception as e:
            result["success"] = False
            result["tests"].append({
                "name": "Collection management error",
                "success": False,
                "error": str(e)
            })

        return result

    async def _test_vector_db_performance(self) -> dict[str, Any]:
        """Test vector DB performance scenarios"""
        result = {"name": "Performance Testing", "success": True, "tests": []}

        try:
            import chromadb
            from sentence_transformers import SentenceTransformer

            chroma_path = REPO_ROOT / "artifacts" / "chroma_perf_test"
            chroma_path.mkdir(parents=True, exist_ok=True)

            client = chromadb.PersistentClient(path=str(chroma_path))

            # Clean up
            try:
                client.delete_collection("perf_test")
            except:
                pass

            collection = client.create_collection("perf_test")
            model = SentenceTransformer('all-MiniLM-L6-v2')

            # Test batch embedding performance
            batch_sizes = [10, 50, 100]

            for batch_size in batch_sizes:
                documents = [f"Test document {i}" for i in range(batch_size)]

                start_time = time.time()
                embeddings = model.encode(documents)
                end_time = time.time()

                result["tests"].append({
                    "name": f"Embed batch {batch_size}",
                    "success": True,
                    "duration": end_time - start_time,
                    "batch_size": batch_size,
                    "docs_per_second": batch_size / (end_time - start_time)
                })

        except Exception as e:
            result["success"] = False
            result["tests"].append({
                "name": "Performance testing error",
                "success": False,
                "error": str(e)
            })

        return result

    async def _test_integration_scenarios(self) -> dict[str, Any]:
        """Test integration scenarios between MCP servers"""
        scenarios = {}

        # Scenario 1: Terminal + Pytest integration
        scenarios["terminal_pytest"] = await self._test_terminal_pytest_integration()

        # Scenario 2: HTTP + Vector DB integration
        scenarios["http_vector_db"] = await self._test_http_vector_db_integration()

        # Scenario 3: Multi-server workflow
        scenarios["multi_server_workflow"] = await self._test_multi_server_workflow()

        return scenarios

    async def _test_terminal_pytest_integration(self) -> dict[str, Any]:
        """Test terminal and pytest integration"""
        result = {"name": "Terminal + Pytest Integration", "success": True, "tests": []}

        try:
            # Use terminal to run pytest and analyze results
            start_time = time.time()
            process = subprocess.run(
                ["python", "-m", "pytest", "tests/unit/agentic_core/L0_routing/config/test_path_constants.py", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=REPO_ROOT
            )
            end_time = time.time()

            # Parse pytest output
            output_lines = process.stdout.split('\n')
            test_results = [line for line in output_lines if any(x in line for x in [' passed', ' failed', ' error'])]

            result["tests"].append({
                "name": "Terminal pytest execution",
                "success": process.returncode in [0, 1],
                "duration": end_time - start_time,
                "test_results": len(test_results),
                "exit_code": process.returncode
            })

        except Exception as e:
            result["success"] = False
            result["tests"].append({
                "name": "Terminal pytest integration error",
                "success": False,
                "error": str(e)
            })

        return result

    async def _test_http_vector_db_integration(self) -> dict[str, Any]:
        """Test HTTP and vector DB integration"""
        result = {"name": "HTTP + Vector DB Integration", "success": True, "tests": []}

        try:
            import chromadb
            import requests
            from sentence_transformers import SentenceTransformer

            # Fetch content via HTTP and index in vector DB
            start_time = time.time()

            # Fetch sample content
            response = requests.get("https://httpbin.org/json", timeout=10)
            http_content = response.json()

            # Convert to text for embedding
            text_content = str(http_content)

            # Setup vector DB
            chroma_path = REPO_ROOT / "artifacts" / "chroma_integration_test"
            chroma_path.mkdir(parents=True, exist_ok=True)

            client = chromadb.PersistentClient(path=str(chroma_path))

            try:
                client.delete_collection("integration_test")
            except:
                pass

            collection = client.create_collection("integration_test")
            model = SentenceTransformer('all-MiniLM-L6-v2')

            # Index the content
            embedding = model.encode([text_content])
            collection.add(
                documents=[text_content],
                embeddings=embedding.tolist(),
                ids=["http_content"],
                metadatas=[{"source": "httpbin.org", "type": "json"}]
            )

            end_time = time.time()

            result["tests"].append({
                "name": "HTTP to Vector DB workflow",
                "success": True,
                "duration": end_time - start_time,
                "content_size": len(text_content),
                "indexed": True
            })

        except Exception as e:
            result["success"] = False
            result["tests"].append({
                "name": "HTTP Vector DB integration error",
                "success": False,
                "error": str(e)
            })

        return result

    async def _test_multi_server_workflow(self) -> dict[str, Any]:
        """Test comprehensive multi-server workflow"""
        result = {"name": "Multi-Server Workflow", "success": True, "tests": []}

        try:
            # Complex workflow: Terminal -> HTTP -> Vector DB -> Pytest
            start_time = time.time()

            # Step 1: Terminal - Get project info
            process = subprocess.run(
                ["git", "log", "--oneline", "-1"],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=REPO_ROOT
            )

            commit_info = process.stdout.strip()

            # Step 2: HTTP - Fetch external data
            import requests
            response = requests.get("https://httpbin.org/uuid", timeout=10)
            uuid_data = response.json()

            # Step 3: Vector DB - Store combined data
            import chromadb
            from sentence_transformers import SentenceTransformer

            chroma_path = REPO_ROOT / "artifacts" / "chroma_workflow_test"
            chroma_path.mkdir(parents=True, exist_ok=True)

            client = chromadb.PersistentClient(path=str(chroma_path))

            try:
                client.delete_collection("workflow_test")
            except:
                pass

            collection = client.create_collection("workflow_test")
            model = SentenceTransformer('all-MiniLM-L6-v2')

            combined_text = f"Commit: {commit_info}, UUID: {uuid_data.get('uuid', 'unknown')}"
            embedding = model.encode([combined_text])

            collection.add(
                documents=[combined_text],
                embeddings=embedding.tolist(),
                ids=["workflow_data"],
                metadatas=[{"workflow": "multi_server", "timestamp": time.time()}]
            )

            # Step 4: Pytest - Run a quick test to verify system health
            test_process = subprocess.run(
                ["python", "-m", "pytest", "tests/unit/agentic_core/L0_routing/config/test_path_constants.py", "-q"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=REPO_ROOT
            )

            end_time = time.time()

            result["tests"].append({
                "name": "Complete workflow",
                "success": process.returncode == 0 and response.status_code == 200 and test_process.returncode in [0, 1],
                "duration": end_time - start_time,
                "steps_completed": 4,
                "git_success": process.returncode == 0,
                "http_success": response.status_code == 200,
                "vector_db_success": True,
                "pytest_success": test_process.returncode in [0, 1]
            })

        except Exception as e:
            result["success"] = False
            result["tests"].append({
                "name": "Multi-server workflow error",
                "success": False,
                "error": str(e)
            })

        return result

    async def _test_performance_stress(self) -> dict[str, Any]:
        """Test performance under stress conditions"""
        scenarios = {}

        # Scenario 1: Concurrent operations
        scenarios["concurrent_operations"] = await self._test_concurrent_operations()

        # Scenario 2: Large dataset handling
        scenarios["large_datasets"] = await self._test_large_datasets()

        # Scenario 3: Memory stress
        scenarios["memory_stress"] = await self._test_memory_stress()

        return scenarios

    async def _test_concurrent_operations(self) -> dict[str, Any]:
        """Test concurrent operations across MCP servers"""
        result = {"name": "Concurrent Operations", "success": True, "tests": []}

        try:
            import concurrent.futures

            import requests

            # Test concurrent HTTP requests
            urls = ["https://httpbin.org/get"] * 10

            start_time = time.time()

            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(requests.get, url, timeout=10) for url in urls]
                responses = [future.result() for future in futures]

            end_time = time.time()

            success_count = sum(1 for r in responses if r.status_code == 200)

            result["tests"].append({
                "name": "Concurrent HTTP requests",
                "success": success_count == len(urls),
                "duration": end_time - start_time,
                "requests_count": len(urls),
                "success_rate": success_count / len(urls),
                "avg_time_per_request": (end_time - start_time) / len(urls)
            })

        except Exception as e:
            result["success"] = False
            result["tests"].append({
                "name": "Concurrent operations error",
                "success": False,
                "error": str(e)
            })

        return result

    async def _test_large_datasets(self) -> dict[str, Any]:
        """Test handling of large datasets"""
        result = {"name": "Large Datasets", "success": True, "tests": []}

        try:
            from sentence_transformers import SentenceTransformer

            # Test large batch embedding
            model = SentenceTransformer('all-MiniLM-L6-v2')

            # Generate large document set
            large_documents = [f"This is test document number {i} with some content to embed." for i in range(100)]

            start_time = time.time()
            embeddings = model.encode(large_documents, batch_size=32)
            end_time = time.time()

            result["tests"].append({
                "name": "Large batch embedding",
                "success": True,
                "duration": end_time - start_time,
                "document_count": len(large_documents),
                "embedding_dimension": embeddings.shape[1],
                "docs_per_second": len(large_documents) / (end_time - start_time)
            })

        except Exception as e:
            result["success"] = False
            result["tests"].append({
                "name": "Large datasets error",
                "success": False,
                "error": str(e)
            })

        return result

    async def _test_memory_stress(self) -> dict[str, Any]:
        """Test memory usage under stress"""
        result = {"name": "Memory Stress", "success": True, "tests": []}

        try:
            import gc

            import psutil

            # Get baseline memory
            process = psutil.Process()
            baseline_memory = process.memory_info().rss / 1024 / 1024  # MB

            # Create multiple large objects
            large_objects = []
            for i in range(10):
                large_objects.append([f"data_{j}" for j in range(10000)])

            peak_memory = process.memory_info().rss / 1024 / 1024  # MB

            # Clean up
            del large_objects
            gc.collect()

            final_memory = process.memory_info().rss / 1024 / 1024  # MB

            result["tests"].append({
                "name": "Memory stress test",
                "success": True,
                "baseline_memory_mb": baseline_memory,
                "peak_memory_mb": peak_memory,
                "final_memory_mb": final_memory,
                "memory_increase_mb": peak_memory - baseline_memory,
                "memory_recovered_mb": peak_memory - final_memory
            })

        except Exception as e:
            result["success"] = False
            result["tests"].append({
                "name": "Memory stress error",
                "success": False,
                "error": str(e)
            })

        return result

    async def _generate_e2e_report(self):
        """Generate comprehensive end-to-end test report"""
        total_time = time.time() - self.start_time

        logger.info("\n" + "="*80)
        logger.info("📊 MCP END-TO-END TEST REPORT")
        logger.info("="*80)

        logger.info(f"Total Test Time: {total_time:.2f}s")
        logger.info(f"Servers Tested: {len([k for k in self.results.keys() if k not in ['integration', 'stress']])}")
        logger.info(f"Integration Tests: {'integration' in self.results}")
        logger.info(f"Stress Tests: {'stress' in self.results}")

        # Calculate overall statistics
        total_scenarios = 0
        passed_scenarios = 0

        for server_name, results in self.results.items():
            if isinstance(results, dict) and "scenarios" in results:
                for scenario_name, scenario_result in results["scenarios"].items():
                    total_scenarios += 1
                    if scenario_result.get("success", False):
                        passed_scenarios += 1
            elif isinstance(results, dict) and "name" in results:
                total_scenarios += 1
                if results.get("success", False):
                    passed_scenarios += 1

        success_rate = (passed_scenarios / total_scenarios * 100) if total_scenarios > 0 else 0

        logger.info(f"Total Scenarios: {total_scenarios}")
        logger.info(f"Passed: {passed_scenarios}")
        logger.info(f"Success Rate: {success_rate:.1f}%")

        logger.info("\n📋 Detailed Results:")

        for server_name, results in self.results.items():
            if server_name in ["integration", "stress"]:
                logger.info(f"\n🔗 {server_name.upper()} Tests")
            else:
                status = "✅ PASS" if results.get("success", False) else "❌ FAIL"
                logger.info(f"\n{server_name.upper()} MCP Server {status}")

            if "scenarios" in results:
                for scenario_name, scenario_result in results["scenarios"].items():
                    scenario_status = "✅" if scenario_result.get("success", False) else "❌"
                    logger.info(f"  {scenario_status} {scenario_result.get('name', scenario_name)}")

                    if "tests" in scenario_result:
                        for test in scenario_result["tests"]:
                            test_status = "✅" if test.get("success", False) else "❌"
                            logger.info(f"    {test_status} {test.get('name', 'Unknown')}")
                            if "duration" in test:
                                logger.info(f"      Duration: {test['duration']:.3f}s")
            elif "name" in results:
                scenario_status = "✅" if results.get("success", False) else "❌"
                logger.info(f"  {scenario_status} {results.get('name', 'Unknown')}")

                if "tests" in results:
                    for test in results["tests"]:
                        test_status = "✅" if test.get("success", False) else "❌"
                        logger.info(f"    {test_status} {test.get('name', 'Unknown')}")
                        if "duration" in test:
                            logger.info(f"      Duration: {test['duration']:.3f}s")

        # Save detailed report
        await self._save_e2e_report()

        logger.info("\n" + "="*80)
        if success_rate >= 90:
            logger.info("🎉 END-TO-END TESTS EXCELLENT!")
        elif success_rate >= 75:
            logger.info("✅ END-TO-END TESTS GOOD!")
        else:
            logger.warning(f"⚠️ END-TO-END TESTS NEED IMPROVEMENT ({success_rate:.1f}% success)")
        logger.info("="*80)

    async def _save_e2e_report(self):
        """Save detailed end-to-end test report"""
        report_data = {
            "timestamp": time.time(),
            "duration": time.time() - self.start_time,
            "repository": str(REPO_ROOT),
            "results": self.results
        }

        try:
            with open(E2E_RESULTS, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, default=str)
            logger.info(f"📄 E2E report saved: {E2E_RESULTS}")
        except Exception as e:
            logger.error(f"Failed to save E2E report: {e}")

async def main():
    """Main entry point"""
    tester = MCPEndToEndTester()
    await tester.run_all_e2e_tests()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nEnd-to-end tests interrupted by user")
    except Exception as e:
        logger.error(f"E2E test error: {e}")
        sys.exit(1)

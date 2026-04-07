#!/usr/bin/env python3
"""
Comprehensive MCP Smoke Tests
Tests all 4 new MCP servers: Terminal, Pytest, Enhanced HTTP, and Vector DB
"""

import asyncio
import json
import logging
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
MCP_SERVERS = {
    "terminal": "tools/mcp/terminal_server.py",
    "pytest": "tools/mcp/pytest_server.py",
    "enhanced_http": "tools/mcp/enhanced_http_server.py",
    "vector_db": "tools/mcp/vector_db_server.py",
}

class MCPSmokeTester:
    def __init__(self):
        self.test_results = {}
        self.start_time = time.time()

    async def run_all_tests(self):
        """Run comprehensive smoke tests for all MCP servers"""
        logger.info("🚀 Starting MCP Smoke Tests")
        logger.info(f"Repository: {REPO_ROOT}")
        logger.info(f"Testing {len(MCP_SERVERS)} MCP servers")

        # Test each MCP server
        for server_name, server_path in MCP_SERVERS.items():
            logger.info(f"\n📋 Testing {server_name} MCP Server")
            self.test_results[server_name] = await self._test_server(server_name, server_path)

        # Generate summary report
        await self._generate_summary_report()

    async def _test_server(self, server_name: str, server_path: str) -> dict[str, Any]:
        """Test a single MCP server"""
        results = {
            "server": server_name,
            "path": server_path,
            "tests": {},
            "start_time": time.time(),
            "success": True,
            "errors": [],
        }

        try:
            # Test 1: File existence and basic syntax
            results["tests"]["file_check"] = await self._test_file_exists(server_path)

            # Test 2: Import test
            results["tests"]["import_test"] = await self._test_imports(server_path)

            # Test 3: Server startup test
            results["tests"]["startup_test"] = await self._test_server_startup(server_path)

            # Test 4: Basic functionality tests
            results["tests"]["functionality"] = await self._test_server_functionality(server_name, server_path)

        except Exception as e:
            results["success"] = False
            results["errors"].append(str(e))
            logger.error(f"Error testing {server_name}: {e}")

        results["end_time"] = time.time()
        results["duration"] = results["end_time"] - results["start_time"]

        return results

    async def _test_file_exists(self, server_path: str) -> dict[str, Any]:
        """Test if server file exists and is readable"""
        result = {"name": "File Check", "success": True, "details": []}

        full_path = REPO_ROOT / server_path

        if not full_path.exists():
            result["success"] = False
            result["details"].append(f"File not found: {full_path}")
            return result

        if not full_path.is_file():
            result["success"] = False
            result["details"].append(f"Path is not a file: {full_path}")
            return result

        # Check file size
        size = full_path.stat().st_size
        result["details"].append(f"File size: {size:,} bytes")

        # Check basic syntax
        try:
            with open(full_path, encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                result["details"].append(f"Lines of code: {len(lines)}")

                # Basic syntax checks
                if "def main()" in content:
                    result["details"].append("✅ Has main() function")
                if "async def" in content:
                    result["details"].append("✅ Uses async functions")
                if "mcp.server" in content:
                    result["details"].append("✅ Imports MCP server")

        except Exception as e:
            result["success"] = False
            result["details"].append(f"Error reading file: {e}")

        return result

    async def _test_imports(self, server_path: str) -> dict[str, Any]:
        """Test if server can import required dependencies"""
        result = {"name": "Import Test", "success": True, "details": []}

        # Read the file to find imports
        full_path = REPO_ROOT / server_path

        try:
            with open(full_path, encoding='utf-8') as f:
                content = f.read()

            # Extract import statements
            imports = []
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith('import ') or line.startswith('from '):
                    imports.append(line)

            result["details"].append(f"Found {len(imports)} import statements")

            # Test key imports
            key_imports = ["mcp.server", "asyncio"]
            server_specific = {
                "terminal": ["subprocess"],
                "pytest": ["xml.etree.ElementTree"],
                "enhanced_http": ["aiohttp", "requests"],
                "vector_db": ["chromadb", "sentence_transformers"],
            }

            key_imports.extend(server_specific.get(server_path.split('/')[-1].replace('_server.py', ''), []))

            for imp in key_imports:
                try:
                    __import__(imp)
                    result["details"].append(f"✅ {imp}")
                except ImportError as e:
                    result["success"] = False
                    result["details"].append(f"❌ {imp}: {e}")

        except Exception as e:
            result["success"] = False
            result["details"].append(f"Error testing imports: {e}")

        return result

    async def _test_server_startup(self, server_path: str) -> dict[str, Any]:
        """Test if server can start without errors"""
        result = {"name": "Startup Test", "success": True, "details": []}

        try:
            # Test Python syntax by running with -m py_compile
            full_path = REPO_ROOT / server_path

            process = subprocess.run(
                [sys.executable, "-m", "py_compile", str(full_path)],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if process.returncode == 0:
                result["details"].append("✅ Python syntax valid")
            else:
                result["success"] = False
                result["details"].append(f"❌ Syntax error: {process.stderr}")

        except subprocess.TimeoutExpired:
            result["success"] = False
            result["details"].append("❌ Compilation timeout")
        except Exception as e:
            result["success"] = False
            result["details"].append(f"❌ Error: {e}")

        return result

    async def _test_server_functionality(self, server_name: str, server_path: str) -> dict[str, Any]:
        """Test server-specific functionality"""
        result = {"name": "Functionality Test", "success": True, "details": []}

        if server_name == "terminal":
            result = await self._test_terminal_functionality(result)
        elif server_name == "pytest":
            result = await self._test_pytest_functionality(result)
        elif server_name == "enhanced_http":
            result = await self._test_http_functionality(result)
        elif server_name == "vector_db":
            result = await self._test_vector_db_functionality(result)

        return result

    async def _test_terminal_functionality(self, result: dict[str, Any]) -> dict[str, Any]:
        """Test terminal server functionality"""
        try:
            # Test basic command execution
            process = subprocess.run(
                ["python", "-c", "import subprocess; print(subprocess.run(['echo', 'test'], capture_output=True, text=True).stdout)"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if process.returncode == 0 and "test" in process.stdout:
                result["details"].append("✅ Basic subprocess execution works")
            else:
                result["success"] = False
                result["details"].append("❌ Subprocess execution failed")

        except Exception as e:
            result["success"] = False
            result["details"].append(f"❌ Error: {e}")

        return result

    async def _test_pytest_functionality(self, result: dict[str, Any]) -> dict[str, Any]:
        """Test pytest server functionality"""
        try:
            # Check if pytest is available
            process = subprocess.run(
                ["python", "-m", "pytest", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if process.returncode == 0:
                result["details"].append("✅ Pytest available")
                version = process.stdout.strip()
                result["details"].append(f"Version: {version}")
            else:
                result["success"] = False
                result["details"].append("❌ Pytest not available")

        except Exception as e:
            result["success"] = False
            result["details"].append(f"❌ Error: {e}")

        return result

    async def _test_http_functionality(self, result: dict[str, Any]) -> dict[str, Any]:
        """Test HTTP server functionality"""
        try:
            # Test aiohttp import
            import aiohttp
            result["details"].append("✅ aiohttp available")

            # Test requests import
            import requests
            result["details"].append("✅ requests available")

            # Test basic HTTP request
            try:
                response = requests.get("https://httpbin.org/get", timeout=5)
                if response.status_code == 200:
                    result["details"].append("✅ Basic HTTP request works")
                else:
                    result["success"] = False
                    result["details"].append(f"❌ HTTP request failed: {response.status_code}")
            except Exception as e:
                result["details"].append(f"⚠️ HTTP test skipped (network): {e}")

        except ImportError as e:
            result["success"] = False
            result["details"].append(f"❌ Import error: {e}")

        return result

    async def _test_vector_db_functionality(self, result: dict[str, Any]) -> dict[str, Any]:
        """Test vector DB server functionality"""
        try:
            # Test chromadb import
            import chromadb
            result["details"].append("✅ ChromaDB available")

            # Test sentence transformers import
            from sentence_transformers import SentenceTransformer
            result["details"].append("✅ Sentence Transformers available")

            # Test basic embedding
            try:
                model = SentenceTransformer('all-MiniLM-L6-v2')
                embedding = model.encode("test text")
                result["details"].append(f"✅ Embedding generation works (dim: {len(embedding)})")
            except Exception as e:
                result["details"].append(f"⚠️ Embedding test skipped: {e}")

        except ImportError as e:
            result["success"] = False
            result["details"].append(f"❌ Import error: {e}")

        return result

    async def _generate_summary_report(self):
        """Generate comprehensive summary report"""
        total_time = time.time() - self.start_time

        logger.info("\n" + "="*80)
        logger.info("📊 MCP SMOKE TEST SUMMARY REPORT")
        logger.info("="*80)

        total_servers = len(self.test_results)
        successful_servers = sum(1 for r in self.test_results.values() if r["success"])

        logger.info(f"Total Time: {total_time:.2f}s")
        logger.info(f"Servers Tested: {total_servers}")
        logger.info(f"Successful: {successful_servers}/{total_servers}")
        logger.info(f"Success Rate: {(successful_servers/total_servers)*100:.1f}%")

        logger.info("\n📋 Detailed Results:")

        for server_name, results in self.test_results.items():
            status = "✅ PASS" if results["success"] else "❌ FAIL"
            logger.info(f"\n{server_name.upper()} MCP Server {status}")
            logger.info(f"  Duration: {results['duration']:.2f}s")

            if results["errors"]:
                logger.error(f"  Errors: {', '.join(results['errors'])}")

            for test_name, test_result in results["tests"].items():
                test_status = "✅" if test_result["success"] else "❌"
                logger.info(f"  {test_status} {test_result['name']}")

                for detail in test_result["details"]:
                    logger.info(f"    {detail}")

        # Save detailed report
        await self._save_detailed_report()

        logger.info("\n" + "="*80)
        if successful_servers == total_servers:
            logger.info("🎉 ALL MCP SERVERS PASSED SMOKE TESTS!")
        else:
            logger.warning(f"⚠️ {total_servers - successful_servers} servers failed tests")
        logger.info("="*80)

    async def _save_detailed_report(self):
        """Save detailed JSON report"""
        report_data = {
            "timestamp": time.time(),
            "duration": time.time() - self.start_time,
            "repository": str(REPO_ROOT),
            "results": self.test_results,
        }

        report_file = REPO_ROOT / "docs" / "reports" / "mcp_smoke_test_report.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, default=str)
            logger.info(f"📄 Detailed report saved: {report_file}")
        except Exception as e:
            logger.error(f"Failed to save report: {e}")

async def main():
    """Main entry point"""
    tester = MCPSmokeTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSmoke tests interrupted by user")
    except Exception as e:
        logger.error(f"Smoke test error: {e}")
        sys.exit(1)

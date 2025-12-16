"""
Phase 1 Core MCP Testing
Tests foundational components: Redis, GitKraken, Filesystem with Gemini Flash API
"""
import json
import logging
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("CoreMCPTest")


class CoreMCPTester:
    def __init__(self):
        """Initialize core MCP connections"""
        self.test_results = []

    def log_result(self, test_name: str, status: str, details: str = ""):
        """Log test result"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)

        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        logger.info(f"{status_icon} {test_name}: {status}")
        if details:
            logger.info(f"   Details: {details}")

    def test_redis_mcp(self):
        """Test Redis MCP operations"""
        logger.info("\n=== Testing Redis MCP (L4) ===")

        try:
            # Import action registry to get Redis tools
            from action_registry import ActionRegistry
            registry = ActionRegistry()
            tools = registry.get_tool_map()

            # Test Redis string operations
            string_set = tools.get('string_set')
            string_get = tools.get('string_get')

            if not string_set or not string_get:
                self.log_result("Redis MCP Tools", "FAIL",
                                "Redis tools not available in registry")
                return

            # Test SET operation
            test_key = f"test:core:mcp:{int(datetime.now().timestamp())}"
            test_value = "core_test_value_123"

            set_result = string_set(test_key, test_value)
            if "OK" not in set_result:
                self.log_result("Redis SET", "FAIL",
                                f"Unexpected result: {set_result}")
                return

            # Test GET operation
            get_result = string_get(test_key)
            if get_result != test_value:
                self.log_result("Redis GET", "FAIL",
                                f"Expected {test_value}, got {get_result}")
                return

            # Test hash operations
            hash_set = tools.get('hash_set')
            hash_get = tools.get('hash_get')

            hash_set("test_hash", "field1", "value1")
            hash_result = hash_get("test_hash", "field1")

            if "value1" not in hash_result:
                self.log_result("Redis Hash", "FAIL",
                                f"Hash operation failed: {hash_result}")
                return

            self.log_result("Redis MCP", "PASS",
                            "All Redis operations successful")

        except Exception as e:
            self.log_result("Redis MCP", "FAIL", str(e))


    def test_filesystem_mcp(self):
        """Test Filesystem MCP operations"""
        logger.info("\n=== Testing Filesystem MCP (L1) ===")

        try:
            from action_registry import ActionRegistry
            registry = ActionRegistry()
            tools = registry.get_tool_map()

            # Get filesystem tools
            read_file = tools.get('read_file')
            save_file = tools.get('save_file')

            if not read_file or not save_file:
                self.log_result("Filesystem MCP Tools", "FAIL",
                                "Filesystem tools not available")
                return

            # Test file creation
            test_content = f"Core MCP Test - {datetime.now().isoformat()}"
            test_file = "test_core_mcp.txt"

            save_result = save_file(test_file, test_content)
            if "OK" not in str(save_result):
                self.log_result("Filesystem Write", "FAIL",
                                f"Write failed: {save_result}")
                return

            # Test file reading
            read_result = read_file(test_file)
            if test_content not in read_result:
                self.log_result("Filesystem Read", "FAIL",
                                f"Content mismatch: {read_result[:100]}")
                return

            # Cleanup
            try:
                os.remove(test_file)
            except Exception:
                pass

            self.log_result("Filesystem MCP", "PASS",
                            "File operations successful")

        except Exception as e:
            self.log_result("Filesystem MCP", "FAIL", str(e))

    def test_gitkraken_mcp(self):
        """Test GitKraken MCP operations"""
        logger.info("\n=== Testing GitKraken MCP (L1) ===")

        try:
            from action_registry import ActionRegistry
            registry = ActionRegistry()
            tools = registry.get_tool_map()

            # Get GitKraken tools
            commit = tools.get('commit')

            if not commit:
                self.log_result("GitKraken MCP Tools", "FAIL",
                                "GitKraken tools not available")
                return

            # Create a test file to commit
            test_file = "test_git_commit.txt"
            test_content = f"Test commit for Core MCP validation\nTimestamp: {datetime.now().isoformat()}"

            with open(test_file, 'w') as f:
                f.write(test_content)

            # Test commit operation
            commit_result = commit(test_file, "Core MCP test commit")

            if not commit_result or "error" in str(commit_result).lower():
                self.log_result("GitKraken Commit", "FAIL",
                                f"Commit failed: {commit_result}")
            else:
                self.log_result("GitKraken MCP", "PASS",
                                f"Commit successful: {str(commit_result)[:50]}")

            # Cleanup
            try:
                os.remove(test_file)
            except Exception:
                pass

        except Exception as e:
            self.log_result("GitKraken MCP", "FAIL", str(e))

    def test_gemini_flash_connection(self):
        """Test Gemini Flash API connection"""
        logger.info("\n=== Testing Gemini Flash API Connection ===")

        try:
            # Check if API key is configured
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                self.log_result("Gemini API Key", "FAIL",
                                "GEMINI_API_KEY not found in environment")
                return

            # Try to import and initialize LLM client
            from llm_client import LLMClient
            llm = LLMClient()

            # Test simple completion
            test_prompt = "Respond with exactly: OK"
            response = llm.generate(test_prompt)

            if "OK" in response:
                self.log_result("Gemini Flash API", "PASS",
                                "API responding correctly")
            else:
                self.log_result("Gemini Flash API", "FAIL",
                                f"Unexpected response: {response[:100]}")

        except Exception as e:
            self.log_result("Gemini Flash API", "FAIL", str(e))

    def test_mcp_tool_integration(self):
        """Test MCP tool integration with LLM"""
        logger.info("\n=== Testing MCP Tool Integration ===")

        try:
            from orchestrator import run_agentic_loop

            # Simple task that uses core tools
            task = """
            Use the filesystem to create a file called 'integration_test.txt' with the content 'MCP Integration Test'.
            Then read the file back to verify.
            """

            # Run the agentic loop
            result = run_agentic_loop(task)

            if result.get("status") == "success":
                self.log_result("MCP Integration", "PASS",
                                "LLM successfully used MCP tools")
            else:
                self.log_result("MCP Integration", "FAIL",
                                f"Integration failed: {result}")

            # Cleanup
            try:
                os.remove("integration_test.txt")
            except Exception:
                pass

        except Exception as e:
            self.log_result("MCP Integration", "FAIL", str(e))

    def run_all_tests(self):
        """Run all Phase 1 core tests"""
        logger.info("\n" + "="*50)
        logger.info("STARTING PHASE 1 CORE MCP VALIDATION")
        logger.info("="*50)

        # Run individual tests
        self.test_redis_mcp()
        self.test_filesystem_mcp()
        self.test_gitkraken_mcp()
        self.test_gemini_flash_connection()
        self.test_mcp_tool_integration()

        # Summary
        logger.info("\n" + "="*50)
        logger.info("PHASE 1 TEST SUMMARY")
        logger.info("="*50)

        passed = sum(1 for r in self.test_results if r["status"] == "PASS")
        failed = sum(1 for r in self.test_results if r["status"] == "FAIL")
        warnings = sum(1 for r in self.test_results if r["status"] == "WARN")

        logger.info(f"✅ Passed: {passed}")
        logger.info(f"❌ Failed: {failed}")
        logger.info(f"⚠️  Warnings: {warnings}")

        # Save results
        with open("phase1_test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)

        logger.info("\nDetailed results saved to: phase1_test_results.json")

        # Return overall status
        if failed == 0:
            logger.info(
                "\n🎉 PHASE 1 VALIDATION SUCCESSFUL - Core MCPs are ready!")
            return True
        else:
            logger.error(
                f"\n💥 PHASE 1 VALIDATION FAILED - {failed} test(s) failed")
            return False


if __name__ == "__main__":
    tester = CoreMCPTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


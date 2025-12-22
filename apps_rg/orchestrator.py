import glob
import json
import logging
import os
import subprocess
import sys

from action_registry import ActionRegistry
from apps_rg.L3_orchestration.toolbox import SAFE_TOOLS, TOOLBOX_DESC  # <--- NEW IMPORT
from cognitive_node import CognitiveNode  # <--- NEW IMPORT
from engines.canon_validator.canon_validator import CanonValidator
from llm_client import LLMClient

# Setup
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Orchestrator")


def get_latest_code_mtime(root_dir: str, exclude_dirs: list = None) -> float:
    """
    Recursively finds the latest modification timestamp among all Python files.
    Skips virtual environments and cache directories to prevent false positives.
    """
    if exclude_dirs is None:
        exclude_dirs = {'.git', '__pycache__', 'venv', 'env', '.idea', '.vscode'}

    latest_mtime = 0.0

    for root, dirs, files in os.walk(root_dir):
        # Modify dirs in-place to skip excluded directories during traversal
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    mtime = os.path.getmtime(file_path)
                    if mtime > latest_mtime:
                        latest_mtime = mtime
                except OSError:
                    pass # Ignore files that might not be accessible

    return latest_mtime

def ensure_manifest_freshness(manifest_path: str, root_dir: str = ".") -> bool:
    """
    Hardened Pre-Flight Check [4a]:
    Ensures manifest exists AND is newer than the latest code change.
    Returns True if fresh, False if stale (triggering Phase A).
    """
    # 1. Existence Check
    if not os.path.exists(manifest_path):
        logger.warning(f"🚫 Manifest missing at {manifest_path}. Triggering Librarian...")
        return False

    # 2. Freshness Check (Time-Based Drift Detection)
    manifest_mtime = os.path.getmtime(manifest_path)
    latest_code_mtime = get_latest_code_mtime(root_dir)

    # Add a small buffer (e.g., 1 second) to handle file system resolution differences
    if latest_code_mtime > (manifest_mtime + 1.0):
        time_diff = latest_code_mtime - manifest_mtime
        logger.warning(f"⚠️  Code drift detected ({time_diff:.2f}s outdated). Triggering Librarian...")
        return False

    logger.info("✅ Manifest is fresh. Proceeding to Phase B runtime.")
    return True

def validate_manifest_integrity(manifest_path: str) -> bool:
    """
    [HARDENED] Quality Gate: Ensures the manifest is valid JSON
    and contains the expected structure before loading it.
    """
    try:
        if not os.path.exists(manifest_path):
            return False

        with open(manifest_path, 'r') as f:
            data = json.load(f)

        # Basic Schema Validation
        if not isinstance(data, dict):
            logging.error("❌ Manifest corruption: Root element is not a dictionary.")
            return False

        # Check for non-empty content (an empty manifest is effectively useless)
        if not data:
            logging.warning("⚠️ Manifest is empty. Librarian may have failed to find files.")

        return True

    except json.JSONDecodeError as e:
        logging.error(f"❌ Manifest corruption: Invalid JSON syntax. {e}")
        return False
    except Exception as e:
        logging.error(f"❌ Manifest validation error: {e}")
        return False




def run_agentic_loop(user_goal: str):
    # print(f"\n🚀 SUBATOMIC AGENT STARTING: {user_goal}")  # [Security Fix]
    # print("="*60)  # [Security Fix]

    manifest_path = "active_manifest.json"

    # [HARDENED 4a & 4b] Check freshness instead of just existence
    if not ensure_manifest_freshness(manifest_path):
        # Trigger Phase A: Librarian Boot Sequence
        try:
            # print("🔄 Re-indexing filesystem (Phase A)...")  # [Security Fix]
            # subprocess.run(["python", "apps_rg/L0_maintenance/deduplicate_and_index.py"], check=True)  # Disabled after manual cleanup

            # [CRITICAL ADDITION] 2. Verify Integrity immediately after generation
            if not validate_manifest_integrity(manifest_path):
                raise RuntimeError("Phase A completed, but generated a corrupt manifest.")

            # print("✅ Sanitization complete & verified.")  # [Security Fix]

        except subprocess.CalledProcessError as e:
            logging.critical(f"🛑 Librarian crashed (Exit Code {e.returncode}). Check logs.")
            sys.exit(1) # Hard Stop
        except RuntimeError as e:
            logging.critical(f"🛑 {e}")
            # Optional: Delete corrupt file to force clean regeneration next time
            if os.path.exists(manifest_path):
                os.remove(manifest_path)
            sys.exit(1) # Hard Stop

    # 1. INITIALIZE COMPONENTS
    validator = CanonValidator()
    LLMClient()
    actions = ActionRegistry()
    cognitive = CognitiveNode()  # <--- NEW COMPONENT

    # 2. Use imported toolbox description
    toolbox_desc = TOOLBOX_DESC


    # 3. THINK SEQUENTIALLY (Generate Draft using the Cognitive Node)
    # The Cognitive Node manages the entire thought process
    try:
        raw_code = cognitive.think(user_goal, toolbox_desc)
    except TimeoutError as e:
        logger.error(f"❌ Sequential thinking timed out: {e}")
        return
    except RuntimeError as e:
        logger.error(f"❌ Sequential thinking failed: {e}")
        return
    except Exception as e:
        logger.error(f"❌ Unexpected error in Cognitive Node: {e}")
        return

    if not raw_code:
        logger.error("❌ Generation failed in Cognitive Node.")
        return

    # print(f"\n📄 DRAFT CODE RECEIVED:\n{'-'*20}\n{raw_code}\n{'-'*20}")  # [Security Fix]

    # 4. AUDIT & REPAIR (The "Golden Loop")
    result = validator.validate(raw_code, auto_repair=True)

    final_code = raw_code
    status = result.get("status")

    if status == "repaired":
        # print(f"\n🔧 AUTO-REPAIR APPLIED!")  # [Security Fix]
        # print(f"📝 Reason: {result.get('reasoning')}")  # [Security Fix]
        final_code = result.get("repaired_code")
        # print(f"✨ NEW CODE:\n{'-'*20}\n{final_code}\n{'-'*20}")  # [Security Fix]
    elif status == "rejected":
        logger.error("❌ Code rejected.")
        return

    # 5. EXECUTE (Action Plane)
    logger.info("⚡ Executing Final Code...")
    try:
        # INJECT ALL TOOLS (Web, File I/O, Mock Email) + SafeToolbox
        # Tools must be in global scope to be accessible inside function definitions
        exec_globals = actions.get_tool_map()
        # Merge SafeToolbox functions into execution context
        exec_globals.update(SAFE_TOOLS)
        exec_globals['__name__'] = '__main__'
        local_scope = {}

        # Execute the code - this defines all functions
        exec(final_code, exec_globals, local_scope)

        # Merge local_scope back into exec_globals so helper functions are accessible
        exec_globals.update(local_scope)

        # Auto-run entry point (find the last defined function that's not a tool)
        tool_names = set(actions.get_tool_map().keys())
        keys = [k for k in local_scope.keys(
        ) if k not in tool_names and "__" not in k and callable(local_scope[k])]
        if keys:
            func_name = keys[-1]
            # print(f"▶️ Running function: {func_name}...")  # [Security Fix]

            # Simple Injection Logic for Logger
            import inspect
            sig = inspect.signature(local_scope[func_name])
            kwargs = {}
            if "logger" in sig.parameters:
                class MockLogger:
                    # def info(self, msg): print(f"INFO: {msg}")  # [Security Fix]
                    # def error(self, msg): print(f"ERROR: {msg}")  # [Security Fix]
                    # def warning(self, msg): print(f"WARN: {msg}")  # [Security Fix]

                    # This prevents the "not callable" error
                    def __call__(self, *args, **kwargs):
                        """Handle cases where agents try to call logger('message') directly."""
                        if args:
                            self.info(args[0])
                kwargs["logger"] = MockLogger()

            res = local_scope[func_name](**kwargs)
            # print(f"✅ RESULT: {res}")  # [Security Fix]

    except Exception as e:
        logger.error(f"Runtime Error: {e}")


def pre_flight_check(skip_purge=False):
    """Ensures the environment is in a Golden State before booting."""
    if skip_purge:
        logger.info("✅ Pre-flight: Skipping purge (duplicates already cleaned).")
    else:
        try:
            from clean_duplicates import purge_everything
            purge_everything()
            logger.info("✅ Pre-flight: Duplicates purged.")
        except ImportError:
            logger.warning("⚠️ clean_duplicates.py not found, skipping pre-flight.")
        except Exception as e:
            logger.error(f"⚠️ Pre-flight cleanup failed: {e}")


if __name__ == "__main__":
    import argparse

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Agentic Workflow Orchestrator")
    parser.add_argument("--task", choices=["resume_generation", "architectural_review", "outreach_campaign"],
                       default="architectural_review", help="Specify the task to execute")
    parser.add_argument("--skip-purge", action="store_true", help="Skip the duplicate file purge")
    args = parser.parse_args()

    # Run pre-flight check to maintain Golden State
    pre_flight_check(skip_purge=args.skip_purge)

    # Set the user goal based on the task
    if args.task == "resume_generation":
        user_goal = """
        Generate a professional resume for a software engineer with 5 years of experience.
        Focus on technical skills, project achievements, and quantifiable impact.
        Use the Resume Engine to create a compelling narrative that highlights expertise in cloud technologies,
        software development, and team leadership.
        """
    elif args.task == "outreach_campaign":
        user_goal = """
        Create a personalized LinkedIn outreach campaign for a SaaS product targeting CTOs and VPs of Engineering.
        Use the Outreach Engine to craft compelling messages that highlight value proposition,
        technical credibility, and business impact.
        Include follow-up sequences and A/B testing strategies.
        """
    else:  # architectural_review (default)
        user_goal = """
        I have integrated 9 core MCP Servers (MEMemory, Pinecone, Redis, GitKraken, Figma, Filesystem, Fetch, Playwright, Send Email) into my L3 Agent architecture.

        Perform an **Architectural Strategy Review** of this unified platform to maximize the utility across the three functional engines: **Canon Validator**, **Resume Engine**, and **Outreach Engine**.

    ### INSTRUCTIONS (Sequential Thinking):

    1.  **Analyze the Toolset:** Review the final, comprehensive list of MCP servers and their core capabilities.
    2.  **Define Core Strategy per Engine:** For each of the three engines, synthesize a single, defining strategic goal that is only possible now that all MCPs are integrated.
    3.  **Propose Synergistic Use Cases (Required Table):** For each engine, create a table listing three **novel, multi-step use cases** that require the combined use of **at least three distinct MCP Servers**.

    ### Output Format Requirements:

    1.  **Strategic Goal Summary:** A short, bolded sentence defining the new, maximum capability of each engine.
    2.  **Use Case Table:** A markdown table summarizing the proposals.

    ### The Unified MCP Toolset for Reference:
    | MCP Server | Category | Core Capability |
    | :--- | :--- | :--- |
    | **MEMemory** | L3 Memory | Knowledge Graph (Relationships, User Profile) |
    | **Pinecone** | L2 RAG/Wisdom | Vector Search (Semantic Templates, Code Patterns) |
    | **Redis** | L1 Cache/State | High-Speed Cache (Prompt Responses, Session State) |
    | **GitKraken** | L0 Code Ops | Git & Issue Management (Commit, Checkout, PR, Issues) |
    | **Figma** | L0 Design Context | Design System Context (Variables, Components, Layout) |
    | **Filesystem** | L0 Secure I/O | Secure File Read/Write/Edit (Resumes, Reports) |
    | **Fetch** | L1 Web Content | URL Fetching and Markdown Conversion |
    | **Playwright** | L1 Automation | Browser Automation (Snapshot, Type, Click) |
    | **Send Email** | Action Tool | External Communication (Mock) |
    """

    # Run the agent with the strategic goal
    run_agentic_loop(user_goal)
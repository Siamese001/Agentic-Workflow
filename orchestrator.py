import time
import logging
import sys
import inspect
from typing import Protocol, Any, Callable
from llm_client import LLMClient
from canon_validator import CanonValidator
from action_registry import ActionRegistry

# Define Logger protocol at module level for execution
class Logger(Protocol):
    """Protocol for logging operations."""
    def log(self, message: str) -> None:
        """Log a message."""
        ...

# Setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Orchestrator")

def run_agentic_loop(user_goal: str):
    print(f"\n🚀 SUBATOMIC AGENT STARTING: {user_goal}")
    print("="*60)
    
    # 1. INITIALIZE COMPONENTS
    validator = CanonValidator()
    llm = LLMClient()
    actions = ActionRegistry()
    
    # 2. DEFINE THE TOOLBOX (Key #3 Whitelist)
    # We explicitly list available tools in the prompt
    toolbox_desc = """
    AVAILABLE TOOLS (You can call these python functions directly):
    - search_web(query: str) -> str : Returns search results for a query.
    - read_file(file_path: str) -> str : Reads text from .txt, .md, or .pdf files.
    - save_file(content: str, file_path: str) -> str : Saves content to a file.
    - send_email(recipient: str, subject: str, body: str) -> str : Simulates sending an email.
    - print(msg) : Standard python print.
    """
    
    # 3. THINK (Generate Draft with Tool Awareness)
    logger.info("🧠 Cognitive Plane: Generating plan...")
    system_prompt = f"""
    You are an Autonomous Agent.
    Write a Python script to solve the user's request.
    {toolbox_desc}
    
    RULES:
    - Output JSON with a 'code' field.
    - Use 'search_web' if you need outside information.
    - Do NOT import requests or use other tools. Use the provided functions.
    """
    
    draft = llm.generate_plan(system_context=system_prompt, user_goal=user_goal)
    raw_code = draft.get("code")
    
    if not raw_code:
        logger.error("❌ Generation failed.")
        return

    print(f"\n📄 DRAFT CODE RECEIVED:\n{'-'*20}\n{raw_code}\n{'-'*20}")

    # 4. AUDIT & REPAIR (The "Golden Loop")
    # Note: We relax strict dependency injection for the 'search_web' tool 
    # because it is a globally injected 'magic' function in this context.
    result = validator.validate(raw_code, auto_repair=True)
    
    final_code = raw_code
    status = result.get("status")
    
    if status == "repaired":
        print(f"\n🔧 AUTO-REPAIR APPLIED!")
        print(f"📝 Reason: {result.get('reasoning')}")
        final_code = result.get("repaired_code")
        print(f"✨ NEW CODE:\n{'-'*20}\n{final_code}\n{'-'*20}")
        
    elif status == "rejected":
        logger.error("❌ Code rejected.")
        return
        
    elif status == "valid":
        logger.info("✅ Draft code was perfect.")

    # 5. EXECUTE (Action Plane)
    logger.info("⚡ Executing Final Code...")
    try:
        # INJECT THE HANDS INTO THE BRAIN
        # We pass the tool map into the global scope so they're available everywhere
        exec_globals = actions.get_tool_map()
        exec_globals['__name__'] = '__main__'
        local_scope = {}
        
        exec(final_code, exec_globals, local_scope)
        
        # Run the entry point if it exists
        keys = [k for k in local_scope.keys() if k not in actions.get_tool_map() and "__" not in k and callable(local_scope[k])]
        if keys:
            func_name = keys[-1]
            print(f"▶️ Running function: {func_name}...")
            
            # Inspect function to see if it needs a logger injected
            sig = inspect.signature(local_scope[func_name])
            kwargs = {}
            if "logger" in sig.parameters:
                class MockLogger:
                    def info(self, msg): print(f"[LOG] {msg}")
                kwargs["logger"] = MockLogger()
                
            res = local_scope[func_name](**kwargs)
            print(f"✅ RESULT: {res}")
        else:
            # Script-based execution - output already printed during exec
            print("✅ Script executed successfully")
            
    except Exception as e:
        logger.error(f"Runtime Error: {e}")

if __name__ == "__main__":
    # Test the new capability
    run_agentic_loop("Find the current price of Bitcoin and log it.")

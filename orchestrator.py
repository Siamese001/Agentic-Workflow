import time
import logging
import sys
from llm_client import LLMClient
from canon_validator import CanonValidator
from action_registry import ActionRegistry
from cognitive_node import CognitiveNode # <--- NEW IMPORT

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
    cognitive = CognitiveNode() # <--- NEW COMPONENT
    
    # 2. DEFINE TOOLBOX (This is the critical step for unification)
    toolbox_desc = """
    AVAILABLE TOOLS (You MUST use these for your tasks):

    [REDIS MCP - L1 Cache & Session State]
    - string_set(key: str, value: str) : Stores simple session state or caching keys.
    - string_get(key: str) -> str : Retrieves simple session state or caching keys.
    - hash_set(key: str, field: str, value: str) : Stores field-value pairs (e.g., user profiles, complex cache objects).
    - hash_get(key: str, field: str) -> str : Retrieves a field from a hash key.
    
    [WEB SEARCH & CONTENT]
    - search_web(query: str) -> str : Returns real-time search results.
    - print(msg) : Standard output.
    
    [FILESYSTEM]
    - read_file(file_path: str) -> str : Reads contents of a file.
    - save_file(content: str, file_path: str) -> str : Saves content to a file.
    
    [EMAIL]
    - send_email(recipient: str, subject: str, body: str) -> str : Simulates sending an email (Mock).
    """
    
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

    print(f"\n📄 DRAFT CODE RECEIVED:\n{'-'*20}\n{raw_code}\n{'-'*20}")

    # 4. AUDIT & REPAIR (The "Golden Loop")
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

    # 5. EXECUTE (Action Plane)
    logger.info("⚡ Executing Final Code...")
    try:
        # INJECT ALL TOOLS (Web, File I/O, Mock Email)
        # Tools must be in global scope to be accessible inside function definitions
        exec_globals = actions.get_tool_map()
        exec_globals['__name__'] = '__main__'
        local_scope = {}
        
        # Execute the code - this defines all functions
        exec(final_code, exec_globals, local_scope)
        
        # Merge local_scope back into exec_globals so helper functions are accessible
        exec_globals.update(local_scope)
        
        # Auto-run entry point (find the last defined function that's not a tool)
        tool_names = set(actions.get_tool_map().keys())
        keys = [k for k in local_scope.keys() if k not in tool_names and "__" not in k and callable(local_scope[k])]
        if keys:
            func_name = keys[-1]
            print(f"▶️ Running function: {func_name}...")
            
            # Simple Injection Logic for Logger
            import inspect
            sig = inspect.signature(local_scope[func_name])
            kwargs = {}
            if "logger" in sig.parameters:
                class MockLogger:
                    def __call__(self, msg): print(f"[LOG] {msg}")
                    def info(self, msg): print(f"[LOG] {msg}")
                kwargs["logger"] = MockLogger()
                
            res = local_scope[func_name](**kwargs)
            print(f"✅ RESULT: {res}")
            
    except Exception as e:
        logger.error(f"Runtime Error: {e}")

if __name__ == "__main__":
    # Example task now leveraging caching and state management
    task = "Find the latest stock price for NVIDIA. Cache the result for 5 minutes using the Redis string_set tool with key 'NVDA_STOCK'. If the price is over $1000, save a file named 'NVIDIA_ALERT.txt' using the save_file tool."
    run_agentic_loop(task)

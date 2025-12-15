import time
import logging
import sys
import inspect
from typing import Protocol, Any, Callable
from llm_client import LLMClient
from canon_validator import CanonValidator

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
    
    # 1. INITIALIZE (Connects to Redis & Pinecone inside Validator)
    validator = CanonValidator()
    llm = LLMClient()
    
    # 2. THINK (Generate Draft)
    logger.info("🧠 Cognitive Plane: Generating draft solution...")
    system_prompt = "You are a Python Expert. Output a JSON with a 'code' field. Write a function solving the user request."
    
    draft = llm.generate_plan(system_context=system_prompt, user_goal=user_goal)
    raw_code = draft.get("code")
    
    if not raw_code:
        logger.error("❌ Generation failed.")
        return

    print(f"\n📄 DRAFT CODE RECEIVED:\n{'-'*20}\n{raw_code}\n{'-'*20}")

    # 3. AUDIT & REPAIR (The "Golden Loop")
    # This single call hits Redis -> Pinecone -> Gemini -> Fix -> Write Back
    result = validator.validate(raw_code, auto_repair=True)
    
    final_code = raw_code
    status = result.get("status")
    
    if status == "repaired":
        print(f"\n🔧 AUTO-REPAIR APPLIED!")
        print(f"📝 Reason: {result.get('reasoning')}")
        final_code = result.get("repaired_code")
        print(f"✨ NEW CODE:\n{'-'*20}\n{final_code}\n{'-'*20}")
        
    elif status == "rejected":
        logger.error("❌ Code rejected and could not be repaired.")
        return
        
    elif status == "valid":
        logger.info("✅ Draft code was perfect.")

    # 4. EXECUTE (Action Plane)
    logger.info("⚡ Executing Final Code...")
    try:
        # Sandboxed execution simulation
        # Add common imports to globals for repaired code
        exec_globals = {
            'Any': Any,
            'Protocol': Protocol,
            'Callable': Callable,
            '__name__': '__main__'
        }
        local_scope = {}
        exec(final_code, exec_globals, local_scope)
        
        # Try to find a runnable function
        keys = [k for k in local_scope.keys() if "__" not in k and callable(local_scope[k])]
        if keys:
            func_name = keys[-1] # Pick the last defined function
            func = local_scope[func_name]
            
            print(f"▶️ Running function: {func_name}...")
            
            # Get function signature
            sig = inspect.signature(func)
            args = {}
            
            # Prepare mock objects for injection
            class MockLogger:
                def log(self, msg): print(f"[LOG] {msg}")
                def info(self, msg): print(f"[LOG] {msg}")  # Support both log() and info()
                def __call__(self, msg): print(f"[LOG] {msg}")  # Make callable
            
            # Map parameters to values based on name and type
            for param_name, param in sig.parameters.items():
                if param_name in ['a', 'num1', 'x', 'first']:
                    args[param_name] = 10
                elif param_name in ['b', 'num2', 'y', 'second']:
                    args[param_name] = 5
                elif param_name in ['logger', 'log_func', 'log']:
                    args[param_name] = MockLogger()
                elif param.default == inspect.Parameter.empty:
                    # Required parameter without a clear mapping
                    if 'int' in str(param.annotation).lower():
                        args[param_name] = 10
                    elif 'float' in str(param.annotation).lower():
                        args[param_name] = 10.0
                    elif 'str' in str(param.annotation).lower():
                        args[param_name] = "test"
            
            # Call the function with prepared arguments
            res = func(**args)
            print(f"✅ RESULT: {res}")
    except Exception as e:
        logger.error(f"Runtime Error: {e}")

if __name__ == "__main__":
    # Test with a prompt that usually generates "lazy" code (triggering a repair)
    run_agentic_loop("Write a function called calculate that adds two numbers and logs the result.")

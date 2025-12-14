import sys
import logging
from typing import Dict, Any

# Import the Trinity
from cognitive_node import CognitiveNode
from action_node import ActionNode

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Orchestrator")

class AgentOrchestrator:
    """
    The Conductor.
    Ties the Brain (Cognitive) to the Body (Action).
    """
    
    def __init__(self, provider: str = "anthropic"):
        print("🚀 Initializing Agent System...")
        self.cognitive = CognitiveNode(provider=provider)
        self.action = ActionNode()
        print(f"✅ System Online with {provider.upper()} brain.")

    def run(self, user_goal: str):
        print(f"\n🎯 USER GOAL: {user_goal}")
        print("="*60)
        
        # Phase 1: THINK (Cognitive Node)
        print("\n🧠 PHASE 1: COGNITIVE PROCESSING")
        print("-" * 40)
        
        # 1. Retrieve Context & Generate Plan
        cognitive_result = self.cognitive.generate_plan(user_goal)
        
        plan = cognitive_result.get('plan')
        if not plan:
            logger.error("Cognitive Node failed to generate a plan.")
            return

        print(f"✅ Plan Generated with {cognitive_result.get('retrieved_items')} memory citations.")
        print(f"📝 Reasoning: {plan.get('reasoning')}")
        
        # Phase 2: ACT (Action Node)
        print("\n🔨 PHASE 2: ACTION EXECUTION")
        print("-" * 40)
        
        execution_report = self.action.execute_plan(plan)
        
        # Phase 3: REPORT
        self._print_final_report(execution_report)

    def _print_final_report(self, report: Dict[str, Any]):
        print("\n📊 MISSION REPORT")
        print("="*60)
        
        status = report.get('status')
        if status == 'success':
            print("✅ MISSION SUCCESS")
        else:
            print(f"❌ MISSION FAILED: {status}")
            
        print("\nExecution Log:")
        for res in report.get('results', []):
            icon = "✅" if res['status'] == 'success' else "❌"
            print(f"  {icon} Step {res['step']}: {res['output']}")
            
        print("="*60)

if __name__ == "__main__":
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Run the Subatomic Agent Orchestrator")
    parser.add_argument("--provider", choices=["anthropic", "openai", "google"], 
                        default="anthropic", help="LLM provider to use")
    parser.add_argument("goal", nargs="?", 
                        default="I need to write a function that prevents hallucinations by separating thinking from doing.",
                        help="User goal for the agent")
    
    args = parser.parse_args()
    
    orchestrator = AgentOrchestrator(provider=args.provider)
    orchestrator.run(args.goal)

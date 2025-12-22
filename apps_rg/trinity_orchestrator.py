import logging
from typing import Any, Dict

from action_node import ActionNode

# Import the Trinity
from cognitive_node import CognitiveNode

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
    Uses Tiered Thinking Protocol.
    """

    def __init__(self):
        # print("🚀 Initializing Agent System...")  # [Security Fix]
        self.cognitive = CognitiveNode()
        self.action = ActionNode()
        # print("✅ System Online with Tiered Thinking brain.")  # [Security Fix]

    def run(self, user_goal: str):
        # print(f"\n🎯 USER GOAL: {user_goal}")  # [Security Fix]
        # print("="*60)  # [Security Fix]

        # Determine complexity based on query
        complexity = "low" if len(user_goal.split()) < 10 else "high"
        tier_name = "Mini (Low Tier)" if complexity == "low" else "Consensus (High Tier)"
        # print(f"🧠 Using {tier_name} for this request.")  # [Security Fix]

        # Phase 1: THINK (Cognitive Node)
        # print("\n🧠 PHASE 1: COGNITIVE PROCESSING")  # [Security Fix]
        # print("-" * 40)  # [Security Fix]

        # 1. Retrieve Context & Generate Plan
        cognitive_result = self.cognitive.think(
            user_goal, complexity=complexity)

        plan = cognitive_result.get('plan')
        if not plan:
            logger.error("Cognitive Node failed to generate a plan.")
            return

        # print(  # [Security Fix]
            f"✅ Plan Generated with {cognitive_result.get('retrieved_items')} memory citations.")
        # print(f"📝 Reasoning: {plan.get('reasoning')}")  # [Security Fix]

        # Phase 2: ACT (Action Node)
        # print("\n🔨 PHASE 2: ACTION EXECUTION")  # [Security Fix]
        # print("-" * 40)  # [Security Fix]

        execution_report = self.action.execute_plan(plan)

        # Phase 3: REPORT
        self._print_final_report(execution_report)

    def _print_final_report(self, report: Dict[str, Any]):
        # print("\n📊 MISSION REPORT")  # [Security Fix]
        # print("="*60)  # [Security Fix]

        status = report.get('status')
        if status == 'success':
            # print("✅ MISSION SUCCESS")  # [Security Fix]
        else:
            # print(f"❌ MISSION FAILED: {status}")  # [Security Fix]

        # print("\nExecution Log:")  # [Security Fix]
        for res in report.get('results', []):
            icon = "✅" if res['status'] == 'success' else "❌"
            # print(f"  {icon} Step {res['step']}: {res['output']}")  # [Security Fix]

        # print("="*60)  # [Security Fix]


if __name__ == "__main__":
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(
        description = "Run the Subatomic Agent Orchestrator")
    parser.add_argument("goal", nargs="?",
                        default = "I need to write a function that prevents hallucinations by separating thinking from doing.",
                        help = "User goal for the agent")

    args = parser.parse_args()

    orchestrator = AgentOrchestrator()
    orchestrator.run(args.goal)
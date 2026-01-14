import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from agentic_core.L3_orchestration.strategic_recommendation.StrategicRecommendationAgent import StrategicRecommendationAgent

# Load dashboard data
html = Path('agentic_core/L6_observability/dashboards/autonomy_dashboard.html').read_text(encoding='utf-8')
import re
match = re.search(r'const dashboardData = (\[.*?\]);', html, re.DOTALL)
dashboard_data = json.loads(match.group(1))

print("Testing StrategicRecommendationAgent...")
print("=" * 70)

try:
    agent = StrategicRecommendationAgent(project_root=Path.cwd())
    result = agent.run(dashboard_data)
    print("✅ Agent succeeded!")
    print(f"Macro observations: {len(result.get('macro_observations', []))}")
    print(f"Metric observations: {len(result.get('metric_observations', []))}")
    print(f"Recommendations: {len(result.get('recommendations', []))}")
except Exception as e:
    print(f"❌ Agent failed: {e}")
    import traceback
    traceback.print_exc()

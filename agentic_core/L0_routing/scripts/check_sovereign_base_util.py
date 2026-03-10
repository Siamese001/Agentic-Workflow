from pathlib import Path

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

"""Check the actual SovereignBaseAgent class vs territory classification."""
import json

PROJECT_ROOT = Path(__file__).parent.parent
with open(PROJECT_ROOT / "agent_discovery_full.json") as f:
    agents = json.load(f)
sovereign_class = [a for a in agents if a.get("class_name") == "SovereignBaseAgent"]
if sovereign_class:
    for _a in sovereign_class:
        pass
territory_sovereign = [a for a in agents if a.get("territory") == "Sovereign Base Agent"]
base_layer = [a for a in agents if a.get("layer") == "Base"]

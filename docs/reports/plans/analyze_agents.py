import json

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# Load agent data
with open("agent_discovery_full.json") as f:
    data = json.load(f)

# Analyze distributions
dirs = {}
layers = {}
categories = {}
has_healing = 0
total = len(data)

for agent in data:
    # Directory distribution
    top_dir = agent["path"].split("\\")[0]
    dirs[top_dir] = dirs.get(top_dir, 0) + 1

    # Layer distribution
    layer = agent["layer"]
    layers[layer] = layers.get(layer, 0) + 1

    # Category distribution
    category = agent["category"]
    categories[category] = categories.get(category, 0) + 1

    # Healing capability
    if agent.get("has_healing", False):
        has_healing += 1

print("=== Directory Distribution ===")
for k, v in sorted(dirs.items()):
    print(f"{k}: {v}")

print("\n=== Layer Distribution ===")
for k, v in sorted(layers.items()):
    print(f"{k}: {v}")

print("\n=== Category Distribution ===")
for k, v in sorted(categories.items()):
    print(f"{k}: {v}")

print("\n=== Healing Capability ===")
print(f"Agents with healing: {has_healing}/{total} ({has_healing / total * 100:.1f}%)")

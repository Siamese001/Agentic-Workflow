import os, yaml, json

yaml_path = r"C:\Git\agentic-workflow\unified_structure_subatomic.yaml"
root_path = r"C:\Git\agentic-workflow\agentic_core"

with open(yaml_path, "r") as f:
    data = yaml.safe_load(f)

agentic = data["agentic-directory"]["agentic_core"]

def walk(node, prefix=""):
    leaves = []
    for k, v in node.items():
        path = f"{prefix}/{k}" if prefix else k
        if v is None:
            leaves.append(path)  # YAML already has .py extension
        elif isinstance(v, dict):
            leaves.extend(walk(v, path))
    return leaves

yaml_leaves = walk(agentic)
yaml_files = [os.path.join(root_path, p.replace("/", "\\")) for p in yaml_leaves]

actual_files = []
for root, dirs, files in os.walk(root_path):
    for f in files:
        if f.endswith(".py") and f != "__init__.py":
            actual_files.append(os.path.join(root, f))

missing = sorted(set(yaml_files) - set(actual_files))
extra   = sorted(set(actual_files) - set(yaml_files))

print("\nYAML file count:", len(yaml_files))
print("Actual file count:", len(actual_files))

print("\n--- Missing (YAML → local) ---")
print(f"Count: {len(missing)}")
if missing:
    print("First 10 missing files:")
    for f in missing[:10]:
        print(f"  {f}")

print("\n--- Extra (local → YAML) ---")
print(f"Count: {len(extra)}")
if extra:
    print("First 10 extra files:")
    for f in extra[:10]:
        print(f"  {f}")

print(f"\n=== SUMMARY ===")
print(f"Match: {len(yaml_files) - len(missing)}/{len(yaml_files)} files")
print(f"Missing: {len(missing)}")
print(f"Extra: {len(extra)}")

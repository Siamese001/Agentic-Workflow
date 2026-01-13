import json

# Test if both fields are in the dict
test_row = {
    "Territory": "TEST",
    "Proper Base %": 100.0,
    "Base Class Inherit %": 100.0
}

print("Original dict keys:", list(test_row.keys()))
print("\nJSON serialization:")
json_str = json.dumps(test_row, indent=2)
print(json_str)

print("\nDeserialized:")
loaded = json.loads(json_str)
print("Keys after load:", list(loaded.keys()))
print("Proper Base %:", loaded.get("Proper Base %"))
print("Base Class Inherit %:", loaded.get("Base Class Inherit %"))

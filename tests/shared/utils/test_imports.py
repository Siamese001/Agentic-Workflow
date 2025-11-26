errors = []

def test(pkg, alias=None):
    try:
        if alias:
            globals()[alias] = __import__(pkg, fromlist=[''])
        else:
            globals()[pkg] = __import__(pkg)
        print(f"[OK] {pkg} imported")
    except Exception as e:
        errors.append((pkg, str(e)))
        print(f"[ERROR] {pkg} failed:", e)

test("openai")
test("anthropic")
test("google.generativeai", "genai")
test("redis")
# test("chromadb")  # SKIP: Python 3.14 incompatible with Pydantic V1
test("pinecone")
test("numpy")
test("pandas")
test("sklearn")
test("requests")
test("httpx")
test("rich")
test("tqdm")
test("tenacity")

print("\n=== SDK IMPORT SUMMARY ===")
if errors:
    print("Packages with errors:")
    for pkg, err in errors:
        print(f" - {pkg}: {err}")
else:
    print("All SDKs imported successfully!")

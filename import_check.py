import pkgutil

print("=== IMPORT CHECK START ===")
for m in pkgutil.walk_packages(["."], "."):
    name = m.name.lstrip(".")
    try:
        __import__(name)
    except Exception as e:
        print("FAILED:", name, "->", type(e).__name__, str(e))
print("=== IMPORT CHECK END ===")
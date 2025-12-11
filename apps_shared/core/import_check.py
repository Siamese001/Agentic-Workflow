import pkgutil

for m in pkgutil.walk_packages([""]):
    name = (m.name or "").lstrip("")
    if not name:
        # Skip empty or invalid module names.
        continue
    try:
        __import__(name)
    except Exception as e:


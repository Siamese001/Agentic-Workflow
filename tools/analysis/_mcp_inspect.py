import json

data = json.loads(open(".cursor/mcp.json", encoding="utf-8").read())
for name in ["adg_sqlite", "enhanced_http", "memory", "otel_mcp", "redis", "vector_db", "pytest_mcp"]:
    cfg = data["mcpServers"].get(name, {})
    print(f"{name:15s} cmd={cfg.get('command', '?')} args={cfg.get('args')}")

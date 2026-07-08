"""Runtime import proof for E1 trace-import wave 1."""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path


def _module_name(path: str) -> str:
    if not path.endswith(".py"):
        raise ValueError(f"not a Python file: {path}")
    return path[:-3].replace("/", ".").replace("\\", ".")


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: e1_trace_import_wave1_runtime_proof.py <manifest> <output>")
        return 2
    manifest_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    candidates = manifest["candidates"]
    results = []
    for candidate in candidates:
        module = _module_name(candidate["path"])
        try:
            imported = importlib.import_module(module)
        except Exception as exc:  # noqa: BLE001 - proof captures concrete import failure class.
            results.append(
                {
                    "module": module,
                    "path": candidate["path"],
                    "status": "FAIL",
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                }
            )
            continue
        results.append(
            {
                "module": module,
                "path": candidate["path"],
                "status": "PASS",
                "imported_name": getattr(imported, "__name__", module),
            }
        )

    failures = [result for result in results if result["status"] != "PASS"]
    payload = {
        "manifest": str(manifest_path),
        "candidate_count": len(candidates),
        "passed": len(results) - len(failures),
        "failed": len(failures),
        "results": results,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({key: payload[key] for key in ("candidate_count", "passed", "failed")}, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

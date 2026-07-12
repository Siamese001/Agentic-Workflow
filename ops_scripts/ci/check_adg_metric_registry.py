#!/usr/bin/env python3
"""Validate the versioned ADG repository-health metric registry."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.adg.contracts.metric_registry import (  # noqa: E402
    DEFAULT_METRIC_REGISTRY,
    MetricRegistryError,
    load_metric_registry,
)


def main(argv: list[str]) -> int:
    registry_path = Path(argv[1]).expanduser().resolve() if len(argv) > 1 else DEFAULT_METRIC_REGISTRY
    try:
        contracts = load_metric_registry(registry_path)
    except FileNotFoundError as exc:
        print(f"[ERROR] ADG metric registry not found: {exc}")
        return 2
    except OSError as exc:
        print(f"[ERROR] ADG metric registry unreadable: {exc}")
        return 2
    except MetricRegistryError as exc:
        print(f"[FAIL] ADG metric registry invalid:\n{exc}")
        return 1

    print(f"[PASS] ADG metric registry valid: {registry_path} ({len(contracts)} contracts)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

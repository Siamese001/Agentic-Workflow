from __future__ import annotations

import json
from pathlib import Path

from apps_rg.runtime.sections.lane_artifact_io import (
    runtime_payload_for_json,
    sha16,
    write_json,
)


def test_sha16_is_stable_sha256_prefix() -> None:
    assert sha16("abc") == "ba7816bf8f01cfea"
    assert sha16(b"abc") == "ba7816bf8f01cfea"


def test_runtime_payload_for_json_filters_in_process_private_keys() -> None:
    payload = {
        "lane": "headline",
        "_provider_client": object(),
        "__scratch": {"skip": True},
        "nested": {"_kept_inside_nested_payload": True},
    }

    filtered = runtime_payload_for_json(payload)

    assert filtered == {
        "lane": "headline",
        "nested": {"_kept_inside_nested_payload": True},
    }
    assert "_provider_client" in payload


def test_write_json_creates_parent_and_writes_pretty_json(tmp_path: Path) -> None:
    path = tmp_path / "nested" / "runtime_payload.json"

    write_json(path, {"lane": "headline", "count": 2})

    assert path.is_file()
    assert path.read_text(encoding="utf-8").endswith("\n")
    assert json.loads(path.read_text(encoding="utf-8")) == {
        "lane": "headline",
        "count": 2,
    }


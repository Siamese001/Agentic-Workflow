"""Tests for the runtime ADG -> OTEL spans.jsonl exporter."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


class TestOtelRuntimeAdgExporter(unittest.TestCase):
    def test_qualname_heuristic(self) -> None:
        from ops_scripts.calibration.otel_runtime_adg_exporter import _looks_like_qualname
        # Positive cases — qualname-shaped span operation names.
        self.assertTrue(_looks_like_qualname("ExecutionAdapter.submit"))
        self.assertTrue(_looks_like_qualname("EvalEngine.execute"))
        self.assertTrue(_looks_like_qualname("BaseRGEngine.record_fail"))
        # Negative cases — definitely not span-like.
        self.assertFalse(_looks_like_qualname("nodot"))
        self.assertFalse(_looks_like_qualname(""))
        self.assertFalse(_looks_like_qualname("synth_abc.def"))
        self.assertFalse(_looks_like_qualname("synthetic.seed"))
        self.assertFalse(_looks_like_qualname("has space.method"))
        self.assertFalse(_looks_like_qualname("_private.method"))
        # Missing capitalized segment — not Python-class style.
        self.assertFalse(_looks_like_qualname("abc.def"))

    def test_decode_snapshot_returns_none_for_invalid_json(self) -> None:
        from ops_scripts.calibration.otel_runtime_adg_exporter import _decode_snapshot
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.json"
            bad.write_text("not json {{{", encoding="utf-8")
            self.assertIsNone(_decode_snapshot(bad))

    def test_decode_snapshot_returns_none_for_missing_payload(self) -> None:
        from ops_scripts.calibration.otel_runtime_adg_exporter import _decode_snapshot
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "no_payload.json"
            f.write_text(json.dumps({"version_id": "v1"}), encoding="utf-8")
            self.assertIsNone(_decode_snapshot(f))

    def test_decode_snapshot_extracts_qualnames(self) -> None:
        """Build a minimal hex payload that contains one node record
        with a qualname-shaped name field."""
        from ops_scripts.calibration.otel_runtime_adg_exporter import _decode_snapshot

        # Field layout (\x1e separated, 9 fields per node):
        # node_id, name, kind, layer, component, started, duration, status, attrs_json
        node_record = b"\x1e".join([
            b"node1",
            b"TestEngine.execute",  # name — qualname-shaped
            b"function",
            b"L3_ORCHESTRATION",
            b"apps_test",
            b"123",
            b"0.5",
            b"ok",
            b"{}",
        ])
        # Header: trace_id, mission, started, ended (\x1f separated)
        header = b"\x1f".join([b"trace1", b"test_mission", b"100", b"200"])
        # Full payload: header + \x1f + node_record
        raw = header + b"\x1f" + node_record
        hex_payload = raw.hex()

        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "snap.json"
            f.write_text(json.dumps({
                "version_id": "v1",
                "content_hash": "abc123",
                "type": "RuntimeADGSnapshot",
                "payload_hex": hex_payload,
            }), encoding="utf-8")

            result = _decode_snapshot(f)
            self.assertIsNotNone(result)
            spans, _meta = result
            self.assertIn("TestEngine.execute", spans)

    def test_decode_handles_list_root(self) -> None:
        """Some snapshot files have a list at top level — exporter must handle that."""
        from ops_scripts.calibration.otel_runtime_adg_exporter import _decode_snapshot

        node_record = b"\x1e".join([b"n", b"Foo.bar", b"f", b"L1", b"c", b"1", b"0", b"ok", b"{}"])
        header = b"\x1f".join([b"t", b"m", b"1", b"2"])
        hex_payload = (header + b"\x1f" + node_record).hex()

        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "snap.json"
            f.write_text(json.dumps([
                {"unrelated": True},
                {"payload_hex": hex_payload, "type": "RuntimeADGSnapshot"},
            ]), encoding="utf-8")

            result = _decode_snapshot(f)
            self.assertIsNotNone(result)
            spans, _meta = result
            self.assertIn("Foo.bar", spans)


if __name__ == "__main__":
    unittest.main()

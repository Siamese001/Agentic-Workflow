"""Replay the 5 Layer-B DEFERRED_SCOPE markers through the capture hook.

Used when the IDE did not stream an agent response into the post_agent_response
hook (lifecycle gap). Manually pipes the marker text to the hook as if stdin was
the response.
"""

from __future__ import annotations

import logging
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HOOK = REPO / ".codex" / "governance" / "scripts" / "post_agent_deferred_scope_capture.py"

MARKERS = """\
Layer-B markers for scorer OTel auto-source (ADR-031).

DEFERRED_SCOPE: plan=NEW:scorer-otel-autosource-layer-b-c5e4d1 wave=B1 phase=B1.1 layer=L_TOOLS fan_in=0 surface=None coverage_gap_pct=100.0 est_tokens=6000 prod_invocations=0 trajectory_defect_rate=0.0 reversibility=read item_class=capability adds_complexity=true reason=plan-slug agent-class resolver new module
DEFERRED_SCOPE: plan=scorer-otel-autosource-layer-b-c5e4d1 wave=B2 phase=B2.1 layer=L6 fan_in=3 surface=Observability coverage_gap_pct=100.0 est_tokens=9000 prod_invocations=0 trajectory_defect_rate=0.0 reversibility=read item_class=capability adds_complexity=true reason=rolling-window otel query fabric
DEFERRED_SCOPE: plan=scorer-otel-autosource-layer-b-c5e4d1 wave=B3 phase=B3.1 layer=L_TOOLS fan_in=0 surface=None coverage_gap_pct=100.0 est_tokens=5000 prod_invocations=0 trajectory_defect_rate=0.0 reversibility=read item_class=capability adds_complexity=false reason=reversibility inference from adg semantic edges
DEFERRED_SCOPE: plan=scorer-otel-autosource-layer-b-c5e4d1 wave=B4 phase=B4.1 layer=L_TOOLS fan_in=2 surface=Observability coverage_gap_pct=80.0 est_tokens=4000 prod_invocations=0 trajectory_defect_rate=0.0 reversibility=action item_class=regression adds_complexity=false reason=wire autosource into capture hook
DEFERRED_SCOPE: plan=scorer-otel-autosource-layer-b-c5e4d1 wave=B5 phase=B5.1 layer=L6 fan_in=0 surface=Observability coverage_gap_pct=100.0 est_tokens=3000 prod_invocations=0 trajectory_defect_rate=0.0 reversibility=read item_class=capability adds_complexity=true reason=priority calibration ab report
"""

proc = subprocess.run(
    [sys.executable, str(HOOK)],
    input=MARKERS,
    capture_output=True,
    text=True,
    timeout=60,
    check=False,
)
logging.info("C3 write receipt: tools/debug/_replay_layer_b_markers.py write side effect recorded")
print("exit:", proc.returncode)
print("stdout:", proc.stdout)
print("stderr:", proc.stderr)

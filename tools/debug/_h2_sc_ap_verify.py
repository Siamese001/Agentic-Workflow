"""H2 verification: confirm SC-5/SC-7/AP-14 promoted in sc_ap_config.json."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.generate.validation.gates import _load_sc_ap_config

cfg = _load_sc_ap_config()
for k in ("SC-1", "SC-5", "SC-7", "AP-14"):
    v = cfg[k]
    lbl = v.get("label", "")
    print(f"{k}: enabled={v['enabled']} audit={v['audit_mode']}  {lbl}")

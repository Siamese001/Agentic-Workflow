"""Final status check: are all 6 audit gates passing except AUDIT_6?"""
import subprocess, sys
gates = [
    ("AUDIT_1 SSOT magic constants",        "ops_scripts/ci/check_ssot_magic_constants.py"),
    ("AUDIT_2 observability fan-in",        "ops_scripts/ci/check_observability_on_high_fanin.py"),
    ("AUDIT_3 external-service literal",    "ops_scripts/ci/check_external_service_literal_ssot.py"),
    ("AUDIT_4 cross-mainline dispatcher",   "ops_scripts/ci/check_cross_mainline_dispatcher.py"),
    ("AUDIT_5 env var outside config",      "ops_scripts/ci/check_env_var_in_config_layer.py"),
    ("AUDIT_6 violation aging SLA",         "ops_scripts/ci/check_violation_aging_sla.py"),
]
print(f"{'Gate':<42} {'Exit':<6} {'Last line of output'}")
print("-" * 100)
for label, script in gates:
    r = subprocess.run([sys.executable, script], capture_output=True, text=True, timeout=120)
    last = ""
    for ln in (r.stdout + r.stderr).splitlines()[::-1]:
        if ln.strip():
            last = ln.strip()[:60]
            break
    print(f"{label:<42} {r.returncode:<6} {last}")

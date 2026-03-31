"""Run test suite per-subdir to avoid fd crash, aggregate via JUnit XML."""
import os
import subprocess
import sys
import xml.etree.ElementTree as ET

root = r"C:\Git\Agentic-Workflow"
unit_dir = os.path.join(root, "tests", "unit")
xml_dir = os.path.join(root, "artifacts", "xml")
os.makedirs(xml_dir, exist_ok=True)

env = os.environ.copy()
env["PYTHONDONTWRITEBYTECODE"] = "1"

total = {"tests": 0, "errors": 0, "failures": 0, "skipped": 0}

for sd in sorted(os.listdir(unit_dir)):
    sdp = os.path.join(unit_dir, sd)
    if not os.path.isdir(sdp) or sd.startswith("_"):
        continue
    xml_path = os.path.join(xml_dir, f"{sd}.xml")
    with open(os.devnull, "w") as devnull:
        proc = subprocess.Popen(
            [sys.executable, "-m", "pytest", f"tests/unit/{sd}",
             "-c", "tools/pytest_minimal.ini",
             "--tb=no", "-q", "-p", "no:warnings",
             "--timeout=10",
             f"--junitxml={xml_path}"],
            stdout=devnull, stderr=devnull, env=env
        )
        try:
            proc.wait(timeout=300)
        except (ValueError, TypeError, RuntimeError) as e:
            proc.kill()
            print(f"  {sd}: TIMEOUT")
            continue

    if os.path.exists(xml_path):
        tree = ET.parse(xml_path)
        for ts in tree.getroot().iter("testsuite"):
            t = int(ts.get("tests", "0"))
            e = int(ts.get("errors", "0"))
            f = int(ts.get("failures", "0"))
            s = int(ts.get("skipped", "0"))
            p = t - e - f - s
            total["tests"] += t
            total["errors"] += e
            total["failures"] += f
            total["skipped"] += s
            if t > 0:
                print(f"  {sd:<25} tests={t:>5}  pass={p:>5}  fail={f:>3}  err={e:>3}  skip={s:>3}")

print(f"\n{'='*60}")
t, e, f, s = total["tests"], total["errors"], total["failures"], total["skipped"]
p = t - e - f - s
print(f"TOTAL: tests={t}  pass={p}  fail={f}  err={e}  skip={s}")
if t > 0:
    print(f"Pass rate: {p}/{t} ({p/t*100:.1f}%)")

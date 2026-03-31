"""Run test suite with JUnit XML output to get results reliably."""
import os
import subprocess
import sys
import xml.etree.ElementTree as ET

env = os.environ.copy()
env["PYTHONDONTWRITEBYTECODE"] = "1"

xml_path = os.path.join("artifacts", "test_results.xml")

# Open NUL for discarding stdout
with open(os.devnull, "w") as devnull:
    proc = subprocess.Popen(
        [sys.executable, "-m", "pytest", "tests/unit/",
         "--tb=no", "-q",
         "-p", "no:warnings", "-p", "no:capture",
         "--timeout=10",
         f"--junitxml={xml_path}"],
        stdout=devnull, stderr=devnull,
        env=env
    )
    try:
        proc.wait(timeout=600)
    except (ValueError, TypeError, RuntimeError) as e:
        proc.kill()
        print("TIMEOUT after 600s")
        sys.exit(1)

print(f"Return code: {proc.returncode}")

# Parse JUnit XML
if os.path.exists(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    for ts in root.iter("testsuite"):
        tests = ts.get("tests", "0")
        errors = ts.get("errors", "0")
        failures = ts.get("failures", "0")
        skipped = ts.get("skipped", "0")
        time_taken = ts.get("time", "0")
        print(f"Tests: {tests}, Errors: {errors}, Failures: {failures}, Skipped: {skipped}, Time: {time_taken}s")
else:
    print("No XML output generated")

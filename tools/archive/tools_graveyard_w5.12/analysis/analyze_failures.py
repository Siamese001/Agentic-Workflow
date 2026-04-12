"""Analyze test failures and errors from JUnit XML files."""

import os
import xml.etree.ElementTree as ET
from collections import Counter

xml_dir = os.path.join("artifacts", "xml")

for xml_file in sorted(os.listdir(xml_dir)):
    if not xml_file.endswith(".xml"):
        continue
    subdir = xml_file.replace(".xml", "")
    tree = ET.parse(os.path.join(xml_dir, xml_file))

    failures = []
    errors = []
    for tc in tree.getroot().iter("testcase"):
        fail = tc.find("failure")
        err = tc.find("error")
        name = tc.get("classname", "") + "." + tc.get("name", "")
        if fail is not None:
            msg = fail.get("message", "")[:120]
            failures.append(msg)
        if err is not None:
            msg = err.get("message", "")[:120]
            errors.append(msg)

    if failures or errors:
        print(f"\n=== {subdir} ({len(failures)} failures, {len(errors)} errors) ===")
        if errors:
            err_counter = Counter(errors)
            print("  ERRORS:")
            for msg, cnt in err_counter.most_common(5):
                print(f"    [{cnt:3d}] {msg}")
        if failures:
            fail_counter = Counter(failures)
            print("  FAILURES:")
            for msg, cnt in fail_counter.most_common(10):
                print(f"    [{cnt:3d}] {msg}")

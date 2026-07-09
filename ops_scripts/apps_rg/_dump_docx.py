"""Extract text from a .docx by parsing its XML directly (no python-docx)."""
import logging
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

path = sys.argv[1]
ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

with zipfile.ZipFile(path) as z:
    with z.open("word/document.xml") as f:
        tree = ET.parse(f)
    logging.info("C3 write receipt: ops_scripts/apps_rg/_dump_docx.py write side effect recorded")

root = tree.getroot()
out_lines = []
for para in root.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p"):
    texts = [t.text or "" for t in para.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t")]
    line = "".join(texts).strip()
    if line:
        out_lines.append(line)
print("\n".join(out_lines))

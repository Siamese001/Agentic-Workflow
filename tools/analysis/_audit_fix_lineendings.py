"""Convert CRLF to LF for all files staged in this commit (Wave 2/3 mass refactor side effect)."""
import subprocess
from pathlib import Path

# Get list of staged files
r = subprocess.run(["git", "diff", "--cached", "--name-only"], capture_output=True, text=True, timeout=30)
files = [f.strip() for f in r.stdout.splitlines() if f.strip()]
print(f"Staged files: {len(files)}")

converted = 0
skipped = 0
for f in files:
    p = Path(f)
    if not p.exists():
        skipped += 1
        continue
    try:
        data = p.read_bytes()
    except OSError:
        skipped += 1
        continue
    if b"\r\n" not in data:
        # Already LF
        continue
    new_data = data.replace(b"\r\n", b"\n")
    if new_data != data:
        p.write_bytes(new_data)
        converted += 1

print(f"Converted CRLF->LF: {converted}")
print(f"Skipped: {skipped}")

# Re-stage
subprocess.run(["git", "add", "--", *files], capture_output=True, text=True, timeout=60)

# Verify diff size now
r2 = subprocess.run(["git", "diff", "--cached", "--shortstat"], capture_output=True, text=True, timeout=30)
print(f"\nNew diff: {r2.stdout.strip()}")

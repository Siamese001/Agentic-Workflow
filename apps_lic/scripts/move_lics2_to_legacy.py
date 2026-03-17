"""Move LicS2SupervisorAgent to LEGACY status."""

from pathlib import Path

def main():
    file_path = Path("apps_lic/engines/LicS2SupervisorAgent.py")
    content = file_path.read_text(encoding="utf-8")
    legacy_header = '"""LEGACY FILE - Moved to legacy during Terminal Alignment Command\nThis file has fundamental architectural issues that require complete rewrite.\nStatus: DEPRECATED - Do not use in production\n"""\n\n# LEGACY CODE BELOW - COMMENTED OUT\n'
    lines = content.split("\n")
    commented_lines = [f"# {line}" if line.strip() and (not line.startswith("#")) else line for line in lines]
    new_content = legacy_header + "\n".join(commented_lines)
    file_path.write_text(new_content, encoding="utf-8")
    print("LicS2SupervisorAgent.py moved to LEGACY")


if __name__ == "__main__":
    main()

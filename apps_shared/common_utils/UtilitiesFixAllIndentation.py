
#!/usr/bin/env python3
"""Fix all indentation errors in canon_validator_engine.py"""

import re


def fix_all_indentation():
    """Brief description of functionality and purpose."""

    # Read the file with UTF-8 encoding
    with open("canon_validator_engine.py", encoding="utf-8") as f:
        content = f.read()

    # Pattern to match broken except blocks
    # Matches: except Exception as e:\n    pass\npass\n<actual_code>
    pattern = r"(\s+except Exception as e:\n)\s+pass\npass\n(.*?)(?=\n    |\n\ndef |\n\n|\Z)"

    def fix_except_block(match):
        except_line = match.group(1)
        actual_code = match.group(2).strip()

        # Determine proper indentation for the actual code
        if actual_code.startswith("return"):
            fixed_code = f"        {actual_code}"
        elif actual_code.startswith("if Logger:"):
            fixed_code = "        if Logger:"
            # Add the Logger lines after
            lines = actual_code.split("\n")
            for line in lines[1:]:
                if line.strip():
                    fixed_code += f"\n            {line.strip()}"
        else:
            fixed_code = f"        {actual_code}"

        return except_line + fixed_code + "\n"

    # Apply the fix
    content = re.sub(pattern, fix_except_block, content, flags=re.DOTALL)

    # Also fix bare except blocks
    pattern2 = r"(\s+except Exception:\n)\s+pass\npass\n(.*?)(?=\n    |\n\ndef |\n\n|\Z)"

    def fix_bare_except(match):
        except_line = match.group(1)
        actual_code = match.group(2).strip()

        if actual_code.startswith("return"):
            fixed_code = f"        {actual_code}"
        elif actual_code.startswith("if"):
            fixed_code = f"        {actual_code}"
        else:
            fixed_code = "        pass"

        return except_line + fixed_code + "\n"

    content = re.sub(pattern2, fix_bare_except, content, flags=re.DOTALL)

    # Write the fixed content back
    with open("canon_validator_engine.py", "w", encoding="utf-8") as f:
        f.write(content)

    # print('Fixed all indentation errors')  # [Security Fix]


if __name__ == "__main__":
    fix_all_indentation()
#!/usr/bin/env python3
import subprocess
import json
import sys

def extract_json_from_ssot():
    """Extract JSON output from SSOT dry run"""
    try:
        # Run the SSOT script with UTF-8 encoding
        result = subprocess.run([
            sys.executable, 
            "-m", 
            "agentic_core.L0_routing.scripts.execute_ssot_entrypoint", 
            "--legacy", 
            "--dry-run"
        ], capture_output=True, text=True, encoding='utf-8', cwd="c:\\Git\\Agentic-Workflow")
        
        output = result.stdout
        
        # Find the start of JSON (looks for opening brace at start of line)
        lines = output.split('\n')
        json_start = None
        brace_count = 0
        
        for i, line in enumerate(lines):
            if line.strip().startswith('{'):
                json_start = i
                break
        
        if json_start is None:
            print("No JSON found in output")
            return
        
        # Extract JSON from the start to the matching closing brace
        json_lines = []
        for line in lines[json_start:]:
            json_lines.append(line)
            brace_count += line.count('{')
            brace_count -= line.count('}')
            
            if brace_count <= 0:
                break
        
        json_text = '\n'.join(json_lines)
        
        # Parse and save the JSON to a file
        try:
            data = json.loads(json_text)
            
            # Save to file
            with open('ssot_report.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print("JSON report saved to ssot_report.json")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
            print("Raw JSON text:")
            print(json_text)
            
    except Exception as e:
        print(f"Error running SSOT script: {e}")

if __name__ == "__main__":
    extract_json_from_ssot()

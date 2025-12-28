import os
import subprocess
from pathlib import Path


def wake_the_brain():
    print("[*] MISSION START: FINAL SOVEREIGN VALIDATION")
    
    # We run the validator with a specific focus on the 239 core files
    # The 'auto-heal' is enabled to clean up those last synaptic scars
    cmd = [
        "python", "canon_validator_agentic_v2.py",
        "--target", "agentic_core",
        "--mode", "comprehensive",
        "--heal", "true"
    ]
    
    try:
        # We stream the output so we can see the HealerAgent in action
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        for line in process.stdout:
            # We're looking for the 'MISSION ACCOMPLISHED' signal
            print(line, end="")
            
        process.wait()
        
        if process.returncode == 0:
            print("\n[SUCCESS] SOVEREIGN CORE IS FULLY FUNCTIONAL.")
        else:
            print(f"\n[!] ALERT: Validator exited with code {process.returncode}.")
            
    except Exception as e:
        print(f"[ERROR] Could not start validation: {e}")

if __name__ == "__main__":
    wake_the_brain()

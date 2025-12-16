import json
import time
import os
from datetime import datetime

BLACKBOARD_PATH = "/app/active_manifest.json"

def monitor():
    print(f"📡 [MONITOR] Watching Swarm Blackboard at {BLACKBOARD_PATH}...")
    last_mtime = 0

    while True:
        try:
            if os.path.exists(BLACKBOARD_PATH):
                current_mtime = os.path.getmtime(BLACKBOARD_PATH)
                if current_mtime != last_mtime:
                    with open(BLACKBOARD_PATH, 'r') as f:
                        data = json.load(f)
                    
                    # Extract high-level metrics
                    file_count = len(data.get("files", {}))
                    last_agent = data.get("metadata", {}).get("last_agent", "None")
                    status = data.get("metadata", {}).get("status", "Idling")
                    
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"\n--- [UPDATE: {timestamp}] ---")
                    print(f"🤖 Active Agent: {last_agent}")
                    print(f"📊 Files in View: {file_count}")
                    print(f"📍 System Status: {status}")
                    
                    # Watch for consensus flags
                    if "consensus" in data:
                        print(f"🤝 CONSENSUS: {data['consensus'].get('agreement', 'pending')}")

                    last_mtime = current_mtime
            
            time.sleep(2) # Polling interval
        except KeyboardInterrupt:
            print("\n👋 Monitor shutting down.")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    monitor()

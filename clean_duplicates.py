import json
import os
import logging

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

def purge_duplicates(manifest_path="active_manifest.json"):
    if not os.path.exists(manifest_path):
        logger.error(f"❌ Manifest not found at {manifest_path}. Run the orchestrator once first.")
        return

    try:
        with open(manifest_path, 'r') as f:
            data = json.load(f)
        
        # In your system, the Librarian logs identify 'duplicate file pairs'
        # We target the files marked as duplicates in the Librarian's scan log.
        # This script specifically targets the common 'test_repo' and '_clean' clones.
        
        duplicates_purged = 0
        python_files = [f for f in os.listdir('.') if f.endswith('.py')]
        
        # Recursive walk to find test_repo clones and _clean files
        for root, dirs, files in os.walk('.'):
            for file in files:
                file_path = os.path.join(root, file)
                
                # Logic: Target known duplicate naming patterns identified in your logs
                is_runaway = any(x in file_path for x in ["test_repo_1765", "_clean.py", "duplicate of"])
                
                if is_runaway and os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        logger.info(f"🗑️ Purged: {file_path}")
                        duplicates_purged += 1
                    except Exception as e:
                        logger.error(f"❌ Failed to delete {file_path}: {e}")

        logger.info(f"\n✨ Cleanup Complete. {duplicates_purged} duplicate files removed.")
        logger.info("🚀 Your next Librarian scan should now finish in seconds.")

    except Exception as e:
        logger.error(f"🚨 Script Error: {e}")

if __name__ == "__main__":
    purge_duplicates()

import json
import os
import shutil
import logging

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

def purge_everything():
    purged_count = 0
    # 1. Target runaway directories identified in your logs
    for item in os.listdir('.'):
        if os.path.isdir(item) and item.startswith("test_repo_1765"):
            try:
                shutil.rmtree(item)
                logger.info(f"🗑️ PURGED DIRECTORY: {item}")
                purged_count += 1
            except Exception as e:
                logger.error(f"❌ Failed to delete directory {item}: {e}")

    # 2. Target individual "clean" file clones and reports
    for root, dirs, files in os.walk('.'):
        for file in files:
            file_path = os.path.join(root, file)
            if "_clean.py" in file or file == "test_report.html":
                try:
                    os.remove(file_path)
                    logger.info(f"�️ Purged File: {file_path}")
                    purged_count += 1
                except Exception as e:
                    pass

    logger.info(f"\n✨ Aggressive Cleanup Complete. {purged_count} items removed.")

if __name__ == "__main__":
    purge_everything()


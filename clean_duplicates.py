import json
import os
import shutil
import logging
import argparse

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

def aggressive_cleanup():
    """More aggressive cleanup targeting additional patterns"""
    purged_count = 0

    # Remove all test_repo directories
    for item in os.listdir('.'):
        if os.path.isdir(item) and item.startswith("test_repo"):
            try:
                shutil.rmtree(item)
                logger.info(f"🗑️ PURGED DIRECTORY: {item}")
                purged_count += 1
            except Exception as e:
pass
logger.error(f"❌ Failed to delete directory {item}: {e}")

    # Remove temporary and cache files
    temp_patterns = ["*.tmp", "*.temp", "*.bak", "*~", ".DS_Store", "Thumbs.db"]
    for pattern in temp_patterns:
        import glob
        for file in glob.glob(pattern, recursive=True):
            try:
                os.remove(file)
                logger.info(f"🗑️ Purged temp file: {file}")
                purged_count += 1
            except Exception as e:
pass
pass

    # Remove __pycache__ directories
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(pycache_path)
                logger.info(f"🗑️ PURGED DIRECTORY: {pycache_path}")
                purged_count += 1
            except Exception as e:
pass
pass

    return purged_count

def organize_structure():
    """Reorganize files into proper engine directories"""
    logger.info("📁 Starting folder reorganization...")

    # Create main directories if they don't exist
    engines_dir = "/app/engines"
    subdirs = ["resume_engine", "outreach_engine", "canon_validator"]

    for subdir in subdirs:
        path = os.path.join(engines_dir, subdir)
        os.makedirs(path, exist_ok=True)
        logger.info(f"📁 Created directory: {path}")

    # Move relevant files to appropriate directories
    file_mappings = {
        "resume": "resume_engine",
        "outreach": "outreach_engine",
        "canon": "canon_validator",
        "validator": "canon_validator"
    }

    moved_count = 0
    for root, dirs, files in os.walk('/app'):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                file_lower = file.lower()

                # Determine target directory based on filename
                target_dir = None
                for keyword, directory in file_mappings.items():
                    if keyword in file_lower:
                        target_dir = directory
                        break

                if target_dir and not file.startswith('__'):
                    target_path = os.path.join(engines_dir, target_dir, file)
                    try:
                        # Avoid overwriting existing files
                        if not os.path.exists(target_path):
                            shutil.move(file_path, target_path)
                            logger.info(f"📁 Moved {file} to {target_dir}/")
                            moved_count += 1
                    except Exception as e:
pass
logger.error(f"❌ Failed to move {file}: {e}")

    logger.info(f"\n✨ Reorganization complete. Moved {moved_count} files.")
    return moved_count

def purge_everything(aggressive=False, organize=False):
    purged_count = 0

    # 1. Target runaway directories identified in your logs
    for item in os.listdir('.'):
        if os.path.isdir(item) and item.startswith("test_repo_1765"):
            try:
                shutil.rmtree(item)
                logger.info(f"🗑️ PURGED DIRECTORY: {item}")
                purged_count += 1
            except Exception as e:
pass
logger.error(f"❌ Failed to delete directory {item}: {e}")

    # 2. Target individual "clean" file clones and reports
    for root, dirs, files in os.walk('.'):
        for file in files:
            file_path = os.path.join(root, file)
            if "_clean.py" in file or file == "test_report.html":
                try:
                    os.remove(file_path)
                    logger.info(f"🗑️ Purged File: {file_path}")
                    purged_count += 1
                except Exception as e:
pass
pass

    # 3. Aggressive cleanup if requested
    if aggressive:
        purged_count += aggressive_cleanup()

    logger.info(f"\n✨ Aggressive Cleanup Complete. {purged_count} items removed.")

    # 4. Organize structure if requested
    if organize:
        organize_structure()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean duplicates and organize code structure")
    parser.add_argument("--aggressive", action="store_true", help="Perform aggressive cleanup")
    parser.add_argument("--organize", action="store_true", help="Organize files into engine directories")
    args = parser.parse_args()

    purge_everything(aggressive=args.aggressive, organize=args.organize)


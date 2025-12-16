import sys
import os
import logging

# --- 1. BOOTSTRAP ENVIRONMENT ---
# Dynamically add the project root to python path to resolve 'apps_rg' imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Configure logging to see the Hardening in action
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("Launcher")

def main():
    print("\n🛡️  Hardened Agentic System Initializing...")

    try:
        # Lazy import AFTER sys.path fix to prevent ModuleNotFoundError
        # Adjust this import path if your orchestrator file name differs
        from orchestrator import run_agentic_loop

        # --- 2. CAPTURE GOAL ---
        if len(sys.argv) > 1:
            # Goal from command line argument
            user_goal = " ".join(sys.argv[1:])
        else:
            # Interactive prompt
            print("   (No arguments provided. Entering interactive mode.)")
            user_goal = input("\n🎯 Enter your goal: ").strip()

        if not user_goal:
            logger.error("Goal cannot be empty. Exiting.")
            sys.exit(1)

        # --- 3. EXECUTE HARDENED RUNTIME ---
        logger.info(f"Dispatching Goal: {user_goal}")

        # This function triggers:
        #  1. ensure_manifest_freshness() [Drift Check]
        #  2. validate_manifest_integrity() [Integrity Gate]
        #  3. CognitiveNode.think() [Temperature Decay]
        run_agentic_loop(user_goal)

        print("\n✅ Workflow Completed Successfully.")

    except ImportError as e:
        logger.critical(f"❌ Configuration Error: {e}")
        print("\nFix: Ensure your folder structure matches: orchestrator.py in project root")
        sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n⚠️  User Aborted.")
        sys.exit(0)

    except Exception as e:
        # This catches anything that slipped past the Hardened Orchestrator
        logger.critical(f"❌ Unhandled System Crash: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()


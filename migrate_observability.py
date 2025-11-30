import os
import shutil

ROOT = "observability"

# ------------------------------------------------------------------------------
# Target Level-5 folder structure
# ------------------------------------------------------------------------------
TARGET_STRUCTURE = {
    "telemetry": [
        "metrics.yaml",
        "events.yaml",
        "sampling_rules.yaml",
        "pii_redaction.yaml",
        "cost_tracking.yaml"
    ],
    "tracing": [
        "otel_config.yaml",
        "span_schema.yaml",
        "workflow_trace_rules.yaml",
        "retention_policies.yaml"
    ],
    "dashboards": [
        "system_health.yaml",
        "model_routing.yaml",
        "tool_latency.yaml",
        "safety_violations.yaml",
        "cost_overview.yaml"
    ],
    "pipelines": [
        "ingestion_pipeline.yaml",
        "transformation_rules.yaml",
        "storage_backends.yaml",
        "alerting_routes.yaml"
    ],
    "alerts": [
        "anomaly_detection.yaml",
        "error_thresholds.yaml",
        "slos_slas.yaml",
        "routing.yaml",
        "escalation_policies.yaml"
    ],
}

# ------------------------------------------------------------------------------
# Old structure mapping → new homes
# ------------------------------------------------------------------------------
MOVE_MAP = {
    # cost/
    "model_costs.json": ("telemetry", "cost_tracking.yaml"),
    "tracker.py": ("telemetry", None),
    
    # metrics/
    "collector.py": ("telemetry", None),
    "cost_metrics.json": ("telemetry", "metrics.yaml"),
    "token_usage.json": ("telemetry", "metrics.yaml"),

    # logs/
    "agent.log": ("telemetry", None),
    "safety.log": ("telemetry", None),

    # trace/ + traces/
    "dag_spans.log": ("tracing", None),
    "tool_spans.log": ("tracing", None),
    "tracer.py": ("tracing", None),
}

# ------------------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------------------

YAML_STUB = "# Placeholder YAML configuration file\n"


def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def create_stub(path):
    if os.path.exists(path):
        return
    with open(path, "w", encoding="utf-8") as f:
        f.write(YAML_STUB)


def cleanup_if_empty(path):
    """Remove directory if it's empty after migration."""
    if os.path.isdir(path) and not os.listdir(path):
        os.rmdir(path)


# ------------------------------------------------------------------------------
# Migration logic
# ------------------------------------------------------------------------------

def migrate():
    print("=== Starting observability folder migration ===")

    # Ensure root exists
    ensure_dir(ROOT)

    # STEP 1 — Create Level-5 folders + stub files
    for folder, files in TARGET_STRUCTURE.items():
        folder_path = os.path.join(ROOT, folder)
        ensure_dir(folder_path)

        for file in files:
            create_stub(os.path.join(folder_path, file))

    # STEP 2 — Move existing files into new structure
    OLD_DIRS = ["cost", "logs", "metrics", "trace", "traces"]

    for old in OLD_DIRS:
        old_path = os.path.join(ROOT, old)
        if not os.path.exists(old_path):
            continue

        for entry in os.listdir(old_path):
            src = os.path.join(old_path, entry)

            if entry in MOVE_MAP:
                new_folder, replace_with_stub = MOVE_MAP[entry]
                dest_folder = os.path.join(ROOT, new_folder)
                ensure_dir(dest_folder)

                if replace_with_stub:
                    # File data goes into one of the new YAMLs via stub creation
                    dest = os.path.join(dest_folder, replace_with_stub)
                    print(f"Creating stub for {entry} → {dest}")
                    create_stub(dest)
                else:
                    dest = os.path.join(dest_folder, entry)
                    print(f"Moving {entry} → {dest}")
                    shutil.move(src, dest)
            else:
                # Unknown file: move to telemetry/logs for safety
                fallback_folder = os.path.join(ROOT, "telemetry")
                ensure_dir(fallback_folder)
                dest = os.path.join(fallback_folder, entry)
                print(f"Moving (fallback) {entry} → {dest}")
                shutil.move(src, dest)

        cleanup_if_empty(old_path)

    # STEP 3 — Remove __pycache__
    pyc = os.path.join(ROOT, "__pycache__")
    if os.path.isdir(pyc):
        shutil.rmtree(pyc)
        print("Removed __pycache__/")

    print("=== Migration complete ===")


if __name__ == "__main__":
    migrate()

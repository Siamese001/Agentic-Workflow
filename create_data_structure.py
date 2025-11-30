import os

ROOT = "data"

# Full Level-4 → Level-5 structure for /data
STRUCTURE = {
    "production_inputs": {
        "master_resume": [
            "resume_master.md",
            "resume_metadata.json"
        ],
        "job_descriptions": [
            "jd_001.txt",
            "jd_002.txt"
        ],
        "outreach_targets": [
            "target_list.csv",
            "org_profiles.yaml"
        ],
        "user_profiles": [
            "persona.yaml",
            "constraints.yaml"
        ]
    },

    "datasets": {
        "taxonomies": [
            "skills_v1.yaml",
            "industries.yaml",
            "seniority_map.yaml"
        ],
        "embeddings": [
            "skill_embeddings.json",
            "jd_cluster_centroids.npy"
        ],
        "corpora": [
            "outreach_examples.json",
            "resume_examples.json"
        ]
    },

    "golden_sets": {
        "resume_engine": [
            "golden_resumes.json",
            "golden_scores.json"
        ],
        "outreach_engine": [
            "golden_messages.json",
            "golden_archetypes.json"
        ],
        "common": [
            "sanity_tests.json",
            "quality_baselines.json"
        ]
    },

    "tmp_runtime": {
        "scratchpad": [],
        "cache": []
    },

    "lookups": [
        "stopwords.txt",
        "country_codes.yaml",
        "degree_map.yaml",
        "title_normalization.yaml"
    ]
}

# Stub content
YAML_STUB = "# Placeholder configuration/data file\n"
JSON_STUB = "{\n  \"placeholder\": true\n}\n"
TEXT_STUB = "# Placeholder text file\n"
CSV_STUB = "placeholder_column\n"
NPY_STUB = b""  # empty binary file

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def write_stub_file(path):
    if os.path.exists(path):
        return  # do not overwrite

    ext = path.split(".")[-1]

    if ext in ("yaml", "yml"):
        content = YAML_STUB
        mode = "w"
    elif ext == "json":
        content = JSON_STUB
        mode = "w"
    elif ext == "txt":
        content = TEXT_STUB
        mode = "w"
    elif ext == "csv":
        content = CSV_STUB
        mode = "w"
    elif ext == "npy":
        mode = "wb"
        content = NPY_STUB
    else:
        content = ""
        mode = "w"

    with open(path, mode, encoding="utf-8") if mode != "wb" else open(path, mode) as f:
        f.write(content)

def populate():
    print(f"Enforcing `{ROOT}` folder structure...")

    ensure_dir(ROOT)

    for top, entries in STRUCTURE.items():
        top_path = os.path.join(ROOT, top)
        ensure_dir(top_path)

        # Nested hierarchy
        if isinstance(entries, dict):
            for subfolder, files in entries.items():
                sub_path = os.path.join(top_path, subfolder)
                ensure_dir(sub_path)
                for file in files:
                    file_path = os.path.join(sub_path, file)
                    write_stub_file(file_path)

        # Flat file list
        elif isinstance(entries, list):
            for file in entries:
                file_path = os.path.join(top_path, file)
                write_stub_file(file_path)

    print("All data folders and stub files created/enforced successfully.")

if __name__ == "__main__":
    populate()

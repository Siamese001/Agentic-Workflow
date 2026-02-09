"""
Reproducible import verification script (v4).
Generated: 2026-02-09T03:42:13.423459+00:00

Verification contract:
  default:         require core only.
  --require-dev:   require core + dev.
  --require-infra: require core + infra (declared optional deps).
  --all:           require core + dev + infra (declared optional deps).

Output is keyed by dist package with per-import breakdown.
"""

import importlib
import sys

PACKAGES = {
    "core": [
        ("PyYAML", ["yaml"]),
        ("aiofiles", ["aiofiles"]),
        ("jinja2", ["jinja2"]),
        ("libcst", ["libcst"]),
        ("networkx", ["networkx"]),
        ("pinecone", ["pinecone"]),
        ("psutil", ["psutil"]),
        ("pydantic", ["pydantic"]),
        ("python-dotenv", ["dotenv"]),
        ("redis", ["redis"]),
        ("tenacity", ["tenacity"]),
        ("tqdm", ["tqdm"]),
        ("watchdog", ["watchdog"]),
    ],
    "dev": [
        ("pytest", ["pytest"]),
    ],
    "infra": [
        ("numpy", ["numpy"]),
        ("chromadb", ["chromadb"]),
        ("duckdb", ["duckdb"]),
        ("rank-bm25", ["rank_bm25"]),
        ("scikit-learn", ["sklearn"]),
        ("pydantic-settings", ["pydantic_settings"]),
        ("beautifulsoup4", ["bs4"]),
        ("dash", ["dash"]),
        ("fastapi", ["fastapi"]),
        ("livereload", ["livereload"]),
        ("pandas", ["pandas"]),
        ("playwright", ["playwright"]),
        ("plotly", ["plotly"]),
        ("waitress", ["waitress"]),
        ("rich", ["rich"]),
    ],
    "external": [
        ("FlagEmbedding", ["FlagEmbedding"]),
        ("GitPython", ["git"]),
        ("PyPDF2", ["PyPDF2"]),
        ("anthropic", ["anthropic"]),
        ("bandit", ["bandit"]),
        ("boto3", ["boto3"]),
        ("google-genai", ["google.genai"]),
        ("google-generativeai", ["google.generativeai"]),
        ("neo4j", ["neo4j"]),
        ("openai", ["openai"]),
        ("opentelemetry-api", ["opentelemetry"]),
        ("pdf2image", ["pdf2image"]),
        ("pdfplumber", ["pdfplumber"]),
        ("pypdf", ["pypdf"]),
        ("pytesseract", ["pytesseract"]),
        ("pytz", ["pytz"]),
        ("requests", ["requests"]),
        ("sentence-transformers", ["sentence_transformers"]),
        ("tabulate", ["tabulate"]),
        ("tiktoken", ["tiktoken"]),
        ("torch", ["torch"]),
        ("tree-sitter", ["tree_sitter"]),
        ("tree-sitter-python", ["tree_sitter_python"]),
        ("uvicorn", ["uvicorn"]),
        ("websockets", ["websockets"]),
    ],
    "sdks": [
        ("backoff", ["backoff"]),
        ("google-cloud-aiplatform", ["vertexai"]),
        ("jsonschema", ["jsonschema"]),
    ],
}


def main():
    require_dev = "--require-dev" in sys.argv
    require_infra = "--require-infra" in sys.argv
    require_all = "--all" in sys.argv

    required_buckets = {"core"}
    if require_dev:
        required_buckets.add("dev")
    if require_infra:
        required_buckets.add("infra")
    if require_all:
        required_buckets.update({"core", "dev", "infra"})

    bucket_ok = {}
    bucket_fail = {}
    bucket_skip = {}
    rows = []

    for bucket, packages in PACKAGES.items():
        required = bucket in required_buckets
        bucket_ok[bucket] = 0
        bucket_fail[bucket] = 0
        bucket_skip[bucket] = 0
        for dist, imports in packages:
            import_results = []
            all_ok = True
            for imp in imports:
                try:
                    importlib.import_module(imp)
                    import_results.append((imp, "OK"))
                except ImportError as e:
                    import_results.append((imp, f"MISSING: {e}"))
                    all_ok = False
            if all_ok:
                bucket_ok[bucket] += 1
                tag = "OK"
            elif required:
                bucket_fail[bucket] += 1
                tag = "FAIL"
            else:
                bucket_skip[bucket] += 1
                tag = "EXPECTED_MISSING"
            req_s = "REQ" if required else "OPT"
            imp_detail = ", ".join(f"{i}={s}" for i, s in import_results)
            rows.append(f"  [{bucket:5s}] [{req_s}] dist={dist:30s} {tag:18s} imports: {imp_detail}")

    for row in rows:
        print(row)

    print()
    print("Bucket Summary:")
    hdr = f"{'bucket':8s} {'required?':10s} {'OK':>4s} {'FAIL':>5s} {'SKIP':>5s} {'verdict':>8s}"
    print(f"  {hdr}")
    blocking = 0
    for bucket in PACKAGES:
        required = bucket in required_buckets
        ok = bucket_ok.get(bucket, 0)
        fail = bucket_fail.get(bucket, 0)
        skip = bucket_skip.get(bucket, 0)
        verdict = "PASS" if fail == 0 else "BLOCK"
        blocking += fail
        req_s = "yes" if required else "no"
        print(f"  {bucket:8s} {req_s:10s} {ok:4d} {fail:5d} {skip:5d} {verdict:>8s}")

    total_ok = sum(bucket_ok.values())
    total_fail = sum(bucket_fail.values())
    total_skip = sum(bucket_skip.values())
    total = total_ok + total_fail + total_skip
    print()
    print(f"Total: {total_ok}/{total} dist packages OK, {total_fail} BLOCKING, {total_skip} EXPECTED_MISSING")
    if blocking > 0:
        print(f"RESULT: FAIL ({blocking} blocking failures)")
        sys.exit(1)
    else:
        print("RESULT: PASS (all required imports OK)")
        sys.exit(0)


if __name__ == "__main__":
    main()

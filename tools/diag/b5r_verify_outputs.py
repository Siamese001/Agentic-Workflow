from pathlib import Path
import json

proof = Path("docs/reports/wave_b_b5r_chromadb_direct_proof.md")
qmap = Path("docs/reports/wave_b_b5r_family_query_map.md")
raw = Path("artifacts/b5r_proof_raw.json")

print(f"proof report : {proof.stat().st_size:,} bytes  exists={proof.exists()}")
print(f"query map    : {qmap.stat().st_size:,} bytes  exists={qmap.exists()}")
print(f"raw JSON     : {raw.stat().st_size:,} bytes  exists={raw.exists()}")

data = json.load(open(raw, encoding="utf-8"))
results = data["family_results"]
cont = data["contamination_summary"]

print(f"\nFamilies: {len(results)}")
print(f"ext_authority chunks: {cont['ext_authority']}")
print(f"repo_evidence chunks: {cont['repo_evidence']}")
print(f"ext_raw chunks:       {cont['ext_raw']}")

print("\nAll grade divergences:")
for r in results:
    fid = r["family"]["id"]
    claim = r["family"]["grade_claim"]
    live = r["live_grade"]
    if claim != live:
        print(f"  {fid}: claim={claim:<18}  live={live}")

print("\nBlocking family status:")
for r in results:
    if r["family"]["blocks_b6"]:
        fid = r["family"]["id"]
        live = r["live_grade"]
        d1 = r["dist_at_1"]
        rel = r["n_relevant_lt050"]
        print(f"  {fid}: live={live:<22}  dist@1={d1}  rel={rel}/5")

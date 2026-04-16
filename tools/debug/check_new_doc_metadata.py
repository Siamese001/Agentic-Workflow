"""C2.1 G4/G5/G6 invariant check for the new TS-20 doc chunks.

Temporary diagnostic script — safe to delete after C2.1 closeout.
"""

from __future__ import annotations

import chromadb

REQUIRED = [
    "source_collection",
    "source_band",
    "authority_tier",
    "normative_scope",
    "invalid_for_normative_use",
    "source_type",
    "topic_bucket",
    "doc_family",
    "source_url",
    "heading_path",
    "collapse_group",
    "title",
    "chunk_index",
    "canonical_digest",
    "file_path",
]

c = chromadb.PersistentClient(path=r"C:\Git\Agentic-Workflow\data\cache\chromadb").get_collection(
    "repo_evidence"
)
res = c.get(
    where={"file_path": "docs/requirements/normative_requirements_spec.md"},
    limit=50,
    include=["metadatas"],
)
n = len(res["ids"])
print(f"new_doc_chunks={n}")
if n == 0:
    raise SystemExit("FAIL: no chunks found for new doc")

metas = res["metadatas"]
m0 = metas[0]

missing = [k for k in REQUIRED if k not in m0]
print(f"G6_all_required_fields_present={not missing} missing={missing}")

invalids = [m for m in metas if m.get("invalid_for_normative_use") is not True]
print(f"G4_invalid_for_normative_use_True_on_all={len(invalids) == 0} violations={len(invalids)}")

with_https = [m for m in metas if str(m.get("source_url", "")).startswith("https://")]
print(f"G5_no_https_source_url={len(with_https) == 0} violations={len(with_https)}")

print(f"sample_metadata:")
print(f"  source_band={m0['source_band']}")
print(f"  authority_tier={m0['authority_tier']}")
print(f"  source_collection={m0['source_collection']}")
print(f"  invalid_for_normative_use={m0['invalid_for_normative_use']}")
print(f"  source_url={m0['source_url']}")
print(f"  doc_family={m0['doc_family']}")
print(f"  topic_bucket={m0['topic_bucket']}")
print(f"  collapse_group={m0['collapse_group']}")

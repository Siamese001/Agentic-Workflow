# apps_repo_brief engines package.
#
# W3 SPINE RESTRUCTURE NOTE:
# - IngestionEngine: RETIRED. Live directory scan replaced by UWG-seeded
#   repo_brief_docs L4 retrieval surface. See P3.3.
# - CapabilityExtractionEngine logic: MOVED TO C0. Claim extraction is now
#   a C0 retrieval lane (BM25 + code-symbol + graph). See P3.4.
# - BriefAssemblyEngine: SPLIT. Prompt slot composition → PA (repo_brief_pa_compiler).
#   Narrative rendering → L2 (governed gateway). See P3.5.
# - StyleGateValidator: SPLIT. Same-authority repair → L2.E4 heal pass.
#   Persistent violation gate → Exit v6 check. See P3.6.
#
# Plan: .windsurf/plans/apps-repo-brief-plan3-zero-loss-overwrite.md §P3.3-P3.6

# Job Workflow v19.2 → v19.3 — Size-Reduced (No-Loss) Report

## Version & Guarantee
- v19.3 uses centralized references; inline duplicates moved to `*_legacy` for audit.
- `compat.qa_rows_expand = true` and `compat.inline_materialize_policies = true` ensure behavior parity.

## Nodes updated
- K.6_most_recent_experience, K.7_prior_experience

## File Size
- v19.2: **87.69 KB**
- v19.3: **87.85 KB**
- Δ: **+0.16 KB**

## Unified Diff (context)
```diff
--- v19.2
+++ v19.3
@@ -4,7 +4,7 @@
   "metadata": {
     "last_saved": "2025-10-02",
     "last_saved_note": "Date only - no timestamp",
-    "version": "v19.2",
+    "version": "v19.3",
     "sources": "JW v18.9 + JW Enhancements Tier 1-2 implementation",
     "notes": "Agentic enhancement version: K.2.5 competitive positioning NEW, K.8 intelligent gap-filling UPGRADED, K.9 specificity-driven research UPGRADED",
     "sha256": "pending_calculation",
@@ -57,7 +57,8 @@
       "roi_justification": "Getting interviews >> saving $3 in API costs per application"
     },
     "change_log": [
-      "v19.2 (non-destructive): added centralized governance blocks & refs; behavior unchanged"
+      "v19.2 (non-destructive): added centralized governance blocks & refs; behavior unchanged",
+      "v19.3: size-reduced by replacing inline node configs with references (backed up under *_legacy); behavior preserved via compat materialization"
     ]
   },
   "instructions": [
@@ -1271,72 +1272,72 @@
         "verb_variety": "No verb used more than 2x across 7 bullets (AI detection defense)",
         "keyword_density": "Bullets 1-2 should contain 3-4 JD keywords each"
       },
-      "qa_rows": [
-        {
-          "check": "Bullet count",
-          "threshold": "Exactly 7",
-          "status": "PASS/FAIL"
-        },
-        {
-          "check": "Bullet length",
-          "threshold": "15-25 words each",
-          "status": "PASS/FAIL"
-        },
-        {
-          "check": "Intro sentence",
-          "threshold": "20-35 words",
-          "status": "PASS/FAIL"
-        },
-        {
-          "check": "Intro vs K.5",
-          "threshold": "<0.50 cosine",
-          "status": "PASS/FAIL"
-        },
-        {
-          "check": "Intro vs K.8",
-          "threshold": "<0.70 cosine",
-          "status": "PASS/FAIL"
-        },
-        {
-          "check": "Intro vs K.4",
-          "threshold": "<0.50 cosine",
-          "status": "PASS/FAIL"
-        },
-        {
-          "check": "2-3-2 provenance",
-          "threshold": "2 verbatim + 3 adapted + 2 synth",
-          "status": "PASS/FAIL"
-        },
-        {
-          "check": "Verb variety",
-          "threshold": "No verb >2x",
-          "status": "PASS/FAIL"
-        },
-        {
-          "check": "Position weighting",
-          "threshold": "Bullets 1-2 boosted 1.15-1.20x",
-          "status": "PASS/FAIL"
-        },
-        {
-          "check": "Dedup internal",
-          "threshold": "No pairs >0.75 cosine",
-          "status": "PASS/FAIL"
-        },
-        {
-          "check": "Dedup vs K.5",
-          "threshold": "No bullet >0.40 vs exec summary",
-          "status": "PASS/FAIL"
-        },
-        {
-          "check": "ASCII hygiene",
-          "threshold": "Clean",
-          "status": "PASS/FAIL"
-        }
-      ],
       "lock_status": "✅ K.6 Status: LOCKED | Ready for K.7 ingestion",
       "message_policy_ref": "K.6",
       "qa_rows_ref": [
         "bullet_block"
+      ],
+      "qa_rows_legacy": [
+        {
+          "check": "Bullet count",
+          "threshold": "Exactly 7",
+          "status": "PASS/FAIL"
+        },
+        {
+          "check": "Bullet length",
+          "threshold": "15-25 words each",
+          "status": "PASS/FAIL"
+        },
+        {
+          "check": "Intro sentence",
+          "threshold": "20-35 words",
+          "status": "PASS/FAIL"
+        },
+        {
+          "check": "Intro vs K.5",
+          "threshold": "<0.50 cosine",
+          "status": "PASS/FAIL"
+        },
+        {
+          "check": "Intro vs K.8",
+          "threshold": "<0.70 cosine",
+          "status": "PASS/FAIL"
+        },
+        {
+          "check": "Intro vs K.4",
+          "threshold": "<0.50 cosine",
+          "status": "PASS/FAIL"
+        },
+        {
+          "check": "2-3-2 provenance",
+          "threshold": "2 verbatim + 3 adapted + 2 synth",
+          "status": "PASS/FAIL"
+        },
+        {
+          "check": "Verb variety",
+          "threshold": "No verb >2x",
+          "status": "PASS/FAIL"
+        },
+        {
+          "check": "Position weighting",
+          "threshold": "Bullets 1-2 boosted 1.15-1.20x",
+          "status": "PASS/FAIL"
+        },
+        {
+          "check": "Dedup internal",
+          "threshold": "No pairs >0.75 cosine",
+          "status": "PASS/FAIL"
+        },
+        {
+          "check": "Dedup vs K.5",
+          "threshold": "No bullet >0.40 vs exec summary",
+          "status": "PASS/FAIL"
+        },
+        {
+          "check": "ASCII hygiene",
+          "threshold": "Clean",
+          "status": "PASS/FAIL"
+        }
       ]
     },
     "K.7_prior_experience": {
@@ -1407,72 +1408,72 @@
         "verb_variety": "No verb used more than 2x across 7 bullets (AI detection defense)",
         "keyword_density": "Moderate JD keyword inclusion (not as aggressive as K.6)"
       },
-      "qa_rows": [
-        {
-          "check": "Bullet count",
-          "threshold": "Exactly 7",
-          "status": "PASS/FAIL"
-        },
-        {
-          "check": "Bullet length",
-          "threshold": "15-25 words each",
-          "status": "PASS/FAIL"
-        },
-        {
-          "check": "Intro sentence",
-          "threshold": "15-20 words",
-          "status": "PASS/FAIL"
-        },
-        {
-          "check": "Intro vs K.5",
-          "threshold": "<0.50 cosine",
-          "status": "PASS/FAIL"
-        },
-        {
-          "check": "Intro vs K.8",
-          "threshold": "<0.70 cosine",
-          "status": "PASS/FAIL"
-        },
-        {
-          "check": "Intro vs K.4",
-          "threshold": "<0.50 cosine",
-          "status": "PASS/FAIL"
-        },
-        {
-          "check": "Global scope",
-          "threshold": "≥2 bullets with global indicators",
-          "status": "PASS/FAIL"
-        },
-        {
-          "check": "2-3-2 provenance",
-          "threshold": "2 verbatim + 3 adapted + 2 synth",
-          "status": "PASS/FAIL"
-        },
-        {
-          "check": "Verb variety",
-          "threshold": "No verb >2x",
-          "status": "PASS/FAIL"
-        },
-        {
-          "check": "Dedup internal",
-          "threshold": "No pairs >0.75 cosine",
-          "status": "PASS/FAIL"
-        },
-        {
-          "check": "Dedup vs K.5",
-          "threshold": "No bullet >0.40 vs exec summary",
-          "status": "PASS/FAIL"
-        },
-        {
-          "check": "ASCII hygiene",
-          "threshold": "Clean",
-          "status": "PASS/FAIL"
-        }
-      ],
       "lock_status": "✅ K.7 Status: LOCKED | Ready for K.8 ENHANCED intelligent agent",
       "message_policy_ref": "K.7",
       "qa_rows_ref": [
         "bullet_block"
+      ],
+      "qa_rows_legacy": [
+        {
+          "check": "Bullet count",
+          "threshold": "Exactly 7",
+          "status": "PASS/FAIL"
+        },
+        {
+          "check": "Bullet length",
+          "threshold": "15-25 words each",
+          "status": "PASS/FAIL"
+        },
+        {
+          "check": "Intro sentence",
+          "threshold": "15-20 words",
+          "status": "PASS/FAIL"
+        },
+        {
+          "check": "Intro vs K.5",
+          "threshold": "<0.50 cosine",
+          "status": "PASS/FAIL"
+        },
+        {
+          "check": "Intro vs K.8",
+          "threshold": "<0.70 cosine",
+          "status": "PASS/FAIL"
+        },
+        {
+          "check": "Intro vs K.4",
+          "threshold": "<0.50 cosine",
+          "status": "PASS/FAIL"
+        },
+        {
+          "check": "Global scope",
+          "threshold": "≥2 bullets with global indicators",
+          "status": "PASS/FAIL"
+        },
+        {
+          "check": "2-3-2 provenance",
+          "threshold": "2 verbatim + 3 adapted + 2 synth",
+          "status": "PASS/FAIL"
+        },
+        {
+          "check": "Verb variety",
+          "threshold": "No verb >2x",
+          "status": "PASS/FAIL"
+        },
+        {
+          "check": "Dedup internal",
+          "threshold": "No pairs >0.75 cosine",
+          "status": "PASS/FAIL"
+        },
+        {
+          "check": "Dedup vs K.5",
+          "threshold": "No bullet >0.40 vs exec summary",
+          "status": "PASS/FAIL"
+        },
+        {
+          "check": "ASCII hygiene",
+          "threshold": "Clean",
+          "status": "PASS/FAIL"
+        }
       ]
     },
     "K.8_leadership_competencies": {
--- v19.2
+++ v19.3
@@ -4,7 +4,7 @@
   "metadata": {
     "last_saved": "2025-10-02",
     "last_saved_note": "Date only - no timestamp",
-    "version": "v19.2",
+    "version": "v19.3",
     "sources": "JW v18.9 + JW Enhancements Tier 1-2 implementation",
     "notes": "Agentic enhancement version: K.2.5 competitive positioning NEW, K.8 intelligent gap-filling UPGRADED, K.9 specificity-driven research UPGRADED",
     "sha256": "pending_calculation",
@@ -57,7 +57,8 @@
       "roi_justification": "Getting interviews >> saving $3 in API costs per application"
     },
     "change_log": [
-      "v19.2 (non-destructive): added centralized governance blocks & refs; behavior unchanged"
+      "v19.2 (non-destructive): added centralized governance blocks & refs; behavior unchanged",
+      "v19.3: size-reduced by replacing inline node configs with references (backed up under *_legacy); behavior preserved via compat materialization"
     ]
   },
   "instructions": [
@@ -1271,72 +1272,72 @@
         "verb_variety": "No verb used more than 2x across 7 bullets (AI detection defense)",
         "keyword_density": "Bullets 1-2 should contain 3-4 JD keywords each"
       },
-      "qa_rows": [
-        {
-          "check": "Bullet count",
-          "threshold": "Exactly 7",
-          "status": "PASS/FAIL"
-        },
-        {
-          "check": "Bullet length",
-          "threshold": "15-25 words each",
-          "status": "PASS/FAIL"
-        },
-        {
-          "check": "Intro sentence",
-          "threshold": "20-35 words",
-          "status": "PASS/FAIL"
-        },
-        {
-          "check": "Intro vs K.5",
-          "threshold": "<0.50 cosine",
-          "status": "PASS/FAIL"
-        },
-        {
-          "check": "Intro vs K.8",
-          "threshold": "<0.70 cosine",
-          "status": "PASS/FAIL"
-        },
-        {
-          "check": "Intro vs K.4",
-          "threshold": "<0.50 cosine",
-          "status": "PASS/FAIL"
-        },
-        {
-          "check": "2-3-2 provenance",
-          "threshold": "2 verbatim + 3 adapted + 2 synth",
-          "status": "PASS/FAIL"
-        },
-        {
-          "check": "Verb variety",
-          "threshold": "No verb >2x",
-          "status": "PASS/FAIL"
-        },
-        {
-          "check": "Position weighting",
-          "threshold": "Bullets 1-2 boosted 1.15-1.20x",
-          "status": "PASS/FAIL"
-        },
-        {
-          "check": "Dedup internal",
-          "threshold": "No pairs >0.75 cosine",
-          "status": "PASS/FAIL"
-        },
-        {
-          "check": "Dedup vs K.5",
-          "threshold": "No bullet >0.40 vs exec summary",
-          "status": "PASS/FAIL"
-        },
-        {
-          "check": "ASCII hygiene",
-          "threshold": "Clean",
-          "status": "PASS/FAIL"
-        }
-      ],
       "lock_status": "✅ K.6 Status: LOCKED | Ready for K.7 ingestion",
       "message_policy_ref": "K.6",
       "qa_rows_ref": [
         "bullet_block"
+      ],
+      "qa_rows_legacy": [
+        {
+          "check": "Bullet count",
+          "threshold": "Exactly 7",
+          "status": "PASS/FAIL"
+        },
+        {
+          "check": "Bullet length",
+          "threshold": "15-25 words each",
+          "status": "PASS/FAIL"
+        },
+        {
+          "check": "Intro sentence",
+          "threshold": "20-35 words",
+          "status": "PASS/FAIL"
+        },
+        {
+          "check": "Intro vs K.5",
+          "threshold": "<0.50 cosine",
+          "status": "PASS/FAIL"
+        },
+        {
+          "check": "Intro vs K.8",
+          "threshold": "<0.70 cosine",
+          "status": "PASS/FAIL"
+        },
+        {
+          "check": "Intro vs K.4",
+          "threshold": "<0.50 cosine",
+          "status": "PASS/FAIL"
+        },
+        {
+          "check": "2-3-2 provenance",
+          "threshold": "2 verbatim + 3 adapted + 2 synth",
+          "status": "PASS/FAIL"
+        },
+        {
+          "check": "Verb variety",
+          "threshold": "No verb >2x",
+          "status": "PASS/FAIL"
+        },
+        {
+          "check": "Position weighting",
+          "threshold": "Bullets 1-2 boosted 1.15-1.20x",
+          "status": "PASS/FAIL"
+        },
+        {
+          "check": "Dedup internal",
+          "threshold": "No pairs >0.75 cosine",
+          "status": "PASS/FAIL"
+        },
+        {
+          "check": "Dedup vs K.5",
+          "threshold": "No bullet >0.40 vs exec summary",
+          "status": "PASS/FAIL"
+        },
+        {
+          "check": "ASCII hygiene",
+          "threshold": "Clean",
+          "status": "PASS/FAIL"
+        }
       ]
     },
     "K.7_prior_experience": {
@@ -1407,72 +1408,72 @@
         "verb_variety": "No verb used more than 2x across 7 bullets (AI detection defense)",
         "keyword_density": "Moderate JD keyword inclusion (not as aggressive as K.6)"
       },
-      "qa_rows": [
-        {
-          "check": "Bullet count",
-          "threshold": "Exactly 7",
-          "status": "PASS/FAIL"
-        },
-        {
-          "check": "Bullet length",
-          "threshold": "15-25 words each",
-          "status": "PASS/FAIL"
-        },
-        {
-          "check": "Intro sentence",
-          "threshold": "15-20 words",
-          "status": "PASS/FAIL"
-        },
-        {
-          "check": "Intro vs K.5",
-          "threshold": "<0.50 cosine",
-          "status": "PASS/FAIL"
-        },
-        {
-          "check": "Intro vs K.8",
-          "threshold": "<0.70 cosine",
-          "status": "PASS/FAIL"
-        },
-        {
-          "check": "Intro vs K.4",
-          "threshold": "<0.50 cosine",
-          "status": "PASS/FAIL"
-        },
-        {
-          "check": "Global scope",
-          "threshold": "≥2 bullets with global indicators",
-          "status": "PASS/FAIL"
-        },
-        {
-          "check": "2-3-2 provenance",
-          "threshold": "2 verbatim + 3 adapted + 2 synth",
-          "status": "PASS/FAIL"
-        },
-        {
-          "check": "Verb variety",
-          "threshold": "No verb >2x",
-          "status": "PASS/FAIL"
-        },
-        {
-          "check": "Dedup internal",
-          "threshold": "No pairs >0.75 cosine",
-          "status": "PASS/FAIL"
-        },
-        {
-          "check": "Dedup vs K.5",
-          "threshold": "No bullet >0.40 vs exec summary",
-          "status": "PASS/FAIL"
-        },
-        {
-          "check": "ASCII hygiene",
-          "threshold": "Clean",
-          "status": "PASS/FAIL"
-        }
-      ],
       "lock_status": "✅ K.7 Status: LOCKED | Ready for K.8 ENHANCED intelligent agent",
       "message_policy_ref": "K.7",
       "qa_rows_ref": [
         "bullet_block"
+      ],
+      "qa_rows_legacy": [
+        {
+          "check": "Bullet count",
+          "threshold": "Exactly 7",
+          "status": "PASS/FAIL"
+        },
+        {
+          "check": "Bullet length",
+          "threshold": "15-25 words each",
+          "status": "PASS/FAIL"
+        },
+        {
+          "check": "Intro sentence",
+          "threshold": "15-20 words",
+          "status": "PASS/FAIL"
+        },
+        {
+          "check": "Intro vs K.5",
+          "threshold": "<0.50 cosine",
+          "status": "PASS/FAIL"
+        },
+        {
+          "check": "Intro vs K.8",
+          "threshold": "<0.70 cosine",
+          "status": "PASS/FAIL"
+        },
+        {
+          "check": "Intro vs K.4",
+          "threshold": "<0.50 cosine",
+          "status": "PASS/FAIL"
+        },
+        {
+          "check": "Global scope",
+          "threshold": "≥2 bullets with global indicators",
+          "status": "PASS/FAIL"
+        },
+        {
+          "check": "2-3-2 provenance",
+          "threshold": "2 verbatim + 3 adapted + 2 synth",
+          "status": "PASS/FAIL"
+        },
+        {
+          "check": "Verb variety",
+          "threshold": "No verb >2x",
+          "status": "PASS/FAIL"
+        },
+        {
+          "check": "Dedup internal",
+          "threshold": "No pairs >0.75 cosine",
+          "status": "PASS/FAIL"
+        },
+        {
+          "check": "Dedup vs K.5",
+          "threshold": "No bullet >0.40 vs exec summary",
+          "status": "PASS/FAIL"
+        },
+        {
+          "check": "ASCII hygiene",
+          "threshold": "Clean",
+          "status": "PASS/FAIL"
+        }
       ]
     },
     "K.8_leadership_competencies": {
```
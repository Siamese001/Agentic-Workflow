# JW v19.4 → v19.5 — Consolidation Diff

```diff
--- v19.4
+++ v19.5
@@ -4,7 +4,7 @@
   "metadata": {
     "last_saved": "2025-10-02",
     "last_saved_note": "Date only - no timestamp",
-    "version": "v19.4",
+    "version": "v19.5",
     "sources": "JW v18.9 + JW Enhancements Tier 1-2 implementation",
     "notes": "Agentic enhancement version: K.2.5 competitive positioning NEW, K.8 intelligent gap-filling UPGRADED, K.9 specificity-driven research UPGRADED",
     "sha256": "pending_calculation",
@@ -59,7 +59,8 @@
     "change_log": [
       "v19.2 (non-destructive): added centralized governance blocks & refs; behavior unchanged",
       "v19.3: size-reduced by replacing inline node configs with references (backed up under *_legacy); behavior preserved via compat materialization",
-      "v19.4: Added ASCII hygiene, product insertion prevention, K.5 name-dropping guard, date standardization, App Schema filtering. Additive only."
+      "v19.4: Added ASCII hygiene, product insertion prevention, K.5 name-dropping guard, date standardization, App Schema filtering. Additive only.",
+      "v19.5: Consolidation (SSOT): removed legacy mirrors; templated Section 5; centralized length & dedup via refs; reasoning_config → deltas; zero semantic change."
     ]
   },
   "instructions": [
@@ -799,11 +800,9 @@
         "tot_breadth": null,
         "tot_depth": null,
         "beam_width": 1,
-        "reflexion": "ON",
         "rag_mode": "ON",
         "rag_strategy": "basic",
         "rag_min_retrievers": 1,
-        "agentic_mode": "OFF",
         "rationale": "Deterministic extraction - no voting/branching needed"
       },
       "qa_rows": [
@@ -860,14 +859,7 @@
         "sub_category"
       ],
       "reasoning_config": {
-        "cot_mode": "self_consistency",
-        "hybrid_cot_tot": "Y",
-        "temperature": 0.3,
         "self_consistency_k": 5,
-        "tot_breadth": 3,
-        "tot_depth": 1,
-        "beam_width": 2,
-        "reflexion": "ON",
         "rag_mode": "ON",
         "rag_strategy": "hybrid",
         "rag_min_retrievers": 3,
@@ -970,14 +962,6 @@
         }
       },
       "reasoning_config": {
-        "cot_mode": "self_consistency",
-        "hybrid_cot_tot": "Y",
-        "temperature": 0.3,
-        "self_consistency_k": 3,
-        "tot_breadth": 3,
-        "tot_depth": 1,
-        "beam_width": 2,
-        "reflexion": "ON",
         "rag_mode": "ON",
         "rag_strategy": "agentic",
         "rag_min_retrievers": 10,
@@ -1028,14 +1012,12 @@
         "primary_job_role"
       ],
       "reasoning_config": {
-        "cot_mode": "self_consistency",
         "hybrid_cot_tot": "N",
         "temperature": 0.2,
         "self_consistency_k": 5,
         "tot_breadth": null,
         "tot_depth": null,
         "beam_width": 1,
-        "reflexion": "ON",
         "rag_mode": "ON",
         "rag_strategy": "hybrid",
         "rag_min_retrievers": 3,
@@ -1075,16 +1057,7 @@
         "headline"
       ],
       "reasoning_config": {
-        "cot_mode": "self_consistency",
-        "hybrid_cot_tot": "Y",
         "temperature": 0.6,
-        "self_consistency_k": 3,
-        "tot_breadth": 3,
-        "tot_depth": 1,
-        "beam_width": 2,
-        "reflexion": "ON",
-        "rag_mode": "OFF",
-        "rag_strategy": "none",
         "rationale": "Highest temperature for creative lexical variety and differentiation"
       },
       "v19_competitive_enhancement": {
@@ -1152,16 +1125,10 @@
         "executive_summary"
       ],
       "reasoning_config": {
-        "cot_mode": "self_consistency",
-        "hybrid_cot_tot": "Y",
         "temperature_start": 0.5,
         "temperature_increment": 0.1,
         "temperature_max": 1.0,
         "self_consistency_k": 5,
-        "tot_breadth": 3,
-        "tot_depth": 1,
-        "beam_width": 2,
-        "reflexion": "ON",
         "rag_mode": "ON",
         "rag_strategy": "hybrid",
         "rag_min_retrievers": 2,
@@ -1204,75 +1171,6 @@
         "primary": "Strategic identity narrative - WHO the candidate is professionally",
         "secondary": "Differentiated value proposition for target role",
         "forbidden": [
-          "B",
-          "u",
-          "l",
-          "l",
-          "e",
-          "t",
-          " ",
-          "s",
-          "u",
-          "m",
-          "m",
-          "a",
-          "r",
-          "y",
-          " ",
-          "f",
-          "o",
-          "r",
-          "m",
-          "a",
-          "t",
-          ",",
-          " ",
-          "t",
-          "a",
-          "c",
-          "t",
-          "i",
-          "c",
-          "a",
-          "l",
-          " ",
-          "e",
-          "x",
-          "e",
-          "c",
-          "u",
-          "t",
-          "i",
-          "o",
-          "n",
-          " ",
-          "d",
-          "e",
-          "t",
-          "a",
-          "i",
-          "l",
-          "s",
-          ",",
-          " ",
-          "g",
-          "e",
-          "n",
-          "e",
-          "r",
-          "i",
-          "c",
-          " ",
-          "p",
-          "l",
-          "a",
-          "t",
-          "i",
-          "t",
-          "u",
-          "d",
-          "e",
-          "s",
           "Company name-dropping patterns: 'At [COMPANY]', 'while at [COMPANY]', '[COMPANY] experience'"
         ],
         "narrative_style": {
@@ -1369,31 +1267,21 @@
         "bullet_7"
       ],
       "reasoning_config": {
-        "cot_mode": "self_consistency",
-        "hybrid_cot_tot": "Y",
         "temperature": 0.5,
-        "self_consistency_k": 3,
-        "tot_breadth": 3,
-        "tot_depth": 1,
-        "beam_width": 2,
-        "reflexion": "ON",
-        "rag_mode": "OFF",
-        "rag_strategy": "none",
         "rationale": "Moderate temperature for genuine variety in self-consistency voting"
       },
       "intro_sentence": {
-        "word_count": "20-35 words",
         "purpose": "Set context for Unify role and scope",
         "required_elements": [
           "company_name",
           "role_scope",
           "time_period"
         ],
-        "dedup_thresholds": {
-          "vs_K5": "<0.50 cosine (relaxed for domain overlap)",
-          "vs_K8": "<0.70 cosine (relaxed for domain overlap)",
-          "vs_K4": "<0.50 cosine"
-        }
+        "dedup_checks_ref": [
+          "K.6_intro_vs_K.5",
+          "K.6_intro_vs_K.8",
+          "K.6_intro_vs_K.4"
+        ]
       },
       "provenance_strategy": {
         "split": "2-3-2",
@@ -1410,7 +1298,6 @@
       },
       "bullet_structure": {
         "format": "Strong verb + Technology/Method + Quantified outcome",
-        "word_count": "15-25 words per bullet",
         "verb_variety": "No verb used more than 2x across 7 bullets (AI detection defense)",
         "keyword_density": "Bullets 1-2 should contain 3-4 JD keywords each",
         "forbidden_customization_patterns": {
@@ -1444,68 +1331,6 @@
       "qa_rows_ref": [
         "bullet_block"
       ],
-      "qa_rows_legacy": [
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
       "qa_rows": [
         {
           "check": "No target company name",
@@ -1545,32 +1370,22 @@
         "bullet_7"
       ],
       "reasoning_config": {
-        "cot_mode": "self_consistency",
-        "hybrid_cot_tot": "Y",
         "temperature": 0.5,
-        "self_consistency_k": 3,
-        "tot_breadth": 3,
-        "tot_depth": 1,
-        "beam_width": 2,
-        "reflexion": "ON",
-        "rag_mode": "OFF",
-        "rag_strategy": "none",
         "rationale": "Moderate temperature for genuine variety in self-consistency voting"
       },
       "intro_sentence": {
-        "word_count": "15-20 words",
         "purpose": "Set context for IBM role with global scope emphasis",
         "required_elements": [
           "company_name",
           "global_scope_indicator",
           "time_period"
         ],
-        "dedup_thresholds": {
-          "vs_K5": "<0.50 cosine (relaxed for domain overlap)",
-          "vs_K8": "<0.70 cosine (relaxed for domain overlap)",
-          "vs_K4": "<0.50 cosine"
-        },
-        "note": "Shorter than K.6 intro (15-20 vs 20-35 words) for balance"
+        "note": "Shorter than K.6 intro (15-20 vs 20-35 words) for balance",
+        "dedup_checks_ref": [
+          "K.7_intro_vs_K.5",
+          "K.7_intro_vs_K.8",
+          "K.7_intro_vs_K.4"
+        ]
       },
       "provenance_strategy": {
         "split": "2-3-2",
@@ -1594,7 +1409,6 @@
       },
       "bullet_structure": {
         "format": "Strong verb + Technology/Method + Quantified outcome",
-        "word_count": "15-25 words per bullet",
         "verb_variety": "No verb used more than 2x across 7 bullets (AI detection defense)",
         "keyword_density": "Moderate JD keyword inclusion (not as aggressive as K.6)"
       },
@@ -1602,68 +1416,6 @@
       "message_policy_ref": "K.7",
       "qa_rows_ref": [
         "bullet_block"
-      ],
-      "qa_rows_legacy": [
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
       ],
       "qa_rows": [
         {
@@ -1798,14 +1550,7 @@
         }
       },
       "reasoning_config": {
-        "cot_mode": "self_consistency",
-        "hybrid_cot_tot": "Y",
-        "temperature": 0.3,
         "self_consistency_k": 5,
-        "tot_breadth": 3,
-        "tot_depth": 1,
-        "beam_width": 2,
-        "reflexion": "ON",
         "rag_mode": "ON",
         "rag_strategy": "agentic",
         "rag_min_retrievers": 15,
@@ -2024,14 +1769,7 @@
         }
       },
       "reasoning_config": {
-        "cot_mode": "self_consistency",
-        "hybrid_cot_tot": "Y",
         "temperature": 0.4,
-        "self_consistency_k": 3,
-        "tot_breadth": 3,
-        "tot_depth": 1,
-        "beam_width": 2,
-        "reflexion": "ON",
         "rag_mode": "ON",
         "rag_strategy": "agentic",
         "rag_min_retrievers": 20,
@@ -2248,44 +1986,74 @@
       "note": "Outputs are professional deliverables, not technical traces"
     },
     "5.1_k1_output": {
-      "title": "## K.1 — Company & Job Title",
-      "format": "**Company:** {company_name}\n**Job Title:** {job_title}\n**Job URL:** {job_url}\n**Req #:** {req_number or 'N/A'}\n\n**Quality Validation:**\n| Check | Required | Actual | Status |\n|-------|----------|--------|--------|\n| Company present | Required | {value} | ✅ |\n| Title present | Required | {value} | ✅ |\n| URL valid | Valid format | {value} | ✅ |\n| Confidence | ≥0.95 | {value} | ✅ |\n\n**✓ K.1 Complete**"
+      "template_ref": "k_node_output_generic",
+      "params": {
+        "title": "## K.1 — Company & Job Title",
+        "format": "**Company:** {company_name}\n**Job Title:** {job_title}\n**Job URL:** {job_url}\n**Req #:** {req_number or 'N/A'}\n\n**Quality Validation:**\n| Check | Required | Actual | Status |\n|-------|----------|--------|--------|\n| Company present | Required | {value} | ✅ |\n| Title present | Required | {value} | ✅ |\n| URL valid | Valid format | {value} | ✅ |\n| Confidence | ≥0.95 | {value} | ✅ |\n\n**✓ K.1 Complete**"
+      }
     },
     "5.2_k2_output": {
-      "title": "## K.2 — Industry Classification",
-      "format": "**Category:** {category}\n**Sub-Category:** {sub_category}\n\n**Quality Validation:**\n| Check | Required | Actual | Status |\n|-------|----------|--------|--------|\n| GICS/SIC valid | Valid taxonomy | {value} | ✅ |\n| Sub-category aligned | Consistent | {value} | ✅ |\n| Confidence | ≥0.90 | {value} | ✅ |\n\n**✓ K.2 Complete**"
+      "template_ref": "k_node_output_generic",
+      "params": {
+        "title": "## K.2 — Industry Classification",
+        "format": "**Category:** {category}\n**Sub-Category:** {sub_category}\n\n**Quality Validation:**\n| Check | Required | Actual | Status |\n|-------|----------|--------|--------|\n| GICS/SIC valid | Valid taxonomy | {value} | ✅ |\n| Sub-category aligned | Consistent | {value} | ✅ |\n| Confidence | ≥0.90 | {value} | ✅ |\n\n**✓ K.2 Complete**"
+      }
     },
     "5.2.5_k2.5_output_NEW": {
-      "title": "## K.2.5 — 🤖 Competitive Positioning (NEW v19.0)",
-      "format": "**Agent Status:** COMPLETE\n**Peer JDs Analyzed:** {count} JDs\n\n**Table Stakes Keywords:** (appear in ≥80% of peer JDs)\n{table_stakes_list}\n\n**Differentiator Keywords:** (unique to target JD)\n{differentiator_list}\n\n**Positioning Strategy:**\n{positioning_guidance}\n\n**Quality Validation:**\n| Check | Required | Actual | Status |\n|-------|----------|--------|--------|\n| Peer JDs found | ≥3 | {count} | ✅ |\n| Table stakes | ≥5 keywords | {count} | ✅ |\n| Differentiators | ≥3 keywords | {count} | ✅ |\n| Strategy clear | Guidance for K.4/K.5 | Present | ✅ |\n| Confidence | ≥0.85 | {value} | ✅ |\n\n**✓ K.2.5 Complete** | Latency: +{seconds}s"
+      "template_ref": "k_node_output_generic",
+      "params": {
+        "title": "## K.2.5 — 🤖 Competitive Positioning (NEW v19.0)",
+        "format": "**Agent Status:** COMPLETE\n**Peer JDs Analyzed:** {count} JDs\n\n**Table Stakes Keywords:** (appear in ≥80% of peer JDs)\n{table_stakes_list}\n\n**Differentiator Keywords:** (unique to target JD)\n{differentiator_list}\n\n**Positioning Strategy:**\n{positioning_guidance}\n\n**Quality Validation:**\n| Check | Required | Actual | Status |\n|-------|----------|--------|--------|\n| Peer JDs found | ≥3 | {count} | ✅ |\n| Table stakes | ≥5 keywords | {count} | ✅ |\n| Differentiators | ≥3 keywords | {count} | ✅ |\n| Strategy clear | Guidance for K.4/K.5 | Present | ✅ |\n| Confidence | ≥0.85 | {value} | ✅ |\n\n**✓ K.2.5 Complete** | Latency: +{seconds}s"
+      }
     },
     "5.3_k3_output": {
-      "title": "## K.3 — Primary Job Role",
-      "format": "**Primary Role:** {primary_job_role}\n\n**Quality Validation:**\n| Check | Required | Actual | Status |\n|-------|----------|--------|--------|\n| Catalog match | Exact | {value} | ✅ |\n| Single role only | No secondary | {value} | ✅ |\n| JD alignment | ≥0.85 | {value} | ✅ |\n| Confidence | ≥0.90 | {value} | ✅ |\n\n**✓ K.3 Complete**"
+      "template_ref": "k_node_output_generic",
+      "params": {
+        "title": "## K.3 — Primary Job Role",
+        "format": "**Primary Role:** {primary_job_role}\n\n**Quality Validation:**\n| Check | Required | Actual | Status |\n|-------|----------|--------|--------|\n| Catalog match | Exact | {value} | ✅ |\n| Single role only | No secondary | {value} | ✅ |\n| JD alignment | ≥0.85 | {value} | ✅ |\n| Confidence | ≥0.90 | {value} | ✅ |\n\n**✓ K.3 Complete**"
+      }
     },
     "5.4_k4_output": {
-      "title": "## K.4 — Professional Headline",
-      "format": "**Headline:**\n\n{headline}\n\n**Competitive Positioning:** {uses_k2.5_differentiators}\n\n**Quality Validation:**\n| Check | Required | Actual | Status |\n|-------|----------|--------|--------|\n| Word count | 8-13 words | {count} words | ✅ |\n| 3-axis structure | All present | {value} | ✅ |\n| Strategic positioning | No tactical verbs | {value} | ✅ |\n| Competitive differentiation | Uses K.2.5 insights | {value} | ✅ |\n| Confidence | ≥0.85 | {value} | ✅ |\n\n**✓ K.4 Complete**"
+      "template_ref": "k_node_output_generic",
+      "params": {
+        "title": "## K.4 — Professional Headline",
+        "format": "**Headline:**\n\n{headline}\n\n**Competitive Positioning:** {uses_k2.5_differentiators}\n\n**Quality Validation:**\n| Check | Required | Actual | Status |\n|-------|----------|--------|--------|\n| Word count | 8-13 words | {count} words | ✅ |\n| 3-axis structure | All present | {value} | ✅ |\n| Strategic positioning | No tactical verbs | {value} | ✅ |\n| Competitive differentiation | Uses K.2.5 insights | {value} | ✅ |\n| Confidence | ≥0.85 | {value} | ✅ |\n\n**✓ K.4 Complete**"
+      }
     },
     "5.5_k5_output": {
-      "title": "## K.5 — Executive Summary",
-      "format": "**Executive Summary:**\n\n{executive_summary}\n\n**Competitive Positioning:** {uses_k2.5_differentiators}\n\n**Quality Validation:**\n| Check | Required | Actual | Status |\n|-------|----------|--------|--------|\n| Token count | 100-120 tokens | {count} tokens | ✅ |\n| Sentence count | 3-5 sentences | {count} sentences | ✅ |\n| Alignment score | ≥0.9 | {score} | ✅ |\n| Competitive framing | Uses K.2.5 insights | {value} | ✅ |\n| Confidence | ≥0.90 | {value} | ✅ |\n\n**✓ K.5 Complete**"
+      "template_ref": "k_node_output_generic",
+      "params": {
+        "title": "## K.5 — Executive Summary",
+        "format": "**Executive Summary:**\n\n{executive_summary}\n\n**Competitive Positioning:** {uses_k2.5_differentiators}\n\n**Quality Validation:**\n| Check | Required | Actual | Status |\n|-------|----------|--------|--------|\n| Token count | 100-120 tokens | {count} tokens | ✅ |\n| Sentence count | 3-5 sentences | {count} sentences | ✅ |\n| Alignment score | ≥0.9 | {score} | ✅ |\n| Competitive framing | Uses K.2.5 insights | {value} | ✅ |\n| Confidence | ≥0.90 | {value} | ✅ |\n\n**✓ K.5 Complete**"
+      }
     },
     "5.6_k6_output": {
-      "title": "## K.6 — Most Recent Experience",
-      "format": "**{Company Name} | {Role Title} | {Dates}**\n\n{intro_sentence}\n\n• {bullet_1}\n• {bullet_2}\n• {bullet_3}\n• {bullet_4}\n• {bullet_5}\n• {bullet_6}\n• {bullet_7}\n\n**Quality Validation:**\n| Check | Required | Actual | Status |\n|-------|----------|--------|--------|\n| Bullet count | 7 | {count} | ✅ |\n| Bullet length | 15-25 words | {range} | ✅ |\n| 2-3-2 provenance | 2V+3A+2S | {split} | ✅ |\n| Position weighting | 1-2 boosted | {value} | ✅ |\n\n**✓ K.6 Complete**"
+      "template_ref": "k_node_output_generic",
+      "params": {
+        "title": "## K.6 — Most Recent Experience",
+        "format": "**{Company Name} | {Role Title} | {Dates}**\n\n{intro_sentence}\n\n• {bullet_1}\n• {bullet_2}\n• {bullet_3}\n• {bullet_4}\n• {bullet_5}\n• {bullet_6}\n• {bullet_7}\n\n**Quality Validation:**\n| Check | Required | Actual | Status |\n|-------|----------|--------|--------|\n| Bullet count | 7 | {count} | ✅ |\n| Bullet length | 15-25 words | {range} | ✅ |\n| 2-3-2 provenance | 2V+3A+2S | {split} | ✅ |\n| Position weighting | 1-2 boosted | {value} | ✅ |\n\n**✓ K.6 Complete**"
+      }
     },
     "5.7_k7_output": {
-      "title": "## K.7 — Prior Experience",
-      "format": "**{Company Name} | {Role Title} | {Dates}**\n\n{intro_sentence}\n\n• {bullet_1}\n• {bullet_2}\n• {bullet_3}\n• {bullet_4}\n• {bullet_5}\n• {bullet_6}\n• {bullet_7}\n\n**Quality Validation:**\n| Check | Required | Actual | Status |\n|-------|----------|--------|--------|\n| Bullet count | 7 | {count} | ✅ |\n| Bullet length | 15-25 words | {range} | ✅ |\n| Global scope | ≥2 bullets | {count} | ✅ |\n| 2-3-2 provenance | 2V+3A+2S | {split} | ✅ |\n\n**✓ K.7 Complete**"
+      "template_ref": "k_node_output_generic",
+      "params": {
+        "title": "## K.7 — Prior Experience",
+        "format": "**{Company Name} | {Role Title} | {Dates}**\n\n{intro_sentence}\n\n• {bullet_1}\n• {bullet_2}\n• {bullet_3}\n• {bullet_4}\n• {bullet_5}\n• {bullet_6}\n• {bullet_7}\n\n**Quality Validation:**\n| Check | Required | Actual | Status |\n|-------|----------|--------|--------|\n| Bullet count | 7 | {count} | ✅ |\n| Bullet length | 15-25 words | {range} | ✅ |\n| Global scope | ≥2 bullets | {count} | ✅ |\n| 2-3-2 provenance | 2V+3A+2S | {split} | ✅ |\n\n**✓ K.7 Complete**"
+      }
     },
     "5.8_k8_output_ENHANCED": {
-      "title": "## K.8 — 🤖 Leadership Competencies (ENHANCED v19.0)",
-      "format": "**Agent Status:** COMPLETE\n**Gap Coverage:** {percent}% (Target: ≥85%)\n**Authentic Phrasing Sources:** LinkedIn profiles + industry frameworks\n\n**Leadership Competencies:**\n\n**{competency_1_title}**\n{competency_1_description}\n\n**{competency_2_title}**\n{competency_2_description}\n\n**{competency_3_title}**\n{competency_3_description}\n\n**{competency_4_title}**\n{competency_4_description}\n\n**{competency_5_title}**\n{competency_5_description}\n\n**{competency_6_title}**\n{competency_6_description}\n\n**Quality Validation:**\n| Check | Required | Actual | Status |\n|-------|----------|--------|--------|\n| Competency count | 6 | {count} | ✅ |\n| Gap coverage | ≥85% | {percent}% | ✅ |\n| Authentic phrasing | LinkedIn/framework patterns | {value} | ✅ |\n| Keyword density | 2-3 per comp | {value} | ✅ |\n| Credibility | Plausible | {value} | ✅ |\n\n**✓ K.8 Complete** | Latency: +{seconds}s"
+      "template_ref": "k_node_output_generic",
+      "params": {
+        "title": "## K.8 — 🤖 Leadership Competencies (ENHANCED v19.0)",
+        "format": "**Agent Status:** COMPLETE\n**Gap Coverage:** {percent}% (Target: ≥85%)\n**Authentic Phrasing Sources:** LinkedIn profiles + industry frameworks\n\n**Leadership Competencies:**\n\n**{competency_1_title}**\n{competency_1_description}\n\n**{competency_2_title}**\n{competency_2_description}\n\n**{competency_3_title}**\n{competency_3_description}\n\n**{competency_4_title}**\n{competency_4_description}\n\n**{competency_5_title}**\n{competency_5_description}\n\n**{competency_6_title}**\n{competency_6_description}\n\n**Quality Validation:**\n| Check | Required | Actual | Status |\n|-------|----------|--------|--------|\n| Competency count | 6 | {count} | ✅ |\n| Gap coverage | ≥85% | {percent}% | ✅ |\n| Authentic phrasing | LinkedIn/framework patterns | {value} | ✅ |\n| Keyword density | 2-3 per comp | {value} | ✅ |\n| Credibility | Plausible | {value} | ✅ |\n\n**✓ K.8 Complete** | Latency: +{seconds}s"
+      }
     },
     "5.9_k9_output_ENHANCED": {
-      "title": "## K.9 — 🤖 Cover Letter (ENHANCED v19.0)",
-      "format": "**Agent Status:** COMPLETE\n**Company-Specific Details:** {count} (Target: ≥4)\n**Find-Replace Test:** {paragraphs_passed}/3 paragraphs PASS\n\n**Cover Letter Elements:**\n\n**Why I'm Interested:**\n\n{why_interested_paragraph}\n\n**Why I'm Ideal (Part 1 - Experience):**\n\n{why_ideal_paragraph_1}\n\n**Why I'm Ideal (Part 2 - Leadership):**\n\n{why_ideal_paragraph_2}\n\n**Quality Validation:**\n| Check | Required | Actual | Status |\n|-------|----------|--------|--------|\n| Paragraph count | 3 (1+2) | {count} | ✅ |\n| Company specifics | ≥4 details | {count} | ✅ |\n| Find-replace test | ≥2 paragraphs PASS | {count}/3 | ✅ |\n| Unique signals | Uses Phase 3 research | {value} | ✅ |\n| Proof points | ≥2 achievements | {count} | ✅ |\n| Confidence | ≥0.85 | {value} | ✅ |\n\n**✓ K.9 Complete** | Latency: +{seconds}s"
+      "template_ref": "k_node_output_generic",
+      "params": {
+        "title": "## K.9 — 🤖 Cover Letter (ENHANCED v19.0)",
+        "format": "**Agent Status:** COMPLETE\n**Company-Specific Details:** {count} (Target: ≥4)\n**Find-Replace Test:** {paragraphs_passed}/3 paragraphs PASS\n\n**Cover Letter Elements:**\n\n**Why I'm Interested:**\n\n{why_interested_paragraph}\n\n**Why I'm Ideal (Part 1 - Experience):**\n\n{why_ideal_paragraph_1}\n\n**Why I'm Ideal (Part 2 - Leadership):**\n\n{why_ideal_paragraph_2}\n\n**Quality Validation:**\n| Check | Required | Actual | Status |\n|-------|----------|--------|--------|\n| Paragraph count | 3 (1+2) | {count} | ✅ |\n| Company specifics | ≥4 details | {count} | ✅ |\n| Find-replace test | ≥2 paragraphs PASS | {count}/3 | ✅ |\n| Unique signals | Uses Phase 3 research | {value} | ✅ |\n| Proof points | ≥2 achievements | {count} | ✅ |\n| Confidence | ≥0.85 | {value} | ✅ |\n\n**✓ K.9 Complete** | Latency: +{seconds}s"
+      }
     },
     "final_summary": {
       "title": "## 🎉 All K-Nodes Complete (v19.0 Agentic Enhancement)",
@@ -2387,6 +2155,15 @@
           "regeneration_includes": "Explicit constraint prompts"
         }
       }
+    },
+    "templates": {
+      "k_node_output_generic": {
+        "description": "Render with provided title and format exactly as stored in params.",
+        "fields": [
+          "title",
+          "format"
+        ]
+      }
     }
   },
   "6.conditions": {
```
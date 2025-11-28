# JW v19.3 → v19.4 Diff

```diff
--- v19.3
+++ v19.4
@@ -4,7 +4,7 @@
   "metadata": {
     "last_saved": "2025-10-02",
     "last_saved_note": "Date only - no timestamp",
-    "version": "v19.3",
+    "version": "v19.4",
     "sources": "JW v18.9 + JW Enhancements Tier 1-2 implementation",
     "notes": "Agentic enhancement version: K.2.5 competitive positioning NEW, K.8 intelligent gap-filling UPGRADED, K.9 specificity-driven research UPGRADED",
     "sha256": "pending_calculation",
@@ -58,7 +58,8 @@
     },
     "change_log": [
       "v19.2 (non-destructive): added centralized governance blocks & refs; behavior unchanged",
-      "v19.3: size-reduced by replacing inline node configs with references (backed up under *_legacy); behavior preserved via compat materialization"
+      "v19.3: size-reduced by replacing inline node configs with references (backed up under *_legacy); behavior preserved via compat materialization",
+      "v19.4: Added ASCII hygiene, product insertion prevention, K.5 name-dropping guard, date standardization, App Schema filtering. Additive only."
     ]
   },
   "instructions": [
@@ -119,6 +120,34 @@
         "rag_min_retrievers": 0,
         "agentic_mode": "OFF",
         "agentic_max_hops": 0
+      },
+      "date_format_standard": {
+        "format": "MM-DD-YYYY",
+        "regex_validation": "^(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])-(19|20)\\d{2}$",
+        "apply_to": [
+          "Application Date",
+          "Interview Date fields",
+          "Communication Date fields",
+          "Follow-Up Date fields"
+        ]
+      },
+      "app_schema_v4_field_rules": {
+        "never_populate": [
+          "Base Resume",
+          "Outreach Channel"
+        ],
+        "always_populate": [
+          "Company",
+          "Category",
+          "Sub-Category",
+          "Job Title",
+          "Primary Job Role",
+          "JD URL",
+          "Application Date",
+          "Pipeline Status",
+          "Versioned Resume"
+        ],
+        "conditionally_populate": "All other fields only if data available"
       }
     },
     "qa_row_templates": {
@@ -754,10 +783,13 @@
       "name": "Company Name & Job Title Extraction",
       "scope": "Extract structured data from JD via RAG web_fetch",
       "output_fields": [
+        "job_title",
+        "job_req_number",
+        "target_company_services",
+        "job_url",
+        "target_company_products",
         "company_name",
-        "job_title",
-        "job_url",
-        "job_req_number"
+        "target_company_platforms"
       ],
       "reasoning_config": {
         "cot_mode": "greedy",
@@ -801,7 +833,23 @@
           "status": "PASS/FAIL"
         }
       ],
-      "lock_status": "✅ K.1 Status: LOCKED | Ready for K.2 ingestion"
+      "lock_status": "✅ K.1 Status: LOCKED | Ready for K.2 ingestion",
+      "extraction_functions": {
+        "extract_target_company_products": {
+          "pseudo_code": [
+            "FUNCTION extract_target_company_products(job_description, company_name):",
+            "  products = []",
+            "  product_patterns = [",
+            "    r'\\b([A-Z][a-zA-Z]+\\s){0,2}(Cloud|Platform|Service|Hub|Suite|Engine)\\b',",
+            "    r'\\b' + company_name + r'\\s+([A-Z][a-zA-Z]+)\\b'",
+            "  ]",
+            "  FOR pattern IN product_patterns:",
+            "    products.extend(regex_findall(pattern, job_description))",
+            "  products.append(company_name)",
+            "  RETURN unique(products)"
+          ]
+        }
+      }
     },
     "K.2_industry_classification": {
       "node_id": "K.2",
@@ -1155,7 +1203,94 @@
       "content_focus": {
         "primary": "Strategic identity narrative - WHO the candidate is professionally",
         "secondary": "Differentiated value proposition for target role",
-        "forbidden": "Bullet summary format, tactical execution details, generic platitudes"
+        "forbidden": [
+          "B",
+          "u",
+          "l",
+          "l",
+          "e",
+          "t",
+          " ",
+          "s",
+          "u",
+          "m",
+          "m",
+          "a",
+          "r",
+          "y",
+          " ",
+          "f",
+          "o",
+          "r",
+          "m",
+          "a",
+          "t",
+          ",",
+          " ",
+          "t",
+          "a",
+          "c",
+          "t",
+          "i",
+          "c",
+          "a",
+          "l",
+          " ",
+          "e",
+          "x",
+          "e",
+          "c",
+          "u",
+          "t",
+          "i",
+          "o",
+          "n",
+          " ",
+          "d",
+          "e",
+          "t",
+          "a",
+          "i",
+          "l",
+          "s",
+          ",",
+          " ",
+          "g",
+          "e",
+          "n",
+          "e",
+          "r",
+          "i",
+          "c",
+          " ",
+          "p",
+          "l",
+          "a",
+          "t",
+          "i",
+          "t",
+          "u",
+          "d",
+          "e",
+          "s",
+          "Company name-dropping patterns: 'At [COMPANY]', 'while at [COMPANY]', '[COMPANY] experience'"
+        ],
+        "narrative_style": {
+          "approach": "capability_focused_narrative",
+          "voice": "I have [CAPABILITY]... while [CAPABILITY-ING]...",
+          "forbidden_patterns": [
+            "At [COMPANY], I [VERB]",
+            "while at [COMPANY], I [VERB]",
+            "During my time at [COMPANY]",
+            "[COMPANY] experience"
+          ],
+          "allowed_patterns": [
+            "I have [VERB-ed] [OUTCOME]",
+            "My expertise includes [CAPABILITY]",
+            "I [VERB] [OUTCOME] by [METHOD]",
+            "Having [VERB-ed] [CONTEXT]"
+          ]
+        }
       },
       "qa_rows": [
         {
@@ -1207,6 +1342,13 @@
           "check": "Confidence",
           "threshold": "≥0.90",
           "status": "PASS/FAIL"
+        },
+        {
+          "check": "No company name-dropping",
+          "threshold": "Zero previous employer names",
+          "status": "PASS/FAIL",
+          "validation": "validate_no_company_namedropping()",
+          "block_on_fail": true
         }
       ],
       "lock_status": "✅ K.5 Status: LOCKED | Ready for K.6 ingestion",
@@ -1270,7 +1412,32 @@
         "format": "Strong verb + Technology/Method + Quantified outcome",
         "word_count": "15-25 words per bullet",
         "verb_variety": "No verb used more than 2x across 7 bullets (AI detection defense)",
-        "keyword_density": "Bullets 1-2 should contain 3-4 JD keywords each"
+        "keyword_density": "Bullets 1-2 should contain 3-4 JD keywords each",
+        "forbidden_customization_patterns": {
+          "never_use": [
+            "deliver [TARGET_COMPANY] implementations",
+            "implement [TARGET_COMPANY_PRODUCT]",
+            "deploy [TARGET_COMPANY_PRODUCT]",
+            "using [TARGET_COMPANY_PRODUCT]",
+            "[TARGET_COMPANY]'s [PRODUCT]",
+            "establish [TARGET_COMPANY] as foundation"
+          ],
+          "always_use_instead": [
+            "deliver cloud data platform implementations",
+            "implement advanced analytics solutions",
+            "deploy enterprise data infrastructure",
+            "using cloud-native architectures",
+            "enterprise-grade data platforms",
+            "establish scalable data foundation"
+          ],
+          "generic_term_mapping": {
+            "Snowflake Data Cloud": "cloud data platform",
+            "Snowpark": "cloud-native compute environment",
+            "Databricks": "unified analytics platform",
+            "BigQuery": "cloud data warehouse",
+            "Redshift": "cloud data warehouse"
+          }
+        }
       },
       "lock_status": "✅ K.6 Status: LOCKED | Ready for K.7 ingestion",
       "message_policy_ref": "K.6",
@@ -1337,6 +1504,29 @@
           "check": "ASCII hygiene",
           "threshold": "Clean",
           "status": "PASS/FAIL"
+        }
+      ],
+      "qa_rows": [
+        {
+          "check": "No target company name",
+          "threshold": "Zero occurrences in intro+bullets",
+          "status": "PASS/FAIL",
+          "validation": "validate_no_target_products_in_past_roles()",
+          "block_on_fail": true
+        },
+        {
+          "check": "No target company products",
+          "threshold": "Zero product names from JD",
+          "status": "PASS/FAIL",
+          "validation": "validate_no_target_products_in_past_roles()",
+          "block_on_fail": true
+        },
+        {
+          "check": "Generic technology terms used",
+          "threshold": "Category-level terminology only",
+          "status": "PASS/FAIL",
+          "validation": "check_for_generic_terms(['cloud data platform','advanced analytics','data infrastructure','AI/ML platforms'])",
+          "block_on_fail": true
         }
       ]
     },
@@ -1473,6 +1663,29 @@
           "check": "ASCII hygiene",
           "threshold": "Clean",
           "status": "PASS/FAIL"
+        }
+      ],
+      "qa_rows": [
+        {
+          "check": "No target company name",
+          "threshold": "Zero occurrences in intro+bullets",
+          "status": "PASS/FAIL",
+          "validation": "validate_no_target_products_in_past_roles()",
+          "block_on_fail": true
+        },
+        {
+          "check": "No target company products",
+          "threshold": "Zero product names from JD",
+          "status": "PASS/FAIL",
+          "validation": "validate_no_target_products_in_past_roles()",
+          "block_on_fail": true
+        },
+        {
+          "check": "Generic technology terms used",
+          "threshold": "Category-level terminology only",
+          "status": "PASS/FAIL",
+          "validation": "check_for_generic_terms(['cloud data platform','advanced analytics','data infrastructure'])",
+          "block_on_fail": true
         }
       ]
     },
@@ -1692,6 +1905,13 @@
           "check": "Overall score",
           "threshold": "≥0.88",
           "status": "PASS/FAIL"
+        },
+        {
+          "check": "No target company products in competencies",
+          "threshold": "Generic platform terms only",
+          "status": "PASS/FAIL",
+          "validation": "validate_no_target_products_in_past_roles()",
+          "block_on_fail": true
         }
       ],
       "performance_impact": {
@@ -1970,6 +2190,50 @@
           "note": "Intro should not repeat headline phrasing"
         }
       }
+    },
+    "validation_functions": {
+      "validate_no_target_products_in_past_roles": {
+        "execution_point": "After bullet generation, before QA validation",
+        "apply_to": [
+          "K.6 intro_sentence",
+          "K.6 bullets",
+          "K.7 intro_sentence",
+          "K.7 bullets"
+        ],
+        "on_fail": {
+          "action": "REGENERATE",
+          "max_retries": 3,
+          "regeneration_instruction": "Replace [TARGET_COMPANY]/[TARGET_PRODUCTS] with generic tech terms: 'cloud data platform','advanced analytics','enterprise data infrastructure','AI/ML platforms'",
+          "if_retries_exhausted": "Block K-node completion and notify with violations"
+        },
+        "pseudo_code": [
+          "FUNCTION validate_no_target_products_in_past_roles(text, base_resume_company, target_company, target_products):",
+          "  IF base_resume_company == target_company: RETURN {'status':'PASS'}",
+          "  violations = []",
+          "  if target_company.lower() in text.lower(): violations.append({'type':'company_name','text':target_company})",
+          "  for p in target_products:",
+          "    if p.lower() in text.lower(): violations.append({'type':'product','text':p})",
+          "  if (target_company+\"'s\").lower() in text.lower(): violations.append({'type':'possessive','text':target_company+\"'s\"})",
+          "  RETURN {'status':'FAIL','violations':violations} if violations else {'status':'PASS'}"
+        ]
+      },
+      "validate_no_company_namedropping": {
+        "execution_point": "After K.5 generation, before QA validation",
+        "on_fail": {
+          "action": "REGENERATE",
+          "max_retries": 3,
+          "regeneration_instruction": "Rewrite in capability-focused style; remove previous employer names; focus on what was accomplished, not where."
+        },
+        "pseudo_code": [
+          "FUNCTION validate_no_company_namedropping(summary, previous_employers):",
+          "  patterns = [r'\\bAt\\s+([A-Z][a-zA-Z]+)', r'while at\\s+([A-Z][a-zA-Z]+)', r'During my time at\\s+([A-Z][a-zA-Z]+)', r'([A-Z][a-zA-Z]+)\\s+experience']",
+          "  viols = []",
+          "  for pat in patterns:",
+          "    for m in regex_findall(pat, summary):",
+          "      if m in previous_employers: viols.append({'pattern':pat,'company':m})",
+          "  return {'status':'FAIL','violations':viols} if viols else {'status':'PASS'}"
+        ]
+      }
     }
   },
   "5.output": {
@@ -2027,6 +2291,102 @@
       "title": "## 🎉 All K-Nodes Complete (v19.0 Agentic Enhancement)",
       "content": "**Resume Customization Summary:**\n\n✅ K.1: Company & job extracted\n✅ K.2: Industry classified\n✅ K.2.5: 🤖 Competitive positioning analyzed ({peer_jds} peer JDs)\n✅ K.3: Role mapped\n✅ K.4: Headline created (8-13 words, strategic + competitive)\n✅ K.5: Executive summary generated (100-120 tokens + competitive framing)\n✅ K.6: Recent experience (7 bullets, 2-3-2 provenance)\n✅ K.7: Prior experience (7 bullets, global scope)\n✅ K.8: 🤖 Competencies (6 items, {gap_percent}% gap coverage, authentic phrasing)\n✅ K.9: 🤖 Cover letter ({specifics_count} company-specific details)\n\n**v19.0 Agentic Enhancements:**\n- K.2.5: +{k2.5_seconds}s | {peer_jd_count} peer JDs analyzed\n- K.8: +{k8_seconds}s | {linkedin_searches} LinkedIn + {framework_searches} framework searches\n- K.9: +{k9_seconds}s | {company_searches} company-specific searches\n- Total added latency: ~{total_seconds}s\n- Quality improvements: 85%+ gap coverage, 90%+ recruiter engagement\n\n**Next Steps:**\n1. Copy outputs above into your resume template\n2. Format professionally (fonts, spacing)\n3. Export as PDF with metadata\n4. Run final spell check\n5. Submit with confidence!",
       "delivery_note": "All outputs are copy-paste ready in plain text format"
+    },
+    "pre_delivery_validation": {
+      "ascii_hygiene_check": {
+        "execution_order": 1,
+        "validation_function": {
+          "name": "enforce_ascii_hygiene",
+          "pseudo_code": [
+            "FUNCTION enforce_ascii_hygiene(text):",
+            "  forbidden_chars = {'—': '-', '–': '-', '“': '\"', '”': '\"', '’': \"'\", '‘': \"'\", '…': '...'}",
+            "  cleaned_text = text",
+            "  FOR char, replacement IN forbidden_chars:",
+            "    cleaned_text = cleaned_text.replace(char, replacement)",
+            "  FOR ch IN cleaned_text:",
+            "    IF ord(ch) > 127:",
+            "      RAISE ValidationError('Non-ASCII character found')",
+            "  RETURN cleaned_text"
+          ],
+          "apply_to": [
+            "K.4 headline",
+            "K.5 executive_summary",
+            "K.6 intro and bullets",
+            "K.7 intro and bullets",
+            "K.8 competencies",
+            "K.9 cover letter paragraphs"
+          ],
+          "on_fail": "Block Section 5; auto-correct then verify"
+        }
+      }
+    },
+    "formatters": {
+      "format_all_dates": {
+        "execution_point": "Before final JSON output",
+        "pseudo_code": [
+          "FUNCTION format_all_dates(json_data):",
+          "  # convert YYYY-MM-DD to MM-DD-YYYY if detected",
+          "  for k,v in list(json_data.items()):",
+          "    if isinstance(v,str) and re_match(r'^\\d{4}-\\d{2}-\\d{2}$', v):",
+          "      y,m,d = v.split('-'); json_data[k] = f'{m}-{d}-{y}'",
+          "  return json_data"
+        ]
+      },
+      "filter_empty_fields": {
+        "execution_point": "Final step before JSON output",
+        "pseudo_code": [
+          "FUNCTION filter_empty_fields(app_schema_data):",
+          "  for f in ['Base Resume','Outreach Channel']:",
+          "    if f in app_schema_data: del app_schema_data[f]",
+          "  return {k:v for k,v in app_schema_data.items() if v not in (None,'')}"
+        ],
+        "example": {
+          "input": {
+            "Company": "Snowflake",
+            "Application Date": "10-02-2025",
+            "Base Resume": "",
+            "Hiring Recruiter": "",
+            "Outreach Channel": ""
+          },
+          "output": {
+            "Company": "Snowflake",
+            "Application Date": "10-02-2025"
+          }
+        }
+      }
+    },
+    "release_pipeline": {
+      "execution_order": [
+        "1. K.1: Extract target company products",
+        "2. K.2-K.4: Standard generation",
+        "3. K.5: Generate with company name-dropping validation",
+        "4. K.6: Generate with target product validation",
+        "5. K.7: Generate with target product validation",
+        "6. K.8: Generate with target product validation",
+        "7. K.9: Standard generation",
+        "8. ASCII hygiene check on ALL outputs",
+        "9. Filter JSON to populated fields only",
+        "10. Format all dates to MM-DD-YYYY",
+        "11. Deliver Section 5 output"
+      ],
+      "enforcement_summary": {
+        "blocking_validations": [
+          "ASCII hygiene (auto-correct then verify)",
+          "Target company product insertion in K.6/K.7/K.8",
+          "Company name-dropping in K.5",
+          "QA row failures for above checks"
+        ],
+        "auto_corrections": [
+          "ASCII character replacement",
+          "Date format conversion",
+          "JSON field filtering"
+        ],
+        "retry_logic": {
+          "max_retries_per_validation": 3,
+          "on_exhaustion": "Block K-node; notify user",
+          "regeneration_includes": "Explicit constraint prompts"
+        }
+      }
     }
   },
   "6.conditions": {
@@ -2159,7 +2519,8 @@
       "provenance_enforcement": "2-3-2 split strictly required for K.6 and K.7",
       "agentic_timeout_limit": "120 seconds per agent (K.2.5, K.8, K.9)",
       "gap_coverage_minimum": "85% target for K.8 (WARNING if 70-84%, CRITICAL if <70%)",
-      "specificity_minimum": "4 company-specific details for K.9 (WARNING if 2-3, CRITICAL if <2)"
+      "specificity_minimum": "4 company-specific details for K.9 (WARNING if 2-3, CRITICAL if <2)",
+      "ascii_hygiene_mandatory": "ASCII-only (0-127) required before Section 5; auto-correct then verify."
     },
     "success_criteria": {
       "all_k_nodes_pass": "Every K.1-K.9 QA table shows all ✅",
```
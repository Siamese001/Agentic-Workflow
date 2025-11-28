# LinkedIn Outreach Orchestrator (LIC) Technical Appendix

## Overview

This technical appendix provides deep implementation details extracted from the LIC v5.4 configuration, including exact parameter values, validation rules, transition logic, and persona mappings that drive the AI-powered outreach system.

## 1. Complete Parameter Tables (Extracted from v5.4)

### 1.1 Message Type Specific Parameters

#### C_LEVEL Executive Parameters
```json
{
  "temperature": {
    "K.1": 0.10,
    "K.2": 0.60, 
    "K.3": 0.90,
    "K.4": 0.15,
    "K.5": 0.25
  },
  "tot_branches": {
    "K.1": 7,
    "K.2": 9,
    "K.3": "12-15",
    "K.4": 5,
    "K.5": 6
  },
  "self_consistency": {
    "K.1": 8,
    "K.2": 8,
    "K.3": 12,
    "K.4": 3,
    "K.5": 7
  },
  "rag_retrievers": {
    "K.1": 6,
    "K.2": 3,
    "K.3": 20,
    "K.4": "OFF",
    "K.5": "OFF"
  }
}
```

#### EXECUTIVE Parameters
```json
{
  "temperature": {
    "K.1": 0.10,
    "K.2": 0.50,
    "K.3": 0.70,
    "K.4": 0.15,
    "K.5": 0.22
  },
  "tot_branches": {
    "K.1": 5,
    "K.2": 6,
    "K.3": "10-11",
    "K.4": 4,
    "K.5": 5
  },
  "self_consistency": {
    "K.1": 5,
    "K.2": 5,
    "K.3": 7,
    "K.4": 3,
    "K.5": 5
  },
  "rag_retrievers": {
    "K.1": 4,
    "K.2": 2,
    "K.3": 12,
    "K.4": "OFF",
    "K.5": "OFF"
  }
}
```

### 1.2 Sampling Parameter Ranges (v5.3+)
```json
{
  "temperature": {
    "range": "0.0-2.0",
    "description": "higher = more creative, lower = more focused"
  },
  "top_p": {
    "range": "0.0-1.0",
    "description": "nucleus sampling threshold"
  },
  "top_k": {
    "range": "1-100",
    "description": "candidate token limit"
  },
  "min_p": {
    "range": "0.0-1.0",
    "default": 0.05,
    "description": "minimum probability threshold"
  },
  "repetition_penalty": {
    "range": "1.0-2.0",
    "default": 1.08,
    "description": "higher = less repetition"
  }
}
```

### 1.3 Structure Parameters by Message Type
```json
{
  "C_LEVEL": {
    "word_count": "100-150",
    "insights_count": 3,
    "intro_style": "strategic_observations",
    "cta_style": "executive_brief",
    "bridge_phrase": "Given your role..."
  },
  "EXECUTIVE": {
    "word_count": "140-200", 
    "insights_count": 2,
    "intro_style": "role_alignment",
    "cta_style": "lifecycle_aligned",
    "bridge_phrase": "In my current role..."
  },
  "SENIOR_TA": {
    "word_count": "140-200",
    "insights_count": 2,
    "intro_style": "lessons_framework",
    "cta_style": "business_value",
    "bridge_phrase": "From my experience..."
  },
  "RECRUITER": {
    "word_count": "40-120",
    "insights_count": 1,
    "intro_style": "candidate_focus",
    "cta_style": "application_process",
    "bridge_phrase": "Regarding the position..."
  },
  "SHORT_NEW": {
    "char_count": "280-330",
    "format": "compressed",
    "insights_count": 1,
    "intro_style": "connection_request",
    "cta_style": "micro",
    "bridge_phrase": "I'd like to connect..."
  }
}
```

## 2. Validation Rules Configuration

### 2.1 Reasoning Configuration Validation (v5.1+)

#### Severity Classifications
```json
{
  "blocking_severity": ["CRITICAL"],
  "warning_severity": ["WARNING"], 
  "info_severity": ["INFO"],
  "validation_execution": {
    "when": "After Section 3 completion, before K.1 execution",
    "execution_order": [
      "Load Section 3 defaults (runtime_toggles)",
      "Load Section 4 per-node overrides",
      "Load Section 3 complete_parameter_tables",
      "Merge defaults + overrides + parameters for each K-node",
      "Run validation rules against effective configuration",
      "Aggregate violations by severity",
      "Display validation report"
    ]
  }
}
```

#### Critical Validation Rules
```json
{
  "rule_001": {
    "id": "TEMP_RANGE_VALIDATION",
    "severity": "CRITICAL",
    "condition": "temperature < 0.0 OR temperature > 2.0",
    "message": "Temperature out of valid range",
    "fix": "Set temperature between 0.0-2.0"
  },
  "rule_002": {
    "id": "TOT_BRANCHES_VALIDATION", 
    "severity": "CRITICAL",
    "condition": "tot_branches < 3 OR tot_branches > 15",
    "message": "ToT branches outside operational range",
    "fix": "Set tot_branches between 3-15"
  },
  "rule_003": {
    "id": "RAG_RETRIEVER_VALIDATION",
    "severity": "WARNING", 
    "condition": "rag_retrievers < 3 AND rag_mode = ON",
    "message": "Insufficient RAG retrievers for quality",
    "fix": "Increase rag_retrievers to 3+ or disable RAG"
  }
}
```

### 2.2 Parameter Modification Validation
```json
{
  "validation_on_modify": {
    "rules": [
      "Check against Section 4 validation rules",
      "Validate against Section 3 parameter tables",
      "Ensure parameter compatibility",
      "Maintain message type consistency"
    ],
    "audit_trail": "Log all modifications with timestamp and user_override flag"
  }
}
```

## 3. Message Type Transition Logic

### 3.1 Transition Detection Rules
```json
{
  "detection_rules": [
    {
      "condition": "prior_message_type='connection_request' AND current_route='FOLLOW_UP'",
      "action": "Flag K.3-K.4 for expansion",
      "from": "SHORT_NEW (280 chars)",
      "to": "Determined by K.1 routing"
    },
    {
      "condition": "prior_message_content.length < 330 AND current allows full message",
      "action": "Flag K.3-K.4 for regeneration", 
      "rationale": "Compressed format needs expansion"
    }
  ],
  "regeneration_flags": {
    "regenerate_k3": false,
    "regenerate_k4": false,
    "k3_target_format": null,
    "k4_attachment_type": null
  }
}
```

### 3.2 Supported Transitions with Parameter Changes
```json
{
  "SHORT_NEW_to_SENIOR_TA": {
    "trigger": "Follow-up after connection request accepted",
    "K.3_change": "300-330 chars → 140-200 words with lessons framework",
    "K.4_change": "No attachment → Resume attachment required",
    "parameter_updates": {
      "temperature": "0.10 → 0.70",
      "tot_branches": "3 → 8-10",
      "rag_retrievers": "OFF → 15"
    }
  },
  "SHORT_NEW_to_EXECUTIVE": {
    "trigger": "Escalation to executive messaging",
    "K.3_change": "300-330 chars → 140-200 words with strategic insights", 
    "K.4_change": "No attachment → Resume attachment",
    "parameter_updates": {
      "temperature": "0.10 → 0.70",
      "tot_branches": "3 → 6-8",
      "rag_retrievers": "OFF → 12"
    }
  },
  "CONNECTION_REQ_to_FOLLOW_UP": {
    "trigger": "Connection accepted, full messaging enabled",
    "K.3_change": "300-330 chars → 200-300 words with 3 strategic observations",
    "K.4_change": "Blocked → Attachments allowed",
    "parameter_updates": {
      "temperature": "0.10 → 0.90",
      "tot_branches": "OFF → 12-15",
      "rag_retrievers": "OFF → 20"
    }
  }
}
```

## 4. TA Executive Detection Logic (v5.2+)

### 4.1 Trigger Conditions
```json
{
  "trigger": {
    "recipient_title_contains": [
      "recruitment", "recruiter", "talent acquisition", 
      "people", "HR", "human resources", "CHRO", "CPO"
    ],
    "AND_seniority_level": [
      "VP", "SVP", "Global VP", "Chief", "Head of", 
      "Director", "Senior Director"
    ]
  }
}
```

### 4.2 Special Handling Rules
```json
{
  "special_handling": {
    "achievement_focus": "COMPANY_BUSINESS_ONLY",
    "forbidden_topics": [
      "Recruiting operations",
      "Hiring efficiency", 
      "Talent pipeline management",
      "TA technology/tools"
    ],
    "required_topics": [
      "Revenue/ARR/RPO growth",
      "Product adoption/expansion",
      "Partnership ecosystem",
      "Customer success metrics",
      "Platform/technology objectives"
    ],
    "cta_pattern": "Your perspective on connecting with leaders in {business_function} would be invaluable",
    "cta_avoid": "Your perspective as {TA_title}",
    "positioning": "Business value contributor seeking introductions to decision-makers"
  }
}
```

### 4.3 Parameter Overrides for TA Executives
```json
{
  "TA_EXECUTIVE_overrides": {
    "temperature": {
      "K.3": "reduce by 0.2 for business focus",
      "K.5": "reduce by 0.1 for direct CTA"
    },
    "rag_retrievers": {
      "K.3": "increase to 25 for company research",
      "K.1": "focus on business signals only"
    },
    "structure": {
      "insights_count": "increase by 1 for business value",
      "forbidden_keywords": ["hiring", "recruiting", "talent"],
      "required_keywords": ["revenue", "growth", "business", "strategy"]
    }
  }
}
```

## 5. K-Node Persona Mapping System

### 5.1 General Analyst (CoT Spine)
```json
{
  "general_analyst": {
    "icon": "👤",
    "name": "General Analyst",
    "role": "CoT spine reasoning",
    "slides": ["1", "2", "3", "7"],
    "responsibilities": [
      "Feature extraction",
      "Semantic binding", 
      "Task compression",
      "Final output generation"
    ],
    "attention_heads": "All layers"
  }
}
```

### 5.2 Specialist Analysts by K-Node
```json
{
  "K.1_Message_Type_Routing": {
    "branch_a": {
      "icon": "💎",
      "name": "C-Suite Analyst",
      "attention_heads": "0-3"
    },
    "branch_b": {
      "icon": "💼", 
      "name": "Executive Analyst",
      "attention_heads": "4-7"
    },
    "branch_c": {
      "icon": "🎯",
      "name": "TA Specialist Analyst", 
      "attention_heads": "8-11"
    }
  },
  "K.2_Subject_Line": {
    "branch_a": {
      "icon": "🎯",
      "name": "Role-First Analyst"
    },
    "branch_b": {
      "icon": "🏢",
      "name": "Company-First Analyst"
    },
    "branch_c": {
      "icon": "💡",
      "name": "Value-Prop Analyst"
    }
  },
  "K.3_Message_Body": {
    "branch_a": {
      "icon": "💎",
      "name": "Role Alignment Analyst"
    },
    "branch_b": {
      "icon": "🏢", 
      "name": "Company Culture Analyst"
    },
    "branch_c": {
      "icon": "📈",
      "name": "Market Position Analyst"
    },
    "branch_d": {
      "icon": "🤝",
      "name": "Peer Comparison Analyst"
    }
  }
}
```

### 5.3 Integration and Review Specialists
```json
{
  "integration_analyst": {
    "icon": "🔀",
    "name": "Integration Analyst",
    "role": "Branch merge and consensus",
    "slides": ["5"],
    "responsibilities": [
      "Weighted merge",
      "Confidence restoration"
    ]
  },
  "reflexion_reviewers": {
    "specialist_reviewer": {
      "icon": "👩‍💼",
      "name": "Specialist Reviewer",
      "role": "Domain expert review",
      "round": 1
    },
    "ga_reviewer": {
      "icon": "🧑‍💼",
      "name": "GA Reviewer", 
      "role": "Common-sense review",
      "round": 2
    }
  }
}
```

## 6. RAG Configuration and Multi-Hop Logic

### 6.1 RAG Pre-Processing Visualization (v5.4)
```ascii
                🔎 RAG PRE-PROCESSING (v16/v17)
                ┌─────────────────────────────────┐
                │ Hop 1: {hop1_query}            │
                │ Sources: {hop1_sources}         │
                │ Signal Quality: {hop1_quality}  │
                ├─────────────────────────────────┤
                │ Hop 2: {hop2_query}            │
                │ Sources: {hop2_sources}         │
                │ Signal Quality: {hop2_quality}  │
                ├─────────────────────────────────┤
                │ [Hop 3 if applicable]          │
                ├─────────────────────────────────┤
                │ Synthesized Context:           │
                │ {context_summary}               │
                │ Confidence: {rag_confidence}   │
                └─────────────┬───────────────────┘
                              │
                              ↓
                    🔥 INPUT: [RAG-augmented context + user query]
```

### 6.2 RAG Parameters by Message Type and K-Node
```json
{
  "rag_configuration": {
    "C_LEVEL": {
      "K.1": {"retrievers": 6, "hops": 3, "mode": "ENHANCED"},
      "K.2": {"retrievers": 3, "hops": 2, "mode": "CONDITIONAL"},
      "K.3": {"retrievers": 20, "hops": 4, "mode": "DEEP_RESEARCH"},
      "K.4": {"mode": "OFF"},
      "K.5": {"mode": "OFF"}
    },
    "EXECUTIVE": {
      "K.1": {"retrievers": 4, "hops": 2, "mode": "ENHANCED"},
      "K.2": {"retrievers": 2, "hops": 2, "mode": "CONDITIONAL"},
      "K.3": {"retrievers": 12, "hops": 4, "mode": "DEEP_RESEARCH"},
      "K.4": {"mode": "OFF"},
      "K.5": {"mode": "OFF"}
    },
    "SENIOR_TA": {
      "K.1": {"retrievers": 4, "hops": 2, "mode": "ENHANCED"},
      "K.2": {"retrievers": 2, "hops": 2, "mode": "CONDITIONAL"},
      "K.3": {"retrievers": 15, "hops": 3, "mode": "LESSONS_FRAMEWORK"},
      "K.4": {"mode": "RESUME_FOCUSED"},
      "K.5": {"mode": "OFF"}
    }
  }
}
```

## 7. Transformer Layer Visualization Requirements

### 7.1 Layer Groupings and Purpose
```json
{
  "layers_1_3": {
    "name": "Surface Patterns → Information Bottleneck",
    "purpose": "Compress tokens to concepts to tasks",
    "show": ["token_count_reduction", "hidden_states", "compression_ratio"],
    "metrics": ["Features", "Confidence", "Coverage"]
  },
  "layers_4_6": {
    "name": "Semantic Understanding + Bottleneck",
    "purpose": "Bind concepts into relationships", 
    "show": ["concept_binding", "relationship_formation", "scoring_logits"]
  },
  "layers_7_8": {
    "name": "Task Comprehension + Final Compression",
    "purpose": "Maximum compression to action vector",
    "show": ["task_vector", "action_representation"]
  },
  "layer_9": {
    "name": "Ambiguity Detection + Hidden States",
    "purpose": "Detect when to branch from CoT to ToT",
    "show": ["hidden_state_values", "threshold_comparison", "probability_tree"]
  },
  "layer_10": {
    "name": "Multi-Path Reasoning (ToT Branches)",
    "purpose": "Parallel specialist processing",
    "show": ["branch_hidden_states", "specialist_reasoning", "confidence_per_branch"]
  },
  "layer_11": {
    "name": "Consensus + Confidence Emergence",
    "purpose": "Merge branches and resolve conflicts",
    "show": ["weighted_merge", "confidence_restoration", "reflexion_reviews"]
  },
  "layer_12": {
    "name": "Output Generation + Final Confidence",
    "purpose": "Generate final output with locked confidence",
    "show": ["output_logits", "softmax_probabilities", "final_lock"]
  }
}
```

### 7.2 Required Visualizations
```json
{
  "mandatory_visualizations": [
    "rag_preprocessing_block (v17, when RAG enabled)",
    "hidden_state_arrays",
    "logit_to_softmax_conversions", 
    "probability_distributions",
    "attention_head_assignments",
    "compression_ratios",
    "confidence_emergence_explanations"
  ],
  "hidden_state_format": {
    "example": "[0.82, 0.67, 0.91, 0.43, 0.78, 0.55, 0.88, 0.71]",
    "precision": 2,
    "emoji_mapping": "each value maps to feature emoji"
  }
}
```

## 8. Output Format Control (JW v18.8)

### 8.1 Simplified Output Structure (SHOW_DETAILED_REASONING=OFF)
```markdown
---

## **K.{X} – {NODE NAME}**

**🎯 Output:** {final_value}
**✅ Status:** PASS

**Quality Checks:**
| Check | Required | Actual | Status |
|-------|----------|--------|--------|
| {check_name} | {threshold} | {value} | ✅/❌ |

**▸ K.{X} complete. Type 'continue' for K.{X+1}**
```

### 8.2 Detailed Output Structure (SHOW_DETAILED_REASONING=ON)
```markdown
## **K.x – [NODE NAME]**

**Input Tokens:**
```
[token1][token2][token3]...
   ↓       ↓       ↓
[id1]   [id2]   [id3]...
```

## **🔎 AGENTIC RAG RETRIEVAL (v16/v17)**
[Multi-hop retrieval details]

## **🎯 HYBRID COT/TOT PATH (ASCII TREE WITH PERSONAS)**
[ASCII tree with RAG pre-processing block]

**Persona Summary:**
- 👤 **General Analyst (CoT):** Slides 1-3, 7
- [Specialist details...]

### **📄 Slide 1: [Task Name]**
**👤 GENERAL ANALYST (CoT Spine)**
**🧠 LAYERS 1-3 (SURFACE → BOTTLENECK)**
[Detailed layer analysis]

## **K.x OUTPUT**
🎯 **[Output field]:** [value]
✅ **Confidence:** [value]
🔗 **Status:** [PASS/FAIL]

**▸ K.x COMPLETE. Type "continue" for K.x+1.**
```

## 9. Skip Notification Templates

### 9.1 CONNECTION_REQ Route Skip Notifications
```markdown
---

## **⏭️ K.2 SKIPPED**

**Reason:** CONNECTION_REQ route constraint
**Route rule:** Section 3.routing_decision_tree.routes.CONNECTION_REQ.k_node_modifications.K.2 = "SKIP (no subject line in connection requests)"
**Impact:** Connection requests do not support subject lines. Message will consist of: greeting + K.3 compressed body + K.5 micro CTA.

---

**Proceeding to K.3 (Compressed Message Body)...**

**▸ Type "continue" for K.3**
```

### 9.2 Transition Regeneration Notification
```markdown
---

## **🔄 K.3 REGENERATING**

**Reason:** Message type transition detected
**Original Type:** SHORT_NEW (connection request)
**New Type:** SENIOR_TA (follow-up message)
**Impact:** K.3 expanding from ~280 chars to 40-120 words with fuller context

**Regeneration in progress...**

---
```

## 10. Parameter Locking and Audit Trail

### 10.1 Parameter Locking Mechanism
```json
{
  "parameter_locking": {
    "purpose": "Prevent parameter drift during execution",
    "scope": "Locked parameters apply to entire message generation session",
    "modification_after_lock": "Not allowed - user must regenerate with different parameters",
    "audit_trail": "All locked parameters logged to 5.output.audit.parameters/Parameters_Locked_{timestamp}_v2.json"
  }
}
```

### 10.2 Audit Trail Structure
```json
{
  "audit_log": {
    "parameters_locked": {
      "timestamp": "2025-01-XX_XX:XX:XX",
      "message_type": "EXECUTIVE",
      "route": "INMAIL_OUTREACH",
      "source_tracking": {
        "K.1_temperature": "Section 3.complete_parameter_tables.C_LEVEL.K.1",
        "K.3_tot_branches": "Section 4.runtime_overrides_by_k.K.3"
      },
      "user_modifications": [],
      "final_locked_values": {...}
    }
  }
}
```

## **5. OUTPUT GENERATION & FORMATTING**

### **Section 5 Execution Gate**
- **Purpose**: Emit final user-facing outputs only after all curated QA rows pass
- **Execution Gate**: Section 5 CANNOT begin until K.1-K.7 complete with PASS status
- **Render Gate**: 
  - emit_output_if: RUN_ALLOWED=true
  - fallback: emit 6.conditions with remediation steps

### **Message Assembly Execution Order**
1. validate_k_completions
2. apply_route_constraints
3. apply_message_type_template
4. apply_job_application_enrichment
5. merge_k_outputs
6. apply_final_formatting
7. validate_character_limits
8. generate_audit_package

### **Blocking Requirements**
- Route determination complete
- All K.x must have confidence >= target
- Message type must be confirmed (not pending)
- LinkedIn inputs must be validated
- QA grid must show PASS
- Character limits must be respected (if applicable)
- RAG quality checks passed (where applicable)
- Job application context integrated (if applicable)
- Message type transition handled (if detected)
- Clean Section 5 deliverable generated per JW v18.8

### **JW v18.8 Output Format Structure**
```
# **FINAL LINKEDIN MESSAGE ({MESSAGE_TYPE} FORMAT)**
**Subject:** {K.2_output}
**Message:**
```
{formatted_message_body}
```
**Quality Validation:**
{mini_qa_table}
**Tracking Fields (if sent):**
```json
{app_schema_v4_fields}
```
**Was this message sent to {recipient_name}? (Y/N):**
```

### **Job Application Enrichment (v17)**
- **Purpose**: Apply job application context to message assembly if is_job_application=Y
- **Execution Point**: After apply_message_type_template, before merge_k_outputs
- **Applies to**: K.3 message body

**Enrichment Logic:**
- If is_job_application=false: Skip enrichment, proceed with standard message assembly
- If is_job_application=true:
  - Prepend application context: "I recently applied for the {job_title} role (Req #{job_req_number})"
  - Frame recipient based on message_type:
    - C_LEVEL/EXECUTIVE: "Position aligns with strategic priorities you've outlined"
    - SENIOR_TA/RECRUITER: "Wanted to connect about the {job_title} opportunity"
  - Demonstrate role-specific value alignment using RAG-sourced insights
  - Position CTA as insights request: "Would value your perspective on..."
  - Maintain character limit compliance

**Character Budget Adjustment:**
- CONNECTION_REQ: Application reference must fit within 280-char K.3 budget
- INMAIL_OUTREACH: Application framing adds ~40-60 chars, ensure body stays within 2000 chars
- FOLLOW_UP: No hard limit, but maintain readability

### **Output Templates by Message Type**

#### **C_LEVEL Format**
- **Structure**: Subject + greeting + 3 strategic insights + 2 achievements with metrics + perspective request + CTA + signature
- **Word Count**: 200-300
- **Paragraphs**: 3-4
- **Formality**: executive
- **Personalization Anchors**: >= 3
- **RAG Requirement**: 20-retriever 6-hop RAG
- **CTA Template**: "Would you have {duration} {time_frame} to discuss connecting with {company_name}'s leaders in {business_function}?"
- **Duration**: 20-25 minutes
- **Time Frame**: next week
- **Word Limit**: 25

#### **EXECUTIVE Format**
- **Structure**: Subject + greeting + 2 strategic insights + achievement bridge + value alignment + CTA + signature
- **Word Count**: 140-200
- **Paragraphs**: 2-3
- **Formality**: professional
- **Personalization Anchors**: >= 2
- **RAG Requirement**: 12-retriever 4-hop RAG
- **CTA Template**: "Would you have {duration} {time_frame} to discuss connecting with {company_name}'s leaders in {business_function}?"
- **Duration**: 15-20 minutes
- **Time Frame**: next week
- **Word Limit**: 22

#### **SENIOR_TA Format**
- **Structure**: Subject + greeting + 2 lessons with metrics + connection to expertise + CTA + attachment note + signature
- **Word Count**: 140-200
- **Paragraphs**: 2-3
- **Formality**: conversational_professional
- **Must Mention Resume**: true
- **RAG Requirement**: 12-retriever 4-hop RAG
- **CTA Template**: "Would you have {duration} {time_frame} to discuss connecting with {company_name}'s leaders in {business_function}?"
- **Duration**: 15-20 minutes
- **Time Frame**: next week
- **Business Function**: partnerships and product strategy
- **Word Limit**: 22

#### **RECRUITER Format**
- **Structure**: Subject + greeting + 2 qualifications + role fit statement + CTA + attachment note + signature
- **Word Count**: 100-150
- **Paragraphs**: 2
- **Formality**: conversational
- **Must Mention ATS**: true
- **RAG Requirement**: 9-retriever 4-hop RAG
- **CTA Template**: "Available for a {duration} call {time_frame}?"
- **Duration**: quick 10-minute
- **Time Frame**: this week
- **Word Limit**: 15

#### **SHORT_NEW Format**
- **Structure**: Greeting + compressed body + micro CTA + brief signature
- **Character Count**: 250-330
- **Paragraphs**: 1-2
- **Formality**: brief_professional
- **No Attachments**: true
- **RAG Requirement**: OFF for CONNECTION_REQ
- **CTA Examples**: "Let's connect", "Happy to chat"
- **Word Limit**: 5

**SHORT_NEW Subtypes:**
- **CXO_TA**: 
  - Char Count: 280-300
  - Temperature: 0.85
  - Structure: More sophisticated opener
- **REC**: 
  - Char Count: 250-280
  - Temperature: 0.5
  - Structure: Direct qualification focus

#### **CONNECTION_REQ_COMPRESSED Format**
- **Note**: Used when route=CONNECTION_REQ
- **Structure**: Greeting + compressed body + micro CTA
- **Character Limit**: 330 hard limit
- **No Subject/Attachments/Signature**: true
- **Blocking on Exceed**: true
- **RAG Requirement**: RAG disabled (anti-pattern for space-constrained format)

### **Post-Send Confirmation (v17)**
- **Purpose**: Track message send status and update App Schema v4 contact tracking fields
- **Execution Point**: After final_artifact_generation display
- **Prompt Template**: "---\n\n## **📤 Message Send Confirmation**\n\n**Was this message sent to {recipient_name}? (Y/N):**"

**If Yes:**
- Output App Schema v4 tracking fields in JSON fenced block
```json
{
  "Recruiter / Contact 1 Name": "{recipient_name}",
  "Recruiter / Contact 1 Title": "{recipient_title}",
  "Recruiter / Contact 1 URL": "{recipient_profile_url}",
  "Date Communication Sent 1": "{date_1_MM_DD_YYYY}"
}
```

**If No:**
- Skip JSON output, log unsent status to audit trail
- Prompt for edit/save/discard/new options

### **Error Handling**

#### **Validation Failures**
- **Response**: Show specific K.x failures with recommendations
- **Recovery**: Allow targeted K.x regeneration without full restart

#### **Missing Inputs**
- **Response**: Return to Section 3 linkedin_input_collection
- **Recovery**: Preserve any completed K.x work

#### **Character Limit Exceeded**
- **Response**: Show current char count vs limit, identify offending sections
- **Recovery**: Offer to regenerate K.3 or K.5 in compressed mode

#### **Timeout**
- **Response**: Save state and allow resume
- **Recovery**: Restore from audit checkpoint

#### **RAG Retrieval Failure**
- **Response**: Log failure, proceed with non-RAG reasoning for affected K-node
- **Recovery**: Flag reduced personalization depth in QA results
- **User Notification**: Inform user that external research was unavailable

#### **RAG Quality Threshold Failure**
- **Response**: If signal_quality < 0.65, flag warning but proceed
- **Recovery**: Document low-quality signals in audit log
- **Blocking**: false

#### **Job Application Context Missing**
- **Response**: If is_job_application=Y but req_number or job_title missing, prompt for missing fields
- **Recovery**: Re-prompt job_application_context gate
- **Blocking**: false
- **Fallback**: If user declines to provide, set is_job_application=false and proceed

#### **Message Type Transition Error**
- **Response**: If K.3 regeneration fails during transition, revert to original format
- **Recovery**: Log transition failure, use original SHORT_NEW format with warning
- **User Notification**: "Transition to {target_type} format failed, using original format"

#### **Parameter Table Mismatch**
- **Response**: If Section 3 parameter tables don't align with message type, use defaults
- **Recovery**: Apply Section 4 runtime overrides as fallback
- **Audit**: Log parameter source conflict to audit trail

### **Performance Metrics**

#### **Tracked Metrics**
- Route determination time
- Time per K.x execution
- Total generation time
- Reasoning path depths
- Self-consistency convergence
- QA pass rate by message type
- QA pass rate by route
- User override frequency
- Character limit compliance rate
- RAG retrieval latency per hop
- RAG success rate by K-node
- Signal quality score distribution
- Retriever utilization efficiency
- Job application context collection rate
- Job application enrichment success rate
- Reasoning display preference distribution
- Message type transition success rate
- K.3 regeneration completion rate
- Parameter table usage frequency

#### **Benchmarks**
- **K1 RAG Latency Target**: < 2s for 3 hops
- **K2 RAG Latency Target**: < 1.5s for 2 hops
- **K3 RAG Latency Target**: < 3s for 3-6 hops depending on type
- **Signal Quality Target**: >= 0.7 aggregate
- **Job Context Collection Time Target**: < 30s
- **Reasoning Preference Prompt Time Target**: < 10s
- **Transition Detection Time Target**: < 1s
- **K3 Regeneration Time Target**: < 5s

#### **Message Type Specific Metrics**
- **C_LEVEL**: 8-12 minutes generation, 20 retrievers/6 hops, 35-45% response rate
- **EXECUTIVE**: 5-7 minutes generation, 12 retrievers/4 hops, 25-35% response rate
- **SENIOR_TA**: 4-6 minutes generation, 12 retrievers/4 hops, 30-40% response rate
- **RECRUITER**: 3-4 minutes generation, 9 retrievers/4 hops, 20-30% response rate
- **SHORT_NEW**: 1-2 minutes generation, None (CONNECTION_REQ), 15-25% response rate

## **6. CONDITIONS & EXECUTION GATES**

### **Purpose**
Define non-negotiable execution gates, error recovery policy, and audit requirements for outreach message generation

### **Execution Gates**

#### **Blocking Requirements**
- Route determined via Section 3 decision tree
- LinkedIn inputs (name, title, about, profile_url) validated
- Message type confirmed by user
- All executed K-nodes achieve minimum confidence thresholds
- Character limits respected for route (CONNECTION_REQ: 330, INMAIL: 2100)
- Aggregate QA score >= 0.90

#### **Non-Blocking Requirements**
- Job application context collected (if applicable)
- RAG signal quality >= 0.65 (proceed with warning if lower)
- Reasoning display preference captured

### **K-Node Confidence Thresholds**
- **K.1**: 0.95
- **K.2**: 0.9
- **K.3**: 0.88
- **K.4**: 0.95
- **K.5**: 0.95
- **K.6**: 0.99
- **K.7**: 0.97
- **Policy**: Block execution if any K-node falls below threshold

### **Error Recovery Policy**
- **Allow Targeted K-Node Retry**: true
- **Max Retry Attempts**: 3
- **Preserve Successful Nodes**: true
- **Character Limit Exceeded**: Offer K.3/K.5 regeneration in compressed mode
- **RAG Failure**: Proceed with non-RAG reasoning, flag in audit
- **Validation Failure**: Display specific failures, allow fixes before retry
- **Timeout**: Save state, allow resume from checkpoint

### **Override Policy**

#### **User Can Override**
- Warning level checks
- RAG quality thresholds

#### **User Cannot Override**
- Character limits
- Route requirements
- Critical validation rules

#### **Override Logging**
- All overrides logged with justification
- Maintain original results: true

### **Audit Requirements**

#### **Mandatory Logging**
- All K-node outputs and confidence scores
- Routing decision and rationale
- RAG retrieval attempts and quality scores
- User overrides with justifications
- Error events and recovery attempts
- Total generation time and per-K-node timing

#### **Retention & Format**
- **Retention Period**: 30 days
- **Format**: JSON with timestamps
- **Location**: 5.output.audit.*

### **Execution Order**

#### **Phase 1: Context**
- Execute Section 3 completely (routing, inputs, preferences)

#### **Phase 2: Reasoning**
- Validate configuration (Section 4.reasoning_configuration_validation)
- Review parameters if requested (Section 4.decoding_parameters_review)
- Execute K.1-K.7 sequentially with skip notifications as needed

#### **Phase 3: Output**
- Validate all QA checks (Section 5.qa_results_by_k)
- Apply job enrichment if applicable (Section 5.job_application_enrichment)
- Generate final artifact (Section 5.final_artifact_generation)
- Confirm send status (Section 5.post_send_confirmation)

### **Critical Validations**

#### **Routing**
- **Valid Routes**: FOLLOW_UP, BATCH_OUTREACH, CONNECTION_REQ, INMAIL_OUTREACH
- **Enforcement**: Refer to Section 3.routing_decision_tree for logic

#### **Parameter Compliance**
- **Source**: Section 3.complete_parameter_tables
- **Enforcement**: Refer to Section 4.reasoning_configuration_validation for checks

#### **Character Limits**
- **CONNECTION_REQ**: 330
- **INMAIL_OUTREACH**: 2100
- **Enforcement**: Hard block if exceeded

### **Final Release Gate**
- **Condition**: ALL(execution_gates.blocking_requirements) == PASS
- **On Pass**: Proceed to Section 5.final_artifact_generation
- **On Fail**: Block execution, display failures, offer recovery options

## **7. COMPLETE PARAMETER MATRIX**

### **Canonical Message Types Parameter Matrix**

#### **Headers**
K1, K2, K3, K4, K5, K6, K7

#### **C_LEVEL Parameters**
- **ToT Branches**: [7, 9, "12-15", 5, 6, 0, 0]
- **Self Consistency**: [8, 8, 12, 3, 7, 1, 10]
- **Temperature**: [0.1, 0.6, 0.9, 0.15, 0.25, 0.1, 0.05]
- **RAG Retrievers**: [6, 3, 20, 0, 0, 0, 0]
- **RAG Hops**: [3, 2, 6, 0, 0, 0, 0]
- **Word Count**: 200-300
- **Structure**: 3 strategic insights

#### **EXECUTIVE Parameters**
- **ToT Branches**: [5, 6, "10-11", 4, 5, 0, 0]
- **Self Consistency**: [5, 5, 7, 3, 5, 1, 6]
- **Temperature**: [0.1, 0.5, 0.7, 0.15, 0.22, 0.1, 0.05]
- **RAG Retrievers**: [4, 2, 12, 0, 0, 0, 0]
- **RAG Hops**: [2, 2, 4, 0, 0, 0, 0]
- **Word Count**: 140-200
- **Structure**: 2 strategic insights

#### **Parameter Matrix Accessor**
`canonical_message_types.parameter_matrix[{type}][{param}][{k_index}]`

### **K5 Call to Action Parameters by Message Type**

#### **C_LEVEL CTA**
- **Template**: "Would you have {duration} {time_frame} to discuss connecting with {company_name}'s leaders in {business_function}?"
- **Duration**: 20-25 minutes
- **Time Frame**: next week
- **Word Limit**: 25
- **Company Name Required**: true
- **Temporal Frame Required**: true

#### **EXECUTIVE CTA**
- **Template**: "Would you have {duration} {time_frame} to discuss connecting with {company_name}'s leaders in {business_function}?"
- **Duration**: 15-20 minutes
- **Time Frame**: next week
- **Word Limit**: 22
- **Company Name Required**: true
- **Temporal Frame Required**: true

#### **SENIOR_TA CTA**
- **Template**: "Would you have {duration} {time_frame} to discuss connecting with {company_name}'s leaders in {business_function}?"
- **Duration**: 15-20 minutes
- **Time Frame**: next week
- **Word Limit**: 22
- **Company Name Required**: true
- **Temporal Frame Required**: true
- **Business Function Examples**: partnerships and product strategy, platform strategy, go-to-market initiatives

#### **RECRUITER CTA**
- **Template**: "Available for a {duration} call {time_frame}?"
- **Duration**: quick 10-minute
- **Time Frame**: this week
- **Word Limit**: 15
- **Company Name Required**: false
- **Temporal Frame Required**: true

#### **SHORT_NEW CTA**
- **Template**: "{micro_cta}"
- **Examples**: Let's connect, Happy to chat
- **Word Limit**: 5
- **Company Name Required**: false
- **Temporal Frame Required**: false

## **8. GLOBAL ENFORCEMENT RULES**

### **Message Constraints by Type**

#### **C_LEVEL Constraints**
- **Word Range**: [200, 300]
- **Formality**: executive
- **Personalization Anchors Min**: 3
- **Paragraph Count**: [3, 4]
- **Insights Required**: 3
- **Achievements Required**: 3

#### **EXECUTIVE Constraints**
- **Word Range**: [140, 200]
- **Formality**: professional
- **Personalization Anchors Min**: 2
- **Paragraph Count**: [2, 3]
- **Insights Required**: 2
- **Achievements Required**: 2

#### **SENIOR_TA Constraints**
- **Word Range**: [140, 200]
- **Formality**: conversational_professional
- **Personalization Anchors Min**: 2
- **Paragraph Count**: [2, 3]
- **Lessons Required**: 2
- **Achievements Required**: 2
- **Must Mention Resume**: true

#### **RECRUITER Constraints**
- **Word Range**: [100, 150]
- **Formality**: conversational
- **Personalization Anchors Min**: 2
- **Paragraph Count**: [2, 2]
- **Qualifications Required**: 2
- **Achievements Required**: 2
- **Must Mention ATS**: true

#### **SHORT_NEW Constraints**
- **Char Range**: [250, 330]
- **Formality**: brief_professional
- **Personalization Anchors Min**: 1
- **Paragraph Count**: [1, 2]
- **Achievements Required**: 0

### **Message Constraints by Route**

#### **CONNECTION_REQ Route**
- **Hard Char Limit**: 330
- **Force Message Type**: SHORT_NEW
- **K-Nodes Disabled**: K.2, K.4, K.6
- **K3 Mode**: compressed
- **K5 Mode**: micro

#### **INMAIL_OUTREACH Route**
- **Hard Char Limit**: 2100
- **Subject Limit**: 60

#### **FOLLOW_UP Route**
- **Reference Prior**: true
- **Transition Detection**: true

#### **BATCH_OUTREACH Route**
- **Multi Recipient**: true
- **Independent Execution**: true

### **K-Node Constraints**

#### **Universal Constraints**
- **ASCII Only**: true
- **No Emojis**: true
- **No Special Chars**: ™, ®, ©, …, —, ', ', ", "

#### **K1 Specific Constraints**
- **Output Type**: enum
- **Valid Enums**: C_LEVEL, EXECUTIVE, SENIOR_TA, RECRUITER, SHORT_NEW
- **Confidence Min**: 0.95
- **Deterministic**: true

#### **K2 Specific Constraints**
- **Char Limit**: 60
- **Skip If Route**: CONNECTION_REQ
- **Distinct From**: K3, K5
- **Confidence Min**: 0.9

#### **K3 Specific Constraints**
- **Word Limit**: @global.message_constraints.by_type.{type}.word_range
- **Char Limit**: @global.message_constraints.by_type.{type}.char_range
- **Overlap With Resume Max**: 0.15
- **Readability Min**: 60
- **Confidence Min**: 0.88

#### **K4 Specific Constraints**
- **Max Attachments**: 1
- **Skip If Route**: CONNECTION_REQ
- **Attachment Types**:
  - C_LEVEL: optional_brief
  - EXECUTIVE: resume
  - SENIOR_TA: resume_required
  - RECRUITER: resume_ats
- **Link Validation**: HTTP_200
- **Confidence Min**: 0.95

#### **K5 Specific Constraints**
- **Word Limit**: C_LEVEL: 25, EXECUTIVE: 20, SENIOR_TA: 20, RECRUITER: 15, SHORT_NEW: 5
- **Required Verbs**: chat, connect, schedule, discuss, explore, meet
- **Confidence Min**: 0.95

#### **K6 Specific Constraints**
- **Skip If Route**: CONNECTION_REQ
- **Max Lines**: 3
- **Required Fields**: name, title, phone, email, linkedin
- **Confidence Min**: 0.99

#### **K7 Specific Constraints**
- **Blocking**: true
- **Coverage Min**: 0.95
- **Confidence Min**: 0.97

### **RAG Constraints**

#### **Always Disabled**
- **Routes**: CONNECTION_REQ
- **K-Nodes**: K.4, K.5, K.6, K.7

#### **Conditional RAG**
- **K2 Enabled For**: C_LEVEL, EXECUTIVE
- **K2 Disabled For**: SENIOR_TA, RECRUITER, SHORT_NEW

#### **Signal Quality Thresholds**
- **C_LEVEL**: 0.7
- **EXECUTIVE**: 0.65
- **SENIOR_TA**: 0.65
- **RECRUITER**: 0.6
- **SHORT_NEW**: null

#### **Retriever Requirements**
- **K1**: C_LEVEL: 6, EXECUTIVE: 4, SENIOR_TA: 4, RECRUITER: 3, SHORT_NEW: 0
- **K2**: C_LEVEL: 3, EXECUTIVE: 2, default: 0
- **K3**: C_LEVEL: 20, EXECUTIVE: 12, SENIOR_TA: 12, RECRUITER: 9, SHORT_NEW: 0

#### **Hop Requirements**
- **K1**: C_LEVEL: 3, EXECUTIVE: 2, SENIOR_TA: 2, RECRUITER: 2, SHORT_NEW: 0
- **K2**: C_LEVEL: 2, EXECUTIVE: 2, default: 0
- **K3**: C_LEVEL: 6, EXECUTIVE: 4, SENIOR_TA: 4, RECRUITER: 4, SHORT_NEW: 0

### **Parameter Constraints**

#### **Temperature**
- **Valid Range**: [0.0, 2.0]
- **Defaults**: K1: 0.1, K2: @varies_by_type, K3: @varies_by_type, K4: 0.15, K5: @varies_by_type, K6: 0.1, K7: 0.05

#### **Top_P**
- **Valid Range**: [0.0, 1.0]
- **Default**: 0.9

#### **Top_K**
- **Valid Range**: [1, 100]
- **Default**: 50

#### **Repetition Penalty**
- **Valid Range**: [1.0, 2.0]
- **Default**: 1.08

#### **Self Consistency**
- **Min Runs**: 2
- **Max Runs**: 12

### **Transition Rules**

#### **Triggers**
- **SHORT_NEW to SENIOR_TA**: k3_regenerate: true, k3_min_words: 140, k4_add_attachment: true
- **SHORT_NEW to EXECUTIVE**: k3_regenerate: true, k3_min_words: 140, k4_add_attachment: true
- **SHORT_NEW to C_LEVEL**: k3_regenerate: true, k3_min_words: 200, k4_add_attachment: optional

### **Enforcement Priority**

#### **CRITICAL Priority**
- Hard char limit
- ASCII only
- K-node confidence min
- Blocking on K7 fail

#### **WARNING Priority**
- Word range
- Personalization anchors min
- Readability min
- Signal quality thresholds

#### **INFO Priority**
- Formality
- Paragraph count

## **9. GLOBAL PATTERNS**

### **Output Formats**

#### **Detailed Reasoning**
- **Components**: input_tokens, rag_retrieval, ascii_tree, transformer, personas, slides
- **Required Emojis**: true
- **Pause After**: true

#### **Simplified Reasoning**
- **Components**: header, output, status, qa_table, continue
- **Max QA Rows**: 3

### **QA Check Patterns**

#### **Standard Checks**
- ASCII hygiene
- Confidence threshold
- Length compliance
- Distinctness
- Determinism

#### **K-Node Specific Checks**
- **K1**: enum_compliance, retrieval_grounding
- **K2**: keyword_presence
- **K3**: tailored_anchors, overlap_check, readability
- **K4**: link_resolution, attachment_type
- **K5**: action_verb
- **K6**: field_presence, line_count
- **K7**: global_coverage, block_on_fail

### **Error Patterns**

#### **Recoverable**
- **Actions**: targeted_retry, parameter_adjustment, fallback_to_non_rag
- **Max Retries**: 3
- **Preserve State**: true

#### **Blocking**
- **Triggers**: char_limit_exceeded, critical_validation_fail, confidence_below_threshold
- **Action**: halt_execution
- **Display**: specific_failure_reason

---

## **CONCLUSION**

This technical appendix provides the complete implementation details needed to understand, debug, or extend the LinkedIn Outreach Orchestrator system with full visibility into parameter values, validation rules, and execution logic.

**Version**: LIC_10-02-2025_v5.4  
**Analysis Date**: October 12, 2025  
**Coverage**: Complete (5167 lines analyzed)

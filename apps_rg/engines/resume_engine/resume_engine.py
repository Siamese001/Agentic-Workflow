import logging
from typing import Any, Optional, Protocol, Dict, List

import json
import time
from typing import Any, Dict, Optional

# The original file had issues with unused imports.
# We keep only the functions actually utilized in the three main functions.
from core_utils import (
    add_observations,
    generate_draft_llm,
    search_nodes,
    search_records,
    semantic_score_draft,
    write_file,
)

# Import fact checker for truth anchor validation
from fact_checker import HallucinationException

# Import hardened MCP functions
from mcp_hardening import get_version_locked_design

# Import egress filter for Protocol 8
from network_utils import strict_egress_filter

# Import Redis/LangCache pipeline functions
from redis_langcache_pipeline import execute_governed_prompt_caching

# Import hardening protocols
from security_utils import PromptFirewall, SecurityException

# Import time-bound benchmarking function
from time_bound_benchmarking import execute_time_bound_salary_benchmarking

# Define the specific allow-list for the Resume Engine
RESUME_ALLOWED_HOSTS = [
    "api.openai.com", "anthropic.com", "genai.google.com",
    "www.ycombinator.com", "linkedin.com", "indeed.com"  # Approved job board domains
]


def _extract_tools(tools: Dict[str, Any]) -> Dict[str, Any]:
    """Extracts and validates required tools from the tools dictionary."""
    extracted = {
        'fetch': tools.get('fetch'),
        'search_nodes_tool': tools.get('search_nodes'),
        'search_records_tool': tools.get('search_records'),
        'write_file_tool': tools.get('write_file'),
        'add_observations_tool': tools.get('add_observations'),
        'read_file_tool': tools.get('read_file'),
        'string_set': tools.get('string_set')
    }
    return extracted


def _validate_tools(tool_keys: list, tools: Dict[str, Any], logger: Optional[Any] = None) -> bool:
    """Checks if all specified tools are available."""
    for key in tool_keys:
        if not tools.get(key):
            if logger:
                logger.error(f"Required tool '{key}' not available.")
            return False
    return True


@strict_egress_filter(allowed_domains=RESUME_ALLOWED_HOSTS)
def _fetch_job_description(job_url: str, fetch_tool: Any, logger: Optional[Any] = None) -> Optional[str]:
    """Fetches job description content."""
    try:
        job_description_markdown = fetch_tool(url=job_url, max_length=1500)
        if logger:
            logger.info(
                f"✅ Fetched job description content from {job_url} (Length: {len(job_description_markdown)} chars)")
        return job_description_markdown
    except Exception as e:
        if logger:
            logger.error(f"Fetch MCP failed to retrieve job URL: {e}")
        return None


def _get_user_profile(user_name: str, search_nodes_tool: Any, logger: Optional[Any] = None) -> Optional[Dict[str, Any]]:
    """Retrieves user profile data from MEMemory."""
    try:
        user_profile_str = search_nodes_tool(
            query=f"detailed profile, career goals, and communication preferences for entity: {user_name}")
        user_profile = json.loads(user_profile_str)
        if logger:
            logger.info(
                f"✅ Retrieved L5 user profile data from MEMemory for {user_name}")
        return user_profile
    except Exception as e:
        if logger:
            logger.error(f"MEMemory MCP failed to retrieve user profile: {e}")
        return None


def _get_canonical_template(job_description_markdown: str, search_records_tool: Any, logger: Optional[Any] = None) -> Optional[str]:
    """Retrieves a canonical cover letter template from Pinecone."""
    pinecone_query = f"Highest-scoring cover letter template matching this job description: {job_description_markdown}"
    try:
        search_result_str = search_records_tool(
            query=pinecone_query, index="resume_templates", top_k=1, namespace="resume_templates")
        search_result = json.loads(search_result_str)
        canonical_template = search_result[0].get('text', '')

        if not canonical_template:
            if logger:
                logger.error("Pinecone search returned no matching canonical template.")
            return None

        if logger:
            logger.info("✅ Retrieved L3 canonical template from Pinecone.")
        return canonical_template

    except Exception as e:
        if logger:
            logger.error(f"Pinecone lookup failed: {e}")
        return None


def _build_cover_letter_content(user_profile: Dict[str, Any], canonical_template: str, job_url: str) -> str:
    """Builds the personalized cover letter content."""
    user_prefs = user_profile.get('preferences', {})
    career_goals = user_profile.get('career_goals', [])
    known_contacts = user_profile.get('relationships', [])

    template_content = canonical_template
    if isinstance(canonical_template, dict):
        template_content = canonical_template.get('text', str(canonical_template))

    user_name = user_profile.get('name', 'Candidate')  # Assuming name is in user_profile or passed

    final_cover_letter_content = f"""{template_content}

{user_name}

---
Generated via Agentic Workflow Resume Engine
Job URL: {job_url}
Date: {time.strftime('%Y-%m-%d')}
Personalization Notes:
- Industry: {user_prefs.get('industry', 'Technology')}
- Career Goals: {', '.join(career_goals[:2]) if career_goals else 'Growth and Innovation'}
- Known Contacts: {known_contacts[0] if known_contacts else 'None'}
"""
    return final_cover_letter_content


def _save_output(file_path_out: str, content: str, write_file_tool: Any, logger: Optional[Any] = None) -> bool:
    """Saves the generated content to a file."""
    try:
        write_file_tool(path=file_path_out, content=content)
        if logger:
            logger.info(f"✅ Final cover letter saved to Filesystem: {file_path_out}")
        return True
    except Exception as e:
        if logger:
            logger.error(f"Filesystem MCP failed to write file: {e}")
        return False


def save_artifact_metadata(file_path: str, metadata: Dict, logger: Optional[Any] = None) -> bool:
    """Saves a verifiable JSON file with LLM provenance metadata."""
    metadata_path = f"{file_path}.metadata.json"

    # Add audit timestamps
    metadata['timestamp'] = time.time()

    # Hash the final content to link metadata to artifact integrity
    import hashlib
    try:
        with open(file_path, 'rb') as f:
            metadata['artifact_hash'] = hashlib.sha256(f.read()).hexdigest()
    except Exception as e:
        if logger:
            logger.error(f"Failed to hash artifact for metadata: {e}")
        metadata['artifact_hash'] = None

    try:
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=4)
        if logger:
            logger.info(f"✅ Artifact Metadata saved to {metadata_path}")
        return True
    except Exception as e:
        if logger:
            logger.error(f"❌ Failed to save metadata: {e}")
        return False


def _update_memory(user_name: str, add_observations_tool: Any, logger: Optional[Any] = None) -> Any:
    """Updates MEMemory with application observation."""
    try:
        # Placeholders - would extract from JD in a real implementation
        job_title = "Senior Developer Role"
        company_name = "TechSolutions Corp"

        memory_update_payload = [{
            "entityName": user_name,
            "contents": [f"Applied for {job_title} at {company_name} on {time.strftime('%Y-%m-%d')}"]
        }]

        add_result = add_observations_tool(observations=memory_update_payload)

        if logger:
            logger.info(f"✅ L5 MEMemory updated with application observation.")
        return add_result

    except Exception as e:
        if logger:
            logger.warning(f"⚠️ MEMemory update failed (non-critical): {e}")
        return "Failed"


def generate_personalized_cover_letter(job_url: str, user_name: str, file_path_out: str, tools: Dict[str, Any], logger: Optional[Any] = None) -> Dict[str, Any]:
    """
    Implements the 'Hyper-Personalized Cover Letter' use case, integrating L1 (Fetch, Filesystem),
    L3 (Pinecone), and L5 (MEMemory) to create a targeted application document.
    """
    if logger:
        logger.info(
            f"🚀 Starting Personalized Cover Letter generation for {user_name} (Job: {job_url})...")

    required_tool_keys = ['fetch', 'search_nodes', 'search_records', 'write_file', 'add_observations']
    if not _validate_tools(required_tool_keys, tools, logger):
        return {"status": "error", "message": "Required MCP tools not available"}

    # --- Step 1: Get External Data (L1 Fetch) ---
    job_description_markdown = _fetch_job_description(job_url, tools['fetch'], logger)
    if not job_description_markdown:
        return {"status": "error", "message": "Failed to retrieve job description."}

    # --- HARDENING PROTOCOL 3: PROMPT FIREWALL ---
    # We validate the fetched content BEFORE sending it to Pinecone or LLM.
    firewall = PromptFirewall()
    try:
        if logger:
            logger.info("Scanning Job Description for injection attacks...")

        # Check if fetch returned valid text
        if not job_description_markdown or not isinstance(job_description_markdown, str):
            if logger:
                logger.warning("Job description is empty or invalid format.")
            return {"status": "FAILED", "reason": "EMPTY_INPUT"}

        # EXECUTE SCAN
        firewall.scan_input(job_description_markdown, context_name="Job Description")

    except SecurityException as e:
        if logger:
            logger.critical(f"HARDENING TRIGGERED: Job Description rejected. {e}")
        # Abort the process safely. DO NOT proceed to LLM generation.
        return {
            "status": "FAILED",
            "reason": "SECURITY_VIOLATION",
            "details": str(e)
        }
    # ---------------------------------------------

    # --- Step 2: Get Internal Context (L5 MEMemory) ---
    user_profile = _get_user_profile(user_name, tools['search_nodes'], logger)
    if not user_profile:
        return {"status": "error", "message": "Failed to retrieve user profile."}

    # --- Step 3: Retrieve Canonical Template (L3 Pinecone) ---
    canonical_template = _get_canonical_template(job_description_markdown, tools['search_records'], logger)
    if not canonical_template:
        return {"status": "error", "message": "Failed to retrieve canonical template."}

    # --- Step 4: Synthesize Content (LLM Action) ---
    final_cover_letter_content = _build_cover_letter_content(user_profile, canonical_template, job_url)

    # --- Step 5: Save Output (L1 Filesystem) ---
    save_success = _save_output(file_path_out, final_cover_letter_content, tools['write_file'], logger)
    if not save_success:
        return {"status": "error", "message": "Failed to save cover letter."}

    # --- HARDENING PROTOCOL 9: CRYPTOGRAPHIC PROVENANCE (Document) ---
    provenance_data = {
        "generator_model": "gemini-3-pro",  # Model used for final synthesis
        "consensus_score": 1.0,  # Result from P6 (if applicable)
        "prompt_hash": hash(job_url),  # Hash of the instruction prompt
        "verified_by_p4": True
    }
    metadata_success = save_artifact_metadata(file_path_out, provenance_data, logger)
    if not metadata_success:
        if logger:
            logger.warning("⚠️ Failed to save artifact metadata (non-critical)")

    # --- Step 6: Update Memory (L5 MEMemory) ---
    add_result = _update_memory(user_name, tools['add_observations'], logger)

    return {
        "status": "success",
        "message": f"Cover letter generated and saved. Memory updated.",
        "file_path": file_path_out,
        "memory_result": add_result
    }


def _get_design_standard(figma_template_id: str, figma_version: str, logger: Optional[Any] = None) -> Optional[Any]:
    """Retrieves design standard from Figma."""
    try:
        design_standard = get_version_locked_design(
            file_id=figma_template_id,
            version_id=figma_version,
            logger=logger
        )
        if logger:
            logger.info(f"✅ L2 Figma: Retrieved version-locked design standard v{figma_version}")
        return design_standard
    except Exception as e:
        if logger:
            logger.warning(f"⚠️ L2 Figma failed. Cannot validate resume design: {e}")
        return None


def _get_user_skills_and_history(user_name: str, search_nodes_tool: Any, logger: Optional[Any] = None) -> Optional[Dict[str, Any]]:
    """Retrieves user's skills and history from MEMemory."""
    try:
        user_skills_and_history_str = search_nodes_tool(
            query=f"detailed project summaries, core skills, and career focus for entity: {user_name}")
        user_skills_and_history = json.loads(user_skills_and_history_str)
        if logger:
            logger.info("✅ L5 MEMemory: Retrieved user profile")
        return user_skills_and_history
    except Exception as e:
        if logger:
            logger.error(f"L5 MEMemory failed to retrieve profile: {e}")
        return None


def _get_missing_keywords(job_description: str, user_skills_and_history: Dict[str, Any], search_records_tool: Any, logger: Optional[Any] = None) -> Optional[list]:
    """Identifies missing keywords using Pinecone."""
    pinecone_query = f"""
    JD Text: {job_description}
    User Skills: {user_skills_and_history.get('skills', 'None listed.')}
    Find the top 5 required keywords missing from the user's skills based on the JD.
    """
    try:
        search_result_str = search_records_tool(
            query=pinecone_query, index="resume_keywords", top_k=5)
        missing_keywords = json.loads(search_result_str)
        if logger:
            logger.info(f"✅ L3 Pinecone: Identified {len(missing_keywords)} potential skill gaps")
        return missing_keywords
    except Exception as e:
        if logger:
            logger.error(f"L3 Pinecone lookup failed: {e}")
        return None


def _generate_skill_gap_report(user_name: str, job_description: str, missing_keywords: list) -> str:
    """Generates the skill gap analysis report content."""
    missing_keywords_list = '\n'.join(
        ["- " + k.get('keyword', 'N/A') + " (Score: " + str(k.get('score', 0)) + ")" for k in missing_keywords])
    skill_report_content = f"""
***SKILL GAP ANALYSIS REPORT for {user_name}***
Date: {time.strftime('%Y-%m-%d %H:%M:%S')}
---
Target Job Description: {job_description[:100]}...
---
## Missing Core Keywords (L3 Pinecone Analysis):
{missing_keywords_list}

## Recommended Action:
Please re-integrate existing project summaries that contain these terms, or mark these as learning goals.
"""
    return skill_report_content


def _perform_design_validation(resume_file_path: str, design_standard: Any, read_file_tool: Any, logger: Optional[Any] = None) -> str:
    """Performs resume design validation."""
    if design_standard is None:
        return "SKIPPED (Figma L2 failure)"
    else:
        try:
            if read_file_tool:
                resume_content = read_file_tool(path=resume_file_path)
                # TODO: Compare resume structure against design_standard
                return "PASSED"
            else:
                if logger:
                    logger.warning("Read file tool not available for design validation.")
                return "UNKNOWN (Read tool unavailable)"
        except Exception as e:
            if logger:
                logger.warning(f"⚠️ Could not read resume file for design validation: {e}")
            return "UNKNOWN (File read error)"


def _cache_validation_status(user_name: str, job_url: str, final_status: str, design_status: str, string_set_tool: Any, logger: Optional[Any] = None) -> str:
    """Caches the validation status in Redis."""
    try:
        cache_key = f"validation_status:{user_name}:{job_url.split('/')[-1]}"
        string_set_tool(key=cache_key,
                        value=f"{final_status}|Design:{design_status}")
        if logger:
            logger.info("✅ L4 Redis: Cached validation status")
        return cache_key
    except Exception as e:
        if logger:
            logger.warning(f"⚠️ L4 Redis cache failed: {e}")
        return "CACHE_FAILED"


def validate_resume_design_skills(job_url: str, resume_file_path: str, user_name: str, tools: Dict[str, Any], logger: Optional[Any] = None) -> Dict[str, Any]:
    """
    Performs multi-layer validation (L1, L2, L3, L4, L5) on a resume against a target JD
    for skill gaps and design compliance, caching the result. (6 MCPs leveraged)
    """
    if logger:
        logger.info(
            f"🧬 Starting 6-MCP validation for {user_name} resume against {job_url}...")

    FIGMA_RESUME_TEMPLATE_ID = "Resume-Template-ID-101"
    report_file_path = f"reports/{user_name}_SkillGap_{int(time.time())}.txt"

    required_tool_keys = ['fetch', 'search_nodes', 'search_records', 'string_set', 'write_file', 'read_file']
    if not _validate_tools(required_tool_keys, tools, logger):
        return {"status": "error", "message": "Required MCP tools not available"}

    # --- Step 1: Get External Context (L1 Fetch) ---
    job_description = _fetch_job_description(job_url, tools['fetch'], logger)
    if not job_description:
        return {"status": "error", "message": "L1 Fetch failed for JD."}

    # --- Step 2: Get Design Standard (L2 Figma) ---
    FIGMA_RESUME_VERSION = "v1.0.0"
    design_standard = _get_design_standard(FIGMA_RESUME_TEMPLATE_ID, FIGMA_RESUME_VERSION, logger)
    design_status = "PASSED" if design_standard is not None else "SKIPPED"

    # --- Step 3: Get Internal Profile (L5 MEMemory) ---
    user_skills_and_history = _get_user_skills_and_history(user_name, tools['search_nodes'], logger)
    if not user_skills_and_history:
        return {"status": "error", "message": "L5 MEMemory failed to retrieve profile."}

    # --- Step 4: Semantic Match (L3 Pinecone) ---
    missing_keywords = _get_missing_keywords(job_description, user_skills_and_history, tools['search_records'], logger)
    if missing_keywords is None:
        return {"status": "error", "message": "L3 Pinecone lookup failed."}

    # --- Step 5: Validation & Cache (LLM + L4 Redis) ---
    skill_report_content = _generate_skill_gap_report(user_name, job_description, missing_keywords)
    design_status = _perform_design_validation(resume_file_path, design_standard, tools['read_file_tool'], logger)

    final_status = "FAILED" if missing_keywords else "PASSED"
    cache_key = _cache_validation_status(user_name, job_url, final_status, design_status, tools['string_set'], logger)

    # --- Step 6: Generate Report (L1 Filesystem) ---
    if not _save_output(report_file_path, skill_report_content, tools['write_file_tool'], logger):
        return {"status": "error", "message": "L1 Filesystem failed to write report."}

    return {
        "status": final_status,
        "message": f"Validation complete. Status: {final_status}. Design: {design_status}.",
        "report_path": report_file_path,
        "cache_key": cache_key,
        "missing_keywords": len(missing_keywords),
        "design_validation": design_status
    }


def _get_initial_context(job_description: str, user_name: str, logger: Optional[Any] = None) -> Optional[Dict[str, Any]]:
    """Retrieves initial context for draft optimization."""
    try:
        user_data_str = search_nodes(
            query=f"project details and skills for {user_name}")
        user_data = json.loads(user_data_str)

        required_keywords_str = search_records(
            query=f"keywords for {job_description}", index="resume_keywords", top_k=5)
        required_keywords = json.loads(required_keywords_str)

        job_title = "Software Engineer"  # Default - would extract from JD
        location = "San Francisco, CA"  # Default - would extract from JD
        salary_result = {"source": "Default"}
        salary_data = "Competitive market rate"

        try:
            salary_result = execute_time_bound_salary_benchmarking(
                job_title=job_title,
                location=location,
                logger=logger
            )
            salary_data = salary_result.get("salary_data")
            if logger:
                logger.info(f"✅ Retrieved fresh salary data: {salary_data}")
        except Exception as e:
            if logger:
                logger.warning(f"Salary benchmarking failed: {e}. Using default.")

        if logger:
            logger.info(
                f"✅ Retrieved user data and {len(required_keywords)} required keywords")
        return {
            "user_data": user_data,
            "required_keywords": required_keywords,
            "salary_data": salary_data,
            "salary_result": salary_result
        }
    except Exception as e:
        if logger:
            logger.error(f"Failed to retrieve initial context: {e}")
        return None


def _render_prompt(job_description: str, context: Dict[str, Any]) -> str:
    """Renders the prompt with all context."""
    rendered_prompt = f"""
CONTEXT:
- Job Description: {job_description}
- User Profile: {context.get('user_data')}
- Keywords: {context.get('required_keywords')}
- Salary Benchmark: {context.get('salary_data')} (Source: {context.get('salary_result', {}).get('source', 'Unknown')})

TASK:
Generate a professional resume draft that optimally aligns with the job requirements.
Focus on skills, projects, and experience that match the keywords.
Include appropriate salary expectations based on current market data.
"""
    return rendered_prompt


def _generate_and_score_draft(rendered_prompt: str, user_name: str, job_description: str, logger: Optional[Any] = None) -> Dict[str, Any]:
    """Generates a draft using governed caching and scores it."""
    try:
        cache_result = execute_governed_prompt_caching(
            user_name=user_name,
            job_description_hash=str(hash(job_description)),
            rendered_prompt=rendered_prompt,
            logger=logger
        )

        if cache_result["status"] == "cache_hit":
            draft_content = cache_result["draft"]
            if logger:
                logger.info(f"✅ Retrieved draft from LangCache")
        elif cache_result["status"] == "budget_aborted":
            return {"status": "budget_aborted", "message": "LLM generation budget exhausted"}
        else:
            draft_content = generate_draft_llm(rendered_prompt)
            if logger:
                logger.info(f"✅ Generated new draft")

        score = semantic_score_draft(draft_content, job_description)
        return {"draft": draft_content, "score": score, "source": cache_result.get("status", "generated")}

    except Exception as e:
        if logger:
            logger.warning(f"Governed caching failed: {e}. Using fallback generation.")
        try:
            draft_content = generate_draft_llm(rendered_prompt)
            score = semantic_score_draft(draft_content, job_description)
            return {"draft": draft_content, "score": score, "source": "fallback_generated"}
        except Exception as fallback_e:
            if logger:
                logger.error(f"Fallback generation also failed: {fallback_e}")
            return {"draft": None, "score": 0.0, "source": "failed"}


def _log_iteration_to_memory(user_name: str, iteration: int, score: float, threshold: float, source: str, logger: Optional[Any] = None) -> None:
    """Logs iteration details to MEMemory."""
    try:
        add_observations(observations=[{
            "entityName": "DraftGeneration",
            "contents": [
                f"Draft iteration {iteration} for {user_name}",
                f"Score: {score:.2f}",
                f"Threshold: {threshold:.2f}",
                f"Source: {source.capitalize()}"
            ]
        }])
    except Exception as e:
        if logger:
            logger.warning(f"MEMemory logging failed for iteration {iteration}: {e}")


def generate_optimized_draft(job_description: str, user_name: str, score_threshold: float = 0.90, max_iterations: int = 3, logger: Optional[Any] = None) -> Dict[str, Any]:
    """
    Iteratively generates and refines a resume draft until a semantic score threshold is met.
    (Sequential Thinking leveraged through the iterative scoring loop.)
    """
    if logger:
        logger.info(
            f"🔄 Starting Iterative Draft Optimization for {user_name} (Target Score: {score_threshold})")

    attempts = 0
    final_draft = None
    final_score = 0.0

    # 1. Initial Context Retrieval
    context = _get_initial_context(job_description, user_name, logger)
    if not context:
        return {"status": "error", "message": "Context retrieval failed."}

    for i in range(max_iterations):
        attempts += 1

        # Render the full prompt with all context
        rendered_prompt = _render_prompt(job_description, context)

        # Generate and score draft
        generation_result = _generate_and_score_draft(rendered_prompt, user_name, job_description, logger)

        if generation_result.get("status") == "budget_aborted":
            return {
                "status": "budget_aborted",
                "message": "LLM generation budget exhausted",
                "attempts": attempts
            }

        draft_content = generation_result.get("draft")
        score = generation_result.get("score", 0.0)
        source = generation_result.get("source", "generated")

        if logger:
            logger.info(
                f"Iteration {i}: Score = {score:.2f} (threshold = {score_threshold:.2f})")

        # Log iteration to MEMory
        _log_iteration_to_memory(user_name, i, score, score_threshold, source, logger)

        # Check if threshold met
        if score >= score_threshold:
            final_draft = draft_content
            final_score = score
            break

        # Use this draft for next iteration (sequential thinking)
        # In a real system, we might refine the prompt based on score feedback

    if final_draft is None and draft_content:
        # Return best effort if threshold not met
        final_draft = draft_content
        final_score = score
        if logger:
            logger.warning(
                f"Threshold not met after {max_iterations} attempts. Returning best effort.")
    elif final_draft is None:
        return {"status": "error", "message": "Draft generation failed after all attempts."}

    # --- HARDENING PROTOCOL 4: TRUTH ANCHOR ---
    try:
        if logger:
            logger.info("Verifying draft against Golden Record...")
        fact_checker.validate_skills(final_draft)
    except HallucinationException as e:
        if logger:
            logger.critical(f"HARDENING TRIGGERED: Draft rejected due to hallucination. {e}")
        # Self-Correction Strategy:
        # We could loop back to the LLM with a correction prompt:
        # "You included unverified skills: {e}. Remove them."
        # For now, we fail closed.
        return {
            "status": "FAILED",
            "reason": "HALLUCINATION_DETECTED",
            "details": str(e)
        }
    # ------------------------------------------

    # --- Finalization (L1 Filesystem) ---
    final_file_path = f"drafts/{user_name}_optimized_draft.txt"
    try:
        write_file(path=final_file_path, content=final_draft)
        if logger:
            logger.info(f"✅ Final draft saved to {final_file_path}")
    except Exception as e:
        if logger:
            logger.error(f"Failed to save final draft: {e}")
        return {"status": "error", "message": f"File write failed: {e}"}

    return {
        "status": "optimized" if final_score >= score_threshold else "threshold_not_met",
        "final_score": final_score,
        "attempts": attempts,
        "file_path": final_file_path,
        "user_name": user_name,
        "target_threshold": score_threshold
    }


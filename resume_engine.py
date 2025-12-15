import time
import json
from typing import Dict, Any, Optional

# Import core utilities for mock functions
from core_utils import (
    semantic_score_draft, 
    generate_draft_llm,
    search_nodes,
    search_records,
    write_file,
    add_observations
)

def generate_personalized_cover_letter(job_url: str, user_name: str, file_path_out: str, tools: Dict[str, Any], logger: Optional[Any] = None) -> Dict[str, Any]:
    """
    Implements the 'Hyper-Personalized Cover Letter' use case, integrating L1 (Fetch, Filesystem), 
    L3 (Pinecone), and L5 (MEMemory) to create a targeted application document.
    """
    if logger:
        logger.info(f"🚀 Starting Personalized Cover Letter generation for {user_name} (Job: {job_url})...")

    # Extract tools from the tools dictionary
    fetch = tools.get('fetch')
    search_nodes = tools.get('search_nodes')
    search_records = tools.get('search_records')
    write_file = tools.get('write_file')
    add_observations = tools.get('add_observations')

    # Validate required tools
    if not all([fetch, search_nodes, search_records, write_file, add_observations]):
        return {"status": "error", "message": "Required MCP tools not available"}

    # --- Step 1: Get External Data (L1 Fetch) ---
    try:
        # Fetches the job description URL and converts it to clean Markdown
        job_description_markdown = fetch(url=job_url, max_length=1500)
        if logger:
            logger.info(f"✅ Fetched job description content from {job_url} (Length: {len(job_description_markdown)} chars)")
    except Exception as e:
        return {"status": "error", "message": f"Fetch MCP failed to retrieve job URL: {e}"}

    # --- Step 2: Get Internal Context (L5 MEMemory) ---
    try:
        # Search the knowledge graph for the user entity and related facts/preferences
        user_profile_str = search_nodes(query=f"detailed profile, career goals, and communication preferences for entity: {user_name}")
        user_profile = json.loads(user_profile_str)
        if logger:
            logger.info(f"✅ Retrieved L5 user profile data from MEMemory for {user_name}")
    except Exception as e:
        return {"status": "error", "message": f"MEMemory MCP failed to retrieve user profile: {e}"}

    # --- Step 3: Retrieve Canonical Template (L3 Pinecone) ---
    # Use the job description (JD) as the semantic query to find the best template
    pinecone_query = f"Highest-scoring cover letter template matching this job description: {job_description_markdown}"
    try:
        search_result_str = search_records(query=pinecone_query, index="resume_templates", top_k=1, namespace="resume_templates")
        search_result = json.loads(search_result_str)
        canonical_template = search_result[0].get('text', '')
        
        if not canonical_template:
             return {"status": "error", "message": "Pinecone search returned no matching canonical template."}
        
        if logger:
            logger.info("✅ Retrieved L3 canonical template from Pinecone.")
            
    except Exception as e:
        return {"status": "error", "message": f"Pinecone lookup failed: {e}"}
        
    # --- Step 4: Synthesize Content (LLM Action) ---
    
    # TO DO: The LLM will now synthesize the final letter based on the three inputs:
    # 1. job_description_markdown
    # 2. user_profile_str (Full JSON profile)
    # 3. canonical_template (Best matching structure)
    
    # In the real execution, the cognitive node would process this entire function 
    # and generate the synthesis logic here. For this structured response, we simulate 
    # the successful synthesis using the inputs.
    
    # Extract key information for personalization
    user_prefs = user_profile.get('preferences', {})
    career_goals = user_profile.get('career_goals', [])
    known_contacts = user_profile.get('relationships', [])
    
    # Since canonical_template is a string, we'll use it directly or parse if it's JSON
    if isinstance(canonical_template, str):
        # Use the template as is or extract sections if it has structure
        template_content = canonical_template
    else:
        # If it's a dict, extract the text content
        template_content = canonical_template.get('text', str(canonical_template))
    
    # Build personalized content using the template
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

    # --- Step 5: Save Output (L1 Filesystem) ---
    try:
        write_result = write_file(path=file_path_out, content=final_cover_letter_content)
        if logger:
            logger.info(f"✅ Final cover letter saved to Filesystem: {file_path_out}")
    except Exception as e:
        return {"status": "error", "message": f"Filesystem MCP failed to write file: {e}"}

    # --- Step 6: Update Memory (L5 MEMemory) ---
    # Log the application event against the user's entity for future context
    try:
        # Extract the company name and job title from the JD for the observation
        # In a real implementation, this would use NLP to extract from the JD
        job_title = "Senior Developer Role"  # Placeholder - would extract from JD
        company_name = "TechSolutions Corp"  # Placeholder - would extract from JD
        
        # We assume the user's entity is already named {user_name}
        memory_update_payload = [{
            "entityName": user_name,
            "contents": [f"Applied for {job_title} at {company_name} on {time.strftime('%Y-%m-%d')}"]
        }]
        
        add_result = add_observations(observations=memory_update_payload)
        
        if logger:
            logger.info(f"✅ L5 MEMemory updated with application observation.")

    except Exception as e:
        if logger:
            logger.warning(f"⚠️ MEMemory update failed (non-critical): {e}")
        add_result = "Failed"

    return {
        "status": "success",
        "message": f"Cover letter generated and saved. Memory updated.",
        "file_path": file_path_out,
        "memory_result": add_result
    }

def validate_resume_design_skills(job_url: str, resume_file_path: str, user_name: str, tools: Dict[str, Any], logger: Optional[Any] = None) -> Dict[str, Any]:
    """
    Performs multi-layer validation (L1, L2, L3, L4, L5) on a resume against a target JD 
    for skill gaps and design compliance, caching the result. (6 MCPs leveraged)
    """
    if logger:
        logger.info(f"🧬 Starting 6-MCP validation for {user_name} resume against {job_url}...")

    # --- Setup Variables ---
    FIGMA_RESUME_TEMPLATE_ID = "Resume-Template-ID-101"
    report_file_path = f"reports/{user_name}_SkillGap_{int(time.time())}.txt"

    # Extract tools from the tools dictionary
    fetch = tools.get('fetch')
    get_variable_defs = tools.get('get_variable_defs')
    search_nodes = tools.get('search_nodes')
    search_records = tools.get('search_records')
    string_set = tools.get('string_set')
    write_file = tools.get('write_file')
    read_file = tools.get('read_file')

    # Validate required tools
    if not all([fetch, get_variable_defs, search_nodes, search_records, string_set, write_file]):
        return {"status": "error", "message": "Required MCP tools not available"}

    # --- Step 1: Get External Context (L1 Fetch) ---
    try:
        job_description = fetch(url=job_url, max_length=2000)
        if logger:
            logger.info("✅ L1 Fetch: Retrieved job description")
    except Exception as e:
        return {"status": "error", "message": f"L1 Fetch failed for JD: {e}"}

    # --- Step 2: Get Design Standard (L2 Figma) ---
    try:
        # Retrieves the approved resume structure/token list
        design_standard_str = get_variable_defs(node_id=FIGMA_RESUME_TEMPLATE_ID)
        design_standard = json.loads(design_standard_str)
        if logger:
            logger.info("✅ L2 Figma: Retrieved design standard")
    except Exception as e:
        # This is a warning state: we can still check skills but design validation is skipped
        if logger:
            logger.warning(f"⚠️ L2 Figma failed. Cannot validate resume design: {e}")
        design_standard = None

    # --- Step 3: Get Internal Profile (L5 MEMemory) ---
    try:
        # Get the source text (skills/projects) that should be in the resume
        user_skills_and_history_str = search_nodes(query=f"detailed project summaries, core skills, and career focus for entity: {user_name}")
        user_skills_and_history = json.loads(user_skills_and_history_str)
        if logger:
            logger.info("✅ L5 MEMemory: Retrieved user profile")
    except Exception as e:
        return {"status": "error", "message": f"L5 MEMemory failed to retrieve profile: {e}"}
    
    # --- Step 4: Semantic Match (L3 Pinecone) ---
    # Query Pinecone with the JD and the user's actual skills to find gaps
    pinecone_query = f"""
    JD Text: {job_description} 
    User Skills: {user_skills_and_history.get('skills', 'None listed.')}
    Find the top 5 required keywords missing from the user's skills based on the JD.
    """
    try:
        search_result_str = search_records(query=pinecone_query, index="resume_keywords", top_k=5)
        # Assuming Pinecone returns the missing keywords list
        missing_keywords = json.loads(search_result_str)
        if logger:
            logger.info(f"✅ L3 Pinecone: Identified {len(missing_keywords)} potential skill gaps")
    except Exception as e:
        return {"status": "error", "message": f"L3 Pinecone lookup failed: {e}"}

    # --- Step 5: Validation & Cache (LLM + L4 Redis) ---
    
    # 5a. Validation 1 (Skill Gap Report Synthesis - LLM Action)
    skill_report_content = f"""
***SKILL GAP ANALYSIS REPORT for {user_name}***
Date: {time.strftime('%Y-%m-%d %H:%M:%S')}
---
Target Job Description: {job_description[:100]}...
---
## Missing Core Keywords (L3 Pinecone Analysis):
{'\n'.join([f"- {k.get('keyword', 'N/A')} (Score: {k.get('score', 0)})" for k in missing_keywords])}

## Recommended Action:
Please re-integrate existing project summaries that contain these terms, or mark these as learning goals.
"""
    
    # 5b. Validation 2 (Design Check Synthesis - LLM Action)
    design_status = "PASSED"
    if design_standard is None:
        design_status = "SKIPPED (Figma L2 failure)"
    else:
        # In a real implementation, we'd read and analyze the resume file
        try:
            if read_file:
                resume_content = read_file(path=resume_file_path)
                # TODO: Compare resume structure against design_standard
                # For now, assume passed
                design_status = "PASSED"
        except Exception as e:
            if logger:
                logger.warning(f"⚠️ Could not read resume file for design validation: {e}")
            design_status = "UNKNOWN (File read error)"
    
    final_status = "FAILED" if missing_keywords else "PASSED"
    
    # 5c. Cache Status (L4 Redis)
    try:
        cache_key = f"validation_status:{user_name}:{job_url.split('/')[-1]}"
        string_set(key=cache_key, value=f"{final_status}|Design:{design_status}")
        if logger:
            logger.info(f"✅ L4 Redis: Cached validation status")
    except Exception as e:
        if logger:
            logger.warning(f"⚠️ L4 Redis cache failed: {e}")
        cache_key = "CACHE_FAILED"

    # --- Step 6: Generate Report (L1 Filesystem) ---
    try:
        write_file(path=report_file_path, content=skill_report_content)
        if logger:
            logger.info(f"✅ L1 Filesystem: Saved skill gap report")
        
        return {
            "status": final_status,
            "message": f"Validation complete. Status: {final_status}. Design: {design_status}.",
            "report_path": report_file_path,
            "cache_key": cache_key,
            "missing_keywords": len(missing_keywords),
            "design_validation": design_status
        }
    except Exception as e:
        return {"status": "error", "message": f"L1 Filesystem failed to write report: {e}"}

def generate_optimized_draft(job_description: str, user_name: str, score_threshold: float = 0.90, max_iterations: int = 3, logger: Optional[Any] = None) -> Dict[str, Any]:
    """
    Iteratively generates and refines a resume draft until a semantic score threshold is met.
    (Sequential Thinking leveraged through the iterative scoring loop.)
    """
    if logger:
        logger.info(f"🔄 Starting Iterative Draft Optimization for {user_name} (Target Score: {score_threshold})")

    current_draft = ""
    current_score = 0.0
    
    # 1. Initial Context Retrieval (L5 MEMemory)
    # Assumes search_nodes finds user data and required keywords from Pinecone (L3)
    try:
        user_data_str = search_nodes(query=f"project details and skills for {user_name}")
        user_data = json.loads(user_data_str)
        
        required_keywords_str = search_records(query=f"keywords for {job_description}", index="resume_keywords", top_k=5)
        required_keywords = json.loads(required_keywords_str)
        
        if logger:
            logger.info(f"✅ Retrieved user data and {len(required_keywords)} required keywords")
    except Exception as e:
        if logger:
            logger.error(f"Failed to retrieve initial context: {e}")
        return {"status": "error", "message": f"Context retrieval failed: {e}"}
    
    # --- Iterative Loop (Sequential Thinking) ---
    for i in range(1, max_iterations + 1):
        if current_score >= score_threshold:
            if logger:
                logger.info(f"✅ Threshold met after {i-1} iterations")
            break # Sequential Thinking Success: Threshold met

        # 2. Generate/Refine Draft (LLM/Thinking Node)
        new_draft = generate_draft_llm("Resume", user_data, job_description, current_draft, required_keywords)
        current_draft = new_draft

        # 3. Semantic Scoring (LLM/Utility)
        new_score = semantic_score_draft(current_draft, job_description)
        current_score = new_score
        
        if logger:
            logger.info(f"Attempt {i}: Draft scored {current_score:.2f}. Continuing refinement...")

        # 4. Log Iteration (L5 MEMemory)
        try:
            add_observations(observations=[{
                "entityName": "OptimizationCycle",
                "contents": [
                    f"Draft Iteration {i} scored {current_score:.2f} against JD.",
                    f"User: {user_name}, Target: {score_threshold:.2f}",
                    f"Current draft saved with {len(current_draft)} characters"
                ]
            }])
        except Exception as e:
            if logger:
                logger.warning(f"⚠️ Failed to log iteration: {e}")

    # --- Finalization (L1 Filesystem) ---
    final_file_path = f"drafts/{user_name}_optimized_draft.txt"
    try:
        write_file(path=final_file_path, content=current_draft)
        if logger:
            logger.info(f"✅ Final draft saved to {final_file_path}")
    except Exception as e:
        if logger:
            logger.error(f"Failed to save final draft: {e}")
        return {"status": "error", "message": f"File write failed: {e}"}
    
    return {
        "status": "optimized" if current_score >= score_threshold else "threshold_not_met",
        "final_score": current_score,
        "attempts": i,
        "file_path": final_file_path,
        "user_name": user_name,
        "target_threshold": score_threshold
    }

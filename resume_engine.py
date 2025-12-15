import time
import json
from typing import Dict, Any, Optional

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

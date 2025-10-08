from langchain.tools import tool
from core.database_handler import search_profiles
from core.vector_store import search_similar_profiles
from tools.web_tools import web_search
import json

@tool
def profile_search(filters: dict) -> str:
    """
    Use for FACTUAL and EXPLICIT queries about profiles. Searches by name, field, institution, or a specific, known skill.
    The input 'filters' should be a dictionary where keys can be 'name', 'field', 'institution', or 'skill' and values are lists of strings.
    This tool is for bilingual search (Persian/English).
    """
    return search_profiles(filters)

@tool
def semantic_search_and_answer(query: str) -> str:
    """
    Use for CONCEPTUAL or SUBJECTIVE queries about qualities and potential within profiles.
    This is for questions like "Who is a good candidate for a leadership role?".
    It finds the most relevant profiles based on the meaning of the query.
    """
    profile_ids = search_similar_profiles(query)
    if not profile_ids:
        return "No relevant profiles found based on the semantic search."
    
    relevant_profiles_data = []
    for pid in profile_ids:
        profile_info_str = search_profiles(filters={"id": pid})
        if "nothing doesn't found" not in profile_info_str:
            relevant_profiles_data.append(profile_info_str)
    
    return "\n---\n".join(relevant_profiles_data)

@tool
def web_searc_pro(query: str) -> str:
    """
    Use when the user's query is clearly about information that CANNOT be found within the user profiles, like current events, definitions, or finding external articles.
    """
    structured_results = web_search(query)
    return json.dumps(structured_results, ensure_ascii=False, indent=2)
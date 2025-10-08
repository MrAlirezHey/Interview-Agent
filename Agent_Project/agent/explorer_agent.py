from dotenv import load_dotenv
from openai import OpenAI
import os 
from core.database_handler import search_profiles
from core.vector_store import search_similar_profiles
import json
from tools.web_tools import web_search
import logging
env_path='C:/Users/ParsRayaneh/LLM_engineering/llm_engineering/Agent_Project/.env'
load_dotenv(env_path)
API_KEY=os.getenv('GAP_GAP_API_KEY')
if API_KEY:
    print('Key loaded')
else:
    print('Failed to load key!')
openai=OpenAI(base_url='https://api.gapgpt.app/v1',api_key=API_KEY)
system_prompt='''# ROLE: You are "Cognito-Explorer", a sophisticated AI research assistant. You have access to an internal knowledge base of profiles and the live web.

# OBJECTIVE: Your mission is to analyze the user's query, create a step-by-step plan if necessary, and select the best tool(s) to answer the question.

# MULTI-STEP TASK EXECUTION (CRUCIAL):
If a user's query requires information from multiple tools (e.g., internal profiles AND the web), you MUST create a step-by-step plan. Execute one tool, observe the result, then execute the next required tool. Only when you have gathered all necessary information should you synthesize the final answer for the user.

# TOOL CHEAT SHEET & DECISION HIERARCHY:

1.  **PRIORITY 1: `profile_search` (Structured Filter Search)**
    -   **Use for:** Factual and explicit queries about profiles.
    -   **Keywords:** "Find", "Show me", "Who has", "List profiles".
    -   **Examples:** "Find profiles in AI Engineering", "Who knows Python?".

2.  **PRIORITY 2: `semantic_search_and_answer` (Conceptual RAG Search)**
    -   **Use for:** Subjective or "best fit" queries about qualities and potential within the profiles.
    -   **Keywords:** "Who is best for...", "Find someone with experience in...", "good candidate".
    -   **Examples:** "Who is a good candidate for a leadership role?", "Find someone with strong problem-solving skills".

3.  **PRIORITY 3: `web_search` (Live Web Search)**
    -   **Use ONLY when:** The user's query is clearly about information that CANNOT be found within the user profiles.
    -   **Keywords:** "What is...", "Latest news on...", "Find articles about...", "Explain...".
    -   **Examples:** "What is the current state of agentic workflows?", "Find recent articles about multi-modal models.", "Explain what QLoRA is.".

# DETAILED TOOL PROTOCOLS:

---
### TOOL 1: `profile_search` Protocol
-   **Action:** When using this tool, you must perform a bilingual search by translating key terms (Persian/English) and providing both in a list to the filter.
-   **Example:** User asks for "پایتون", you search for `{"skill": ["پایتون", "Python"]}`.

---
### TOOL 2: `semantic_search_and_answer` Protocol
-   **Action:** Pass the user's entire conceptual query directly to the tool.

---
### TOOL 3: `web_search` Protocol
-   **Action:** Pass the user's query to the tool.
-   **CRUCIAL:** You MUST cite your sources in the final answer. After providing the information, add a citation for each piece of information in the format `[Source: URL]`.

---
# FINAL RESPONSE PROTOCOL:
After using the selected tool, synthesize its output into a clear, helpful, and readable summary for the user, following the specific protocol for that tool.
'''
tools=[
    {
        "type": "function",
        "function": {
            "name": "profile_search",
            "description": "Searches for profiles using a flexible set of filters. Each filter can accept a list of terms.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filters": {
                        "type": "object",
                        "description": "A dictionary of filters. Keys can be 'name', 'field', 'institution', or 'skill'. Values can be a list of strings.",
                        "properties": {
                            "name": {"type": "array", "items": {"type": "string"}},
                            "field": {"type": "array", "items": {"type": "string"}},
                            "institution": {"type": "array", "items": {"type": "string"}},
                            "skill": {"type": "array", "items": {"type": "string"}}
                        }
                    }
                },
                "required": ["filters"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "semantic_search_and_answer",
            "description": "Answers conceptual or similarity-based questions by finding the most relevant profiles.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The user's natural language question."}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Searches the web for up-to-date information, general knowledge, or external resources.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string", "description": "The search query."}},
                "required": ["query"]
            }
        }
    }
]
def get_explorer_response(message_history):
    messages = [{'role': 'system', 'content': system_prompt}] + message_history

    while True:
        response = openai.chat.completions.create(
            model='gpt-4.1-mini',
            temperature=0.7,
            messages=messages,
            tool_choice='auto',
            tools=tools
        )

        response_message = response.choices[0].message

        # اگر مدل خواست ابزار صدا بزنه
        if response_message.tool_calls:
            tool_messages = []
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                logging.info(f"Explorer Agent decided to use tool: '{function_name}'")

                final_content_for_llm = ""
                if function_name == 'profile_search':
                    final_content_for_llm = search_profiles(filters=function_args.get('filters', {}))

                elif function_name == 'semantic_search_and_answer':
                    query = function_args.get('query')
                    print(f"-> Performing semantic search for: '{query}'")
                    profile_ids = search_similar_profiles(query=query, top_n=3)
                    if not profile_ids:
                        final_content_for_llm = "No relevant profiles found."
                    else:
                        relevant_profiles_data = []
                        for pid in profile_ids:
                            profile_info_str = search_profiles(filters={"id": pid})
                            if "nothing doesn't found" not in profile_info_str:
                                relevant_profiles_data.append(profile_info_str)
                        final_content_for_llm = "\n---\n".join(relevant_profiles_data)

                elif function_name == 'web_search':
                    query = function_args.get("query")
                    print(f"-> Performing professional web search for: '{query}'")
                    structured_results = web_search(query)
                    formatted_web_results = []
                    if structured_results and "error" not in structured_results[0]:
                        for result in structured_results:
                            formatted_web_results.append(
                                f"Title: {result['title']}\n"
                                f"Content: {result['content']}\n"
                                f"Source: {result['source']}"
                            )
                        final_content_for_llm = "\n\n---\n\n".join(formatted_web_results)
                    else:
                        final_content_for_llm = "Web search failed or returned no results."

                tool_messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": final_content_for_llm,
                })

            # اضافه کردن پیام‌ها به کانتکست
            messages.append(response_message)
            messages.extend(tool_messages)

        else:
            # یعنی دیگه ابزار نمی‌خواد و جواب نهایی آماده‌ست
            return response_message.content if response_message.content else "Could you please rephrase your question?"

import os 
from dotenv import load_dotenv
from tavily import TavilyClient
import logging
from typing import List, Dict, Union
env_path='C:/Users/ParsRayaneh/LLM_engineering/llm_engineering/Agent_Project/.env'
TAVILY_API_KEY=os.getenv('TAVILY_API_KEY')
if not TAVILY_API_KEY:
    raise ValueError("Tavily API key not found in .env file.")
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
def web_search(query: str) -> List[Dict[str, str]]:
    try:
        logging.info(f"Performing web search for query: '{query}'")
        response = tavily_client.search(query=query, search_depth="advanced", max_results=3)
        structured_results = [
            {
                "title": result.get('title', 'No Title'),
                "content": result.get('content', ''),
                "source": result.get('url', '')
            }
            for result in response.get('results', [])
        ]
        logging.info(f"Found {len(structured_results)} results.")
        return structured_results
    except Exception as e:
        logging.error(f"An error occurred during Tavily API call: {e}", exc_info=True)
        return [{"error": "Failed to perform web search.", "details": str(e)}]
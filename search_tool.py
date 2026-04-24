from ddgs import DDGS
from typing import List, Dict

def perform_search(query: str, platform: str, max_results: int = 20) -> List[Dict[str, str]]:
    """
    Performs a Google Dork style search using DuckDuckGo.
    :param query: The search keywords
    :param platform: platform name
    :param max_results: Number of results to fetch
    :return: List of dictionaries containing 'title', 'url', 'snippet'
    """
    platform_map = {
        "linkedin": "site:linkedin.com/in/",
        "naukri": "site:naukri.com/naukri-dot-com/",
        "github": "site:github.com",
        "kaggle": "site:kaggle.com",
        "behance": "site:behance.net",
        "dribbble": "site:dribbble.com"
    }
    
    site_filter = platform_map.get(platform.lower(), "site:linkedin.com/in/")
    full_query = f"{site_filter} {query}"
    
    results = []
    try:
        with DDGS() as ddgs:
            # Perform text search
            search_results = ddgs.text(full_query, max_results=max_results)
            for res in search_results:
                results.append({
                    "title": res.get("title", ""),
                    "url": res.get("href", ""),
                    "snippet": res.get("body", ""),
                    "platform": platform
                })
    except Exception as e:
        print(f"Error executing search on {platform}: {e}")
        
    return results

from langchain_community.utilities import DuckDuckGoSearchAPIWrapper

def google_search(query: str, num_results: int = 5):
    """
    Perform a DuckDuckGo search (free, no API key needed)
    and return structured top results.
    """
    try:
        ddg = DuckDuckGoSearchAPIWrapper()
        results = ddg.results(query, num_results)
        return [
            {"title": r["title"], "link": r["link"], "snippet": r["snippet"]}
            for r in results
        ]
    except Exception as e:
        return {"error": f"Search failed: {e}"}



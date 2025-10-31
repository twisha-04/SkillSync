from langchain_community.utilities import WikipediaAPIWrapper
from langchain_community.tools import WikipediaQueryRun
import re

class WikipediaSearchTool:
    """
    A generalized wrapper for Wikipedia search that can be used as a tool or utility.
    Returns structured search results (title, summary, url).
    """

    def __init__(self, top_k: int = 3, max_chars: int = 2500):
        self.top_k = top_k
        self.max_chars = max_chars
        self.api_wrapper = WikipediaAPIWrapper(
            top_k_results=top_k,
            doc_content_chars_max=max_chars
        )
        self.query_tool = WikipediaQueryRun(api_wrapper=self.api_wrapper)

    def search(self, query: str):
        """
        Searches Wikipedia and returns structured information.
        """
        try:
            raw_result = self.query_tool.run(query)
            if not raw_result:
                return {"error": f"No Wikipedia results found for '{query}'."}

            chunks = re.split(r"\n==+|\n\n", raw_result)
            summaries = [c.strip() for c in chunks if c.strip()]

            return {
                "query": query,
                "pages_fetched": len(summaries),
                "summaries": summaries[:self.top_k],
                "combined_text": "\n\n---\n\n".join(summaries[:self.top_k]),
                "wiki_url": f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}"
            }

        except Exception as e:
            return {"error": f"Error fetching Wikipedia info: {e}"}

def wiki_search(query: str, top_k: int = 3, max_chars: int = 2500):
    return WikipediaSearchTool(top_k=top_k, max_chars=max_chars).search(query)

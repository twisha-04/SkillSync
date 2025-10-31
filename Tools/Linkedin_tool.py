"""
LinkedIn Search Tool (DuckDuckGo Version)
-----------------------------------------
Fetches job listings or profile insights from LinkedIn using DuckDuckGo search.
This version does NOT require any API key.
"""

from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
import re

class LinkedInTool:
    """
    A generalized LinkedIn search tool that can fetch job or skill information.
    Uses DuckDuckGo Search API (free, no authentication needed).
    """

    def __init__(self, top_k: int = 5):
        self.top_k = top_k
        self.search = DuckDuckGoSearchAPIWrapper()

    def search_jobs(self, role: str, location: str = "India"):
        """
        Searches for LinkedIn job listings for the given role and location.
        Returns structured job data.
        """
        try:
            query = f"site:linkedin.com/jobs '{role}' {location}"
            results = self.search.results(query, self.top_k)

            jobs = []
            for r in results[:self.top_k]:
                job = {
                    "title": r.get("title", "").strip(),
                    "url": r.get("link", ""),
                    "snippet": r.get("snippet", ""),
                }

                # Try extracting company name heuristically
                match = re.search(r"at\s([A-Z][A-Za-z0-9&.\s]+)", r.get("title", ""))
                if match:
                    job["company"] = match.group(1).strip()

                jobs.append(job)

            return {
                "query": query,
                "count": len(jobs),
                "jobs": jobs,
            }

        except Exception as e:
            return {"error": f"LinkedIn job search failed: {e}"}

    def search_profiles(self, keyword: str):
        """
        Searches LinkedIn public profiles relevant to a keyword (role, skill, or domain).
        Returns structured profile data.
        """
        try:
            query = f"site:linkedin.com/in {keyword}"
            results = self.search.results(query, self.top_k)

            profiles = [
                {
                    "name": r.get("title", "").replace(" | LinkedIn", "").strip(),
                    "url": r.get("link", ""),
                    "headline": r.get("snippet", ""),
                }
                for r in results[:self.top_k]
            ]

            return {
                "query": query,
                "count": len(profiles),
                "profiles": profiles,
            }

        except Exception as e:
            return {"error": f"LinkedIn profile search failed: {e}"}


def linkedin_search_jobs(role: str, location: str = "India", top_k: int = 5):
    """Helper function to quickly fetch LinkedIn job listings."""
    return LinkedInTool(top_k=top_k).search_jobs(role, location)


def linkedin_search_profiles(keyword: str, top_k: int = 5):
    """Helper function to quickly fetch LinkedIn public profiles."""
    return LinkedInTool(top_k=top_k).search_profiles(keyword)

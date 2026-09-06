import httpx
from loguru import logger
from typing import List, Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
from src.config import settings


class GitHubCollector:
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"token {settings.GITHUB_TOKEN}",
            "X-GitHub-Api-Version": "2022-11-28"
        }

    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=60))
    async def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}{endpoint}", 
                    headers=self.headers, 
                    params=params
                )
                
                if response.status_code == 403: # Likely rate limit
                    # Check for X-RateLimit-Reset
                    reset_time = response.headers.get("X-RateLimit-Reset")
                    logger.warning(f"GitHub Rate limit hit. Reset at {reset_time}")
                    # We raise for retry, but in a real app we might sleep until reset_time
                
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error {e.response.status_code} for {endpoint}: {e}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error for {endpoint}: {e}")
                raise

    async def fetch_trending_repos(self, language: str = "python") -> List[Dict[str, Any]]:
        # GitHub doesn't have a direct 'trending' API endpoint. 
        # Usually, we search for repos created recently with high stars.
        # As an alternative for MVP, we use the search API.
        query = f"language:{language} created:>=2024-01-01 stars:>100"
        endpoint = "/search/repositories"
        params = {"q": query, "sort": "stars", "order": "desc", "per_page": 100}
        
        data = await self._make_request(endpoint, params)
        return data.get("items", [])

    async def search_by_keywords(self, keywords: List[str]) -> List[Dict[str, Any]]:
        all_repos = []
        for keyword in keywords:
            query = f"{keyword} stars:>50"
            endpoint = "/search/repositories"
            params = {"q": query, "sort": "updated", "order": "desc", "per_page": 50}
            try:
                data = await self._make_request(endpoint, params)
                all_repos.extend(data.get("items", []))
            except Exception as e:
                logger.error(f"Error searching keyword {keyword}: {e}")
        
        # Deduplicate by full_name
        unique_repos = {repo["full_name"]: repo for repo in all_repos}.values()
        return list(unique_repos)

    async def fetch_file_content(self, owner: str, repo: str, path: str) -> Optional[str]:
        endpoint = f"/repos/{owner}/{repo}/contents/{path}"
        try:
            data = await self._make_request(endpoint)
            import base64
            return base64.b64decode(data["content"]).decode("utf-8")
        except Exception as e:
            logger.error(f"Error fetching file {path} for {owner}/{repo}: {e}")
            return None

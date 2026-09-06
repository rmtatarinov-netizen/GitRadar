from typing import Dict, Any, List, Optional
from datetime import datetime
from src.storage.models import Category, Maturity

class BaseParser:
    def __init__(self):
        self.ai_keywords = {
            "agent", "llm", "rag", "mcp", "workflow", 
            "automation", "tool", "plugin", "skill", "langchain", 
            "llamaindex", "autogen", "crewai", "openai", "anthropic"
        }
        self.category_map = {
            "agent_framework": ["agent", "framework", "orchestration", "multi-agent"],
            "mcp_server": ["mcp", "server", "tool server"],
            "rag": ["rag", "retrieval", "vector", "embedding"],
            "tool_utility": ["tool", "utility", "helper", "cli"],
            "model_wrapper": ["wrapper", "client", "sdk", "api client"],
            "monitoring_eval": ["eval", "benchmark", "monitoring", "observability"],
            "deploy_infra": ["deploy", "serving", "inference", "docker", "k8s"],
        }

    def parse_github_repo(self, repo_data: Dict[str, Any], readme: Optional[str] = None, dependencies: List[str] = None, features: Dict[str, bool] = None) -> Dict[str, Any]:
        description = repo_data.get("description") or ""
        topics = repo_data.get("topics", [])
        full_text = (description + " " + " ".join(topics) + " " + (readme or "")).lower()
        
        if dependencies:
            full_text += " " + " ".join(dependencies).lower()

        # Basic scoring
        score = self._calculate_score(full_text, repo_data, dependencies, features)
        
        # Basic classification
        category = self._determine_category(full_text)

        return {
            "repo_name": repo_data.get("name"),
            "repo_url": repo_data.get("html_url"),
            "owner_login": repo_data.get("owner", {}).get("login"),
            "owner_type": repo_data.get("owner", {}).get("type"),
            "description": description,
            "language": repo_data.get("language"),
            "topics": topics,
            "stars": repo_data.get("stargazers_count", 0),
            "forks": repo_data.get("forks_count", 0),
            "watchers": repo_data.get("watchers_count", 0),
            "license": repo_data.get("license", {}).get("spdx_id") if repo_data.get("license") else None,
            "created_at": datetime.fromisoformat(repo_data["created_at"].replace("Z", "+00:00")),
            "updated_at": datetime.fromisoformat(repo_data["updated_at"].replace("Z", "+00:00")),
            "pushed_at": datetime.fromisoformat(repo_data["pushed_at"].replace("Z", "+00:00")),
            "category": category,
            "agent_relevance_score": score,
            "maturity": Maturity.EARLY, # Default for MVP
            "readme_snippet": self._extract_readme_snippet(readme),
            "tags": list(self.ai_keywords.intersection(set(full_text.split()))),
            "integrations": self._extract_integrations(full_text),
            "has_examples": features.get("has_examples", False) if features else False,
            "has_tests": features.get("has_tests", False) if features else False,
            "has_cli": features.get("has_cli", False) if features else False,
            "has_sdk": features.get("has_sdk", False) if features else False,
            "has_api": features.get("has_api", False) if features else False,
        }

    def _calculate_score(self, text: str, repo_data: Dict[str, Any], dependencies: List[str] = None, features: Dict[str, bool] = None) -> int:
        score = 0
        # +1 for AI keywords
        if any(kw in text for kw in self.ai_keywords):
            score += 1
        # +1 for integrations/dependencies
        if dependencies and len(dependencies) > 0:
            score += 1
        # +1 for examples
        if features and features.get("has_examples"):
            score += 1
        # +1 for tests and CI
        if features and features.get("has_tests"):
            score += 1
        # +1 for active development (recent push within 30 days)
        # (Simplified for MVP)
        if repo_data.get("stargazers_count", 0) > 1000:
            score += 1
        
        return min(max(score, 0), 5)

    def _determine_category(self, text: str) -> Category:
        for cat, keywords in self.category_map.items():
            if any(kw in text for kw in keywords):
                return Category[cat.upper()]
        return Category.OTHER

    def _extract_readme_snippet(self, readme: Optional[str]) -> Optional[str]:
        if not readme:
            return None
        # Basic snippet: first 500 chars
        return readme[:500] + "..." if len(readme) > 500 else readme

    def _extract_integrations(self, text: str) -> List[str]:
        found = []
        for kw in self.ai_keywords:
            if kw in text:
                found.append(kw)
        return found

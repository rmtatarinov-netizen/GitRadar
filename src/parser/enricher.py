import re
import json
from typing import Dict, Any, List, Optional
from src.storage.models import Category, Maturity

class DependencyEnricher:
    def __init__(self):
        self.dependency_files = {
            "python": ["requirements.txt", "pyproject.toml", "setup.py"],
            "javascript": ["package.json"],
            "rust": ["Cargo.toml"],
            "go": ["go.mod"],
        }
        self.ai_libraries = {
            "langchain", "llamaindex", "openai", "anthropic", "crewai", 
            "autogen", "pydantic", "fastapi", "torch", "transformers", 
            "sentence-transformers", "chromadb", "qdrant", "milvus", "pinecone"
        }

    def analyze_dependencies(self, content: str, file_path: str) -> List[str]:
        dependencies = []
        if "package.json" in file_path:
            try:
                data = json.loads(content)
                deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                dependencies.extend(deps.keys())
            except: pass
        elif "requirements.txt" in file_path:
            dependencies.extend(re.findall(r'^([a-zA-Z0-9\-_]+)', content, re.MULTILINE))
        elif "pyproject.toml" in file_path:
            dependencies.extend(re.findall(r'([a-zA-Z0-9\-_]+) =', content))
        elif "Cargo.toml" in file_path:
            dependencies.extend(re.findall(r'([a-zA-Z0-9\-_]+) =', content))
            
        return [d for d in dependencies if d.lower() in self.ai_libraries]

    def detect_features(self, files_list: List[str]) -> Dict[str, bool]:
        features = {
            "has_examples": any("examples/" in f or "demo/" in f or "notebooks/" in f for f in files_list),
            "has_tests": any("tests/" in f or ".github/workflows/" in f for f in files_list),
            "has_cli": any("cli" in f.lower() for f in files_list),
            "has_sdk": any("sdk" in f.lower() for f in files_list),
            "has_api": any("api" in f.lower() for f in files_list),
        }
        return features

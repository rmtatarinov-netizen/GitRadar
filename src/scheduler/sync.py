import asyncio
from loguru import logger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.collector.github import GitHubCollector
from src.parser.base import BaseParser
from src.parser.enricher import DependencyEnricher
from src.storage.repository import SkillRepository, AsyncSessionLocal
from src.config import settings


class SyncService:
    def __init__(self):
        self.collector = GitHubCollector()
        self.parser = BaseParser()
        self.enricher = DependencyEnricher()

    async def sync_repositories(self):
        logger.info("Starting GitHub synchronization...")
        
        # 1. Fetch targets (Trending + Search)
        repos = await self.collector.fetch_trending_repos("python")
        search_results = await self.collector.search_by_keywords(["agent", "mcp", "llm", "rag"])
        all_targets = repos + search_results

        async with AsyncSessionLocal() as session:
            repo_store = SkillRepository(session)
            
            for repo_data in all_targets:
                url = repo_data["html_url"]
                owner = repo_data["owner"]["login"]
                name = repo_data["name"]
                
                # Basic check to avoid redundant processing
                existing = await repo_store.get_by_url(url)
                if existing and existing.updated_at == repo_data["updated_at"]:
                    continue

                # Enrich data
                readme = await self.collector.fetch_file_content(owner, name, "README.md")
                
                # Analysis of dependencies (simplified: check most common files)
                deps = []
                for file_path in ["requirements.txt", "package.json", "pyproject.toml"]:
                    content = await self.collector.fetch_file_content(owner, name, file_path)
                    if content:
                        deps.extend(self.enricher.analyze_dependencies(content, file_path))
                
                # Basic file listing for feature detection (mocked as we need a separate API call for full list)
                # In full version, we'd use /repos/{owner}/{repo}/contents
                features = self.enricher.detect_features(["README.md", "requirements.txt"]) 
                
                # Parse and save
                skill_data = self.parser.parse_github_repo(
                    repo_data, 
                    readme=readme, 
                    dependencies=deps, 
                    features=features
                )
                
                if existing:
                    await repo_store.update(url, skill_data)
                else:
                    await repo_store.create(skill_data)
                
                logger.info(f"Processed {url}")

async def start_scheduler():
    scheduler = AsyncIOScheduler()
    sync_service = SyncService()
    
    # Sync every 24 hours
    scheduler.add_job(sync_service.sync_repositories, "interval", hours=24)
    
    # Digest every 24 hours (simplified: passed bot and channel_id later)
    # scheduler.add_job(digest_service.send_daily_digest, "cron", hour=9)
    
    scheduler.start()
    logger.info("Scheduler started")
    return scheduler

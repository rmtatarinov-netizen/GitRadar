from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, update, delete
from src.storage.models import Base, Skill
from src.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

class SkillRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_url(self, url: str) -> Optional[Skill]:
        result = await self.session.execute(select(Skill).where(Skill.repo_url == url))
        return result.scalar_one_or_none()

    async def create(self, skill_data: dict) -> Skill:
        skill = Skill(**skill_data)
        self.session.add(skill)
        await self.session.commit()
        await self.session.refresh(skill)
        return skill

    async def update(self, url: str, update_data: dict) -> Optional[Skill]:
        await self.session.execute(
            update(Skill).where(Skill.repo_url == url).values(**update_data)
        )
        await self.session.commit()
        return await self.get_by_url(url)

    async def get_newest(self, limit: int = 10):
        result = await self.session.execute(
            select(Skill).order_by(Skill.first_seen_at.desc()).limit(limit)
        )
        return result.scalars().all()

    async def get_top_by_stars(self, limit: int = 10):
        result = await self.session.execute(
            select(Skill).order_by(Skill.stars.desc()).limit(limit)
        )
        return result.scalars().all()

    async def search(self, query: str, limit: int = 20):
        # Enhanced search using ILIKE for name, description and topics
        # For production, we would use tsvector in PostgreSQL
        result = await self.session.execute(
            select(Skill).where(
                (Skill.description.ilike(f"%{query}%")) | 
                (Skill.repo_name.ilike(f"%{query}%")) |
                (Skill.tags.cast(String).ilike(f"%{query}%"))
            ).limit(limit)
        )
        return result.scalars().all()

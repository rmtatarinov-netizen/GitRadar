from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession
from src.config import settings
from src.storage.repository import SkillRepository
from src.storage.AsyncSessionLocal import AsyncSessionLocal # Note: fixing import later

# Note: Using a placeholder for session management in the handler
# In a real app, we'd use a middleware to inject the session

async def get_skill_card(skill) -> str:
    return (
        f"<b>{skill.repo_name}</b>\n"
        f"🔗 <a href='{skill.repo_url}'>GitHub Link</a>\n\n"
        f"{skill.description[:200]}...\n\n"
        f"🌐 Lang: {skill.language} | ⭐ Stars: {skill.stars}\n"
        f"📂 Cat: {skill.category.value} | 🎯 Score: {skill.agent_relevance_score}/5\n"
        f"🛠 Integrations: {', '.join(skill.integrations)}"
    )

async def start_handler(message: Message):
    await message.answer(
        "Привет! Я GitRadar 📡\n\n"
        "Помогаю находить лучшие инструменты для разработки AI-агентов.\n\n"
        "Команды:\n"
        "/search <запрос> — поиск инструментов\n"
        "/new — последние добавленные\n"
        "/top — топ по звездам"
    )

async def search_handler(message: Message, session_factory):
    query = message.text.replace("/search", "").strip()
    if not query:
        return await message.answer("Введите запрос для поиска, например: /search rag")
    
    async with session_factory() as session:
        repo = SkillRepository(session)
        results = await repo.search(query)
        if not results:
            return await message.answer("Ничего не найдено 😕")
        
        for skill in results:
            card = await get_skill_card(skill)
            await message.answer(card, parse_mode="HTML", disable_web_page_preview=True)

async def new_handler(message: Message, session_factory):
    async with session_factory() as session:
        repo = SkillRepository(session)
        skills = await repo.get_newest()
        if not skills:
            return await message.answer("База пока пуста 📭")
        
        for skill in skills:
            card = await get_skill_card(skill)
            await message.answer(card, parse_mode="HTML", disable_web_page_preview=True)

async def top_handler(message: Message, session_factory):
    async with session_factory() as session:
        repo = SkillRepository(session)
        skills = await repo.get_top_by_stars()
        if not skills:
            return await message.answer("База пока пуста 📭")
        
        for skill in skills:
            card = await get_skill_card(skill)
            await message.answer(card, parse_mode="HTML", disable_web_page_preview=True)

from aiogram import types, F
from aiogram.filters import Command
from src.storage.repository import SkillRepository
from src.storage.models import Category, Maturity

async def admin_edit_category(message: types.Message, session_factory):
    # Command: /admin_cat <url> <category_value>
    args = message.text.split()
    if len(args) < 3:
        return await message.answer("Использование: /admin_cat <url> <category>")
    
    url, cat_val = args[1], args[2]
    async with session_factory() as session:
        repo = SkillRepository(session)
        try:
            cat = Category[cat_val.upper()]
            await repo.update(url, {"category": cat})
            await message.answer(f"Категория обновлена на {cat.value}")
        except KeyError:
            await message.answer("Неверная категория. Доступные: " + ", ".join([c.name for c in Category]))

async def admin_delete_skill(message: types.Message, session_factory):
    # Command: /admin_del <url>
    args = message.text.split()
    if len(args) < 2:
        return await message.answer("Использование: /admin_del <url>")
    
    url = args[1]
    async with session_factory() as session:
        repo = SkillRepository(session)
        # Implementation of delete in repository.py needs to be added or used via session
        from sqlalchemy import delete
        from src.storage.models import Skill
        await session.execute(delete(Skill).where(Skill.repo_url == url))
        await session.commit()
        await message.answer(f"Скилл {url} удален из базы")

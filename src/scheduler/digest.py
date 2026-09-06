from loguru import logger
from typing import List
from src.storage.repository import SkillRepository, AsyncSessionLocal
from src.bot.handlers import get_skill_card
from aiogram import Bot
from src.config import settings


class DigestService:
    def __init__(self, bot: Bot, channel_id: str):
        self.bot = bot
        self.channel_id = channel_id

    async def send_daily_digest(self):
        logger.info("Generating daily digest...")
        async with AsyncSessionLocal() as session:
            repo = SkillRepository(session)
            # Get top 5 new skills for the digest
            skills = await repo.get_newest(limit=5)
            
            if not skills:
                logger.info("No new skills for digest")
                return

            text = "🚀 <b>Ежедневный дайджест новых инструментов AI-агентов!</b>\n\n"
            for skill in skills:
                card = await get_skill_card(skill)
                text += f"{card}\n\n---\n\n"
            
            try:
                await self.bot.send_message(
                    chat_id=self.channel_id, 
                    text=text, 
                    parse_mode="HTML", 
                    disable_web_page_preview=True
                )
                logger.info("Digest sent to channel")
            except Exception as e:
                logger.error(f"Error sending digest: {e}")

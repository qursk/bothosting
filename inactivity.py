# inactivity.py
import datetime
import asyncio
from config import TEXT_CHANNEL_ID


class Inactivity:

    def __init__(self, bot):
        self.bot = bot
        self.last = datetime.datetime.utcnow()

    async def on_message(self, message):
        if message.channel.id == TEXT_CHANNEL_ID:
            self.last = datetime.datetime.utcnow()

    async def run(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            now = datetime.datetime.utcnow()
            diff = (now - self.last).total_seconds()

            if diff >= 120:
                channel = self.bot.get_channel(TEXT_CHANNEL_ID)
                if channel:
                    try:

                        def check(m):
                            return not m.pinned

                        deleted = await channel.purge(limit=100, check=check)
                        print("[INACTIVITY] Deleted", len(deleted))
                    except Exception as e:
                        print("[INACTIVITY] ERROR:", e)

            await asyncio.sleep(60)

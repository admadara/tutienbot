"""cogs/tasks.py - Background tasks v4"""
import discord
from discord.ext import commands
from discord.ext import tasks
import time

from utils.persistent_cache import save_all_caches

class Tasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.stamina_regen.start()
        self.expire_auctions.start()
        self.weekly_reset.start()
        self.auto_save.start()   # ← Auto-save mỗi 3 phút

    def cog_unload(self):
        self.stamina_regen.cancel()
        self.expire_auctions.cancel()
        self.weekly_reset.cancel()
        self.auto_save.cancel()

    @tasks.loop(minutes=1)
    async def stamina_regen(self):
        try:
            await self.bot.db.execute(
                "UPDATE players SET stamina=MIN(stamina_max, stamina+stamina_regen) "
                "WHERE stamina<stamina_max"
            )
        except Exception as e:
            print(f"[Tasks] stamina_regen: {e}")

    @stamina_regen.before_loop
    async def before_stamina(self):
        await self.bot.wait_until_ready()

    @tasks.loop(minutes=10)
    async def expire_auctions(self):
        try:
            now = int(time.time())
            rows = await self.bot.db.fetchall(
                "SELECT * FROM auction WHERE status='active' AND expires_at<?", (now,)
            )
            for r in rows:
                seller = await self.bot.db.get_player(r["seller_id"])
                if seller:
                    await self.bot.db.add_item(r["seller_id"], r["item_id"], r["quantity"])
            if rows:
                await self.bot.db.execute(
                    "UPDATE auction SET status='expired' "
                    "WHERE status='active' AND expires_at<?", (now,)
                )
        except Exception as e:
            print(f"[Tasks] expire_auctions: {e}")

    @expire_auctions.before_loop
    async def before_expire(self):
        await self.bot.wait_until_ready()

    @tasks.loop(hours=1)
    async def weekly_reset(self):
        try:
            import datetime
            now_dt = datetime.datetime.utcnow()
            if now_dt.weekday() == 0 and now_dt.hour == 0:
                await self.bot.db.execute(
                    "UPDATE tower SET weekly_floor=0 WHERE 1=1"
                )
                print("[Tasks] Weekly tower reset done!")
        except Exception as e:
            print(f"[Tasks] weekly_reset: {e}")

    @weekly_reset.before_loop
    async def before_weekly(self):
        await self.bot.wait_until_ready()

    # ══ AUTO-SAVE mỗi 3 phút ══════════════════════════════════
    @tasks.loop(minutes=3)
    async def auto_save(self):
        try:
            count = await save_all_caches(self.bot)
            if count > 0:
                print(f"[AutoSave] ✅ Đã lưu {count} cache(s)")
        except Exception as e:
            print(f"[AutoSave] ❌ Lỗi: {e}")

    @auto_save.before_loop
    async def before_auto_save(self):
        await self.bot.wait_until_ready()



async def setup(bot):
    await bot.add_cog(Tasks(bot))

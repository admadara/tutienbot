"""cogs/mystic.py - Thiên Cơ Các: Lời Tiên Tri, Triệu Hồi Hộ Pháp, Linh Thú Đồ

3 tính năng dùng API ngoài (không cần auth):
  1. ,tl thienco  | "Thiên Cơ Bất Khả Lộ" -> Lời tiên tri ngẫu nhiên (Advice Slip API)
  2. ,tl trieuhoi | ,tl hophap          -> Triệu hồi Hộ Pháp/Linh Sứ (Jikan random character)
  3. ,tl linhthudo | ,tl dottha_anh     -> Ảnh linh thú/embed đột phá cảnh giới (waifu.im)
"""
import discord
from discord.ext import commands
import aiohttp
import random
import time

from utils.helpers import require_player, now
from utils.embeds import *

# ── Cấu hình API ─────────────────────────────────────────────
ADVICE_URL = "https://api.adviceslip.com/advice"
JIKAN_URL = "https://api.jikan.moe/v4/random/characters"
WAIFU_URL = "https://api.waifu.im/search"

# Tag dùng cho thẻ Linh Thú / Đột Phá (waifu.im) — toàn bộ đều safe-for-work
WAIFU_TAGS = ["waifu", "maid", "uniform", "selfies"]

# Danh xưng ngẫu nhiên gắn cho Hộ Pháp/Linh Sứ triệu hồi được, để có cảm giác "tu tiên" hơn
HOPHAP_TITLES = [
    "Hộ Pháp Trưởng Lão", "Linh Sứ Thượng Cổ", "Hộ Pháp Tông Môn",
    "Linh Sứ Thiên Mệnh", "Hộ Pháp Bí Cảnh", "Linh Sứ Cửu Trọng Thiên",
    "Hộ Pháp Huyền Vũ", "Linh Sứ Tử Vi",
]
HOPHAP_RARITY = [
    (0.45, "🟩 Phàm Giai", 0x8BC34A),
    (0.30, "🟦 Linh Giai", 0x2196F3),
    (0.15, "🟪 Địa Giai", 0x9C27B0),
    (0.08, "🟧 Thiên Giai", 0xFF9800),
    (0.02, "🟥 Thần Giai", 0xF44336),
]


def _roll_rarity():
    r = random.random()
    acc = 0.0
    for prob, label, color in HOPHAP_RARITY:
        acc += prob
        if r <= acc:
            return label, color
    return HOPHAP_RARITY[0][1], HOPHAP_RARITY[0][2]


def _safe(p, k, d=0):
    v = p.get(k) if p else None
    return v if v is not None else d


class Mystic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._hophap_cooldowns: dict = {}   # uid -> last_ts (chống spam, không cần persist)
        self._linhthudo_cooldowns: dict = {}

    async def cog_load(self):
        # Bảng riêng lưu cooldown "Thiên Cơ" (1 lần/ngày, bền qua restart)
        await self.bot.db.execute("""
            CREATE TABLE IF NOT EXISTS mystic_advice (
                user_id TEXT PRIMARY KEY,
                last_day INTEGER DEFAULT 0,
                streak INTEGER DEFAULT 0
            )
        """)

    # ══════════════════════════════════════════════════════════
    # 1) THIÊN CƠ BẤT KHẢ LỘ — Lời tiên tri ngẫu nhiên mỗi ngày
    # ══════════════════════════════════════════════════════════
    @commands.command(
        name="thienco",
        aliases=["tienco", "thienco_batkhalo", "batkhalo", "tt_thienco"]
    )
    @require_player
    async def thienco(self, ctx):
        """🔮 Thiên Cơ Bất Khả Lộ — Hé lộ một câu thiên cơ huyền bí (1 lần/ngày)"""
        uid = str(ctx.author.id)
        today = int(now() // 86400)

        row = await self.bot.db.fetchone(
            "SELECT * FROM mystic_advice WHERE user_id=?", (uid,)
        )
        last_day = row["last_day"] if row else 0
        streak = row["streak"] if row else 0

        if last_day >= today:
            await ctx.send(embed=warn(
                "Thiên cơ hôm nay đã được hé lộ cho đạo hữu rồi!\n"
                "Thiên cơ bất khả lộ nhị thứ trong cùng một ngày...\n\n"
                f"_Quay lại vào ngày mai để tiếp tục chuỗi `{streak}` ngày._"
            )); return

        loading = await ctx.send("🔮 *Đang thông linh với Thiên Đạo...*")

        advice_text = None
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(ADVICE_URL, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        advice_text = (data.get("slip") or {}).get("advice")
        except Exception:
            advice_text = None

        if not advice_text:
            await loading.delete()
            await ctx.send(embed=warn("❌ Thiên Đạo im lặng... Thử lại sau giây lát!"))
            return

        new_streak = streak + 1 if last_day == today - 1 else 1
        await self.bot.db.execute("""
            INSERT INTO mystic_advice (user_id, last_day, streak) VALUES (?,?,?)
            ON CONFLICT(user_id) DO UPDATE SET last_day=excluded.last_day, streak=excluded.streak
        """, (uid, today, new_streak))

        # Thưởng nhỏ theo streak để có động lực ghé mỗi ngày
        reward = 500 * min(new_streak, 30)
        player = await self.bot.db.get_player(ctx.author.id)
        await self.bot.db.update_player(
            ctx.author.id,
            linh_thach_ha=_safe(player, "linh_thach_ha") + reward
        )

        await loading.delete()
        embed = discord.Embed(
            title="🔮 THIÊN CƠ BẤT KHẢ LỘ",
            description=(
                f"_Thiên Đạo vận hành, một tia thiên cơ lóe lên trong tâm trí đạo hữu..._\n\n"
                f"📜 **\"{advice_text}\"**"
            ),
            color=0x6B48FF
        )
        embed.add_field(name="🔥 Chuỗi Ngày", value=f"`{new_streak}` ngày liên tục", inline=True)
        embed.add_field(name="💰 Thiên Thưởng", value=f"+{reward:,} Hạ LT", inline=True)
        embed.set_footer(text="Mỗi ngày 1 lần • Thiên Cơ Các • ,tl thienco")
        await ctx.send(embed=embed)

    # ══════════════════════════════════════════════════════════
    # 2) TRIỆU HỒI HỘ PHÁP / LINH SỨ — nhân vật anime ngẫu nhiên
    # ══════════════════════════════════════════════════════════
    @commands.command(
        name="trieuhoi",
        aliases=["hophap", "linhsu", "trieu_hophap"]
    )
    @require_player
    async def trieuhoi(self, ctx):
        """⚜️ Triệu Hồi Hộ Pháp/Linh Sứ — gọi một vị Hộ Pháp ngẫu nhiên hộ trì cho đạo hữu"""
        uid = str(ctx.author.id)
        now_ts = time.time()
        COOLDOWN = 60  # 1 phút, chống spam — chỉ mang tính giải trí, không lưu DB

        last = self._hophap_cooldowns.get(uid, 0)
        remaining = COOLDOWN - (now_ts - last)
        if remaining > 0:
            await ctx.send(embed=warn(
                f"⏳ Trận pháp triệu hồi chưa hồi phục! Còn **{remaining:.0f}s**."
            )); return

        loading = await ctx.send("⚜️ *Đang bày trận triệu hồi Hộ Pháp...*")

        char_data = None
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(JIKAN_URL, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        payload = await resp.json()
                        char_data = payload.get("data")
        except Exception:
            char_data = None

        if not char_data:
            await loading.delete()
            await ctx.send(embed=warn("❌ Trận pháp bất ổn, triệu hồi thất bại! Thử lại sau."))
            return

        self._hophap_cooldowns[uid] = now_ts

        name = char_data.get("name", "??? Vô Danh")
        about = char_data.get("about") or ""
        # Cắt ngắn mô tả gốc để vừa embed, không hiển thị quá dài
        about_short = about.strip().splitlines()[0] if about.strip() else ""
        if len(about_short) > 220:
            about_short = about_short[:217] + "..."

        image_url = (
            char_data.get("images", {}).get("webp", {}).get("image_url")
            or char_data.get("images", {}).get("jpg", {}).get("image_url")
        )

        title_name = random.choice(HOPHAP_TITLES)
        rarity_label, rarity_color = _roll_rarity()

        embed = discord.Embed(
            title=f"⚜️ TRIỆU HỒI THÀNH CÔNG!",
            description=(
                f"Trận pháp rung chuyển, không gian xé toạc...\n"
                f"**{title_name}** đã giáng lâm!\n\n"
                f"📛 Danh hiệu: **{name}**\n"
                f"🏵️ Phẩm cấp: {rarity_label}"
            ),
            color=rarity_color
        )
        if about_short:
            embed.add_field(name="📖 Lai Lịch", value=about_short, inline=False)
        if image_url:
            embed.set_image(url=image_url)
        embed.set_footer(text=f"Triệu hồi bởi {ctx.author.display_name} • Hồi chiêu 60s • Thiên Cơ Các")
        await loading.delete()
        await ctx.send(embed=embed)

    # ══════════════════════════════════════════════════════════
    # 3) LINH THÚ ĐỒ / ĐỘT PHÁ CẢNH GIỚI — ảnh minh họa từ waifu.im
    # ══════════════════════════════════════════════════════════
    @commands.command(
        name="linhthudo",
        aliases=["lt_do", "anhlinhthu", "dottha_anh", "dp_anh"]
    )
    @require_player
    async def linhthudo(self, ctx, *, the_loai: str = None):
        """🖼️ Linh Thú Đồ — rút một bức linh thú đồ minh họa ngẫu nhiên (dùng kèm khoe đột phá cảnh giới)"""
        uid = str(ctx.author.id)
        now_ts = time.time()
        COOLDOWN = 30

        last = self._linhthudo_cooldowns.get(uid, 0)
        remaining = COOLDOWN - (now_ts - last)
        if remaining > 0:
            await ctx.send(embed=warn(
                f"⏳ Linh Thú còn mệt, chưa hiện hình! Còn **{remaining:.0f}s**."
            )); return

        tag = the_loai.strip().lower() if the_loai else random.choice(WAIFU_TAGS)
        if tag not in WAIFU_TAGS:
            tag = random.choice(WAIFU_TAGS)

        loading = await ctx.send("🖼️ *Đang triệu hình Linh Thú Đồ...*")

        image_url = None
        source_tag = tag
        try:
            params = {"included_tags": tag, "is_nsfw": "false"}
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    WAIFU_URL, params=params, timeout=aiohttp.ClientTimeout(total=8)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        images = data.get("images") or []
                        if images:
                            image_url = images[0].get("url")
        except Exception:
            image_url = None

        if not image_url:
            await loading.delete()
            await ctx.send(embed=warn("❌ Linh Thú trốn mất, không hiện hình được! Thử lại sau."))
            return

        self._linhthudo_cooldowns[uid] = now_ts

        player = await self.bot.db.get_player(ctx.author.id)
        ri = int(_safe(player, "realm_index", 0))

        embed = discord.Embed(
            title="🖼️ LINH THÚ ĐỒ — KHOE CẢNH GIỚI",
            description=(
                f"**{ctx.author.display_name}** triệu hình một bức Linh Thú Đồ "
                f"để mừng cảnh giới tu vi hiện tại!\n\n"
                f"🏷️ Chủ đề: `{source_tag}`"
            ),
            color=realm_color(ri)
        )
        embed.set_image(url=image_url)
        embed.set_footer(text="Chủ đề: waifu / maid / uniform / selfies • Hồi chiêu 30s • Thiên Cơ Các")
        await loading.delete()
        await ctx.send(embed=embed)

    # ══════════════════════════════════════════════════════════
    # HƯỚNG DẪN
    # ══════════════════════════════════════════════════════════
    @commands.command(name="thiencoc", aliases=["mystic_info", "tcc"])
    async def thiencoc(self, ctx):
        """📖 Hướng dẫn các lệnh Thiên Cơ Các"""
        embed = discord.Embed(title="🔮 THIÊN CƠ CÁC — HƯỚNG DẪN", color=0x6B48FF)
        embed.add_field(
            name="🔮 Thiên Cơ Bất Khả Lộ (`,tl thienco`)",
            value="Hé lộ 1 câu lời khuyên huyền bí mỗi ngày, có thưởng theo streak.",
            inline=False
        )
        embed.add_field(
            name="⚜️ Triệu Hồi Hộ Pháp (`,tl trieuhoi`)",
            value="Triệu hồi 1 vị Hộ Pháp/Linh Sứ ngẫu nhiên (nhân vật anime) hộ trì. CD 60s.",
            inline=False
        )
        embed.add_field(
            name="🖼️ Linh Thú Đồ (`,tl linhthudo [tag]`)",
            value=(
                "Rút 1 bức ảnh minh họa để khoe đột phá cảnh giới.\n"
                f"Tag: `{', '.join(WAIFU_TAGS)}`. CD 30s."
            ),
            inline=False
        )
        embed.set_footer(text="Thiên Cơ Các • Tu Tiên Bot")
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Mystic(bot))

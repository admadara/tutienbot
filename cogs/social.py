"""cogs/social.py - Tặng đồ, nhật ký v3"""
import discord
from discord.ext import commands
import time

from utils.helpers import require_player, now
from utils.embeds import *
from utils.game_data import ITEMS, get_realm_name, fmt_number

class Social(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Lưu nhật ký in-memory (top 50 sự kiện gần nhất mỗi server)
        self._diary: dict = {}  # guild_id -> [(time, user, action), ...]

    def _log(self, guild_id, user_name, action):
        key = str(guild_id)
        if key not in self._diary:
            self._diary[key] = []
        self._diary[key].insert(0, (now(), user_name, action))
        self._diary[key] = self._diary[key][:50]

    # ── ,tl give @người [item] [sl] ──────────────────────
    @commands.command(name="give", aliases=["tang","tango","cho_do"])
    async def give(self, ctx, target: discord.Member = None, item_id: str = None, quantity: int = 1):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        if not target or not item_id:
            await ctx.send(embed=warn("Dùng: `,tl give @người [item_id] [số lượng]`")); return
        if target.id == ctx.author.id:
            await ctx.send(embed=warn("Không thể tặng đồ cho chính mình!")); return
        if target.bot:
            await ctx.send(embed=warn("Không thể tặng cho bot!")); return

        item_id = item_id.lower()
        item = ITEMS.get(item_id)
        if not item:
            await ctx.send(embed=error(f"Không tìm thấy vật phẩm `{item_id}`!")); return

        quantity = max(1, min(quantity, 999))
        have = await self.bot.db.get_item_count(ctx.author.id, item_id)
        if have < quantity:
            await ctx.send(embed=error(f"Không đủ! Có **{have}x**, cần **{quantity}x**")); return

        receiver = await self.bot.db.get_player(target.id)
        if not receiver:
            await ctx.send(embed=error(f"**{target.display_name}** chưa nhập môn!")); return

        await self.bot.db.remove_item(ctx.author.id, item_id, quantity)
        await self.bot.db.add_item(target.id, item_id, quantity)

        self._log(ctx.guild.id, player["name"], f"tặng {quantity}x {item['name']} cho {receiver['name']}")

        embed = success("🎁 TẶNG ĐỒ THÀNH CÔNG!")
        embed.description = (
            f"**{player['name']}** ➜ **{receiver['name']}**\n"
            f"📦 **{quantity}x {item['name']}**"
        )
        embed.set_footer(text="Lan tỏa yêu thương trong giới tu tiên! 💕")
        await ctx.send(embed=embed)

    # ── ,tl doi_lt @người [số] ────────────────────────────
    @commands.command(name="doi_lt", aliases=["chuyen_lt","transfer"])
    async def doi_lt(self, ctx, target: discord.Member = None, amount: int = 0):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        if not target or amount <= 0:
            await ctx.send(embed=warn("Dùng: `,tl doi_lt @người [số Hạ LT]`")); return
        if target.id == ctx.author.id:
            await ctx.send(embed=warn("Không thể chuyển cho chính mình!")); return

        if player["linh_thach_ha"] < amount:
            await ctx.send(embed=error(f"Không đủ Hạ LT! Có {player['linh_thach_ha']:,}")); return

        receiver = await self.bot.db.get_player(target.id)
        if not receiver:
            await ctx.send(embed=error(f"**{target.display_name}** chưa nhập môn!")); return

        # Thuế chuyển khoản 5%
        tax = max(1, int(amount * 0.05))
        net = amount - tax

        await self.bot.db.update_player(ctx.author.id, linh_thach_ha=player["linh_thach_ha"] - amount)
        await self.bot.db.update_player(target.id, linh_thach_ha=receiver["linh_thach_ha"] + net)

        self._log(ctx.guild.id, player["name"], f"chuyển {amount:,} Hạ LT cho {receiver['name']}")

        embed = success("💰 CHUYỂN LINH THẠCH THÀNH CÔNG!")
        embed.add_field(name="💸 Gửi",    value=f"{amount:,} Hạ LT",  inline=True)
        embed.add_field(name="💸 Thuế",   value=f"-{tax:,} Hạ (5%)",  inline=True)
        embed.add_field(name="💰 Nhận",   value=f"{net:,} Hạ LT",     inline=True)
        embed.add_field(name="👤 Người Nhận", value=receiver["name"], inline=False)
        await ctx.send(embed=embed)

    # ── ,tl diary ─────────────────────────────────────────
    @commands.command(name="diary", aliases=["nhat_ky","nhatky","log"])
    async def diary(self, ctx):
        key    = str(ctx.guild.id) if ctx.guild else "dm"
        events = self._diary.get(key, [])

        embed = discord.Embed(title="📖 NHẬT KÝ THIÊN ĐẠO", color=0x607D8B)
        if not events:
            embed.description = "_Chưa có hoạt động nào được ghi nhận._"
        else:
            lines = []
            for ts, uname, action in events[:15]:
                t = time.strftime("%H:%M", time.localtime(ts))
                lines.append(f"`{t}` **{uname}** {action}")
            embed.description = "\n".join(lines)
        embed.set_footer(text="Hiển thị 15 sự kiện gần nhất  •  Tu Tiên Bot v3")
        await ctx.send(embed=embed)

    # ── ,tl tuvi ──────────────────────────────────────────
    @commands.command(name="so_sanh", aliases=["compare","vs"])
    async def so_sanh(self, ctx, target: discord.Member = None):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        if not target:
            await ctx.send(embed=warn("Dùng: `,tl vs @người`")); return
        if target.bot:
            await ctx.send(embed=warn("Không thể so sánh với bot!")); return

        other = await self.bot.db.get_player(target.id)
        if not other:
            await ctx.send(embed=error(f"**{target.display_name}** chưa nhập môn!")); return

        A = player; B = other
        from utils.embeds import fmt, realm_color
        from utils.game_data import get_realm_name

        def cmp(a, b):
            if a > b: return "🟢"
            if a < b: return "🔴"
            return "🟡"

        lc_a = A.get("luc_chien", A["atk"])
        lc_b = B.get("luc_chien", B["atk"])

        embed = discord.Embed(
            title=f"⚔️ SO SÁNH: {A['name']} vs {B['name']}",
            color=0x9C27B0
        )
        embed.add_field(
            name=f"👤 {A['name']}",
            value=(
                f"🌌 {get_realm_name(A)}\n"
                f"⚔️ Lực chiến: `{fmt(lc_a)}`\n"
                f"🗡️ ATK: `{fmt(A['atk'])}`\n"
                f"🛡️ DEF: `{fmt(A.get('def_',50))}`\n"
                f"❤️ HP: `{fmt(A['hp_max'])}`\n"
                f"💥 CRIT: `{A['crit']:.1f}%`"
            ),
            inline=True
        )
        embed.add_field(
            name=f"👤 {B['name']}",
            value=(
                f"🌌 {get_realm_name(B)}\n"
                f"⚔️ Lực chiến: `{fmt(lc_b)}`\n"
                f"🗡️ ATK: `{fmt(B['atk'])}`\n"
                f"🛡️ DEF: `{fmt(B.get('def_',50))}`\n"
                f"❤️ HP: `{fmt(B['hp_max'])}`\n"
                f"💥 CRIT: `{B['crit']:.1f}%`"
            ),
            inline=True
        )
        embed.add_field(
            name="📊 Kết Quả",
            value=(
                f"{cmp(lc_a,lc_b)} Lực chiến: `{fmt(lc_a)}` vs `{fmt(lc_b)}`\n"
                f"{cmp(A['atk'],B['atk'])} ATK\n"
                f"{cmp(A.get('def_',50),B.get('def_',50))} DEF\n"
                f"{cmp(A['hp_max'],B['hp_max'])} HP\n"
                f"{cmp(A['realm_index'],B['realm_index'])} Cảnh Giới"
            ),
            inline=False
        )
        winner = A['name'] if lc_a >= lc_b else B['name']
        embed.set_footer(text=f"🏆 Lực chiến cao hơn: {winner}  •  Tu Tiên Bot v3")
        await ctx.send(embed=embed)

    # ── ,tl co_do ─────────────────────────────────────────
    @commands.command(name="co_do", aliases=["xem_co_do","cd"])
    async def co_do(self, ctx, target: discord.Member = None):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        """Xem hồ sơ người khác"""
        if not target:
            await ctx.send(embed=warn("Dùng: `,tl co_do @người`")); return
        other = await self.bot.db.get_player(target.id)
        if not other:
            await ctx.send(embed=error(f"**{target.display_name}** chưa nhập môn!")); return

        from utils.embeds import fmt, realm_color, realm_icon, bar, fmt_lt
        from utils.game_data import get_realm_name, get_exp_req, DAO

        ri      = other["realm_index"]
        exp_req = get_exp_req(other)
        dao     = DAO.get(other.get("dao",""), {"name":"?","icon":"❓"})

        embed = discord.Embed(color=realm_color(ri))
        embed.set_author(
            name=f"{realm_icon(ri)} {other['name']}",
            icon_url=target.display_avatar.url
        )
        embed.add_field(name="🌌 Cảnh Giới",  value=f"`{get_realm_name(other)}`",          inline=True)
        embed.add_field(name=f"{dao['icon']} Đạo", value=f"`{dao['name']}`",               inline=True)
        embed.add_field(name="⚔️ Lực Chiến",  value=f"`{fmt(other.get('luc_chien',0))}`", inline=True)
        embed.add_field(name="✨ Linh Căn",   value=f"`{other.get('linh_can','?')}`",      inline=True)
        embed.add_field(name="💪 Thể Chất",   value=f"`{other.get('the_chat','?')}`",      inline=True)
        embed.add_field(name="🩸 Huyết Mạch", value=f"`{other.get('huyet_mach','?')}`",   inline=True)
        embed.add_field(
            name="⚡ Tiến Độ EXP",
            value=f"{bar(other['exp'], exp_req, 16)}\n`{fmt(other['exp'])}/{fmt(exp_req)}`",
            inline=False
        )
        embed.set_footer(text=f"Hồ sơ của {other['name']}  •  Tu Tiên Bot v3")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Social(bot))

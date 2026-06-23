"""cogs/market.py - Kinh tế nâng cao: ngân hàng, cho vay, lãi suất"""
import discord
from discord.ext import commands
import time

from utils.helpers import require_player, now
from utils.embeds import *
from utils.persistent_cache import PersistentCache

def _s(n):
    return fmt(n)

def _safe(p,k,d=0):
    v=p.get(k); return v if v is not None else d

class Market(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._loans = PersistentCache(bot, "market_loans")  # uid -> {amount, due, interest}

    async def cog_load(self):
        await self._loans.load()

    async def cog_unload(self):
        await self._loans.save()

    @commands.command(name="ngan_hang", aliases=["nganhang","bank","nh"])
    async def ngan_hang(self, ctx):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        loan = self._loans.get(str(ctx.author.id))
        embed = discord.Embed(title="🏦 NGÂN HÀNG THIÊN ĐẠO", color=0x2196F3)
        embed.set_author(name=player["name"], icon_url=ctx.author.display_avatar.url)
        embed.add_field(
            name="💰 Số Dư",
            value=(
                f"💰 {_safe(player,'linh_thach_ha'):,} Hạ\n"
                f"💎 {_safe(player,'linh_thach_trung'):,} Trung\n"
                f"👑 {_safe(player,'linh_thach_cuc'):,} Cực"
            ),
            inline=True
        )
        if loan:
            due_in = loan["due"] - now()
            embed.add_field(
                name="⚠️ Khoản Vay Hiện Tại",
                value=(
                    f"Nợ: **{loan['amount']:,} Hạ**\n"
                    f"Lãi: {loan['interest']*100:.0f}%\n"
                    f"Hạn: `{fmt_time(max(0,due_in))}` {'⚠️ QUÁ HẠN!' if due_in<0 else ''}"
                ),
                inline=True
            )
        embed.add_field(name="📋 Lệnh", value=(
            "`,tl vay [số]` — Vay Linh Thạch (lãi 10%)\n"
            "`,tl tra_no` — Trả nợ\n"
            "`,tl doi [tier] [sl]` — Quy đổi LT\n"
            "`,tl lich_su` — Lịch sử giao dịch"
        ), inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="vay", aliases=["borrow","loan"])
    async def vay(self, ctx, amount: int = 0):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        if amount <= 0:
            await ctx.send(embed=warn("Dùng: `,tl vay [số Hạ LT]`")); return

        uid = str(ctx.author.id)
        if uid in self._loans:
            await ctx.send(embed=warn("Đang còn nợ! Trả nợ trước (`,tl tra_no`)")); return

        # Giới hạn vay theo realm
        ri     = player["realm_index"]
        max_vay = (ri + 1) * 5000
        if amount > max_vay:
            await ctx.send(embed=warn(f"Tối đa vay **{max_vay:,} Hạ** (theo cảnh giới)!")); return
        if amount < 1000:
            await ctx.send(embed=warn("Vay tối thiểu **1,000 Hạ**!")); return

        interest = 0.10  # 10% lãi
        due_time = now() + 86400  # 24h

        self._loans[uid] = {
            "amount": int(amount * (1 + interest)),
            "due": due_time,
            "interest": interest,
        }
        await self.bot.db.update_player(ctx.author.id,
            linh_thach_ha=_safe(player,"linh_thach_ha")+amount)

        embed = success("✅ VAY THÀNH CÔNG!")
        embed.description = (
            f"💰 Nhận: **+{amount:,} Hạ LT**\n"
            f"💸 Phải trả: **{int(amount*(1+interest)):,} Hạ** (lãi {interest*100:.0f}%)\n"
            f"⏰ Hạn: **24 giờ**\n\n"
            f"⚠️ Quá hạn sẽ bị phạt thêm 20%!"
        )
        await ctx.send(embed=embed)

    @commands.command(name="tra_no", aliases=["repay","traNo","traNg"])
    async def tra_no(self, ctx):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        uid  = str(ctx.author.id)
        loan = self._loans.get(uid)
        if not loan:
            await ctx.send(embed=warn("Không có khoản nợ nào!")); return

        debt = loan["amount"]
        # Phạt nếu quá hạn
        if now() > loan["due"]:
            penalty = int(debt * 0.20)
            debt   += penalty
            embed_title = f"⚠️ QUÁ HẠN! Phạt thêm {penalty:,} Hạ"
        else:
            embed_title = "✅ TRẢ NỢ THÀNH CÔNG"

        if _safe(player,"linh_thach_ha") < debt:
            await ctx.send(embed=error(f"Không đủ LT! Cần **{debt:,} Hạ**, có **{_safe(player,'linh_thach_ha'):,} Hạ**")); return

        del self._loans[uid]
        await self.bot.db.update_player(ctx.author.id,
            linh_thach_ha=_safe(player,"linh_thach_ha")-debt)

        embed = success(embed_title)
        embed.description = f"💸 Đã trả **{debt:,} Hạ LT**"
        await ctx.send(embed=embed)

    @commands.command(name="lich_su", aliases=["history","lichsu","ls_trade"])
    async def lich_su(self, ctx):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        """Lịch sử giao dịch đấu giá"""
        rows = await self.bot.db.fetchall(
            "SELECT * FROM auction WHERE seller_id=? ORDER BY listed_at DESC LIMIT 10",
            (str(ctx.author.id),)
        )
        embed = discord.Embed(title="📋 LỊCH SỬ GIAO DỊCH", color=0x607D8B)
        embed.set_author(name=player["name"], icon_url=ctx.author.display_avatar.url)
        if not rows:
            embed.description = "_Chưa có giao dịch nào._"
        else:
            from utils.game_data import ITEMS
            for r in rows:
                iname = ITEMS.get(r["item_id"],{}).get("name",r["item_id"])
                status_icon = {"active":"🟡","sold":"✅","expired":"❌","cancelled":"🔴"}.get(r["status"],"?")
                t = time.strftime("%d/%m %H:%M", time.localtime(r["listed_at"]))
                embed.add_field(
                    name=f"{status_icon} {iname} ×{r['quantity']}",
                    value=f"💰 {r['price']:,} Hạ | {t} | `{r['status']}`",
                    inline=False
                )
        await ctx.send(embed=embed)

    @commands.command(name="gia_ca", aliases=["giaca","price_check","gia"])
    async def gia_ca(self, ctx, item_id: str = None):
        """Kiểm tra giá thị trường của vật phẩm"""
        from utils.game_data import ITEMS
        if not item_id:
            await ctx.send(embed=warn("Dùng: `,tl gia [item_id]`")); return
        item_id = item_id.lower()
        item = ITEMS.get(item_id)
        if not item:
            await ctx.send(embed=error(f"Không tìm thấy `{item_id}`!")); return

        # Giá chợ đấu giá
        rows = await self.bot.db.fetchall(
            "SELECT price FROM auction WHERE item_id=? AND status='active' ORDER BY price ASC LIMIT 5",
            (item_id,)
        )
        base_price = item.get("price",0)

        embed = discord.Embed(title=f"💹 GIÁ CẢ — {item['name']}", color=0xFF9800)
        embed.add_field(name="🏪 Giá Shop",   value=f"{base_price:,} Hạ" if base_price else "Không bán", inline=True)
        embed.add_field(name="📋 Trần Đấu Giá",value=f"{base_price*50:,} Hạ" if base_price else "N/A", inline=True)
        if rows:
            prices = [r["price"] for r in rows]
            embed.add_field(
                name="🏛️ Đang Bán (Chợ P2P)",
                value="\n".join(f"💰 {p:,} Hạ" for p in prices),
                inline=False
            )
        else:
            embed.add_field(name="🏛️ Chợ P2P", value="_Không có người bán_", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="top_giau", aliases=["topgiau","rich_list","richlist"])
    async def top_giau(self, ctx, pham_vi: str = None):
        """Top 10 người giàu nhất (mặc định theo server, dùng `all` để xem toàn cục)"""
        is_global = pham_vi and pham_vi.lower() in ("all", "global", "toancau")
        if is_global or not ctx.guild:
            rows = await self.bot.db.fetchall(
                "SELECT * FROM players ORDER BY (linh_thach_cuc*1000000 + linh_thach_trung*1000 + linh_thach_ha) DESC LIMIT 10"
            )
        else:
            rows = await self.bot.db.fetchall(
                "SELECT * FROM players WHERE guild_id=? "
                "ORDER BY (linh_thach_cuc*1000000 + linh_thach_trung*1000 + linh_thach_ha) DESC LIMIT 10",
                (str(ctx.guild.id),)
            )
        title = "💰 TOP GIÀU NHẤT" + (" (Toàn Server Bot)" if is_global else "")
        embed = discord.Embed(title=title, color=0xFFD700)
        medals = ["🥇","🥈","🥉"]+["🏅"]*7
        for i,p in enumerate(rows):
            total_ha = _safe(p,"linh_thach_cuc")*1e6 + _safe(p,"linh_thach_trung")*1000 + _safe(p,"linh_thach_ha")
            embed.add_field(
                name=f"{medals[i]} {p['name']}",
                value=(
                    f"👑 {_safe(p,'linh_thach_cuc'):,} Cực | "
                    f"💎 {_safe(p,'linh_thach_trung'):,} Trung | "
                    f"💰 {_safe(p,'linh_thach_ha'):,} Hạ"
                ),
                inline=False
            )
        if not rows:
            embed.description = "_Chưa có người chơi trong server này._" if not is_global else "_Chưa có người chơi._"
        embed.set_footer(text=",tl top_giau [all]  •  Tu Tiên Bot v4")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Market(bot))

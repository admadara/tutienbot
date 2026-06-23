"""cogs/luyen_dan.py - Luyện Đan v3"""
import discord
from discord.ext import commands
import random
from utils.helpers import require_player, require_idle
from utils.embeds import *
from utils.game_data import DAN_RECIPES, ITEMS

class LuyenDan(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @commands.group(name="luyen_dan", aliases=["luyendan","ld","dan"], invoke_without_command=True)
    async def luyen_dan(self, ctx):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        embed = discord.Embed(title="⚗️ LÒ LUYỆN ĐAN", color=0xFF6F00)
        embed.description = (
            "Luyện đan từ nguyên liệu để nhận đan dược chất lượng cao!\n\n"
            "`,tl luyendan cong_thuc` - Xem công thức\n"
            "`,tl luyendan luyen [dan_id]` - Luyện đan"
        )
        embed.add_field(name="📦 Nguyên Liệu Cơ Bản", value=(
            "`linh_thao` - Linh Thảo (Tầng 1)\n"
            "`hoa_tinh` - Hỏa Tinh Thảo (Tầng 2)\n"
            "`thien_nhan` - Thiên Nhẫn Hoa (Tầng 3)\n"
            "`long_khi_tuong` - Long Khí Tượng (Tầng 4)\n"
            "`hon_don_tinh` - Hỗn Độn Tinh Thạch (Tầng 5)"
        ), inline=False)
        await ctx.send(embed=embed)

    @luyen_dan.command(name="cong_thuc", aliases=["congthuc","recipe","ct"])
    async def cong_thuc(self, ctx):
        embed = discord.Embed(title="📜 CÔNG THỨC LUYỆN ĐAN", color=0xFF6F00)
        for rid, recipe in DAN_RECIPES.items():
            ing_str = "  +  ".join(
                f"`{ITEMS.get(k,{}).get('name',k)}` ×{v}"
                for k,v in recipe["ingredients"].items()
            )
            embed.add_field(
                name=f"Tầng {recipe['tier']} — **{recipe['name']}** (ID: `{rid}`)",
                value=(
                    f"📦 {ing_str}\n"
                    f"🎯 Tỉ lệ: **{recipe['success']*100:.0f}%**  •  "
                    f"Nhận: **{recipe['result']}x {recipe['name']}**"
                ),
                inline=False
            )
        embed.set_footer(text=",tl luyendan luyen [id] để luyện đan")
        await ctx.send(embed=embed)

    @luyen_dan.command(name="luyen", aliases=["craft","make"])
    async def luyen(self, ctx, dan_id: str = None, so_luong: int = 1):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        if not dan_id:
            await ctx.send(embed=warn("Dùng: `,tl luyendan luyen [dan_id] [số lượng]`\nXem CT: `,tl luyendan congthuc`"))
            return
        dan_id = dan_id.lower()
        recipe = DAN_RECIPES.get(dan_id)
        if not recipe:
            await ctx.send(embed=error(f"Không có công thức `{dan_id}`!\nXem: `,tl luyendan congthuc`"))
            return

        so_luong = max(1, min(so_luong, 10))
        # Kiểm tra nguyên liệu
        missing = []
        for iid, qty in recipe["ingredients"].items():
            have = await self.bot.db.get_item_count(ctx.author.id, iid)
            need = qty * so_luong
            if have < need:
                iname = ITEMS.get(iid,{}).get("name",iid)
                missing.append(f"❌ {iname}: có `{have}`, cần `{need}`")
        if missing:
            embed = error(f"Thiếu nguyên liệu để luyện {so_luong}x **{recipe['name']}**!\n\n" + "\n".join(missing))
            await ctx.send(embed=embed); return

        # Trừ nguyên liệu
        for iid, qty in recipe["ingredients"].items():
            await self.bot.db.remove_item(ctx.author.id, iid, qty * so_luong)

        # Luyện
        success_count = 0
        fail_count = 0
        for _ in range(so_luong):
            if random.random() < recipe["success"]:
                success_count += 1
            else:
                fail_count += 1

        total_dan = success_count * recipe["result"]
        if total_dan > 0:
            await self.bot.db.add_item(ctx.author.id, dan_id, total_dan)

        color = 0x4CAF50 if success_count > fail_count else 0xFF9800
        embed = discord.Embed(
            title="⚗️ KẾT QUẢ LUYỆN ĐAN",
            color=color
        )
        embed.add_field(name="💊 Đan Dược", value=f"**{recipe['name']}**", inline=True)
        embed.add_field(name="🔄 Luyện",    value=f"{so_luong} lần",        inline=True)
        embed.add_field(name="✅ Thành",     value=f"{success_count} lần",  inline=True)
        embed.add_field(name="❌ Thất",      value=f"{fail_count} lần",     inline=True)
        embed.add_field(name="🎁 Nhận Được",value=f"**{total_dan}x** {recipe['name']}", inline=False)
        embed.set_footer(text=f"Tỉ lệ thành công: {recipe['success']*100:.0f}%")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(LuyenDan(bot))

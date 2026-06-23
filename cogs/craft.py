"""cogs/craft.py - Chế tạo & Luyện Kim v4"""
import discord
from discord.ext import commands
import random

from utils.helpers import require_player, require_idle, now
from utils.embeds import *
from utils.game_data import ITEMS, get_realm_name

def _s(n):
    return fmt(n)

def _safe(p,k,d=0):
    v=p.get(k); return v if v is not None else d

# Công thức chế tạo
CRAFT_RECIPES = {
    "1": {
        "name":"⚔️ Sát Tiên Kiếm","type":"vukhi","slot":"weapon",
        "ingredients":{"301":10,"401":2},
        "base_atk":600,"success":0.90,"realm_min":1,
        "desc":"Kiếm luyện từ Linh Thảo và Hồng Ngọc"
    },
    "2": {
        "name":"⚔️ Thần Long Kiếm","type":"vukhi","slot":"weapon",
        "ingredients":{"302":15,"402":3,"301":5},
        "base_atk":2500,"success":0.75,"realm_min":3,
        "desc":"Kiếm chứa Long Khí, sắc bén vô song"
    },
    "3": {
        "name":"⚔️ Khai Thiên Phủ","type":"vukhi","slot":"weapon",
        "ingredients":{"304":5,"303":10,"405":2},
        "base_atk":9000,"success":0.55,"realm_min":6,
        "desc":"Phủ trảm phá thiên địa, uy lực kinh hồn"
    },
    "4": {
        "name":"🛡️ Tiên Hoàng Giáp","type":"giap","slot":"armor",
        "ingredients":{"302":20,"402":5},
        "base_def":7000,"success":0.65,"realm_min":5,
        "desc":"Giáp luyện từ tinh anh tiên giới"
    },
    "5": {
        "name":"🔮 Bàn Cổ Thần Ấn","type":"phap_bao","slot":"phapbao",
        "ingredients":{"305":3,"304":8,"405":3},
        "base_atk":6000,"base_def":2500,"success":0.40,"realm_min":10,
        "desc":"Pháp bảo cổ đại chứa sức mạnh tạo hóa"
    },
    "6": {
        "name":"💊 Phục Tinh Đan (×5)","type":"dan_duoc",
        "ingredients":{"301":8},
        "stamina":50,"success":0.95,"realm_min":0,
        "desc":"Luyện từ Linh Thảo, hồi phục thể lực"
    },
    "7": {
        "name":"💊 Đại Hoàn Đan (×3)","type":"dan_duoc",
        "ingredients":{"302":5,"301":3},
        "stamina":200,"success":0.80,"realm_min":2,
        "desc":"Đại hoàn đan hồi phục toàn bộ thể lực"
    },
}

class Craft(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @commands.group(name="cheta", aliases=["craft","luyen_kim","ct"], invoke_without_command=True)
    async def cheta(self, ctx):
        embed = discord.Embed(title="⚒️ XE LUYỆN KIM — CHẾ TẠO", color=0x795548)
        embed.description = (
            "Dùng nguyên liệu để chế tạo trang bị và đan dược!\n\n"
            "`,tl cheta congthuc` — Xem công thức\n"
            "`,tl cheta lam [id]` — Chế tạo\n"
            "`,tl cheta nguyen_lieu` — Nguyên liệu cần thiết\n\n"
            "💡 Nguyên liệu mua tại `,tl shop nguyen_lieu`"
        )
        await ctx.send(embed=embed)

    @cheta.command(name="congthuc", aliases=["recipe","ct_list","xem"])
    async def congthuc(self, ctx):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        ri = player["realm_index"]
        embed = discord.Embed(title="📜 CÔNG THỨC CHẾ TẠO", color=0x795548)
        for rid, r in CRAFT_RECIPES.items():
            locked = ri < r.get("realm_min",0)
            icon   = "🔒" if locked else "✅"
            ing    = " + ".join(
                f"{ITEMS.get(k,{}).get('name',k)}×{v}"
                for k,v in r["ingredients"].items()
            )
            embed.add_field(
                name=f"{icon} `{rid}` — {r['name']}",
                value=(
                    f"📦 {ing}\n"
                    f"🎯 Tỉ lệ: **{r['success']*100:.0f}%**"
                    + (f" | 🔒 Cần: {ITEMS.get(rid,{}).get('name','') or ''}" if locked else "")
                ),
                inline=False
            )
        embed.set_footer(text=",tl cheta lam [id] để chế tạo  •  Tu Tiên Bot v3")
        await ctx.send(embed=embed)

    @cheta.command(name="lam", aliases=["make","create","chế"])
    async def lam(self, ctx, recipe_id: str = None, so_luong: int = 1):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        if not recipe_id:
            await ctx.send(embed=warn("Dùng: `,tl cheta lam [id] [số lượng]`\nXem: `,tl cheta congthuc`")); return
        rid = recipe_id.lower().replace(" ","_")
        r   = CRAFT_RECIPES.get(rid)
        if not r:
            await ctx.send(embed=error(f"Không có công thức `{rid}`!")); return
        if player["realm_index"] < r.get("realm_min",0):
            from utils.game_data import REALMS
            need = REALMS[r["realm_min"]]["name"]
            await ctx.send(embed=error(f"Cần **{need}** để chế tạo!")); return

        so_luong = max(1, min(so_luong, 5))
        # Kiểm tra nguyên liệu
        missing = []
        for iid, qty in r["ingredients"].items():
            have = await self.bot.db.get_item_count(ctx.author.id, iid)
            need = qty * so_luong
            if have < need:
                missing.append(f"❌ {ITEMS.get(iid,{}).get('name',iid)}: có `{have}`, cần `{need}`")
        if missing:
            await ctx.send(embed=error(
                f"Thiếu nguyên liệu cho **{so_luong}x {r['name']}**!\n" + "\n".join(missing)
            )); return

        # Trừ nguyên liệu
        for iid, qty in r["ingredients"].items():
            await self.bot.db.remove_item(ctx.author.id, iid, qty * so_luong)

        # Chế tạo
        ok = fail = 0
        for _ in range(so_luong):
            if random.random() < r["success"]: ok += 1
            else: fail += 1

        # Thêm vào túi/mặc vào
        result_lines = []
        if ok > 0:
            if r["type"] in ("vukhi","giap","phap_bao","mu","vongco","gangtay","giay"):
                # Trang bị - thêm vào túi
                item_data = {
                    "name": r["name"], "type": r["type"],
                    "slot": r.get("slot","weapon"),
                    "price": 0,
                    "base_atk": r.get("base_atk",0),
                    "base_def": r.get("base_def",0),
                }
                # Tạo item_id tạm
                fake_id = f"craft_{rid}_{int(now())%10000}"
                # Lưu vào ITEMS động (chỉ trong session)
                ITEMS[fake_id] = item_data
                await self.bot.db.add_item(ctx.author.id, fake_id, ok)
                result_lines.append(f"🎁 +**{ok}x {r['name']}** → túi đồ")
                result_lines.append(f"_(Dùng `,tl mac {fake_id}` để mặc)_")
            elif r["type"] == "dan_duoc":
                # Đan dược - thêm thẳng loại gốc
                target_id = rid.replace("_ct","")
                qty_per   = 5 if "5" in r["name"] else (3 if "3" in r["name"] else 1)
                await self.bot.db.add_item(ctx.author.id, target_id, ok * qty_per)
                result_lines.append(f"💊 +**{ok*qty_per}x {r['name'].split('(')[0].strip()}**")

        embed = discord.Embed(
            title=f"⚒️ CHẾ TẠO {r['name']}",
            color=0x4CAF50 if ok else 0xF44336
        )
        embed.add_field(name="✅ Thành Công", value=f"**{ok}**/{so_luong}", inline=True)
        embed.add_field(name="❌ Thất Bại",   value=f"**{fail}**/{so_luong}", inline=True)
        embed.add_field(name="🎁 Kết Quả",    value="\n".join(result_lines) or "_không có_", inline=False)
        embed.set_footer(text=f"Tỉ lệ: {r['success']*100:.0f}%  •  Tu Tiên Bot v3")
        await ctx.send(embed=embed)

    @cheta.command(name="nguyen_lieu", aliases=["materials","nl"])
    async def nguyen_lieu(self, ctx):
        embed = discord.Embed(title="🌿 NGUYÊN LIỆU CHẾ TẠO", color=0x4CAF50)
        mats = {
            "301":     ("Linh Thảo",         "Tầng 1-2 bí cảnh, shop 200 Hạ"),
            "302":      ("Hỏa Tinh Thảo",     "Tầng 3-5 bí cảnh, shop 800 Hạ"),
            "303":    ("Thiên Nhẫn Hoa",    "Tầng 5-9 bí cảnh, shop 3K Hạ"),
            "304":("Long Khí Tượng",    "Tầng 9+ bí cảnh, shop 15K Hạ"),
            "305":  ("Hỗn Độn Tinh Thạch","Hỗn Độn Hư Không, shop 100K Hạ"),
            "401":     ("Hồng Ngọc",         "Shop ngọc 5K Hạ"),
            "402":      ("Lam Ngọc",          "Shop ngọc 5K Hạ"),
            "405":     ("Thần Ngọc",         "Shop ngọc 50K Hạ"),
        }
        for iid, (name, source) in mats.items():
            embed.add_field(name=f"`{iid}` — {name}", value=source, inline=True)
        embed.set_footer(text=",tl shop nguyen_lieu  •  Tu Tiên Bot v3")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Craft(bot))

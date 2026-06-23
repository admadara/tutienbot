"""cogs/shop_extra.py - Reroll đặc tính, xem ngọc, lệnh bổ sung v3"""
import discord
from discord.ext import commands
import random

from utils.helpers import require_player, require_idle, now
from utils.embeds import *
from utils.game_data import ITEMS, RARITY_EMOJI

class ShopExtra(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.command(name="ngoc", aliases=["xem_ngoc","gems"])
    async def ngoc(self, ctx):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        import json
        equip = await self.bot.db.get_equipment(ctx.author.id)
        SLOTS = [("weapon","⚔️"),("armor","🛡️"),("hat","🪖"),
                 ("necklace","📿"),("gloves","🧤"),("boots","👟"),("phapbao","🔮")]

        embed = discord.Embed(title="💎 NGỌC KHẢM", color=0x9C27B0)
        has_gems = False
        for slot, em in SLOTS:
            if slot not in equip: continue
            e    = equip[slot]
            gems = json.loads(e.get("gems") or "[]")
            itm  = ITEMS.get(e["item_id"], {})
            iname = itm.get("name", e["item_id"])
            if gems:
                has_gems = True
                gem_str = "  ".join(f"`{ITEMS.get(g,{}).get('name',g)}`" for g in gems)
                embed.add_field(name=f"{em} {iname} (+{e['enhance']})", value=gem_str, inline=False)

        if not has_gems:
            embed.description = "_Chưa có ngọc nào được khảm._\nMua ngọc tại `,tl shop ngoc`"
        embed.set_footer(text=",tl kham [slot] [ngoc_id] — Khảm ngọc vào trang bị")
        await ctx.send(embed=embed)

    # ── ,tl kham [slot] [ngoc_id] ────────────────────────
    @commands.command(name="kham", aliases=["insert_gem","khamnhoc"])
    async def kham(self, ctx, slot: str = None, ngoc_id: str = None):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        import json
        if not slot or not ngoc_id:
            await ctx.send(embed=warn("Dùng: `,tl kham [slot] [ngoc_id]`\nSlot: weapon/armor/hat/necklace/gloves/boots/phapbao")); return

        SLOT_MAP = {"weapon":"weapon","vukhi":"weapon","armor":"armor","giap":"armor",
                    "hat":"hat","mu":"hat","necklace":"necklace","vongco":"necklace",
                    "gloves":"gloves","gangtay":"gloves","boots":"boots","giay":"boots","phapbao":"phapbao"}
        slot_id = SLOT_MAP.get(slot.lower(), slot.lower())
        equip   = await self.bot.db.get_equipment(ctx.author.id)

        if slot_id not in equip:
            await ctx.send(embed=error(f"Slot **{slot}** đang trống! Mặc trang bị vào trước.")); return

        ngoc_id = ngoc_id.lower()
        ngoc    = ITEMS.get(ngoc_id)
        if not ngoc or ngoc.get("type") != "ngoc":
            await ctx.send(embed=error(f"Không phải ngọc hợp lệ! Xem: `,tl shop ngoc`")); return

        have = await self.bot.db.get_item_count(ctx.author.id, ngoc_id)
        if have < 1:
            await ctx.send(embed=error(f"Không có **{ngoc['name']}** trong túi!")); return

        e     = equip[slot_id]
        gems  = json.loads(e.get("gems") or "[]")
        MAX_GEMS = 3
        if len(gems) >= MAX_GEMS:
            await ctx.send(embed=warn(f"Slot này đã đầy **{MAX_GEMS}** ngọc! Dùng `,tl thao_ngoc {slot}` để tháo.")); return

        gems.append(ngoc_id)
        await self.bot.db.execute(
            "UPDATE equipment SET gems=? WHERE user_id=? AND slot=?",
            (json.dumps(gems), str(ctx.author.id), slot_id)
        )
        await self.bot.db.remove_item(ctx.author.id, ngoc_id, 1)

        itm   = ITEMS.get(e["item_id"], {})
        bonus = []
        for k,v in ngoc.items():
            if k.endswith("_pct"): bonus.append(f"+{v*100:.0f}% {k.replace('_pct','').upper()}")
        embed = success("💎 KHẢM NGỌC THÀNH CÔNG!")
        embed.description = (
            f"Khảm **{ngoc['name']}** vào **{itm.get('name', e['item_id'])}**\n"
            f"Bonus: {', '.join(bonus)}\n"
            f"Ngọc đã khảm: {len(gems)}/{MAX_GEMS}"
        )
        await ctx.send(embed=embed)

    # ── ,tl thao_ngoc [slot] ─────────────────────────────
    @commands.command(name="thao_ngoc", aliases=["remove_gem","thao_da"])
    async def thao_ngoc(self, ctx, slot: str = None):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        import json
        if not slot:
            await ctx.send(embed=warn("Dùng: `,tl thao_ngoc [slot]`")); return

        SLOT_MAP = {"weapon":"weapon","vukhi":"weapon","armor":"armor","giap":"armor",
                    "hat":"hat","mu":"hat","necklace":"necklace","vongco":"necklace",
                    "gloves":"gloves","gangtay":"gloves","boots":"boots","giay":"boots","phapbao":"phapbao"}
        slot_id = SLOT_MAP.get(slot.lower(), slot.lower())
        equip   = await self.bot.db.get_equipment(ctx.author.id)

        if slot_id not in equip:
            await ctx.send(embed=error(f"Slot **{slot}** trống!")); return

        e    = equip[slot_id]
        gems = json.loads(e.get("gems") or "[]")
        if not gems:
            await ctx.send(embed=warn("Slot này chưa có ngọc nào!")); return

        # Hoàn lại tất cả ngọc, mất 10% ngẫu nhiên
        returned = []
        for g in gems:
            if random.random() > 0.10:  # 90% trả lại
                await self.bot.db.add_item(ctx.author.id, g, 1)
                returned.append(ITEMS.get(g, {}).get("name", g))

        await self.bot.db.execute(
            "UPDATE equipment SET gems='[]' WHERE user_id=? AND slot=?",
            (str(ctx.author.id), slot_id)
        )
        itm = ITEMS.get(e["item_id"], {})
        embed = success("🔧 THÁO NGỌC THÀNH CÔNG!")
        embed.description = (
            f"Tháo ngọc khỏi **{itm.get('name', e['item_id'])}**\n"
            f"Hoàn lại: {', '.join(returned) if returned else '_không có (vỡ)_'}\n"
            f"_(10% mỗi ngọc có thể vỡ khi tháo)_"
        )
        await ctx.send(embed=embed)

    # ── ,tl nap_the [mã] ─────────────────────────────────
    @commands.command(name="nap_the", aliases=["napthe","redeem","doi_ma"])
    async def nap_the(self, ctx, ma: str = None):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        if not ma:
            await ctx.send(embed=warn("Dùng: `,tl nap_the [mã code]`")); return
        # Placeholder - admin sẽ thêm code thật sau
        CODES = {
            "TUTIEN2024": {"ha": 10000, "used": False},
            "NEWPLAYER":  {"ha": 5000,  "trung": 1, "used": False},
        }
        code = CODES.get(ma.upper())
        if not code:
            await ctx.send(embed=error("Mã không hợp lệ hoặc đã hết hạn!")); return
        if code.get("used"):
            await ctx.send(embed=error("Mã đã được dùng rồi!")); return

        updates = {}
        rewards = []
        if code.get("ha"):
            updates["linh_thach_ha"] = player["linh_thach_ha"] + code["ha"]
            rewards.append(f"💰 +{code['ha']:,} Hạ LT")
        if code.get("trung"):
            updates["linh_thach_trung"] = player["linh_thach_trung"] + code["trung"]
            rewards.append(f"💎 +{code['trung']} Trung LT")

        await self.bot.db.update_player(ctx.author.id, **updates)
        code["used"] = True

        embed = success("🎉 NẠP MÃ THÀNH CÔNG!", "\n".join(rewards))
        await ctx.send(embed=embed)

    # ── ,tl tang_kinh / ,tl tkc ──────────────────────────────
    @commands.command(name="tang_kinh", aliases=["tkc","bikip","bi_kip","congphapmoi","shop_cp","tang_kinh_cac"])
    async def tang_kinh(self, ctx, page: int = 1):
        """📚 TÀNG KINH CÁC — Xem và mua Bí Kíp Công Pháp"""
        from utils.game_data import ITEMS
        bk_items = [(k, v) for k, v in ITEMS.items() if v.get("type") == "bi_kip"]
        bk_items.sort(key=lambda x: x[1].get("shop_id", 9999))

        PAGE_SIZE = 10
        total_pages = max(1, (len(bk_items) + PAGE_SIZE - 1) // PAGE_SIZE)
        page = max(1, min(page, total_pages))
        page_items = bk_items[(page-1)*PAGE_SIZE : page*PAGE_SIZE]

        embed = discord.Embed(
            title="📚 TÀNG KINH CÁC (Công Pháp & Bí Kíp) 📚",
            color=0x7B1FA2
        )
        lines = []
        for i, (key, item) in enumerate(page_items, start=(page-1)*PAGE_SIZE+1):
            sid = item.get("shop_id", key)
            price = item.get("price", 0)
            req = item.get("requires", "")
            req_str = f" Yêu cầu học {req} trước." if req else ""
            lines.append(
                f"**[{i}]** 🆔 {item['name']} - **{price:,} LT** (ID: {sid})\n"
                f"   📖 {item['desc']}{req_str}"
            )
        embed.description = "\n\n".join(lines)
        embed.set_footer(
            text=f"Trang {page}/{total_pages} | 💡 Mua: ,tl buy [ID] [Số lượng]"
        )
        await ctx.send(embed=embed)

    # ── ,tl buy bk*** ─────────────────────────────────────────
    # Xử lý đặc biệt khi mua bí kíp (kiểm tra đã học chưa, kiểm tra yêu cầu)
    @commands.command(name="mua_bikip", hidden=True)
    async def mua_bikip(self, ctx, key: str):
        """Nội bộ — dùng ,tl buy bk*** thay thế"""
        pass  # Handled in economy.py buy command via type check

async def setup(bot):
    await bot.add_cog(ShopExtra(bot))

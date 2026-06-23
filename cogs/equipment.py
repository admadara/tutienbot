"""cogs/equipment.py - Trang bị đầy đủ v5"""
import discord
from discord.ext import commands
import random, json

from utils.helpers import require_player, require_idle, now
from utils.embeds import *
from utils.game_data import ITEMS

def _s(n):
    return fmt(n)

def _safe(p,k,d=0):
    v=p.get(k); return v if v is not None else d

SLOTS = [
    ("weapon","⚔️","Vũ Khí"),
    ("armor","🛡️","Giáp Phục"),
    ("hat","🪖","Mũ"),
    ("necklace","📿","Vòng Cổ"),
    ("gloves","🧤","Găng Tay"),
    ("boots","👟","Giày"),
    ("phapbao","🔮","Pháp Bảo"),
]

SLOT_MAP = {
    "weapon":"weapon","vukhi":"weapon","vu_khi":"weapon",
    "armor":"armor","giap":"armor","giap_phuc":"armor",
    "hat":"hat","mu":"hat","non":"hat",
    "necklace":"necklace","vongco":"necklace","vong_co":"necklace",
    "gloves":"gloves","gangtay":"gloves","gang_tay":"gloves",
    "boots":"boots","giay":"boots","dep":"boots",
    "phapbao":"phapbao","phap_bao":"phapbao","pb":"phapbao",
}

# Tên hiển thị thân thiện cho từng slot
SLOT_DISPLAY = {
    "weapon":"vukhi","armor":"giap","hat":"mu",
    "necklace":"vongco","gloves":"gangtay","boots":"giay","phapbao":"phapbao",
}

ENHANCE_RATES = {(0,9):1.0,(10,14):0.80,(15,19):0.60,(20,24):0.40,(25,25):0.20}

def get_rate(lv):
    for (lo,hi),r in ENHANCE_RATES.items():
        if lo<=lv<=hi: return r
    return 0.10

def enhance_cost(lv):
    return int(1000 * (2.2 ** (lv/5)))

UPGRADE_HELP = (
    "⚠️ Vui lòng chọn vị trí trang bị muốn cường hóa:\n"
    "Ví dụ: `,tl upgrade vukhi`\n"
    "💡 Mẹo: Gõ thêm `bua` ở cuối để dùng Bùa Chúc Phúc tăng +15% tỷ lệ và chống hạ cấp\n"
    "(Ví dụ: `,tl upgrade vukhi bua`).\n\n"
    "Các vị trí hợp lệ:\n"
    "- vukhi\n- giap\n- phapbao\n- mu\n- vongco\n- gangtay\n- giay"
)

class Equipment(commands.Cog):
    def __init__(self, bot): self.bot = bot

    # ── ,tl trangbi ──────────────────────────────────────
    @commands.command(name="trangbi", aliases=["gear","tb"])
    async def trangbi(self, ctx):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        equip = await self.bot.db.get_equipment(ctx.author.id)
        total_atk=total_def=total_hp=0.0
        embed = discord.Embed(title=f"🛡️ TRANG BỊ — {player['name']}", color=realm_color(player["realm_index"]))

        for slot_id, em, sname in SLOTS:
            if slot_id in equip:
                e    = equip[slot_id]
                itm  = ITEMS.get(e["item_id"],{})
                enh  = e["enhance"]
                mult = 1 + enh*0.05
                ba   = itm.get("base_atk",0)*mult
                bd   = itm.get("base_def",0)*mult
                total_atk+=ba; total_def+=bd
                gems = json.loads(e.get("gems") or "[]")
                gem_icons = "".join(["🔴🟡🔵🟢🟣"[i%5] for i in range(len(gems))]) if gems else "▫️▫️▫️"
                embed.add_field(
                    name=f"{em} {sname}",
                    value=f"`{itm.get('name',e['item_id'])}` **(+{enh})**\n{gem_icons}",
                    inline=True
                )
            else:
                embed.add_field(
                    name=f"{em} {sname}",
                    value=f"_(trống)_",
                    inline=True
                )

        embed.add_field(
            name="📊 Tổng Bonus",
            value=f"⚔️ ATK +{_s(total_atk)}  🛡️ DEF +{_s(total_def)}",
            inline=False
        )
        embed.set_footer(text=",tl equip [id] | ,tl upgrade [slot] | ,tl unequip [slot]  •  Tu Tiên Bot v5")
        await ctx.send(embed=embed)

    # ── ,tl equip ────────────────────────────────────────
    @commands.command(name="equip", aliases=["mac","wear","trangbi_mac"])
    async def equip_item_cmd(self, ctx, item_id: str = None):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        if not item_id:
            await ctx.send(embed=warn("Dùng: `,tl equip [item_id]`\nXem trang bị: `,tl trangbi`\nXem shop: `,tl shop vukhi/giap`")); return
        item_id = item_id.lower()
        itm = ITEMS.get(item_id)
        if not itm or "slot" not in itm:
            await ctx.send(embed=error(f"`{item_id}` không phải trang bị!")); return
        if await self.bot.db.get_item_count(ctx.author.id, item_id) < 1:
            await ctx.send(embed=error(f"Không có **{itm['name']}** trong túi!")); return

        slot  = itm["slot"]
        equip = await self.bot.db.get_equipment(ctx.author.id)
        old   = None
        if slot in equip:
            old = equip[slot]
            await self.bot.db.add_item(ctx.author.id, old["item_id"], 1)

        await self.bot.db.equip_item(ctx.author.id, slot, item_id)
        await self.bot.db.remove_item(ctx.author.id, item_id, 1)

        embed = success("✅ TRANG BỊ")
        embed.description = f"**{itm['name']}** → slot **{slot}**"
        if old:
            old_name = ITEMS.get(old["item_id"],{}).get("name",old["item_id"])
            embed.description += f"\n_(Tháo: {old_name} +{old['enhance']} → túi đồ)_"
        await ctx.send(embed=embed)

    # ── ,tl unequip ──────────────────────────────────────
    @commands.command(name="unequip", aliases=["thao","remove_eq","thaotrangbi"])
    async def unequip(self, ctx, slot: str = None):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        if not slot:
            await ctx.send(embed=warn(
                "⚠️ Vui lòng chọn vị trí trang bị muốn tháo:\n"
                "Ví dụ: `,tl unequip vukhi`\n\n"
                "Các vị trí hợp lệ:\n"
                "- vukhi\n- giap\n- phapbao\n- mu\n- vongco\n- gangtay\n- giay"
            )); return
        slot_id = SLOT_MAP.get(slot.lower(), slot.lower())
        if slot_id not in [s[0] for s in SLOTS]:
            await ctx.send(embed=error(
                f"Slot **{slot}** không hợp lệ!\n"
                "Dùng: `vukhi / giap / phapbao / mu / vongco / gangtay / giay`"
            )); return
        equip = await self.bot.db.get_equipment(ctx.author.id)
        if slot_id not in equip:
            await ctx.send(embed=warn(f"Slot **{slot}** đang trống!")); return
        e   = equip[slot_id]
        itm = ITEMS.get(e["item_id"],{})
        await self.bot.db.add_item(ctx.author.id, e["item_id"], 1)
        await self.bot.db.execute(
            "DELETE FROM equipment WHERE user_id=? AND slot_id=?",
            (str(ctx.author.id), slot_id)
        )
        embed = success("✅ THÁO TRANG BỊ")
        embed.description = f"**{itm.get('name',e['item_id'])}** (+{e['enhance']}) → túi đồ"
        await ctx.send(embed=embed)

    # ── ,tl upgrade ──────────────────────────────────────
    @commands.command(name="upgrade", aliases=["cuonghoa","enhance","cuong","ch_eq","nangcap_eq"])
    async def upgrade(self, ctx, slot: str = None, option: str = None):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        if not slot:
            await ctx.send(embed=warn(UPGRADE_HELP)); return

        # Parse số lần và cờ bua
        use_bua = False
        so_lan  = 1
        if option:
            if option.lower() in ("bua", "bùa"):
                use_bua = True
            else:
                try:
                    so_lan = max(1, min(int(option), 10))
                except ValueError:
                    pass

        slot_id = SLOT_MAP.get(slot.lower(), slot.lower())
        if slot_id not in [s[0] for s in SLOTS]:
            await ctx.send(embed=error(
                f"Slot **{slot}** không hợp lệ!\n"
                + UPGRADE_HELP
            )); return

        equip = await self.bot.db.get_equipment(ctx.author.id)
        if slot_id not in equip:
            await ctx.send(embed=error(f"Slot **{slot}** trống! Mặc trang bị trước.")); return

        # Kiểm tra & tiêu thụ Bùa Chúc Phúc
        bua_used = False
        if use_bua:
            bua_count = await self.bot.db.get_item_count(ctx.author.id, "bua_chuc_phuc")
            if bua_count < 1:
                await ctx.send(embed=error(
                    "Không có **Bùa Chúc Phúc** trong túi!\n"
                    "Mua tại: `,tl shop danduo` (ID: `bua_chuc_phuc`, giá 50.000 Hạ)"
                )); return
            await self.bot.db.remove_item(ctx.author.id, "bua_chuc_phuc", 1)
            bua_used = True

        e      = equip[slot_id]
        itm    = ITEMS.get(e["item_id"],{})
        iname  = itm.get("name", e["item_id"])
        cur    = e["enhance"]

        if cur >= 25:
            await ctx.send(embed=warn(f"**{iname}** đã đạt MAX **(+25)**!")); return

        results = []
        ha = _safe(player,"linh_thach_ha")
        total_cost = 0

        for _ in range(so_lan):
            if cur >= 25: break
            cost = enhance_cost(cur)
            if ha < cost:
                results.append(f"💸 Không đủ LT! (cần {cost:,} Hạ)")
                break
            ha -= cost; total_cost += cost
            base_rate = get_rate(cur)
            rate = min(1.0, base_rate + (0.15 if bua_used else 0))
            if random.random() < rate:
                cur += 1
                results.append(f"✅ **+{cur}** (tỉ lệ {rate*100:.0f}%{'🍀' if bua_used else ''})")
            else:
                # Bùa chống hạ cấp: không giảm nếu thất bại
                if bua_used:
                    results.append(f"❌ Thất bại — **(+{cur})** giữ nguyên nhờ Bùa 🍀 (tỉ lệ {rate*100:.0f}%)")
                else:
                    results.append(f"❌ Thất bại ở +{cur} (tỉ lệ {rate*100:.0f}%)")

        await self.bot.db.execute(
            "UPDATE equipment SET enhance=? WHERE user_id=? AND slot_id=?",
            (cur, str(ctx.author.id), slot_id)
        )
        await self.bot.db.update_player(ctx.author.id, linh_thach_ha=ha)

        embed = discord.Embed(
            title=f"⚡ CƯỜNG HÓA — {iname}",
            color=0xFFD700 if cur > e["enhance"] else 0xF44336
        )
        if bua_used:
            embed.description = "🍀 _Đã dùng Bùa Chúc Phúc (+15% tỷ lệ, chống hạ cấp)_"
        embed.add_field(name="📜 Kết Quả",  value="\n".join(results[-5:]),  inline=False)
        embed.add_field(name="🔧 Hiện Tại", value=f"**(+{cur})**",          inline=True)
        embed.add_field(name="💰 Đã Chi",   value=f"{total_cost:,} Hạ",     inline=True)
        if cur < 25:
            next_rate = min(1.0, get_rate(cur) + (0.15 if bua_used else 0))
            embed.add_field(name="💡 Lần Sau", value=f"{enhance_cost(cur):,} Hạ | {next_rate*100:.0f}%", inline=True)
        await ctx.send(embed=embed)

    # ── ,tl xem_cuong ─────────────────────────────────────
    @commands.command(name="xem_cuong", aliases=["enhance_info","cuong_info"])
    async def xem_cuong(self, ctx):
        """Xem bảng tỉ lệ và chi phí cường hóa"""
        embed = discord.Embed(title="⚡ BẢNG CƯỜNG HÓA", color=0x9C27B0)
        lines = []
        for lv in range(0, 25):
            rate = get_rate(lv)
            cost = enhance_cost(lv)
            bar_char = "█"*int(rate*10) + "░"*(10-int(rate*10))
            lines.append(f"`+{lv:2d}→+{lv+1}` {bar_char} **{rate*100:.0f}%** — {cost:,} Hạ")
        embed.description = "\n".join(lines)
        embed.set_footer(text="Tối đa +25  •  ,tl upgrade [slot] bua để dùng Bùa Chúc Phúc")
        await ctx.send(embed=embed)

    # ── ,tl so_sanh_trangbi @người ───────────────────────
    @commands.command(name="compare_eq", aliases=["compare_trangbi","sosanh_tb"])
    async def compare_eq(self, ctx, target: discord.Member = None):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        if not target:
            await ctx.send(embed=warn("Dùng: `,tl compare_eq @người`")); return
        other  = await self.bot.db.get_player(target.id)
        if not other:
            await ctx.send(embed=error(f"{target.display_name} chưa nhập môn!")); return

        my_eq  = await self.bot.db.get_equipment(ctx.author.id)
        opp_eq = await self.bot.db.get_equipment(target.id)

        my_power  = sum(
            (ITEMS.get(e["item_id"],{}).get("base_atk",0)+ITEMS.get(e["item_id"],{}).get("base_def",0))
            * (1+e["enhance"]*0.05) for e in my_eq.values()
        )
        opp_power = sum(
            (ITEMS.get(e["item_id"],{}).get("base_atk",0)+ITEMS.get(e["item_id"],{}).get("base_def",0))
            * (1+e["enhance"]*0.05) for e in opp_eq.values()
        )

        embed = discord.Embed(title="⚔️ SO SÁNH TRANG BỊ", color=0x9C27B0)
        embed.add_field(name=f"👤 {player['name']}", value=f"Tổng sức mạnh TB: **{_s(my_power)}**", inline=True)
        embed.add_field(name=f"👤 {other['name']}",  value=f"Tổng sức mạnh TB: **{_s(opp_power)}**", inline=True)
        winner = player["name"] if my_power >= opp_power else other["name"]
        embed.add_field(name="🏆", value=f"Trang bị mạnh hơn: **{winner}**", inline=False)
        for slot_id, em, sname in SLOTS:
            my  = my_eq.get(slot_id)
            opp = opp_eq.get(slot_id)
            my_str  = f"`{ITEMS.get(my['item_id'],{}).get('name',my['item_id'])}` +{my['enhance']}" if my else "_trống_"
            opp_str = f"`{ITEMS.get(opp['item_id'],{}).get('name',opp['item_id'])}` +{opp['enhance']}" if opp else "_trống_"
            embed.add_field(name=f"{em} {sname}", value=f"{my_str}\nvs\n{opp_str}", inline=True)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Equipment(bot))

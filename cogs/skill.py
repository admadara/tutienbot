"""cogs/skill.py - Kỹ năng & Công Pháp v4"""
import discord
from discord.ext import commands
import json, random

from utils.helpers import require_player, require_idle, now
from utils.embeds import *
from utils.game_data import get_realm_name, REALMS
from utils.persistent_cache import PersistentCache

def _safe(p,k,d=0):
    v=p.get(k); return v if v is not None else d

# Danh sách công pháp
CONG_PHAP = {
    "1":   {"name":"🐉 Thiên Long Công",    "realm_min":0,  "price_ha":5000,   "atk_bonus":0.08,"desc":"Căn bản, tăng sát thương"},
    "2":      {"name":"🔥 Hỏa Vân Công",       "realm_min":2,  "price_ha":20000,  "atk_bonus":0.15,"crit_bonus":5,"desc":"Hỏa tính, bùng nổ sát thương"},
    "3":  {"name":"🌊 Thẩm Hải Quy Thu",   "realm_min":3,  "price_ha":50000,  "def_bonus":0.20,"hp_bonus":0.15,"desc":"Thủy tính, tăng phòng thủ"},
    "4":   {"name":"💨 Thanh Phong Tốc",    "realm_min":4,  "price_ha":80000,  "spd_bonus":0.25,"crit_bonus":8,"desc":"Phong tính, tốc độ xuất thần"},
    "5":{"name":"☀️ Cửu Dương Thần Công","realm_min":6, "price_ha":200000, "atk_bonus":0.20,"def_bonus":0.10,"hp_bonus":0.10,"desc":"Dương khí cực mạnh, toàn diện"},
    "6":{"name":"💀 Vong Sinh Cửu Biến", "realm_min":8,  "price_ha":500000, "atk_bonus":0.30,"crit_bonus":15,"desc":"Ma đạo cực phẩm, sát thương kinh thiên"},
    "7":  {"name":"🌀 Hỗn Độn Bát Quái",  "realm_min":12, "price_trung":50,  "atk_bonus":0.25,"def_bonus":0.20,"hp_bonus":0.20,"desc":"Hỗn Độn chi lực, cực phẩm công pháp"},
}

# Kỹ năng chiến đấu
SKILLS = {
    "1":     {"name":"⚔️ Kiếm Khí",      "cost_stam":5,  "atk_mult":1.5, "cooldown":30,  "desc":"Phóng kiếm khí, sát thương ×1.5"},
    "2":      {"name":"🔥 Hỏa Khẩu",       "cost_stam":8,  "atk_mult":2.0, "cooldown":60,  "desc":"Phun lửa, sát thương ×2.0"},
    "3":    {"name":"🛡️ Kim Cương Bảo",  "cost_stam":10, "def_mult":3.0, "cooldown":120, "desc":"Tăng phòng thủ ×3.0 trong 10s"},
    "4":    {"name":"⚡ Thiên Sét",       "cost_stam":15, "atk_mult":3.0, "aoe":True,"cooldown":180,"desc":"Sét đánh, sát thương ×3.0"},
    "5":     {"name":"💚 Phục Hồi",        "cost_stam":12, "heal":0.30,    "cooldown":90,  "desc":"Hồi phục 30% HP tối đa"},
    "6":       {"name":"💨 Tốc Ảnh",         "cost_stam":6,  "dodge":0.50,   "cooldown":45,  "desc":"Né tránh 50% đòn tiếp theo"},
}

class Skill(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._skill_cd = PersistentCache(bot, "skill_cooldowns")  # uid -> {skill: expire_ts}

    async def cog_load(self):
        await self._skill_cd.load()

    async def cog_unload(self):
        await self._skill_cd.save()

    @commands.group(name="cong_phap", aliases=["kung_fu"], invoke_without_command=True)
    async def cong_phap(self, ctx):
        embed = discord.Embed(title="📜 CÔNG PHÁP TU TIÊN", color=0x9C27B0)
        embed.description = (
            "`,tl cong_phap danh_sach` — Xem tất cả công pháp\n"
            "`,tl cong_phap mua [id]` — Mua công pháp\n"
            "`,tl cong_phap cua_toi` — Xem công pháp đang dùng\n"
            "`,tl cong_phap kich_hoat [id]` — Kích hoạt công pháp\n\n"
            "💡 Công pháp cho bonus chiến đấu khi kích hoạt!"
        )
        await ctx.send(embed=embed)

    @cong_phap.command(name="danh_sach", aliases=["list","ds","all"])
    async def danh_sach(self, ctx):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        ri = player["realm_index"]
        embed = discord.Embed(title="📜 DANH SÁCH CÔNG PHÁP", color=0x9C27B0)
        for cpid, cp in CONG_PHAP.items():
            locked = ri < cp["realm_min"]
            icon   = "🔒" if locked else "✅"
            price  = f"{cp.get('price_ha',0):,} Hạ" if cp.get('price_ha') else f"{cp.get('price_trung',0)} Trung"
            bonuses = []
            if cp.get("atk_bonus"):  bonuses.append(f"ATK +{cp['atk_bonus']*100:.0f}%")
            if cp.get("def_bonus"):  bonuses.append(f"DEF +{cp['def_bonus']*100:.0f}%")
            if cp.get("hp_bonus"):   bonuses.append(f"HP +{cp['hp_bonus']*100:.0f}%")
            if cp.get("spd_bonus"):  bonuses.append(f"SPD +{cp['spd_bonus']*100:.0f}%")
            if cp.get("crit_bonus"): bonuses.append(f"CRIT +{cp['crit_bonus']}%")
            embed.add_field(
                name=f"{icon} `{cpid}` {cp['name']}",
                value=(
                    f"_{cp['desc']}_\n"
                    f"📊 {' | '.join(bonuses)}\n"
                    f"💰 {price}"
                    + (f" | 🔒 Cần realm {cp['realm_min']}" if locked else "")
                ),
                inline=False
            )
        embed.set_footer(text=",tl cong_phap mua [id] để mua  •  Tu Tiên Bot v3")
        await ctx.send(embed=embed)

    @cong_phap.command(name="mua", aliases=["buy","hoc"])
    async def mua(self, ctx, cpid: str = None):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        if not cpid:
            await ctx.send(embed=warn("Dùng: `,tl cong_phap mua [id]`")); return
        cpid = cpid.lower()
        cp   = CONG_PHAP.get(cpid)
        if not cp:
            await ctx.send(embed=error(f"Không có công pháp `{cpid}`!")); return
        if player["realm_index"] < cp["realm_min"]:
            await ctx.send(embed=error(f"Cần realm {cp["realm_min"]}!")); return

        # Kiểm tra đã học chưa (dùng inventory với type cp)
        have = await self.bot.db.get_item_count(ctx.author.id, f"cp_{cpid}")
        if have:
            await ctx.send(embed=warn(f"Đã học **{cp['name']}** rồi!")); return

        # Trừ tiền
        if cp.get("price_ha"):
            if _safe(player,"linh_thach_ha") < cp["price_ha"]:
                await ctx.send(embed=error(f"Cần {cp['price_ha']:,} Hạ LT!")); return
            await self.bot.db.update_player(ctx.author.id,
                linh_thach_ha=_safe(player,"linh_thach_ha")-cp["price_ha"])
        elif cp.get("price_trung"):
            if _safe(player,"linh_thach_trung") < cp["price_trung"]:
                await ctx.send(embed=error(f"Cần {cp['price_trung']} Trung LT!")); return
            await self.bot.db.update_player(ctx.author.id,
                linh_thach_trung=_safe(player,"linh_thach_trung")-cp["price_trung"])

        await self.bot.db.add_item(ctx.author.id, f"cp_{cpid}", 1)
        embed = success(f"📜 HỌC CÔNG PHÁP: {cp['name']}!")
        embed.description = f"_{cp['desc']}_\nGõ `,tl cong_phap kich_hoat {cpid}` để kích hoạt bonus!"
        await ctx.send(embed=embed)

    @cong_phap.command(name="cua_toi", aliases=["mine","my","toi"])
    async def cua_toi(self, ctx):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        items = await self.bot.db.get_inventory(ctx.author.id)
        learned = [i["item_id"].replace("cp_","") for i in items if i["item_id"].startswith("cp_")]
        embed = discord.Embed(title="📜 CÔNG PHÁP CỦA TÔI", color=0x9C27B0)
        if not learned:
            embed.description = "_Chưa học công pháp nào!\n`,tl cong_phap danh_sach` để xem._"
        else:
            for cpid in learned:
                cp = CONG_PHAP.get(cpid,{})
                embed.add_field(name=cp.get("name",cpid), value=f"_{cp.get('desc','?')}_", inline=True)
        await ctx.send(embed=embed)

    @cong_phap.command(name="kich_hoat", aliases=["activate","on","enable"])
    async def kich_hoat(self, ctx, cpid: str = None):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        if not cpid:
            await ctx.send(embed=warn("Dùng: `,tl cong_phap kich_hoat [id]`")); return
        cpid = cpid.lower()
        have = await self.bot.db.get_item_count(ctx.author.id, f"cp_{cpid}")
        if not have:
            await ctx.send(embed=error(f"Chưa học `{cpid}`! Mua tại `,tl cong_phap mua {cpid}`")); return
        cp = CONG_PHAP.get(cpid, {})
        # Tính lại lực chiến với bonus công pháp
        atk  = _safe(player,"atk",100) * (1 + cp.get("atk_bonus",0))
        def_ = _safe(player,"def_",50)  * (1 + cp.get("def_bonus",0))
        hp   = _safe(player,"hp_max",1000)*(1 + cp.get("hp_bonus",0))
        spd  = _safe(player,"spd",50)   * (1 + cp.get("spd_bonus",0))
        crit = _safe(player,"crit",5)   +      cp.get("crit_bonus",0)
        new_lc = round(atk*2+def_*1.2+hp*0.005+spd*0.8+crit*50, 2)
        await self.bot.db.update_player(ctx.author.id,
            atk=atk, def_=def_, hp_max=hp, spd=spd, crit=crit, luc_chien=new_lc)
        embed = success(f"⚡ KÍCH HOẠT: {cp.get('name',cpid)}!")
        embed.description = f"_{cp.get('desc','?')}_\n⚔️ Lực Chiến mới: **{new_lc/1000:.1f}K**"
        await ctx.send(embed=embed)

    @commands.command(name="ky_nang", aliases=["kynang","skill","skill_list"])
    async def ky_nang(self, ctx):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        """Xem danh sách kỹ năng chiến đấu"""
        embed = discord.Embed(title="⚡ KỸ NĂNG CHIẾN ĐẤU", color=0xFF5722)
        embed.description = "Kỹ năng sử dụng trong `,tl pk` và `,tl dau_truong`\n"
        for sid, sk in SKILLS.items():
            embed.add_field(
                name=f"`{sid}` {sk['name']}",
                value=(
                    f"_{sk['desc']}_\n"
                    f"🔋 -{sk['cost_stam']} TL | ⏱️ CD: {sk['cooldown']}s"
                ),
                inline=True
            )
        await ctx.send(embed=embed)

    @commands.command(name="su_dung_ky_nang", aliases=["use_skill","cast","uk"])
    async def su_dung_ky_nang(self, ctx, skill_id: str = None):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        """Dùng kỹ năng để nhận buff hoặc hiệu ứng"""
        if not skill_id:
            await ctx.send(embed=warn("Dùng: `,tl uk [skill_id]`\nXem: `,tl ky_nang`")); return
        sid = skill_id.lower()
        sk  = SKILLS.get(sid)
        if not sk:
            await ctx.send(embed=error(f"Kỹ năng `{sid}` không tồn tại!")); return

        uid = str(ctx.author.id)
        cds = self._skill_cd.get(uid, {})
        if now() < cds.get(sid, 0):
            rem = cds[sid] - now()
            await ctx.send(embed=warn(f"**{sk['name']}** đang hồi chiêu! `{rem}s`")); return

        cost = sk["cost_stam"]
        if _safe(player,"stamina") < cost:
            await ctx.send(embed=warn(f"Cần **{cost} TL**!")); return

        # Áp dụng hiệu ứng
        updates = {"stamina": _safe(player,"stamina")-cost}
        effect_lines = []

        if sk.get("heal"):
            heal = int(_safe(player,"hp_max",1000)*sk["heal"])
            effect_lines.append(f"💚 Hồi +{heal:,} HP")
        if sk.get("atk_mult"):
            effect_lines.append(f"⚔️ ATK ×{sk['atk_mult']} trong trận tiếp theo")
        if sk.get("def_mult"):
            effect_lines.append(f"🛡️ DEF ×{sk['def_mult']} trong 10s")

        # Set cooldown
        existing_cd = self._skill_cd.get(uid, {})
        existing_cd[sid] = now() + sk["cooldown"]
        self._skill_cd[uid] = existing_cd

        await self.bot.db.update_player(ctx.author.id, **updates)

        embed = discord.Embed(
            title=f"⚡ {sk['name']}",
            description="\n".join(effect_lines) or "_Kỹ năng được kích hoạt!_",
            color=0xFF5722
        )
        embed.add_field(name="🔋 TL", value=f"-{cost}", inline=True)
        embed.add_field(name="⏱️ CD", value=f"{sk['cooldown']}s", inline=True)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Skill(bot))

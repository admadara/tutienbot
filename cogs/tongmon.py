"""cogs/tongmon.py - Tông Môn v6 — full rewrite"""
import discord
import random
import json
from datetime import datetime, timezone
from discord.ext import commands
from utils.helpers import require_player, now
from utils.embeds import *
from utils.game_data import get_realm_name

# ══════════════════════════════════════════════════════════════
#  CẤU HÌNH
# ══════════════════════════════════════════════════════════════
CREATE_COST = 500_000_000   # Hạ Phẩm LT

# Cấp bậc: 0=Thành Viên  1=Trưởng Lão  2=Phó Tông Chủ  3=Tông Chủ
RANK_NAMES = {0: "Thành Viên", 1: "Trưởng Lão", 2: "Phó Tông Chủ", 3: "Tông Chủ"}
RANK_EMOJI = {0: "👤", 1: "🧓", 2: "⚔️", 3: "👑"}

# Kiến trúc Tông Môn
BUILDINGS = {
    "mainhall": {
        "name": "Đại Điện",
        "max_level": 100,
        "cost_base": 10_000_000,
        "effect": lambda lv: f"Max Members: {10 + lv * 20}",
        "max_members": lambda lv: 10 + lv * 20,
    },
    "library": {
        "name": "Tàng Kinh Các",
        "max_level": 100,
        "cost_base": 8_000_000,
        "effect": lambda lv: f"EXP Buff: +{lv * 2}%",
    },
    "altar": {
        "name": "Tế Đàn",
        "max_level": 100,
        "cost_base": 8_000_000,
        "effect": lambda lv: f"Drop Rate: +{lv}%, Luck: +{lv * 5}",
    },
    "sect_realm": {
        "name": "Bí Cảnh Tông Môn",
        "max_level": 100,
        "cost_base": 15_000_000,
        "effect": lambda lv: f"Unlocked Tier: {lv}",
    },
    "array": {
        "name": "Đại Trận Tông Môn (Buff PK)",
        "max_level": 10,
        "cost_base": 20_000_000,
        "effect": lambda lv: f"EXP +{lv*2}%, HP +{lv*2}%, Dame +{lv}%, Bạo Kích +{lv//2}%",
    },
    "shop": {
        "name": "Bảo Khố Tông Môn",
        "max_level": 5,
        "cost_base": 12_000_000,
        "effect": lambda lv: f"Shop Tier: {lv}",
    },
    "defense": {
        "name": "Đại Trận Hộ Tông",
        "max_level": 100,
        "cost_base": 10_000_000,
        "effect": lambda lv: f"Defense Mult: x{lv}",
    },
}

# Map vùng (dùng ID từ world.py)
MAP_ZONES = {
    "t1": "Rừng Già U Minh (Trung Châu)",
    "t2": "Kỳ Lân Động (Trung Châu)",
    "t3": "Hồ Quang (Trung Châu)",
    "t4": "Biển Cát (Trung Châu)",
    "t5": "Đường Tơ Lụa Cổ (Trung Châu)",
    "t6": "Rừng Trúc Xanh (Trung Châu)",
    "n1": "Rừng Già U Minh (Nam Châu)",
    "n2": "Cổ Linh Thú (Nam Châu)",
    "n3": "Đầm Lầy Độc Khí (Nam Châu)",
    "n4": "Dãy Núi Trường Sinh (Nam Châu)",
    "n5": "Đền Thờ Bạch Hổ (Nam Châu)",
    "tay1": "Đại Sa Hà (Tây Châu)",
    "tay2": "Tàn Tích Cổ Đô (Tây Châu)",
    "tay3": "Ốc Đảo Sâm Đan (Tây Châu)",
    "tay4": "Quỷ Môn Quan (Tây Châu)",
    "b1": "Thiên Sơn Băng Giá (Bắc Châu)",
    "b2": "Rừng Thông Tuyết Phủ (Bắc Châu)",
    "b3": "Ngọc Cung Tuyết Sơn (Bắc Châu)",
    "d1": "Đạo Quán Thiên Vũ (Đông Châu)",
    "d2": "Núi Trường Sinh (Đông Châu)",
    "d3": "Đông Hải (Đông Châu)",
}

TUYENCHIEN_DURATION = 300  # 5 phút (giây)

def _safe(p, k, d=0):
    v = p.get(k); return v if v is not None else d

def _rank(player, tm):
    if str(player["user_id"]) == str(tm["leader_id"]): return 3
    return _safe(player, "sect_rank", 0)

def _upgrade_cost(building_key, current_level):
    base = BUILDINGS[building_key]["cost_base"]
    return int(base * (1.15 ** current_level))

def _get_buildings(tm):
    raw = tm.get("buildings") or "{}"
    try:
        return json.loads(raw) if isinstance(raw, str) else raw
    except Exception:
        return {}

def _max_members(tm):
    blds = _get_buildings(tm)
    lv = blds.get("mainhall", 1)
    return BUILDINGS["mainhall"]["max_members"](lv)

def _get_wars(tm):
    raw = tm.get("active_wars") or "{}"
    try:
        return json.loads(raw) if isinstance(raw, str) else raw
    except Exception:
        return {}


class TongMon(commands.Cog):
    def __init__(self, bot): self.bot = bot

    # ══════════════════════════════════════════════════════
    #  GROUP: ,tl sect / ,tl tm / ,tl tongmon
    # ══════════════════════════════════════════════════════
    @commands.group(
        name="sect",
        aliases=["tm", "tongmon", "mon", "tong"],
        invoke_without_command=True
    )
    async def sect(self, ctx):
        """Hiện bảng lệnh Tông Môn"""
        embed = discord.Embed(
            title="🏰 HỆ THỐNG TÔNG MÔN 🏰",
            color=0x8B4513
        )
        embed.description = (
            "🔷 `,tl sect create [Tên]` — Tạo Tông Môn *(500.000.000 Hạ LT)*\n"
            "🔷 `,tl sect info` — Xem thông tin Tông Môn của bạn\n"
            "🔷 `,tl sect list` — Danh sách Tông Môn server\n"
            "🔷 `,tl sect donate [Số tiền]` — Cống hiến xây dựng Tông Môn\n"
            "🔷 `,tl sect upgrade [Mã]` — Nâng cấp kiến trúc *(Tông Chủ/Phó)*\n"
            "🔷 `,tl sect phongchuc [@Tag] [pho/truonglao/thanhvien]` — Phong chức vụ\n"
            "🔷 `,tl sect invite [@Tag]` — Mời thành viên\n"
            "🔷 `,tl sect join` — Chấp nhận lời mời\n"
            "🔷 `,tl sect apply [ID/Tên]` — Xin gia nhập Tông Môn\n"
            "🔷 `,tl sect accept [@Tag/ID]` — Duyệt đơn xin gia nhập *(Quản trị)*\n"
            "🔷 `,tl sect reject [@Tag/ID]` — Từ chối đơn *(Quản trị)*\n"
            "🔷 `,tl sect apps` — Xem danh sách đơn xin vào\n"
            "🔷 `,tl sect leave` — Rời Tông Môn *(Mất cống hiến)*\n"
            "🔷 `,tl sect kick [@Tag]` — Trục xuất thành viên *(Tông Chủ/Phó)*\n"
            "🔷 `,tl sect transfer [@Tag]` — Chuyển nhượng chức Tông Chủ\n"
            "🔷 `,tl sect disband` — Giải tán Tông Môn *(Tông Chủ)*\n"
            "🔷 `,tl sect members` — Xem danh sách thành viên\n"
            "🔷 `,tl sect mission` — Nhiệm vụ Tông Môn hàng ngày\n"
            "🔷 `,tl sect congkich [ID_vùng]` — Tấn công chiếm Lãnh địa\n"
            "🔷 `,tl sect tuyenchien [ID_vùng]` — Tuyên chiến với Tông môn khác\n"
            "🔷 `,tl sect beast [ID_vùng] [loại]` — Triệu hồi/Nâng cấp Thần Thú\n"
            "🔷 `,tl sect tubo [ID_vùng] [LT]` — Bơm máu/Nâng cấp Trận Pháp\n"
            "🔷 `,tl sect shop` — Mở cửa hàng Tông môn"
        )
        embed.set_footer(text="Alias: ,tl sect | ,tl tm | ,tl tongmon  •  Tu Tiên Bot v6")
        await ctx.send(embed=embed)

    # ══ CREATE ═════════════════════════════════════════════
    @sect.command(name="create", aliases=["tao", "lap", "found"])
    async def create(self, ctx, *, ten: str):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player: await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        if _safe(player, "tong_mon_id"): await ctx.send(embed=warn("Đã có Tông Môn! Rời trước.")); return
        if _safe(player, "linh_thach_ha") < CREATE_COST:
            await ctx.send(embed=warn(
                f"Cần **{CREATE_COST:,} Hạ Phẩm LT** để lập Tông Môn!\n"
                f"Hiện có: `{_safe(player,'linh_thach_ha'):,}` Hạ LT"
            )); return
        ten = ten.strip()[:30]
        if await self.bot.db.fetchone("SELECT id FROM tong_mon WHERE name=?", (ten,)):
            await ctx.send(embed=error(f"Tên **{ten}** đã tồn tại!")); return

        init_blds = json.dumps({"mainhall": 1, "library": 0, "altar": 0,
                                 "sect_realm": 0, "array": 0, "shop": 0, "defense": 0})
        await self.bot.db.execute(
            "INSERT INTO tong_mon(name,leader_id,treasury,buildings,active_wars) VALUES(?,?,?,?,?)",
            (ten, str(ctx.author.id), 0, init_blds, "{}")
        )
        tm = await self.bot.db.fetchone("SELECT id FROM tong_mon WHERE name=?", (ten,))
        await self.bot.db.update_player(ctx.author.id,
            tong_mon_id=tm["id"], sect_rank=3,
            linh_thach_ha=_safe(player, "linh_thach_ha") - CREATE_COST
        )
        embed = success(f"🏰 LẬP TÔNG MÔN: {ten}!")
        embed.description = (
            f"**{player['name']}** trở thành **👑 Tông Chủ** đầu tiên!\n"
            f"💰 -{CREATE_COST:,} Hạ Phẩm LT\n\n"
            f"_Mời thành viên: `,tl sect invite @người` hoặc đợi đơn `,tl sect apps`_"
        )
        await ctx.send(embed=embed)

    # ══ INFO ═══════════════════════════════════════════════
    @sect.command(name="info", aliases=["thongtin", "xem"])
    async def info(self, ctx):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player: await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        tm_id = _safe(player, "tong_mon_id")
        if not tm_id:
            await ctx.send(embed=info("⛩️ TÔNG MÔN",
                "Chưa gia nhập Tông Môn!\n\n"
                "`,tl sect create [tên]` — Lập mới\n"
                "`,tl sect apply [tên]` — Xin gia nhập\n"
                "`,tl sect list` — Xem top server"
            )); return

        tm = await self.bot.db.fetchone("SELECT * FROM tong_mon WHERE id=?", (tm_id,))
        if not tm: await ctx.send(embed=error("Tông Môn không tồn tại!")); return

        members = await self.bot.db.fetchall(
            "SELECT * FROM players WHERE tong_mon_id=?", (tm_id,)
        )
        leader = await self.bot.db.get_player(tm["leader_id"])
        blds   = _get_buildings(tm)
        max_m  = _max_members(tm)
        treasury = _safe(tm, "treasury", 0)

        created_ts = _safe(tm, "created_at", 0)
        try:
            created_str = datetime.fromtimestamp(created_ts, tz=timezone.utc).strftime("%-d/%-m/%Y")
        except Exception:
            created_str = "N/A"

        embed = discord.Embed(
            title=f"🏰 {tm['name']}",
            color=0x8B4513
        )
        embed.add_field(name="👤 Tông Chủ",    value=leader["name"] if leader else "???",  inline=True)
        embed.add_field(name="🏆 Cấp Độ",      value=f"**{_safe(tm,'level',1)}**",         inline=True)
        embed.add_field(name="💰 Ngân Quỹ",    value=f"{treasury:,}",                      inline=True)
        embed.add_field(name="👥 Thành Viên",  value=f"{len(members)} / {max_m}",          inline=True)
        embed.add_field(name="📅 Ngày lập",    value=created_str,                           inline=True)
        embed.add_field(name="\u200b",          value="\u200b",                              inline=True)

        # Kiến trúc
        bld_lines = []
        for key, bdata in BUILDINGS.items():
            lv = blds.get(key, 0)
            if lv > 0:
                eff = bdata["effect"](lv)
                bld_lines.append(f"- **{bdata['name']}**: Lv.{lv} *({eff})*")
        if bld_lines:
            embed.add_field(name="🏛️ KIẾN TRÚC:", value="\n".join(bld_lines), inline=False)

        embed.set_footer(text=",tl sect members | ,tl sect upgrade | ,tl sect shop  •  Tu Tiên Bot v6")
        await ctx.send(embed=embed)

    # ══ LIST ═══════════════════════════════════════════════
    @sect.command(name="list", aliases=["danhsach_tong", "top"])
    async def list_sect(self, ctx):
        rows = await self.bot.db.fetchall(
            "SELECT * FROM tong_mon ORDER BY level DESC, exp DESC LIMIT 10"
        )
        embed = discord.Embed(title="🏆 BẢNG XẾP HẠNG TÔNG MÔN", color=0xFFD700)
        lines = []
        medals = ["🥇", "🥈", "🥉"]
        for i, tm in enumerate(rows):
            cnt = await self.bot.db.fetchone(
                "SELECT COUNT(*) as c FROM players WHERE tong_mon_id=?", (tm["id"],)
            )
            mc  = cnt["c"] if cnt else 0
            max_m = _max_members(tm)
            m   = medals[i] if i < 3 else f"`{i+1}.`"
            lines.append(f"{m} **{tm['name']}** — Cấp {_safe(tm,'level',1)} | 👥 {mc}/{max_m}")
        embed.description = "\n".join(lines) if lines else "_Chưa có Tông Môn nào_"
        embed.set_footer(text=",tl sect create [tên] để lập Tông Môn  •  Tu Tiên Bot v6")
        await ctx.send(embed=embed)

    # ══ DONATE ═════════════════════════════════════════════
    @sect.command(name="donate", aliases=["donggop", "cong_hien"])
    async def donate(self, ctx, so_lt: int = 0):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player: await ctx.send(embed=warn("Chưa nhập môn!")); return
        tm_id = _safe(player, "tong_mon_id")
        if not tm_id: await ctx.send(embed=warn("Chưa gia nhập Tông Môn!")); return
        if so_lt <= 0: await ctx.send(embed=warn("Dùng: `,tl sect donate [số LT]`")); return
        if _safe(player, "linh_thach_ha") < so_lt:
            await ctx.send(embed=warn(f"Không đủ Hạ LT! Cần `{so_lt:,}`.")); return

        exp_gained = max(1, so_lt // 100)
        await self.bot.db.update_player(ctx.author.id,
            linh_thach_ha=_safe(player, "linh_thach_ha") - so_lt)
        await self.bot.db.execute(
            "UPDATE tong_mon SET treasury=treasury+?, exp=exp+? WHERE id=?",
            (so_lt, exp_gained, tm_id)
        )
        # Level up
        tm = await self.bot.db.fetchone("SELECT * FROM tong_mon WHERE id=?", (tm_id,))
        lv = _safe(tm, "level", 1); exp = _safe(tm, "exp", 0)
        while exp >= lv * 50_000:
            exp -= lv * 50_000; lv += 1
        await self.bot.db.execute(
            "UPDATE tong_mon SET level=?, exp=? WHERE id=?", (lv, exp, tm_id)
        )
        embed = success("🎁 ĐÓNG GÓP TÔNG MÔN!")
        embed.description = (
            f"💰 -{so_lt:,} Hạ LT → Ngân Quỹ Tông Môn\n"
            f"✨ +{exp_gained:,} EXP Tông Môn\n"
            f"⭐ Tông Môn Cấp: **{lv}**"
        )
        await ctx.send(embed=embed)

    # ══ UPGRADE ════════════════════════════════════════════
    @sect.command(name="upgrade", aliases=["nangcap", "nc"])
    async def upgrade(self, ctx, ma: str = None):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player: await ctx.send(embed=warn("Chưa nhập môn!")); return
        tm_id = _safe(player, "tong_mon_id")
        if not tm_id: await ctx.send(embed=warn("Chưa gia nhập Tông Môn!")); return
        tm = await self.bot.db.fetchone("SELECT * FROM tong_mon WHERE id=?", (tm_id,))
        if _rank(player, tm) < 2:
            await ctx.send(embed=warn("Chỉ **Tông Chủ/Phó Tông Chủ** mới nâng cấp kiến trúc!")); return

        blds = _get_buildings(tm)

        if not ma or ma.lower() not in BUILDINGS:
            # Hiện danh sách
            embed = discord.Embed(title="⚙️ [NÂNG CẤP KIẾN TRÚC TÔNG MÔN]", color=0x8B4513)
            lines = []
            for key, bdata in BUILDINGS.items():
                lv      = blds.get(key, 0)
                max_lv  = bdata["max_level"]
                eff     = bdata["effect"](lv) if lv > 0 else bdata["effect"](1) + " (Lv.1 preview)"
                maxstr  = " (MAX)" if lv >= max_lv else ""
                lines.append(
                    f"\n🔹 **{bdata['name']}** *(Mã: `{key}`)*\n"
                    f"   🔸 Cấp độ hiện tại: Lv.**{lv}** / {max_lv}{maxstr}\n"
                    f"   🔸 Hiệu quả hiện tại: {bdata['effect'](lv) if lv > 0 else 'Chưa xây'}"
                )
            embed.description = "\n".join(lines)
            embed.set_footer(text="👉 Dùng: ,tl sect upgrade [Mã]  •  Ví dụ: ,tl sect upgrade array")
            await ctx.send(embed=embed); return

        key   = ma.lower()
        bdata = BUILDINGS[key]
        lv    = blds.get(key, 0)
        max_lv = bdata["max_level"]
        if lv >= max_lv:
            await ctx.send(embed=warn(f"**{bdata['name']}** đã đạt MAX Lv.{max_lv}!")); return

        cost = _upgrade_cost(key, lv)
        treasury = _safe(tm, "treasury", 0)
        if treasury < cost:
            await ctx.send(embed=warn(
                f"Ngân quỹ Tông Môn không đủ!\n"
                f"Cần: `{cost:,}` | Hiện có: `{treasury:,}`\n"
                f"_Dùng `,tl sect donate` để nạp thêm vào ngân quỹ._"
            )); return

        blds[key] = lv + 1
        await self.bot.db.execute(
            "UPDATE tong_mon SET buildings=?, treasury=treasury-? WHERE id=?",
            (json.dumps(blds), cost, tm_id)
        )
        new_eff = bdata["effect"](lv + 1)
        embed = success(f"🏗️ NÂNG CẤP: {bdata['name']}")
        embed.description = (
            f"Lv.**{lv}** → Lv.**{lv+1}** / {max_lv}\n"
            f"💰 -{cost:,} từ Ngân Quỹ\n"
            f"✅ Hiệu quả mới: **{new_eff}**"
        )
        await ctx.send(embed=embed)

    # ══ PHONG CHỨC ═════════════════════════════════════════
    @sect.command(name="phongchuc", aliases=["rank_set", "chuc"])
    async def phongchuc(self, ctx, member: discord.Member = None, chuc: str = None):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player: await ctx.send(embed=warn("Chưa nhập môn!")); return
        tm_id = _safe(player, "tong_mon_id")
        if not tm_id: await ctx.send(embed=warn("Chưa gia nhập Tông Môn!")); return
        tm = await self.bot.db.fetchone("SELECT * FROM tong_mon WHERE id=?", (tm_id,))
        if _rank(player, tm) < 2:
            await ctx.send(embed=warn("Chỉ **Tông Chủ/Phó Tông Chủ** mới phong chức!")); return
        if not member or not chuc:
            await ctx.send(embed=warn(
                "Dùng: `,tl sect phongchuc @Tag [chuc]`\n"
                "`pho` | `truonglao` | `thanhvien`"
            )); return

        chuc_map = {"pho": 2, "photongchu": 2, "truonglao": 1, "tl": 1, "thanhvien": 0, "tv": 0}
        rank_val = chuc_map.get(chuc.lower())
        if rank_val is None:
            await ctx.send(embed=error("Chức không hợp lệ! Dùng: `pho` / `truonglao` / `thanhvien`")); return
        if rank_val == 2 and _rank(player, tm) < 3:
            await ctx.send(embed=warn("Chỉ **Tông Chủ** mới phong **Phó Tông Chủ**!")); return

        target = await self.bot.db.get_player(member.id)
        if not target or _safe(target, "tong_mon_id") != tm_id:
            await ctx.send(embed=error("Người này không trong Tông Môn!")); return
        if str(member.id) == str(tm["leader_id"]):
            await ctx.send(embed=warn("Không thể phong chức cho Tông Chủ!")); return

        await self.bot.db.update_player(member.id, sect_rank=rank_val)
        await ctx.send(embed=success(
            f"🎖️ **{target['name']}** được phong **{RANK_EMOJI[rank_val]} {RANK_NAMES[rank_val]}**!"
        ))

    # ══ INVITE ═════════════════════════════════════════════
    @sect.command(name="invite", aliases=["moi"])
    async def invite(self, ctx, member: discord.Member = None):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player: await ctx.send(embed=warn("Chưa nhập môn!")); return
        tm_id = _safe(player, "tong_mon_id")
        if not tm_id: await ctx.send(embed=warn("Chưa gia nhập Tông Môn!")); return
        tm = await self.bot.db.fetchone("SELECT * FROM tong_mon WHERE id=?", (tm_id,))
        if _rank(player, tm) < 2:
            await ctx.send(embed=warn("Chỉ **Phó Tông Chủ** trở lên mới mời!")); return
        if not member: await ctx.send(embed=warn("Dùng: `,tl sect invite @người`")); return

        target = await self.bot.db.get_player(member.id)
        if not target: await ctx.send(embed=error("Người này chưa nhập môn!")); return
        if _safe(target, "tong_mon_id"): await ctx.send(embed=warn("Người này đã có Tông Môn rồi!")); return

        max_m = _max_members(tm)
        cnt = await self.bot.db.fetchone("SELECT COUNT(*) as c FROM players WHERE tong_mon_id=?", (tm_id,))
        if cnt and cnt["c"] >= max_m:
            await ctx.send(embed=warn(f"Tông Môn đầy {max_m} thành viên! Nâng cấp **Đại Điện** để mở rộng.")); return

        await self.bot.db.update_player(member.id, sect_invite_id=tm_id)
        embed = success("📨 LỜI MỜI GIA NHẬP")
        embed.description = (
            f"**{player['name']}** mời **{target['name']}** vào **{tm['name']}**!\n\n"
            f"_{member.mention} dùng `,tl sect join` để chấp nhận._"
        )
        await ctx.send(embed=embed)

    # ══ JOIN ═══════════════════════════════════════════════
    @sect.command(name="join", aliases=["chapmoi"])
    async def join(self, ctx):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player: await ctx.send(embed=warn("Chưa nhập môn!")); return
        if _safe(player, "tong_mon_id"): await ctx.send(embed=warn("Rời Tông Môn hiện tại trước!")); return
        invite_id = _safe(player, "sect_invite_id")
        if not invite_id: await ctx.send(embed=warn("Bạn chưa có lời mời!\nXin vào: `,tl sect apply [tên]`")); return

        tm = await self.bot.db.fetchone("SELECT * FROM tong_mon WHERE id=?", (invite_id,))
        if not tm: await ctx.send(embed=error("Tông Môn không còn tồn tại!")); return

        max_m = _max_members(tm)
        cnt = await self.bot.db.fetchone("SELECT COUNT(*) as c FROM players WHERE tong_mon_id=?", (invite_id,))
        if cnt and cnt["c"] >= max_m:
            await ctx.send(embed=warn(f"Tông Môn đã đầy {max_m} thành viên!")); return

        await self.bot.db.update_player(ctx.author.id, tong_mon_id=invite_id, sect_invite_id=None, sect_rank=0)
        await ctx.send(embed=success(f"🎉 **{player['name']}** gia nhập **{tm['name']}** với tư cách **Thành Viên**!"))

    # ══ APPLY ══════════════════════════════════════════════
    @sect.command(name="apply", aliases=["xinvao", "xin"])
    async def apply(self, ctx, *, ten: str = None):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player: await ctx.send(embed=warn("Chưa nhập môn!")); return
        if _safe(player, "tong_mon_id"): await ctx.send(embed=warn("Rời Tông Môn hiện tại trước!")); return
        if not ten: await ctx.send(embed=warn("Dùng: `,tl sect apply [Tên/ID Tông Môn]`")); return

        tm = None
        if ten.isdigit():
            tm = await self.bot.db.fetchone("SELECT * FROM tong_mon WHERE id=?", (int(ten),))
        if not tm:
            tm = await self.bot.db.fetchone("SELECT * FROM tong_mon WHERE name=?", (ten.strip(),))
        if not tm: await ctx.send(embed=error(f"Không tìm thấy Tông Môn **{ten}**!")); return

        await self.bot.db.update_player(ctx.author.id, sect_apply_id=tm["id"])
        await ctx.send(
            f"📨 **{player['name']}** đã gửi đơn xin gia nhập **{tm['name']}**!\n"
            f"_Tông Chủ/Phó dùng `,tl sect accept @{ctx.author.display_name}` để duyệt._"
        )

    # ══ ACCEPT ═════════════════════════════════════════════
    @sect.command(name="accept", aliases=["chapnhan", "duyet"])
    async def accept(self, ctx, member: discord.Member = None):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player: await ctx.send(embed=warn("Chưa nhập môn!")); return
        tm_id = _safe(player, "tong_mon_id")
        if not tm_id: await ctx.send(embed=warn("Bạn chưa có Tông Môn!")); return
        tm = await self.bot.db.fetchone("SELECT * FROM tong_mon WHERE id=?", (tm_id,))
        if _rank(player, tm) < 2: await ctx.send(embed=warn("Chỉ **Tông Chủ/Phó** mới duyệt đơn!")); return
        if not member: await ctx.send(embed=warn("Dùng: `,tl sect accept @người`")); return

        target = await self.bot.db.get_player(member.id)
        if not target: await ctx.send(embed=error("Người này chưa nhập môn!")); return
        if _safe(target, "tong_mon_id"): await ctx.send(embed=warn("Người này đã có Tông Môn rồi!")); return
        if _safe(target, "sect_apply_id") != tm_id:
            await ctx.send(embed=warn("Người này chưa gửi đơn vào Tông Môn của bạn!")); return

        max_m = _max_members(tm)
        cnt = await self.bot.db.fetchone("SELECT COUNT(*) as c FROM players WHERE tong_mon_id=?", (tm_id,))
        if cnt and cnt["c"] >= max_m:
            await ctx.send(embed=warn(f"Tông Môn đầy {max_m} thành viên! Nâng cấp **Đại Điện** để mở rộng.")); return

        await self.bot.db.update_player(member.id, tong_mon_id=tm_id, sect_apply_id=None, sect_rank=0)
        await ctx.send(embed=success(f"✅ **{target['name']}** gia nhập **{tm['name']}**!"))

    # ══ REJECT ═════════════════════════════════════════════
    @sect.command(name="reject", aliases=["tuchoi"])
    async def reject(self, ctx, member: discord.Member = None):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player: await ctx.send(embed=warn("Chưa nhập môn!")); return
        tm_id = _safe(player, "tong_mon_id")
        if not tm_id: await ctx.send(embed=warn("Bạn chưa có Tông Môn!")); return
        tm = await self.bot.db.fetchone("SELECT * FROM tong_mon WHERE id=?", (tm_id,))
        if _rank(player, tm) < 2: await ctx.send(embed=warn("Chỉ **Tông Chủ/Phó** mới từ chối đơn!")); return
        if not member: await ctx.send(embed=warn("Dùng: `,tl sect reject @người`")); return

        target = await self.bot.db.get_player(member.id)
        if not target or _safe(target, "sect_apply_id") != tm_id:
            await ctx.send(embed=warn("Không có đơn của người này!")); return
        await self.bot.db.update_player(member.id, sect_apply_id=None)
        await ctx.send(embed=info("❌ TỪ CHỐI", f"Đã từ chối đơn của **{target['name']}**."))

    # ══ APPS ═══════════════════════════════════════════════
    @sect.command(name="apps", aliases=["donxin", "don"])
    async def apps(self, ctx):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player: await ctx.send(embed=warn("Chưa nhập môn!")); return
        tm_id = _safe(player, "tong_mon_id")
        if not tm_id: await ctx.send(embed=warn("Chưa gia nhập Tông Môn!")); return
        tm = await self.bot.db.fetchone("SELECT * FROM tong_mon WHERE id=?", (tm_id,))
        if _rank(player, tm) < 2: await ctx.send(embed=warn("Chỉ **Phó Tông Chủ** trở lên mới xem đơn!")); return

        rows = await self.bot.db.fetchall(
            "SELECT * FROM players WHERE sect_apply_id=? LIMIT 20", (tm_id,)
        )
        embed = discord.Embed(title=f"📋 ĐƠN XIN GIA NHẬP — {tm['name']}", color=0x8B4513)
        if not rows:
            embed.description = "_Không có đơn nào đang chờ duyệt_"
        else:
            lines = [f"{i+1}. **{m['name']}** — {get_realm_name(m)}" for i, m in enumerate(rows)]
            embed.description = "\n".join(lines)
        embed.set_footer(text=",tl sect accept @Tag | ,tl sect reject @Tag")
        await ctx.send(embed=embed)

    # ══ LEAVE ══════════════════════════════════════════════
    @sect.command(name="leave", aliases=["roi", "thoat"])
    async def leave(self, ctx):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player: await ctx.send(embed=warn("Chưa nhập môn!")); return
        tm_id = _safe(player, "tong_mon_id")
        if not tm_id: await ctx.send(embed=warn("Chưa gia nhập Tông Môn!")); return
        tm = await self.bot.db.fetchone("SELECT * FROM tong_mon WHERE id=?", (tm_id,))
        if tm and tm["leader_id"] == str(ctx.author.id):
            await ctx.send(embed=warn("Tông Chủ không thể rời! Nhượng chức (`,tl sect transfer @Tag`) hoặc giải tán trước.")); return
        await self.bot.db.update_player(ctx.author.id, tong_mon_id=None, sect_rank=0)
        tname = tm["name"] if tm else "Tông Môn"
        await ctx.send(embed=success(f"👋 Đã rời **{tname}**!\n_Cống hiến sẽ bị mất khi rời._"))

    # ══ KICK ═══════════════════════════════════════════════
    @sect.command(name="kick", aliases=["trucxuat", "duc"])
    async def kick(self, ctx, member: discord.Member = None):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player: await ctx.send(embed=warn("Chưa nhập môn!")); return
        tm_id = _safe(player, "tong_mon_id")
        if not tm_id: await ctx.send(embed=warn("Chưa gia nhập Tông Môn!")); return
        tm = await self.bot.db.fetchone("SELECT * FROM tong_mon WHERE id=?", (tm_id,))
        if _rank(player, tm) < 2: await ctx.send(embed=warn("Chỉ **Tông Chủ/Phó** mới trục xuất!")); return
        if not member: await ctx.send(embed=warn("Dùng: `,tl sect kick @người`")); return
        if member.id == ctx.author.id: await ctx.send(embed=warn("Không kick chính mình!")); return

        target = await self.bot.db.get_player(member.id)
        if not target or _safe(target, "tong_mon_id") != tm_id:
            await ctx.send(embed=error("Người này không trong Tông Môn!")); return
        if str(member.id) == str(tm["leader_id"]):
            await ctx.send(embed=warn("Không thể trục xuất Tông Chủ!")); return
        if _rank(player, tm) == 2 and _safe(target, "sect_rank", 0) >= 2:
            await ctx.send(embed=warn("Phó Tông Chủ không thể kick Phó Tông Chủ khác!")); return

        await self.bot.db.update_player(member.id, tong_mon_id=None, sect_rank=0)
        await ctx.send(embed=success(f"⚡ **{target['name']}** bị trục xuất khỏi **{tm['name']}**!"))

    # ══ TRANSFER ═══════════════════════════════════════════
    @sect.command(name="transfer", aliases=["nhuong", "giaoquyen"])
    async def transfer(self, ctx, member: discord.Member = None):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player: await ctx.send(embed=warn("Chưa nhập môn!")); return
        tm_id = _safe(player, "tong_mon_id")
        tm = await self.bot.db.fetchone("SELECT * FROM tong_mon WHERE id=?", (tm_id,))
        if not tm or tm["leader_id"] != str(ctx.author.id):
            await ctx.send(embed=warn("Chỉ **Tông Chủ** mới chuyển nhượng!")); return
        if not member: await ctx.send(embed=warn("Dùng: `,tl sect transfer @người`")); return

        target = await self.bot.db.get_player(member.id)
        if not target or _safe(target, "tong_mon_id") != tm_id:
            await ctx.send(embed=error("Người này không trong Tông Môn!")); return

        await self.bot.db.execute("UPDATE tong_mon SET leader_id=? WHERE id=?", (str(member.id), tm_id))
        await self.bot.db.update_player(member.id, sect_rank=3)
        await self.bot.db.update_player(ctx.author.id, sect_rank=2)
        await ctx.send(embed=success(
            f"👑 Nhường chức **Tông Chủ** cho **{target['name']}**!\n"
            f"_{player['name']}_ trở thành **Phó Tông Chủ**."
        ))

    # ══ DISBAND ════════════════════════════════════════════
    @sect.command(name="disband", aliases=["giaitan"])
    async def disband(self, ctx, confirm: str = None):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player: await ctx.send(embed=warn("Chưa nhập môn!")); return
        tm_id = _safe(player, "tong_mon_id")
        tm = await self.bot.db.fetchone("SELECT * FROM tong_mon WHERE id=?", (tm_id,))
        if not tm or tm["leader_id"] != str(ctx.author.id):
            await ctx.send(embed=warn("Chỉ **Tông Chủ** mới giải tán Tông Môn!")); return

        if confirm != "confirm":
            await ctx.send(embed=warn(
                f"⚠️ XÁC NHẬN GIẢI TÁN **{tm['name']}**?\n\n"
                f"Tất cả thành viên sẽ bị đẩy ra, ngân quỹ mất trắng.\n"
                f"Gõ `,tl sect disband confirm` để xác nhận!"
            )); return

        tname = tm["name"]
        await self.bot.db.execute(
            "UPDATE players SET tong_mon_id=NULL, sect_rank=0 WHERE tong_mon_id=?", (tm_id,)
        )
        await self.bot.db.execute("DELETE FROM tong_mon WHERE id=?", (tm_id,))
        await ctx.send(embed=success(f"💀 Tông Môn **{tname}** đã bị giải tán!"))

    # ══ MEMBERS ════════════════════════════════════════════
    @sect.command(name="members", aliases=["thanhvien", "ds"])
    async def members(self, ctx):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player: await ctx.send(embed=warn("Chưa nhập môn!")); return
        tm_id = _safe(player, "tong_mon_id")
        if not tm_id: await ctx.send(embed=warn("Chưa gia nhập Tông Môn!")); return
        tm = await self.bot.db.fetchone("SELECT * FROM tong_mon WHERE id=?", (tm_id,))
        members_list = await self.bot.db.fetchall(
            "SELECT * FROM players WHERE tong_mon_id=? ORDER BY sect_rank DESC, realm_index DESC LIMIT 50",
            (tm_id,)
        )
        max_m = _max_members(tm)
        embed = discord.Embed(
            title=f"⛩️ {tm['name']} — Thành Viên ({len(members_list)}/{max_m})",
            color=0x8B4513
        )
        lines = []
        for i, m in enumerate(members_list, 1):
            r = 3 if m["user_id"] == tm["leader_id"] else _safe(m, "sect_rank", 0)
            lc = _safe(m, "luc_chien", 0) or _safe(m, "atk", 0)
            lc_str = f"| LC: `{lc/1e3:.1f}K`" if lc >= 1000 else ""
            lines.append(f"{i}. {RANK_EMOJI[r]} **{m['name']}** *({RANK_NAMES[r]})* — {get_realm_name(m)} {lc_str}")
        embed.description = "\n".join(lines) if lines else "_Không có thành viên_"
        await ctx.send(embed=embed)

    # ══ MISSION ════════════════════════════════════════════
    @sect.command(name="mission", aliases=["nhiemvu", "nv"])
    async def mission(self, ctx):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player: await ctx.send(embed=warn("Chưa nhập môn!")); return
        tm_id = _safe(player, "tong_mon_id")
        if not tm_id: await ctx.send(embed=warn("Chưa gia nhập Tông Môn!")); return
        tm = await self.bot.db.fetchone("SELECT * FROM tong_mon WHERE id=?", (tm_id,))

        today = now().strftime("%Y-%m-%d")
        if str(_safe(player, "sect_mission_date", "")) == today:
            await ctx.send(embed=warn("Đã hoàn thành nhiệm vụ Tông Môn hôm nay! Reload lúc 00:00.")); return

        lv = _safe(tm, "level", 1)
        missions = ["☁️ Luyện đan 3 lần", "⚔️ Đánh boss 1 lần", "🧘 Bế quan 1 giờ",
                    "🛒 Mua 1 vật phẩm tại cửa hàng", "🏹 Thám hiểm 1 lần"]
        task       = random.choice(missions)
        exp_bonus  = 2_000 * lv
        lt_bonus   = 10_000 * lv

        await self.bot.db.update_player(ctx.author.id,
            sect_mission_date=today,
            exp=_safe(player, "exp", 0) + exp_bonus,
            linh_thach_ha=_safe(player, "linh_thach_ha") + lt_bonus
        )
        await self.bot.db.execute("UPDATE tong_mon SET exp=exp+500 WHERE id=?", (tm_id,))

        embed = success("📋 NHIỆM VỤ TÔNG MÔN")
        embed.description = (
            f"📌 Nhiệm vụ: **{task}**\n\n"
            f"✅ Hoàn thành! Phần thưởng:\n"
            f"✨ +**{exp_bonus:,}** EXP\n"
            f"💰 +**{lt_bonus:,}** Hạ LT\n"
            f"🏯 +500 EXP Tông Môn"
        )
        await ctx.send(embed=embed)

    # ══ TUYÊN CHIẾN (khai chiến trước 5 phút) ══════════════
    @sect.command(name="tuyenchien", aliases=["war", "declare"])
    async def tuyenchien(self, ctx, zone_id: str = None):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player: await ctx.send(embed=warn("Chưa nhập môn!")); return
        tm_id = _safe(player, "tong_mon_id")
        if not tm_id: await ctx.send(embed=warn("Chưa gia nhập Tông Môn!")); return
        tm = await self.bot.db.fetchone("SELECT * FROM tong_mon WHERE id=?", (tm_id,))
        if _rank(player, tm) < 2:
            await ctx.send(embed=warn("Chỉ **Tông Chủ/Phó** mới tuyên chiến!")); return

        if not zone_id or zone_id.lower() not in MAP_ZONES:
            lines = [f"`{k}` — **{v}**" for k, v in MAP_ZONES.items()]
            embed = info("🗺️ DANH SÁCH VÙNG ĐẤT", "\n".join(lines))
            embed.set_footer(text="Dùng: ,tl sect tuyenchien [ID_vùng]  •  ID lấy từ ,tl map")
            await ctx.send(embed=embed); return

        zone_id = zone_id.lower()
        zone_name = MAP_ZONES[zone_id]

        # Tìm Tông Môn đang giữ vùng này
        all_tms = await self.bot.db.fetchall("SELECT * FROM tong_mon WHERE lanh_dia IS NOT NULL")
        enemy_tm = None
        for atm in all_tms:
            ld_raw = atm.get("lanh_dia") or ""
            try:
                ld = json.loads(ld_raw) if ld_raw.startswith("{") else {}
            except Exception:
                ld = {}
            if zone_id in ld and atm["id"] != tm_id:
                enemy_tm = atm
                break

        if not enemy_tm:
            await ctx.send(embed=warn(
                f"Vùng **{zone_name}** không có Tông Môn nào đang giữ!\n"
                f"Dùng `,tl sect congkich {zone_id}` để chiếm thẳng."
            )); return

        # Lưu trạng thái tuyên chiến với timestamp
        import time
        wars = _get_wars(tm)
        wars[zone_id] = {
            "enemy_id": enemy_tm["id"],
            "enemy_name": enemy_tm["name"],
            "declared_at": int(time.time())
        }
        await self.bot.db.execute(
            "UPDATE tong_mon SET active_wars=? WHERE id=?",
            (json.dumps(wars), tm_id)
        )
        embed = discord.Embed(title="🎺 TUYÊN CHIẾN!", color=0xFF4444)
        embed.description = (
            f"**{tm['name']}** tuyên chiến với **{enemy_tm['name']}**\n"
            f"về vùng đất 📍 **{zone_name}**!\n\n"
            f"⏳ Chờ **5 phút** sau đó dùng:\n"
            f"`,tl sect congkich {zone_id}` để tấn công!"
        )
        embed.set_footer(text="Tuyên chiến xong mới được công kích!")
        await ctx.send(embed=embed)

    # ══ CÔNG KÍCH (bình thường & auto) ════════════════════
    @sect.command(name="congkich", aliases=["attack", "ck"])
    async def congkich(self, ctx, zone_id: str = None, mode: str = "normal"):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player: await ctx.send(embed=warn("Chưa nhập môn!")); return
        tm_id = _safe(player, "tong_mon_id")
        if not tm_id: await ctx.send(embed=warn("Chưa gia nhập Tông Môn!")); return
        tm = await self.bot.db.fetchone("SELECT * FROM tong_mon WHERE id=?", (tm_id,))
        if _rank(player, tm) < 2:
            await ctx.send(embed=warn("Chỉ **Tông Chủ/Phó** mới chỉ huy công kích!")); return

        if not zone_id or zone_id.lower() not in MAP_ZONES:
            lines = [f"`{k}` — **{v}**" for k, v in MAP_ZONES.items()]
            embed = info("🗺️ DANH SÁCH VÙNG ĐẤT", "\n".join(lines))
            embed.set_footer(text="Dùng: ,tl sect congkich [ID_vùng] [normal/auto]")
            await ctx.send(embed=embed); return

        zone_id   = zone_id.lower()
        zone_name = MAP_ZONES[zone_id]
        mode      = mode.lower()
        import time

        # Lấy lanh_dia của TM hiện tại
        ld_raw = tm.get("lanh_dia") or "{}"
        try:
            my_ld = json.loads(ld_raw)
        except Exception:
            my_ld = {}

        # Tìm Tông Môn đang chiếm vùng này
        all_tms = await self.bot.db.fetchall("SELECT * FROM tong_mon WHERE lanh_dia IS NOT NULL")
        owner_tm = None
        for atm in all_tms:
            try:
                ld = json.loads(atm.get("lanh_dia") or "{}")
            except Exception:
                ld = {}
            if zone_id in ld:
                if atm["id"] == tm_id:
                    await ctx.send(embed=warn(f"Tông Môn bạn đã chiếm **{zone_name}** rồi!")); return
                owner_tm = atm
                break

        # Nếu có kẻ địch → cần kiểm tra tuyên chiến trước
        if owner_tm:
            wars = _get_wars(tm)
            war_info = wars.get(zone_id)
            if not war_info:
                await ctx.send(embed=warn(
                    f"Phải **tuyên chiến** trước!\n"
                    f"Dùng: `,tl sect tuyenchien {zone_id}`\n"
                    f"_Chờ 5 phút sau mới công kích được._"
                )); return
            declared_at = war_info.get("declared_at", 0)
            elapsed = int(time.time()) - declared_at
            if elapsed < TUYENCHIEN_DURATION:
                remain = TUYENCHIEN_DURATION - elapsed
                mins, secs = divmod(remain, 60)
                await ctx.send(embed=warn(
                    f"Chưa đến giờ tấn công!\n"
                    f"⏳ Còn **{mins} phút {secs} giây** nữa mới được công kích."
                )); return

        # ── AUTO MODE ──────────────────────────────────────
        if mode in ("auto", "a"):
            embed = discord.Embed(title=f"🤖 AUTO CÔNG KÍCH — {zone_name}", color=0xFF6600)
            rounds = []
            success_count = 0
            blds = _get_buildings(tm)
            def_lv = blds.get("defense", 0)

            for rd in range(1, 6):
                atk_power = _safe(tm, "level", 1) + def_lv + random.randint(0, 10)
                def_power = (_safe(owner_tm, "level", 1) if owner_tm else 0) + random.randint(0, 8)
                won = atk_power > def_power
                if won:
                    success_count += 1
                rounds.append(f"Round {rd}: {'✅ Thắng' if won else '❌ Thua'} *({atk_power} vs {def_power})*")

            won_war = success_count >= 3
            if won_war:
                if owner_tm:
                    try:
                        enemy_ld = json.loads(owner_tm.get("lanh_dia") or "{}")
                    except Exception:
                        enemy_ld = {}
                    enemy_ld.pop(zone_id, None)
                    await self.bot.db.execute(
                        "UPDATE tong_mon SET lanh_dia=? WHERE id=?",
                        (json.dumps(enemy_ld), owner_tm["id"])
                    )
                my_ld[zone_id] = {"conquered_at": int(time.time())}
                await self.bot.db.execute(
                    "UPDATE tong_mon SET lanh_dia=? WHERE id=?",
                    (json.dumps(my_ld), tm_id)
                )
                # Xóa chiến tranh
                wars = _get_wars(tm)
                wars.pop(zone_id, None)
                await self.bot.db.execute(
                    "UPDATE tong_mon SET active_wars=? WHERE id=?",
                    (json.dumps(wars), tm_id)
                )
            embed.description = "\n".join(rounds)
            embed.add_field(
                name="📊 Kết Quả",
                value=(
                    f"Thắng: {success_count}/5 round\n"
                    f"{'🏆 **CHIẾM THÀNH CÔNG!**' if won_war else '💀 **THẤT BẠI!**'}\n"
                    f"{'📍 ' + zone_name + ' thuộc về ' + tm['name'] if won_war else '_Thử lại sau_'}"
                ),
                inline=False
            )
            await ctx.send(embed=embed)
            return

        # ── NORMAL MODE ────────────────────────────────────
        blds    = _get_buildings(tm)
        def_lv  = blds.get("defense", 0)
        atk_pow = _safe(tm, "level", 1) + def_lv + random.randint(0, 15)
        def_pow = (_safe(owner_tm, "level", 1) if owner_tm else 0) + random.randint(0, 10)
        won     = atk_pow > def_pow

        if won:
            if owner_tm:
                try:
                    enemy_ld = json.loads(owner_tm.get("lanh_dia") or "{}")
                except Exception:
                    enemy_ld = {}
                enemy_ld.pop(zone_id, None)
                await self.bot.db.execute(
                    "UPDATE tong_mon SET lanh_dia=? WHERE id=?",
                    (json.dumps(enemy_ld), owner_tm["id"])
                )
            my_ld[zone_id] = {"conquered_at": int(time.time())}
            await self.bot.db.execute(
                "UPDATE tong_mon SET lanh_dia=? WHERE id=?",
                (json.dumps(my_ld), tm_id)
            )
            wars = _get_wars(tm)
            wars.pop(zone_id, None)
            await self.bot.db.execute(
                "UPDATE tong_mon SET active_wars=? WHERE id=?",
                (json.dumps(wars), tm_id)
            )
            embed = success("⚔️ CÔNG KÍCH THÀNH CÔNG!")
            embed.description = (
                f"📍 **{zone_name}** giờ thuộc về **{tm['name']}**!\n"
                f"⚡ Sức tấn công: `{atk_pow}` vs Phòng thủ: `{def_pow}`"
            )
        else:
            embed = error("💀 CÔNG KÍCH THẤT BẠI!")
            embed.description = (
                f"📍 **{zone_name}** được phòng thủ vững chắc!\n"
                f"⚡ Sức tấn công: `{atk_pow}` vs Phòng thủ: `{def_pow}`\n"
                f"_Nâng cấp **Đại Trận Hộ Tông** để tăng sức mạnh._"
            )
        await ctx.send(embed=embed)

    # ══ BEAST ══════════════════════════════════════════════
    @sect.command(name="beast", aliases=["thanhthu"])
    async def beast(self, ctx, zone_id: str = None, loai: str = "trieu"):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player: await ctx.send(embed=warn("Chưa nhập môn!")); return
        tm_id = _safe(player, "tong_mon_id")
        if not tm_id: await ctx.send(embed=warn("Chưa gia nhập Tông Môn!")); return
        tm = await self.bot.db.fetchone("SELECT * FROM tong_mon WHERE id=?", (tm_id,))
        if _rank(player, tm) < 2: await ctx.send(embed=warn("Chỉ **Tông Chủ/Phó** mới điều phối Thần Thú!")); return
        if not zone_id or zone_id.lower() not in MAP_ZONES:
            await ctx.send(embed=warn("Dùng: `,tl sect beast [ID_vùng] [trieu/nangcap]`\nXem vùng: `,tl map`")); return

        zone_name = MAP_ZONES[zone_id.lower()]
        loai = loai.lower()
        beasts = ["🐉 Hỏa Long", "🦁 Linh Sư", "🦅 Thần Điêu", "🐢 Huyền Quy"]
        beast  = random.choice(beasts)
        cost   = 100_000 if loai == "nangcap" else 50_000
        action = "Nâng cấp" if loai == "nangcap" else "Triệu hồi"

        if _safe(player, "linh_thach_ha") < cost:
            await ctx.send(embed=warn(f"Cần **{cost:,} Hạ LT** để {action.lower()} Thần Thú!")); return
        await self.bot.db.update_player(ctx.author.id, linh_thach_ha=_safe(player, "linh_thach_ha") - cost)

        embed = success(f"🐉 {action.upper()} THẦN THÚ")
        embed.description = (
            f"{beast} được {action.lower()} tại 📍 **{zone_name}**!\n"
            f"💰 -{cost:,} Hạ LT\n"
            f"🛡️ +20% Phòng Thủ Lãnh Địa"
        )
        await ctx.send(embed=embed)

    # ══ TUBO ═══════════════════════════════════════════════
    @sect.command(name="tubo", aliases=["tranphap", "tp"])
    async def tubo(self, ctx, zone_id: str = None, lt: int = None):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player: await ctx.send(embed=warn("Chưa nhập môn!")); return
        tm_id = _safe(player, "tong_mon_id")
        if not tm_id: await ctx.send(embed=warn("Chưa gia nhập Tông Môn!")); return
        tm = await self.bot.db.fetchone("SELECT * FROM tong_mon WHERE id=?", (tm_id,))
        if _rank(player, tm) < 1: await ctx.send(embed=warn("Cần ít nhất **Trưởng Lão** để bơm Trận Pháp!")); return
        if not zone_id or zone_id.lower() not in MAP_ZONES:
            await ctx.send(embed=warn("Dùng: `,tl sect tubo [ID_vùng] [số LT]`\nXem vùng: `,tl map`")); return
        if not lt or lt <= 0: await ctx.send(embed=warn("Nhập số LT muốn đầu tư!")); return
        if _safe(player, "linh_thach_ha") < lt:
            await ctx.send(embed=warn(f"Không đủ LT! Cần **{lt:,}** Hạ LT.")); return

        zone_name = MAP_ZONES[zone_id.lower()]
        await self.bot.db.update_player(ctx.author.id, linh_thach_ha=_safe(player, "linh_thach_ha") - lt)
        def_bonus = min(lt // 10_000, 50)

        embed = success("🔱 BƠM TRẬN PHÁP")
        embed.description = (
            f"💰 -{lt:,} Hạ LT đầu tư vào 📍 **{zone_name}**\n"
            f"🛡️ +{def_bonus}% Phòng Thủ Lãnh Địa *(tối đa +50%)*"
        )
        await ctx.send(embed=embed)

    # ══ SHOP ═══════════════════════════════════════════════
    @sect.command(name="shop", aliases=["cuahang"])
    async def shop(self, ctx):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player: await ctx.send(embed=warn("Chưa nhập môn!")); return
        tm_id = _safe(player, "tong_mon_id")
        if not tm_id: await ctx.send(embed=warn("Chưa gia nhập Tông Môn!")); return
        tm = await self.bot.db.fetchone("SELECT * FROM tong_mon WHERE id=?", (tm_id,))

        blds     = _get_buildings(tm)
        shop_lv  = blds.get("shop", 0)
        if shop_lv == 0:
            await ctx.send(embed=warn("Cần xây **Bảo Khố Tông Môn** trước!\nDùng: `,tl sect upgrade shop`")); return

        SHOP_ITEMS = [
            ("🧪 Tông Môn Đan",         20_000, "EXP +500, HP +20%",          1),
            ("⚔️ Tông Môn Lệnh",        50_000, "+10% Chiến Đấu 1 ngày",      2),
            ("📜 Truyền Thừa Bí Lục",  100_000, "+5% tất cả chỉ số vĩnh viễn", 3),
            ("🏮 Tông Môn Linh Phù",    30_000, "Tăng 20% EXP Tu Vi 1 giờ",   1),
            ("💎 Tông Môn Tinh Thạch", 200_000, "+10% Drop Rate 3 ngày",       4),
            ("🌀 Bí Cảnh Lệnh",        500_000, "Vào Bí Cảnh Tông Môn",       5),
        ]
        embed = discord.Embed(
            title=f"🏪 CỬA HÀNG TÔNG MÔN — Tier {shop_lv}",
            color=0x8B4513
        )
        lines = []
        for name, price, desc, req_tier in SHOP_ITEMS:
            if shop_lv >= req_tier:
                lines.append(f"• **{name}** — `{price:,}` Hạ LT\n  _{desc}_")
            else:
                lines.append(f"• ~~{name}~~ — _Cần Bảo Khố Lv.{req_tier}_")
        embed.description = "\n".join(lines)
        embed.set_footer(text=f"Nâng cấp Bảo Khố: ,tl sect upgrade shop  •  Tu Tiên Bot v6")
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(TongMon(bot))

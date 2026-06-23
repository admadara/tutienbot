"""cogs/events.py — Sự kiện theo mùa v1"""
import discord
from discord.ext import commands
import datetime, time, random

from utils.embeds import success, warn, error, fmt

# ══════════════════════════════════════════════════════════
#  ĐỊNH NGHĨA SỰ KIỆN THEO MÙA
#  start/end: (tháng, ngày)  — so sánh theo giờ VN (UTC+7)
# ══════════════════════════════════════════════════════════
SEASONAL_EVENTS = [
    {
        "id": "tet_nguyen_dan",
        "name": "🧧 Tết Nguyên Đán",
        "start": (1, 1), "end": (1, 15),
        "color": 0xE53935,
        "desc": (
            "Xuân về! Hái lộc nhận Hồng Bao may mắn.\n"
            "Mỗi ngày dùng `,tl hailoc` nhận thưởng đặc biệt."
        ),
        "cmd": "hailoc",
        "reward_ha":    200_000,
        "reward_trung": 5,
        "reward_exp":   500_000,
        "cooldown_h":   22,
        "icon": "🧧",
    },
    {
        "id": "thanh_minh",
        "name": "🌸 Tiết Thanh Minh",
        "start": (4, 4), "end": (4, 6),
        "color": 0x66BB6A,
        "desc": (
            "Mùa xuân hoa nở, linh khí đất trời sung mãn.\n"
            "Tu luyện trong 3 ngày này nhận **+50% EXP**."
        ),
        "cmd": None,
        "exp_bonus": 1.5,
        "icon": "🌸",
    },
    {
        "id": "trung_thu",
        "name": "🌕 Tết Trung Thu",
        "start": (9, 25), "end": (10, 5),
        "color": 0xFFA726,
        "desc": (
            "Trăng rằm tháng Tám, linh thạch rơi khắp nơi.\n"
            "Dùng `,tl banh_truoc` để nhận Bánh Trăng Thần Bí."
        ),
        "cmd": "banh_truoc",
        "reward_ha":    500_000,
        "reward_trung": 10,
        "reward_exp":   1_000_000,
        "cooldown_h":   22,
        "icon": "🌕",
    },
    {
        "id": "halloween",
        "name": "🎃 Quỷ Dạ Ma Vương",
        "start": (10, 28), "end": (11, 1),
        "color": 0xFF6F00,
        "desc": (
            "Âm khí xung thiên! Ma quỷ tràn ra khắp nơi.\n"
            "Dùng `,tl trick_or_treat` thách thức quỷ nhận thưởng."
        ),
        "cmd": "trick_or_treat",
        "reward_ha":    300_000,
        "reward_trung": 8,
        "reward_exp":   800_000,
        "cooldown_h":   22,
        "icon": "🎃",
    },
    {
        "id": "giang_sinh",
        "name": "🎄 Giáng Sinh Tu Tiên",
        "start": (12, 24), "end": (12, 27),
        "color": 0x43A047,
        "desc": (
            "Tuyết trắng phủ kín Tiên Giới. Ông Già Tuyết tặng quà!\n"
            "Dùng `,tl mo_qua` để mở hộp quà Giáng Sinh."
        ),
        "cmd": "mo_qua",
        "reward_ha":    1_000_000,
        "reward_trung": 20,
        "reward_exp":   2_000_000,
        "cooldown_h":   22,
        "icon": "🎄",
    },
    {
        "id": "nam_moi",
        "name": "🎆 Năm Mới Dương Lịch",
        "start": (12, 31), "end": (1, 2),
        "color": 0xAB47BC,
        "desc": (
            "Pháo hoa nở rộ trên Thiên Đình!\n"
            "Dùng `,tl dem_giao_thua` để đón năm mới và nhận đặc thưởng."
        ),
        "cmd": "dem_giao_thua",
        "reward_ha":    2_000_000,
        "reward_trung": 50,
        "reward_exp":   5_000_000,
        "cooldown_h":   22,
        "icon": "🎆",
    },
]

# ══ Helpers ═══════════════════════════════════════════════

def _vn_now() -> datetime.datetime:
    return datetime.datetime.utcnow() + datetime.timedelta(hours=7)

def _get_active_events() -> list:
    dt = _vn_now()
    month, day = dt.month, dt.day
    active = []
    for ev in SEASONAL_EVENTS:
        sm, sd = ev["start"]
        em, ed = ev["end"]
        # Xử lý wrap-around qua năm (vd: 12/31 → 1/2)
        if sm <= em:
            if (month, day) >= (sm, sd) and (month, day) <= (em, ed):
                active.append(ev)
        else:  # wrap qua năm mới
            if (month, day) >= (sm, sd) or (month, day) <= (em, ed):
                active.append(ev)
    return active

def _event_exp_bonus() -> float:
    """Trả về hệ số EXP bonus lớn nhất từ các sự kiện đang diễn ra."""
    best = 1.0
    for ev in _get_active_events():
        best = max(best, ev.get("exp_bonus", 1.0))
    return best

# ══════════════════════════════════════════════════════════
class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        await self.bot.db.execute("""
            CREATE TABLE IF NOT EXISTS event_claims (
                user_id   TEXT NOT NULL,
                event_id  TEXT NOT NULL,
                claimed_at INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (user_id, event_id)
            )
        """)

    # ── Xem sự kiện hiện tại ─────────────────────────────
    @commands.command(name="le_hoi", aliases=["lehoi","seasonal"])
    async def sukien(self, ctx):
        active = _get_active_events()
        dt = _vn_now()

        if not active:
            # Tìm sự kiện gần nhất sắp tới
            upcoming = []
            for ev in SEASONAL_EVENTS:
                sm, sd = ev["start"]
                next_start = datetime.datetime(dt.year, sm, sd)
                if next_start < dt:
                    next_start = datetime.datetime(dt.year + 1, sm, sd)
                upcoming.append((next_start, ev))
            upcoming.sort(key=lambda x: x[0])
            embed = discord.Embed(
                title="📅 SỰ KIỆN THEO MÙA",
                description="Hiện tại không có sự kiện nào đang diễn ra.",
                color=0x607D8B
            )
            if upcoming:
                nxt_dt, nxt = upcoming[0]
                days_left = (nxt_dt - dt).days
                embed.add_field(
                    name=f"🔔 Sắp tới: {nxt['name']}",
                    value=f"Bắt đầu ngày **{nxt['start'][1]}/{nxt['start'][0]}** (còn ~{days_left} ngày)",
                    inline=False
                )
            embed.set_footer(text="Tu Tiên Bot  •  Sự kiện cập nhật theo lịch thực")
            await ctx.send(embed=embed); return

        embed = discord.Embed(
            title="🎉 SỰ KIỆN ĐANG DIỄN RA",
            color=active[0]["color"]
        )
        for ev in active:
            cmd_hint = f"\n✨ Lệnh: `,tl {ev['cmd']}`" if ev.get("cmd") else ""
            bonus_hint = f"\n📚 EXP Bonus: **×{ev.get('exp_bonus',1.0):.1f}**" if ev.get("exp_bonus",1.0) > 1 else ""
            thoi_gian = f"{ev['start'][1]}/{ev['start'][0]} — {ev['end'][1]}/{ev['end'][0]}"
            embed.add_field(
                name=f"{ev['icon']} {ev['name']}  ({thoi_gian})",
                value=ev["desc"] + cmd_hint + bonus_hint,
                inline=False
            )
        embed.set_footer(text=f"Giờ VN: {dt.strftime('%H:%M %d/%m/%Y')}  •  ,tl le_hoi")
        await ctx.send(embed=embed)

    # ── Hàm chung xử lý nhận thưởng sự kiện ─────────────
    async def _claim_event(self, ctx, event_id: str):
        ev = next((e for e in SEASONAL_EVENTS if e["id"] == event_id), None)
        active = _get_active_events()
        if not ev or ev not in active:
            await ctx.send(embed=warn("Sự kiện này chưa diễn ra hoặc đã kết thúc!")); return

        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return

        now_ts = int(time.time())
        row = await self.bot.db.fetchone(
            "SELECT * FROM event_claims WHERE user_id=? AND event_id=?",
            (str(ctx.author.id), event_id)
        )
        cd_secs = ev.get("cooldown_h", 22) * 3600
        if row and (now_ts - row["claimed_at"]) < cd_secs:
            rem = cd_secs - (now_ts - row["claimed_at"])
            h, m = divmod(rem // 60, 60)
            await ctx.send(embed=warn(
                f"Đã nhận rồi! Quay lại sau **{h}h {m}m** nữa."
            )); return

        # Phần thưởng ngẫu nhiên ±20%
        def rng(base): return int(base * random.uniform(0.8, 1.2)) if base else 0
        ha   = rng(ev.get("reward_ha",  0))
        trg  = rng(ev.get("reward_trung",0))
        exp_ = rng(ev.get("reward_exp", 0))

        await self.bot.db.update_player(ctx.author.id,
            linh_thach_ha   = int(player.get("linh_thach_ha",   0)) + ha,
            linh_thach_trung= int(player.get("linh_thach_trung",0)) + trg,
            exp             = int(player.get("exp",             0)) + exp_,
        )
        # Upsert claim
        await self.bot.db.execute("""
            INSERT INTO event_claims (user_id, event_id, claimed_at) VALUES (?,?,?)
            ON CONFLICT(user_id, event_id) DO UPDATE SET claimed_at=excluded.claimed_at
        """, (str(ctx.author.id), event_id, now_ts))

        lines = []
        if ha:   lines.append(f"💰 +**{ha:,}** Hạ LT")
        if trg:  lines.append(f"💎 +**{trg:,}** Trung LT")
        if exp_: lines.append(f"📚 +**{fmt(exp_)}** EXP")
        embed = success(
            f"{ev['icon']} {ev['name']} — Đã Nhận Thưởng!",
            "\n".join(lines) or "Không có phần thưởng."
        )
        embed.set_footer(text=f"Quay lại sau {ev.get('cooldown_h',22)}h  •  ,tl sukien")
        await ctx.send(embed=embed)

    # ── Các lệnh nhận thưởng theo từng sự kiện ───────────
    @commands.command(name="hailoc")
    async def hailoc(self, ctx):
        await self._claim_event(ctx, "tet_nguyen_dan")

    @commands.command(name="banh_truoc")
    async def banh_truoc(self, ctx):
        await self._claim_event(ctx, "trung_thu")

    @commands.command(name="trick_or_treat")
    async def trick_or_treat(self, ctx):
        await self._claim_event(ctx, "halloween")

    @commands.command(name="mo_qua")
    async def mo_qua(self, ctx):
        await self._claim_event(ctx, "giang_sinh")

    @commands.command(name="dem_giao_thua")
    async def dem_giao_thua(self, ctx):
        await self._claim_event(ctx, "nam_moi")


async def setup(bot):
    await bot.add_cog(Events(bot))

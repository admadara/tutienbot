"""
cogs/linhthu.py - Hệ Thống Linh Thú v2 (Pet System)
Lệnh: ,tl pet / ,tl linhthu / ,tl thu
"""
import discord
from discord.ext import commands
import random, asyncio, time, math

from utils.helpers import require_player, now
from utils.embeds import fmt, fmt_time, warn, info, error, bar, make
from utils.game_data import ITEMS, DAO

# ══════════════════════════════════════════════════════════════
#  DỮ LIỆU LINH THÚ
# ══════════════════════════════════════════════════════════════
RARITY_COLOR = {
    "common":    0xAAAAAA, "uncommon": 0x55AA55,
    "rare":      0x5588FF, "epic":     0xAA55FF,
    "legendary": 0xFF9900, "mythic":   0xFF2244,
    "divine":    0xFFEE00,
}
RARITY_STAR = {
    "common":"⬜","uncommon":"🟩","rare":"🟦",
    "epic":"🟪","legendary":"🟧","mythic":"🟥","divine":"✨"
}
RARITY_ORDER = ["common","uncommon","rare","epic","legendary","mythic","divine"]

PET_DATA = {
    # ── Common ──────────────────────────────────────────────────
    "tho_than":    {"name":"🐇 Thỏ Thần",      "rarity":"common",    "emoji":"🐇",
                    "atk":0.02,"def":0.02,"hp":0.03,
                    "passive":"Mỗi giờ hồi 1% HP khi bế quan",
                    "skill":"Đoán Cỏ","evolve_to":"linh_tho",
                    "desc":"Thỏ nhỏ linh khí nhẹ, phổ biến trong rừng tu tiên."},
    "linh_meo":    {"name":"🐱 Linh Miêu",     "rarity":"common",    "emoji":"🐱",
                    "crit":2,"luck":5,
                    "passive":"Tăng 5% may mắn khi thám hiểm",
                    "skill":"Mắt Dạ Quang","evolve_to":"tien_meo",
                    "desc":"Mèo linh nhìn thấy vật ẩn, thường theo các đạo sĩ."},
    "son_cu":      {"name":"🐦 Sơn Cư",         "rarity":"common",    "emoji":"🐦",
                    "spd":0.03,
                    "passive":"+3% tốc độ thám hiểm",
                    "skill":"Trinh Sát","evolve_to":"linh_chim",
                    "desc":"Chim núi nhỏ, dẫn đường giỏi trong bí cảnh."},
    # ── Uncommon ────────────────────────────────────────────────
    "hoa_ho_ly":   {"name":"🦊 Hỏa Hồ Ly",    "rarity":"uncommon",  "emoji":"🦊",
                    "crit":5,"luck":15,
                    "passive":"Tăng 8% CRIT & 15 Vận Khí",
                    "skill":"Mê Hoặc","evolve_to":"cuu_vi_ho",
                    "desc":"Hồ ly lửa, mắt sáng như sao, khéo léo và quyến rũ."},
    "bang_soi":    {"name":"🐺 Băng Sói",       "rarity":"uncommon",  "emoji":"🐺",
                    "atk":0.08,"spd":0.08,
                    "passive":"+8% ATK & SPD",
                    "skill":"Cắn Chết Lạnh","evolve_to":"tuyet_lang_than",
                    "desc":"Sói băng tốc độ phi thường, săn mồi không tiếng động."},
    "diep_tinh":   {"name":"🦋 Điệp Tinh",     "rarity":"uncommon",  "emoji":"🦋",
                    "hp":0.10,"exp_rate":0.05,
                    "passive":"+10% HP & +5% EXP tu luyện",
                    "skill":"Phấn Hoa Thần","evolve_to":"mong_tiep",
                    "desc":"Bướm tiên phấn màu ngũ sắc, làm tăng ngộ tính tu luyện."},
    # ── Rare ────────────────────────────────────────────────────
    "than_quy":    {"name":"🐢 Thần Quy",      "rarity":"rare",      "emoji":"🐢",
                    "def":0.20,"hp":0.15,
                    "passive":"+20% DEF & +15% HP",
                    "skill":"Mai Thần Hộ Thể","evolve_to":"huyen_vu",
                    "desc":"Rùa thần vạn năm, mai khắc bát quái, phòng thủ vô song."},
    "loi_ung":     {"name":"🦅 Lôi Ưng",       "rarity":"rare",      "emoji":"🦅",
                    "atk":0.15,"crit":8,
                    "passive":"+15% ATK & +8 CRIT",
                    "skill":"Sét Tà Kích","evolve_to":"thien_loi_phuong",
                    "desc":"Đại bàng sấm sét, mỗi lần tấn công kèm lôi điện."},
    "huyet_mi":    {"name":"🦌 Huyết Mị",      "rarity":"rare",      "emoji":"🦌",
                    "hp":0.20,"exp_rate":0.10,
                    "passive":"+20% HP & +10% EXP",
                    "skill":"Hồi Sinh Chi","evolve_to":"than_lu",
                    "desc":"Nai thần đỏ như huyết, tiết ra linh dịch hồi phục."},
    # ── Epic ────────────────────────────────────────────────────
    "phuong_hoang":{"name":"🦅 Phượng Hoàng",  "rarity":"epic",      "emoji":"🔥",
                    "spd":0.20,"crit":12,"atk":0.10,
                    "passive":"+20% SPD, +12 CRIT, +10% ATK",
                    "skill":"Lửa Hồi Sinh","evolve_to":"bat_sac_phuong",
                    "desc":"Phượng hoàng lửa, chết đi rồi hóa thân từ tro tàn."},
    "long_ma":     {"name":"🐎 Long Mã",        "rarity":"epic",      "emoji":"🐎",
                    "atk":0.18,"def":0.12,"spd":0.15,
                    "passive":"+18% ATK, +12% DEF, +15% SPD",
                    "skill":"Vạn Lý Phi Phong","evolve_to":"than_long_ma",
                    "desc":"Ngựa rồng phi nhanh như gió, mang chủ nhân vượt ngàn dặm."},
    "linh_gui":    {"name":"🐢 Linh Quy",       "rarity":"epic",      "emoji":"🐢",
                    "def":0.25,"hp":0.25,
                    "passive":"+25% DEF & HP, giảm 10% sát thương nhận",
                    "skill":"Càn Khôn Đại Hộ","evolve_to":"huyền_vu_than",
                    "desc":"Quy thần cổ đại, mang cả một thế giới trên mai."},
    # ── Legendary ───────────────────────────────────────────────
    "than_long":   {"name":"🐉 Thần Long",      "rarity":"legendary", "emoji":"🐉",
                    "atk":0.30,"def":0.15,"hp":0.20,
                    "passive":"+30% ATK, +15% DEF, +20% HP",
                    "skill":"Rồng Thở Lửa","evolve_to":"cuu_long_than",
                    "desc":"Long thần đệ nhất, khí thế ngất trời, vạn thú thần phục."},
    "kieu_ho":     {"name":"🐯 Kiều Hổ",        "rarity":"legendary", "emoji":"🐯",
                    "atk":0.35,"crit":20,
                    "passive":"+35% ATK & +20 CRIT — Sát thương boss +15%",
                    "skill":"Hổ Phách Vạn Quân","evolve_to":"bai_ho_than",
                    "desc":"Hổ trắng thiên mệnh, tiếng gầm rung chuyển tam giới."},
    # ── Mythic ──────────────────────────────────────────────────
    "ky_lan":      {"name":"🦄 Kỳ Lân",         "rarity":"mythic",    "emoji":"🦄",
                    "atk":0.25,"def":0.25,"hp":0.25,"spd":0.25,"luck":50,
                    "passive":"Toàn chỉ số +25%, Vận +50, +20% EXP",
                    "exp_rate":0.20,
                    "skill":"Thánh Linh Phúc Trạch","evolve_to":None,
                    "desc":"Thần thú cát tường đệ nhất, xuất hiện khi thiên địa thái bình."},
    "huyền_vu":   {"name":"🐢 Huyền Vũ",       "rarity":"mythic",    "emoji":"🌑",
                    "def":0.40,"hp":0.40,
                    "passive":"+40% DEF & HP, miễn nhiễm 1 đòn chí mạng/trận",
                    "skill":"Bắc Phương Huyền Thiên","evolve_to":None,
                    "desc":"Thần vật phương Bắc, rùa rắn hợp thể, bất tử chi thân."},
    # ── Divine ──────────────────────────────────────────────────
    "thanh_long":  {"name":"🐲 Thanh Long",     "rarity":"divine",    "emoji":"💙",
                    "atk":0.50,"def":0.30,"hp":0.40,"spd":0.30,"crit":25,"luck":80,
                    "exp_rate":0.30,
                    "passive":"Toàn chỉ số cực mạnh — Thần thú Đông Phương",
                    "skill":"Thanh Long Bát Hoang","evolve_to":None,
                    "desc":"Tứ Thánh Thú Đông Phương, thần long xanh trời Đông."},
}

# ── Tỉ lệ săn theo rarity ──────────────────────────────────
HUNT_POOL = [
    ("tho_than",30),("linh_meo",28),("son_cu",25),
    ("hoa_ho_ly",20),("bang_soi",18),("diep_tinh",15),
    ("than_quy",10),("loi_ung",9),("huyet_mi",8),
    ("phuong_hoang",5),("long_ma",4),("linh_gui",3),
    ("than_long",2),("kieu_ho",1),
    ("ky_lan",0.3),("huyền_vu",0.2),
    ("thanh_long",0.05),
]

# ── EXP cần để lên cấp ─────────────────────────────────────
def pet_exp_req(level: int) -> int:
    return int(100 * (level ** 1.5))

# ── Max level theo rarity ───────────────────────────────────
MAX_LEVEL = {
    "common":30,"uncommon":50,"rare":70,
    "epic":90,"legendary":120,"mythic":150,"divine":200
}

# ── Bonus chỉ số nhân theo level ───────────────────────────
def pet_stat_mult(level: int, rarity: str) -> float:
    base = 1.0 + level * 0.02
    rarity_mult = {
        "common":1.0,"uncommon":1.1,"rare":1.25,
        "epic":1.5,"legendary":2.0,"mythic":3.0,"divine":5.0
    }
    return base * rarity_mult.get(rarity, 1.0)

# ── Items cần cho hệ thống ──────────────────────────────────
PET_ITEMS = {
    "thu_quyet":      {"name":"📜 Thú Quyết",       "price":5_000,  "desc":"Dùng để săn Linh Thú"},
    "linh_thuc":      {"name":"🍖 Linh Thức",        "price":1_000,  "desc":"Thức ăn cho thú, +50 EXP"},
    "than_thuc":      {"name":"🍗 Thần Thức",         "price":5_000,  "desc":"Thức ăn cao cấp, +300 EXP"},
    "hoa_hinh_dan":   {"name":"💊 Hóa Hình Đan",     "price":50_000, "desc":"Tiến hóa thú lên dạng cao hơn"},
    "huyet_mach_dan": {"name":"💉 Huyết Mạch Đan",   "price":80_000, "desc":"Tẩy luyện huyết mạch thú"},
    "thu_ngu_chu":    {"name":"🔮 Thú Ngũ Châu",     "price":30_000, "desc":"Thức tỉnh Thần Thú (thức tỉnh)"},
    "truoc_trung_dan":{"name":"🥚 Trứng Tước Trùng", "price":20_000, "desc":"Trứng thú con ngẫu nhiên"},
}

# ── Trang bị thú (vuot/giap/chau) ──────────────────────────
PET_EQUIP_DATA = {
    "vuot": [
        {"id":"pv1","name":"Vuốt Sắt",      "rarity":"common",    "atk":0.05},
        {"id":"pv2","name":"Vuốt Ngân",     "rarity":"uncommon",  "atk":0.10},
        {"id":"pv3","name":"Vuốt Vàng",     "rarity":"rare",      "atk":0.18},
        {"id":"pv4","name":"Vuốt Thần",     "rarity":"epic",      "atk":0.28,"crit":5},
        {"id":"pv5","name":"Vuốt Thiên Ma", "rarity":"legendary", "atk":0.45,"crit":12},
    ],
    "giap": [
        {"id":"pg1","name":"Giáp Da",       "rarity":"common",    "def":0.05,"hp":0.05},
        {"id":"pg2","name":"Giáp Ngân",     "rarity":"uncommon",  "def":0.10,"hp":0.10},
        {"id":"pg3","name":"Giáp Vàng",     "rarity":"rare",      "def":0.18,"hp":0.15},
        {"id":"pg4","name":"Giáp Rồng",     "rarity":"epic",      "def":0.28,"hp":0.25},
        {"id":"pg5","name":"Giáp Thần",     "rarity":"legendary", "def":0.45,"hp":0.40},
    ],
    "chau": [
        {"id":"pc1","name":"Ngọc Gió",      "rarity":"common",    "spd":0.05},
        {"id":"pc2","name":"Ngọc Vận",      "rarity":"uncommon",  "luck":10},
        {"id":"pc3","name":"Ngọc Linh",     "rarity":"rare",      "exp_rate":0.10},
        {"id":"pc4","name":"Ngọc Thiên",    "rarity":"epic",      "spd":0.15,"luck":20},
        {"id":"pc5","name":"Ngọc Thần",     "rarity":"legendary", "spd":0.25,"luck":40,"exp_rate":0.20},
    ],
}

# ── Vạn Thú Tháp ────────────────────────────────────────────
TOWER_FLOORS = [
    {"floor":1, "name":"Tầng 1 — Thú Rừng",   "enemy":"🐗 Lợn Rừng Tinh",   "hp":500,  "atk":50,  "reward_lt":10_000},
    {"floor":2, "name":"Tầng 2 — Thú Nước",   "enemy":"🐊 Giao Long",        "hp":1500, "atk":120, "reward_lt":30_000},
    {"floor":3, "name":"Tầng 3 — Thú Không",  "enemy":"🦅 Đại Bằng Ma",      "hp":4000, "atk":300, "reward_lt":80_000},
    {"floor":4, "name":"Tầng 4 — Yêu Vương",  "enemy":"🐯 Bạch Hổ Yêu",     "hp":10000,"atk":700, "reward_lt":200_000},
    {"floor":5, "name":"Tầng 5 — Thần Thú",   "enemy":"🐉 Cổ Long Tinh",     "hp":30000,"atk":1500,"reward_lt":500_000},
]

# ── Thám hiểm thú ───────────────────────────────────────────
EXPLORE_REWARDS = {
    4:  {"lt_min":5_000,   "lt_max":20_000,  "drop_chance":0.3},
    8:  {"lt_min":20_000,  "lt_max":80_000,  "drop_chance":0.5},
    12: {"lt_min":80_000,  "lt_max":300_000, "drop_chance":0.7},
}

# ══════════════════════════════════════════════════════════════
#  HÀM TIỆN ÍCH
# ══════════════════════════════════════════════════════════════
def _pet_power(pet: dict) -> float:
    """Tính sức mạnh tổng của 1 thú."""
    d = PET_DATA.get(pet["pet_type"], {})
    lv = pet.get("level", 1)
    mult = pet_stat_mult(lv, d.get("rarity", "common"))
    power = 0
    for k in ("atk","def","hp","spd"):
        power += d.get(k, 0) * mult * 100
    power += d.get("crit", 0) * 2
    power += d.get("luck", 0) * 0.5
    return round(power, 1)

def _fmt_pet(pet: dict, idx: int) -> str:
    d = PET_DATA.get(pet["pet_type"], {})
    star = RARITY_STAR.get(d.get("rarity","common"), "⬜")
    lv = pet.get("level", 1)
    name = pet.get("nickname") or d.get("name", pet["pet_type"])
    awakened = "⚡" if pet.get("awakened") else ""
    evolved = "✨" if pet.get("evolved") else ""
    return f"`{idx}.` {star}{awakened}{evolved} **{name}** Lv.{lv}"

def _safe(d, k, dv=0):
    v = d.get(k); return v if v is not None else dv


# ══════════════════════════════════════════════════════════════
#  COG CHÍNH
# ══════════════════════════════════════════════════════════════
class LinhThu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ── Helper DB ────────────────────────────────────────────
    async def _get_pets(self, user_id) -> list:
        rows = await self.bot.db.fetchall(
            "SELECT * FROM pets WHERE user_id=? ORDER BY slot ASC",
            (str(user_id),)
        )
        return [dict(r) for r in rows] if rows else []

    async def _get_pet(self, user_id, slot: int) -> dict | None:
        row = await self.bot.db.fetchone(
            "SELECT * FROM pets WHERE user_id=? AND slot=?",
            (str(user_id), slot)
        )
        return dict(row) if row else None

    async def _save_pet(self, user_id, slot: int, **kwargs):
        existing = await self._get_pet(user_id, slot)
        if existing:
            sets = ", ".join(f"{k}=?" for k in kwargs)
            vals = list(kwargs.values()) + [str(user_id), slot]
            await self.bot.db.execute(
                f"UPDATE pets SET {sets} WHERE user_id=? AND slot=?", vals
            )
        else:
            kwargs["user_id"] = str(user_id)
            kwargs["slot"] = slot
            cols = ", ".join(kwargs.keys())
            ph   = ", ".join("?" * len(kwargs))
            await self.bot.db.execute(
                f"INSERT INTO pets ({cols}) VALUES ({ph})", list(kwargs.values())
            )

    async def _next_slot(self, user_id) -> int:
        pets = await self._get_pets(user_id)
        used = {p["slot"] for p in pets}
        for i in range(1, 201):
            if i not in used:
                return i
        return -1

    async def _get_active(self, user_id) -> dict | None:
        row = await self.bot.db.fetchone(
            "SELECT * FROM pets WHERE user_id=? AND equipped=1",
            (str(user_id),)
        )
        return dict(row) if row else None

    async def _pay_lt(self, user_id, amount: int) -> bool:
        p = await self.bot.db.get_player(user_id)
        if not p: return False
        ha = int(_safe(p, "linh_thach_ha"))
        if ha < amount: return False
        await self.bot.db.set_player(user_id, linh_thach_ha=ha - amount)
        return True

    async def _add_lt(self, user_id, amount: int):
        p = await self.bot.db.get_player(user_id)
        if not p: return
        ha = int(_safe(p, "linh_thach_ha"))
        await self.bot.db.set_player(user_id, linh_thach_ha=ha + amount)

    async def _has_item(self, user_id, item_key: str) -> int:
        """Kiểm tra số lượng item trong túi."""
        row = await self.bot.db.fetchone(
            "SELECT qty FROM inventory WHERE user_id=? AND item_id=?",
            (str(user_id), item_key)
        )
        return row["qty"] if row else 0

    async def _use_item(self, user_id, item_key: str, qty=1) -> bool:
        current = await self._has_item(user_id, item_key)
        if current < qty: return False
        if current - qty <= 0:
            await self.bot.db.execute(
                "DELETE FROM inventory WHERE user_id=? AND item_id=?",
                (str(user_id), item_key)
            )
        else:
            await self.bot.db.execute(
                "UPDATE inventory SET qty=? WHERE user_id=? AND item_id=?",
                (current - qty, str(user_id), item_key)
            )
        return True

    async def _add_item(self, user_id, item_key: str, qty=1):
        current = await self._has_item(user_id, item_key)
        if current > 0:
            await self.bot.db.execute(
                "UPDATE inventory SET qty=? WHERE user_id=? AND item_id=?",
                (current + qty, str(user_id), item_key)
            )
        else:
            await self.bot.db.execute(
                "INSERT INTO inventory (user_id, item_id, qty) VALUES (?,?,?)",
                (str(user_id), item_key, qty)
            )

    # ══════════════════════════════════════════════════════════
    #  LỆNH GROUP
    # ══════════════════════════════════════════════════════════
    @commands.group(name="linhthu", aliases=["pet","thu"], invoke_without_command=True)
    async def linhthu(self, ctx):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        # Hiện menu tổng quan
        pets = await self._get_pets(ctx.author.id)
        active = await self._get_active(ctx.author.id)

        e = discord.Embed(
            title="🦁 HỆ THỐNG LINH THÚ",
            description=(
                "📜 **CÁC LỆNH CƠ BẢN:**\n"
                "🔸 `,tl pet hunt` — Săn bắt Linh Thú (Cần Thú Quyết)\n"
                "🔸 `,tl pet list` — Xem danh sách thú đã bắt\n"
                "🔸 `,tl pet info [STT]` — Xem chi tiết thú & Passive\n"
                "🔸 `,tl pet equip [STT]` — Trang bị thú để nhận chỉ số\n"
                "🔸 `,tl pet unequip` — Tháo thú đang trang bị\n"
                "🔸 `,tl pet feed [STT]` — Cho thú ăn (Tăng EXP)\n"
                "🔸 `,tl pet evolve [STT]` — Tiến hóa thú\n"
                "🔸 `,tl pet thuctinh [STT]` — Thức tỉnh Thần Thú\n"
                "🔸 `,tl pet lai [STT1] [STT2]` — Lai tạo thú (50M LT)\n"
                "🔸 `,tl pet ap [STT Trứng]` — Ấp trứng nở thú con\n"
                "🔸 `,tl pet thap` — Vạn Thú Tháp\n"
                "🔸 `,tl pet thamhiem [STT/all] [4/8/12]` — Thám hiểm\n"
                "🔸 `,tl pet thamhiem claim` — Nhận thưởng\n"
                "🔸 `,tl pet nuot [Chính] [Phụ]` — Hấp thụ EXP\n"
                "🔸 `,tl pet macdo [STT] [ID]` — Mặc trang bị\n"
                "🔸 `,tl pet thaodo [STT] [vuot/giap/chau]` — Tháo trang bị\n"
                "🔸 `,tl pet huyetmach [STT]` — Tẩy luyện Huyết Mạch (200M LT)\n"
                "🔸 `,tl pet arena [@tag]` — Thách đấu Arena (Cược 10M LT)\n"
                "🔸 `,tl pet rename [STT] [Tên]` — Đặt tên cho thú\n"
                "🔸 `,tl pet release [STT]` — Phóng sinh thú\n"
            ),
            color=0xFF9800
        )
        e.add_field(
            name="📊 Tổng Quan",
            value=(
                f"🐾 Số thú: **{len(pets)}/200**\n"
                f"⚔️ Đang trang bị: **{PET_DATA.get(active['pet_type'],{}).get('name','?') if active else 'Không có'}**"
            )
        )
        e.set_footer(text="⚠️ Giới hạn: 200 thú/người | 100 thú thám hiểm")
        await ctx.send(embed=e)

    # ──────────────────────────────────────────────────────────
    #  HUNT — Săn thú
    # ──────────────────────────────────────────────────────────
    @linhthu.command(name="hunt", aliases=["san","bat"])
    async def hunt(self, ctx):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn!")); return

        pets = await self._get_pets(ctx.author.id)
        if len(pets) >= 200:
            await ctx.send(embed=warn("❌ Đã đủ 200 thú! Phóng sinh bớt đi.")); return

        if not await self._use_item(ctx.author.id, "thu_quyet"):
            await ctx.send(embed=warn(
                "❌ Cần **Thú Quyết** để săn!\n"
                "Mua tại `,tl shop linhthu` — 5,000 LT/cái"
            )); return

        # Tính luck bonus
        luck = int(_safe(player, "luck", 0))
        luck_bonus = luck / 1000  # +0.1% per luck

        # Roll
        pool = [(k, w * (1 + luck_bonus)) for k, w in HUNT_POOL]
        total = sum(w for _, w in pool)
        r = random.uniform(0, total)
        chosen = pool[0][0]
        for k, w in pool:
            r -= w
            if r <= 0:
                chosen = k
                break

        d = PET_DATA[chosen]
        slot = await self._next_slot(ctx.author.id)
        await self._save_pet(
            ctx.author.id, slot,
            pet_type=chosen, level=1, exp=0,
            equipped=0, awakened=0, evolved=0,
            nickname="", equip_vuot="", equip_giap="", equip_chau="",
            explore_end=0
        )

        rarity = d["rarity"]
        color  = RARITY_COLOR.get(rarity, 0xAAAAAA)
        star   = RARITY_STAR.get(rarity, "⬜")

        e = discord.Embed(
            title=f"🎉 Săn Được Linh Thú!",
            description=(
                f"{star} **{d['name']}** — `{rarity.upper()}`\n"
                f"_{d['desc']}_\n\n"
                f"📍 Vị trí: **#{slot}**\n"
                f"⚡ Kỹ năng: **{d['skill']}**\n"
                f"💡 Passive: _{d['passive']}_"
            ),
            color=color
        )
        e.set_footer(text=f"Dùng `,tl pet equip {slot}` để trang bị | `,tl pet info {slot}` xem chi tiết")
        await ctx.send(embed=e)

    # ──────────────────────────────────────────────────────────
    #  LIST — Danh sách thú
    # ──────────────────────────────────────────────────────────
    @linhthu.command(name="list", aliases=["ds","danhsach"])
    async def list_pets(self, ctx):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn!")); return
        pets = await self._get_pets(ctx.author.id)
        if not pets:
            await ctx.send(embed=warn("Chưa có Linh Thú! Dùng `,tl pet hunt` để săn.")); return

        # Group by rarity
        by_rarity = {}
        for p in pets:
            d = PET_DATA.get(p["pet_type"], {})
            r = d.get("rarity", "common")
            by_rarity.setdefault(r, []).append(p)

        e = discord.Embed(title=f"🐾 Linh Thú Của {player['name']} ({len(pets)}/200)", color=0xFF9800)

        for rarity in reversed(RARITY_ORDER):
            group = by_rarity.get(rarity, [])
            if not group: continue
            lines = [_fmt_pet(p, p["slot"]) for p in group[:10]]
            if len(group) > 10:
                lines.append(f"_...và {len(group)-10} thú khác_")
            e.add_field(
                name=f"{RARITY_STAR.get(rarity,'⬜')} {rarity.upper()} ({len(group)})",
                value="\n".join(lines),
                inline=False
            )

        active = await self._get_active(ctx.author.id)
        if active:
            d = PET_DATA.get(active["pet_type"], {})
            e.set_footer(text=f"⚔️ Đang trang bị: {d.get('name','?')} #{active['slot']}")
        await ctx.send(embed=e)

    # ──────────────────────────────────────────────────────────
    #  INFO — Chi tiết thú
    # ──────────────────────────────────────────────────────────
    @linhthu.command(name="info", aliases=["chitiet","xem"])
    async def info_pet(self, ctx, slot: int = 1):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player: await ctx.send(embed=warn("Chưa nhập môn!")); return

        pet = await self._get_pet(ctx.author.id, slot)
        if not pet:
            await ctx.send(embed=warn(f"❌ Không có thú ở vị trí #{slot}!")); return

        d = PET_DATA.get(pet["pet_type"], {})
        rarity = d.get("rarity", "common")
        lv = pet.get("level", 1)
        exp_cur = pet.get("exp", 0)
        exp_req = pet_exp_req(lv)
        mult = pet_stat_mult(lv, rarity)
        max_lv = MAX_LEVEL.get(rarity, 30)

        name = pet.get("nickname") or d.get("name", "???")
        color = RARITY_COLOR.get(rarity, 0xAAAAAA)
        star = RARITY_STAR.get(rarity, "⬜")
        awakened = pet.get("awakened", 0)
        evolved = pet.get("evolved", 0)

        badges = ""
        if awakened: badges += " ⚡**[THỨC TỈNH]**"
        if evolved:  badges += " ✨**[TIẾN HÓA]**"

        # Tính chỉ số thực
        stats = []
        for k, label in [("atk","⚔️ ATK"),("def","🛡️ DEF"),("hp","❤️ HP"),("spd","⚡ SPD")]:
            base = d.get(k, 0)
            if base:
                stats.append(f"{label}: +{base*mult*100:.1f}%")
        if d.get("crit"): stats.append(f"💥 CRIT: +{d['crit']} (x{mult:.1f})")
        if d.get("luck"): stats.append(f"🍀 VẬN: +{int(d['luck']*mult)}")
        if d.get("exp_rate"): stats.append(f"📈 EXP: +{d['exp_rate']*100:.0f}%")

        # Trang bị thú
        equip_lines = []
        for slot_name, label in [("equip_vuot","🦷 Vuốt"),("equip_giap","🛡️ Giáp"),("equip_chau","💎 Châu")]:
            eq = pet.get(slot_name, "")
            equip_lines.append(f"{label}: **{eq if eq else '(trống)'}**")

        e = discord.Embed(
            title=f"{star} {name}{badges}",
            description=f"_{d.get('desc','')}_",
            color=color
        )
        e.add_field(name="📋 Thông Tin", value=(
            f"🔢 Vị trí: **#{slot}**\n"
            f"📛 Loại: **{d.get('name','?')}**\n"
            f"✨ Rarity: **{rarity.upper()}**\n"
            f"⭐ Cấp: **{lv}/{max_lv}**\n"
            f"📊 EXP: `{int(exp_cur)}/{exp_req}`\n"
            f"{bar(exp_cur, exp_req, 12)}"
        ), inline=True)
        e.add_field(name="📈 Chỉ Số (Lv.{})".format(lv), value="\n".join(stats) if stats else "_Không có bonus_", inline=True)
        e.add_field(name="⚡ Kỹ Năng & Passive", value=(
            f"🌀 **{d.get('skill','?')}**\n"
            f"_{d.get('passive','?')}_"
        ), inline=False)
        e.add_field(name="🎽 Trang Bị Thú", value="\n".join(equip_lines), inline=True)
        e.add_field(name="💪 Sức Mạnh", value=f"**{_pet_power(pet):,.0f}**", inline=True)
        if d.get("evolve_to"):
            next_d = PET_DATA.get(d["evolve_to"], {})
            e.add_field(name="🔄 Tiến Hóa", value=f"→ **{next_d.get('name','?')}**", inline=True)
        e.set_footer(text=f"{'⚔️ Đang trang bị' if pet.get('equipped') else '💤 Không trang bị'}")
        await ctx.send(embed=e)

    # ──────────────────────────────────────────────────────────
    #  EQUIP / UNEQUIP
    # ──────────────────────────────────────────────────────────
    @linhthu.command(name="equip", aliases=["tb","trangbi"])
    async def equip(self, ctx, slot: int):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player: await ctx.send(embed=warn("Chưa nhập môn!")); return

        pet = await self._get_pet(ctx.author.id, slot)
        if not pet:
            await ctx.send(embed=warn(f"❌ Không có thú ở #{slot}!")); return

        # Tháo thú cũ
        await self.bot.db.execute(
            "UPDATE pets SET equipped=0 WHERE user_id=?", (str(ctx.author.id),)
        )
        await self._save_pet(ctx.author.id, slot, equipped=1)

        d = PET_DATA.get(pet["pet_type"], {})
        lv = pet.get("level", 1)
        mult = pet_stat_mult(lv, d.get("rarity","common"))

        bonus_lines = []
        for k, label in [("atk","ATK"),("def","DEF"),("hp","HP"),("spd","SPD")]:
            if d.get(k): bonus_lines.append(f"+{d[k]*mult*100:.1f}% {label}")
        if d.get("crit"): bonus_lines.append(f"+{d['crit']} CRIT")
        if d.get("luck"): bonus_lines.append(f"+{int(d['luck']*mult)} VẬN")

        e = discord.Embed(
            title=f"✅ Đã trang bị {d.get('name','?')}",
            description=(
                f"⭐ Lv.**{lv}** | {RARITY_STAR.get(d.get('rarity'),'⬜')} {d.get('rarity','').upper()}\n\n"
                f"**Bonus nhận được:**\n" + "\n".join(bonus_lines)
            ),
            color=RARITY_COLOR.get(d.get("rarity","common"), 0xFF9800)
        )
        await ctx.send(embed=e)

    @linhthu.command(name="unequip", aliases=["thao","thaothu"])
    async def unequip(self, ctx):
        await self.bot.db.execute(
            "UPDATE pets SET equipped=0 WHERE user_id=?", (str(ctx.author.id),)
        )
        await ctx.send(embed=make("✅ Đã tháo Linh Thú", "", 0x88BB88))

    # ──────────────────────────────────────────────────────────
    #  FEED — Cho ăn
    # ──────────────────────────────────────────────────────────
    @linhthu.command(name="feed", aliases=["choan","an"])
    async def feed(self, ctx, slot: int, item_key: str = "linh_thuc"):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player: await ctx.send(embed=warn("Chưa nhập môn!")); return

        pet = await self._get_pet(ctx.author.id, slot)
        if not pet:
            await ctx.send(embed=warn(f"❌ Không có thú ở #{slot}!")); return

        item_info = PET_ITEMS.get(item_key)
        if not item_info or item_key not in ("linh_thuc","than_thuc"):
            await ctx.send(embed=warn("❌ Item không hợp lệ! Dùng `linh_thuc` hoặc `than_thuc`")); return

        if not await self._use_item(ctx.author.id, item_key):
            await ctx.send(embed=warn(f"❌ Không có **{item_info['name']}** trong túi!")); return

        d = PET_DATA.get(pet["pet_type"], {})
        rarity = d.get("rarity","common")
        lv = pet.get("level", 1)
        exp_gain = 50 if item_key == "linh_thuc" else 300
        max_lv = MAX_LEVEL.get(rarity, 30)

        new_exp = pet.get("exp", 0) + exp_gain
        leveled = []
        while lv < max_lv and new_exp >= pet_exp_req(lv):
            new_exp -= pet_exp_req(lv)
            lv += 1
            leveled.append(lv)

        await self._save_pet(ctx.author.id, slot, level=lv, exp=new_exp)

        desc = f"🍖 +**{exp_gain} EXP**"
        if leveled:
            desc += f"\n🎉 **LÊN CẤP!** Lv.{leveled[-1]}"
        if lv >= max_lv:
            desc += f"\n⚠️ Đã max cấp ({max_lv})! Dùng `,tl pet evolve {slot}` để tiến hóa."

        e = discord.Embed(title=f"🍖 Cho {d.get('name','?')} Ăn", description=desc, color=0xFF9800)
        e.add_field(name="📊 EXP", value=f"`{int(new_exp)}/{pet_exp_req(lv)}`")
        e.add_field(name="⭐ Cấp", value=f"**{lv}/{max_lv}**")
        await ctx.send(embed=e)

    # ──────────────────────────────────────────────────────────
    #  EVOLVE — Tiến hóa
    # ──────────────────────────────────────────────────────────
    @linhthu.command(name="evolve", aliases=["tienhoa","tienho"])
    async def evolve(self, ctx, slot: int):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player: await ctx.send(embed=warn("Chưa nhập môn!")); return

        pet = await self._get_pet(ctx.author.id, slot)
        if not pet: await ctx.send(embed=warn(f"❌ Không có thú ở #{slot}!")); return

        d = PET_DATA.get(pet["pet_type"], {})
        rarity = d.get("rarity","common")
        max_lv = MAX_LEVEL.get(rarity, 30)
        lv = pet.get("level", 1)

        if lv < max_lv:
            await ctx.send(embed=warn(f"❌ Thú chưa max cấp! ({lv}/{max_lv})")); return

        evolve_to = d.get("evolve_to")
        if not evolve_to:
            await ctx.send(embed=warn("❌ Thú này đã đạt dạng tối thượng, không thể tiến hóa!")); return

        if not await self._use_item(ctx.author.id, "hoa_hinh_dan"):
            await ctx.send(embed=warn("❌ Cần **Hóa Hình Đan** để tiến hóa!\nMua tại `,tl shop linhthu`")); return

        new_d = PET_DATA[evolve_to]
        await self._save_pet(ctx.author.id, slot, pet_type=evolve_to, level=1, exp=0, evolved=1)

        e = discord.Embed(
            title="✨ TIẾN HÓA THÀNH CÔNG!",
            description=(
                f"**{d['name']}** → **{new_d['name']}**\n\n"
                f"{RARITY_STAR.get(new_d['rarity'],'⬜')} **{new_d['rarity'].upper()}**\n"
                f"_{new_d['desc']}_\n\n"
                f"⚡ Kỹ năng mới: **{new_d['skill']}**\n"
                f"💡 Passive mới: _{new_d['passive']}_"
            ),
            color=RARITY_COLOR.get(new_d["rarity"], 0xFFEE00)
        )
        await ctx.send(embed=e)

    # ──────────────────────────────────────────────────────────
    #  THỨC TỈNH
    # ──────────────────────────────────────────────────────────
    @linhthu.command(name="thuctinh", aliases=["awaken","thuctinhgiac"])
    async def thuctinh(self, ctx, slot: int):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player: await ctx.send(embed=warn("Chưa nhập môn!")); return

        pet = await self._get_pet(ctx.author.id, slot)
        if not pet: await ctx.send(embed=warn(f"❌ Không có thú ở #{slot}!")); return
        if pet.get("awakened"):
            await ctx.send(embed=warn("❌ Thú đã được thức tỉnh rồi!")); return

        if not await self._use_item(ctx.author.id, "thu_ngu_chu"):
            await ctx.send(embed=warn("❌ Cần **Thú Ngũ Châu** để thức tỉnh!\nMua tại `,tl shop linhthu`")); return

        d = PET_DATA.get(pet["pet_type"], {})
        await self._save_pet(ctx.author.id, slot, awakened=1)

        e = discord.Embed(
            title="⚡ THỨC TỈNH THÀNH CÔNG!",
            description=(
                f"**{d.get('name','?')}** đã thức tỉnh!\n\n"
                f"⚡ Toàn bộ chỉ số tăng thêm **+25%**\n"
                f"🌟 Kỹ năng **{d.get('skill','?')}** được tăng cường!"
            ),
            color=0xFFCC00
        )
        await ctx.send(embed=e)

    # ──────────────────────────────────────────────────────────
    #  LAI TẠO
    # ──────────────────────────────────────────────────────────
    @linhthu.command(name="lai", aliases=["breed","laitao"])
    async def lai(self, ctx, slot1: int, slot2: int):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player: await ctx.send(embed=warn("Chưa nhập môn!")); return
        if slot1 == slot2:
            await ctx.send(embed=warn("❌ Không thể lai 2 thú giống nhau!")); return

        p1 = await self._get_pet(ctx.author.id, slot1)
        p2 = await self._get_pet(ctx.author.id, slot2)
        if not p1 or not p2:
            await ctx.send(embed=warn("❌ Không tìm thấy thú!")); return

        d1 = PET_DATA.get(p1["pet_type"], {})
        d2 = PET_DATA.get(p2["pet_type"], {})
        r1 = RARITY_ORDER.index(d1.get("rarity","common"))
        r2 = RARITY_ORDER.index(d2.get("rarity","common"))

        if p1.get("level",1) < 20 or p2.get("level",1) < 20:
            await ctx.send(embed=warn("❌ Cả 2 thú phải đạt tối thiểu **Lv.20** để lai tạo!")); return

        COST = 50_000_000
        if not await self._pay_lt(ctx.author.id, COST):
            await ctx.send(embed=warn(f"❌ Cần **50,000,000 LT Hạ Phẩm** để lai tạo!")); return

        # Kết quả: có thể ra rarity cao hơn hoặc bằng cha mẹ
        max_rarity = max(r1, r2)
        roll = random.random()
        if roll < 0.05:  # 5% ra cao hơn 1 bậc
            result_rarity = min(max_rarity + 1, len(RARITY_ORDER)-1)
        else:
            result_rarity = max_rarity

        # Chọn thú ngẫu nhiên trong pool rarity đó
        target_r = RARITY_ORDER[result_rarity]
        pool = [k for k, v in PET_DATA.items() if v.get("rarity") == target_r]
        chosen = random.choice(pool) if pool else p1["pet_type"]

        # Phóng sinh thú phụ (slot2)
        await self.bot.db.execute(
            "DELETE FROM pets WHERE user_id=? AND slot=?", (str(ctx.author.id), slot2)
        )
        # Chuyển slot1 thành con mới
        await self._save_pet(ctx.author.id, slot1,
            pet_type=chosen, level=1, exp=0,
            equipped=0, awakened=0, evolved=0,
            nickname="", equip_vuot="", equip_giap="", equip_chau=""
        )

        new_d = PET_DATA[chosen]
        e = discord.Embed(
            title="🥚 LAI TẠO THÀNH CÔNG!",
            description=(
                f"**{d1['name']}** × **{d2['name']}**\n"
                f"→ {RARITY_STAR.get(target_r,'⬜')} **{new_d['name']}** (`{target_r.upper()}`)\n\n"
                f"_{new_d['desc']}_"
            ),
            color=RARITY_COLOR.get(target_r, 0xFF9800)
        )
        await ctx.send(embed=e)

    # ──────────────────────────────────────────────────────────
    #  ẤP TRỨNG
    # ──────────────────────────────────────────────────────────
    @linhthu.command(name="ap", aliases=["hatch","no"])
    async def ap(self, ctx, egg_slot: int):
        """Ấp trứng từ túi đồ (item type linhthu_egg)."""
        player = await self.bot.db.get_player(ctx.author.id)
        if not player: await ctx.send(embed=warn("Chưa nhập môn!")); return

        pets = await self._get_pets(ctx.author.id)
        if len(pets) >= 200:
            await ctx.send(embed=warn("❌ Đã đủ 200 thú!")); return

        # Tìm trứng trong túi theo vị trí (slot trong inventory)
        eggs = []
        for iid, idata in ITEMS.items():
            if idata.get("type") == "linhthu_egg":
                qty = await self._has_item(ctx.author.id, iid)
                if qty > 0:
                    eggs.append((iid, idata, qty))

        # Thêm trứng từ PET_ITEMS
        for iid in ["truoc_trung_dan"]:
            qty = await self._has_item(ctx.author.id, iid)
            if qty > 0:
                eggs.append((iid, PET_ITEMS[iid], qty))

        if not eggs:
            await ctx.send(embed=warn("❌ Không có trứng trong túi!\nMua tại `,tl shop linhthu`")); return

        if egg_slot < 1 or egg_slot > len(eggs):
            egg_list = "\n".join(f"`{i+1}.` {d['name']} x{q}" for i,(k,d,q) in enumerate(eggs))
            await ctx.send(embed=warn(f"❌ Chọn trứng:\n{egg_list}")); return

        egg_id, egg_data, _ = eggs[egg_slot-1]
        await self._use_item(ctx.author.id, egg_id)

        # Xác định loại thú
        pet_type = egg_data.get("thu_type")
        if not pet_type or egg_id == "truoc_trung_dan":
            # Trứng ngẫu nhiên
            pool = [(k, w) for k, w in HUNT_POOL]
            total = sum(w for _, w in pool)
            r = random.uniform(0, total)
            pet_type = pool[0][0]
            for k, w in pool:
                r -= w
                if r <= 0:
                    pet_type = k
                    break

        d = PET_DATA.get(pet_type, {})
        slot = await self._next_slot(ctx.author.id)
        await self._save_pet(ctx.author.id, slot,
            pet_type=pet_type, level=1, exp=0,
            equipped=0, awakened=0, evolved=0,
            nickname="", equip_vuot="", equip_giap="", equip_chau="",
            explore_end=0
        )

        e = discord.Embed(
            title="🥚 Trứng Nở!",
            description=(
                f"{RARITY_STAR.get(d.get('rarity','common'),'⬜')} **{d.get('name','?')}** xuất hiện!\n"
                f"_{d.get('desc','')}_\n\n"
                f"📍 Vị trí: **#{slot}**"
            ),
            color=RARITY_COLOR.get(d.get("rarity","common"), 0xFF9800)
        )
        await ctx.send(embed=e)

    # ──────────────────────────────────────────────────────────
    #  VẠN THÚ THÁP
    # ──────────────────────────────────────────────────────────
    @linhthu.command(name="thap", aliases=["tower","tanthu"])
    async def thap(self, ctx, floor: int = 1):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player: await ctx.send(embed=warn("Chưa nhập môn!")); return

        active = await self._get_active(ctx.author.id)
        if not active:
            await ctx.send(embed=warn("❌ Cần trang bị Linh Thú trước! Dùng `,tl pet equip [STT]`")); return

        if floor < 1 or floor > len(TOWER_FLOORS):
            await ctx.send(embed=warn(f"❌ Tháp có {len(TOWER_FLOORS)} tầng (1-{len(TOWER_FLOORS)})!")); return

        tf = TOWER_FLOORS[floor-1]
        d = PET_DATA.get(active["pet_type"], {})
        power = _pet_power(active)
        awakened_mult = 1.25 if active.get("awakened") else 1.0
        pet_atk = (100 + d.get("atk",0)*100) * pet_stat_mult(active.get("level",1), d.get("rarity","common")) * awakened_mult

        # Chiến đấu đơn giản
        enemy_hp = tf["hp"]
        pet_hp = 1000 + int(d.get("hp",0)*5000)
        rounds = 0
        while enemy_hp > 0 and pet_hp > 0 and rounds < 50:
            enemy_hp -= max(1, int(pet_atk * random.uniform(0.8, 1.2)))
            if enemy_hp <= 0: break
            pet_hp -= max(1, int(tf["atk"] * random.uniform(0.8, 1.2) * (1 - d.get("def",0)*0.5)))
            rounds += 1

        win = pet_hp > 0
        if win:
            reward = tf["reward_lt"]
            await self._add_lt(ctx.author.id, reward)
            # EXP cho thú
            exp_gain = floor * 50
            new_exp = active.get("exp",0) + exp_gain
            lv = active.get("level",1)
            max_lv = MAX_LEVEL.get(d.get("rarity","common"), 30)
            while lv < max_lv and new_exp >= pet_exp_req(lv):
                new_exp -= pet_exp_req(lv)
                lv += 1
            await self._save_pet(ctx.author.id, active["slot"], level=lv, exp=new_exp)

            e = discord.Embed(
                title=f"⚔️ Tầng {floor} — CHIẾN THẮNG!",
                description=(
                    f"{tf['enemy']} đã bị đánh bại!\n\n"
                    f"💰 Nhận: **{fmt(reward)} LT**\n"
                    f"📈 Thú +{exp_gain} EXP"
                ),
                color=0x55FF55
            )
            if floor < len(TOWER_FLOORS):
                e.set_footer(text=f"Thử tầng {floor+1}: ,tl pet thap {floor+1}")
        else:
            e = discord.Embed(
                title=f"⚔️ Tầng {floor} — THẤT BẠI",
                description=f"{tf['enemy']} quá mạnh!\n\nNâng cấp thú trước khi thử lại.",
                color=0xFF4444
            )
        await ctx.send(embed=e)

    # ──────────────────────────────────────────────────────────
    #  THÁM HIỂM
    # ──────────────────────────────────────────────────────────
    @linhthu.command(name="thamhiem", aliases=["explore","th"])
    async def thamhiem(self, ctx, target: str = "1", hours: str = "4"):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player: await ctx.send(embed=warn("Chưa nhập môn!")); return

        # Claim
        if target.lower() == "claim":
            return await self._thamhiem_claim(ctx, player)

        h = int(hours) if hours.isdigit() and int(hours) in EXPLORE_REWARDS else 4
        end_ts = now() + h * 3600

        if target.lower() == "all":
            pets = await self._get_pets(ctx.author.id)
            idle_pets = [p for p in pets if not p.get("explore_end") or p["explore_end"] < now()][:100]
            for p in idle_pets:
                await self._save_pet(ctx.author.id, p["slot"], explore_end=end_ts)
            await ctx.send(embed=make(
                f"🗺️ Thám Hiểm {h}h",
                f"Đã gửi **{len(idle_pets)} thú** đi thám hiểm {h} giờ!\n"
                f"Dùng `,tl pet thamhiem claim` sau {h}h để nhận thưởng.",
                0xFF9800
            ))
        elif target.isdigit():
            slot = int(target)
            pet = await self._get_pet(ctx.author.id, slot)
            if not pet: await ctx.send(embed=warn(f"❌ Không có thú #{slot}!")); return
            if pet.get("explore_end",0) > now():
                rem = pet["explore_end"] - now()
                await ctx.send(embed=warn(f"❌ Thú đang thám hiểm! Còn {fmt_time(int(rem))}")); return

            await self._save_pet(ctx.author.id, slot, explore_end=end_ts)
            d = PET_DATA.get(pet["pet_type"], {})
            await ctx.send(embed=make(
                f"🗺️ {d.get('name','?')} Đi Thám Hiểm",
                f"Thú #{slot} đi thám hiểm **{h} giờ**\nDùng `,tl pet thamhiem claim` sau {h}h để nhận.",
                0xFF9800
            ))
        else:
            await ctx.send(embed=warn("Cú pháp: `,tl pet thamhiem [STT/all] [4/8/12]`"))

    async def _thamhiem_claim(self, ctx, player):
        pets = await self._get_pets(ctx.author.id)
        done = [p for p in pets if p.get("explore_end",0) > 0 and p["explore_end"] <= now()]
        if not done:
            await ctx.send(embed=warn("❌ Không có thú nào hoàn thành thám hiểm!")); return

        total_lt = 0
        total_items = []
        for p in done:
            # Tính thời gian thám hiểm
            elapsed_h = min(12, max(4, (p["explore_end"] - (p["explore_end"] % 3600)) // 3600))
            # Tìm reward tier gần nhất
            tier = min(EXPLORE_REWARDS.keys(), key=lambda x: abs(x - elapsed_h))
            rw = EXPLORE_REWARDS[tier]
            lt = random.randint(rw["lt_min"], rw["lt_max"])
            total_lt += lt
            if random.random() < rw["drop_chance"]:
                # Drop trang bị thú ngẫu nhiên
                slot_name = random.choice(["vuot","giap","chau"])
                eq_list = PET_EQUIP_DATA[slot_name]
                weights = [5,4,3,2,1][:len(eq_list)]
                eq = random.choices(eq_list, weights=weights)[0]
                total_items.append(f"🎁 {eq['name']} ({slot_name})")
                await self._add_item(ctx.author.id, f"pet_eq_{eq['id']}", 1)
            await self._save_pet(ctx.author.id, p["slot"], explore_end=0)

        await self._add_lt(ctx.author.id, total_lt)
        desc = f"**{len(done)} thú** đã về!\n\n💰 Tổng LT: **{fmt(total_lt)}**"
        if total_items:
            desc += f"\n\n🎁 Vật phẩm nhặt được:\n" + "\n".join(total_items[:10])

        await ctx.send(embed=make("🏆 Thám Hiểm Hoàn Thành!", desc, 0xFF9800))

    # ──────────────────────────────────────────────────────────
    #  NUỐT — Hấp thụ EXP
    # ──────────────────────────────────────────────────────────
    @linhthu.command(name="nuot", aliases=["absorb","hutexp"])
    async def nuot(self, ctx, main_slot: int, sub: str = ""):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player: await ctx.send(embed=warn("Chưa nhập môn!")); return

        main_pet = await self._get_pet(ctx.author.id, main_slot)
        if not main_pet: await ctx.send(embed=warn(f"❌ Không có thú #{main_slot}!")); return

        if not sub:
            await ctx.send(embed=warn("Cú pháp: `,tl pet nuot [Chính] [Phụ/all]`")); return

        if sub.lower() == "all":
            pets = await self._get_pets(ctx.author.id)
            sub_pets = [p for p in pets if p["slot"] != main_slot and not p.get("equipped")]
        elif sub.isdigit():
            sp = await self._get_pet(ctx.author.id, int(sub))
            sub_pets = [sp] if sp and sp["slot"] != main_slot else []
        else:
            await ctx.send(embed=warn("❌ Nhập STT thú phụ hoặc 'all'")); return

        if not sub_pets:
            await ctx.send(embed=warn("❌ Không có thú phụ hợp lệ!")); return

        total_exp = 0
        for sp in sub_pets:
            sd = PET_DATA.get(sp["pet_type"], {})
            # EXP nhận = level * 50 * rarity multiplier
            rarity_mult = {
                "common":1,"uncommon":1.5,"rare":2,
                "epic":3,"legendary":5,"mythic":8,"divine":15
            }.get(sd.get("rarity","common"), 1)
            total_exp += sp.get("level",1) * 50 * rarity_mult
            await self.bot.db.execute(
                "DELETE FROM pets WHERE user_id=? AND slot=?",
                (str(ctx.author.id), sp["slot"])
            )

        d = PET_DATA.get(main_pet["pet_type"], {})
        lv = main_pet.get("level", 1)
        new_exp = main_pet.get("exp", 0) + total_exp
        max_lv = MAX_LEVEL.get(d.get("rarity","common"), 30)
        leveled = []
        while lv < max_lv and new_exp >= pet_exp_req(lv):
            new_exp -= pet_exp_req(lv)
            lv += 1
            leveled.append(lv)

        await self._save_pet(ctx.author.id, main_slot, level=lv, exp=new_exp)

        desc = f"Hấp thụ **{len(sub_pets)} thú** → +**{fmt(int(total_exp))} EXP**"
        if leveled:
            desc += f"\n🎉 **LÊN CẤP → Lv.{leveled[-1]}**"

        await ctx.send(embed=make(f"🌀 Hấp Thụ — {d.get('name','?')}", desc, 0x9955FF))

    # ──────────────────────────────────────────────────────────
    #  MẶC TRANG BỊ / THÁO TRANG BỊ
    # ──────────────────────────────────────────────────────────
    @linhthu.command(name="macdo", aliases=["do","mac"])
    async def macdo(self, ctx, slot: int, eq_id: str):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player: await ctx.send(embed=warn("Chưa nhập môn!")); return

        pet = await self._get_pet(ctx.author.id, slot)
        if not pet: await ctx.send(embed=warn(f"❌ Không có thú #{slot}!")); return

        if not await self._use_item(ctx.author.id, f"pet_eq_{eq_id}"):
            await ctx.send(embed=warn(f"❌ Không có trang bị ID `{eq_id}` trong túi!")); return

        # Tìm trang bị
        eq_found = None
        eq_slot_name = None
        for sname, eqs in PET_EQUIP_DATA.items():
            for eq in eqs:
                if eq["id"] == eq_id:
                    eq_found = eq
                    eq_slot_name = sname
                    break

        if not eq_found:
            await self._add_item(ctx.author.id, f"pet_eq_{eq_id}", 1)
            await ctx.send(embed=warn(f"❌ Trang bị `{eq_id}` không tồn tại!")); return

        # Tháo cũ trả lại túi
        old_eq = pet.get(f"equip_{eq_slot_name}","")
        if old_eq:
            await self._add_item(ctx.author.id, f"pet_eq_{old_eq}", 1)

        await self._save_pet(ctx.author.id, slot, **{f"equip_{eq_slot_name}": eq_id})
        d = PET_DATA.get(pet["pet_type"], {})
        await ctx.send(embed=make(
            f"🎽 Mặc Trang Bị",
            f"**{d.get('name','?')}** #{slot} đã mặc **{eq_found['name']}**\n"
            f"Slot: {eq_slot_name} | Rarity: {RARITY_STAR.get(eq_found['rarity'],'⬜')} {eq_found['rarity'].upper()}",
            RARITY_COLOR.get(eq_found["rarity"], 0xFF9800)
        ))

    @linhthu.command(name="thaodo", aliases=["thaotrangbi"])
    async def thaodo(self, ctx, slot: int, eq_slot: str):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player: await ctx.send(embed=warn("Chưa nhập môn!")); return

        if eq_slot not in ("vuot","giap","chau"):
            await ctx.send(embed=warn("❌ Slot phải là: `vuot`, `giap`, hoặc `chau`")); return

        pet = await self._get_pet(ctx.author.id, slot)
        if not pet: await ctx.send(embed=warn(f"❌ Không có thú #{slot}!")); return

        eq_id = pet.get(f"equip_{eq_slot}","")
        if not eq_id:
            await ctx.send(embed=warn(f"❌ Slot {eq_slot} đang trống!")); return

        await self._add_item(ctx.author.id, f"pet_eq_{eq_id}", 1)
        await self._save_pet(ctx.author.id, slot, **{f"equip_{eq_slot}": ""})
        await ctx.send(embed=make("✅ Tháo Trang Bị", f"Đã tháo slot **{eq_slot}** và trả về túi.", 0x88BB88))

    # ──────────────────────────────────────────────────────────
    #  TẨY HUYẾT MẠCH
    # ──────────────────────────────────────────────────────────
    @linhthu.command(name="huyetmach", aliases=["reroll","tay"])
    async def huyetmach(self, ctx, slot: int):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player: await ctx.send(embed=warn("Chưa nhập môn!")); return

        COST = 200_000_000
        if not await self._pay_lt(ctx.author.id, COST):
            await ctx.send(embed=warn("❌ Cần **200,000,000 LT** để tẩy luyện Huyết Mạch!")); return

        pet = await self._get_pet(ctx.author.id, slot)
        if not pet: await ctx.send(embed=warn(f"❌ Không có thú #{slot}!")); return

        if not await self._use_item(ctx.author.id, "huyet_mach_dan"):
            await self._add_lt(ctx.author.id, COST)  # hoàn tiền
            await ctx.send(embed=warn("❌ Cần **Huyết Mạch Đan**!\nMua tại `,tl shop linhthu`")); return

        bonuses = ["Tốc Độ Tăng Cao","Phòng Thủ Kiên Cố","Công Kích Mạnh Mẽ",
                   "Sinh Mệnh Dồi Dào","Vận Khí Thượng Thừa","Bùng Nổ Sát Thương"]
        result = random.choice(bonuses)
        d = PET_DATA.get(pet["pet_type"], {})

        await ctx.send(embed=make(
            "🩸 Tẩy Luyện Huyết Mạch",
            f"**{d.get('name','?')}** #{slot}\n\n"
            f"✨ Huyết Mạch mới: **{result}**\n"
            f"_(Tăng thêm 10% chỉ số tương ứng)_",
            0xFF4488
        ))

    # ──────────────────────────────────────────────────────────
    #  ARENA
    # ──────────────────────────────────────────────────────────
    @linhthu.command(name="arena", aliases=["pvp","dadau"])
    async def arena(self, ctx, member: discord.Member = None):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player: await ctx.send(embed=warn("Chưa nhập môn!")); return

        COST = 10_000_000
        my_pet = await self._get_active(ctx.author.id)
        if not my_pet:
            await ctx.send(embed=warn("❌ Cần trang bị Linh Thú! `,tl pet equip [STT]`")); return

        if member is None or member.id == ctx.author.id:
            await ctx.send(embed=warn("❌ Tag người chơi muốn thách đấu! `,tl pet arena @người`")); return

        opp_player = await self.bot.db.get_player(member.id)
        if not opp_player:
            await ctx.send(embed=warn("❌ Người đó chưa nhập môn!")); return

        opp_pet = await self._get_active(member.id)
        if not opp_pet:
            await ctx.send(embed=warn("❌ Đối thủ chưa trang bị Linh Thú!")); return

        if not await self._pay_lt(ctx.author.id, COST):
            await ctx.send(embed=warn(f"❌ Cần **{fmt(COST)} LT** để tham gia Arena!")); return

        # Tính power
        my_power   = _pet_power(my_pet)   * (1.25 if my_pet.get("awakened") else 1)
        opp_power  = _pet_power(opp_pet)  * (1.25 if opp_pet.get("awakened") else 1)
        my_luck    = int(_safe(player, "luck", 0))
        win_chance = min(0.85, max(0.15, 0.5 + (my_power - opp_power) / max(my_power + opp_power, 1) * 0.5 + my_luck/5000))
        win = random.random() < win_chance

        my_d   = PET_DATA.get(my_pet["pet_type"],  {})
        opp_d  = PET_DATA.get(opp_pet["pet_type"], {})

        if win:
            await self._add_lt(ctx.author.id, COST * 2)
            e = discord.Embed(
                title="⚔️ ARENA — THẮNG!",
                description=(
                    f"**{my_d.get('name','?')}** vs **{opp_d.get('name','?')}**\n\n"
                    f"🏆 **{player['name']}** chiến thắng!\n"
                    f"💰 Nhận: **{fmt(COST*2)} LT**"
                ),
                color=0x55FF55
            )
        else:
            e = discord.Embed(
                title="⚔️ ARENA — THUA",
                description=(
                    f"**{my_d.get('name','?')}** vs **{opp_d.get('name','?')}**\n\n"
                    f"💀 **{player['name']}** thất bại!\n"
                    f"💸 Mất: **{fmt(COST)} LT**"
                ),
                color=0xFF4444
            )
        e.add_field(name=f"⚡ {player['name']}", value=f"Power: **{my_power:,.0f}**", inline=True)
        e.add_field(name=f"⚡ {opp_player['name']}", value=f"Power: **{opp_power:,.0f}**", inline=True)
        await ctx.send(embed=e)

    # ──────────────────────────────────────────────────────────
    #  RENAME
    # ──────────────────────────────────────────────────────────
    @linhthu.command(name="rename", aliases=["tenla","dat"])
    async def rename(self, ctx, slot: int, *, name: str):
        if len(name) > 20:
            await ctx.send(embed=warn("❌ Tên tối đa 20 ký tự!")); return
        pet = await self._get_pet(ctx.author.id, slot)
        if not pet: await ctx.send(embed=warn(f"❌ Không có thú #{slot}!")); return
        await self._save_pet(ctx.author.id, slot, nickname=name[:20])
        await ctx.send(embed=make("✅ Đặt Tên", f"Thú #{slot} giờ tên là **{name}**", 0x88BBFF))

    # ──────────────────────────────────────────────────────────
    #  RELEASE — Phóng sinh
    # ──────────────────────────────────────────────────────────
    @linhthu.command(name="release", aliases=["phongsinh","tha"])
    async def release(self, ctx, slot: int):
        pet = await self._get_pet(ctx.author.id, slot)
        if not pet: await ctx.send(embed=warn(f"❌ Không có thú #{slot}!")); return
        if pet.get("equipped"):
            await ctx.send(embed=warn("❌ Tháo thú trước khi phóng sinh! `,tl pet unequip`")); return

        d = PET_DATA.get(pet["pet_type"], {})
        rarity = d.get("rarity","common")
        if rarity in ("mythic","divine","legendary"):
            # Xác nhận
            e = warn(
                f"⚠️ Bạn sắp phóng sinh **{d.get('name','?')}** ({rarity.upper()})!\n"
                f"Gõ `,tl pet release {slot} confirm` để xác nhận."
            )
            await ctx.send(embed=e); return

        await self.bot.db.execute(
            "DELETE FROM pets WHERE user_id=? AND slot=?", (str(ctx.author.id), slot)
        )
        await ctx.send(embed=make("🕊️ Phóng Sinh", f"**{d.get('name','?')}** đã được tự do.", 0xAADDFF))

    @linhthu.command(name="release_confirm")
    async def release_confirm(self, ctx, slot: int, confirm: str = ""):
        if confirm.lower() != "confirm": return
        pet = await self._get_pet(ctx.author.id, slot)
        if not pet: return
        d = PET_DATA.get(pet["pet_type"], {})
        await self.bot.db.execute(
            "DELETE FROM pets WHERE user_id=? AND slot=?", (str(ctx.author.id), slot)
        )
        await ctx.send(embed=make("🕊️ Phóng Sinh", f"**{d.get('name','?')}** đã được tự do.", 0xAADDFF))

    # ──────────────────────────────────────────────────────────
    #  SHOP LINHTHU (info)
    # ──────────────────────────────────────────────────────────
    @commands.command(name="shoplinhthu")
    async def shoplinhthu(self, ctx):
        e = discord.Embed(title="🛒 Shop Linh Thú", color=0xFF9800)
        for key, item in PET_ITEMS.items():
            e.add_field(
                name=f"{item['name']}",
                value=f"💰 {fmt(item['price'])} LT\n_{item['desc']}_\nID: `{key}`",
                inline=True
            )
        e.set_footer(text="Mua bằng: ,tl buy [ID] [số lượng]")
        await ctx.send(embed=e)


async def setup(bot):
    await bot.add_cog(LinhThu(bot))

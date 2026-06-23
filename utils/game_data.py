"""utils/game_data.py - Dữ liệu game v3 CHUẨN"""
import random

# ══ CẢNH GIỚI ════════════════════════════════════════════════
REALMS = [
    # ── Sơ Cấp ──────────────────────────────
    {"name":"Luyện Thể",   "tiers":9, "exp":200,       "mult":1.2},
    {"name":"Tụ Khí",      "tiers":9, "exp":1_000,     "mult":1.4},
    {"name":"Luyện Khí",   "tiers":9, "exp":5_000,     "mult":1.6},
    {"name":"Ngưng Khí",   "tiers":9, "exp":20_000,    "mult":1.8},
    {"name":"Trúc Cơ",     "tiers":9, "exp":80_000,    "mult":2.0},
    {"name":"Tử Phủ",      "tiers":9, "exp":300_000,   "mult":2.2},
    {"name":"Đạo Cung",    "tiers":9, "exp":1_000_000, "mult":2.4},
    {"name":"Kim Đan",     "tiers":9, "exp":4_000_000, "mult":2.6},
    # ── Trung Cấp ────────────────────────────
    {"name":"Nguyên Anh",  "tiers":9, "exp":1.5e7,     "mult":2.8},
    {"name":"Hóa Thần",    "tiers":9, "exp":6e7,       "mult":3.0},
    {"name":"Luyện Hư",    "tiers":9, "exp":2.5e8,     "mult":3.2},
    {"name":"Hợp Thể",     "tiers":9, "exp":1e9,       "mult":3.4},
    {"name":"Đại Thừa",    "tiers":9, "exp":4e9,       "mult":3.6},
    {"name":"Độ Kiếp",     "tiers":9, "exp":1.5e10,    "mult":3.8},
    # ── Tiên Cấp ─────────────────────────────
    {"name":"Bán Tiên",    "tiers":9, "exp":6e10,      "mult":4.0, "fail":0.10},
    {"name":"Nhân Tiên",   "tiers":9, "exp":2.5e11,    "mult":4.2, "fail":0.12},
    {"name":"Địa Tiên",    "tiers":9, "exp":1e12,      "mult":4.4, "fail":0.14},
    {"name":"Thiên Tiên",  "tiers":9, "exp":4e12,      "mult":4.6, "fail":0.16},
    {"name":"Chân Tiên",   "tiers":9, "exp":1.5e13,    "mult":4.8, "fail":0.18},
    {"name":"Huyền Tiên",  "tiers":9, "exp":6e13,      "mult":5.0, "fail":0.20},
    {"name":"Kim Tiên",    "tiers":9, "exp":2.5e14,    "mult":5.2, "fail":0.22},
    {"name":"Thái Ất Tiên","tiers":9, "exp":1e15,      "mult":5.4, "fail":0.24},
    {"name":"Đại La Tiên", "tiers":9, "exp":4e15,      "mult":5.6, "fail":0.26},
    # ── Tiên Vương ───────────────────────────
    {"name":"Tiên Quân",   "tiers":9, "exp":1.5e16,    "mult":5.8, "fail":0.28},
    {"name":"Tiên Vương",  "tiers":9, "exp":6e16,      "mult":6.0, "fail":0.30},
    {"name":"Tiên Hoàng",  "tiers":9, "exp":2.5e17,    "mult":6.2, "fail":0.32},
    {"name":"Tiên Tôn",    "tiers":9, "exp":1e18,      "mult":6.4, "fail":0.34},
    {"name":"Tiên Đế",     "tiers":9, "exp":4e18,      "mult":6.6, "fail":0.36},
    {"name":"Tiên Thánh",  "tiers":9, "exp":1.5e19,    "mult":6.8, "fail":0.38},
    {"name":"Tiên Tổ",     "tiers":3, "exp":6e19,      "mult":7.0, "fail":0.40},
    # ── Thần Cấp ─────────────────────────────
    {"name":"Chân Thần",   "tiers":9, "exp":2.5e20,    "mult":7.2, "fail":0.42},
    {"name":"Thiên Thần",  "tiers":9, "exp":1e21,      "mult":7.4, "fail":0.44},
    {"name":"Cổ Thần",     "tiers":9, "exp":4e21,      "mult":7.6, "fail":0.46},
    {"name":"Thần Vương",  "tiers":9, "exp":1.5e22,    "mult":7.8, "fail":0.48},
    {"name":"Thần Hoàng",  "tiers":9, "exp":6e22,      "mult":8.0, "fail":0.50},
    {"name":"Thần Đế",     "tiers":9, "exp":2.5e23,    "mult":8.2, "fail":0.52},
    {"name":"Thần Tôn",    "tiers":9, "exp":1e24,      "mult":8.4, "fail":0.54},
    {"name":"Thần Thánh",  "tiers":9, "exp":4e24,      "mult":8.6, "fail":0.56},
    {"name":"Thần Tổ",     "tiers":3, "exp":1.5e25,    "mult":8.8, "fail":0.58},
    # ── Hỗn Độn / Vô Thủy ───────────────────
    {"name":"Hỗn Độn",     "tiers":9, "exp":6e25,      "mult":9.0, "fail":0.60},
    {"name":"Hồng Mông",   "tiers":9, "exp":2.5e26,    "mult":9.2, "fail":0.62},
    {"name":"Thái Sơ",     "tiers":9, "exp":1e27,      "mult":9.4, "fail":0.64},
    {"name":"Khởi Nguyên", "tiers":9, "exp":4e27,      "mult":9.6, "fail":0.66},
    {"name":"Tạo Hóa",     "tiers":9, "exp":1.5e28,    "mult":9.8, "fail":0.68},
    {"name":"Chưởng Đạo",  "tiers":9, "exp":6e28,      "mult":10.0,"fail":0.70},
    {"name":"Bất Hủy",     "tiers":9, "exp":2.5e29,    "mult":10.0,"fail":0.72},
    {"name":"Vĩnh Hằng",   "tiers":9, "exp":1e30,      "mult":10.0,"fail":0.74},
    {"name":"Siêu Thoát",  "tiers":9, "exp":4e30,      "mult":10.0,"fail":0.76},
    {"name":"Chúa Tể",     "tiers":9, "exp":1.5e31,    "mult":10.0,"fail":0.78},
    {"name":"Vô Thượng Đạo Tổ","tiers":9, "exp":6e31,      "mult":10.0,"fail":0.80},
    # ── Hư Không Cấp ─────────────────────────
    {"name":"Hư Không Thần",  "tiers":9, "exp":2.5e32,    "mult":10.0,"fail":0.82},
    {"name":"Hư Không Thánh", "tiers":9, "exp":1e33,      "mult":10.0,"fail":0.82},
    {"name":"Hư Không Vương", "tiers":9, "exp":4e33,      "mult":10.0,"fail":0.84},
    {"name":"Hư Không Đế",    "tiers":9, "exp":1.5e34,    "mult":10.0,"fail":0.84},
    {"name":"Hư Không Tổ",    "tiers":9, "exp":6e34,      "mult":10.0,"fail":0.86},
    # ── Thiên Đạo Cấp ────────────────────────
    {"name":"Thiên Đạo Giả",  "tiers":9, "exp":2.5e35,    "mult":10.0,"fail":0.86},
    {"name":"Thiên Đạo Thần", "tiers":9, "exp":1e36,      "mult":10.0,"fail":0.88},
    {"name":"Thiên Đạo Thánh","tiers":9, "exp":4e36,      "mult":10.0,"fail":0.88},
    {"name":"Thiên Đạo Đế",   "tiers":9, "exp":1.5e37,    "mult":10.0,"fail":0.90},
    {"name":"Thiên Đạo Tổ",   "tiers":9, "exp":6e37,      "mult":10.0,"fail":0.90},
    # ── Vũ Trụ Cấp ───────────────────────────
    {"name":"Vũ Trụ Thần",    "tiers":9, "exp":2.5e38,    "mult":10.0,"fail":0.92},
    {"name":"Vũ Trụ Thánh",   "tiers":9, "exp":1e39,      "mult":10.0,"fail":0.92},
    {"name":"Vũ Trụ Đế",      "tiers":9, "exp":4e39,      "mult":10.0,"fail":0.94},
    {"name":"Vũ Trụ Tổ",      "tiers":9, "exp":1.5e40,    "mult":10.0,"fail":0.94},
    # ── Bản Nguyên Cấp ───────────────────────
    {"name":"Bản Nguyên Thần", "tiers":9, "exp":6e40,      "mult":10.0,"fail":0.95},
    {"name":"Bản Nguyên Thánh","tiers":9, "exp":2.5e41,    "mult":10.0,"fail":0.95},
    {"name":"Bản Nguyên Đế",   "tiers":9, "exp":1e42,      "mult":10.0,"fail":0.96},
    {"name":"Bản Nguyên Tổ",   "tiers":9, "exp":4e42,      "mult":10.0,"fail":0.96},
    # ── Tuyệt Đỉnh ───────────────────────────
    {"name":"Vô Cực Đạo Thần", "tiers":9, "exp":1.5e43,    "mult":10.0,"fail":0.98},
    {"name":"Vạn Giới Chí Tôn","tiers":1, "exp":0,         "mult":10.0,"fail":0.0},
]


# Map cảnh giới cũ (20 realm) → index mới (70 realm)
# Dựa theo tên: tìm index mới tương ứng với tên cũ
_REALM_NAME_TO_IDX = {r["name"]: i for i, r in enumerate(REALMS)}

# Cảnh giới cũ theo thứ tự index (để migrate DB)
_OLD_REALM_NAMES = [
    "Phàm Nhân","Luyện Khí","Trúc Cơ","Kim Đan","Nguyên Anh",
    "Hóa Thần","Luyện Hư","Hợp Thể","Đại Thừa","Độ Kiếp",
    "Chân Tiên","Kim Tiên","Thái Ất","Đại La","Chuẩn Thánh",
    "Thánh Nhân","Lọ Đế","Lọ Tôn","Lọ Vương","Hỗn Độn Vô Thủy",
]
# Map tên cũ -> tên mới gần nhất
_OLD_TO_NEW_NAME = {
    "Phàm Nhân":         "Luyện Thể",
    "Luyện Khí":         "Luyện Khí",
    "Trúc Cơ":           "Trúc Cơ",
    "Kim Đan":           "Kim Đan",
    "Nguyên Anh":        "Nguyên Anh",
    "Hóa Thần":          "Hóa Thần",
    "Luyện Hư":          "Luyện Hư",
    "Hợp Thể":           "Hợp Thể",
    "Đại Thừa":          "Đại Thừa",
    "Độ Kiếp":           "Độ Kiếp",
    "Chân Tiên":         "Chân Tiên",
    "Kim Tiên":          "Kim Tiên",
    "Thái Ất":           "Thái Ất Tiên",
    "Đại La":            "Đại La Tiên",
    "Chuẩn Thánh":       "Tiên Quân",
    "Thánh Nhân":        "Tiên Vương",
    "Lọ Đế":             "Tiên Hoàng",
    "Lọ Tôn":            "Tiên Tôn",
    "Lọ Vương":          "Tiên Đế",
    "Lọ Quân":           "Tiên Thánh",
    "Hỗn Độn Vô Thủy":  "Vô Thượng Đạo Tổ",
}

def migrate_realm_index(old_idx: int) -> int:
    """Chuyển realm_index cũ (≤19) sang index mới (≤69)"""
    if old_idx >= len(REALMS):
        # Index cũ nằm ngoài range mới - map theo tỉ lệ
        if old_idx < len(_OLD_REALM_NAMES):
            old_name = _OLD_REALM_NAMES[old_idx]
            new_name = _OLD_TO_NEW_NAME.get(old_name)
            if new_name and new_name in _REALM_NAME_TO_IDX:
                return _REALM_NAME_TO_IDX[new_name]
        # Fallback: clamp về max
        return len(REALMS) - 1
    return old_idx  # Index mới, giữ nguyên

def get_realm_name(p: dict) -> str:
    ri = int(p.get("realm_index", 0))
    # Auto-migrate nếu index cũ vượt range
    if ri >= len(REALMS):
        ri = migrate_realm_index(ri)
    r = REALMS[ri]
    return r["name"] if r["tiers"] == 1 else f"{r['name']} - Tầng {p.get('realm_tier', 1)}"

def get_exp_req(p: dict) -> int:
    ri = int(p.get("realm_index", 0))
    if ri >= len(REALMS):
        ri = migrate_realm_index(ri)
    r = REALMS[ri]
    tier = int(p.get("realm_tier", 1))
    return int(r["exp"] * (tier ** r["mult"]))

# Alias tương thích
get_realm_display  = get_realm_name
get_exp_required   = get_exp_req


# ── CHUYỂN SINH (Prestige) ───────────────────────────────────────
# Mỗi lần chuyển sinh: +15% tốc độ tu luyện vĩnh viễn, giảm dần độ
# hiệu quả (lũy thừa 0.92) để tránh lạm phát vô hạn ở số lần rất cao.
PRESTIGE_BASE_BONUS = 0.15
PRESTIGE_DECAY      = 0.92

def prestige_exp_mult(prestige: int) -> float:
    """Hệ số nhân tốc độ tu luyện vĩnh viễn từ số lần Chuyển Sinh."""
    p = int(prestige or 0)
    if p <= 0:
        return 1.0
    total = 1.0
    bonus = PRESTIGE_BASE_BONUS
    for _ in range(p):
        total += bonus
        bonus *= PRESTIGE_DECAY
    return round(total, 4)

PRESTIGE_TITLES = [
    "", "Nhất Chuyển Đạo Nhân", "Nhị Chuyển Chân Nhân", "Tam Chuyển Thiên Tôn",
    "Tứ Chuyển Đế Quân", "Ngũ Chuyển Cổ Thần", "Lục Chuyển Hỗn Độn",
    "Thất Chuyển Vô Cực", "Bát Chuyển Hư Vô", "Cửu Chuyển Diệt Thế",
]

def get_prestige_title(prestige: int) -> str:
    p = int(prestige or 0)
    if p <= 0:
        return ""
    if p < len(PRESTIGE_TITLES):
        return PRESTIGE_TITLES[p]
    return f"Thập Chuyển+{p - 9} Vĩnh Hằng"


DAO = {
    "nhapma":  {"name":"Ma Đạo",   "icon":"🌑","desc":"Sát thương bùng nổ",    "atk":1.30,"def":0.90,"crit":10},
    "nhapdao": {"name":"Chính Đạo","icon":"☀️","desc":"Cân bằng toàn diện",    "atk":1.10,"def":1.10,"hp":1.10},
    "nhapnho": {"name":"Nho Đạo",  "icon":"📖","desc":"Phòng thủ kiên cố",     "def":1.50,"hp":1.30,"atk":0.85},
    "nhapquy": {"name":"Quỷ Đạo",  "icon":"👻","desc":"Tốc độ xuất thần",      "spd":1.50,"crit":15,"def":0.85},
    "nhapyeu": {"name":"Yêu Đạo",  "icon":"🐾","desc":"Sinh mệnh dồi dào",     "hp":1.60,"atk":1.05,"spd":1.05},
    "nhaplo":  {"name":"Lọ Đạo",   "icon":"🧴","desc":"EXP nhanh, Phẩm Parody","exp_rate":1.25,"luck":50,"atk":0.95},
    # ── ĐẠO ĐẶC BIỆT (chỉ Admin gán được, không thể nhập môn thường) ──
    "thiendao": {"name":"Thiên Đạo","icon":"🌟","desc":"Đạo của Trời, tối cao vô song",
                  "atk":3.0,"def":3.0,"hp":3.0,"spd":2.0,"crit":30,"exp_rate":2.0,"luck":100,"admin_only":True},
    "thiensu":  {"name":"Thiên Sứ","icon":"😇","desc":"Phó Thiên Đạo, mạnh hơn người thường 10 lần",
                  "atk":10.0,"def":10.0,"hp":10.0,"spd":10.0,"crit":20,"exp_rate":1.5,"luck":50,"admin_only":True},
}

# Đạo chỉ admin mới gán được (không xuất hiện trong lệnh nhập môn thường)
ADMIN_ONLY_DAO = [k for k, v in DAO.items() if v.get("admin_only")]

# ══ ĐẶC TÍNH ════════════════════════════════════════════════
LINH_CAN = [
    # ── Phế Phẩm ──────────────────────────────────────
    {"name":"Phế Linh Căn",             "rarity":"trash",      "w":5,   "exp_rate":0.50},
    # ── Hạ Phẩm ───────────────────────────────────────
    {"name":"Ngũ Hành Tạp Linh Căn",    "rarity":"common",     "w":14,  "exp_rate":0.60},
    {"name":"Tứ Hệ Linh Căn",           "rarity":"common",     "w":18,  "exp_rate":0.80},
    {"name":"Tam Hệ Linh Căn",          "rarity":"uncommon",   "w":16,  "exp_rate":1.00, "atk":1.03},
    # ── Thượng Phẩm ────────────────────────────────────
    {"name":"Song Hệ Linh Căn",         "rarity":"rare",       "w":12,  "exp_rate":1.10, "atk":1.08, "luck":5},
    # ── Địa Phẩm ───────────────────────────────────────
    {"name":"Đơn Hệ Linh Căn",          "rarity":"epic",       "w":8,   "exp_rate":1.20, "atk":1.10, "def":1.05},
    {"name":"Dị Linh Căn (Lôi)",        "rarity":"epic",       "w":4,   "exp_rate":1.40, "atk":1.15, "crit":12, "luck":10},
    {"name":"Dị Linh Căn (Băng)",       "rarity":"epic",       "w":4,   "exp_rate":1.40, "atk":1.10, "def":1.18, "hp":1.10},
    {"name":"Dị Linh Căn (Phong)",      "rarity":"epic",       "w":4,   "exp_rate":1.40, "atk":1.10, "spd":1.22, "crit":8},
    {"name":"Dị Linh Căn (Hỏa)",        "rarity":"epic",       "w":3,   "exp_rate":1.45, "atk":1.20, "crit":15, "luck":8},
    # ── Thiên Phẩm ─────────────────────────────────────
    {"name":"Thiên Linh Căn",           "rarity":"legendary",  "w":2,   "exp_rate":1.50, "atk":1.25, "def":1.10, "luck":30},
    {"name":"Cửu Biến Dị Căn",          "rarity":"legendary",  "w":1.5, "exp_rate":1.60, "atk":1.30, "spd":1.10, "crit":15, "luck":25},
    # ── Tiên Phẩm ──────────────────────────────────────
    {"name":"Âm Dương Hỗn Độn Căn",     "rarity":"mythic",     "w":1,   "exp_rate":1.80, "atk":1.50, "def":1.20, "hp":1.20, "luck":60},
    {"name":"Hỗn Độn Linh Căn",         "rarity":"mythic",     "w":0.8, "exp_rate":2.00, "atk":1.60, "crit":20,  "luck":80},
    # ── Thần Phẩm ──────────────────────────────────────
    {"name":"Vô Thủy Linh Căn",         "rarity":"divine",     "w":0.4, "exp_rate":2.50, "atk":1.90, "def":1.30, "hp":1.30, "luck":120},
    {"name":"Thái Cổ Hỗn Nguyên Căn",   "rarity":"divine",     "w":0.2, "exp_rate":3.00, "atk":2.20, "def":1.40, "hp":1.40, "spd":1.20, "crit":25, "luck":180},
    # ── Vô Thượng Phẩm ─────────────────────────────────
    {"name":"Vạn Đạo Quy Nhất Căn",     "rarity":"transcendent","w":0.08,"exp_rate":4.00, "atk":2.80, "def":1.60, "hp":1.60, "spd":1.30, "crit":30, "luck":300},
    {"name":"Khai Thiên Thần Căn",       "rarity":"transcendent","w":0.02,"exp_rate":5.00, "atk":3.50, "def":2.00, "hp":2.00, "spd":1.50, "crit":40, "luck":500},
]
THE_CHAT = [
    # ── Phàm Phẩm ──────────────────────────────────────
    {"name":"Bình Thường",             "rarity":"common",     "w":25},
    {"name":"Phàm Nhân Chi Thể",       "rarity":"trash",     "w":12, "def":1.05, "hp":1.05},
    {"name":"Hàn Độc Chi Thể",         "rarity":"trash",     "w":6,  "def":0.90, "hp":0.90, "spd":0.90},
    {"name":"Thiên Tuyệt Chi Thể",     "rarity":"trash",     "w":5,  "def":0.90, "hp":0.90, "spd":0.90},
    # ── Hạ Phẩm ───────────────────────────────────────
    {"name":"Đồng Bì Thiết Cốt",       "rarity":"uncommon",  "w":10, "def":1.18, "hp":1.15},
    {"name":"Bách Mạch Thông Suốt",    "rarity":"uncommon",  "w":10, "def":1.12, "hp":1.18, "spd":1.05},
    {"name":"Cường Hồn Thể",           "rarity":"uncommon",  "w":10, "hp":1.22, "def":1.08},
    {"name":"Thiên Sinh Thần Lực",     "rarity":"uncommon",  "w":7,  "atk":1.20, "def":1.50, "hp":1.50, "spd":1.15, "crit_resist":10},
    # ── Trung Phẩm ─────────────────────────────────────
    {"name":"Kim Cương Thể",           "rarity":"rare",      "w":9,  "def":1.30, "hp":1.15, "crit_resist":8},
    {"name":"Thiết Huyết Cương Thể",   "rarity":"rare",      "w":6,  "atk":1.15, "def":1.25, "hp":1.20},
    # ── Thượng Phẩm ────────────────────────────────────
    {"name":"Long Huyết Thể",          "rarity":"epic",      "w":6,  "atk":1.35, "hp":1.30, "crit":8},
    {"name":"Thần Lực Cổ Thể",         "rarity":"epic",      "w":4,  "atk":1.30, "def":1.25, "hp":1.25, "spd":1.12},
    # ── Địa Phẩm ───────────────────────────────────────
    {"name":"Thương Thiên Bá Thể",     "rarity":"legendary", "w":3.5,"atk":1.50, "def":1.35, "hp":1.40, "luck":20},
    {"name":"Huyền Vũ Bất Diệt Thể",   "rarity":"legendary", "w":2,  "atk":1.40, "def":1.60, "hp":1.55, "crit_resist":20, "luck":15},
    # ── Thiên Phẩm ─────────────────────────────────────
    {"name":"Thiên Ma Thể",            "rarity":"mythic",    "w":2,  "atk":1.80, "spd":1.40, "crit":25, "luck":50},
    {"name":"Cửu Dương Thần Thể",      "rarity":"mythic",    "w":1.5,"atk":1.70, "def":1.50, "hp":1.60, "crit":18, "luck":40},
    # ── Thánh Phẩm ─────────────────────────────────────
    {"name":"Vô Cực Đế Thể",           "rarity":"divine",    "w":0.6,"atk":2.20, "def":1.70, "hp":2.20, "luck":120},
    {"name":"Hỗn Nguyên Bất Hoại Thể", "rarity":"divine",    "w":0.3,"atk":2.50, "def":2.00, "hp":2.50, "spd":1.30, "crit":20, "luck":150},
    # ── Vô Thượng Phẩm ─────────────────────────────────
    {"name":"Khai Thiên Thần Thể",     "rarity":"transcendent","w":0.08,"atk":3.20, "def":2.50, "hp":3.00, "spd":1.50, "crit":30, "luck":250},
    {"name":"Vạn Cổ Bất Diệt Thần Thể","rarity":"transcendent","w":0.02,"atk":4.00, "def":3.00, "hp":4.00, "spd":1.80, "crit":40, "luck":400},
]
HUYET_MACH = [
    # ── Phàm Phẩm ──────────────────────────────────────
    {"name":"Huyết Mạch Phàm Nhân",         "rarity":"common",      "w":25,  "crit":3},
    {"name":"Huyết Mạch Hoàng Tộc",         "rarity":"uncommon",    "w":10,  "def":1.05, "hp":1.05, "crit":5, "luck":5},
    # ── Hạ Phẩm ───────────────────────────────────────
    {"name":"Huyết Mạch Yêu Thú (Tạp)",    "rarity":"uncommon",    "w":10,  "atk":1.12, "spd":1.18, "crit":8,  "dodge":8},
    {"name":"Lang Tộc Huyết Mạch",          "rarity":"rare",        "w":8,   "atk":1.20, "spd":1.22, "crit":10, "dodge":12},
    # ── Trung Phẩm ─────────────────────────────────────
    {"name":"Thanh Khâu Hồ Tộc (Cửu Vĩ)",  "rarity":"epic",        "w":6,   "atk":1.25, "spd":1.30, "crit":12, "dodge":15, "luck":15},
    {"name":"Hùng Vương Địa Huyết",         "rarity":"epic",        "w":5,   "atk":1.25, "def":1.22, "hp":1.22, "crit_resist":15},
    # ── Thượng Phẩm ────────────────────────────────────
    {"name":"Giao Long Huyết Mạch",         "rarity":"legendary",   "w":5,   "atk":1.50, "def":1.40, "hp":1.40, "spd":1.20, "crit":15, "crit_resist":12},
    {"name":"Long Tộc Huyết Mạch",          "rarity":"legendary",   "w":5,   "atk":1.45, "hp":1.35, "crit":12, "luck":20},
    {"name":"Phượng Hoàng Huyết",           "rarity":"legendary",   "w":4,   "atk":1.35, "spd":1.40, "crit":18, "luck":25},
    # ── Địa Phẩm ───────────────────────────────────────
    {"name":"Thần Long Cổ Huyết",           "rarity":"mythic",      "w":3,   "atk":1.75, "def":1.50, "hp":1.55, "crit":20, "luck":50},
    {"name":"Bất Tử Tiên Hoàng",            "rarity":"mythic",      "w":2.5, "hp":1.80,  "def":1.60, "crit_resist":25, "luck":45},
    # ── Thiên Phẩm ─────────────────────────────────────
    {"name":"Hỗn Độn Cổ Huyết",             "rarity":"divine",      "w":1.5, "atk":2.00, "hp":2.00, "def":1.50, "luck":100},
    {"name":"Thái Cổ Thần Huyết",           "rarity":"divine",      "w":0.8, "atk":2.30, "hp":2.30, "def":1.80, "spd":1.20, "crit":20, "luck":160},
    # ── Thánh Phẩm ─────────────────────────────────────
    {"name":"Nguyên Thủy Ma Thần Huyết",    "rarity":"transcendent","w":0.15,"atk":3.00, "hp":2.80, "def":2.20, "spd":1.40, "crit":28, "luck":250},
    {"name":"Khai Thiên Hỗn Nguyên Huyết",  "rarity":"transcendent","w":0.05,"atk":4.00, "hp":3.50, "def":2.80, "spd":1.60, "crit":38, "dodge":25, "luck":400},
]

# ══ ĐỘT PHÁ (breakthrough) helpers — dùng để admin set cảnh giới
# ra đúng 1 mức sức mạnh tuyệt đối, không phụ thuộc dữ liệu cũ ═
BT_ATK_MULT = 1.22
BT_DEF_MULT = 1.22
BT_HP_MULT  = 1.28
BT_SPD_MULT = 1.05

_LC_BY_NAME = {e["name"]: e for e in LINH_CAN}
_TC_BY_NAME = {e["name"]: e for e in THE_CHAT}
_HM_BY_NAME = {e["name"]: e for e in HUYET_MACH}

def total_breakthroughs(realm_idx: int, tier: int) -> int:
    """Tổng số lần đột phá (tier-up) cần để đạt tới (realm_idx, tier),
    tính từ mốc Luyện Thể - Tầng 1 (0 lần đột phá)."""
    realm_idx = max(0, min(int(realm_idx), len(REALMS) - 1))
    tier = max(1, int(tier))
    n = sum(r["tiers"] for r in REALMS[:realm_idx])
    n += tier - 1
    return n

def scale_stats_for_realm_change(p: dict, new_realm_idx: int, new_tier: int) -> dict:
    """Đặt LẠI atk/def_/hp/hp_max/spd/luc_chien theo đúng cảnh giới mới,
    tính tuyệt đối từ công thức gốc (như lúc nhập môn) nhân lũy thừa số
    lần đột phá tới cảnh giới đó — KHÔNG dựa vào realm_index/tier hay
    stat cũ trong DB (vì dữ liệu cũ có thể đã sai/lệch do bug/chỉnh tay
    trước đây, dẫn tới scale tương đối ra số âm khổng lồ → stat về 0).
    Bonus Đạo/Linh Căn/Thể Chất/Huyết Mạch hiện tại của người chơi vẫn
    được áp dụng (tra theo tên đã lưu); nếu là tên tùy chỉnh không khớp
    danh sách gốc (VD: từ tẩy tủy đặc biệt) thì coi như không có bonus
    số (hệ số 1.0) để tránh suy ra sai.

    ⚠️  Người chơi mang cờ vt_locked=1 (Vô Thượng Đạo Tổ) sẽ không bị
    scale lại — stats của họ giữ nguyên vô cực."""
    # Guard: Vô Thượng không bị scale override
    if int(p.get("vt_locked", 0) or 0) == 1:
        oa  = float(p.get("atk",    100) or 100)
        od  = float(p.get("def_",    50) or  50)
        oh  = float(p.get("hp_max",1000) or 1000)
        osp = float(p.get("spd",     50) or  50)
        nl  = float(p.get("luc_chien", oa) or oa)
        return {
            "old": {"atk": oa, "def_": od, "hp_max": oh, "spd": osp},
            "new": {"atk": oa, "def_": od, "hp_max": oh, "spd": osp, "luc_chien": nl},
        }

    n = total_breakthroughs(new_realm_idx, new_tier)

    dao_info = DAO.get(p.get("dao", ""), {})
    lc = _LC_BY_NAME.get(p.get("linh_can", ""), {})
    tc = _TC_BY_NAME.get(p.get("the_chat", ""), {})
    hm = _HM_BY_NAME.get(p.get("huyet_mach", ""), {})

    atk_mult = dao_info.get("atk", 1.0) * lc.get("atk", 1.0) * tc.get("atk", 1.0) * hm.get("atk", 1.0)
    def_mult = dao_info.get("def", 1.0) * tc.get("def", 1.0) * hm.get("def", 1.0)
    hp_mult  = dao_info.get("hp",  1.0) * tc.get("hp",  1.0) * hm.get("hp",  1.0)
    spd_mult = dao_info.get("spd", 1.0)
    crit     = float(p.get("crit", 5.0) or 5.0)

    oa  = float(p.get("atk", 100) or 100)
    od  = float(p.get("def_", 50) or 50)
    oh  = float(p.get("hp_max", 1000) or 1000)
    osp = float(p.get("spd", 50) or 50)

    na  = round(100  * atk_mult * (BT_ATK_MULT ** n), 2)
    nd  = round(50   * def_mult * (BT_DEF_MULT ** n), 2)
    nh  = round(1000 * hp_mult  * (BT_HP_MULT  ** n), 2)
    nsp = round(50   * spd_mult * (BT_SPD_MULT ** n), 2)
    nl  = round(na * 2.0 + nd * 1.2 + nh * 0.005 + nsp * 0.8 + crit * 50, 2)

    return {
        "old": {"atk": oa, "def_": od, "hp_max": oh, "spd": osp},
        "new": {"atk": na, "def_": nd, "hp_max": nh, "spd": nsp, "luc_chien": nl},
    }

MENH_CACH = [
    # Phàm Phẩm
    {"name":"Thiên Sát Cô Tinh",       "rarity":"common",   "w":20},
    {"name":"Pháo Hôi",                "rarity":"common",   "w":15, "def":1.10, "hp":1.10, "luck":-20},
    {"name":"Người Qua Đường Giáp",    "rarity":"common",   "w":15, "def":1.10, "hp":1.10, "luck":-20},
    {"name":"Nhân Vật Phụ",            "rarity":"common",   "w":12, "def":1.10, "hp":1.10, "luck":-20},
    # Hạ Phẩm
    {"name":"Đào Hoa Kiếp",            "rarity":"uncommon", "w":10, "hp":1.50,  "luck":-50},
    {"name":"Thiên Mệnh Chi Tử",       "rarity":"uncommon", "w":8,  "exp_rate":1.10, "luck":30},
    {"name":"Kim Lan Kết Nghĩa",       "rarity":"uncommon", "w":8,  "hp":1.20, "def":1.15},
    # Trung Phẩm
    {"name":"Kẻ Phản Diện Bức Cách",   "rarity":"rare",     "w":6,  "atk":1.50, "crit":15, "lifesteal":5},
    {"name":"Nghịch Thiên Cải Mệnh",   "rarity":"epic",     "w":4,  "atk":1.30, "crit":10, "exp_rate":1.05},
    # Thượng Phẩm
    {"name":"Thiên Kiêu Chi Mệnh",     "rarity":"legendary","w":3,  "atk":1.40, "def":1.30, "hp":1.40},
    {"name":"Vạn Cổ Độc Tôn",          "rarity":"legendary","w":2,  "atk":1.60, "crit":20, "luck":50},
    # Thánh Phẩm
    {"name":"Hồng Hoang Thủy Tổ",      "rarity":"divine",   "w":1,  "atk":1.80, "hp":1.80, "def":1.50, "luck":100},
]

def gacha(pool: list) -> dict:
    total = sum(e["w"] for e in pool)
    r = random.uniform(0, total)
    acc = 0
    for e in pool:
        acc += e["w"]
        if r <= acc: return e
    return pool[-1]

# ══ CÔNG THỨC SỨC MẠNH VŨ KHÍ THEO GIÁ ══════════════════════════
# Giá vũ khí càng cao → % quy đổi sang chỉ số càng lớn (không chỉ tăng tuyến
# tính theo giá, mà % quy đổi CHÍNH NÓ cũng tăng theo từng cấp) → vũ khí đắt
# mạnh hơn RẤT NHIỀU so với vũ khí rẻ, đồng thời mở khóa thêm chỉ số phụ
# (Crit / Tốc Độ / Phòng Thủ / Hút Máu / Phá Giáp) ở các cấp cao hơn.
#   (giá_tối_thiểu, tên_cấp, emoji, %ATK, %Crit, %SPD~ATK, %DEF~ATK, %HútMáu, %PháGiáp)
WEAPON_TIERS = [
    (0,              "Phổ Thông",     "⚪", 0.50, 0.01, 0.00, 0.00, 0.00, 0.00),
    (1_000,          "Tinh Anh",      "🟢", 0.70, 0.03, 0.05, 0.00, 0.00, 0.00),
    (10_000,         "Hi Hữu",        "🔵", 1.00, 0.08, 0.08, 0.05, 0.00, 0.00),
    (100_000,        "Sử Thi",        "🟣", 1.50, 0.15, 0.10, 0.10, 0.03, 0.00),
    (1_000_000,      "Truyền Thuyết", "🟠", 3.00, 0.25, 0.12, 0.15, 0.08, 0.00),
    (100_000_000,    "Thần Thoại",    "🔴", 8.00, 0.40, 0.15, 0.20, 0.15, 0.20),
    (10_000_000_000, "Tối Thượng",    "🌟", 20.0, 0.60, 0.20, 0.25, 0.25, 0.40),
]

def get_weapon_tier(price: float) -> tuple:
    """Trả về tier (giá_tối_thiểu, tên, emoji, %atk, %crit, %spd, %def, %hutmau, %phagiap) theo giá."""
    tier = WEAPON_TIERS[0]
    for t in WEAPON_TIERS:
        if price >= t[0]:
            tier = t
        else:
            break
    return tier

def gen_weapon_stats(price: float) -> dict:
    """Sinh chỉ số vũ khí tự động theo % của giá — vũ khí đắt hơn LUÔN mạnh hơn
    và có nhiều chỉ số được buff hơn vũ khí rẻ."""
    _, tier_name, emoji, atk_mult, crit, spd_pct, def_pct, ls_pct, idef_pct = get_weapon_tier(price)
    atk = max(1, round(price * atk_mult))
    stats = {"slot": "weapon", "base_atk": atk, "atk": atk, "crit_bonus": crit, "tier": tier_name, "tier_emoji": emoji}
    if spd_pct  > 0: stats["spd"]         = round(atk * spd_pct)
    if def_pct  > 0: stats["def_"]        = round(atk * def_pct)
    if ls_pct   > 0: stats["life_steal"]  = ls_pct
    if idef_pct > 0: stats["ignore_def"]  = idef_pct
    return stats

def gen_weapon_stats_eq(price: float) -> dict:
    """Như gen_weapon_stats(), nhưng thêm base_atk để tương thích hệ thống
    trang bị (,tl mac / ,tl cuonghoa) vốn đọc base_atk."""
    s = gen_weapon_stats(price)
    s["base_atk"] = s["atk"]
    return s

# ══ VẬT PHẨM ════════════════════════════════════════════════
ITEMS = {
    # ══ ĐAN DƯỢC ════════════════════════════════════════════════
    # --- Trang 1 (ID 1-23) ---
    "1":    {"name":"Huyết Khí Đan",      "type":"dan_duoc","price":30,        "shop_id":1,  "desc":"Hồi phục toàn bộ HP và chữa trị thương thế ngay lập tức.", "hp_restore_pct":1.0},
    "2":      {"name":"Tụ Linh Đan",         "type":"dan_duoc","price":70,        "shop_id":2,  "desc":"Tăng 20% EXP cho lần tu luyện/bí cảnh tới.", "exp_rate_bonus":0.20,"duration":0,"next_session":True},
    "3":       {"name":"Hộ Tâm Đan",          "type":"dan_duoc","price":120,       "shop_id":3,  "desc":"Giảm 50% thời gian bị thương nếu tẩu hỏa.", "tau_hoa_reduce":0.50,"duration":86400},
    "4":      {"name":"Đột Phá Đan",         "type":"dan_duoc","price":2500,      "shop_id":4,  "desc":"Tăng 10% tỷ lệ đột phá thành công.", "breakthrough":0.10},
    "5":      {"name":"Hồi Thể Đan",         "type":"dan_duoc","price":100,       "shop_id":5,  "desc":"Hồi phục 100 điểm thể lực.", "stamina":100},
    "6":      {"name":"Tẩy Tủy Đan",         "type":"dan_duoc","price":5_000_000, "shop_id":6,  "desc":"Random lại chỉ số vĩnh viễn (Căn Cốt, Thể Chất, Vận Mệnh).", "reroll":True},
    "7":    {"name":"Thông Tuệ Đan",        "type":"dan_duoc","price":150,       "shop_id":7,  "desc":"Tăng 5-10 điểm Ngộ Tính vĩnh viễn (trong ngày).", "ngo_tinh_bonus":[5,10]},
    "8":    {"name":"Hồng Phúc Đan",        "type":"dan_duoc","price":25000,     "shop_id":8,  "desc":"Tăng mạnh Phúc Duyên (+200) trong 60 phút.", "luck_bonus":200,"duration":3600},
    "9":     {"name":"Bổ Thiên Đan",         "type":"dan_duoc","price":200,       "shop_id":9,  "desc":"Tăng giới hạn tu luyện thêm 60 phút (trong ngày).", "cultivate_time_bonus":3600},
    "10":      {"name":"Quỷ Hồn Đan",          "type":"dan_duoc","price":15000,     "shop_id":10, "desc":"Uẩn dưỡng linh hồn cực mạnh. Nhận ngay 10.000 EXP (Quỷ Tu nhận 20.000).", "exp":10000,"dao_bonus":{"nhapquy":20000}},
    "11":    {"name":"Yêu Huyết Đan",        "type":"dan_duoc","price":250,       "shop_id":11, "desc":"Hồi 100% HP và tăng 10% HP Max trong ngày (Yêu Tu tăng 20% HP Max).", "hp_restore_pct":1.0,"hp_max_bonus_pct":0.10,"dao_bonus":{"nhapyeu":0.20}},
    "12":    {"name":"Huyết Sát Đan",        "type":"dan_duoc","price":300,       "shop_id":20, "desc":"Ma: +30% Tốc độ. Chính: +30% Tốc độ, Trừ 50% HP hiện tại.", "spd_bonus_pct":0.30,"dao_penalty":{"nhapdao":"hp50pct"}},
    "13":       {"name":"Âm Hồn Đan",           "type":"dan_duoc","price":3000,      "shop_id":21, "desc":"Ma: +5000 EXP. Chính: +2000 EXP, +50% Rủi ro.", "exp":2000,"dao_bonus":{"nhapma":5000}},
    "14": {"name":"Nghịch Thiên Đan",     "type":"dan_duoc","price":1000,      "shop_id":22, "desc":"Ma: Full HP & Thể Lực. Chính: Full HP, Trừ 5 Phúc Duyên.", "hp_restore_pct":1.0},
    "15":    {"name":"Thanh Tâm Đan",        "type":"dan_duoc","price":300,       "shop_id":23, "desc":"Chính: Giảm 50% Rủi ro. Ma: Giảm 30% EXP tu luyện.", "risk_reduce":0.50},
    # --- Trang 2 (ID 24-39) ---
    "16":    {"name":"Sinh Mệnh Đan",        "type":"dan_duoc","price":800,       "shop_id":24, "desc":"Chính: Hồi 100% HP & Thể Lực. Ma: Mất 90% HP.", "hp_restore_pct":1.0,"stamina":200},
    "17":       {"name":"Ma Khí Tán",           "type":"dan_duoc","price":750,       "shop_id":25, "desc":"Sơ cấp Ma Đạo. Ma: +500 EXP, +5% Risk. Chính: +100 EXP, +10% Risk.", "exp":100,"dao_bonus":{"nhapma":500}},
    "18":     {"name":"Tĩnh Tâm Trà",         "type":"dan_duoc","price":50,        "shop_id":26, "desc":"Sơ cấp Chính Đạo. Chính: -10% Rủi ro. Ma: -5% Rủi ro, -500 EXP.", "risk_reduce":0.10},
    "19":      {"name":"Hộ Mệnh Đan",          "type":"dan_duoc","price":150,       "shop_id":27, "desc":"Giảm 30% sát thương nhận trong lần thám hiểm bí cảnh tiếp theo.", "dmg_reduce_next":0.30},
    "20":    {"name":"Thám Hiểm Đan",        "type":"dan_duoc","price":200,       "shop_id":28, "desc":"Tăng 25% EXP nhận được từ bí cảnh lần tới.", "exp_rate_bonus":0.25,"next_session":True},
    "21":      {"name":"Tầm Bảo Đan",          "type":"dan_duoc","price":250,       "shop_id":29, "desc":"Tăng 20% tỷ lệ rơi vật phẩm quý trong lần thám hiểm tới.", "drop_rate_bonus":0.20},
    "bua_chuc_phuc": {"name":"Bùa Chúc Phúc", "type":"dan_duoc", "price":50000, "shop_id":"bua_chuc_phuc", "desc":"Dùng khi cường hóa: +15% tỷ lệ thành công và chống hạ cấp khi thất bại.", "enhance_boost":0.15, "enhance_no_downgrade":True},
    "22":     {"name":"Bùa Tốc Hành",         "type":"dan_duoc","price":100,       "shop_id":30, "desc":"Tạm thời +20% SPD trong 30 phút.", "spd_bonus_pct":0.20,"duration":1800},
    "23":      {"name":"Bùa Hộ Mạng",          "type":"dan_duoc","price":150,       "shop_id":31, "desc":"Tạm thời +30% HP trong 60 phút.", "hp_bonus_pct":0.30,"duration":3600},
    "24":     {"name":"Bùa Thần Lực",         "type":"dan_duoc","price":200,       "shop_id":32, "desc":"Tạm thời +25% ATK trong 60 phút.", "atk_bonus_pct":0.25,"duration":3600},
    "25":       {"name":"Thẻ Tốc Độ",           "type":"dan_duoc","price":500,       "shop_id":33, "desc":"Tăng 100% (x2) EXP tu luyện trong 24 giờ.", "exp_rate_bonus":1.0,"duration":86400},
    "26":     {"name":"Thất Sát Phù",         "type":"dan_duoc","price":500000,    "shop_id":35, "desc":"Phù chú cổ đại làm suy yếu ma tính của Boss Tháp. Giảm 50% sức mạnh Scaling của Boss trong 60 phút.", "boss_scale_reduce":0.50,"duration":3600},
    "27":{"name":"Thiên Thiên Bảo Hộ", "type":"dan_duoc","price":900000,    "shop_id":36, "desc":"Hào quang bảo vệ tâm mạch. Giới hạn sát thương nhận vào tối đa 15% HP bản thân mỗi đòn trong Tháp (60 phút).", "dmg_cap_pct":0.15,"duration":3600},
    "28":    {"name":"Thần Hành Đan",        "type":"dan_duoc","price":15000,     "shop_id":37, "desc":"Tăng x2 tốc độ thám hiểm Bí Cảnh.", "explore_speed":2.0,"duration":0},
    "29":    {"name":"Dẫn Hồn Hương",        "type":"dan_duoc","price":20000,     "shop_id":38, "desc":"Thu hút Boss, x2 tỷ lệ sự kiện đặc biệt và tăng 80% cơ hội gặp Boss trong Bí Cảnh.", "boss_attract":True,"duration":0},
    "30":   {"name":"Hàu Sữa Đại Bổ",      "type":"dan_duoc","price":1500,      "shop_id":39, "desc":"Vật phẩm đại bổ. Hồi phục 500 Thể Lực (Dành riêng cho Lọ Đạo).", "stamina":500,"dao_restrict":"nhaplo"},
    # --- Trang 3 (ID 43-70) ---
    "31":      {"name":"Đơn Tâm Đan",          "type":"dan_duoc","price":1_500_000, "shop_id":43, "desc":"Phá bỏ giới hạn và gây sát thương tối thiểu (1.5% HP Boss) mỗi hiệp trong Tháp Ma Tôn (30 phút).", "min_dmg_pct":0.015,"duration":1800},
    "32":    {"name":"Cuồng Bạo Đan",        "type":"dan_duoc","price":500,       "shop_id":50, "desc":"Tăng 20% ATK, giảm 10% DEF trong 30 phút.", "atk_bonus_pct":0.20,"def_penalty_pct":0.10,"duration":1800},
    "33":    {"name":"Kim Chung Đan",         "type":"dan_duoc","price":500,       "shop_id":51, "desc":"Tăng 20% DEF, giảm 10% SPD trong 30 phút.", "def_bonus_pct":0.20,"spd_penalty_pct":0.10,"duration":1800},
    "34":    {"name":"Tật Phong Đan",         "type":"dan_duoc","price":500,       "shop_id":52, "desc":"Tăng 20% SPD trong 30 phút.", "spd_bonus_pct":0.20,"duration":1800},
    "35":     {"name":"Thần Tài Đan",          "type":"dan_duoc","price":2000,      "shop_id":60, "desc":"Tăng 10% tiền thắng cược trong 5 ván tiếp theo.", "gamble_bonus":0.10,"next_rounds":5},
    "36":      {"name":"Tán Tài Đan",           "type":"dan_duoc","price":1000,      "shop_id":61, "desc":"Hoàn trả 10% tiền thua cược trong 5 ván tiếp theo.", "gamble_refund":0.10,"next_rounds":5},
    "37":      {"name":"Tẩy Tâm Đan",           "type":"dan_duoc","price":5000,      "shop_id":70, "desc":"Xóa 1 điểm PK (Giảm nghiệp chướng).", "pk_reduce":1},
    # --- Legacy / Compat ---
    "202":    {"name":"Luyện Khí Đan",        "type":"dan_duoc","price":500,       "desc":"Đan dược hỗ trợ tu luyện.", "exp":1000},
    "501":      {"name":"Trúc Cơ Đan",          "type":"dan_duoc","price":5000,      "desc":"Đan dược đột phá Trúc Cơ.", "exp":10000},
    "502":      {"name":"Tích Tụ Đan",          "type":"dan_duoc","price":2000,      "desc":"Tăng 50% tốc độ EXP trong 1 giờ.", "exp_rate_bonus":0.5,"duration":3600},
    "201":    {"name":"Phục Tinh Đan",        "type":"dan_duoc","price":3000,      "desc":"Hồi 50 thể lực.", "stamina":50},
    "204":     {"name":"Đại Hoàn Đan",         "type":"dan_duoc","price":8000,      "desc":"Hồi 200 thể lực.", "stamina":200},
    "503":  {"name":"Trường Sinh Đan",      "type":"dan_duoc","price":100000,    "desc":"Đan dược trường sinh.", "exp":5000000},
    "504":     {"name":"Thần Hóa Đan",         "type":"dan_duoc","price":500000,    "desc":"Đan dược thần hóa.", "exp":50000000},
    # Vũ Khí
    "1":    {"name":"Sát Tiên Kiếm",      "type":"vukhi",  "slot":"weapon",  "price":10000,  **gen_weapon_stats_eq(10000)},
    "2":   {"name":"Thần Long Kiếm",     "type":"vukhi",  "slot":"weapon",  "price":80000,  **gen_weapon_stats_eq(80000)},
    "3":   {"name":"Khai Thiên Phủ",     "type":"vukhi",  "slot":"weapon",  "price":500000, **gen_weapon_stats_eq(500000)},
    # Giáp
    "601":         {"name":"U Minh Luân Hồi Y",  "type":"giap",   "slot":"armor",   "price":80000,  "base_def":2000},
    "606":  {"name":"Tiên Hoàng Giáp",    "type":"giap",   "slot":"armor",   "price":400000, "base_def":6000},
    # Mũ/Phụ kiện
    "602":          {"name":"Thần Mão Trấn Thế",  "type":"mu",     "slot":"hat",     "price":50000,  "base_def":800},
    "603":    {"name":"Tinh Hồn Lệnh",      "type":"vongco", "slot":"necklace","price":60000,  "base_atk":600,"base_def":400},
    "604":     {"name":"Diệt Thế Bá Thủ",    "type":"gangtay","slot":"gloves",  "price":70000,  "base_atk":700},
    "605":      {"name":"Hư Không Bộ",        "type":"giay",   "slot":"boots",   "price":70000,  "base_spd":500},
    # Pháp Bảo
    "607":        {"name":"Bàn Cổ Thần Ấn",     "type":"phap_bao","slot":"phapbao","price":600000, "base_atk":5000,"base_def":2000},
    # ══ PHÁP BẢO CÁC (Cấp cao — mua bằng Linh Thạch) ══
    "legendary_1": {
        "name": "Thiên Tôn Ấn", "type": "phap_bao", "slot": "phapbao",
        "price": 10_000_000, "shop_id": "legendary_1",
        "atk": 100_000, "base_atk": 100_000,
        "def_": 50_000,  "base_def": 50_000,
        "hp":  1_000_000,"base_hp": 1_000_000,
        "tier": "Tầng 100", "tier_emoji": "🏆",
        "desc": "Ấn triện của Thiên Tôn. Chỉ dành cho đại gia siêu cấp!",
    },
    "pb_pangu_seal": {
        "name": "Bàn Cổ Thần Ấn", "type": "phap_bao", "slot": "phapbao",
        "price": 25_000_000_000, "shop_id": "pb_pangu_seal",
        "atk": 2_000_000_000_000_000_0, "base_atk": 2_000_000_000_000_000_0,
        "def_": 8_000_000_000_000_000,  "base_def": 8_000_000_000_000_000,
        "hp":  2_000_000_000_000_000_000,"base_hp": 2_000_000_000_000_000_000,
        "boss_scale_immune": True,
        "desc": "Thần ấn của Bàn Cổ, trấn áp chư thiên. Kháng 100% Boss Scaling. (TỐI THƯỢNG)",
    },
    "pb_taiji_chart": {
        "name": "Thái Cực Đồ", "type": "phap_bao", "slot": "phapbao",
        "price": 15_000_000_000, "shop_id": "pb_taiji_chart",
        "def_": 5_000_000_000_000_000, "base_def": 5_000_000_000_000_000,
        "desc": "Bản đồ thái cực, chuyển hóa âm dương. (PHÒNG NGỰ)",
    },
    "pb_donghuang_bell": {
        "name": "Đông Hoàng Chuông", "type": "phap_bao", "slot": "phapbao",
        "price": 15_000_000_000, "shop_id": "pb_donghuang_bell",
        "hp":  500_000_000_000_000_000, "base_hp": 500_000_000_000_000_000,
        "luck_pct": 0.20,
        "desc": "Tiếng chuông vang vọng khắp thái cổ. (KHÍ VẬN)",
    },
    "pb_kyu_cauldron": {
        "name": "Cửu Châu Đỉnh", "type": "phap_bao", "slot": "phapbao",
        "price": 12_000_000_000, "shop_id": "pb_kyu_cauldron",
        "atk": 100_000_000_000_000, "base_atk": 100_000_000_000_000,
        "def_": 50_000_000_000_000,  "base_def": 50_000_000_000_000,
        "hp":  1_000_000_000_000_000, "base_hp": 1_000_000_000_000_000,
        "exp_pct": 1.00,
        "desc": "Đỉnh luyện hóa cả cửu châu. (TU VI)",
    },
    # Ngọc
    "401":        {"name":"Hồng Ngọc",          "type":"ngoc",   "price":5000,    "atk_pct":0.05},
    "402":         {"name":"Lam Ngọc",           "type":"ngoc",   "price":5000,    "def_pct":0.05},
    "403":         {"name":"Lục Ngọc",           "type":"ngoc",   "price":5000,    "hp_pct":0.05},
    "404":       {"name":"Hoàng Ngọc",         "type":"ngoc",   "price":8000,    "spd_pct":0.05},
    "405":        {"name":"Thần Ngọc",          "type":"ngoc",   "price":50000,   "atk_pct":0.15,"def_pct":0.10},
    # Nguyên Liệu Luyện Đan
    "301":        {"name":"Linh Thảo",          "type":"nguyen_lieu","price":200,  "tier":1},
    "302":         {"name":"Hỏa Tinh Thảo",      "type":"nguyen_lieu","price":800,  "tier":2},
    "303":       {"name":"Thiên Nhẫn Hoa",     "type":"nguyen_lieu","price":3000, "tier":3},
    "304":   {"name":"Long Khí Tượng",     "type":"nguyen_lieu","price":15000,"tier":4},
    "305":     {"name":"Hỗn Độn Tinh Thạch", "type":"nguyen_lieu","price":100000,"tier":5},
    # Rương
    "105":    {"name":"Rương Tân Thủ",      "type":"ruong",  "price":0,       "loot":"tan_thu"},
    "101":        {"name":"Rương Bạc",          "type":"ruong",  "price":5000,    "loot":"bac"},
    "102":       {"name":"Rương Vàng",         "type":"ruong",  "price":20000,   "loot":"vang"},
    "103":  {"name":"Rương Kim Cương",    "type":"ruong",  "price":100000,  "loot":"kim_cuong"},
    "104":       {"name":"Rương Thần",         "type":"ruong",  "price":500000,  "loot":"than"},
    # ── Linh Thú v2 Items ──────────────────────────────────────
    "701":  {"name":"Trứng Thần Long",    "type":"linhthu_egg","price":200000,"thu_type":"than_long"},
    "702":  {"name":"Trứng Phượng Hoàng","type":"linhthu_egg","price":150000,"thu_type":"phuong_hoang"},
    "703":  {"name":"Trứng Thần Quy",    "type":"linhthu_egg","price":100000,"thu_type":"than_quy"},
    "704":  {"name":"Trứng Kỳ Lân",      "type":"linhthu_egg","price":500000,"thu_type":"ky_lan"},
    # Pet consumables
    "thu_quyet":       {"name":"📜 Thú Quyết",      "type":"pet_item","price":5000,   "desc":"Dùng để săn Linh Thú"},
    "linh_thuc":       {"name":"🍖 Linh Thức",       "type":"pet_item","price":1000,   "desc":"Thức ăn cho thú, +50 EXP"},
    "than_thuc":       {"name":"🍗 Thần Thức",        "type":"pet_item","price":5000,   "desc":"Thức ăn cao cấp, +300 EXP"},
    "hoa_hinh_dan":    {"name":"💊 Hóa Hình Đan",    "type":"pet_item","price":50000,  "desc":"Tiến hóa thú lên dạng cao hơn"},
    "huyet_mach_dan":  {"name":"💉 Huyết Mạch Đan",  "type":"pet_item","price":80000,  "desc":"Tẩy luyện huyết mạch thú"},
    "thu_ngu_chu":     {"name":"🔮 Thú Ngũ Châu",    "type":"pet_item","price":30000,  "desc":"Thức tỉnh Thần Thú"},
    "truoc_trung_dan": {"name":"🥚 Trứng Tước Trùng","type":"linhthu_egg","price":20000,"thu_type":None},
    # Linh thạch đặc biệt
    "801":   {"name":"Linh Thạch Bảo Phong","type":"special","price":0,"trung":10},
    # ══ VŨ KHÍ (chỉ số TỰ SINH theo % giá — giá cao hơn = mạnh hơn & buff nhiều chỉ số hơn) ══
    "w1":  {"name":"Thiết Kiếm",          "type":"vukhi","price":100,        "shop_id":"w1",
            **gen_weapon_stats(100),
            "desc":"Kiếm sắt thường, trang bị cơ bản cho người mới nhập môn."},
    "w2":  {"name":"Thanh Phong Kiếm",    "type":"vukhi","price":500,        "shop_id":"w2",
            **gen_weapon_stats(500),
            "desc":"Kiếm nhẹ tựa gió, tăng tốc độ ra đòn."},
    "w3":  {"name":"Huyết Đao",           "type":"vukhi","price":1500,       "shop_id":"w3",
            **gen_weapon_stats(1500),
            "desc":"Đao tà khí, sắc bén dị thường, khát máu vô tận."},
    "w4":  {"name":"Lôi Thần Búa",        "type":"vukhi","price":5000,       "shop_id":"w4",
            **gen_weapon_stats(5000),
            "desc":"Búa thần chứa sấm sét, sức công phá hủy diệt."},
    "w5":  {"name":"Hỏa Long Kiếm",       "type":"vukhi","price":10000,      "shop_id":"w5",
            **gen_weapon_stats(10000),
            "desc":"Kiếm rèn từ vảy rồng lửa, thiêu đốt mọi kẻ thù."},
    "w6":  {"name":"Băng Phách Thần Châm","type":"vukhi","price":20000,      "shop_id":"w6",
            **gen_weapon_stats(20000),
            "desc":"Châm lạnh thấu xương, tấn công điểm yếu."},
    "w7":  {"name":"Hiên Viên Kiếm",      "type":"vukhi","price":50000,      "shop_id":"w7",
            **gen_weapon_stats(50000),
            "desc":"Thánh kiếm của hoàng đế, mang lại may mắn và sức mạnh."},
    "w8":  {"name":"Tru Tiên Kiếm",       "type":"vukhi","price":150000,     "shop_id":"w8",
            **gen_weapon_stats(150000),
            "desc":"Kiếm tiên giới rơi xuống phàm trần. Sát thần diệt phật! (VIP)"},
    "w9":  {"name":"Vạn Hồn Phiên",       "type":"vukhi","price":30000,      "shop_id":"w9",
            **gen_weapon_stats(30000),
            "desc":"Phiên vũ khí tụ hồn, hút máu kẻ địch để tự hồi phục."},
    "w10": {"name":"Tháp Thần Kiếm",      "type":"vukhi","price":200000,     "shop_id":"w10",
            **gen_weapon_stats(200000),
            "desc":"🗼 Tầng 10: Kiếm thần từ tháp. Có tiền là mua được!"},
    "w11": {"name":"Thiên Long Thương",   "type":"vukhi","price":500000,     "shop_id":"w11",
            **gen_weapon_stats(500000),
            "desc":"🗼 Tầng 40: Thương rồng trời. Giá chát nhưng chất."},
    "w12": {"name":"Hồng Hoang Búa",      "type":"vukhi","price":2000000,    "shop_id":"w12",
            **gen_weapon_stats(2000000),
            "desc":"🗼 Tầng 70: Búa thái cổ. Đã bị phong ấn một phần sức mạnh."},
    "w_ice_1":     {"name":"Băng Vũ Kiếm",         "type":"vukhi","price":250,        "shop_id":"w_ice_1",
            **gen_weapon_stats(250),
            "desc":"Kiếm băng phách sơ cấp, chém ra hơi lạnh."},
    "w_thunder_1": {"name":"Lôi Đình Trượng",      "type":"vukhi","price":6000,       "shop_id":"w_thunder_1",
            **gen_weapon_stats(6000),
            "desc":"Trượng chứa sấm sét, tê liệt kẻ thù."},
    "w_mid_1":     {"name":"Thất Tinh Kiếm",       "type":"vukhi","price":90000,      "shop_id":"w_mid_1",
            **gen_weapon_stats(90000),
            "desc":"Kiếm khắc bảy ngôi sao, dẫn động tinh lực."},
    "w_mid_2":     {"name":"Phá Thiên Kích",       "type":"vukhi","price":200000,     "shop_id":"w_mid_2",
            **gen_weapon_stats(200000),
            "desc":"Kích phá vỡ bầu trời, sức mạnh kinh hoàng."},
    "w_mid_3":     {"name":"Cửu Kiếp Kiếm",        "type":"vukhi","price":350000,     "shop_id":"w_mid_3",
            **gen_weapon_stats(350000),
            "desc":"Kiếm qua chín kiếp luân hồi, sát khí ngút trời."},
    "w_nho_1":     {"name":"Thiên Quan Bút",       "type":"vukhi","price":8000,       "shop_id":"w_nho_1",
            **gen_weapon_stats(8000),
            "desc":"Bút lông ngự ban, nét chữ chứa hạo nhiên khí."},
    "w_nho_2":     {"name":"Xuân Thu Bút",         "type":"vukhi","price":100000,     "shop_id":"w_nho_2",
            **gen_weapon_stats(100000),
            "desc":"Bút viết nên lịch sử, trấn áp tà ma."},
    "w_lo_1":      {"name":"Giấy Vệ Sinh Bạch Kim","type":"vukhi","price":40000,      "shop_id":"w_lo_1",
            **gen_weapon_stats(40000),
            "desc":"Lau dọn mọi vết tích, tốc độ vung vẩy cực nhanh."},
    "w_lo_2":      {"name":"Chuột Gaming RGB",     "type":"vukhi","price":350000,     "shop_id":"w_lo_2",
            **gen_weapon_stats(350000),
            "desc":"Click liên hoàn! Tốc độ bàn thờ, phản xạ vô địch."},
    "w_vip_2":     {"name":"Hiên Viên Kiếm (VIP)", "type":"vukhi","price":550000,     "shop_id":"w_vip_2",
            **gen_weapon_stats(550000),
            "desc":"Thánh kiếm của Hoàng Đế. Thống nhất tam giới! (SUPER VIP)"},
    "w_god_1":     {"name":"Thần Ma Diệt Thế Kiếm","type":"vukhi","price":100000000,  "shop_id":"w_god_1",
            **gen_weapon_stats(100000000),
            "desc":"Kiếm diệt thế, chém đứt luân hồi. (GOD TIER)"},
    "w_god_2":     {"name":"Táng Thiên Kiếm",      "type":"vukhi","price":500000000,  "shop_id":"w_god_2",
            **gen_weapon_stats(500000000),
            "desc":"Kiếm chôn vùi cả bầu trời. (GOD TIER)"},
    "w_divine_1":  {"name":"Vô Thượng Kiếm",       "type":"vukhi","price":6000000000, "shop_id":"w_divine_1",
            **gen_weapon_stats(6000000000),
            "desc":"Thanh kiếm của thần linh. (THẦN CẤP)"},
    "w_supreme_1": {"name":"Khai Thiên Phủ",       "type":"vukhi","price":10000000000,"shop_id":"w_supreme_1",
            **gen_weapon_stats(10000000000),
            "desc":"Sức mạnh khai thiên tích địa, tối thượng vô song. (CHÍ TÔN)"},

    # ══ TÀNG KINH CÁC — Bí Kíp & Công Pháp ════════════════════════════════
    # ID hiển thị (shop_id) khớp với số trong yêu cầu, key = "bk<id>"
    "bk34":  {"name":"Bí Kíp: Cửu Chuyển Hồi Thể",    "type":"bi_kip","price":10_000,
              "shop_id":34,  "desc":"Bí kíp rèn luyện thể chất, tăng thẳng 500 điểm giới hạn Stamina (Max).",
              "stamina_max_flat":500},
    "bk201": {"name":"Bí Kíp: Trường Xuân Công",        "type":"bi_kip","price":400,
              "shop_id":201, "desc":"Công pháp tăng cường sinh mệnh, tăng 30 phút tu luyện mỗi ngày.",
              "cultivate_time_bonus":1800},
    "bk202": {"name":"Bí Kíp: Tụ Linh Quyết",          "type":"bi_kip","price":800,
              "shop_id":202, "desc":"Công pháp hấp thu linh khí, tăng 10% tốc độ tu luyện.",
              "passive_exp_rate":0.10},
    "bk203": {"name":"Bí Kíp: Kim Cương Bất Hoại",      "type":"bi_kip","price":800,
              "shop_id":203, "desc":"Công pháp luyện thể, giảm 20% tỷ lệ bị thương.",
              "passive_dmg_reduce":0.20},
    "bk204": {"name":"Bí Kíp: Thiên Diễn Thần Toán",   "type":"bi_kip","price":1_000,
              "shop_id":204, "desc":"Công pháp rèn luyện trí tuệ, tăng 10 điểm Ngộ Tính vĩnh viễn.",
              "ngo_tinh_flat":10},
    "bk205": {"name":"Bí Kíp: Huyết Tế Đại Pháp",      "type":"bi_kip","price":2_000,
              "shop_id":205, "desc":"Ma: +15% Tốc độ, +10% HP. Chính: +10% Tốc độ, -10% HP (Passive).",
              "passive_dao":{"nhapma":{"spd":0.15,"hp":0.10},"nhapdao":{"spd":0.10,"hp":-0.10}}},
    "bk206": {"name":"Bí Kíp: Thôn Thiên Ma Công",      "type":"bi_kip","price":5_000,
              "shop_id":206, "desc":"Ma: +30% Tỷ lệ rơi đồ Bí Cảnh. Chính: -20 Phúc Duyên (Passive).",
              "passive_dao":{"nhapma":{"drop_rate":0.30},"nhapdao":{"luck":-20}}},
    "bk207": {"name":"Bí Kíp: Hạo Nhiên Chính Khí",    "type":"bi_kip","price":2_000,
              "shop_id":207, "desc":"Chính: Giảm Rủi ro, Tăng Def. Ma: Tăng Rủi ro, Giảm Def (Passive).",
              "passive_dao":{"nhapdao":{"risk_reduce":0.15,"def":0.10},"nhapma":{"risk_add":0.15,"def":-0.10}}},
    "bk208": {"name":"Bí Kíp: Từ Bi Chú",               "type":"bi_kip","price":4_000,
              "shop_id":208, "desc":"Chính: Tăng Phúc Duyên. Ma: Giảm Phúc Duyên (Passive).",
              "passive_dao":{"nhapdao":{"luck":20},"nhapma":{"luck":-20}}},
    "bk209": {"name":"Bí Kíp: Du Hiệp Tâm Pháp",       "type":"bi_kip","price":1_500,
              "shop_id":209, "desc":"Giảm 20% sát thương khi thám hiểm (Passive).",
              "passive_dmg_reduce":0.20},
    "bk210": {"name":"Bí Kíp: Cửu U Minh Khúc",        "type":"bi_kip","price":5_000_000,
              "shop_id":210, "desc":"Quỷ Đạo: +20% Tốc độ. Đạo khác: +10% Tốc độ, tăng 10% rủi ro.",
              "passive_dao":{"nhapquy":{"spd":0.20},"_other":{"spd":0.10,"risk_add":0.10}}},
    "bk211": {"name":"Bí Kíp: Vô Ảnh Quỷ Bộ",          "type":"bi_kip","price":10_000_000,
              "shop_id":211, "desc":"Quỷ Đạo: Tăng 20% tỉ lệ Bạo kích. Đạo khác: Tăng 5% Bạo kích.",
              "passive_dao":{"nhapquy":{"crit":0.20},"_other":{"crit":0.05}}},
    "bk212": {"name":"Bí Kíp: Vạn Thú Quyết",          "type":"bi_kip","price":5_000_000,
              "shop_id":212, "desc":"Yêu Đạo: +20% HP, +10% Thủ. Đạo khác: +5% HP.",
              "passive_dao":{"nhapyeu":{"hp":0.20,"def":0.10},"_other":{"hp":0.05}}},
    "bk213": {"name":"Bí Kíp: Huyết Mạch Thừa Kế",     "type":"bi_kip","price":10_000_000,
              "shop_id":213, "desc":"Yêu Đạo: +20% Thủ, giảm 10% rủi ro. Đạo khác: +5% Thủ.",
              "passive_dao":{"nhapyeu":{"def":0.20,"risk_reduce":0.10},"_other":{"def":0.05}}},
    "bk214": {"name":"Bí Kíp: Thiên Địa Hồng Lô Thể",  "type":"bi_kip","price":25_000_000_000,
              "shop_id":214, "desc":"+2.000 Thể Lực max. Yêu cầu học bk213 trước.",
              "stamina_max_flat":2000, "requires":"bk213"},
    "bk215": {"name":"Bí Kíp: Hỗn Độn Bất Diệt Thể",   "type":"bi_kip","price":100_000_000_000,
              "shop_id":215, "desc":"+5.000 Thể Lực max. Yêu cầu học bk214 trước. Đỉnh cao!",
              "stamina_max_flat":5000, "requires":"bk214"},
    "bk216": {"name":"Bí Kíp: Hạo Nhiên Kinh",          "type":"bi_kip","price":5_000,
              "shop_id":216, "desc":"Nho Đạo: +15% Thủ, +10% Máu. Đạo khác: -5% Thủ (Passive).",
              "passive_dao":{"nhapnho":{"def":0.15,"hp":0.10},"_other":{"def":-0.05}}},
    "bk217": {"name":"Bí Kíp: Xuân Thu Đại Pháp",       "type":"bi_kip","price":15_000,
              "shop_id":217, "desc":"Nho Đạo: +10% Phản sát thương, +5% Giảm thương (Passive).",
              "passive_dao":{"nhapnho":{"reflect":0.10,"dmg_reduce":0.05}}},
    "bk218": {"name":"Bí Kíp: Độc Thủ Đại Công",        "type":"bi_kip","price":25_000,
              "shop_id":218, "desc":"Lọ Đạo: +50% Tốc độ, +20% Bạo kích, -50% HP. Đạo khác: Tự Hủy (Passive).",
              "passive_dao":{"nhaplo":{"spd":0.50,"crit":0.20,"hp":-0.50},"_other":{"self_destruct":True}}},
    "bk219": {"name":"Bí Kíp: Thánh Tốc Quyết",         "type":"bi_kip","price":120_000,
              "shop_id":219, "desc":"Lọ Đạo: +100% Tốc độ, +50% Bạo kích, -80% HP. Đạo khác: Tự Hủy (Passive).",
              "passive_dao":{"nhaplo":{"spd":1.00,"crit":0.50,"hp":-0.80},"_other":{"self_destruct":True}}},
    "bk220": {"name":"Bí Kíp: Thiên Lôi Kiếm Quyết",       "type":"bi_kip","price":500_000,
              "shop_id":220, "desc":"Tăng 25% Công kích. Mỗi đòn đánh có 10% gây thêm sát thương Lôi (Passive).",
              "passive_dao":{"_all":{"atk":0.25,"lightning_proc":0.10}}},
    "bk221": {"name":"Bí Kíp: Vạn Kiếp Bất Diệt Công",     "type":"bi_kip","price":3_000_000,
              "shop_id":221, "desc":"Khi HP xuống dưới 20%, tự động hồi 15% HP tối đa (CD 60s). (Passive).",
              "passive_dao":{"_all":{"auto_heal_threshold":0.20,"auto_heal_pct":0.15}}},
    "bk222": {"name":"Bí Kíp: Âm Dương Song Tu",            "type":"bi_kip","price":8_000_000,
              "shop_id":222, "desc":"Vừa tăng 15% ATK vừa tăng 15% DEF. Cân bằng tuyệt đối giữa công và thủ (Passive).",
              "passive_dao":{"_all":{"atk":0.15,"def":0.15}}},
    "bk223": {"name":"Bí Kíp: Thái Cực Huyền Công",         "type":"bi_kip","price":20_000_000,
              "shop_id":223, "desc":"Phản 15% sát thương nhận về. Tăng 10% giảm sát thương (Passive).",
              "passive_dao":{"_all":{"reflect":0.15,"dmg_reduce":0.10}}},
    "bk224": {"name":"Bí Kíp: Hỗn Nguyên Nhất Khí",        "type":"bi_kip","price":500_000_000,
              "shop_id":224, "desc":"Tăng 20% tất cả chỉ số chiến đấu (ATK/DEF/HP/SPD). Thiên hạ vô địch (Passive).",
              "requires":"bk222", "passive_dao":{"_all":{"atk":0.20,"def":0.20,"hp":0.20,"spd":0.20}}},
}

LOOT_TABLES = {
    "tan_thu":   [("202",3,0.9),("301",5,0.8),("101",1,0.3)],
    "bac":       [("202",5,0.9),("501",1,0.5),("201",1,0.4),("301",3,0.7)],
    "vang":      [("501",3,0.8),("502",1,0.6),("4",1,0.3),("401",1,0.4)],
    "kim_cuong": [("502",2,0.9),("4",2,0.7),("405",1,0.3),("204",2,0.8)],
    "than":      [("4",5,0.95),("503",1,0.6),("405",2,0.5),("607",1,0.08)],
}

# ══ BÍ CẢNH (KEY CHUẨN) ═════════════════════════════════════
AREAS = [
    # ── Luyện Thể (realm 0) ─────────────────────────────
    {"id":"rung_linh_moc",   "name":"🌲 Rừng Linh Mộc",        "min_realm":0,  "max_realm":2,
     "duration_min":10, "duration_max":30,  "stamina_cost":10,
     "exp_min":100,      "exp_max":500,      "lt_min":50,    "lt_max":200,
     "drop_items":["301","101"], "drop_rate":0.40,
     "desc":"Rừng linh khí dày đặc, phù hợp người mới nhập môn"},
    # ── Tụ Khí (realm 1) ─────────────────────────────────
    {"id":"suoi_linh_tuyen", "name":"💧 Suối Linh Tuyền",       "min_realm":1,  "max_realm":3,
     "duration_min":20, "duration_max":50,  "stamina_cost":15,
     "exp_min":800,      "exp_max":3000,     "lt_min":200,   "lt_max":800,
     "drop_items":["202","301","101"], "drop_rate":0.38,
     "desc":"Tuyền nước Linh Khí, bổ dưỡng tâm mạch"},
    # ── Luyện Khí (realm 2) ──────────────────────────────
    {"id":"dong_thanh_long", "name":"🐉 Động Thanh Long",        "min_realm":2,  "max_realm":5,
     "duration_min":30, "duration_max":80,  "stamina_cost":25,
     "exp_min":4000,     "exp_max":15000,    "lt_min":500,   "lt_max":2000,
     "drop_items":["501","302","102"], "drop_rate":0.33,
     "desc":"Hang Long cổ đại, Long Khí sung mãn"},
    # ── Ngưng Khí (realm 3) ──────────────────────────────
    {"id":"bai_chien_co",    "name":"⚔️ Bãi Chiến Cổ Xưa",      "min_realm":3,  "max_realm":6,
     "duration_min":40, "duration_max":100, "stamina_cost":30,
     "exp_min":15000,    "exp_max":60000,    "lt_min":1000,  "lt_max":5000,
     "drop_items":["3","102","301"], "drop_rate":0.30,
     "desc":"Chiến trường cổ đại, linh khí tàn dư vô cùng phong phú"},
    # ── Trúc Cơ (realm 4) ────────────────────────────────
    {"id":"gio_linh_dong",   "name":"🌀 Giỗ Linh Động",          "min_realm":4,  "max_realm":7,
     "duration_min":50, "duration_max":120, "stamina_cost":35,
     "exp_min":60000,    "exp_max":250000,   "lt_min":3000,  "lt_max":12000,
     "drop_items":["4","302","103"], "drop_rate":0.28,
     "desc":"Hang động linh phong xoáy, tăng tốc đột phá"},
    # ── Tử Phủ (realm 5) ─────────────────────────────────
    {"id":"thien_ma_vuc",    "name":"😈 Thiên Ma Vực",           "min_realm":5,  "max_realm":9,
     "duration_min":60, "duration_max":150, "stamina_cost":45,
     "exp_min":250000,   "exp_max":1000000,  "lt_min":8000,  "lt_max":30000,
     "drop_items":["505","303","103"], "drop_rate":0.26,
     "desc":"Vực sâu Ma Khí, nguy hiểm - lợi lộc cực lớn"},
    # ── Đạo Cung (realm 6) ───────────────────────────────
    {"id":"tuyet_phong_lam", "name":"❄️ Tuyết Phong Lâm",        "min_realm":6,  "max_realm":10,
     "duration_min":70, "duration_max":180, "stamina_cost":55,
     "exp_min":1000000,  "exp_max":5000000,  "lt_min":20000, "lt_max":80000,
     "drop_items":["4","104","405"], "drop_rate":0.24,
     "desc":"Rừng tuyết phong linh, khí hàn thấu tâm"},
    # ── Kim Đan (realm 7) ────────────────────────────────
    {"id":"ngu_hanh_son",    "name":"🌋 Ngũ Hành Sơn",          "min_realm":7,  "max_realm":11,
     "duration_min":80, "duration_max":200, "stamina_cost":65,
     "exp_min":5000000,  "exp_max":25000000, "lt_min":50000, "lt_max":200000,
     "drop_items":["503","304","104"], "drop_rate":0.22,
     "desc":"Núi chứa ngũ hành linh lực, trợ Kim Đan thành tựu"},
    # ── Nguyên Anh (realm 8) ─────────────────────────────
    {"id":"co_than_mieu",    "name":"⛩️ Cổ Thần Miếu",          "min_realm":8,  "max_realm":13,
     "duration_min":100,"duration_max":240, "stamina_cost":80,
     "exp_min":25000000, "exp_max":120000000,"lt_min":200000,"lt_max":800000,
     "drop_items":["4","403","104"], "drop_rate":0.20,
     "desc":"Miếu Thần Cổ xưa, Nguyên Anh bí tịch vô lượng"},
    # ── Hóa Thần (realm 9) ───────────────────────────────
    {"id":"huyen_thien_vuc", "name":"🌌 Huyền Thiên Vực",        "min_realm":9,  "max_realm":14,
     "duration_min":120,"duration_max":300, "stamina_cost":100,
     "exp_min":100000000,"exp_max":600000000,"lt_min":500000,"lt_max":2000000,
     "drop_items":["503","104","305"], "drop_rate":0.18,
     "desc":"Vực thẳm Huyền Thiên, Hóa Thần chi địa"},
    # ── Luyện Hư (realm 10) ──────────────────────────────
    {"id":"tien_vuc",        "name":"🌸 Tiên Vực Phong Hoa",     "min_realm":10, "max_realm":15,
     "duration_min":140,"duration_max":360, "stamina_cost":120,
     "exp_min":600000000,"exp_max":3000000000,"lt_min":1000000,"lt_max":5000000,
     "drop_items":["503","403","104"], "drop_rate":0.16,
     "desc":"Vực Tiên thấm đẫm Tiên Khí ngàn năm"},
    # ── Hợp Thể (realm 11) ───────────────────────────────
    {"id":"hoa_long_tam",    "name":"🔥 Hỏa Long Đàm",           "min_realm":11, "max_realm":16,
     "duration_min":160,"duration_max":400, "stamina_cost":140,
     "exp_min":3000000000,"exp_max":15000000000,"lt_min":3000000,"lt_max":12000000,
     "drop_items":["504","104","305"], "drop_rate":0.15,
     "desc":"Đàm lửa rồng, Hỏa Long Khí tụ đỉnh cao"},
    # ── Đại Thừa (realm 12) ──────────────────────────────
    {"id":"linh_thu_vien",   "name":"🦋 Linh Thú Viên Lâm",      "min_realm":12, "max_realm":18,
     "duration_min":180,"duration_max":440, "stamina_cost":160,
     "exp_min":15000000000,"exp_max":80000000000,"lt_min":8000000,"lt_max":40000000,
     "drop_items":["4","403","104"], "drop_rate":0.14,
     "desc":"Vườn linh thú thần kỳ, Đại Thừa chi cảnh"},
    # ── Độ Kiếp (realm 13) ───────────────────────────────
    {"id":"thien_kiep_truong","name":"⚡ Thiên Kiếp Trường",      "min_realm":13, "max_realm":20,
     "duration_min":200,"duration_max":480, "stamina_cost":180,
     "exp_min":80000000000,"exp_max":400000000000,"lt_min":20000000,"lt_max":100000000,
     "drop_items":["503","305","104"], "drop_rate":0.13,
     "desc":"Trường sấm sét thiên kiếp, vượt qua là thành Tiên"},
    # ── Bán Tiên+ (realm 14+) ────────────────────────────
    {"id":"tien_linh_dao",   "name":"🏝️ Tiên Linh Đảo",          "min_realm":14, "max_realm":25,
     "duration_min":240,"duration_max":560, "stamina_cost":200,
     "exp_min":400000000000,"exp_max":2000000000000,"lt_min":50000000,"lt_max":300000000,
     "drop_items":["503","403","104"], "drop_rate":0.12,
     "desc":"Đảo Tiên giới, Bán Tiên lĩnh ngộ"},
    # ── Chân Tiên+ (realm 18+) ───────────────────────────
    {"id":"loi_phat_chi_dia","name":"☁️ Lôi Phạt Chi Địa",       "min_realm":18, "max_realm":30,
     "duration_min":280,"duration_max":620, "stamina_cost":240,
     "exp_min":2000000000000,"exp_max":12000000000000,"lt_min":200000000,"lt_max":1000000000,
     "drop_items":["504","305","104"], "drop_rate":0.11,
     "desc":"Đất sấm sét Thiên Lôi, Chân Tiên mới dám bước vào"},
    # ── Lạc Tiên (realm 24+) ─────────────────────────────
    {"id":"cuu_trong_thien", "name":"🌈 Cửu Trọng Thiên",         "min_realm":24, "max_realm":38,
     "duration_min":320,"duration_max":700, "stamina_cost":280,
     "exp_min":12000000000000,"exp_max":80000000000000,"lt_min":800000000,"lt_max":5000000000,
     "drop_items":["503","305","104"], "drop_rate":0.10,
     "desc":"Chín tầng trời, Lạc Tiên chi cảnh tuyệt đỉnh"},
    # ── Đại La (realm 35+) ───────────────────────────────
    {"id":"thien_ngoai_thien","name":"✨ Thiên Ngoại Thiên",      "min_realm":35, "max_realm":48,
     "duration_min":400,"duration_max":800, "stamina_cost":350,
     "exp_min":80000000000000,"exp_max":600000000000000,"lt_min":5000000000,"lt_max":30000000000,
     "drop_items":["305","405","104"], "drop_rate":0.09,
     "desc":"Cảnh giới ngoài thiên địa, Đại La Thánh Nhân lĩnh ngộ"},
    # ── Hỗn Độn (realm 44+) ──────────────────────────────
    {"id":"hon_don_xu",      "name":"🌀 Hỗn Độn Hư Không",        "min_realm":44, "max_realm":99,
     "duration_min":480,"duration_max":900, "stamina_cost":400,
     "exp_min":600000000000000,"exp_max":5000000000000000,"lt_min":30000000000,"lt_max":200000000000,
     "drop_items":["305","104","504"], "drop_rate":0.08,
     "desc":"Không gian hỗn mang, chỉ Đạo Tổ mới sống sót"},
]

# ══ BOSS ════════════════════════════════════════════════════
WORLD_BOSS = {
    "id":"hun_don_ma_vuong", "name":"👹 Hỗn Độn Ma Vương",
    "hp":1_000_000_000_000, "atk":1_000_000, "def":500_000,
    "respawn_h":24, "stamina_cost":20,
    "reward_ha":50000, "reward_trung":100,
}

def get_tower_boss(floor: int) -> dict:
    tier = (floor - 1) // 10 + 1
    return {
        "name": f"Tháp Vệ Tầng {floor}",
        "hp":   100_000 * (1.5 ** tier),
        "atk":  10_000  * (1.4 ** tier),
        "def":  5_000   * (1.3 ** tier),
    }

# ══ LINH THÚ ════════════════════════════════════════════════
LINHTHU_DATA = {
    "than_long":   {"name":"🐉 Thần Long",    "rarity":"mythic",  "atk_bonus":0.20,"def_bonus":0.10,"hp_bonus":0.15,"skill":"Rồng Thở Lửa"},
    "phuong_hoang":{"name":"🦅 Phượng Hoàng", "rarity":"legendary","spd_bonus":0.25,"crit_bonus":10,"skill":"Lửa Hồi Sinh"},
    "than_quy":    {"name":"🐢 Thần Quy",     "rarity":"epic",    "def_bonus":0.30,"hp_bonus":0.25,"skill":"Mai Thần Hộ Thể"},
    "wolf":        {"name":"🐺 Băng Sói",      "rarity":"rare",    "atk_bonus":0.12,"spd_bonus":0.12,"skill":"Cắn Chết Lạnh"},
    "fox":         {"name":"🦊 Hỏa Hồ Ly",    "rarity":"uncommon","crit_bonus":8,  "luck_bonus":30,"skill":"Mê Hoặc"},
}

# ══ LUYỆN ĐAN ═══════════════════════════════════════════════
DAN_RECIPES = {
    "202":   {"name":"Luyện Khí Đan",  "ingredients":{"301":3},              "result":2,"success":0.95,"tier":1},
    "501":     {"name":"Trúc Cơ Đan",    "ingredients":{"302":3,"301":2}, "result":2,"success":0.85,"tier":2},
    "505":         {"name":"Kim Đan",         "ingredients":{"303":4,"302":2},"result":1,"success":0.70,"tier":3},
    "4":     {"name":"Đột Phá Đan",     "ingredients":{"304":3,"303":3},"result":1,"success":0.50,"tier":4},
    "503": {"name":"Trường Sinh Đan", "ingredients":{"305":2,"304":5},"result":1,"success":0.30,"tier":5},
}

# ══ NHIỆM VỤ ════════════════════════════════════════════════
DAILY_QUESTS = [
    {"id":"bequan_30m",  "name":"🧘 Bế quan 30 phút",    "type":"cultivation_time","target":1800,"reward_ha":2000, "reward_exp":5000},
    {"id":"bequan_2h",   "name":"🧘 Bế quan 2 giờ",       "type":"cultivation_time","target":7200,"reward_ha":8000, "reward_exp":20000},
    {"id":"bicanh_1",    "name":"🗺️ Thám hiểm 1 lần",     "type":"explore_count",  "target":1,   "reward_ha":3000, "reward_trung":1},
    {"id":"bicanh_3",    "name":"🗺️ Thám hiểm 3 lần",     "type":"explore_count",  "target":3,   "reward_ha":8000, "reward_trung":3},
    {"id":"boss_attack", "name":"👹 Tấn công Boss 3 lần",  "type":"boss_attack",    "target":3,   "reward_ha":5000, "reward_trung":2},
    {"id":"dt_play",     "name":"🎲 Chơi Đổ Thạch 2 lần", "type":"dt_play",        "target":2,   "reward_ha":1500},
    {"id":"buy_shop",    "name":"🛒 Mua đồ trong shop",    "type":"buy_item",       "target":1,   "reward_ha":1000},
    {"id":"use_dan",     "name":"💊 Dùng 1 đan dược",      "type":"use_dan",        "target":1,   "reward_ha":1000},
]

TOWER_SHOP = [
    {"id":"4",   "name":"Đột Phá Đan",    "cost":500,  "qty":1},
    {"id":"204",  "name":"Đại Hoàn Đan",   "cost":300,  "qty":3},
    {"id":"102",    "name":"Rương Vàng",     "cost":1000, "qty":1},
    {"id":"103","name":"Rương Kim Cương","cost":3000, "qty":1},
    {"id":"405",     "name":"Thần Ngọc",      "cost":2000, "qty":1},
]

RARITY_EMOJI = {
    "common":"⬜","uncommon":"🟩","rare":"🟦",
    "epic":"🟪","legendary":"🟧","mythic":"🟥","divine":"✨"
}

# ══ COMPAT FUNCS ════════════════════════════════════════════
def fmt_number(n):
    from utils.embeds import fmt
    return fmt(n)

def format_linh_thach(ha=0, trung=0, cuc=0):
    from utils.embeds import fmt_lt
    return fmt_lt(ha, trung, cuc)

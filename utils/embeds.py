"""utils/embeds.py - Hàm tiện ích format số & tạo embed Discord

File này được toàn bộ các cog import (thường qua `from utils.embeds import *`).
Cung cấp: fmt, fmt_time, fmt_lt, bar, bar_color, realm_color, realm_icon,
success, warn, error, info, make, REALM_COLORS.
"""
import discord
import math

# ══ MÀU SẮC THEO CẢNH GIỚI ════════════════════════════════════
# Index càng cao (cảnh giới càng mạnh) màu càng "nóng/quý" hơn.
REALM_COLORS = [
    0x9E9E9E,  # 0  Luyện Khí - xám
    0x8BC34A,  # 1  xanh lá nhạt
    0x4CAF50,  # 2  xanh lá
    0x009688,  # 3  xanh ngọc
    0x00BCD4,  # 4  xanh cyan
    0x2196F3,  # 5  xanh dương
    0x3F51B5,  # 6  chàm
    0x673AB7,  # 7  tím
    0x9C27B0,  # 8  tím đậm
    0xE91E63,  # 9  hồng
    0xF44336,  # 10 đỏ
    0xFF5722,  # 11 cam đỏ
    0xFF9800,  # 12 cam
    0xFFC107,  # 13 vàng cam (tiên cấp)
    0xFFEB3B,  # 14 vàng
    0xFFD700,  # 15 vàng kim
    0xFFFFFF,  # 16 trắng (tiên vương)
    0xE0E0E0,  # 17 xám sáng (Hư Không)
    0xB0BEC5,  # 18 xám xanh (Thiên Đạo)
    0xCFD8DC,  # 19 trắng bạc (Vũ Trụ)
    0xF8F9FA,  # 20 trắng ngà (Bản Nguyên)
    0xFFF9C4,  # 21 vàng nhạt siêu việt (Vạn Giới)
]

REALM_ICONS = [
    "🌱","🍀","🌿","🌾","🌻","🔥","💧","⚡","☁️","🌙",
    "⭐","✨","🌟","💫","🌞","👑","🐉",
    "🌑","🌌","🔮","♾️","🌈",
]


def _realm_band(realm_index: int, total_realms: int = 70) -> int:
    """Chia realm_index thành 1 trong N băng màu/icon."""
    n = max(1, total_realms)
    band_count = len(REALM_COLORS)
    band = int((realm_index / n) * band_count)
    return max(0, min(band, band_count - 1))


def realm_color(realm_index: int) -> int:
    """Trả về màu hex (int) tương ứng với cảnh giới."""
    try:
        return REALM_COLORS[_realm_band(int(realm_index))]
    except Exception:
        return 0x9E9E9E


def realm_icon(realm_index: int) -> str:
    """Trả về icon tương ứng với cảnh giới."""
    try:
        return REALM_ICONS[_realm_band(int(realm_index))]
    except Exception:
        return "🌱"


# ══ FORMAT SỐ ═════════════════════════════════════════════════
_SUFFIXES = [
    (1e60, "∞"),
    (1e57, "Vg"),  (1e54, "Ug"),  (1e51, "Tg"),
    (1e48, "Sg"),  (1e45, "Qig"), (1e42, "Qag"),
    (1e39, "Trig"),(1e36, "Dug"),
    (1e33, "Dc"),  (1e30, "No"),  (1e27, "Oc"),  (1e24, "Sp"),
    (1e21, "Sx"),  (1e18, "Qi"),  (1e15, "Qa"),  (1e12, "T"),
    (1e9,  "B"),   (1e6,  "M"),
]

def fmt(n) -> str:
    """Format số lớn cho dễ đọc: 1234 -> 1,234 | 1_500_000 -> 1.5M"""
    try:
        n = float(n)
    except (TypeError, ValueError):
        return str(n)
    neg = n < 0
    n = abs(n)
    # Số quá lớn hoặc inf: dùng scientific notation gọn
    if math.isinf(n) or math.isnan(n) or n >= 1e60:
        if math.isinf(n) or math.isnan(n):
            return "-∞" if neg else "∞"
        exp = int(math.floor(math.log10(n))) if n > 0 else 0
        mantissa = n / (10 ** exp)
        out = f"{mantissa:.2f}e{exp}"
        return f"-{out}" if neg else out
    out = None
    for val, suf in _SUFFIXES:
        if n >= val:
            num = n / val
            out = f"{num:,.2f}".rstrip("0").rstrip(".") + suf
            break
    if out is None:
        if n == int(n):
            out = f"{int(n):,}"
        else:
            out = f"{n:,.2f}"
    return f"-{out}" if neg else out


def fmt_time(seconds) -> str:
    """Format giây thành chuỗi thời gian dễ đọc: 3661 -> 1h 1m 1s"""
    try:
        seconds = int(seconds)
    except (TypeError, ValueError):
        return str(seconds)
    if seconds < 0:
        seconds = 0
    d, rem = divmod(seconds, 86400)
    h, rem = divmod(rem, 3600)
    m, s = divmod(rem, 60)
    parts = []
    if d: parts.append(f"{d}d")
    if h: parts.append(f"{h}h")
    if m: parts.append(f"{m}m")
    if s or not parts: parts.append(f"{s}s")
    return " ".join(parts)


def fmt_lt(ha=0, trung=0, cuc=0) -> str:
    """Format hiển thị 3 loại Linh Thạch (Hạ/Trung/Cực)."""
    parts = []
    if cuc:
        parts.append(f"👑{fmt(cuc)}")
    if trung:
        parts.append(f"💎{fmt(trung)}")
    parts.append(f"💰{fmt(ha)}")
    return " ".join(parts)


def bar(current, maximum, length: int = 10) -> str:
    """Tạo thanh progress bar bằng ký tự block."""
    try:
        current = float(current)
        maximum = float(maximum) if maximum else 1
    except (TypeError, ValueError):
        current, maximum = 0, 1
    if maximum <= 0:
        maximum = 1
    ratio = max(0.0, min(1.0, current / maximum))
    filled = int(round(ratio * length))
    return "█" * filled + "░" * (length - filled)


def bar_color(ratio: float) -> int:
    """Trả màu theo % (0.0 - 1.0): đỏ thấp -> xanh lá cao."""
    try:
        ratio = float(ratio)
    except (TypeError, ValueError):
        ratio = 0
    if ratio >= 0.7:
        return 0x4CAF50  # xanh lá
    if ratio >= 0.4:
        return 0xFFC107  # vàng
    if ratio >= 0.15:
        return 0xFF9800  # cam
    return 0xF44336      # đỏ


# ══ EMBED BUILDERS ═══════════════════════════════════════════
def make(title: str = None, desc: str = None, color: int = 0x2196F3, **kwargs) -> discord.Embed:
    """Embed tổng quát, có thể truyền thêm field qua kwargs (footer=...)."""
    embed = discord.Embed(title=title, description=desc, color=color)
    if "footer" in kwargs and kwargs["footer"]:
        embed.set_footer(text=kwargs["footer"])
    return embed


def success(title: str, desc: str = "") -> discord.Embed:
    """Embed báo thành công (màu xanh lá), title có thể tự kèm ✅ hoặc không."""
    t = title if any(c in title for c in ("✅","🎉","🏆")) else f"✅ {title}"
    return discord.Embed(title=t, description=desc, color=0x4CAF50)


def warn(desc: str, title: str = "⚠️ Cảnh Báo") -> discord.Embed:
    """Embed cảnh báo (màu cam)."""
    return discord.Embed(title=title, description=desc, color=0xFF9800)


def error(desc: str, title: str = "❌ Lỗi") -> discord.Embed:
    """Embed lỗi (màu đỏ)."""
    return discord.Embed(title=title, description=desc, color=0xF44336)


def info(title: str, desc: str = "") -> discord.Embed:
    """Embed thông tin chung (màu xanh dương)."""
    return discord.Embed(title=title, description=desc, color=0x2196F3)

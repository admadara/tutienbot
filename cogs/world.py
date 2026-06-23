"""cogs/world.py - Thế giới tu tiên: sự kiện, tin tức, thời tiết linh khí
PATCH: Open-Meteo API (no key) cho thời tiết thật → linh khí
"""
import discord
from discord.ext import commands
import random, time, aiohttp

from utils.helpers import require_player, now
from utils.embeds import *
from utils.game_data import REALMS, AREAS, get_realm_name

# Tọa độ mặc định mỗi guild (guild_id -> (lat, lon, city_name))
# Server Việt Nam default Hà Nội, admin có thể đổi bằng ,tl setloc
DEFAULT_LOCATION = (21.0285, 105.8542, "Hà Nội")

# Map thời tiết thật (WMO code) → thời tiết linh khí
def _wmo_to_linh_khi(wmo_code, temp_c):
    """Chuyển WMO weather code + nhiệt độ → thời tiết linh khí."""
    if wmo_code == 0:  # Clear sky
        if temp_c >= 35:
            return {
                "name": "🔥 Hỏa Thiên Chi Lực",
                "exp_bonus": 0.1, "atk_bonus": 0.15,
                "desc": f"Nắng nóng {temp_c:.0f}°C! Hỏa linh khí bùng cháy, tăng sát thương!",
                "real": f"☀️ Trời thật: Nắng nóng {temp_c:.0f}°C"
            }
        return {
            "name": "☀️ Linh Khí Sung Mãn",
            "exp_bonus": 0.2, "drop_bonus": 0.1,
            "desc": f"Trời quang mây tạnh {temp_c:.0f}°C, linh khí dồi dào — tu luyện hiệu quả cao!",
            "real": f"☀️ Trời thật: Nắng đẹp {temp_c:.0f}°C"
        }
    elif wmo_code in (1, 2, 3):  # Partly/mostly cloudy
        return {
            "name": "🌫️ Mù Linh Khí",
            "exp_bonus": 0, "drop_bonus": 0.2,
            "desc": f"Mây mù {temp_c:.0f}°C, sương linh khí tụ lại — tăng tỉ lệ drop vật phẩm!",
            "real": f"⛅ Trời thật: Có mây {temp_c:.0f}°C"
        }
    elif wmo_code in (45, 48):  # Fog
        return {
            "name": "🌫️ Mù Linh Khí Đặc",
            "exp_bonus": 0.05, "drop_bonus": 0.25,
            "desc": f"Sương mù dày đặc {temp_c:.0f}°C! Drop rate tăng mạnh!",
            "real": f"🌁 Trời thật: Sương mù {temp_c:.0f}°C"
        }
    elif wmo_code in range(51, 68):  # Drizzle/Rain
        return {
            "name": "❄️ Hàn Băng Chi Khí",
            "exp_bonus": 0.05, "def_bonus": 0.15,
            "desc": f"Mưa nhẹ {temp_c:.0f}°C, hàn khí tràn về — tăng phòng thủ!",
            "real": f"🌧️ Trời thật: Mưa {temp_c:.0f}°C"
        }
    elif wmo_code in range(71, 78):  # Snow
        return {
            "name": "❄️ Hàn Băng Phong Bạo",
            "exp_bonus": 0.1, "def_bonus": 0.25,
            "desc": f"Tuyết rơi {temp_c:.0f}°C! Hàn băng chi lực cực mạnh — DEF tăng vượt trội!",
            "real": f"🌨️ Trời thật: Tuyết rơi {temp_c:.0f}°C"
        }
    elif wmo_code in (95, 96, 99):  # Thunderstorm
        return {
            "name": "⛈️ Thiên Kiếp Giáng",
            "exp_bonus": -0.1, "fail_bonus": 0.1, "crit_bonus": 10,
            "desc": f"Sấm sét {temp_c:.0f}°C! Thiên Kiếp xuất hiện — cẩn thận đột phá, nhưng Crit tăng!",
            "real": f"⛈️ Trời thật: Giông tố {temp_c:.0f}°C"
        }
    elif wmo_code in range(80, 90):  # Rain showers
        return {
            "name": "🌙 Đêm Trăng Tiên",
            "exp_bonus": 0.15, "crit_bonus": 5,
            "desc": f"Mưa rào {temp_c:.0f}°C, linh khí trong sạch — tăng EXP và Crit!",
            "real": f"🌦️ Trời thật: Mưa rào {temp_c:.0f}°C"
        }
    else:
        return {
            "name": "☀️ Linh Khí Sung Mãn",
            "exp_bonus": 0.1, "drop_bonus": 0.05,
            "desc": f"Thời tiết ổn định {temp_c:.0f}°C — linh khí bình thường.",
            "real": f"🌤️ Trời thật: {temp_c:.0f}°C"
        }


class World(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._weather_cache = {}   # guild_id -> (weather, expire)
        self._events_cache  = {}   # guild_id -> [events]
        self._guild_loc     = {}   # guild_id -> (lat, lon, city)

    async def _fetch_real_weather(self, lat, lon):
        """Gọi Open-Meteo API (free, no key) lấy WMO code + nhiệt độ."""
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,weathercode"
            f"&forecast_days=1"
        )
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(url, timeout=aiohttp.ClientTimeout(total=5)) as r:
                    if r.status == 200:
                        data = await r.json()
                        cur  = data["current"]
                        return cur["weathercode"], cur["temperature_2m"]
        except Exception:
            pass
        return None, None

    async def _get_weather(self, guild_id):
        """Lấy thời tiết linh khí — từ API thật nếu được, fallback random."""
        key = str(guild_id)
        if key in self._weather_cache:
            w, exp = self._weather_cache[key]
            if now() < exp:
                return w

        lat, lon, city = self._guild_loc.get(key, DEFAULT_LOCATION)
        wmo, temp = await self._fetch_real_weather(lat, lon)

        if wmo is not None:
            w = _wmo_to_linh_khi(wmo, temp)
            w["city"] = city
            w["from_api"] = True
        else:
            # Fallback random nếu API lỗi
            WEATHERS = [
                {"name": "☀️ Linh Khí Sung Mãn",  "exp_bonus": 0.2,  "drop_bonus": 0.1,  "desc": "Linh khí trời đất dồi dào, tu luyện hiệu quả cao!"},
                {"name": "🌙 Đêm Trăng Tiên",      "exp_bonus": 0.15, "crit_bonus": 5,    "desc": "Ánh trăng tiên chiếu xuống, tăng sát thương bạo kích!"},
                {"name": "⛈️ Thiên Kiếp Giáng",    "exp_bonus": -0.1, "fail_bonus": 0.1,  "desc": "Thiên Kiếp xuất hiện! Cẩn thận khi đột phá!"},
                {"name": "🌫️ Mù Linh Khí",         "exp_bonus": 0,    "drop_bonus": 0.2,  "desc": "Sương mù linh khí dày đặc, tăng tỉ lệ drop vật phẩm!"},
                {"name": "🔥 Hỏa Thiên Chi Lực",   "exp_bonus": 0.1,  "atk_bonus": 0.15,  "desc": "Hỏa linh khí bùng cháy, tăng sát thương!"},
                {"name": "❄️ Hàn Băng Chi Khí",    "exp_bonus": 0.05, "def_bonus": 0.15,  "desc": "Hàn khí bao phủ, tăng phòng thủ!"},
            ]
            w = random.choice(WEATHERS)
            w["from_api"] = False
            w["city"] = city

        self._weather_cache[key] = (w, now() + 1800)  # cache 30 phút
        return w

    @commands.command(name="thoi_tiet", aliases=["thoitiet", "tt", "weather"])
    async def thoi_tiet(self, ctx):
        gid = ctx.guild.id if ctx.guild else 0
        async with ctx.typing():
            w = await self._get_weather(gid)
        expire = self._weather_cache.get(str(gid), (None, now() + 1800))[1]

        embed = discord.Embed(title=f"🌍 THỜI TIẾT LINH KHÍ — {w['name']}", color=0x2196F3)
        embed.description = w["desc"]

        if w.get("real"):
            embed.description += f"\n\n📡 _{w['real']}_"
        if w.get("city"):
            embed.description += f"\n📍 Vị trí: **{w['city']}**"

        bonuses = []
        if w.get("exp_bonus"):
            pct = w["exp_bonus"]
            bonuses.append(f"✨ EXP {'+'if pct>0 else ''}{pct*100:.0f}%")
        if w.get("drop_bonus"):
            bonuses.append(f"🎁 Drop +{w['drop_bonus']*100:.0f}%")
        if w.get("crit_bonus"):
            bonuses.append(f"💥 CRIT +{w['crit_bonus']}%")
        if w.get("atk_bonus"):
            bonuses.append(f"⚔️ ATK +{w['atk_bonus']*100:.0f}%")
        if w.get("def_bonus"):
            bonuses.append(f"🛡️ DEF +{w['def_bonus']*100:.0f}%")
        if w.get("fail_bonus"):
            bonuses.append(f"⚠️ Fail chance +{w['fail_bonus']*100:.0f}%")

        if bonuses:
            embed.add_field(name="📊 Hiệu Ứng", value="\n".join(bonuses), inline=False)

        src = "📡 Open-Meteo (thời tiết thật)" if w.get("from_api") else "🎲 Ngẫu nhiên (API không khả dụng)"
        embed.set_footer(text=f"Đổi sau: {fmt_time(int(expire - now()))}  •  {src}")
        await ctx.send(embed=embed)

    @commands.command(name="setloc", aliases=["setlocation", "datloc"])
    @commands.has_permissions(administrator=True)
    async def setloc(self, ctx, lat: float, lon: float, *, city: str = "Server"):
        """Admin: đặt tọa độ thật cho server (,tl setloc 21.03 105.85 Hà Nội)"""
        gid = str(ctx.guild.id if ctx.guild else 0)
        self._guild_loc[gid] = (lat, lon, city)
        self._weather_cache.pop(gid, None)  # xóa cache cũ
        await ctx.send(embed=discord.Embed(
            description=f"✅ Đã đặt vị trí server: **{city}** ({lat}, {lon})\nGõ `,tl tt` để xem thời tiết mới.",
            color=0x4CAF50
        ))

    @commands.command(name="su_kien", aliases=["sukien", "sk", "events"])
    async def su_kien(self, ctx):
        EVENTS = [
            "🌟 **Song Nguyệt Tề Chiếu** — EXP ×2 trong 2 giờ tới!",
            "👹 **Ma Vương Xuất Thế** — Boss có HP ×3 và thưởng ×5!",
            "💰 **Chợ Linh Tiên** — Giá shop giảm 20% hôm nay!",
            "⚗️ **Ngày Luyện Đan** — Tỉ lệ thành công luyện đan +30%!",
            "🎁 **Mưa Hồng Bao** — Điểm danh nhận thêm 2x LT!",
            "🗺️ **Khám Phá Bí Cảnh Mới** — Drop rate bí cảnh +50%!",
            "⚔️ **Đại Tỉ Võ** — PK được thêm 2x thưởng LT!",
            "🧘 **Thánh Địa Mở Cửa** — Tu luyện được +1 TL/phút!",
        ]
        import datetime
        today = datetime.date.today().toordinal()
        random.seed(today)
        active = random.sample(EVENTS, k=random.randint(2, 4))
        random.seed()

        embed = discord.Embed(title="📅 SỰ KIỆN ĐANG DIỄN RA", color=0xFF9800)
        embed.description = "\n\n".join(active)
        embed.set_footer(text="Sự kiện thay đổi mỗi ngày  •  Tu Tiên Bot v4")
        await ctx.send(embed=embed)

    @commands.command(name="ban_do", aliases=["bando", "map", "bd"])
    async def ban_do(self, ctx, chau: str = None):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return

        import random, datetime
        WEATHER = ["☀️ Nắng Đẹp", "🌧️ Mưa Rào", "⛅ Âm U", "⚡ Sấm Sét", "❄️ Tuyết Rơi", "🌈 Cầu Vồng"]
        random.seed(datetime.date.today().toordinal())
        weather = random.choice(WEATHER)
        random.seed()

        CHAU_DATA = {
            "trung": {
                "name": "TRUNG CHÂU", "icon": "🏯", "color": 0xFFD700,
                "img": "https://cdn.discordapp.com/attachments/1423202524512522302/1516937145560862720/IMG_20260617_145347.jpg",
                "desc": "Trung tâm của thế giới tu tiên, nơi Thiên Đô tọa lạc.",
                "safe": ["Thiên Đô", "Cố Đô", "Thần Điện Thiên Cực"],
                "wild": [
                    ("t1","Rừng Già U Minh","Linh thạch"),
                    ("t2","Kỳ Lân Động","Quái vật"),
                    ("t3","Hồ Quang","Khoáng thạch"),
                    ("t4","Biển Cát","Linh thạch"),
                    ("t5","Đường Tơ Lụa Cổ","Thương mại"),
                    ("t6","Rừng Trúc Xanh","Thảo dược"),
                ]
            },
            "nam": {
                "name": "NAM THIÊM BỘ CHÂU", "icon": "🌴", "color": 0x2E7D32,
                "img": "https://cdn.discordapp.com/attachments/1423202524512522302/1516937144319475924/IMG_20260617_145110.jpg",
                "desc": "Đại lục phương Nam, rừng già u minh bí ẩn.",
                "safe": ["Thành Cổ Tiên Lâm", "Cảng Biển Dạ Khúc"],
                "wild": [
                    ("n1","Rừng Già U Minh","Thảo dược"),
                    ("n2","Cổ Linh Thú","Quái vật"),
                    ("n3","Đầm Lầy Độc Khí","Độc phẩm"),
                    ("n4","Dãy Núi Trường Sinh","Khoáng thạch"),
                    ("n5","Đền Thờ Bạch Hổ","Linh thạch"),
                    ("n6","Strange Ecosystem","Bí ẩn"),
                ]
            },
            "tay": {
                "name": "TÂY NGƯU HẠ CHÂU", "icon": "🏜️", "color": 0xF57F17,
                "img": "https://cdn.discordapp.com/attachments/1423202524512522302/1516937144776527973/IMG_20260617_145051.jpg",
                "desc": "Sa mạc bất tận với những bí ẩn cổ đại.",
                "safe": ["Hải Cảng Cát Cứ","Đoàn Thương Buôn"],
                "wild": [
                    ("tay1","Đại Sa Hà","Linh thạch"),
                    ("tay2","Tàn Tích Cổ Đô","Khoáng thạch"),
                    ("tay3","Ốc Đảo Sâm Đan","Thảo dược"),
                    ("tay4","Quỷ Môn Quan","Quái vật"),
                    ("tay5","Ma Điện U Minh","Quái vật"),
                    ("tay6","Phù Sa Đảo","Linh thạch"),
                    ("tay7","Ốc Đảo Nam Sâm Đan","Thảo dược"),
                    ("tay8","Núi Viêm Sa","Khoáng thạch"),
                    ("tay9","Tháp Quỷ","Quái vật"),
                    ("tay10","Ốc Đảo Bích Sa","Thảo dược"),
                    ("tay11","Tây Hải","Khoáng thạch"),
                ]
            },
            "bac": {
                "name": "BẮC CÂU LƯ CHÂU", "icon": "❄️", "color": 0x0288D1,
                "img": "https://cdn.discordapp.com/attachments/1423202524512522302/1516937146014109788/IMG_20260617_145607.jpg",
                "desc": "Đại lục băng tuyết vĩnh cửu, lạnh giá cực độ.",
                "safe": ["Cung Điện Băng Giá","Thành Phố Băng Tinh"],
                "wild": [
                    ("b1","Thiên Sơn Băng Giá","Khoáng thạch"),
                    ("b2","Rừng Thông Tuyết Phủ","Thảo dược"),
                    ("b3","Ngọc Cung Tuyết Sơn","Linh thạch"),
                    ("b4","Hang Động Duyệt Linch","Bí ẩn"),
                    ("b5","Vực Thẳm Băng Dao","Quái vật"),
                    ("b6","Cánh Đồng Băng Vĩnh Cửu","Linh thạch"),
                ]
            },
            "dong": {
                "name": "ĐÔNG THẮNG THẦN CHÂU", "icon": "🐉", "color": 0x6A1B9A,
                "img": "https://cdn.discordapp.com/attachments/1423202524512522302/1516937145166860469/IMG_20260617_145604.jpg",
                "desc": "Đảo thần tiên nổi giữa biển, cội nguồn của tu tiên.",
                "safe": ["Phù Đảo Sơn","Thành Phố Thanh Long"],
                "wild": [
                    ("d1","Đạo Quán Thiên Vũ","Linh thạch"),
                    ("d2","Núi Trường Sinh","Thảo dược"),
                    ("d3","Đông Hải","Khoáng thạch"),
                    ("d4","Phù Đảo Thiên Di","Bí ẩn"),
                    ("d5","Thác Vân Hà","Linh thạch"),
                    ("d6","Quần Đảo Thần Tiên","Quái vật"),
                ]
            },
        }

        MAP_IMAGES = {
            "tay":   "https://cdn.discordapp.com/attachments/1423202524512522302/1516937144776527973/IMG_20260617_145051.jpg",
            "nam":   "https://cdn.discordapp.com/attachments/1423202524512522302/1516937144319475924/IMG_20260617_145110.jpg",
            "dong":  "https://cdn.discordapp.com/attachments/1423202524512522302/1516937145166860469/IMG_20260617_145604.jpg",
            "trung": "https://cdn.discordapp.com/attachments/1423202524512522302/1516937145560862720/IMG_20260617_145347.jpg",
            "bac":   "https://cdn.discordapp.com/attachments/1423202524512522302/1516937146014109788/IMG_20260617_145607.jpg",
        }

        if chau and chau.lower() in CHAU_DATA:
            c = CHAU_DATA[chau.lower()]
            embed = discord.Embed(
                title=f"🗺️ BẢN ĐỒ: {c['name']}",
                description=f"🌥️ **Thời tiết hiện tại:** {weather}\n\n_{c['desc']}_",
                color=c["color"]
            )
            safe_str = "\n".join(f"• {s}" for s in c["safe"])
            embed.add_field(name="🏙️ KHU VỰC AN TOÀN:", value=safe_str, inline=False)
            wild_str = "\n".join(f"• `[{w[0]}]` **{w[1]}** _({w[2]})_" for w in c["wild"])
            embed.add_field(name="⚔️ KHU VỰC DÃ NGOẠI:", value=wild_str, inline=False)
            others = "\n".join(
                f"  • `,tl map {k}` ({v['name'].title()})"
                for k, v in CHAU_DATA.items() if k != chau.lower()
            )
            embed.add_field(
                name="🌍 XEM BẢN ĐỒ CÁC ĐẠI LỤC KHÁC:",
                value=f"Sử dụng lệnh: `,tl map [tên châu lục]`\n{others}",
                inline=False
            )
            embed.add_field(name="👉 Di chuyển:", value="Dùng lệnh `,tl dichuyen [ID vùng]` để tới vùng đó.", inline=False)
            embed.set_footer(text="Tu Tiên Bot v4")
            await ctx.send(embed=embed)
            img_url = MAP_IMAGES.get(chau.lower())
            if img_url:
                img_embed = discord.Embed(color=c["color"])
                img_embed.set_image(url=img_url)
                await ctx.send(embed=img_embed)
        else:
            ri = int(player.get("realm_index", 0))
            realm_name = REALMS[ri]["name"] if ri < len(REALMS) else "?"
            embed = discord.Embed(
                title="🌍 BẢN ĐỒ THẾ GIỚI TU TIÊN",
                description=(
                    f"🌥️ **Thời tiết:** {weather}\n"
                    f"🌌 **Cảnh giới:** `{realm_name}`\n\n"
                    "Chọn châu lục để xem chi tiết:"
                ),
                color=0x1565C0
            )
            for k, c in CHAU_DATA.items():
                embed.add_field(
                    name=f"{c['icon']} {c['name']}",
                    value=f"_{c['desc']}_\n`,tl map {k}`",
                    inline=True
                )
            embed.set_footer(text=",tl map [tay/nam/bac/dong/trung]  •  Tu Tiên Bot v4")
            await ctx.send(embed=embed)

    @commands.command(name="tin_tuc", aliases=["tintuc", "news", "tt2"])
    async def tin_tuc(self, ctx):
        NEWS = [
            "📰 Hỗn Độn Ma Vương xuất hiện! Các tu sĩ hợp lực tiêu diệt!",
            "⭐ Thiên Tài mới xuất thế - đột phá 5 cảnh giới trong 1 ngày!",
            "💰 Giá Đột Phá Đan tăng mạnh tại chợ đấu giá thiên đạo!",
            "🌟 Thiên Tầng Tháp tầng 300 lần đầu tiên bị chinh phục!",
            "⚠️ Thiên Kiếp lớn sắp giáng xuống - chuẩn bị đan dược!",
            "🎉 Tông Môn mới được thành lập thu hút hàng trăm tu sĩ!",
        ]
        import datetime
        today = datetime.date.today().toordinal()
        random.seed(today + 999)
        picks = random.sample(NEWS, k=3)
        random.seed()

        embed = discord.Embed(title="📰 TIN TỨC THIÊN ĐẠO", color=0x607D8B)
        for i, n in enumerate(picks, 1):
            embed.add_field(name=f"Tin {i}", value=n, inline=False)
        embed.set_footer(text="Cập nhật hàng ngày  •  Tu Tiên Bot v4")
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(World(bot))

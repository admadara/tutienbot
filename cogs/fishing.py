"""cogs/fishing.py - Hệ Thống Câu Cá v6.0+ (Prefix riêng: ,cc)

Toàn bộ lệnh dùng DB thật (bảng fish_inventory, fish_baits, players.fish_*)
qua self.bot.db (xem utils/database.py). Đây là hệ thống độc lập với
Tu Tiên (,tl) — chỉ chia sẻ chung database/player record.
"""
import discord
from discord.ext import commands
import time, random, json

from utils.helpers import now
from utils.embeds import fmt, fmt_time, success, warn, error, info
from utils.fish_data import (
    BAITS, FISH_BOATS, FISH_RODS, MAPS, MAP_PAGES, RARITY, ISLAND_NPCS, ISLAND_NPC_MAX,
    roll_fish, current_weather, get_seasonal_event, market_price_today,
    FISH_DAILY_QUESTS, FISH_ADVENTURE, FISH_TROPHIES, FISH_BOSS,
)

CC_COLOR = 0x00BFFF


def _s(n):
    return fmt(n)


def _vn(n):
    """Format số nguyên kiểu Việt Nam, dùng dấu chấm phân cách hàng nghìn (vd: 1.000.000)."""
    return f"{int(n):,}".replace(",", ".")


def _mult(x):
    """Format hệ số nhân, bỏ số 0 thừa (vd: 1.0 -> '1', 2.45 -> '2.45')."""
    return f"{x:g}"


def _cap_display(kg):
    """Format sức chứa thuyền: dưới 1 tấn hiện kg, từ 1 tấn trở lên hiện Tấn."""
    if kg < 1000:
        return f"Sức chứa {kg}kg"
    tons = kg // 1000
    if tons < 1000:
        return f"{tons} Tấn"
    return f"{tons:,} Tấn"


async def _get_or_create_player(bot, user_id, name, guild_id=None):
    player = await bot.db.get_player(user_id)
    if not player:
        player = await bot.db.create_player(user_id, name, guild_id=guild_id)
    return player


class Fishing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ══ GUARD: yêu cầu đã có hồ sơ trước khi dùng lệnh câu cá ════
    async def _require(self, ctx):
        player = await _get_or_create_player(
            self.bot, ctx.author.id, ctx.author.display_name,
            guild_id=ctx.guild.id if ctx.guild else None
        )
        return player

    # ══ HƯỚNG DẪN (,cc) ═══════════════════════════════════════
    @commands.group(name="cc", aliases=["cauca", "fishing"], invoke_without_command=True)
    async def cc(self, ctx):
        await self._require(ctx)
        embed = discord.Embed(
            title="🎣 🎣 HƯỚNG DẪN CÂU CÁ 6.0 🎣",
            color=CC_COLOR,
            description=(
                "─────────────────\n"
                "**[Cơ Bản]**\n"
                "👉 `,cc map [trang]`: Xem bản đồ khu vực\n"
                "👉 `,cc start [map] [mồi]`: Bắt đầu câu\n"
                "👉 `,cc stop`: Kéo cần lên & Xem kết quả\n"
                "👉 `,cc info`: Xem hồ sơ & Tình trạng câu\n"
                "👉 `,cc bag`: Xem kho cá & vật phẩm\n"
                "👉 `,cc shop / ,cc buy`: Cửa hàng trang bị\n\n"
                "**[Nâng Cấp 3.0]**\n"
                "🌤️ `,cc thoitiet`: Thời tiết & hiệu ứng\n"
                "📜 `,cc nguypha`: Ngư Phả sưu tập cá\n"
                "✨ `,cc skill`: Nâng cấp kỹ năng\n"
                "📅 `,cc quest`: Nhiệm vụ hàng ngày\n\n"
                "**[V4.0]**\n"
                "🏆 `,cc trophy`: Thành tựu & Huy hiệu\n"
                "📈 `,cc market`: Thị trường giá cá hôm nay\n"
                "🥊 `,cc tournament`: Giải đấu Ngư Vương hàng tuần\n"
                "🏝️ `,cc island`: Đảo cá AFK (Thuê NPC câu hộ)\n\n"
                "**[V5.0]**\n"
                "🗺️ `,cc haido`: Hải Đồ Bí Ẩn\n"
                "🧙 `,cc adventure`: Nhiệm Vụ Phiêu Lưu\n"
                "🏰 `,cc clan`: Tộc Ngư Dân\n"
                "🎆 `,cc event`: Sự kiện theo mùa\n\n"
                "**[V6.0 🔥]**\n"
                "📅 `,cc daily`: Điểm danh nhận thưởng streak\n"
                "📊 `,cc stats`: Thống kê hồ sơ cần thủ\n"
                "🍱 `,cc chebien`: Chế biến cá bán giá cao\n\n"
                "**[Kinh Tế]**\n"
                "🛠️ `,cc craft`: Chế tạo mồi từ cá thường\n"
                "🕶️ `,cc blackmarket`: Chợ đen đổi cá lấy HT\n"
                "💎 `,cc premium`: Shop vật phẩm cao cấp\n"
                "🔱 `,cc nguthanh`: Đặc quyền & Autofill\n\n"
                "**[Hệ Thống Phụ]**\n"
                "🏠 `,cc tank`: Bể cá AFK kiếm FishCoin\n"
                "🔨 `,cc dapcan`: Cường hóa cần câu\n"
                "🏵️ `,cc vip`: Đăng ký thẻ tháng Ngư Tôn\n"
                "🎲 `,cc gacha`: Quay rương hải tặc\n"
                "🌊 `,cc boss`: Săn Boss Thế Giới\n\n"
                "👉 `,cc top`: BXH Đại Gia / Sát Ngư\n"
                "─────────────────\n"
                "💡 **Mẹo:** Pity System giúp bạn chắc chắn dính cá EPIC sau 100 lần hụt!"
            )
        )
        embed.set_footer(text="Tu Tiên Fishing Bot v6.0+  •  Prefix: ,cc")
        await ctx.send(embed=embed)

    # ══ BẢN ĐỒ KHU VỰC ════════════════════════════════════════
    @cc.command(name="map", aliases=["banDo", "khu_vuc"])
    async def cc_map(self, ctx, page: int = 1):
        page = max(1, min(page, len(MAP_PAGES)))
        map_ids = MAP_PAGES[page - 1]
        next_page = page % len(MAP_PAGES) + 1

        # Gửi ảnh trước
        import os
        img_path = f"assets/fishing/map_page{page}.jpg"
        if os.path.exists(img_path):
            await ctx.send(file=discord.File(img_path))

        # Gửi text sau
        lines = []
        for mid in map_ids:
            m = MAPS[mid]
            vip_tag = " ⭐VIP" if m.get("vip_only") else ""
            lines.append(f"**[{mid}]** {m['name']}{vip_tag}\n   📋 Yêu cầu: {m['req']} | {m['desc']}")

        embed = discord.Embed(
            title=f"🗺️ BẢN ĐỒ KHU VỰC — Trang {page}/{len(MAP_PAGES)} 🗺️",
            color=CC_COLOR,
            description=(
                f"─────────────────\n"
                f"📄 Trang {page}/{len(MAP_PAGES)}  ➡️ `,cc map {next_page}`\n"
                f"🎣 Câu cá: `,cc start <ID khu vực>`\n"
                "─────────────────\n\n" +
                "\n\n".join(lines) +
                "\n─────────────────"
            )
        )
        await ctx.send(embed=embed)

    # ══ START ═══════════════════════════════════════════════════
    @cc.command(name="start", aliases=["go", "buongcan"])
    async def cc_start(self, ctx, map_id: str = "ho", bait_id: str = None):
        player = await self._require(ctx)
        if player.get("fish_status") == "fishing":
            await ctx.send(embed=warn("Bạn đang câu cá rồi! Dùng `,cc stop` để thu cần trước.")); return

        map_id = map_id.lower()
        if map_id not in MAPS:
            names = "\n".join(f"`{k}` — {v['name']}" for k, v in MAPS.items())
            await ctx.send(embed=warn(f"Không tìm thấy bản đồ `{map_id}`!\n\n{names}")); return

        m = MAPS[map_id]
        if m.get("vip_only") and not (player.get("fish_vip_until", 0) > time.time()):
            await ctx.send(embed=warn(f"**{m['name']}** chỉ dành cho VIP! Dùng `,cc vip` để xem chi tiết.")); return

        if bait_id:
            bait_id = bait_id.lower()
            if bait_id not in BAITS:
                await ctx.send(embed=warn(f"Không tìm thấy mồi `{bait_id}`! Xem `,cc shop`.")); return
            bait = BAITS[bait_id]
            if not bait.get("permanent"):
                have = await self.bot.db.get_bait_count(ctx.author.id, bait_id)
                if have < 1:
                    await ctx.send(embed=warn(f"Bạn không có **{bait['name']}**! Mua tại `,cc shop`.")); return

        await self.bot.db.update_player(
            ctx.author.id,
            fish_status="fishing", fish_map=map_id,
            fish_bait=bait_id or "", fish_start=time.time()
        )
        bait_name = BAITS[bait_id]["name"] if bait_id else "Không dùng mồi"
        embed = success("🎣 BẮT ĐẦU CÂU CÁ",
            f"📍 **Vùng câu:** {m['name']}\n"
            f"🪱 **Mồi:** {bait_name}\n\n"
            f"📌 Dùng `,cc stop` để thu cần và xem kết quả."
        )
        await ctx.send(embed=embed)

    # ══ STOP ════════════════════════════════════════════════════
    @cc.command(name="stop", aliases=["thucan", "kethuc"])
    async def cc_stop(self, ctx):
        player = await self._require(ctx)
        if player.get("fish_status") != "fishing":
            await ctx.send(embed=warn("Bạn chưa thả cần! Dùng `,cc start [map] [mồi]` trước.")); return

        map_id = player.get("fish_map") or "ho"
        bait_id = player.get("fish_bait") or None
        elapsed = max(1, int(time.time() - player.get("fish_start", time.time())))
        minutes = elapsed / 60

        weather = current_weather()
        weather_luck = weather["luck_bonus"]

        casts = max(1, min(30, int(minutes / 3)))

        bait = BAITS.get(bait_id, {})
        results = []
        pity = player.get("fish_pity", 0)
        for _ in range(casts):
            f = roll_fish(map_id, bait_id, weather_luck)
            if f["rarity"] in ("common", "uncommon"):
                pity += 1
            else:
                pity = 0
            if pity >= 100:
                f = roll_fish(map_id, bait_id, weather_luck + 0.6)
                if f["rarity"] in ("common", "uncommon"):
                    f["rarity"] = "epic"
                    f["emoji"] = RARITY["epic"]["emoji"]
                pity = 0
            results.append(f)
            await self.bot.db.add_fish(ctx.author.id, f["fish_id"] + ":" + f["name"], 1, f["weight"])

        if bait_id and not bait.get("permanent"):
            await self.bot.db.remove_bait(ctx.author.id, bait_id, casts)

        await self.bot.db.update_player(
            ctx.author.id, fish_status="idle", fish_pity=pity
        )

        total_value = sum(f["value"] for f in results)
        rare_count = sum(1 for f in results if f["rarity"] not in ("common", "uncommon"))

        await self._add_fish_quest(ctx.author.id, "fish_count", casts)
        if rare_count:
            await self._add_fish_quest(ctx.author.id, "fish_rare", rare_count)

        lines = []
        for f in results[:10]:
            lines.append(f"{f['emoji']} {f['name']} — {f['weight']}kg (≈{_s(f['value'])} FC)")
        more = f"\n... và {len(results)-10} con khác" if len(results) > 10 else ""

        embed = success("🎣 KÉO CẦN LÊN!",
            f"📍 **{MAPS.get(map_id,{}).get('name','?')}**  •  ⏱️ Đã câu: {fmt_time(elapsed)}\n"
            f"🐟 **Số cá câu được:** {casts}\n\n"
            + "\n".join(lines) + more +
            f"\n\n💵 **Tổng giá trị ước tính:** {_s(total_value)} FishCoin\n"
            f"💡 Dùng `,cc sell all` để bán hết kho cá."
        )
        await ctx.send(embed=embed)

    async def _add_fish_quest(self, uid, qtype, amount):
        today = int(now() // 86400)
        db_qs = {q["quest_id"]: q for q in await self.bot.db.get_quests(uid)}
        for q in FISH_DAILY_QUESTS:
            if q["type"] != qtype:
                continue
            dq = db_qs.get(q["id"], {})
            reset = dq.get("reset_day", 0)
            prog = dq.get("progress", 0) if reset >= today else 0
            done = dq.get("completed", 0) if reset >= today else 0
            if done:
                continue
            np = min(prog + amount, q["target"])
            await self.bot.db.update_quest(uid, q["id"], np, 1 if np >= q["target"] else 0, today)

    # ══ INFO ═══════════════════════════════════════════════════
    @cc.command(name="info", aliases=["status", "hoso"])
    async def cc_info(self, ctx):
        player = await self._require(ctx)
        rod = FISH_RODS.get(player.get("fish_rod") or "rod_default", FISH_RODS["rod_default"])
        boat = FISH_BOATS.get(player.get("fish_boat") or "boat_default", FISH_BOATS["boat_default"])
        if player.get("fish_status") == "fishing":
            elapsed = int(time.time() - player.get("fish_start", time.time()))
            m = MAPS.get(player.get("fish_map"), {})
            embed = discord.Embed(
                title=f"⏳ BẠN ĐANG CÂU CÁ ({m.get('name','?')})",
                color=CC_COLOR,
                description=(
                    "─────────────────\n"
                    f"🎣 **Cần câu:** {rod['name']} (+{player.get('fish_rod_enhance',0)})\n"
                    f"⏱️ **Đã câu:** {fmt_time(elapsed)}\n\n"
                    "📌 Dùng `,cc stop` để thu cần."
                )
            )
        else:
            embed = discord.Embed(
                title=f"🎣 HỒ SƠ CẦN THỦ — {player['name']}",
                color=CC_COLOR,
                description=(
                    "─────────────────\n"
                    f"💰 **FishCoin:** {_s(player.get('fish_coin',0))}\n"
                    f"🐚 **Hải Trân:** {player.get('hai_tran',0)}\n"
                    f"🎣 **Cần câu:** {rod['name']} (+{player.get('fish_rod_enhance',0)})\n"
                    f"⛵ **Thuyền:** {boat['name']}\n"
                    f"📊 **Trạng thái:** Đang rảnh — sẵn sàng `,cc start`"
                )
            )
        await ctx.send(embed=embed)

    # ══ SHOP ════════════════════════════════════════════════════
    @cc.command(name="shop", aliases=["cuahang"])
    async def cc_shop(self, ctx):
        await self._require(ctx)

        rod_lines = ["🎣 **--- CẦN CÂU ---**"]
        for rid, r in FISH_RODS.items():
            if r.get("hidden") or r.get("vip_only") or r.get("gacha_only"):
                continue
            extra = f" + 🐚 {r['hai_tran']}" if r.get("hai_tran") else ""
            price_str = "Miễn phí" if r["price"] == 0 else f"💰 {_vn(r['price'])}"
            rod_lines.append(
                f"**[{rid}]** {r['name']} - {price_str}{extra}\n"
                f"   🍀 x{_mult(r['luck_mult'])} | 🐟 +{r['fish_bonus']}"
            )

        boat_lines = ["⛵ **--- THUYỀN CÂU ---**"]
        for bid, b in FISH_BOATS.items():
            if b.get("hidden"):
                continue
            extra = f" + 🐚 {b['hai_tran']}" if b.get("hai_tran") else ""
            price_str = "Miễn phí" if b["price"] == 0 else f"💰 {_vn(b['price'])}"
            boat_lines.append(
                f"**[{bid}]** {b['name']} - {price_str}{extra}\n"
                f"   📦 {_cap_display(b['capacity'])}"
            )

        bait_lines = ["🐛 **--- MỒI CÂU ---**"]
        for bid, b in BAITS.items():
            bait_lines.append(f"**[{bid}]** {b['name']} - 💰 {_vn(b['price'])}\n   ℹ️ {b['desc']}")

        sections = ["\n".join(rod_lines), "\n".join(boat_lines), "\n".join(bait_lines)]

        embed = discord.Embed(title="🏪 CỬA HÀNG ĐỒ CÂU", color=0xFF9800,
            description="─────────────────\n" + "\n\n".join(sections) +
                        "\n\n👉 **Mua:** `,cauca buy <id> [số lượng]`\n─────────────────")
        await ctx.send(embed=embed)

    @cc.command(name="buy", aliases=["mua"])
    async def cc_buy(self, ctx, item_id: str, quantity: int = 1):
        player = await self._require(ctx)
        item_id = item_id.lower()
        quantity = max(1, min(quantity, int(1e21)))

        if item_id in BAITS:
            b = BAITS[item_id]
            cost = b["price"] * quantity
            if player.get("fish_coin", 0) < cost:
                await ctx.send(embed=error(f"Không đủ FishCoin! Cần **{_s(cost)}**, có **{_s(player.get('fish_coin',0))}**.")); return
            await self.bot.db.update_player(ctx.author.id, fish_coin=player["fish_coin"] - cost)
            await self.bot.db.add_bait(ctx.author.id, item_id, quantity)
            await ctx.send(embed=success("✅ MUA THÀNH CÔNG", f"🪱 **{quantity}x {b['name']}**\n💰 Đã trả: {_s(cost)} FishCoin"))
            return

        if item_id in FISH_RODS:
            r = FISH_RODS[item_id]
            if r.get("vip_only"):
                await ctx.send(embed=warn("Cần câu này chỉ tặng cho VIP, không bán trực tiếp!")); return
            if r.get("gacha_only"):
                await ctx.send(embed=warn("Cần câu này chỉ có được qua Gacha, không bán trực tiếp!")); return
            if player.get("fish_coin", 0) < r["price"]:
                await ctx.send(embed=error(f"Không đủ FishCoin! Cần **{_vn(r['price'])}**.")); return
            hai_tran_cost = r.get("hai_tran", 0)
            if hai_tran_cost and player.get("hai_tran", 0) < hai_tran_cost:
                await ctx.send(embed=error(f"Cần thêm 🐚 **{hai_tran_cost}** Hải Trân!")); return
            await self.bot.db.update_player(ctx.author.id,
                fish_coin=player["fish_coin"] - r["price"],
                hai_tran=player.get("hai_tran", 0) - hai_tran_cost,
                fish_rod=item_id, fish_rod_enhance=0)
            await ctx.send(embed=success("✅ MUA THÀNH CÔNG", f"🎣 Đã trang bị **{r['name']}**!")); return

        if item_id in FISH_BOATS:
            b = FISH_BOATS[item_id]
            if player.get("fish_coin", 0) < b["price"]:
                await ctx.send(embed=error(f"Không đủ FishCoin! Cần **{_vn(b['price'])}**.")); return
            hai_tran_cost = b.get("hai_tran", 0)
            if hai_tran_cost and player.get("hai_tran", 0) < hai_tran_cost:
                await ctx.send(embed=error(f"Cần thêm 🐚 **{hai_tran_cost}** Hải Trân!")); return
            await self.bot.db.update_player(ctx.author.id,
                fish_coin=player["fish_coin"] - b["price"],
                hai_tran=player.get("hai_tran", 0) - hai_tran_cost,
                fish_boat=item_id)
            await ctx.send(embed=success("✅ MUA THÀNH CÔNG", f"⛵ Đã trang bị **{b['name']}**!")); return

        await ctx.send(embed=error(f"Không tìm thấy vật phẩm `{item_id}`! Xem `,cauca shop`."))

    # ══ BAG ═════════════════════════════════════════════════════
    @cc.command(name="bag", aliases=["kho", "inv"])
    async def cc_bag(self, ctx, page: int = 1):
        player = await self._require(ctx)
        fish_inv = await self.bot.db.get_fish_inventory(ctx.author.id)
        fish_inv = [f for f in fish_inv if f["count"] > 0]
        baits = await self.bot.db.get_baits(ctx.author.id)
        rod = FISH_RODS.get(player.get("fish_rod") or "rod_default", FISH_RODS["rod_default"])
        boat = FISH_BOATS.get(player.get("fish_boat") or "boat_default", FISH_BOATS["boat_default"])

        PAGE_SIZE = 10
        total_pages = max(1, (len(fish_inv) + PAGE_SIZE - 1) // PAGE_SIZE)
        page = max(1, min(page, total_pages))
        page_fish = fish_inv[(page-1)*PAGE_SIZE: page*PAGE_SIZE]

        total_weight = sum(f["total_weight"] for f in fish_inv)
        fish_lines = []
        for f in page_fish:
            try:
                _, name = f["fish_id"].split(":", 1)
            except ValueError:
                name = f["fish_id"]
            fish_lines.append(f"🐟 {name} [ID: {f['fish_id'].split(':')[0]}]: {f['count']} con ({f['total_weight']:.1f}kg)")

        bait_lines = [f"   ▪️ {BAITS.get(b['bait_id'],{}).get('name', b['bait_id'])}: {b['quantity']}" for b in baits]

        embed = discord.Embed(
            title="🎒 KHO CÁ & VẬT PHẨM", color=0x32CD32,
            description=(
                "─────────────────\n"
                f"💰 **Số dư:** {_s(player.get('fish_coin',0))} FishCoin\n"
                f"🐚 **Hải Trân:** {player.get('hai_tran',0)} viên\n"
                f"🎣 **Cần câu:** {rod['name']} (+{player.get('fish_rod_enhance',0)})\n"
                f"⛵ **Thuyền:** {boat['name']}\n"
                "─────────────────\n"
                "🐛 **MỒI CÂU:**\n" + ("\n".join(bait_lines) if bait_lines else "   _Không có mồi nào_") + "\n"
                "─────────────────\n"
                f"📦 **CÁ (Trang {page}/{total_pages})**\n\n" +
                ("\n".join(fish_lines) if fish_lines else "_Chưa có con cá nào, đi câu thôi!_") + "\n"
                "─────────────────\n"
                f"⚖️ **Tổng trọng lượng:** {total_weight:.1f}kg\n\n"
                "💡 **Lệnh:** `,cc bag [trang]` | `,cc sell all`"
            )
        )
        await ctx.send(embed=embed)

    # ══ SELL ════════════════════════════════════════════════════
    @cc.command(name="sell", aliases=["ban"])
    async def cc_sell(self, ctx, target: str = "all"):
        player = await self._require(ctx)
        fish_inv = await self.bot.db.get_fish_inventory(ctx.author.id)
        fish_inv = [f for f in fish_inv if f["count"] > 0]
        if not fish_inv:
            await ctx.send(embed=warn("Bạn không có cá nào để bán!")); return

        if target.lower() != "all":
            fish_inv = [f for f in fish_inv if f["fish_id"].startswith(target.lower())]
            if not fish_inv:
                await ctx.send(embed=warn(f"Không tìm thấy cá `{target}` trong kho!")); return

        total = 0
        for f in fish_inv:
            rid_char = f["fish_id"][0]
            rarity_map = {"c": "common", "u": "uncommon", "r": "rare", "e": "epic", "l": "legendary", "m": "mythic"}
            rarity = rarity_map.get(rid_char, "common")
            price = market_price_today(rarity)
            value = int(f["total_weight"] * price)
            total += value
            await self.bot.db.remove_fish(ctx.author.id, f["fish_id"], f["count"])

        await self.bot.db.update_player(ctx.author.id, fish_coin=player.get("fish_coin", 0) + total)
        await self._add_fish_quest(ctx.author.id, "fish_sell", len(fish_inv))
        await ctx.send(embed=success("💰 BÁN THÀNH CÔNG", f"Đã bán **{len(fish_inv)} loại cá**\n💵 Nhận được: **{_s(total)} FishCoin**"))

    # ══ THỜI TIẾT ═══════════════════════════════════════════════
    @cc.command(name="thoitiet", aliases=["weather"])
    async def cc_thoitiet(self, ctx):
        w = current_weather()
        embed = discord.Embed(
            title="🌤️ DỰ BÁO THỜI TIẾT 🌤️", color=0xFFD700,
            description=(
                "─────────────────\n"
                f"**Trạng thái:** {w['emoji']} {w['name']}\n"
                f"**Hiệu quả:** {w['effect']}\n\n"
                "💡 Thời tiết thay đổi mỗi 4 tiếng. Hãy chọn thời điểm thích hợp để buông cần!\n"
                "─────────────────"
            )
        )
        await ctx.send(embed=embed)

    # ══ SỰ KIỆN ═════════════════════════════════════════════════
    @cc.command(name="event", aliases=["sukien"])
    async def cc_event(self, ctx):
        import datetime
        month = datetime.datetime.now().month
        e = get_seasonal_event(month)
        embed = discord.Embed(
            title="🎆 SỰ KIỆN THEO MÙA 🎆", color=0xFF6347,
            description=(
                "─────────────────\n"
                f"📅 **Tháng hiện tại:** {month}\n\n"
                f"✨ **ĐANG DIỄN RA:** {e['name']}\n"
                f"📝 {e['desc']}\n\n"
                f"⚔️ **Bonus:** {e['bonus']}\n"
                "─────────────────"
            )
        )
        await ctx.send(embed=embed)

    # ══ NGƯ PHẢ ═════════════════════════════════════════════════
    @cc.command(name="nguypha", aliases=["ngu_pha", "fishdex"])
    async def cc_nguypha(self, ctx):
        player = await self._require(ctx)
        fish_inv = await self.bot.db.get_fish_inventory(ctx.author.id)
        caught_ids = {f["fish_id"].split(":")[0] for f in fish_inv if f["count"] > 0}

        from utils.fish_data import FISH_NAMES
        lines = []
        total_species = 0
        caught_species = 0
        for rarity, names in FISH_NAMES.items():
            rconf = RARITY[rarity]
            for i, name in enumerate(names):
                total_species += 1
                found = any(cid.startswith(rarity[0]) for cid in caught_ids)
                if found:
                    caught_species += 1
            count_in_rarity = sum(1 for cid in caught_ids if cid.startswith(rarity[0]))
            lines.append(f"{rconf['emoji']} **{rconf['name']}**: {min(count_in_rarity,len(names))}/{len(names)} loài đã ghi danh")

        pct = int(caught_species / total_species * 100) if total_species else 0
        embed = discord.Embed(
            title="📜 NGƯ PHẢ — Sưu Tập Cá", color=0x795548,
            description=(
                "─────────────────\n" + "\n".join(lines) +
                f"\n─────────────────\n📊 **Hoàn thành:** {pct}%\n\n"
                "💡 Câu cá ở nhiều vùng khác nhau để hoàn thiện Ngư Phả!"
            )
        )
        await ctx.send(embed=embed)

    # ══ SKILL ═══════════════════════════════════════════════════
    @cc.command(name="skill", aliases=["kynang"])
    async def cc_skill(self, ctx):
        player = await self._require(ctx)
        nguthanh = player.get("fish_nguthanh", 0)
        discount = "50%" if nguthanh else "0%"
        embed = discord.Embed(
            title="✨ KỸ NĂNG CẦN THỦ", color=0x9C27B0,
            description=(
                "─────────────────\n"
                "🎯 **Độ Chính Xác** — Tăng tỉ lệ dính cá. Lv hiện tại: 0\n"
                "💪 **Sức Kéo** — Tăng tốc độ thu cần. Lv hiện tại: 0\n"
                "🍀 **May Mắn** — Tăng tỉ lệ cá hiếm. Lv hiện tại: 0\n"
                "─────────────────\n"
                f"💰 **Giảm giá nâng cấp (Ngư Thánh):** {discount}\n\n"
                "💡 Dùng `,cc skill up <tên kỹ năng>` để nâng cấp (sắp ra mắt)."
            )
        )
        await ctx.send(embed=embed)

    # ══ QUEST (Nhiệm vụ hàng ngày) ═══════════════════════════════
    @cc.command(name="quest", aliases=["nhiemvu"])
    async def cc_quest(self, ctx):
        player = await self._require(ctx)
        today = int(now() // 86400)
        db_qs = {q["quest_id"]: q for q in await self.bot.db.get_quests(ctx.author.id)}
        lines = []
        for q in FISH_DAILY_QUESTS:
            dq = db_qs.get(q["id"], {})
            reset = dq.get("reset_day", 0)
            prog = dq.get("progress", 0) if reset >= today else 0
            done = dq.get("completed", 0) if reset >= today else 0
            icon = "✅" if done else "▶️"
            reward = f"💰{_s(q['reward_coin'])}"
            if q.get("reward_bait"):
                bid, qty = q["reward_bait"]
                reward += f" + {qty}x {BAITS[bid]['name']}"
            lines.append(f"{icon} **{q['name']}**\n   📊 {prog}/{q['target']}  •  🎁 {reward}")
        embed = discord.Embed(
            title="📅 NHIỆM VỤ HÀNG NGÀY", color=0x4CAF50,
            description="─────────────────\n" + "\n\n".join(lines) + "\n─────────────────"
        )
        await ctx.send(embed=embed)

    # ══ TROPHY (V4.0) ═════════════════════════════════════════════
    @cc.command(name="trophy", aliases=["thanhtuu"])
    async def cc_trophy(self, ctx):
        player = await self._require(ctx)
        fish_inv = await self.bot.db.get_fish_inventory(ctx.author.id)
        total_fish = sum(f["count"] for f in fish_inv)
        epic_fish = sum(f["count"] for f in fish_inv if f["fish_id"].startswith("e"))
        mythic_fish = sum(f["count"] for f in fish_inv if f["fish_id"].startswith("m"))

        lines = []
        for t in FISH_TROPHIES:
            cur = {"total_fish": total_fish, "epic_fish": epic_fish, "mythic_fish": mythic_fish, "boss_kill": 0}.get(t["type"], 0)
            done = cur >= t["target"]
            icon = "🏆" if done else "🔒"
            lines.append(f"{icon} **{t['name']}**\n   {t['desc']}  ({min(cur,t['target'])}/{t['target']})")

        embed = discord.Embed(
            title="🏆 THÀNH TỰU & HUY HIỆU", color=0xFFD700,
            description="─────────────────\n" + "\n\n".join(lines) + "\n─────────────────"
        )
        await ctx.send(embed=embed)

    # ══ MARKET (V4.0) ═══════════════════════════════════════════
    @cc.command(name="market", aliases=["thitruong"])
    async def cc_market(self, ctx):
        lines = []
        for rid, r in RARITY.items():
            price = market_price_today(rid)
            lines.append(f"{r['emoji']} **{r['name']}**: {_s(price)} FC/kg")
        embed = discord.Embed(
            title="📈 THỊ TRƯỜNG GIÁ CÁ HÔM NAY", color=0x009688,
            description="─────────────────\n" + "\n".join(lines) +
            "\n─────────────────\n💡 Giá dao động mỗi ngày, hãy bán đúng lúc giá cao!"
        )
        await ctx.send(embed=embed)

    # ══ TOURNAMENT (V4.0) ════════════════════════════════════════
    @cc.command(name="tournament", aliases=["giaidau"])
    async def cc_tournament(self, ctx):
        guild_id = ctx.guild.id if ctx.guild else None
        top = await self.bot.db.get_fish_leaderboard(order="fish_coin", limit=5, guild_id=guild_id)
        lines = [f"**#{i+1}** {p['name']} — {_s(p.get('fish_coin',0))} FC" for i, p in enumerate(top)] or ["_Chưa có ai tham gia tuần này_"]
        embed = discord.Embed(
            title="🥊 GIẢI ĐẤU NGƯ VƯƠNG HÀNG TUẦN", color=0xE91E63,
            description=(
                "─────────────────\n"
                "🏆 **BXH Tuần Này (theo FishCoin):**\n" + "\n".join(lines) +
                "\n─────────────────\n🎁 Top 3 nhận thưởng vào Chủ Nhật hàng tuần."
            )
        )
        await ctx.send(embed=embed)

    # ══ ISLAND (V4.0 - Đảo cá AFK) ════════════════════════════════
    @cc.command(name="island", aliases=["dao"])
    async def cc_island(self, ctx, sub: str = None):
        player = await self._require(ctx)
        if sub == "collect":
            await self.cc_island_collect(ctx); return
        if sub == "hire":
            await self.cc_island_hire(ctx); return
        npcs = json.loads(player.get("island_npcs") or "{}")
        last = player.get("island_last_collect") or 0

        # Tính thu nhập / giờ tổng
        income_per_hour = sum(
            ISLAND_NPCS[nid]["income_per_hour"] * count
            for nid, count in npcs.items()
            if nid in ISLAND_NPCS
        )

        # Tính số tiền chờ thu (tối đa 24h)
        elapsed_hours = min((time.time() - last) / 3600, 24) if last else 0
        pending = int(income_per_hour * elapsed_hours)

        # Danh sách nhân viên
        if npcs:
            npc_parts = []
            for nid, count in npcs.items():
                if count > 0 and nid in ISLAND_NPCS:
                    npc_parts.append(", ".join([ISLAND_NPCS[nid]["name"]] * count))
            npc_str = ", ".join(npc_parts) if npc_parts else "_Chưa có nhân viên_"
        else:
            npc_str = "_Chưa có nhân viên_"

        embed = discord.Embed(
            title="🏝️ ĐẢO CÁ CỦA BẠN 🏝️",
            color=0x4FC3F7,
            description=(
                "─────────────────\n"
                f"👥 **Nhân viên:** {npc_str}\n"
                f"💰 **Thu nhập:** {_vn(income_per_hour)}/giờ\n"
                f"📦 **Chờ thu:** {_vn(pending)}\n\n"
                "👉 `,cc island collect` - Thu hoạch\n"
                "👉 `,cc island hire` - Xem & Thuê NPC\n"
                "─────────────────"
            )
        )
        await ctx.send(embed=embed)

    @cc.command(name="island_collect", aliases=["islandcollect"])
    async def cc_island_collect(self, ctx):
        player = await self._require(ctx)
        npcs = json.loads(player.get("island_npcs") or "{}")
        last = player.get("island_last_collect") or 0

        income_per_hour = sum(
            ISLAND_NPCS[nid]["income_per_hour"] * count
            for nid, count in npcs.items()
            if nid in ISLAND_NPCS
        )
        if income_per_hour == 0:
            await ctx.send(embed=warn("Đảo của bạn chưa có nhân viên! Dùng `,cc island hire` để thuê.")); return

        elapsed_hours = min((time.time() - last) / 3600, 24) if last else 0
        earned = int(income_per_hour * elapsed_hours)
        if earned < 1:
            await ctx.send(embed=warn("Chưa đủ thu nhập để thu hoạch, hãy đợi thêm nhé!")); return

        await self.bot.db.update_player(
            ctx.author.id,
            fish_coin=player.get("fish_coin", 0) + earned,
            island_last_collect=time.time()
        )
        await ctx.send(embed=success(
            "📦 THU HOẠCH THÀNH CÔNG",
            f"💰 Nhận được: **{_vn(earned)} FishCoin**\n"
            f"⏱️ Thời gian tích lũy: {elapsed_hours:.1f} giờ"
        ))

    @cc.command(name="island_hire", aliases=["islandhire"])
    async def cc_island_hire(self, ctx, npc_id: str = None):
        player = await self._require(ctx)

        if npc_id is None:
            # Hiển thị danh sách NPC
            lines = []
            for nid, n in ISLAND_NPCS.items():
                lines.append(
                    f"{n['emoji']} **{n['name']}** `[{nid}]`\n"
                    f"   Giá: {_vn(n['price'])} | Thu nhập: {_vn(n['income_per_hour'])}/giờ\n"
                    f"   {n['desc']}"
                )
            embed = discord.Embed(
                title="🏝️ NPC ĐẢO CÁ:",
                color=0x4FC3F7,
                description=(
                    "─────────────────\n" +
                    "\n\n".join(lines) +
                    f"\n\nLệnh: `,cc island hire <id>`\n\n"
                    f"⚠️ Tối đa **{ISLAND_NPC_MAX} người** cùng loại trên đảo.\n"
                    "─────────────────"
                )
            )
            await ctx.send(embed=embed)
            return

        # Thuê NPC
        npc_id = npc_id.lower()
        if npc_id not in ISLAND_NPCS:
            await ctx.send(embed=error(f"Không tìm thấy NPC `{npc_id}`! Xem `,cc island hire`.")); return

        n = ISLAND_NPCS[npc_id]
        npcs = json.loads(player.get("island_npcs") or "{}")
        current_count = npcs.get(npc_id, 0)

        if current_count >= ISLAND_NPC_MAX:
            await ctx.send(embed=warn(f"Đã đủ {ISLAND_NPC_MAX} **{n['name']}** trên đảo!")); return

        if player.get("fish_coin", 0) < n["price"]:
            await ctx.send(embed=error(f"Không đủ FishCoin! Cần **{_vn(n['price'])}**, có **{_vn(player.get('fish_coin',0))}**.")); return

        npcs[npc_id] = current_count + 1
        await self.bot.db.update_player(
            ctx.author.id,
            fish_coin=player.get("fish_coin", 0) - n["price"],
            island_npcs=json.dumps(npcs)
        )
        await ctx.send(embed=success(
            "✅ THUÊ THÀNH CÔNG",
            f"🏝️ Đã thuê **{n['name']}** (#{current_count + 1}/{ISLAND_NPC_MAX})\n"
            f"💰 Đã trả: {_vn(n['price'])} FishCoin\n"
            f"📈 Thu nhập tăng thêm: +{_vn(n['income_per_hour'])}/giờ"
        ))

    # ══ HẢI ĐỒ (V5.0) ════════════════════════════════════════════
    @cc.command(name="haido", aliases=["map_bi_an"])
    async def cc_haido(self, ctx):
        embed = discord.Embed(
            title="🗺️ HẢI ĐỒ BÍ ẨN", color=0x8D6E63,
            description=(
                "─────────────────\n"
                "Mảnh hải đồ có thể rơi ra ngẫu nhiên khi câu cá.\n"
                "Thu thập đủ **5 mảnh** để mở khóa rương kho báu chìm!\n\n"
                "📦 **Mảnh hiện có:** 0/5\n\n"
                "💡 Tỉ lệ rơi mảnh hải đồ: ~2% mỗi lần câu (tăng theo độ hiếm vùng câu).\n"
                "─────────────────"
            )
        )
        await ctx.send(embed=embed)

    # ══ ADVENTURE (V5.0) ═══════════════════════════════════════════
    @cc.command(name="adventure", aliases=["phieuluu"])
    async def cc_adventure(self, ctx):
        player = await self._require(ctx)
        fish_inv = await self.bot.db.get_fish_inventory(ctx.author.id)
        total_fish = sum(f["count"] for f in fish_inv)
        rare_fish = sum(f["count"] for f in fish_inv if not f["fish_id"].startswith(("c", "u")))
        legendary_fish = sum(f["count"] for f in fish_inv if f["fish_id"].startswith("l") or f["fish_id"].startswith("m"))

        progress_map = {"total_fish": total_fish, "rare_fish": rare_fish, "boss_fight": 0, "deep_fish": 0, "legendary_fish": legendary_fish}
        lines = []
        done_count = 0
        for adv in FISH_ADVENTURE:
            cur = min(progress_map.get(adv["type"], 0), adv["target"])
            done = cur >= adv["target"]
            if done:
                done_count += 1
                lines.append(f"✅ {adv['name']}")
            else:
                lines.append(f"▶️ **{adv['name']}** [ĐANG THỰC HIỆN]\n   → {adv['desc']}\n   📊 Tiến độ: {cur}/{adv['target']}")
        embed = discord.Embed(
            title="🗺️ NHIỆM VỤ PHIÊU LƯU 🗺️", color=0x8B4513,
            description=(
                "─────────────────\n"
                f"📊 **Hoàn thành:** {done_count}/{len(FISH_ADVENTURE)}\n\n" +
                "\n".join(lines) + "\n─────────────────"
            )
        )
        await ctx.send(embed=embed)

    # ══ CLAN (V5.0) ═══════════════════════════════════════════════
    @cc.command(name="clan", aliases=["toc"])
    async def cc_clan(self, ctx):
        player = await self._require(ctx)
        clan_id = player.get("fish_clan_id")
        if not clan_id:
            embed = discord.Embed(
                title="🏰 TỘC NGƯ DÂN", color=0x9932CC,
                description=(
                    "─────────────────\n"
                    "Bạn chưa gia nhập tộc nào!\n\n"
                    "👉 `,cc clancreate <tên>` — Tạo tộc mới (💰 1,000,000 FC)\n"
                    "👉 `,cc clan list` — Xem danh sách tộc\n"
                    "─────────────────"
                )
            )
            await ctx.send(embed=embed); return

        clan = await self.bot.db.fetchone("SELECT * FROM fish_clans WHERE id=?", (clan_id,))
        if not clan:
            await ctx.send(embed=warn("Tộc của bạn không còn tồn tại!")); return
        role = "👑 Tộc Trưởng" if str(clan["leader_id"]) == str(ctx.author.id) else "👤 Thành viên"
        embed = discord.Embed(
            title=f"🏰 TỘC: {clan['name']}", color=0x9932CC,
            description=(
                "─────────────────\n"
                f"{role}\n"
                f"💰 **Quỹ tộc:** {_s(clan['fund'])} FishCoin\n\n"
                "💡 Dùng `,cc clandonate <số tiền>` để đóng góp quỹ tộc.\n"
                "─────────────────"
            )
        )
        await ctx.send(embed=embed)

    @cc.command(name="clanlist")
    async def cc_clan_list(self, ctx):
        rows = await self.bot.db.fetchall("SELECT * FROM fish_clans ORDER BY fund DESC LIMIT 10")
        lines = [f"**#{i+1}** {r['name']} — 💰 {_s(r['fund'])}" for i, r in enumerate(rows)] or ["_Chưa có tộc nào được thành lập_"]
        embed = discord.Embed(
            title="🏰 DANH SÁCH TỘC NGƯ DÂN", color=0x9932CC,
            description="─────────────────\n" + "\n".join(lines) + "\n─────────────────"
        )
        await ctx.send(embed=embed)

    @cc.command(name="clancreate")
    async def cc_clan_create(self, ctx, *, name: str):
        player = await self._require(ctx)
        if player.get("fish_clan_id"):
            await ctx.send(embed=warn("Bạn đã có tộc rồi! Rời tộc cũ trước.")); return
        cost = 1_000_000
        if player.get("fish_coin", 0) < cost:
            await ctx.send(embed=error(f"Cần **{_s(cost)} FishCoin** để lập tộc!")); return
        await self.bot.db.execute(
            "INSERT INTO fish_clans (name, leader_id, fund) VALUES (?,?,0)",
            (name, str(ctx.author.id))
        )
        row = await self.bot.db.fetchone(
            "SELECT id FROM fish_clans WHERE leader_id=? ORDER BY id DESC LIMIT 1", (str(ctx.author.id),)
        )
        await self.bot.db.update_player(ctx.author.id, fish_coin=player["fish_coin"] - cost, fish_clan_id=row["id"])
        await ctx.send(embed=success("🏰 LẬP TỘC THÀNH CÔNG", f"Tộc **{name}** đã được thành lập!"))

    @cc.command(name="clandonate")
    async def cc_clan_donate(self, ctx, amount: int):
        player = await self._require(ctx)
        clan_id = player.get("fish_clan_id")
        if not clan_id:
            await ctx.send(embed=warn("Bạn chưa có tộc!")); return
        if amount <= 0 or player.get("fish_coin", 0) < amount:
            await ctx.send(embed=error("Số tiền không hợp lệ hoặc không đủ FishCoin!")); return
        await self.bot.db.execute("UPDATE fish_clans SET fund = fund + ? WHERE id=?", (amount, clan_id))
        await self.bot.db.update_player(ctx.author.id, fish_coin=player["fish_coin"] - amount)
        await ctx.send(embed=success("💰 ĐÓNG GÓP THÀNH CÔNG", f"Đã đóng góp **{_s(amount)} FishCoin** vào quỹ tộc!"))

    # ══ DAILY (V6.0) ═════════════════════════════════════════════
    @cc.command(name="daily", aliases=["diemdanh"])
    async def cc_daily(self, ctx):
        player = await self._require(ctx)
        today = int(now() // 86400)
        last = player.get("fish_daily_last", 0)
        streak = player.get("fish_daily_streak", 0)
        if last == today:
            await ctx.send(embed=warn(f"Bạn đã điểm danh hôm nay rồi! Streak hiện tại: **{streak} ngày**.")); return
        streak = streak + 1 if last == today - 1 else 1
        reward = 5000 * min(streak, 30)
        await self.bot.db.update_player(ctx.author.id,
            fish_daily_last=today, fish_daily_streak=streak,
            fish_coin=player.get("fish_coin", 0) + reward)
        await ctx.send(embed=success("📅 ĐIỂM DANH THÀNH CÔNG",
            f"🔥 **Streak:** {streak} ngày liên tiếp\n💰 **Thưởng:** +{_s(reward)} FishCoin"))

    # ══ STATS (V6.0) ═════════════════════════════════════════════
    @cc.command(name="stats", aliases=["thongke"])
    async def cc_stats(self, ctx):
        player = await self._require(ctx)
        fish_inv = await self.bot.db.get_fish_inventory(ctx.author.id)
        total_fish = sum(f["count"] for f in fish_inv)
        total_weight = sum(f["total_weight"] for f in fish_inv)
        species = len(fish_inv)
        embed = discord.Embed(
            title=f"📊 THỐNG KÊ CẦN THỦ — {player['name']}", color=0x3F51B5,
            description=(
                "─────────────────\n"
                f"🐟 **Tổng số cá đang có:** {total_fish}\n"
                f"🧬 **Số loài đã câu được:** {species}\n"
                f"⚖️ **Tổng trọng lượng kho:** {total_weight:.1f}kg\n"
                f"💰 **FishCoin hiện có:** {_s(player.get('fish_coin',0))}\n"
                f"🔥 **Streak điểm danh:** {player.get('fish_daily_streak',0)} ngày\n"
                "─────────────────"
            )
        )
        await ctx.send(embed=embed)

    # ══ CHẾ BIẾN (V6.0) ══════════════════════════════════════════
    @cc.command(name="chebien")
    async def cc_chebien(self, ctx):
        embed = discord.Embed(
            title="🍱 CHẾ BIẾN CÁ", color=0xFF7043,
            description=(
                "─────────────────\n"
                "Chế biến cá thường thành món ăn bán giá cao hơn!\n\n"
                "🍣 **Sashimi** — Cần 3 cá Thường → Bán x2 giá gốc\n"
                "🍲 **Lẩu Cá** — Cần 5 cá Khá Hiếm → Bán x3 giá gốc\n"
                "🍢 **Cá Nướng Muối Ớt** — Cần 2 cá bất kỳ → Bán x1.5 giá gốc\n\n"
                "👉 `,cc chebien <món>` để chế biến (sắp ra mắt)\n"
                "─────────────────"
            )
        )
        await ctx.send(embed=embed)

    # ══ CRAFT (Chế tạo mồi) ══════════════════════════════════════
    @cc.command(name="craft", aliases=["chetao"])
    async def cc_craft(self, ctx):
        embed = discord.Embed(
            title="🛠️ CHẾ TẠO MỒI TỪ CÁ THƯỜNG", color=0x607D8B,
            description=(
                "─────────────────\n"
                "Tái chế cá Thường dư thừa thành mồi câu!\n\n"
                "🪱 **5x Cá Thường → 1x Mồi Bột**\n"
                "🩸 **10x Cá Thường → 1x Mồi Trùng Huyết**\n\n"
                "👉 `,cc craft bait_bot` để chế tạo (sắp ra mắt)\n"
                "─────────────────"
            )
        )
        await ctx.send(embed=embed)

    # ══ CHỢ ĐEN ═══════════════════════════════════════════════════
    @cc.command(name="blackmarket", aliases=["chodeb", "cho_den"])
    async def cc_blackmarket(self, ctx):
        embed = discord.Embed(
            title="🕶️ CHỢ ĐEN", color=0x37474F,
            description=(
                "─────────────────\n"
                "Đổi cá hiếm lấy Hải Trân (tỉ giá đặc biệt, không qua thị trường thường)!\n\n"
                "👑 **1x Cá Thần Thoại → 3 🐚 Hải Trân**\n"
                "🐉 **1x Cá Huyền Thoại → 1 🐚 Hải Trân**\n\n"
                "👉 `,cc blackmarket trade <fish_id>` (sắp ra mắt)\n"
                "─────────────────"
            )
        )
        await ctx.send(embed=embed)

    # ══ PREMIUM SHOP ═══════════════════════════════════════════════
    @cc.command(name="premium")
    async def cc_premium(self, ctx):
        embed = discord.Embed(
            title="💎 SHOP VẬT PHẨM CAO CẤP", color=0xAB47BC,
            description=(
                "─────────────────\n"
                "🎁 **Rương Hải Tặc Vàng** — 🐚 5 — Mở ra trang bị/mồi ngẫu nhiên cao cấp\n"
                "🧲 **Nam Châm Hút Cá** — 🐚 10 — Tăng vĩnh viễn 5% tỉ lệ dính cá\n"
                "⏱️ **Đồng Hồ Cát Thời Gian** — 🐚 8 — Bỏ qua 1 giờ câu ngay lập tức\n\n"
                "👉 `,cc premium buy <id>` (sắp ra mắt)\n"
                "─────────────────"
            )
        )
        await ctx.send(embed=embed)

    # ══ VIP ═══════════════════════════════════════════════════════
    @cc.command(name="vip")
    async def cc_vip(self, ctx):
        player = await self._require(ctx)
        active = player.get("fish_vip_until", 0) > time.time()
        status = f"✅ ĐANG HOẠT ĐỘNG (còn {fmt_time(player['fish_vip_until']-time.time())})" if active else "CHƯA ĐĂNG KÝ ❌"
        embed = discord.Embed(
            title="💎 THÔNG TIN THẺ VIP TÀI LỘC 💎", color=0xFFD700,
            description=(
                "─────────────────\n"
                f"**Trạng thái:** {status}\n"
                "(Dùng `,cc vipbuy` để mua với giá 10 Hải Trân/Tuần)\n\n"
                "🌟 **ĐẶC QUYỀN VIP:**\n"
                "- Tặng Cần Ngư Tôn siêu xịn (Chỉ tặng lần đầu).\n"
                "- Mở khóa Biển Vàng (Map Long Cung).\n"
                "- Tăng 10% Tỉ lệ May Mắn.\n"
                "- Tăng Tốc Độ Câu 15%.\n"
                "- Lương mỗi ngày: 50Tr FishCoin + 1 Hải Trân.\n"
                "─────────────────"
            )
        )
        await ctx.send(embed=embed)

    @cc.command(name="vipbuy")
    async def cc_vip_buy(self, ctx):
        player = await self._require(ctx)
        cost = 10
        if player.get("hai_tran", 0) < cost:
            await ctx.send(embed=error(f"Cần **{cost} 🐚 Hải Trân**! Bạn có **{player.get('hai_tran',0)}**.")); return
        new_until = max(player.get("fish_vip_until", 0), time.time()) + 7 * 86400
        updates = {"hai_tran": player["hai_tran"] - cost, "fish_vip_until": new_until}
        first_time = player.get("fish_rod") in (None, "", "rod_default")
        if first_time:
            updates["fish_rod"] = "rod_vip1"
            updates["fish_rod_enhance"] = 0
        await self.bot.db.update_player(ctx.author.id, **updates)
        bonus = "\n🎁 Đã tặng **👑 Cần Ngư Tôn**!" if first_time else ""
        await ctx.send(embed=success("💎 ĐĂNG KÝ VIP THÀNH CÔNG", f"VIP có hiệu lực 7 ngày.{bonus}"))

    # ══ NGƯ THÁNH ════════════════════════════════════════════════
    @cc.command(name="nguthanh")
    async def cc_nguthanh(self, ctx):
        player = await self._require(ctx)
        owned = player.get("fish_nguthanh", 0)
        status = "✅ Đã Sở Hữu" if owned else "Chưa Sở Hữu ❌"
        embed = discord.Embed(
            title="✨ ĐẶC QUYỀN NGƯ THÁNH ✨", color=0xFF69B4,
            description=(
                "─────────────────\n"
                f"**Trạng thái:** {status}\n\n"
                "🎁 **QUYỀN LỢI:**\n"
                "⚡ Giảm 30% thời gian câu (Cộng dồn VIP).\n"
                "💰 Giảm 50% chi phí nâng cấp Kỹ năng.\n"
                "⚙️ Lệnh `,cc autofill`: Tự động mua mồi khi hết.\n"
                "🌟 Khung Profile Card độc quyền.\n\n"
                "💳 **Giá:** 100 Hải Trân (Vĩnh viễn)\n"
                "👉 **Lệnh:** `,cc nguthanhbuy` để sở hữu.\n"
                "─────────────────"
            )
        )
        await ctx.send(embed=embed)

    @cc.command(name="nguthanhbuy")
    async def cc_nguthanh_buy(self, ctx):
        player = await self._require(ctx)
        if player.get("fish_nguthanh"):
            await ctx.send(embed=warn("Bạn đã sở hữu Ngư Thánh rồi!")); return
        cost = 100
        if player.get("hai_tran", 0) < cost:
            await ctx.send(embed=error(f"Cần **{cost} 🐚 Hải Trân**! Bạn có **{player.get('hai_tran',0)}**.")); return
        await self.bot.db.update_player(ctx.author.id, hai_tran=player["hai_tran"] - cost, fish_nguthanh=1)
        await ctx.send(embed=success("✨ SỞ HỮU NGƯ THÁNH", "Chúc mừng! Bạn đã sở hữu Đặc Quyền Ngư Thánh vĩnh viễn."))

    @cc.command(name="autofill")
    async def cc_autofill(self, ctx):
        player = await self._require(ctx)
        if not player.get("fish_nguthanh"):
            await ctx.send(embed=warn("Lệnh này chỉ dành cho Ngư Thánh! Xem `,cc nguthanh`.")); return
        await ctx.send(embed=info("⚙️ AUTOFILL", "Tính năng tự động mua mồi khi hết sẽ sớm được bật cho tài khoản của bạn."))

    # ══ TANK (Bể cá AFK) ═════════════════════════════════════════
    @cc.command(name="tank", aliases=["beca"])
    async def cc_tank(self, ctx):
        embed = discord.Embed(
            title="🏠 BỂ CÁ AFK", color=0x26A69A,
            description=(
                "─────────────────\n"
                "Nuôi cá trong bể để kiếm FishCoin thụ động!\n\n"
                "🐟 Thả cá vào bể → Mỗi giờ sinh ra FishCoin theo độ hiếm.\n"
                "📈 Nâng cấp bể để tăng số lượng cá nuôi tối đa.\n\n"
                "👉 `,cc tank add <fish_id>` — Thả cá vào bể (sắp ra mắt)\n"
                "👉 `,cc tank collect` — Thu hoạch FishCoin (sắp ra mắt)\n"
                "─────────────────"
            )
        )
        await ctx.send(embed=embed)

    # ══ DẬP CẦN (cường hóa) ══════════════════════════════════════
    @cc.command(name="dapcan", aliases=["enhance_rod"])
    async def cc_dapcan(self, ctx):
        player = await self._require(ctx)
        rod = FISH_RODS.get(player.get("fish_rod") or "rod_default", FISH_RODS["rod_default"])
        enh = player.get("fish_rod_enhance", 0)
        cost = (enh + 1) * 50000
        embed = discord.Embed(
            title="🔨 CƯỜNG HÓA CẦN CÂU", color=0xBF360C,
            description=(
                "─────────────────\n"
                f"🎣 **Cần hiện tại:** {rod['name']} (+{enh})\n"
                f"💰 **Chi phí cường hóa tiếp:** {_s(cost)} FishCoin\n"
                f"📈 **Tỉ lệ thành công:** {max(20, 90 - enh*5)}%\n\n"
                "👉 `,cc dapcan go` để tiến hành cường hóa (sắp ra mắt)\n"
                "─────────────────"
            )
        )
        await ctx.send(embed=embed)

    # ══ GACHA ════════════════════════════════════════════════════
    @cc.command(name="gacha", aliases=["quayruong"])
    async def cc_gacha(self, ctx):
        embed = discord.Embed(
            title="🎲 QUAY RƯƠNG HẢI TẶC", color=0xFFAB00,
            description=(
                "─────────────────\n"
                "💰 **Giá quay:** 50,000 FishCoin / lượt\n\n"
                "🎁 **Phần thưởng có thể nhận:**\n"
                "🪱 Mồi câu ngẫu nhiên (60%)\n"
                "💰 FishCoin x2-5 lần giá quay (25%)\n"
                "🎣 Cần câu hiếm (10%)\n"
                "👑 Hải Trân x1-3 (5%)\n\n"
                "👉 `,cc gacha go` để quay (sắp ra mắt)\n"
                "─────────────────"
            )
        )
        await ctx.send(embed=embed)

    # ══ BOSS THẾ GIỚI ════════════════════════════════════════════
    @cc.command(name="boss", aliases=["attack", "tancong"])
    async def cc_boss(self, ctx):
        boss = FISH_BOSS
        top = await self.bot.db.get_boss_top(boss["id"], 5)
        lines = [f"**#{i+1}** <@{r['user_id']}> — {_s(r['damage'])} dmg" for i, r in enumerate(top)] or ["_Chưa ai tấn công_"]
        embed = discord.Embed(
            title=f"🌊 BOSS THẾ GIỚI: {boss['name']}", color=0xD32F2F,
            description=(
                "─────────────────\n"
                f"❤️ **HP:** {_s(boss['hp'])}\n"
                f"⚔️ **ATK:** {_s(boss['atk'])}\n\n"
                "🏆 **Top sát thương:**\n" + "\n".join(lines) +
                f"\n\n🎁 Hạ gục thưởng: {_s(boss['reward_coin'])} FC + 🐚 {boss['reward_hai_tran']}\n"
                "👉 `,cc boss go` để tấn công (sắp ra mắt)\n"
                "─────────────────"
            )
        )
        await ctx.send(embed=embed)

    # ══ TOP (Bảng xếp hạng) ══════════════════════════════════════
    @cc.command(name="top", aliases=["bxh", "rank"])
    async def cc_top(self, ctx, kind: str = "coin", pham_vi: str = None):
        is_global = (pham_vi and pham_vi.lower() in ("all", "global", "toancau")) or not ctx.guild
        guild_id = None if is_global else ctx.guild.id
        suffix = " (Toàn Server Bot)" if is_global else ""
        if kind.lower() in ("coin", "giau", "daigia"):
            rows = await self.bot.db.get_fish_leaderboard(order="fish_coin", limit=10, guild_id=guild_id)
            title = "👉 BXH ĐẠI GIA (FishCoin)" + suffix
            lines = [f"**#{i+1}** {p['name']} — {_s(p.get('fish_coin',0))} FC" for i, p in enumerate(rows)]
        else:
            rows = await self.bot.db.get_fish_leaderboard(order="hai_tran", limit=10, guild_id=guild_id)
            title = "👉 BXH SÁT NGƯ (Hải Trân)" + suffix
            lines = [f"**#{i+1}** {p['name']} — 🐚 {p.get('hai_tran',0)}" for i, p in enumerate(rows)]
        embed = discord.Embed(
            title=title, color=0xFFC107,
            description="─────────────────\n" + ("\n".join(lines) if lines else "_Chưa có dữ liệu_") + "\n─────────────────"
        )
        embed.set_footer(text=",cc top [coin/hai_tran] [all]")
        await ctx.send(embed=embed)


    # ══ ADMIN: BUFF FISH COIN & HẢI TRÂN ════════════════════
    @cc.command(name="givecoin", aliases=["addcoin","buffcoin"])
    @commands.has_permissions(administrator=True)
    async def give_fish_coin(self, ctx, target: discord.Member, so_luong: int):
        """[Admin] Thêm FishCoin cho người chơi. Dùng: ,cc givecoin @người [số]"""
        if so_luong <= 0:
            await ctx.send(embed=warn("Số lượng phải lớn hơn 0!")); return
        player = await self.bot.db.get_player(target.id)
        if not player:
            await ctx.send(embed=warn(f"**{target.display_name}** chưa tham gia câu cá!")); return
        hien_co = int(player.get("fish_coin", 0))
        await self.bot.db.update_player(target.id, fish_coin=hien_co + so_luong)
        embed = success(
            "✅ BUFF FISHCOIN",
            f"👤 **{player['name']}**\n"
            f"💰 +**{so_luong:,}** FishCoin\n"
            f"📊 Tổng: **{hien_co + so_luong:,}**"
        )
        embed.set_footer(text=f"Admin: {ctx.author.display_name}")
        await ctx.send(embed=embed)

    @cc.command(name="giveht", aliases=["addht","buffht","givehaitran"])
    @commands.has_permissions(administrator=True)
    async def give_hai_tran(self, ctx, target: discord.Member, so_luong: int):
        """[Admin] Thêm Hải Trân cho người chơi. Dùng: ,cc giveht @người [số]"""
        if so_luong <= 0:
            await ctx.send(embed=warn("Số lượng phải lớn hơn 0!")); return
        player = await self.bot.db.get_player(target.id)
        if not player:
            await ctx.send(embed=warn(f"**{target.display_name}** chưa tham gia câu cá!")); return
        hien_co = int(player.get("hai_tran", 0))
        await self.bot.db.update_player(target.id, hai_tran=hien_co + so_luong)
        embed = success(
            "✅ BUFF HẢI TRÂN",
            f"👤 **{player['name']}**\n"
            f"🐚 +**{so_luong:,}** Hải Trân\n"
            f"📊 Tổng: **{hien_co + so_luong:,}**"
        )
        embed.set_footer(text=f"Admin: {ctx.author.display_name}")
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Fishing(bot))

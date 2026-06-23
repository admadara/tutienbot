"""cogs/economy.py - Shop, mua bán, đổi LT, đấu giá v3"""
import discord
from discord.ext import commands
import time, random

from utils.helpers import require_player, now
from utils.embeds import *
from utils.game_data import ITEMS, LOOT_TABLES, format_linh_thach, DAO

AUCTION_FEE = 0.02
AUCTION_TAX = 0.15
AUCTION_DAYS = 3
PRICE_CAP = 50

class Economy(commands.Cog):
    def __init__(self, bot): self.bot = bot

    # ══ SHOP ════════════════════════════════════════════════
    @commands.command(name="shop", aliases=["cua_hang","store"])
    async def shop(self, ctx, category: str = None, page: int = 1):
        TYPE_MAP = {
            "danduoc": "dan_duoc", "dd": "dan_duoc",
            "vukhi": "vukhi", "vk": "vukhi",
            "giap": "giap",
            "phapbao": "phap_bao", "pb": "phap_bao",
            "ngoc": "ngoc",
            "nguyen_lieu": "nguyen_lieu", "nl": "nguyen_lieu",
            "linhthu": "linhthu_egg",
            "petitem": "pet_item", "pet": "pet_item", "vt": "pet_item",
            "ruong": "ruong",
            "congphap": "bi_kip", "cp": "bi_kip", "bikip": "bi_kip", "bk": "bi_kip",
        }
        if not category:
            embed = discord.Embed(title="🏪 CỬA HÀNG TU TIÊN", color=0xFF9800)
            embed.description = (
                "📦 Chọn danh mục:\n\n"
                "💊 `,tl shop danduoc` — Đan Dược & Bổ Trợ\n"
                "⚔️ `,tl shop vukhi` — Vũ Khí\n"
                "🛡️ `,tl shop giap` — Giáp Phục\n"
                "🔮 `,tl shop phapbao` — Pháp Bảo\n"
                "💎 `,tl shop ngoc` — Ngọc Khảm\n"
                "🌿 `,tl shop nguyen_lieu` — Nguyên Liệu Luyện Đan\n"
                "🐾 `,tl shop linhthu` — Trứng Linh Thú\n"
                "🦁 `,tl shop pet` — Vật Phẩm Linh Thú (Thú Quyết, Thức Ăn...)\n"
                "🎁 `,tl shop ruong` — Rương Hộp\n"
                "📚 `,tl shop congphap` — Tàng Kinh Các (Bí Kíp)\n\n"
                "💡 Mua: `,tl buy [item_id] [số]`"
            )
            embed.set_footer(text="Tu Tiên Bot v3  •  Giá tính bằng Hạ Phẩm Linh Thạch")
            await ctx.send(embed=embed)
            return

        type_filter = TYPE_MAP.get(category.lower())
        if not type_filter:
            await ctx.send(embed=warn(f"Không có danh mục `{category}`!\nGõ `,tl shop` để xem danh sách."))
            return

        # Lấy danh sách items theo loại, có giá
        all_items = [
            (iid, item) for iid, item in ITEMS.items()
            if item["type"] == type_filter and (item.get("price", 0) > 0 or type_filter == "ruong")
        ]
        # Với danduoc: sort theo shop_id nếu có
        if type_filter == "dan_duoc":
            all_items.sort(key=lambda x: (lambda v: int(v) if str(v).isdigit() else 9999)(x[1].get("shop_id", 9999)))
        elif type_filter == "vukhi":
            all_items.sort(key=lambda x: x[1].get("price", 0))
        elif type_filter == "bi_kip":
            all_items.sort(key=lambda x: (lambda v: int(v) if str(v).isdigit() else 9999)(x[1].get("shop_id", 9999)))

        PAGE_SIZE = 15
        total_pages = max(1, (len(all_items) + PAGE_SIZE - 1) // PAGE_SIZE)
        page = max(1, min(page, total_pages))
        page_items = all_items[(page-1)*PAGE_SIZE : page*PAGE_SIZE]

        CAT_TITLE = {
            "dan_duoc":    "🏪 CỬA HÀNG LINH ĐAN (Dược Phẩm) 🏪",
            "vukhi":       "⚔️ CỬA HÀNG VŨ KHÍ",
            "giap":        "🛡️ CỬA HÀNG GIÁP PHỤC",
            "phap_bao":    "🔮 CỬA HÀNG PHÁP BẢO",
            "ngoc":        "💎 CỬA HÀNG NGỌC KHẢM",
            "nguyen_lieu": "🌿 CỬA HÀNG NGUYÊN LIỆU",
            "linhthu_egg": "🐾 CỬA HÀNG LINH THÚ",
            "pet_item":    "🦁 VẬT PHẨM LINH THÚ",
            "ruong":       "🎁 CỬA HÀNG RƯƠNG HỘP",
            "bi_kip":      "📚 TÀNG KINH CÁC (Công Pháp & Bí Kíp) 📚",
        }
        embed = discord.Embed(
            title=CAT_TITLE.get(type_filter, "🏪 CỬA HÀNG"),
            color=0xFF9800
        )
        if type_filter == "vukhi":
            embed.description = "💡 *Giá càng cao → % chỉ số quy đổi càng lớn → vũ khí càng mạnh và được buff càng nhiều chỉ số!*"

        if type_filter in ("dan_duoc", "bi_kip"):
            # Format đặc biệt cho danduoc/bi_kip: có mô tả đầy đủ
            lines = []
            for i, (iid, item) in enumerate(page_items, start=(page-1)*PAGE_SIZE+1):
                sid = item.get("shop_id", iid)
                price = item.get("price", 0)
                desc = item.get("desc", "")
                req = item.get("requires", "")
                req_str = f" Yêu cầu học {req} trước." if req else ""
                if type_filter == "bi_kip":
                    sid = item.get("shop_id", iid)
                    lines.append(
                        f"**[{i}]** 🆔 {item['name']} - **{price:,} LT** (ID: {sid})\n"
                        f"   📖 {desc}{req_str}"
                    )
                else:
                    lines.append(
                        f"**[{i}]** 🆔 {item['name']} - **{price:,} LT** (ID: {iid})\n"
                        f"   📖 {desc}{req_str}"
                    )
            embed.description = "\n\n".join(lines)
        else:
            # Format cho vũ khí / giáp / pháp bảo: đầy đủ chỉ số
            for iid, item in page_items:
                price = item.get("price", 0)
                sid   = item.get("shop_id", iid)
                desc  = item.get("desc","")
                tier      = item.get("tier")
                tier_icon = item.get("tier_emoji","")
                stats = []
                if item.get("atk"):        stats.append(f"⚔️+{fmt(item['atk'])}")
                if item.get("def_"):       stats.append(f"🛡️+{fmt(item['def_'])}")
                if item.get("hp"):         stats.append(f"❤️+{fmt(item['hp'])}" if item["hp"]>0 else f"❤️{fmt(item['hp'])}")
                if item.get("spd"):        stats.append(f"⚡+{fmt(item['spd'])}")
                if item.get("crit_bonus"): stats.append(f"💥+{item['crit_bonus']*100:.0f}%")
                if item.get("life_steal"): stats.append(f"🩸+{item['life_steal']*100:.0f}%")
                if item.get("ignore_def"): stats.append(f"🗡️+{item['ignore_def']*100:.0f}%")
                if item.get("luck_pct"):   stats.append(f"🔰+{item['luck_pct']*100:.0f}%")
                if item.get("exp_pct"):    stats.append(f"⭐+{item['exp_pct']*100:.0f}%")
                stat_str  = f"[{', '.join(stats)}]" if stats else ""
                tier_str  = f"{tier_icon} **{tier}** " if tier else ""
                embed.add_field(
                    name=f"🆔 [{sid}] {item['name']} {stat_str}",
                    value=(
                        f"{tier_str}💰 **{price:,} LT**\n"
                        + (f"_{desc}_" if desc else "")
                    ),
                    inline=False
                )

        footer = f"Trang {page}/{total_pages}"
        if page < total_pages:
            footer += f" | Xem tiếp: ,tl shop {category} {page+1}"
        footer += "\n💡 Mua: ,tl buy [item_id] [Số lượng]"
        embed.set_footer(text=footer)
        await ctx.send(embed=embed)

    # ══ BUY ═════════════════════════════════════════════════
    @commands.command(name="buy", aliases=["mua"])
    async def buy(self, ctx, item_id: str, quantity: int = 1):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        item_id = item_id.lower()
        item = ITEMS.get(item_id)
        if not item:
            # Không khớp key nội bộ -> thử khớp theo shop_id hiển thị trong ,tl shop
            for iid, data in ITEMS.items():
                sid = data.get("shop_id")
                if sid is not None and str(sid).lower() == item_id:
                    item_id, item = iid, data
                    break
        if not item:
            await ctx.send(embed=error(f"Không tìm thấy vật phẩm `{item_id}`!\nGõ `,tl shop` để xem danh sách."))
            return
        price = item.get("price", 0)
        if price == 0:
            await ctx.send(embed=warn("Vật phẩm này không bán ở cửa hàng!"))
            return
        quantity = max(1, min(quantity, 10**21))
        total = price * quantity

        ha  = int(player.get("linh_thach_ha",  0))
        trg = int(player.get("linh_thach_trung", 0))
        cuc = int(player.get("linh_thach_cuc",  0))
        tong_ha = ha + trg * 10_000 + cuc * 100_000_000

        if tong_ha < total:
            await ctx.send(embed=error(
                f"Không đủ Linh Thạch!\n"
                f"Cần: **{total:,} Hạ** | Tổng có: **{tong_ha:,} Hạ**"
            ))
            return

        doi_trung = 0; doi_cuc = 0
        note_doi = ""
        if ha < total:
            # Thiếu bao nhiêu thì đổi Cực/Trung xuống Hạ
            can_them = total - ha
            # Đổi Trung trước (1 Trung = 10.000 Hạ)
            if trg > 0 and can_them > 0:
                so_trung = min(trg, (can_them + 9_999) // 10_000)
                doi_trung = so_trung
                ha  += so_trung * 10_000
                trg -= so_trung
                can_them = max(0, total - ha)
            # Đổi Cực nếu vẫn còn thiếu (1 Cực = 100.000.000 Hạ)
            if cuc > 0 and can_them > 0:
                so_cuc = min(cuc, (can_them + 99_999_999) // 100_000_000)
                doi_cuc = so_cuc
                ha  += so_cuc * 100_000_000
                cuc -= so_cuc
            if doi_trung or doi_cuc:
                parts = []
                if doi_cuc:   parts.append(f"**{doi_cuc:,}** Cực Phẩm")
                if doi_trung: parts.append(f"**{doi_trung:,}** Trung Phẩm")
                note_doi = f"🔄 Tự đổi {' + '.join(parts)} → Hạ Phẩm"

        new_ha  = ha  - total
        new_trg = trg
        new_cuc = cuc

        await self.bot.db.add_item(ctx.author.id, item_id, quantity)
        await self.bot.db.update_player(ctx.author.id,
            linh_thach_ha=new_ha,
            linh_thach_trung=new_trg,
            linh_thach_cuc=new_cuc,
        )

        desc = f"🛒 **{quantity}x {item['name']}**\n💰 Đã trả: **{total:,} Hạ LT**"
        if note_doi:
            desc += f"\n{note_doi}"
        embed = success("✅ MUA THÀNH CÔNG", desc)
        embed.add_field(name="👛 Số Dư", value=f"{new_ha:,} Hạ", inline=True)
        await ctx.send(embed=embed)

    # ══ USE ══════════════════════════════════════════════════
    @commands.command(name="use", aliases=["dung","su_dung"])
    async def use(self, ctx, item_id: str, quantity: int = 1):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        item_id = item_id.lower()
        item = ITEMS.get(item_id)
        if not item:
            for iid, data in ITEMS.items():
                sid = data.get("shop_id")
                if sid is not None and str(sid).lower() == item_id:
                    item_id, item = iid, data
                    break
        if not item:
            await ctx.send(embed=error(f"Không tìm thấy `{item_id}`!"))
            return
        have = await self.bot.db.get_item_count(ctx.author.id, item_id)
        if have < quantity:
            await ctx.send(embed=error(f"Không đủ! Có **{have}x**, cần **{quantity}x**"))
            return

        results = []
        updates = {}
        new_buffs = []  # list of (buff_type, value, duration, source) để ghi vào bảng buffs

        itype = item["type"]
        if itype == "dan_duoc":
            dao = player.get("dao", "")

            # Vật phẩm giới hạn theo Dao Tâm (vd: Hàu Sữa Đại Bổ chỉ dành cho Lọ Đạo)
            restrict = item.get("dao_restrict")
            if restrict and dao != restrict:
                req_name = DAO.get(restrict, {}).get("name", restrict)
                await ctx.send(embed=warn(f"Vật phẩm này chỉ dùng được cho **{req_name}**!"))
                return

            # ── EXP / Tu Vi (có override theo Dao Tâm) ──
            exp_gain = item.get("exp", 0) * quantity
            dao_bonus = item.get("dao_bonus", {})
            if dao in dao_bonus and isinstance(dao_bonus[dao], (int, float)):
                exp_gain = dao_bonus[dao] * quantity
            if exp_gain:
                updates["exp"] = min(player["exp"] + exp_gain, 999_999_999_999_999)
                results.append(f"✨ +**{fmt(exp_gain)}** Tu Vi")

            # ── Thể Lực ──
            if item.get("stamina"):
                gained = item["stamina"] * quantity
                cur_s = updates.get("stamina", player["stamina"])
                new_s = min(cur_s + gained, player["stamina_max"])
                updates["stamina"] = new_s
                results.append(f"🔋 +**{gained}** Thể Lực (`{new_s}/{player['stamina_max']}`)")

            # ── Hồi HP ──
            if item.get("hp_restore_pct"):
                pct = item["hp_restore_pct"]
                hp_max = updates.get("hp_max", player.get("hp_max", 1000))
                updates["hp"] = hp_max * min(pct, 1.0)
                results.append(f"❤️ Hồi **{pct*100:.0f}% HP** (`{fmt(updates['hp'])}/{fmt(hp_max)}`)")

            # ── Tăng HP Max (buff, mặc định 1 ngày nếu không ghi duration) ──
            if item.get("hp_max_bonus_pct"):
                pct = item["hp_max_bonus_pct"]
                dur = item.get("duration") or 86400
                new_buffs.append(("hp_max", pct*100, dur, item_id))
                results.append(f"❤️ HP Tối Đa +**{pct*100:.0f}%** trong `{fmt_time(dur)}`")

            # ── Ngộ Tính (random range, cộng trực tiếp) ──
            if item.get("ngo_tinh_bonus"):
                lo, hi = item["ngo_tinh_bonus"]
                gained = random.randint(lo, hi)
                new_nt = _safe(player, "ngo_tinh", 50) + gained
                updates["ngo_tinh"] = new_nt
                results.append(f"🧠 Ngộ Tính +**{gained}** (`{new_nt}`)")

            # ── Phúc Duyên / Luck tạm thời ──
            if item.get("luck_bonus"):
                dur = item.get("duration") or 3600
                new_buffs.append(("luck", item["luck_bonus"], dur, item_id))
                results.append(f"🍀 Vận Mệnh +**{item['luck_bonus']}** trong `{fmt_time(dur)}`")

            # ── Đột Phá ──
            if item.get("breakthrough"):
                dur = item.get("duration") or 1800
                new_buffs.append(("breakthrough", item["breakthrough"]*100, dur, item_id))
                results.append(f"🚀 Đột Phá Đan: +**{item['breakthrough']*100:.0f}%** tỉ lệ thành công trong `{fmt_time(dur)}`")

            # ── EXP Rate (tăng % tu luyện) ──
            if item.get("exp_rate_bonus"):
                dur = item.get("duration") or 1800
                new_buffs.append(("exp_rate", item["exp_rate_bonus"]*100, dur, item_id))
                tag = "lần tới" if item.get("next_session") else f"`{fmt_time(dur)}`"
                results.append(f"⚡ EXP +**{item['exp_rate_bonus']*100:.0f}%** ({tag})")

            # ── Tốc Độ (SPD) tạm thời ──
            if item.get("spd_bonus_pct"):
                dur = item.get("duration") or 1800
                new_buffs.append(("spd", item["spd_bonus_pct"]*100, dur, item_id))
                results.append(f"💨 SPD +**{item['spd_bonus_pct']*100:.0f}%** trong `{fmt_time(dur)}`")
            if item.get("spd_penalty_pct"):
                dur = item.get("duration") or 1800
                new_buffs.append(("spd_penalty", item["spd_penalty_pct"]*100, dur, item_id))
                results.append(f"💨 SPD -**{item['spd_penalty_pct']*100:.0f}%** trong `{fmt_time(dur)}`")

            # ── Sức Công (ATK) tạm thời ──
            if item.get("atk_bonus_pct"):
                dur = item.get("duration") or 1800
                new_buffs.append(("atk", item["atk_bonus_pct"]*100, dur, item_id))
                results.append(f"⚔️ ATK +**{item['atk_bonus_pct']*100:.0f}%** trong `{fmt_time(dur)}`")

            # ── Phòng Ngự (DEF) tạm thời ──
            if item.get("def_bonus_pct"):
                dur = item.get("duration") or 1800
                new_buffs.append(("def", item["def_bonus_pct"]*100, dur, item_id))
                results.append(f"🛡️ DEF +**{item['def_bonus_pct']*100:.0f}%** trong `{fmt_time(dur)}`")
            if item.get("def_penalty_pct"):
                dur = item.get("duration") or 1800
                new_buffs.append(("def_penalty", item["def_penalty_pct"]*100, dur, item_id))
                results.append(f"🛡️ DEF -**{item['def_penalty_pct']*100:.0f}%** trong `{fmt_time(dur)}`")

            # ── HP % tạm thời (buff cộng thêm, khác hồi máu) ──
            if item.get("hp_bonus_pct"):
                dur = item.get("duration") or 3600
                new_buffs.append(("hp", item["hp_bonus_pct"]*100, dur, item_id))
                results.append(f"❤️ HP +**{item['hp_bonus_pct']*100:.0f}%** trong `{fmt_time(dur)}`")

            # ── Giảm sát thương lần thám hiểm tới ──
            if item.get("dmg_reduce_next"):
                dur = item.get("duration") or 1800
                new_buffs.append(("dmg_reduce", item["dmg_reduce_next"]*100, dur, item_id))
                results.append(f"🔰 Giảm **{item['dmg_reduce_next']*100:.0f}%** sát thương (lần thám hiểm tới)")

            # ── Giới hạn sát thương nhận mỗi đòn (Tháp) ──
            if item.get("dmg_cap_pct"):
                dur = item.get("duration") or 3600
                new_buffs.append(("dmg_cap", item["dmg_cap_pct"]*100, dur, item_id))
                results.append(f"🛡️ Giới hạn sát thương mỗi đòn ở **{item['dmg_cap_pct']*100:.0f}%** HP trong `{fmt_time(dur)}`")

            # ── Sát thương tối thiểu mỗi hiệp (Tháp) ──
            if item.get("min_dmg_pct"):
                dur = item.get("duration") or 1800
                new_buffs.append(("min_dmg", item["min_dmg_pct"]*100, dur, item_id))
                results.append(f"💥 Sát thương tối thiểu **{item['min_dmg_pct']*100:.2f}%** HP Boss/hiệp trong `{fmt_time(dur)}`")

            # ── Giảm sức mạnh Boss Tháp ──
            if item.get("boss_scale_reduce"):
                dur = item.get("duration") or 3600
                new_buffs.append(("boss_scale", item["boss_scale_reduce"]*100, dur, item_id))
                results.append(f"⬇️ Giảm **{item['boss_scale_reduce']*100:.0f}%** sức mạnh Boss Tháp trong `{fmt_time(dur)}`")

            # ── Tỷ lệ rơi vật phẩm ──
            if item.get("drop_rate_bonus"):
                dur = item.get("duration") or 1800
                new_buffs.append(("drop_rate", item["drop_rate_bonus"]*100, dur, item_id))
                tag = "lần tới" if item.get("next_session") else f"`{fmt_time(dur)}`"
                results.append(f"🎁 Tỷ lệ rơi đồ +**{item['drop_rate_bonus']*100:.0f}%** ({tag})")

            # ── Tốc độ thám hiểm ──
            if item.get("explore_speed"):
                dur = item.get("duration") or 1800
                new_buffs.append(("explore_speed", item["explore_speed"], dur, item_id))
                results.append(f"🗺️ Tốc độ thám hiểm x**{item['explore_speed']}** trong `{fmt_time(dur)}`")

            # ── Hút Boss / sự kiện đặc biệt ──
            if item.get("boss_attract"):
                dur = item.get("duration") or 1800
                new_buffs.append(("boss_attract", 1, dur, item_id))
                results.append(f"👹 Tăng tỷ lệ gặp Boss & sự kiện đặc biệt trong `{fmt_time(dur)}`")

            # ── Giảm rủi ro tẩu hỏa ──
            if item.get("risk_reduce"):
                dur = item.get("duration") or 1800
                new_buffs.append(("risk_reduce", item["risk_reduce"]*100, dur, item_id))
                results.append(f"🧘 Giảm **{item['risk_reduce']*100:.0f}%** rủi ro tẩu hỏa trong `{fmt_time(dur)}`")

            # ── Tăng giới hạn thời gian tu luyện trong ngày ──
            if item.get("cultivate_time_bonus"):
                dur = item.get("duration") or 86400
                new_buffs.append(("cultivate_time", item["cultivate_time_bonus"], dur, item_id))
                results.append(f"⏰ Giới hạn tu luyện +**{fmt_time(item['cultivate_time_bonus'])}** trong `{fmt_time(dur)}`")

            # ── Cược: thắng thêm / hoàn trả thua ──
            if item.get("gamble_bonus"):
                rounds = item.get("next_rounds", 5)
                new_buffs.append(("gamble_bonus", item["gamble_bonus"]*100, 3600, f"{item_id}:{rounds}"))
                results.append(f"🎲 Tiền thắng cược +**{item['gamble_bonus']*100:.0f}%** trong **{rounds}** ván tới")
            if item.get("gamble_refund"):
                rounds = item.get("next_rounds", 5)
                new_buffs.append(("gamble_refund", item["gamble_refund"]*100, 3600, f"{item_id}:{rounds}"))
                results.append(f"🎲 Hoàn **{item['gamble_refund']*100:.0f}%** tiền thua cược trong **{rounds}** ván tới")

            # ── Giảm điểm PK (nghiệp chướng) ──
            if item.get("pk_reduce"):
                cur_pk = _safe(player, "pk_point", 0)
                new_pk = max(0, cur_pk - item["pk_reduce"]*quantity)
                updates["pk_point"] = new_pk
                results.append(f"☮️ Giảm **{item['pk_reduce']*quantity}** điểm PK (`{new_pk}`)")

            # ── Tẩy Tủy: random lại Linh Căn, Thể Chất, Huyết Mạch ──
            if item.get("reroll"):
                from utils.game_data import (
                    LINH_CAN, THE_CHAT, HUYET_MACH, gacha, RARITY_EMOJI,
                    scale_stats_for_realm_change,
                )
                for key, pool, label in (("linh_can", LINH_CAN, "Linh Căn"),
                                          ("the_chat", THE_CHAT, "Thể Chất"),
                                          ("huyet_mach", HUYET_MACH, "Huyết Mạch")):
                    res = gacha(pool)
                    updates[key] = res["name"]
                    icon = RARITY_EMOJI.get(res.get("rarity","common"), "✨")
                    results.append(f"{icon} {label} mới: **{res['name']}**")

                # Đồng bộ lại atk/def/hp/spd/lực chiến theo tư chất mới
                # ngay lập tức (giữ nguyên cảnh giới hiện tại), để ,tl i
                # luôn hiển thị đúng — không cần đột phá lại mới thấy đổi.
                _scaled_player = {**player, **updates}
                _scaled = scale_stats_for_realm_change(
                    _scaled_player,
                    player.get("realm_index", 0),
                    player.get("realm_tier", 1),
                )["new"]
                updates["atk"]        = _scaled["atk"]
                updates["def_"]       = _scaled["def_"]
                updates["hp_max"]     = _scaled["hp_max"]
                updates["hp"]         = _scaled["hp_max"]
                updates["spd"]        = _scaled["spd"]
                updates["luc_chien"]  = _scaled["luc_chien"]
                results.append(
                    f"📊 Chỉ số đã đồng bộ lại: ⚔️ATK `{fmt(_scaled['atk'])}` · "
                    f"🛡️DEF `{fmt(_scaled['def_'])}` · ❤️HP `{fmt(_scaled['hp_max'])}` · "
                    f"⚡SPD `{fmt(_scaled['spd'])}` · 🔥Lực Chiến `{fmt(_scaled['luc_chien'])}`"
                )

            # ── Hình phạt theo Dao Tâm (vd: trừ % HP hiện tại) ──
            penalty_map = item.get("dao_penalty", {})
            if dao in penalty_map:
                penalty = penalty_map[dao]
                if isinstance(penalty, str) and penalty.startswith("hp") and penalty.endswith("pct"):
                    try:
                        pct = int(penalty[2:-3]) / 100
                        cur_hp = updates.get("hp", player.get("hp", player.get("hp_max", 1000)))
                        updates["hp"] = max(0, cur_hp * (1 - pct))
                        results.append(f"💢 Mất **{pct*100:.0f}%** HP hiện tại do tương khắc Dao Tâm")
                    except (ValueError, IndexError):
                        pass

            # ── Giảm thời gian bị thương nếu tẩu hỏa ──
            if item.get("tau_hoa_reduce"):
                dur = item.get("duration") or 86400
                new_buffs.append(("tau_hoa_reduce", item["tau_hoa_reduce"]*100, dur, item_id))
                results.append(f"🩹 Giảm **{item['tau_hoa_reduce']*100:.0f}%** thời gian bị thương nếu tẩu hỏa trong `{fmt_time(dur)}`")

            if not results:
                results.append("_Đan dược này hiện chưa có hiệu ứng được lập trình. Báo Admin để được hỗ trợ!_")

        elif itype == "bi_kip":
            # ── Kiểm tra đã học chưa ──
            # Sau khi học, bi_kip KHÔNG bị xóa khỏi túi → count >= 1 = đã học rồi
            # Người chơi chỉ học được khi vừa mua (count = 1 và chưa dùng)
            # Ta lưu trạng thái "đã học" = item vẫn còn trong túi với tag learned
            # Cách đơn giản: kiểm tra bảng buffs/player xem đã có effect chưa
            # → Dùng cách đơn giản nhất: item bi_kip không xóa sau học,
            #   nên khi use lần 2 (count vẫn = 1) thì đây là "đã học rồi"
            # Để phân biệt "mới mua" vs "đã học": dùng quantity=0 trick —
            # Ta sẽ lưu vào bảng bot_cache key "learned_{user}_{item}" sau khi học
            # Kiểm tra đã học chưa qua bot_cache (namespace="bikip_learned", data=JSON dict uid->set)
            import json as _json
            _bk_ns = "bikip_learned"
            _bk_row = await self.bot.db.fetchone(
                "SELECT data FROM bot_cache WHERE namespace=?", (_bk_ns,)
            )
            _bk_data = _json.loads(_bk_row["data"]) if _bk_row else {}
            _uid_str = str(ctx.author.id)
            _learned_set = _bk_data.get(_uid_str, [])
            if item_id in _learned_set:
                await ctx.send(embed=warn(f"Đã học **{item['name']}** rồi! Passive đang được áp dụng."))
                return
            have_bk = await self.bot.db.get_item_count(ctx.author.id, item_id)
            if have_bk < 1:
                await ctx.send(embed=error(f"Không có **{item['name']}** trong túi!"))
                return

            # ── Kiểm tra yêu cầu (requires) ──
            req_id = item.get("requires")
            if req_id:
                req_have = await self.bot.db.get_item_count(ctx.author.id, req_id)
                if not req_have:
                    req_item = ITEMS.get(req_id, {})
                    req_name = req_item.get("name", req_id)
                    await ctx.send(embed=error(f"Cần học **{req_name}** trước!"))
                    return

            dao = player.get("dao", "")

            # ── Tăng Stamina Max ngay (flat) ──
            if item.get("stamina_max_flat"):
                val = item["stamina_max_flat"]
                new_smax = _safe(player, "stamina_max", 100) + val
                updates["stamina_max"] = new_smax
                results.append(f"🔋 Thể Lực Tối Đa +**{val}** → `{new_smax}`")

            # ── Tăng Ngộ Tính ngay (flat) ──
            if item.get("ngo_tinh_flat"):
                val = item["ngo_tinh_flat"]
                new_nt = _safe(player, "ngo_tinh", 50) + val
                updates["ngo_tinh"] = new_nt
                results.append(f"🧠 Ngộ Tính +**{val}** → `{new_nt}`")

            # ── Cultivate time bonus (buff) ──
            if item.get("cultivate_time_bonus"):
                dur = 86400
                new_buffs.append(("cultivate_time", item["cultivate_time_bonus"], dur, item_id))
                results.append(f"⏰ Giới hạn tu luyện +**30 phút**/ngày (kích hoạt)")

            # ── Passive EXP Rate ──
            if item.get("passive_exp_rate"):
                pct = item["passive_exp_rate"]
                dur = 86400 * 3650  # 10 năm ~ vĩnh viễn
                new_buffs.append(("exp_rate", pct * 100, dur, item_id))
                results.append(f"⚡ Tốc độ tu luyện +**{pct*100:.0f}%** (Passive vĩnh viễn)")

            # ── Passive DMG Reduce ──
            if item.get("passive_dmg_reduce"):
                pct = item["passive_dmg_reduce"]
                dur = 86400 * 3650
                new_buffs.append(("dmg_reduce", pct * 100, dur, item_id))
                results.append(f"🛡️ Giảm **{pct*100:.0f}%** sát thương khi thám hiểm (Passive vĩnh viễn)")

            # ── Passive theo Dao Tâm ──
            if item.get("passive_dao"):
                pd = item["passive_dao"]
                dao_effects = pd.get(dao) or pd.get("_other")
                dao_from = DAO.get(dao, {})
                dao_name = dao_from.get("name", dao)
                if dao_effects:
                    if dao_effects.get("self_destruct"):
                        results.append(f"💥 Công pháp **TỰ HỦY** — không tương thích với {dao_name}!")
                        # Không áp hiệu ứng, ghi log
                    else:
                        dur = 86400 * 3650
                        effect_descs = []
                        for eff_key, eff_val in dao_effects.items():
                            if eff_key == "spd":
                                new_buffs.append(("spd", eff_val * 100, dur, item_id))
                                effect_descs.append(f"⚡ SPD {'+' if eff_val>0 else ''}{eff_val*100:.0f}%")
                            elif eff_key == "hp":
                                new_buffs.append(("hp", eff_val * 100, dur, item_id))
                                effect_descs.append(f"❤️ HP {'+' if eff_val>0 else ''}{eff_val*100:.0f}%")
                            elif eff_key == "def":
                                new_buffs.append(("def", eff_val * 100, dur, item_id))
                                effect_descs.append(f"🛡️ DEF {'+' if eff_val>0 else ''}{eff_val*100:.0f}%")
                            elif eff_key == "crit":
                                new_buffs.append(("crit_pct", eff_val * 100, dur, item_id))
                                effect_descs.append(f"💥 Bạo kích {'+' if eff_val>0 else ''}{eff_val*100:.0f}%")
                            elif eff_key == "luck":
                                cur_luck = _safe(player, "luck", 0)
                                updates["luck"] = cur_luck + eff_val
                                effect_descs.append(f"🍀 Phúc Duyên {'+' if eff_val>0 else ''}{eff_val}")
                            elif eff_key == "drop_rate":
                                new_buffs.append(("drop_rate", eff_val * 100, dur, item_id))
                                effect_descs.append(f"🎁 Tỷ lệ rơi đồ +{eff_val*100:.0f}%")
                            elif eff_key == "risk_reduce":
                                new_buffs.append(("risk_reduce", eff_val * 100, dur, item_id))
                                effect_descs.append(f"🧘 Giảm {eff_val*100:.0f}% rủi ro")
                            elif eff_key == "risk_add":
                                new_buffs.append(("risk_add", eff_val * 100, dur, item_id))
                                effect_descs.append(f"⚠️ Tăng {eff_val*100:.0f}% rủi ro")
                            elif eff_key == "reflect":
                                new_buffs.append(("reflect", eff_val * 100, dur, item_id))
                                effect_descs.append(f"↩️ Phản sát thương +{eff_val*100:.0f}%")
                            elif eff_key == "dmg_reduce":
                                new_buffs.append(("dmg_reduce", eff_val * 100, dur, item_id))
                                effect_descs.append(f"🛡️ Giảm thương +{eff_val*100:.0f}%")
                        results.append(f"🌟 [{dao_name}] Passive: " + " | ".join(effect_descs))
                else:
                    results.append(f"📜 Bí kíp học thành công — hiệu ứng Passive đã ghi nhớ.")

            if not results:
                results.append(f"📜 Đã học **{item['name']}**! Passive sẽ áp dụng trong các trận chiến.")

            # Lưu trạng thái đã học vào bot_cache (namespace bikip_learned)
            _learned_set.append(item_id)
            _bk_data[_uid_str] = _learned_set
            import time as _time
            await self.bot.db.execute(
                "INSERT OR REPLACE INTO bot_cache(namespace, data, updated_at) VALUES(?,?,?)",
                (_bk_ns, _json.dumps(_bk_data), int(_time.time()))
            )
            quantity = 0  # KHÔNG xóa bi_kip khỏi túi — item tồn tại = đã học

        elif itype == "ruong":
            loot = await self._open_chest(ctx.author.id, item.get("loot","bac"), quantity)
            results.extend(loot)

        elif itype == "linhthu_egg":
            existing = await self.bot.db.get_linhthu(ctx.author.id)
            if existing:
                await ctx.send(embed=warn("Đã có Linh Thú rồi! Không thể ấp thêm trứng."))
                return
            thu_type = item.get("thu_type","wolf")
            from utils.game_data import LINHTHU_DATA
            lt_data = LINHTHU_DATA.get(thu_type, {})
            name = lt_data.get("name","Linh Thú")
            await self.bot.db.execute(
                "INSERT OR IGNORE INTO linhthu(user_id,thu_type,name) VALUES(?,?,?)",
                (str(ctx.author.id), thu_type, name)
            )
            results.append(f"🐾 Đã ấp trứng! **{name}** đã chào đời!")
            quantity = 1

        if updates:
            await self.bot.db.update_player(ctx.author.id, **updates)
        for buff_type, value, duration, source in new_buffs:
            await self.bot.db.execute(
                "INSERT INTO buffs(user_id, buff_type, value, expires_at, source) VALUES(?,?,?,?,?)",
                (str(ctx.author.id), buff_type, value, now() + duration, source)
            )
        await self.bot.db.remove_item(ctx.author.id, item_id, quantity)

        embed = discord.Embed(
            title=f"✅ ĐÃ DÙNG {quantity}x {item['name']}",
            description="\n".join(results) if results else "_Không có hiệu ứng_",
            color=0x4CAF50
        )
        await ctx.send(embed=embed)

    async def _open_chest(self, uid, loot_key, qty) -> list:
        pool = LOOT_TABLES.get(loot_key, LOOT_TABLES["bac"])
        results = []
        totals = {}
        for _ in range(qty):
            for (iid, amt, chance) in pool:
                if random.random() < chance:
                    totals[iid] = totals.get(iid, 0) + amt
        for iid, total_amt in totals.items():
            await self.bot.db.add_item(uid, iid, total_amt)
            iname = ITEMS.get(iid, {}).get("name", iid)
            results.append(f"🎁 +**{total_amt}x** {iname}")
        return results or ["_Rương trống..._"]

    # ══ BAG ══════════════════════════════════════════════════
    @commands.command(name="bag", aliases=["tui","inventory","inv","b"])
    async def bag(self, ctx, page: int = 1):
        import datetime
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=error("Chưa nhập môn! Dùng `,tl nhapdao`.")); return

        inv_list = await self.bot.db.get_inventory(ctx.author.id)
        inv_list = [i for i in inv_list if i["quantity"] > 0]

        ITEMS_PER_PAGE = 10
        total_pages = max(1, (len(inv_list) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)
        page = max(1, min(page, total_pages))
        start_idx = (page - 1) * ITEMS_PER_PAGE
        page_items = inv_list[start_idx:start_idx + ITEMS_PER_PAGE]

        TYPE_ICON = {
            "dan_duoc":"💊","vukhi":"⚔️","giap":"🛡️","phap_bao":"🔮","rune":"💎",
            "ngoc":"💎","nguyen_lieu":"🌿","ruong":"🎁","linhthu_egg":"🥚","mu":"🪖",
            "vongco":"📿","gangtay":"🧤","giay":"👟","currency":"💰","temp_buff":"✨",
            "dual_effect":"📦","tower_buff":"✨","tower_pill_30":"💊","special":"⭐",
        }

        # Tính tổng LT
        ha  = int(player.get("linh_thach_ha", 0))
        trg = int(player.get("linh_thach_trung", 0))
        cuc = int(player.get("linh_thach_cuc", 0))
        tong = ha + trg * 10000 + cuc * 100000000

        lt_str = (
            f"👑 **Cực Phẩm LT:** {cuc:,}\n"
            f"💎 **Trung Phẩm LT:** {trg:,}\n"
            f"💚 **Hạ Phẩm LT:** {ha:,}\n"
            f"⭐ **Tổng cộng:** {tong/1e6:.1f} Triệu"
        ) if cuc or trg else f"💚 **Hạ Phẩm LT:** {ha:,}"

        embed = discord.Embed(
            title=f"🛍️ TÚI ĐỒ CỦA ĐẠO HỮU",
            color=0xFFD700
        )
        embed.add_field(name="💰 Tài sản hiện có:", value=lt_str, inline=False)
        embed.add_field(name="\u200b", value="─"*28, inline=False)

        if not page_items:
            embed.add_field(name="📭 Vật phẩm trong túi", value="_Trống rỗng — Mua đồ tại `,tl shop`_", inline=False)
        else:
            lines = []
            for inv in page_items:
                iid  = inv["item_id"]
                item = ITEMS.get(iid, {})
                icon = TYPE_ICON.get(item.get("type",""), "📦")
                name = item.get("name", iid)
                itype = item.get("type", "unknown")
                lines.append(
                    f"{icon} **{name}** (x{inv['quantity']})\n"
                    f"└ ID: `{iid}` | *{itype}*"
                )
            embed.add_field(
                name=f"🎒 Vật phẩm trong túi",
                value="\n".join(lines),
                inline=False
            )

        now_str = datetime.datetime.now().strftime("%H:%M")
        embed.set_footer(text=f"Trang {page}/{total_pages}  •  Tổng số: {len(inv_list)} vật phẩm  •  Hôm nay lúc {now_str}")
        await ctx.send(embed=embed)

    # ══ TRACUU ═══════════════════════════════════════════════
    @commands.command(name="tracuu_shop", aliases=["shopinfo"])
    async def tracuu(self, ctx, item_id: str):
        item_id = item_id.lower()
        item = ITEMS.get(item_id)
        if not item:
            await ctx.send(embed=error(f"Không tìm thấy `{item_id}`!"))
            return
        TYPE_ICON = {"dan_duoc":"💊","vukhi":"⚔️","giap":"🛡️","phap_bao":"🔮","ngoc":"💎",
                     "nguyen_lieu":"🌿","ruong":"🎁","linhthu_egg":"🥚"}
        icon = TYPE_ICON.get(item["type"], "📦")
        embed = discord.Embed(title=f"{icon} {item['name']}", color=0x607D8B)
        embed.add_field(name="🆔 ID",    value=f"`{item_id}`",          inline=True)
        embed.add_field(name="📦 Loại",  value=item.get("type","?"),    inline=True)
        price = item.get("price", 0)
        embed.add_field(name="💰 Giá",   value=f"{price:,} Hạ" if price else "Không bán", inline=True)
        effects = []
        if item.get("exp"):         effects.append(f"✨ +{fmt(item['exp'])} EXP")
        if item.get("stamina"):     effects.append(f"🔋 +{item['stamina']} Thể Lực")
        if item.get("breakthrough"):effects.append(f"🚀 +{item['breakthrough']*100:.0f}% ĐP rate")
        if item.get("atk"):         effects.append(f"⚔️ ATK +{fmt(item['atk'])}")
        elif item.get("base_atk"):  effects.append(f"⚔️ ATK +{fmt(item['base_atk'])}")
        if item.get("def_"):        effects.append(f"🛡️ DEF +{fmt(item['def_'])}")
        elif item.get("base_def"):  effects.append(f"🛡️ DEF +{fmt(item['base_def'])}")
        if item.get("spd"):         effects.append(f"⚡ SPD +{fmt(item['spd'])}")
        if item.get("crit_bonus"):  effects.append(f"💥 Crit +{item['crit_bonus']*100:.0f}%")
        if item.get("life_steal"):  effects.append(f"🩸 Hút Máu +{item['life_steal']*100:.0f}%")
        if item.get("ignore_def"):  effects.append(f"🗡️ Phá Giáp +{item['ignore_def']*100:.0f}%")
        if item.get("tier"):        effects.append(f"{item.get('tier_emoji','')} Cấp: **{item['tier']}**")
        if item.get("slot"):        effects.append(f"🎽 Slot: {item['slot']}")
        if effects:
            embed.add_field(name="✨ Hiệu Ứng", value="\n".join(effects), inline=False)
        await ctx.send(embed=embed)

    # ══ ĐỔI LINH THẠCH ══════════════════════════════════════
    @commands.command(name="doi", aliases=["exchange","quy_doi"])
    async def doi(self, ctx, tier: str, amount_str: str = "1"):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        tier = tier.lower()
        ha=player["linh_thach_ha"]; trung=player["linh_thach_trung"]; cuc=player["linh_thach_cuc"]

        def parse_amt(s, max_val):
            return max_val if s == "all" else min(int(s), max_val)

        if tier in ("ha","h"):
            max_q = ha // 1000
            qty = parse_amt(amount_str, max_q)
            if qty == 0:
                await ctx.send(embed=warn("Cần ít nhất **1,000 Hạ** để đổi 1 Trung!"))
                return
            await self.bot.db.update_player(ctx.author.id,
                linh_thach_ha=ha-qty*1000, linh_thach_trung=trung+qty)
            await ctx.send(embed=success("💱 QUY ĐỔI",f"💰 -{qty*1000:,} Hạ  →  💎 +{qty:,} Trung Phẩm LT"))

        elif tier in ("trung","t"):
            max_q = trung // 1000
            qty = parse_amt(amount_str, max_q)
            if qty == 0:
                await ctx.send(embed=warn("Cần ít nhất **1,000 Trung** để đổi 1 Cực!"))
                return
            await self.bot.db.update_player(ctx.author.id,
                linh_thach_trung=trung-qty*1000, linh_thach_cuc=cuc+qty)
            await ctx.send(embed=success("💱 QUY ĐỔI",f"💎 -{qty*1000:,} Trung  →  👑 +{qty:,} Cực Phẩm LT"))

        elif tier in ("cuc","c"):
            qty = parse_amt(amount_str, cuc)
            if qty == 0:
                await ctx.send(embed=warn("Không có Cực Phẩm để đổi!"))
                return
            await self.bot.db.update_player(ctx.author.id,
                linh_thach_cuc=cuc-qty, linh_thach_trung=trung+qty*1000)
            await ctx.send(embed=success("💱 QUY ĐỔI",f"👑 -{qty} Cực  →  💎 +{qty*1000:,} Trung Phẩm LT"))
        else:
            await ctx.send(embed=warn("Dùng: `,tl doi [ha/trung/cuc] [số/all]`"))

    # ══ ĐẤU GIÁ ══════════════════════════════════════════════
    @commands.group(name="daugia", aliases=["ag","auction"], invoke_without_command=True)
    async def daugia(self, ctx):
        embed = info("🏛️ CHỢ ĐẤU GIÁ THIÊN ĐẠO",
            "`,tl daugia list` — Xem chợ\n"
            "`,tl daugia ban [id] [sl] [giá]` — Rao bán\n"
            "`,tl daugia mua [#ID]` — Mua ngay\n"
            "`,tl daugia huy [#ID]` — Huỷ đơn của mình\n\n"
            f"📋 Phí rao: **{AUCTION_FEE*100:.0f}%** | Thuế: **{AUCTION_TAX*100:.0f}%** | Hạn: **{AUCTION_DAYS} ngày**"
        )
        await ctx.send(embed=embed)

    @daugia.command(name="list", aliases=["ls","xem"])
    async def daugia_list(self, ctx, page: int = 1):
        rows = await self.bot.db.fetchall(
            "SELECT * FROM auction WHERE status='active' ORDER BY listed_at DESC LIMIT 20"
        )
        embed = discord.Embed(title="🏛️ CHỢ ĐẤU GIÁ THIÊN ĐẠO", color=0xFF9800)
        if not rows:
            embed.description = "_Chưa có vật phẩm nào được rao bán._"
        else:
            for r in rows:
                item = ITEMS.get(r["item_id"], {})
                name = item.get("name", r["item_id"])
                embed.add_field(
                    name=f"#{r['id']} {name} ×{r['quantity']}",
                    value=f"💰 **{r['price']:,} Hạ/cái** | 👤 <@{r['seller_id']}>",
                    inline=False
                )
        embed.set_footer(text=f"Phí treo {AUCTION_FEE*100:.0f}% | Thuế {AUCTION_TAX*100:.0f}% | Trần x{PRICE_CAP}")
        await ctx.send(embed=embed)

    @daugia.command(name="ban", aliases=["sell","rao"])
    async def daugia_ban(self, ctx, item_id: str, quantity: int, price: int):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        item_id = item_id.lower()
        item = ITEMS.get(item_id)
        if not item:
            await ctx.send(embed=error(f"Không tìm thấy `{item_id}`!")); return
        base_price = item.get("price", 1)
        if price > base_price * PRICE_CAP:
            await ctx.send(embed=warn(f"Giá vượt trần! Max: **{base_price*PRICE_CAP:,} Hạ**")); return
        have = await self.bot.db.get_item_count(ctx.author.id, item_id)
        if have < quantity:
            await ctx.send(embed=error(f"Không đủ! Có **{have}x**")); return
        fee = int(price * quantity * AUCTION_FEE)
        if player["linh_thach_ha"] < fee:
            await ctx.send(embed=error(f"Cần **{fee:,} Hạ** để trả phí rao bán!")); return

        expires = int(time.time()) + AUCTION_DAYS * 86400
        await self.bot.db.execute(
            "INSERT INTO auction(seller_id,item_id,quantity,price,expires_at) VALUES(?,?,?,?,?)",
            (str(ctx.author.id), item_id, quantity, price, expires)
        )
        await self.bot.db.remove_item(ctx.author.id, item_id, quantity)
        await self.bot.db.update_player(ctx.author.id, linh_thach_ha=player["linh_thach_ha"]-fee)

        embed = success("✅ ĐÃ ĐĂNG BÁN",
            f"**{quantity}x {item['name']}** với giá **{price:,} Hạ/cái**\n"
            f"💸 Phí rao bán: -{fee:,} Hạ | Hạn: {AUCTION_DAYS} ngày"
        )
        await ctx.send(embed=embed)

    @daugia.command(name="mua", aliases=["buy_ag"])
    async def daugia_mua(self, ctx, auction_id: int):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return

        # Lock đơn hàng trước: dùng UPDATE để "giữ chỗ" atomic
        # Nếu 2 người mua cùng lúc, chỉ 1 UPDATE thành công (rowcount=1)
        changed = await self.bot.db.execute(
            "UPDATE auction SET status='pending' WHERE id=? AND status='active'",
            (auction_id,)
        )
        # Lấy row sau khi lock
        row = await self.bot.db.fetchone(
            "SELECT * FROM auction WHERE id=? AND status='pending'", (auction_id,)
        )
        if not row:
            await ctx.send(embed=error("Không tìm thấy đơn này hoặc đã được mua!")); return
        if row["seller_id"] == str(ctx.author.id):
            # Hoàn lại status nếu là đơn của mình
            await self.bot.db.execute(
                "UPDATE auction SET status='active' WHERE id=?", (auction_id,)
            )
            await ctx.send(embed=warn("Không thể mua đồ của chính mình!")); return

        total = row["price"] * row["quantity"]
        tax   = int(total * AUCTION_TAX)
        cost  = total + tax

        if player["linh_thach_ha"] < cost:
            # Hoàn lại status nếu không đủ tiền
            await self.bot.db.execute(
                "UPDATE auction SET status='active' WHERE id=?", (auction_id,)
            )
            await ctx.send(embed=error(f"Cần **{cost:,} Hạ** (thuế {tax:,}). Có: {player['linh_thach_ha']:,}")); return

        try:
            # Thực hiện giao dịch
            seller = await self.bot.db.get_player(row["seller_id"])
            if seller:
                await self.bot.db.update_player(row["seller_id"],
                    linh_thach_ha=seller["linh_thach_ha"] + total - tax)
            await self.bot.db.add_item(ctx.author.id, row["item_id"], row["quantity"])
            await self.bot.db.update_player(ctx.author.id, linh_thach_ha=player["linh_thach_ha"]-cost)
            await self.bot.db.execute("UPDATE auction SET status='sold' WHERE id=?", (auction_id,))
        except Exception as e:
            # Rollback: hoàn lại đơn về active nếu có lỗi giữa chừng
            await self.bot.db.execute(
                "UPDATE auction SET status='active' WHERE id=?", (auction_id,)
            )
            await ctx.send(embed=error(f"Lỗi giao dịch, đã hoàn lại đơn hàng: `{e}`")); return

        iname = ITEMS.get(row["item_id"], {}).get("name", row["item_id"])
        embed = success("✅ MUA THÀNH CÔNG",
            f"**{row['quantity']}x {iname}**\n💰 Đã trả: **{cost:,} Hạ** (thuế: {tax:,})"
        )
        await ctx.send(embed=embed)

    @daugia.command(name="huy", aliases=["cancel"])
    async def daugia_huy(self, ctx, auction_id: int):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        row = await self.bot.db.fetchone(
            "SELECT * FROM auction WHERE id=? AND status='active' AND seller_id=?",
            (auction_id, str(ctx.author.id))
        )
        if not row:
            await ctx.send(embed=error("Không tìm thấy đơn của bạn!")); return
        await self.bot.db.add_item(ctx.author.id, row["item_id"], row["quantity"])
        await self.bot.db.execute("UPDATE auction SET status='cancelled' WHERE id=?", (auction_id,))
        iname = ITEMS.get(row["item_id"], {}).get("name", row["item_id"])
        await ctx.send(embed=success("✅ HUỶ ĐƠN", f"Đã hoàn lại **{row['quantity']}x {iname}** vào túi đồ."))

    # ══ CHUYỂN LINH THẠCH ═══════════════════════════════════
    @commands.command(name="chuyenlt", aliases=["transferlt","clt"])
    async def chuyen_lt(self, ctx, target: discord.Member, loai: str, so_luong: int):
        """
        Chuyển linh thạch cho người khác.
        Dùng: ,tl chuyenlt @người [ha/trung/cuc] [số lượng]
        """
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        if target.id == ctx.author.id:
            await ctx.send(embed=warn("Không thể chuyển cho chính mình!")); return
        if so_luong <= 0:
            await ctx.send(embed=warn("Số lượng phải lớn hơn 0!")); return

        receiver = await self.bot.db.get_player(target.id)
        if not receiver:
            await ctx.send(embed=warn(f"**{target.display_name}** chưa nhập môn!")); return

        loai = loai.lower().strip()
        LOAI_MAP = {
            "ha": ("linh_thach_ha",  "💰 Hạ Phẩm"),
            "h":  ("linh_thach_ha",  "💰 Hạ Phẩm"),
            "trung": ("linh_thach_trung", "💎 Trung Phẩm"),
            "t":     ("linh_thach_trung", "💎 Trung Phẩm"),
            "cuc": ("linh_thach_cuc", "👑 Cực Phẩm"),
            "c":   ("linh_thach_cuc", "👑 Cực Phẩm"),
        }
        if loai not in LOAI_MAP:
            await ctx.send(embed=warn("Loại không hợp lệ!\nDùng: `ha` / `trung` / `cuc`")); return

        field, ten_loai = LOAI_MAP[loai]
        co = int(player.get(field, 0))
        if co < so_luong:
            await ctx.send(embed=error(
                f"Không đủ {ten_loai}!\nCần: **{so_luong:,}** | Có: **{co:,}**"
            )); return

        await self.bot.db.update_player(ctx.author.id, **{field: co - so_luong})
        await self.bot.db.update_player(target.id,    **{field: int(receiver.get(field, 0)) + so_luong})

        embed = success(
            "✅ CHUYỂN LINH THẠCH THÀNH CÔNG",
            f"**{player['name']}** → **{receiver['name']}**\n"
            f"{ten_loai}: **{so_luong:,}**"
        )
        embed.add_field(name="👛 Số Dư Của Bạn", value=f"{co - so_luong:,}", inline=True)
        embed.set_footer(text=",tl chuyenlt @người [ha/trung/cuc] [số]")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Economy(bot))

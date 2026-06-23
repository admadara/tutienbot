"""cogs/achievement.py v5 - Danh hiệu nâng cấp, bỏ lệnh thành tựu"""
import discord
from discord.ext import commands
from difflib import get_close_matches

from utils.helpers import require_player, now
from utils.embeds import *
from utils.game_data import get_realm_name

def _safe(p, k, d=0):
    v = p.get(k); return v if v is not None else d

# ── DANH SÁCH DANH HIỆU ─────────────────────────────────────────
# (id, tên hiển thị, mô tả điều kiện, func check(player, extra))
TITLES_DEF = [
    # Nhập môn
    ("tan_thu",        "🌱 Tân Thủ Tu Tiên",         "Vừa bước vào con đường tu tiên",
        lambda p,e: True),
    # Đạo phái
    ("ma_dao",         "🌑 Ma Đạo Truyền Nhân",       "Chọn Ma Đạo",
        lambda p,e: p.get("dao") == "nhapma"),
    ("chinh_dao",      "☀️ Chính Đạo Đệ Tử",          "Chọn Chính Đạo",
        lambda p,e: p.get("dao") == "nhapdao"),
    ("nho_dao",        "📖 Nho Gia Học Giả",           "Chọn Nho Đạo",
        lambda p,e: p.get("dao") == "nhapnho"),
    ("quy_dao",        "👻 Quỷ Môn Du Khách",          "Chọn Quỷ Đạo",
        lambda p,e: p.get("dao") == "nhapquy"),
    ("yeu_dao",        "🐾 Yêu Tộc Thiếu Chủ",         "Chọn Yêu Đạo",
        lambda p,e: p.get("dao") == "nhapyeu"),
    ("lo_dao",         "🧴 Lọ Đạo Kỳ Nhân",           "Chọn Lọ Đạo",
        lambda p,e: p.get("dao") == "nhaplo"),
    # Cảnh giới
    ("luyen_khi",      "🌿 Luyện Khí Tu Sĩ",          "Đạt Luyện Khí",
        lambda p,e: int(_safe(p,"realm_index",0)) >= 1),
    ("truc_co",        "🪨 Trúc Cơ Cường Giả",         "Đạt Trúc Cơ",
        lambda p,e: int(_safe(p,"realm_index",0)) >= 2),
    ("kim_dan",        "💛 Kim Đan Tu Sĩ",             "Đạt Kim Đan",
        lambda p,e: int(_safe(p,"realm_index",0)) >= 3),
    ("nguyen_anh",     "🟣 Nguyên Anh Tiên",           "Đạt Nguyên Anh",
        lambda p,e: int(_safe(p,"realm_index",0)) >= 4),
    ("hoa_than",       "🔥 Hóa Thần Cường Giả",        "Đạt Hóa Thần",
        lambda p,e: int(_safe(p,"realm_index",0)) >= 5),
    ("luyen_hu",       "🌸 Luyện Hư Tiên Nhân",        "Đạt Luyện Hư",
        lambda p,e: int(_safe(p,"realm_index",0)) >= 6),
    ("hop_the",        "🟠 Hợp Thể Đại Năng",          "Đạt Hợp Thể",
        lambda p,e: int(_safe(p,"realm_index",0)) >= 7),
    ("dai_thua",       "💫 Đại Thừa Tiên Nhân",        "Đạt Đại Thừa",
        lambda p,e: int(_safe(p,"realm_index",0)) >= 8),
    ("do_kiep",        "⚡ Độ Kiếp Thành Tiên",         "Đạt Độ Kiếp",
        lambda p,e: int(_safe(p,"realm_index",0)) >= 9),
    ("chan_tien",       "✨ Chân Tiên Đắc Đạo",         "Đạt Chân Tiên",
        lambda p,e: int(_safe(p,"realm_index",0)) >= 10),
    ("dai_la",         "❤️‍🔥 Đại La Kim Tiên",           "Đạt Đại La",
        lambda p,e: int(_safe(p,"realm_index",0)) >= 13),
    ("thanh_nhan",     "👑 Thánh Giả Vô Song",          "Đạt Thánh Nhân",
        lambda p,e: int(_safe(p,"realm_index",0)) >= 15),
    # PK
    ("chien_si",       "⚔️ Chiến Sĩ Sơ Kỳ",            "Thắng 1 trận PK",
        lambda p,e: int(_safe(p,"total_pk_win",0)) >= 1),
    ("cao_thu",        "⚔️ Cao Thủ Giang Hồ",           "Thắng 10 trận PK",
        lambda p,e: int(_safe(p,"total_pk_win",0)) >= 10),
    ("chien_than",     "⚔️ Chiến Thần Bất Bại",         "Thắng 50 trận PK",
        lambda p,e: int(_safe(p,"total_pk_win",0)) >= 50),
    ("thien_ha_vo_dich","⚔️ Thiên Hạ Vô Địch",          "Thắng 100 trận PK",
        lambda p,e: int(_safe(p,"total_pk_win",0)) >= 100),
    # Boss
    ("boss_san",       "👹 Kẻ Săn Thần Thú",           "Đánh Boss 10 lần",
        lambda p,e: int(_safe(p,"total_boss_attack",0)) >= 10),
    ("boss_hunter",    "👹 Boss Hunter",                "Đánh Boss 50 lần",
        lambda p,e: int(_safe(p,"total_boss_attack",0)) >= 50),
    ("boss_diet",      "👹 Thần Diệt Boss",             "Đánh Boss 100 lần",
        lambda p,e: int(_safe(p,"total_boss_attack",0)) >= 100),
    # Thám hiểm
    ("tham_hiem",      "🗺️ Nhà Thám Hiểm",             "Thám hiểm 10 lần",
        lambda p,e: int(_safe(p,"total_explore",0)) >= 10),
    ("lu_khach",       "🗺️ Lữ Khách Bốn Phương",        "Thám hiểm 50 lần",
        lambda p,e: int(_safe(p,"total_explore",0)) >= 50),
    ("chinh_phuc",     "🗺️ Thiên Hạ Đệ Nhất Khám Phá",  "Thám hiểm 100 lần",
        lambda p,e: int(_safe(p,"total_explore",0)) >= 100),
    # Điểm danh
    ("sieng_nang",     "✨ Siêng Năng Tu Luyện",         "Điểm danh 7 ngày liên tiếp",
        lambda p,e: e.get("streak",0) >= 7),
    ("tin_do",         "🔥 Tín Đồ Tu Tiên",             "Điểm danh 30 ngày liên tiếp",
        lambda p,e: e.get("streak",0) >= 30),
    ("kien_tri",       "💎 Kiên Trì Bất Khuất",          "Điểm danh 60 ngày liên tiếp",
        lambda p,e: e.get("streak",0) >= 60),
]

# Map id -> (tên, mô tả)
TITLE_MAP = {tid: (tname, tdesc) for tid, tname, tdesc, _ in TITLES_DEF}

def _get_unlocked(player, streak=0):
    extra = {"streak": streak}
    return [tid for tid, tname, tdesc, check in TITLES_DEF if check(player, extra)]

class Achievement(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @commands.group(name="danh_hieu", aliases=["danhhieu","title","dh"], invoke_without_command=True)
    async def danh_hieu(self, ctx):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        """Xem danh hiệu đang đeo hoặc mở menu"""
        # Hiện danh hiệu đang đeo + gợi ý sub-lệnh
        current = player.get("passport", "")  # dùng tạm passport để store title id
        # Lấy title id từ status_data
        try:
            sd = player.get("status_data") or "{}"
            sd_dict = __import__("json").loads(sd) if isinstance(sd, str) else (sd or {})
            active_title_id = sd_dict.get("active_title", "")
        except Exception:
            active_title_id = ""

        tname = TITLE_MAP.get(active_title_id, ("_(chưa đeo danh hiệu)_", ""))[0] if active_title_id else "_(chưa đeo danh hiệu)_"

        streak_data = await self.bot.db.get_streak(ctx.author.id)
        streak = _safe(streak_data, "streak", 0)
        unlocked = _get_unlocked(player, streak)

        embed = discord.Embed(title="🎖️ DANH HIỆU", color=realm_color(int(_safe(player,"realm_index",0))))
        embed.set_author(name=player["name"], icon_url=ctx.author.display_avatar.url)
        embed.add_field(name="🏅 Đang Đeo", value=tname, inline=False)
        embed.add_field(
            name="📋 Lệnh",
            value=(
                "`,tl danhhieu xem` — Xem tất cả danh hiệu đã mở\n"
                "`,tl danhhieu mac [tên hoặc id]` — Đeo danh hiệu"
            ),
            inline=False
        )
        embed.add_field(name="📊 Đã Mở", value=f"`{len(unlocked)}/{len(TITLES_DEF)}`", inline=True)
        embed.set_footer(text="Tu Tiên Bot v4")
        await ctx.send(embed=embed)

    @danh_hieu.command(name="xem", aliases=["list","all","ds"])
    async def dh_xem(self, ctx):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        """Xem tất cả danh hiệu đã mở khóa"""
        streak_data = await self.bot.db.get_streak(ctx.author.id)
        streak = _safe(streak_data, "streak", 0)
        unlocked_ids = set(_get_unlocked(player, streak))

        # Lấy danh hiệu đang đeo
        try:
            sd = player.get("status_data") or "{}"
            sd_dict = __import__("json").loads(sd) if isinstance(sd, str) else (sd or {})
            active_id = sd_dict.get("active_title", "")
        except Exception:
            active_id = ""

        embed = discord.Embed(title="🎖️ DANH SÁCH DANH HIỆU", color=0xFFD700)
        embed.set_author(name=player["name"], icon_url=ctx.author.display_avatar.url)
        embed.description = f"Đã mở: **{len(unlocked_ids)}/{len(TITLES_DEF)}** danh hiệu\n"

        # Chia thành đã mở và chưa mở
        unlocked_lines = []
        locked_lines   = []
        for tid, tname, tdesc, _ in TITLES_DEF:
            if tid in unlocked_ids:
                marker = "🏅" if tid == active_id else "✅"
                unlocked_lines.append(f"{marker} **{tname}**\n  _{tdesc}_")
            else:
                locked_lines.append(f"🔒 {tname} — _{tdesc}_")

        # Hiện danh hiệu đã mở
        if unlocked_lines:
            # Chia thành nhiều field nếu dài
            chunk = []
            for line in unlocked_lines:
                chunk.append(line)
                if len(chunk) >= 6:
                    embed.add_field(
                        name="✅ Đã Mở Khóa",
                        value="\n".join(chunk),
                        inline=False
                    )
                    chunk = []
            if chunk:
                embed.add_field(name="✅ Đã Mở Khóa", value="\n".join(chunk), inline=False)
        else:
            embed.add_field(name="✅ Đã Mở Khóa", value="_Chưa có_", inline=False)

        # Hiện tối đa 5 danh hiệu chưa mở
        if locked_lines:
            preview = locked_lines[:5]
            if len(locked_lines) > 5:
                preview.append(f"_...và {len(locked_lines)-5} danh hiệu khác_")
            embed.add_field(name="🔒 Chưa Mở", value="\n".join(preview), inline=False)

        embed.set_footer(text="🏅 = đang đeo  •  ,tl danhhieu mac [tên/id] để đeo  •  Tu Tiên Bot v4")
        await ctx.send(embed=embed)

    @danh_hieu.command(name="mac", aliases=["wear","doi","equip_title"])
    async def dh_mac(self, ctx, *, query: str = None):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn!")); return
        """Đeo danh hiệu theo tên hoặc id"""
        if not query:
            await ctx.send(embed=warn("Dùng: `,tl danhhieu mac [tên hoặc id danh hiệu]`"))
            return

        streak_data = await self.bot.db.get_streak(ctx.author.id)
        streak = _safe(streak_data, "streak", 0)
        unlocked_ids = set(_get_unlocked(player, streak))

        q = query.lower().strip()

        # Tìm match theo id hoặc tên
        found_id = None
        # Exact id
        if q in TITLE_MAP and q in unlocked_ids:
            found_id = q
        else:
            # Partial match tên hoặc id
            candidates = []
            for tid in unlocked_ids:
                tname = TITLE_MAP[tid][0].lower()
                if q in tid.lower() or q in tname:
                    candidates.append(tid)
            if len(candidates) == 1:
                found_id = candidates[0]
            elif len(candidates) > 1:
                # Nhiều kết quả - hỏi rõ hơn
                lines = [f"• `{tid}` — {TITLE_MAP[tid][0]}" for tid in candidates[:6]]
                embed = warn(f"Tìm thấy **{len(candidates)}** danh hiệu khớp. Nhập chính xác hơn:")
                embed.add_field(name="Kết Quả", value="\n".join(lines), inline=False)
                await ctx.send(embed=embed)
                return

        if not found_id:
            # Gợi ý fuzzy
            all_ids   = [tid for tid in unlocked_ids]
            all_names = [TITLE_MAP[tid][0].lower() for tid in unlocked_ids]
            from difflib import get_close_matches
            sug_ids   = get_close_matches(q, all_ids,   n=3, cutoff=0.4)
            sug_names = get_close_matches(q, all_names, n=3, cutoff=0.4)
            sug_lines = []
            for sid in sug_ids:
                sug_lines.append(f"• `{sid}` — {TITLE_MAP[sid][0]}")
            for sn in sug_names:
                for tid in unlocked_ids:
                    if TITLE_MAP[tid][0].lower() == sn and tid not in sug_ids:
                        sug_lines.append(f"• `{tid}` — {TITLE_MAP[tid][0]}")
            embed = error(f"Không tìm thấy danh hiệu **`{query}`** trong danh sách đã mở!")
            if sug_lines:
                embed.add_field(name="💡 Có phải bạn muốn?", value="\n".join(sug_lines[:5]), inline=False)
            embed.set_footer(text=",tl danhhieu xem — xem tất cả danh hiệu đã mở")
            await ctx.send(embed=embed)
            return

        # Lưu vào status_data
        import json as _json
        try:
            sd = player.get("status_data") or "{}"
            sd_dict = _json.loads(sd) if isinstance(sd, str) else (sd or {})
        except Exception:
            sd_dict = {}

        sd_dict["active_title"] = found_id
        await self.bot.db.update_player(ctx.author.id, status_data=_json.dumps(sd_dict))

        tname = TITLE_MAP[found_id][0]
        embed = success("✅ ĐEO DANH HIỆU THÀNH CÔNG!")
        embed.description = f"Bạn đang đeo: **{tname}**"
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Achievement(bot))

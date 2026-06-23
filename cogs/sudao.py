"""cogs/sudao.py — Hệ Thống Sư Đạo (Sư Phụ / Đồ Đệ) v1.0

Cơ chế:
- Sư phụ nhận tối đa 5 đồ đệ (có thể nâng qua prestige)
- Yêu cầu cảnh giới sư phụ >= Kim Đan (realm_index >= 7)
- Khi đồ đệ lên cảnh giới → sư phụ nhận 5% EXP của đồ đệ
- Khi đồ đệ đột phá → sư phụ nhận thêm thưởng linh thạch
- Đồ đệ nhận +10% EXP tu luyện khi có sư phụ
- Lệnh bai_su / chap_nhan / tu_choi / truyen_giao / xem_su_dao
"""

import discord
from discord.ext import commands
import time

from utils.embeds import success, warn, error, info, fmt, fmt_time
from utils.game_data import REALMS

# ══ Cấu hình ══════════════════════════════════════════════
MIN_REALM_SU_PHU   = 7      # Kim Đan trở lên mới được nhận đồ đệ
MAX_DO_DE_BASE     = 5      # Tối đa 5 đồ đệ
EXP_SHARE_RATIO    = 0.05   # Sư phụ nhận 5% EXP khi đồ đệ đột phá
DO_DE_EXP_BONUS    = 0.10   # Đồ đệ nhận thêm 10% EXP tu luyện
COOLDOWN_BAI_SU    = 86400  # 24h cooldown nếu bị từ chối / rời bỏ

def _realm_name(player: dict) -> str:
    ri = int(player.get("realm_index", 0))
    rt = int(player.get("realm_tier",  1))
    if ri >= len(REALMS): return "Thiên Đạo"
    return f"{REALMS[ri]['name']} tầng {rt}"

def _max_do_de(su_phu: dict) -> int:
    return MAX_DO_DE_BASE + int(su_phu.get("prestige", 0))

# ══════════════════════════════════════════════════════════
class SuDao(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        db = self.bot.db
        # Bảng quan hệ sư phụ – đồ đệ
        await db.execute("""
            CREATE TABLE IF NOT EXISTS su_dao (
                do_de_id   TEXT PRIMARY KEY,
                su_phu_id  TEXT NOT NULL,
                joined_at  INTEGER NOT NULL DEFAULT 0,
                exp_shared REAL    NOT NULL DEFAULT 0
            )
        """)
        # Bảng lời mời bái sư đang chờ
        await db.execute("""
            CREATE TABLE IF NOT EXISTS su_dao_pending (
                do_de_id   TEXT PRIMARY KEY,
                su_phu_id  TEXT NOT NULL,
                sent_at    INTEGER NOT NULL DEFAULT 0
            )
        """)
        # Cooldown rời/bị từ chối
        await db.execute("""
            CREATE TABLE IF NOT EXISTS su_dao_cooldown (
                user_id    TEXT PRIMARY KEY,
                until      INTEGER NOT NULL DEFAULT 0
            )
        """)

    # ── Helper: lấy danh sách đồ đệ của sư phụ ───────────
    async def _get_do_de(self, su_phu_id: str) -> list:
        return await self.bot.db.fetchall(
            "SELECT * FROM su_dao WHERE su_phu_id=? ORDER BY joined_at ASC",
            (su_phu_id,)
        )

    async def _get_su_phu(self, do_de_id: str):
        return await self.bot.db.fetchone(
            "SELECT * FROM su_dao WHERE do_de_id=?", (do_de_id,)
        )

    # ── Helper: cooldown check ─────────────────────────────
    async def _check_cd(self, user_id: str) -> int:
        row = await self.bot.db.fetchone(
            "SELECT * FROM su_dao_cooldown WHERE user_id=?", (user_id,)
        )
        if row:
            rem = int(row["until"]) - int(time.time())
            return max(0, rem)
        return 0

    async def _set_cd(self, user_id: str, seconds: int):
        until = int(time.time()) + seconds
        await self.bot.db.execute("""
            INSERT INTO su_dao_cooldown (user_id, until) VALUES (?,?)
            ON CONFLICT(user_id) DO UPDATE SET until=excluded.until
        """, (user_id, until))

    # ══ LỆNH BÁI SƯ ══════════════════════════════════════
    @commands.command(name="bai_su", aliases=["baisu","xin_su","xinsu"])
    async def bai_su(self, ctx, target: discord.Member):
        """Gửi lời mời bái sư tới người chơi khác."""
        if target.id == ctx.author.id:
            await ctx.send(embed=warn("Không thể tự bái mình làm sư phụ!")); return

        do_de   = await self.bot.db.get_player(ctx.author.id)
        su_phu  = await self.bot.db.get_player(target.id)
        if not do_de:
            await ctx.send(embed=warn("Bạn chưa nhập môn!")); return
        if not su_phu:
            await ctx.send(embed=warn(f"**{target.display_name}** chưa nhập môn!")); return

        # Kiểm tra đã có sư phụ chưa
        hien_su = await self._get_su_phu(str(ctx.author.id))
        if hien_su:
            sp_player = await self.bot.db.get_player(hien_su["su_phu_id"])
            sp_name = sp_player["name"] if sp_player else "???"
            await ctx.send(embed=warn(f"Bạn đã có Sư Phụ: **{sp_name}**!\nDùng `,tl roi_su` để rời bỏ trước.")); return

        # Cooldown
        cd = await self._check_cd(str(ctx.author.id))
        if cd > 0:
            h, m = divmod(cd // 60, 60)
            await ctx.send(embed=warn(f"Bạn đang trong thời gian hồi phục Sư Đạo!\nCòn lại: **{h}h {m}m**")); return

        # Kiểm tra sư phụ đủ cảnh giới
        if int(su_phu.get("realm_index", 0)) < MIN_REALM_SU_PHU:
            req = REALMS[MIN_REALM_SU_PHU]["name"]
            await ctx.send(embed=warn(f"Sư Phụ cần đạt **{req}** trở lên mới được nhận đồ đệ!")); return

        # Kiểm tra sư phụ còn chỗ không
        do_de_list = await self._get_do_de(str(target.id))
        if len(do_de_list) >= _max_do_de(su_phu):
            await ctx.send(embed=warn(f"**{su_phu['name']}** đã đủ {_max_do_de(su_phu)} đồ đệ!")); return

        # Kiểm tra sư phụ không phải đồ đệ của mình
        self_do_de = await self._get_do_de(str(ctx.author.id))
        if any(d["do_de_id"] == str(target.id) for d in self_do_de):
            await ctx.send(embed=warn("Không thể bái sư người đang là đồ đệ của bạn!")); return

        # Gửi lời mời
        await self.bot.db.execute("""
            INSERT INTO su_dao_pending (do_de_id, su_phu_id, sent_at) VALUES (?,?,?)
            ON CONFLICT(do_de_id) DO UPDATE SET su_phu_id=excluded.su_phu_id, sent_at=excluded.sent_at
        """, (str(ctx.author.id), str(target.id), int(time.time())))

        embed = discord.Embed(
            title="🙏 LỜI MỜI BÁI SƯ",
            description=(
                f"**{do_de['name']}** ({_realm_name(do_de)}) muốn bái\n"
                f"**{su_phu['name']}** ({_realm_name(su_phu)}) làm **Sư Phụ**!\n\n"
                f"Sư phụ dùng `,tl chap_nhan_su @{ctx.author.display_name}` để đồng ý\n"
                f"hoặc `,tl tu_choi_su @{ctx.author.display_name}` để từ chối.\n"
                f"_(Alias: `chap_chan`, `chapchan`, `dongysu`)_"
            ),
            color=0xFFD700
        )
        embed.set_footer(text="Lời mời hết hạn sau 24 giờ")
        await ctx.send(embed=embed)

    # ══ CHẤP NHẬN ════════════════════════════════════════
    @commands.command(name="chap_nhan_su", aliases=["chapnhansu","accept_su","chap_chan","chapchan","dong_y_su","dongysu"])
    async def chap_nhan_su(self, ctx, target: discord.Member):
        """Chấp nhận lời mời bái sư."""
        su_phu  = await self.bot.db.get_player(ctx.author.id)
        do_de_p = await self.bot.db.get_player(target.id)
        if not su_phu or not do_de_p:
            await ctx.send(embed=warn("Người chơi không tồn tại!")); return

        pending = await self.bot.db.fetchone(
            "SELECT * FROM su_dao_pending WHERE do_de_id=? AND su_phu_id=?",
            (str(target.id), str(ctx.author.id))
        )
        if not pending:
            await ctx.send(embed=warn(f"Không có lời mời bái sư từ **{do_de_p['name']}**!")); return

        # Hết hạn?
        if int(time.time()) - int(pending["sent_at"]) > 86400:
            await self.bot.db.execute(
                "DELETE FROM su_dao_pending WHERE do_de_id=?", (str(target.id),)
            )
            await ctx.send(embed=warn("Lời mời đã hết hạn!")); return

        # Kiểm tra lại
        do_de_list = await self._get_do_de(str(ctx.author.id))
        if len(do_de_list) >= _max_do_de(su_phu):
            await ctx.send(embed=warn(f"Bạn đã đủ {_max_do_de(su_phu)} đồ đệ!")); return

        # Lưu quan hệ
        await self.bot.db.execute("""
            INSERT OR IGNORE INTO su_dao (do_de_id, su_phu_id, joined_at) VALUES (?,?,?)
        """, (str(target.id), str(ctx.author.id), int(time.time())))
        await self.bot.db.execute(
            "DELETE FROM su_dao_pending WHERE do_de_id=?", (str(target.id),)
        )

        embed = success(
            "🎊 KẾT NGHĨA SƯ ĐẠO",
            f"**{su_phu['name']}** ({_realm_name(su_phu)}) đã nhận\n"
            f"**{do_de_p['name']}** ({_realm_name(do_de_p)}) làm Đồ Đệ!\n\n"
            f"📚 Đồ đệ nhận **+{int(DO_DE_EXP_BONUS*100)}% EXP** khi tu luyện\n"
            f"✨ Sư phụ nhận **{int(EXP_SHARE_RATIO*100)}% EXP** khi đồ đệ đột phá"
        )
        await ctx.send(embed=embed)
        # Thông báo cho đồ đệ
        try:
            user = await self.bot.fetch_user(int(target.id))
            await user.send(embed=success(
                "🎊 BÁI SƯ THÀNH CÔNG",
                f"**{su_phu['name']}** đã nhận bạn làm Đồ Đệ!\n"
                f"Từ nay tu luyện sẽ được cộng thêm **+{int(DO_DE_EXP_BONUS*100)}% EXP**."
            ))
        except Exception:
            pass

    # ══ TỪ CHỐI ══════════════════════════════════════════
    @commands.command(name="tu_choi_su", aliases=["tuchoisu","reject_su"])
    async def tu_choi_su(self, ctx, target: discord.Member):
        """Từ chối lời mời bái sư."""
        pending = await self.bot.db.fetchone(
            "SELECT * FROM su_dao_pending WHERE do_de_id=? AND su_phu_id=?",
            (str(target.id), str(ctx.author.id))
        )
        if not pending:
            await ctx.send(embed=warn("Không có lời mời nào để từ chối!")); return

        await self.bot.db.execute(
            "DELETE FROM su_dao_pending WHERE do_de_id=?", (str(target.id),)
        )
        await self._set_cd(str(target.id), COOLDOWN_BAI_SU)

        do_de_p = await self.bot.db.get_player(target.id)
        await ctx.send(embed=info(
            "❌ ĐÃ TỪ CHỐI",
            f"Đã từ chối lời mời bái sư của **{do_de_p['name'] if do_de_p else '???'}**."
        ))

    # ══ RỜI BỎ SƯ PHỤ ════════════════════════════════════
    @commands.command(name="roi_su", aliases=["roisu","leave_su"])
    async def roi_su(self, ctx):
        """Rời bỏ Sư Phụ (cooldown 24h)."""
        hien_su = await self._get_su_phu(str(ctx.author.id))
        if not hien_su:
            await ctx.send(embed=warn("Bạn chưa có Sư Phụ!")); return

        sp_player = await self.bot.db.get_player(hien_su["su_phu_id"])
        sp_name   = sp_player["name"] if sp_player else "???"
        player    = await self.bot.db.get_player(ctx.author.id)

        await self.bot.db.execute(
            "DELETE FROM su_dao WHERE do_de_id=?", (str(ctx.author.id),)
        )
        await self._set_cd(str(ctx.author.id), COOLDOWN_BAI_SU)

        await ctx.send(embed=warn(
            f"**{player['name']}** đã rời bỏ Sư Phụ **{sp_name}**.\n"
            f"⏳ Cooldown bái sư: **24 giờ**."
        ))

    # ══ TRỤC XUẤT ĐỒ ĐỆ ══════════════════════════════════
    @commands.command(name="truc_xuat", aliases=["trucxuat_de","kick_de"])
    async def truc_xuat(self, ctx, target: discord.Member):
        """Trục xuất đồ đệ khỏi môn phái."""
        su_phu = await self.bot.db.get_player(ctx.author.id)
        if not su_phu: await ctx.send(embed=warn("Bạn chưa nhập môn!")); return

        row = await self.bot.db.fetchone(
            "SELECT * FROM su_dao WHERE do_de_id=? AND su_phu_id=?",
            (str(target.id), str(ctx.author.id))
        )
        if not row:
            await ctx.send(embed=warn(f"**{target.display_name}** không phải đồ đệ của bạn!")); return

        do_de_p = await self.bot.db.get_player(target.id)
        await self.bot.db.execute(
            "DELETE FROM su_dao WHERE do_de_id=?", (str(target.id),)
        )
        await self._set_cd(str(target.id), COOLDOWN_BAI_SU)

        await ctx.send(embed=warn(
            f"**{su_phu['name']}** đã trục xuất **{do_de_p['name'] if do_de_p else '???'}** khỏi môn!\n"
            f"Đồ đệ bị cooldown bái sư **24 giờ**."
        ))

    # ══ TRUYỀN GIAO (sư phụ tặng EXP/LT cho đồ đệ) ═════
    @commands.command(name="truyen_giao", aliases=["truyengiao","day_do"])
    async def truyen_giao(self, ctx, target: discord.Member, loai: str, so_luong: int):
        """
        Sư phụ truyền giao tài nguyên cho đồ đệ.
        Dùng: ,tl truyen_giao @đồđệ [exp/ha/trung/cuc] [số]
        """
        su_phu = await self.bot.db.get_player(ctx.author.id)
        if not su_phu: await ctx.send(embed=warn("Bạn chưa nhập môn!")); return
        if so_luong <= 0: await ctx.send(embed=warn("Số lượng phải > 0!")); return

        # Kiểm tra đây có phải đồ đệ không
        row = await self.bot.db.fetchone(
            "SELECT * FROM su_dao WHERE do_de_id=? AND su_phu_id=?",
            (str(target.id), str(ctx.author.id))
        )
        if not row:
            await ctx.send(embed=warn(f"**{target.display_name}** không phải đồ đệ của bạn!")); return

        do_de_p = await self.bot.db.get_player(target.id)
        if not do_de_p: await ctx.send(embed=warn("Đồ đệ không tồn tại!")); return

        loai = loai.lower()
        LOAI = {
            "exp":   ("exp",            "✨ Tu Vi"),
            "ha":    ("linh_thach_ha",  "💰 Hạ Phẩm LT"),
            "trung": ("linh_thach_trung","💎 Trung Phẩm LT"),
            "cuc":   ("linh_thach_cuc", "👑 Cực Phẩm LT"),
        }
        if loai not in LOAI:
            await ctx.send(embed=warn("Loại không hợp lệ! Dùng: `exp` / `ha` / `trung` / `cuc`")); return

        field, ten = LOAI[loai]
        sp_co = float(su_phu.get(field, 0))
        if sp_co < so_luong:
            await ctx.send(embed=error(f"Bạn không đủ **{ten}**!\nCần: {so_luong:,} | Có: {int(sp_co):,}")); return

        await self.bot.db.update_player(ctx.author.id, **{field: sp_co - so_luong})
        await self.bot.db.update_player(target.id,     **{field: float(do_de_p.get(field, 0)) + so_luong})

        embed = success(
            "📜 TRUYỀN GIAO SƯ ĐẠO",
            f"**{su_phu['name']}** → **{do_de_p['name']}**\n"
            f"{ten}: **{so_luong:,}**"
        )
        embed.set_footer(text=",tl truyen_giao @đồđệ [exp/ha/trung/cuc] [số]")
        await ctx.send(embed=embed)

    # ══ XEM SƯ ĐẠO ════════════════════════════════════════
    @commands.command(name="su_dao", aliases=["sudao","xem_sudao","mon_phai_ta"])
    async def xem_su_dao(self, ctx, target: discord.Member = None):
        """Xem thông tin Sư Đạo của bản thân hoặc người khác."""
        user   = target or ctx.author
        player = await self.bot.db.get_player(user.id)
        if not player:
            await ctx.send(embed=warn("Người chơi chưa nhập môn!")); return

        embed = discord.Embed(
            title=f"🏯 SƯ ĐẠO — {player['name']}",
            color=0xFFD700
        )
        embed.set_thumbnail(url=user.display_avatar.url)

        # Sư phụ
        hien_su = await self._get_su_phu(str(user.id))
        if hien_su:
            sp = await self.bot.db.get_player(hien_su["su_phu_id"])
            sp_name  = sp["name"] if sp else "???"
            sp_realm = _realm_name(sp) if sp else "???"
            days = (int(time.time()) - int(hien_su["joined_at"])) // 86400
            shared = int(hien_su.get("exp_shared", 0))
            embed.add_field(
                name="👴 Sư Phụ",
                value=(
                    f"**{sp_name}**\n"
                    f"Cảnh Giới: {sp_realm}\n"
                    f"Thọ Sư: **{days}** ngày\n"
                    f"Tu Vi đã nhận: **{fmt(shared)}**"
                ),
                inline=False
            )
        else:
            embed.add_field(name="👴 Sư Phụ", value="_Chưa có_", inline=False)

        # Đồ đệ
        do_de_list = await self._get_do_de(str(user.id))
        max_de = _max_do_de(player)
        if do_de_list:
            lines = []
            for d in do_de_list:
                dp = await self.bot.db.get_player(d["do_de_id"])
                if not dp: continue
                days = (int(time.time()) - int(d["joined_at"])) // 86400
                lines.append(
                    f"• **{dp['name']}** ({_realm_name(dp)}) — {days}ngày | EXP giao: {fmt(d.get('exp_shared',0))}"
                )
            embed.add_field(
                name=f"👨‍👩‍👧‍👦 Đồ Đệ ({len(do_de_list)}/{max_de})",
                value="\n".join(lines),
                inline=False
            )
        else:
            embed.add_field(
                name=f"👨‍👩‍👧‍👦 Đồ Đệ (0/{max_de})",
                value="_Chưa có đồ đệ_\nDùng `,tl chap_nhan_su @người` để nhận đồ đệ.",
                inline=False
            )

        # Lợi ích
        embed.add_field(
            name="📋 Lợi Ích",
            value=(
                f"✅ Đồ đệ: **+{int(DO_DE_EXP_BONUS*100)}% EXP** tu luyện\n"
                f"✅ Sư phụ: **{int(EXP_SHARE_RATIO*100)}% EXP** khi đồ đệ đột phá\n"
                f"✅ Truyền giao tài nguyên: `,tl truyen_giao`"
            ),
            inline=False
        )
        embed.set_footer(text=",tl bai_su @người | ,tl su_dao | ,tl truyen_giao")
        await ctx.send(embed=embed)


# ══ HÀM PUBLIC: gọi từ cultivation.py khi đột phá thành công ══
async def on_dotpha_success(bot, do_de_id: str, exp_gained: float):
    """
    Gọi sau khi đồ đệ đột phá thành công.
    - Sư phụ nhận EXP_SHARE_RATIO % exp_gained
    - Thêm thưởng linh thạch nhỏ cho sư phụ
    """
    try:
        row = await bot.db.fetchone(
            "SELECT * FROM su_dao WHERE do_de_id=?", (str(do_de_id),)
        )
        if not row: return

        sp_id  = row["su_phu_id"]
        sp     = await bot.db.get_player(sp_id)
        do_de  = await bot.db.get_player(do_de_id)
        if not sp or not do_de: return

        bonus_exp = float(exp_gained) * EXP_SHARE_RATIO
        bonus_lt  = max(1000, int(bonus_exp / 10_000))  # ~1k–vài chục k hạ LT tùy đột phá

        await bot.db.update_player(sp_id,
            exp           = float(sp.get("exp", 0)) + bonus_exp,
            linh_thach_ha = int(sp.get("linh_thach_ha", 0)) + bonus_lt,
        )
        # Cộng vào tổng exp đã chia sẻ
        await bot.db.execute("""
            UPDATE su_dao SET exp_shared = exp_shared + ? WHERE do_de_id=?
        """, (bonus_exp, str(do_de_id)))

    except Exception as e:
        print(f"[SuDao] on_dotpha_success error: {e}")


async def setup(bot):
    await bot.add_cog(SuDao(bot))

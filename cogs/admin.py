"""cogs/admin.py - Lệnh quản trị (chỉ owner/admin) v3"""
import discord
from discord.ext import commands
from utils.embeds import *
from utils.game_data import ITEMS, REALMS, DAO, get_realm_name, LINH_CAN, THE_CHAT, HUYET_MACH, scale_stats_for_realm_change
from utils.helpers import sync_realm_role

def is_owner():
    """Đấng Sáng Thế - chỉ bot owner (tao) hoặc server owner"""
    async def predicate(ctx):
        if await ctx.bot.is_owner(ctx.author):
            return True
        if ctx.guild and ctx.author.id == ctx.guild.owner_id:
            return True
        return False
    return commands.check(predicate)

def is_admin():
    """Admin = quyền quản trị server, sub-admin được thêm bằng tl admin add, hoặc Đấng Sáng Thế"""
    async def predicate(ctx):
        if await ctx.bot.is_owner(ctx.author):
            return True
        if ctx.guild and ctx.author.id == ctx.guild.owner_id:
            return True
        if ctx.guild and ctx.author.guild_permissions.administrator:
            return True
        if ctx.bot.db and await ctx.bot.db.is_bot_admin(ctx.author.id):
            return True
        return False
    return commands.check(predicate)

class Admin(commands.Cog):
    def __init__(self, bot): self.bot = bot

    # ══ HELP ADMIN ════════════════════════════════════════════
    @commands.command(name="admin_help", aliases=["adminhelp","quantri"])
    @is_admin()
    async def admin_help(self, ctx):
        """📜 Bí Tịch Quản Trị Tu Tiên"""
        embed = discord.Embed(
            title="📜 BÍ TỊCH QUẢN TRỊ TU TIÊN 📜",
            description="*(Những lệnh này có thể ảnh hưởng lớn đến game)*",
            color=0xFF5722
        )

        embed.add_field(
            name="☯️ Quyền Năng Vô Thượng (CHỈ ĐẤNG SÁNG THẾ)",
            value=(
                "⚡ `,tl vothuong [@tag]` — **Phong Vô Thượng Đạo Tổ** cho mình hoặc người khác.\n"
                "🌑 `,tl thu_vothuong [@tag]` — Thu hồi Vô Thượng, hoàn về căn cơ ban đầu.\n"
                "_Vô Thượng = stats vô cực, one-hit tất cả, cảnh giới tối thượng._"
            ),
            inline=False
        )

        embed.add_field(
            name="🌌 Quyền Hạn Tối Cao (Đấng Sáng Thế Only)",
            value=(
                "1. `,tl buffitem [id] [số_lượng] [@tag/all]` — Trao/Thu hồi vật phẩm.\n"
                "2. `,tl setitem [id] [số_lượng] [@tag/all]` — ĐẶT số lượng vật phẩm.\n"
                "3. `,tl thap reset [all/@tag]` — Reset tiến độ Tháp.\n"
                "4. `,tl admin buff-all [số_tiền]` — Tặng Linh Thạch toàn server.\n"
                "5. `,tl admin clear-items` — Dọn dẹp túi đồ lạm phát đồ hiếm.\n"
                "6. `,tl admin sync [OLD_UID] [NEW_UID]` — Đồng bộ dữ liệu người chơi.\n"
                "7. `,tl admin doicuc [all/@tag]` — Quy đổi cưỡng chế sang Cực Phẩm LT.\n"
                "8. `,tl findid \"tên\"` — Tìm kiếm ID người chơi dựa trên tên.\n"
                "9. `,tl admin bank [on/off]` — Đóng/Mở chuyển khoản toàn server.\n"
                "10. `,tl admin staff [on/off]` — Đóng/Mở quyền của Sáng Thế & Thượng Đế Lệnh."
            ),
            inline=False
        )

        embed.add_field(
            name="⭐ Quyền Hạn Quản Lý (Thượng Đế Lệnh / Staff)",
            value=(
                "1. `,tl admin set [hp/atk/def/spd/money/exp/tl/ngo] @tag [giá_trị]` — Chỉnh chỉ số.\n"
                "2. `,tl admin set [linhcan/thechat/huyetmach] @tag [tên/số]` — Đổi căn cơ.\n"
                "3. `,tl adminbuff [lt/exp/tl/mau/ngo] <số_lượng> [@tag]` — Cộng thêm thông số.\n"
                "4. `,tl checkadmin @tag` — Kiểm tra lịch sử thao tác của Admin.\n"
                "5. `,tl settime [số_phút] [@tag]` — [DEBUG] Chỉnh thời gian đã tu luyện.\n"
                "6. `,tl resettp [@tag] [Tier 1-5] [lc:X tc:Y HM:Z mc:W]` — Cưỡng chế tẩy tủy.\n"
                "7. `,tl banacc @tag [thời_gian (1d, 1h)]` — Phong ấn tài khoản.\n"
                "8. `,tl unban @tag` — Giải trừ phong ấn.\n"
                "9. `,tl set daicanhgioi [1-70] [@tag]` — Set Đại Cảnh Giới.\n"
                "10. `,tl set dao [thiendao/thiensu] [@tag]` — Gán Đạo đặc biệt.\n"
                "11. `,tl admin reset @tag` — Reset (xóa) nhân vật.\n"
                "12. `,tl admin list` — Xem danh sách Sub-Admin.\n"
                "13. `,tl admin realmrole [on/off]` — Bật/tắt role Discord tự động theo cảnh giới."
            ),
            inline=False
        )

        embed.add_field(
            name="🌟 Sub-Admin (chỉ Đấng Sáng Thế)",
            value=(
                "`,tl admin add @tag` — Thêm Sub-Admin (quyền như Admin, thua Sáng Thế 1 bậc).\n"
                "`,tl admin remove @tag` — Xóa quyền Sub-Admin."
            ),
            inline=False
        )

        embed.set_footer(text="📌 Dùng quyền một cách công tâm để duy trì cân bằng Tam Giới!")
        await ctx.send(embed=embed)

    # ══ ADMIN GROUP ═══════════════════════════════════════════
    @commands.group(name="admin", aliases=["ad"], invoke_without_command=True)
    @is_admin()
    async def admin(self, ctx):
        """Liệt kê tất cả lệnh admin hiện có kèm giải thích (tự động, luôn khớp với code)"""
        def walk(cmds, prefix=",tl "):
            rows = []
            for cmd in sorted(cmds, key=lambda c: c.name):
                if cmd.hidden:
                    continue
                full = f"{prefix}{cmd.qualified_name}"
                sig = f" {cmd.signature}" if cmd.signature else ""
                desc = cmd.help.strip().splitlines()[0] if cmd.help else "_(chưa có mô tả)_"
                rows.append(f"`{full}{sig}`\n　└ {desc}")
                if isinstance(cmd, commands.Group):
                    rows.extend(walk(cmd.commands, prefix=prefix))
            return rows

        all_cmds = [c for c in self.bot.commands if isinstance(c.cog, Admin)]
        lines = walk(all_cmds)
        text = "\n".join(lines) if lines else "_Không có lệnh nào._"

        embed = discord.Embed(title="📜 TẤT CẢ LỆNH ADMIN", color=0xFF5722)
        if len(text) <= 4000:
            embed.description = text
        else:
            chunks, cur = [], ""
            for line in lines:
                if len(cur) + len(line) + 1 > 1000:
                    chunks.append(cur); cur = ""
                cur += line + "\n"
            if cur:
                chunks.append(cur)
            for i, chunk in enumerate(chunks, 1):
                embed.add_field(name=f"({i})", value=chunk, inline=False)
        embed.set_footer(text="📌 Dùng quyền một cách công tâm để duy trì cân bằng Tam Giới!")
        await ctx.send(embed=embed)

    # ── ,tl admin set <stat> <@tag> <value> ─────────────────────
    SET_STAT_MAP = {
        "money": "linh_thach_ha", "lt": "linh_thach_ha",
        "exp":   "exp",
        "tl":    "stamina", "stamina": "stamina",
        "hp":    "hp", "mau": "hp",
        "hpmax": "hp_max", "maumax": "hp_max",
        "atk":   "atk", "congkich": "atk",
        "def":   "def_", "thuthu": "def_",
        "spd":   "spd", "tocdo": "spd",
        "ngo":   "ngo_tinh",
    }
    TALENT_POOLS = {
        "linhcan":   ("linh_can",   LINH_CAN,   "Linh Căn"),
        "thechat":   ("the_chat",   THE_CHAT,   "Thể Chất"),
        "huyetmach": ("huyet_mach", HUYET_MACH, "Huyết Mạch"),
    }

    SQLITE_INT_MAX = 9_223_372_036_854_775_807

    @admin.group(name="set", invoke_without_command=True)
    @is_admin()
    async def admin_set_group(self, ctx, stat: str = None, target: discord.Member = None, value: int = None):
        """Chỉnh chỉ số (hp/atk/def/spd/money/exp/tl/ngo) hoặc gõ kèm subcommand linhcan/thechat/huyetmach để đổi căn cơ"""
        if stat is None or target is None or value is None:
            embed = discord.Embed(title="⚙️ ,tl admin set", color=0x607D8B)
            embed.add_field(
                name="Chỉnh chỉ số",
                value=(
                    "`,tl admin set [hp/atk/def/spd/money/exp/tl/ngo] @tag [giá_trị]`\n"
                    "Vd: `,tl admin set hp @tag 50000`"
                ),
                inline=False
            )
            embed.add_field(
                name="Đổi căn cơ",
                value=(
                    "`,tl admin set linhcan @tag [tên/số]`\n"
                    "`,tl admin set thechat @tag [tên/số]`\n"
                    "`,tl admin set huyetmach @tag [tên/số]`\n"
                    "Gõ không kèm tên/số để xem danh sách lựa chọn."
                ),
                inline=False
            )
            await ctx.send(embed=embed)
            return

        stat_l = stat.lower()
        if stat_l not in self.SET_STAT_MAP:
            valid = "/".join(sorted(set(self.SET_STAT_MAP.keys())))
            await ctx.send(embed=warn(f"Stat không hợp lệ! Dùng: {valid}")); return

        if value < 0 or value > self.SQLITE_INT_MAX:
            await ctx.send(embed=warn(
                f"Giá trị vượt giới hạn cho phép!\n"
                f"Tối đa: **{self.SQLITE_INT_MAX:,}**"
            )); return

        p = await self.bot.db.get_player(target.id)
        if not p:
            await ctx.send(embed=error(f"{target.display_name} chưa nhập môn!")); return

        field = self.SET_STAT_MAP[stat_l]
        await self.bot.db.update_player(target.id, **{field: value})
        await ctx.send(embed=success("✅ SET", f"**{p['name']}** → `{stat_l}` = **{value:,}**"))

    async def _set_talent(self, ctx, kind: str, target: discord.Member, query: str):
        field, pool, label = self.TALENT_POOLS[kind]
        p = await self.bot.db.get_player(target.id)
        if not p:
            await ctx.send(embed=error(f"{target.display_name} chưa nhập môn!")); return

        if not query:
            lines = [f"`{i}` — {item['name']} _({item['rarity']})_" for i, item in enumerate(pool, start=1)]
            embed = discord.Embed(
                title=f"📜 Danh Sách {label}",
                description="\n".join(lines) + f"\n\n💡 Dùng: `,tl admin set {kind} @tag [tên hoặc số]`",
                color=0x607D8B
            )
            await ctx.send(embed=embed)
            return

        chosen = None
        if query.isdigit():
            idx = int(query) - 1
            if 0 <= idx < len(pool):
                chosen = pool[idx]
        if chosen is None:
            q = query.lower()
            for item in pool:
                if q == item["name"].lower() or q in item["name"].lower():
                    chosen = item
                    break
        if chosen is None:
            await ctx.send(embed=error(f"Không tìm thấy {label} `{query}`!\nGõ `,tl admin set {kind} @tag` để xem danh sách.")); return

        await self.bot.db.update_player(target.id, **{field: chosen["name"]})

        # Đồng bộ lại atk/def/hp/spd/lực chiến theo tư chất mới ngay lập tức
        # (giữ nguyên cảnh giới hiện tại) — để ,tl i hiển thị đúng ngay,
        # không cần đột phá lại mới thấy thay đổi.
        _updated_p = {**p, field: chosen["name"]}
        _scaled = scale_stats_for_realm_change(
            _updated_p,
            p.get("realm_index", 0),
            p.get("realm_tier", 1),
        )["new"]
        await self.bot.db.update_player(
            target.id,
            atk=_scaled["atk"], def_=_scaled["def_"],
            hp_max=_scaled["hp_max"], hp=_scaled["hp_max"],
            spd=_scaled["spd"], luc_chien=_scaled["luc_chien"],
        )

        embed = success(f"✅ ĐỔI {label.upper()}", f"**{p['name']}** → **{chosen['name']}** _({chosen['rarity']})_")
        embed.add_field(
            name="📊 Chỉ số đã đồng bộ",
            value=(
                f"⚔️ ATK `{fmt(_scaled['atk'])}` · 🛡️ DEF `{fmt(_scaled['def_'])}` · "
                f"❤️ HP `{fmt(_scaled['hp_max'])}` · ⚡ SPD `{fmt(_scaled['spd'])}` · "
                f"🔥 Lực Chiến `{fmt(_scaled['luc_chien'])}`"
            ),
            inline=False
        )
        await ctx.send(embed=embed)

    @admin_set_group.command(name="linhcan", aliases=["lc"])
    @is_admin()
    async def admin_set_linhcan(self, ctx, target: discord.Member, *, query: str = None):
        """[ADMIN] Đổi Linh Căn của người chơi"""
        await self._set_talent(ctx, "linhcan", target, query)

    @admin_set_group.command(name="thechat", aliases=["tc"])
    @is_admin()
    async def admin_set_thechat(self, ctx, target: discord.Member, *, query: str = None):
        """[ADMIN] Đổi Thể Chất của người chơi"""
        await self._set_talent(ctx, "thechat", target, query)

    @admin_set_group.command(name="huyetmach", aliases=["hm"])
    @is_admin()
    async def admin_set_huyetmach(self, ctx, target: discord.Member, *, query: str = None):
        """[ADMIN] Đổi Huyết Mạch của người chơi"""
        await self._set_talent(ctx, "huyetmach", target, query)

    # ── Staff commands ─────────────────────────────────────────
    @commands.command(name="adminbuff", aliases=["abuff"])
    @is_admin()
    async def admin_buff(self, ctx, stat: str, amount: int, target: discord.Member):
        """Cộng thêm thông số người chơi"""
        p = await self.bot.db.get_player(target.id)
        if not p:
            await ctx.send(embed=error(f"{target.display_name} chưa nhập môn!")); return

        stat = stat.lower()
        mapping = {
            "lt": "linh_thach_ha", "money": "linh_thach_ha",
            "exp":  "exp",
            "tl":   "stamina",
            "mau":  "hp",
            "ngo":  "ngo_tinh",
        }
        if stat not in mapping:
            await ctx.send(embed=warn(f"Stat không hợp lệ! Dùng: lt/exp/tl/mau/ngo")); return

        field = mapping[stat]
        new_val = int(p.get(field) or 0) + amount
        new_val = max(0, min(new_val, self.SQLITE_INT_MAX))
        await self.bot.db.update_player(target.id, **{field: new_val})
        sign = "+" if amount >= 0 else ""
        await ctx.send(embed=success("✅ BUFF", f"**{p['name']}** → `{stat}` {sign}**{amount:,}** = **{new_val:,}**"))

    @commands.command(name="checkadmin")
    @is_admin()
    async def checkadmin(self, ctx, target: discord.Member):
        """Kiểm tra lịch sử thao tác admin (stub - cần DB log)"""
        embed = discord.Embed(
            title=f"📋 LỊCH SỬ ADMIN: {target.display_name}",
            description="_Tính năng log đang phát triển..._",
            color=0x607D8B
        )
        await ctx.send(embed=embed)

    @commands.command(name="banacc")
    @is_admin()
    async def banacc(self, ctx, target: discord.Member, duration: str = "1d"):
        """Phong ấn tài khoản người chơi"""
        p = await self.bot.db.get_player(target.id)
        if not p:
            await ctx.send(embed=error("Người này chưa nhập môn!")); return
        await self.bot.db.update_player(target.id, status="banned")
        await ctx.send(embed=success("⛔ PHONG ẤN",
            f"Đã phong ấn **{p['name']}** trong **{duration}**\n"
            f"Dùng `,tl unban @tag` để giải trừ."))

    @commands.command(name="unban")
    @is_admin()
    async def unban(self, ctx, target: discord.Member):
        """Giải trừ phong ấn tài khoản"""
        p = await self.bot.db.get_player(target.id)
        if not p:
            await ctx.send(embed=error("Người này chưa nhập môn!")); return
        await self.bot.db.update_player(target.id, status="idle")
        await ctx.send(embed=success("✅ GIẢI TRỪ PHONG ẤN", f"Đã giải phong ấn cho **{p['name']}**"))

    @commands.command(name="settime")
    @is_admin()
    async def settime(self, ctx, minutes: int, target: discord.Member):
        """[DEBUG] Chỉnh thời gian đã tu luyện"""
        p = await self.bot.db.get_player(target.id)
        if not p:
            await ctx.send(embed=error("Người này chưa nhập môn!")); return
        seconds = minutes * 60
        await self.bot.db.update_player(target.id, total_cultivate_time=seconds)
        await ctx.send(embed=success("✅ SETTIME", f"**{p['name']}** → {minutes} phút tu luyện"))

    # ── Owner commands ─────────────────────────────────────────
    @commands.command(name="buffitem")
    @is_owner()
    async def buffitem(self, ctx, item_id: str, amount: int, target: discord.Member = None):
        """[OWNER] Trao/Thu hồi vật phẩm"""
        item = ITEMS.get(item_id)
        if not item:
            await ctx.send(embed=error(f"Item `{item_id}` không tồn tại!")); return

        if target:
            p = await self.bot.db.get_player(target.id)
            if not p:
                await ctx.send(embed=error("Người này chưa nhập môn!")); return
            await self.bot.db.add_item(target.id, item_id, amount)
            sign = "+" if amount >= 0 else ""
            await ctx.send(embed=success("✅ BUFFITEM",
                f"{sign}**{amount}x {item['name']}** → **{p['name']}**"))
        else:
            await ctx.send(embed=warn("Cần @tag người chơi hoặc 'all' (all chưa hỗ trợ)"))

    @commands.command(name="setitem")
    @is_owner()
    async def setitem(self, ctx, item_id: str, amount: int, target: discord.Member):
        """[OWNER] ĐẶT số lượng vật phẩm"""
        item = ITEMS.get(item_id)
        if not item:
            await ctx.send(embed=error(f"Item `{item_id}` không tồn tại!")); return
        p = await self.bot.db.get_player(target.id)
        if not p:
            await ctx.send(embed=error("Người này chưa nhập môn!")); return
        await self.bot.db.execute(
            "INSERT INTO inventory (user_id, item_id, quantity) VALUES (?,?,?) "
            "ON CONFLICT(user_id, item_id) DO UPDATE SET quantity=?",
            (str(target.id), item_id, amount, amount)
        )
        await ctx.send(embed=success("✅ SETITEM",
            f"**{p['name']}** → **{item['name']}** = **{amount}**"))

    @commands.command(name="findid")
    @is_admin()
    async def findid(self, ctx, *, name: str):
        """Tìm kiếm ID người chơi theo tên"""
        results = await self.bot.db.fetchall(
            "SELECT user_id, name, realm_index FROM players WHERE name LIKE ? LIMIT 10",
            (f"%{name}%",)
        )
        if not results:
            await ctx.send(embed=warn(f"Không tìm thấy ai tên **{name}**")); return
        embed = discord.Embed(title=f"🔍 KẾT QUẢ TÌM KIẾM: \"{name}\"", color=0x2196F3)
        from utils.game_data import REALMS
        for r in results:
            ri = r["realm_index"]
            rname = REALMS[ri]["name"] if ri < len(REALMS) else "???"
            embed.add_field(
                name=r["name"],
                value=f"ID: `{r['user_id']}`  •  {rname}",
                inline=False
            )
        await ctx.send(embed=embed)

    # ── Admin sub-commands ─────────────────────────────────────
    @admin.command(name="give")
    @is_admin()
    async def admin_give(self, ctx, target: discord.Member, item_id: str, quantity: int = 1):
        """Tặng vật phẩm cho người chơi"""
        item_id = item_id.lower()
        item = ITEMS.get(item_id)
        if not item:
            await ctx.send(embed=error(f"Item `{item_id}` không tồn tại!")); return
        p = await self.bot.db.get_player(target.id)
        if not p:
            await ctx.send(embed=error(f"{target.display_name} chưa nhập môn!")); return
        await self.bot.db.add_item(target.id, item_id, quantity)
        await ctx.send(embed=success("✅ ADMIN GIVE",
            f"Đã tặng **{quantity}x {item['name']}** cho **{p['name']}**"))

    @admin.command(name="lt")
    @is_admin()
    async def admin_lt(self, ctx, target: discord.Member, amount: int, tier: str = "ha"):
        """Cộng Linh Thạch cho người chơi (tier: ha/trung/cuc)"""
        p = await self.bot.db.get_player(target.id)
        if not p:
            await ctx.send(embed=error(f"{target.display_name} chưa nhập môn!")); return
        tier = tier.lower()
        if tier == "ha":
            await self.bot.db.update_player(target.id, linh_thach_ha=p["linh_thach_ha"]+amount)
        elif tier == "trung":
            await self.bot.db.update_player(target.id, linh_thach_trung=p["linh_thach_trung"]+amount)
        elif tier == "cuc":
            await self.bot.db.update_player(target.id, linh_thach_cuc=p["linh_thach_cuc"]+amount)
        await ctx.send(embed=success("✅ ADMIN LT",
            f"Nạp **{amount:,} {tier.upper()} LT** cho **{p['name']}**"))

    @admin.command(name="reset")
    @is_admin()
    async def admin_reset(self, ctx, target: discord.Member):
        """Xóa toàn bộ nhân vật của người chơi (không thể hoàn tác)"""
        p = await self.bot.db.get_player(target.id)
        if not p:
            await ctx.send(embed=error("Người này chưa nhập môn!")); return
        await self.bot.db.execute("DELETE FROM players WHERE user_id=?",    (str(target.id),))
        await self.bot.db.execute("DELETE FROM inventory WHERE user_id=?",  (str(target.id),))
        await self.bot.db.execute("DELETE FROM equipment WHERE user_id=?",  (str(target.id),))
        await self.bot.db.execute("DELETE FROM tower WHERE user_id=?",      (str(target.id),))
        await ctx.send(embed=success("✅ RESET", f"Đã reset nhân vật **{p['name']}**"))

    @admin.command(name="broadcast", aliases=["bc_admin"])
    @is_admin()
    async def broadcast(self, ctx, *, message: str):
        """Gửi thông báo từ Admin tới kênh hiện tại"""
        embed = discord.Embed(
            title="📢 THÔNG BÁO TỪ ADMIN",
            description=message,
            color=0xFF9800
        )
        embed.set_footer(text=f"Từ: {ctx.author.display_name}  •  Tu Tiên Bot v3")
        await ctx.send(embed=embed)

    @admin.command(name="setlv")
    @is_admin()
    async def setlv(self, ctx, target: discord.Member, realm_idx: int, tier: int = 1):
        """Set Cảnh Giới + Tầng cho người chơi (theo index thực, khác ,tl set daicanhgioi)"""
        from utils.game_data import REALMS, get_realm_name, scale_stats_for_realm_change
        p = await self.bot.db.get_player(target.id)
        if not p:
            await ctx.send(embed=error("Người này chưa nhập môn!")); return
        realm_idx = max(0, min(realm_idx, len(REALMS)-1))
        tier      = max(1, min(tier, REALMS[realm_idx]["tiers"]))
        stats = scale_stats_for_realm_change(p, realm_idx, tier)
        new_s = stats["new"]
        await self.bot.db.update_player(
            target.id, realm_index=realm_idx, realm_tier=tier, exp=0,
            atk=new_s["atk"], def_=new_s["def_"], hp=new_s["hp_max"],
            hp_max=new_s["hp_max"], spd=new_s["spd"], luc_chien=new_s["luc_chien"])
        await sync_realm_role(self.bot, target, realm_idx)
        new_name = get_realm_name({"realm_index":realm_idx,"realm_tier":tier})
        await ctx.send(embed=success("✅ SET LEVEL",
            f"**{p['name']}** → **{new_name}**\n"
            f"⚔️ ATK: `{stats['old']['atk']:,.0f}` → `{new_s['atk']:,.0f}`\n"
            f"🛡️ DEF: `{stats['old']['def_']:,.0f}` → `{new_s['def_']:,.0f}`\n"
            f"❤️ HP: `{stats['old']['hp_max']:,.0f}` → `{new_s['hp_max']:,.0f}`\n"
            f"⚡ Lực Chiến: `{new_s['luc_chien']:,.0f}`"))

    @admin.command(name="info")
    @is_admin()
    async def admin_info(self, ctx, target: discord.Member):
        """Xem thông tin chi tiết (ID, passport, cảnh giới...) của người chơi"""
        p = await self.bot.db.get_player(target.id)
        if not p:
            await ctx.send(embed=error("Chưa nhập môn!")); return
        from utils.game_data import get_realm_name
        from utils.embeds import fmt, fmt_lt
        embed = discord.Embed(title=f"🔍 ADMIN INFO: {p['name']}", color=0x607D8B)
        embed.add_field(name="ID",        value=p["user_id"],          inline=True)
        embed.add_field(name="Passport",  value=p.get("passport","?"), inline=True)
        embed.add_field(name="Cảnh Giới", value=get_realm_name(p),     inline=True)
        embed.add_field(name="Lực Chiến", value=fmt(p.get("luc_chien",0)), inline=True)
        embed.add_field(name="Trạng Thái",value=p["status"],           inline=True)
        embed.add_field(name="Linh Thạch",
            value=fmt_lt(p["linh_thach_ha"],p["linh_thach_trung"],p["linh_thach_cuc"]),
            inline=False)
        await ctx.send(embed=embed)

    @admin.command(name="buff-all")
    @is_owner()
    async def admin_buff_all(self, ctx, amount: int):
        """[OWNER] Tặng Linh Thạch toàn server"""
        await self.bot.db.execute(
            "UPDATE players SET linh_thach_ha = linh_thach_ha + ?", (amount,)
        )
        await ctx.send(embed=success("✅ BUFF ALL",
            f"Đã tặng **{amount:,} Hạ LT** cho toàn bộ người chơi!"))

    @admin.command(name="bank")
    @is_owner()
    async def admin_bank(self, ctx, state: str = "on"):
        """[OWNER] Đóng/Mở chuyển khoản toàn server"""
        state = state.lower()
        # Lưu vào bot config (stub - cần implement theo hệ thống config của bot)
        self.bot._bank_enabled = (state == "on")
        status = "🟢 Mở" if state == "on" else "🔴 Đóng"
        await ctx.send(embed=success("🏦 BANK", f"Chuyển khoản toàn server: **{status}**"))

    @admin.command(name="staff")
    @is_owner()
    async def admin_staff(self, ctx, state: str = "on"):
        """[OWNER] Đóng/Mở quyền Staff"""
        state = state.lower()
        self.bot._staff_enabled = (state == "on")
        status = "🟢 Bật" if state == "on" else "🔴 Tắt"
        await ctx.send(embed=success("👑 STAFF", f"Quyền Sáng Thế & Thượng Đế Lệnh: **{status}**"))

    @admin.command(name="clear-items")
    @is_owner()
    async def admin_clear_items(self, ctx):
        """[OWNER] Dọn dẹp túi đồ lạm phát đồ hiếm"""
        embed = discord.Embed(
            title="🧹 CLEAR ITEMS",
            description=(
                "⚠️ **Thao tác này sẽ xóa đồ hiếm dư thừa!**\n\n"
                "Xác nhận bằng cách reply `CONFIRM` trong 30 giây."
            ),
            color=0xFF5722
        )
        await ctx.send(embed=embed)
        # Stub - cần implement confirm flow nếu muốn

    @admin.command(name="sync")
    @is_owner()
    async def admin_sync(self, ctx, old_uid: str, new_uid: str):
        """[OWNER] Đồng bộ dữ liệu người chơi (đổi UID)"""
        tables = ["players", "inventory", "equipment", "tower"]
        for table in tables:
            try:
                await self.bot.db.execute(
                    f"UPDATE {table} SET user_id=? WHERE user_id=?",
                    (new_uid, old_uid)
                )
            except Exception:
                pass
        await ctx.send(embed=success("✅ SYNC",
            f"Đã chuyển dữ liệu từ `{old_uid}` → `{new_uid}`"))

    @admin.command(name="doicuc")
    @is_owner()
    async def admin_doicuc(self, ctx, target: discord.Member = None):
        """[OWNER] Quy đổi cưỡng chế sang Cực Phẩm LT"""
        if target:
            p = await self.bot.db.get_player(target.id)
            if not p:
                await ctx.send(embed=error("Người này chưa nhập môn!")); return
            # Stub - đổi tất cả vật phẩm dư thừa sang LT Cực Phẩm
            await ctx.send(embed=success("✅ DOICUC",
                f"Đã quy đổi đồ dư của **{p['name']}** sang Cực Phẩm LT"))
        else:
            await ctx.send(embed=warn("Dùng: `,tl admin doicuc @tag` hoặc `,tl admin doicuc all`"))

    # ── Sub-admin system (chỉ Đấng Sáng Thế thêm/xóa được) ─────
    @admin.command(name="add")
    @is_owner()
    async def admin_add(self, ctx, target: discord.Member):
        """[OWNER] Thêm Sub-Admin (quyền như Admin nhưng thua Sáng Thế 1 bậc)"""
        if await ctx.bot.is_owner(target) or (ctx.guild and target.id == ctx.guild.owner_id):
            await ctx.send(embed=warn(f"**{target.display_name}** đã là Đấng Sáng Thế!")); return
        if await self.bot.db.is_bot_admin(target.id):
            await ctx.send(embed=warn(f"**{target.display_name}** đã là Admin rồi!")); return
        ok = await self.bot.db.add_bot_admin(target.id, ctx.author.id)
        if not ok:
            await ctx.send(embed=error("Không thể thêm Admin (đã tồn tại?)")); return
        await ctx.send(embed=success("👑 THÊM ADMIN",
            f"**{target.display_name}** giờ đã là **Admin** (thua Đấng Sáng Thế 1 bậc)."))

    @admin.command(name="remove", aliases=["del","xoa"])
    @is_owner()
    async def admin_remove(self, ctx, target: discord.Member):
        """[OWNER] Xóa quyền Sub-Admin"""
        ok = await self.bot.db.remove_bot_admin(target.id)
        if not ok:
            await ctx.send(embed=warn(f"**{target.display_name}** không phải Admin (do Sáng Thế thêm)!")); return
        await ctx.send(embed=success("🗑️ XÓA ADMIN", f"Đã xóa quyền Admin của **{target.display_name}**"))

    @admin.command(name="list")
    @is_admin()
    async def admin_list(self, ctx):
        """Xem danh sách Sub-Admin"""
        rows = await self.bot.db.list_bot_admins()
        embed = discord.Embed(title="👑 DANH SÁCH ADMIN", color=0xFFD700)
        if not rows:
            embed.description = "_Chưa có Sub-Admin nào._"
        else:
            lines = []
            for r in rows:
                member = ctx.guild.get_member(int(r["user_id"])) if ctx.guild else None
                name = member.display_name if member else r["user_id"]
                lines.append(f"• **{name}** (ID: `{r['user_id']}`)")
            embed.description = "\n".join(lines)
        embed.set_footer(text="Sub-Admin có quyền như Admin, thua Đấng Sáng Thế 1 bậc")
        await ctx.send(embed=embed)

    # ── Set group: ,tl set <stat> ... ──────────────────────────
    @commands.group(name="set", invoke_without_command=True)
    @is_admin()
    async def set_group(self, ctx):
        embed = discord.Embed(title="⚙️ LỆNH SET (ADMIN)", color=0x607D8B)
        embed.add_field(
            name="Danh sách",
            value=(
                "`,tl set daicanhgioi [1-70] [@tag]` — Set Đại Cảnh Giới (Tầng 1)\n"
                "`,tl set dao [thiendao/thiensu] [@tag]` — Gán Đạo đặc biệt"
            ),
            inline=False
        )
        await ctx.send(embed=embed)

    @set_group.command(name="daicanhgioi", aliases=["dcg"])
    @is_admin()
    async def set_daicanhgioi(self, ctx, level: int, target: discord.Member = None):
        """[ADMIN] Set Đại Cảnh Giới (1-70) cho người chơi"""
        target = target or ctx.author
        p = await self.bot.db.get_player(target.id)
        if not p:
            await ctx.send(embed=error(f"{target.display_name} chưa nhập môn!")); return
        if int(p.get("vt_locked", 0) or 0) == 1:
            await ctx.send(embed=warn(
                f"**{p['name']}** đang ở cõi **Vô Thượng** — không thể override!\n"
                f"Dùng `,tl thu_vothuong @tag` trước."
            )); return
        if level < 1 or level > len(REALMS):
            await ctx.send(embed=warn(f"Đại Cảnh Giới phải trong khoảng `1-{len(REALMS)}`!")); return
        realm_idx = level - 1
        from utils.game_data import scale_stats_for_realm_change
        from utils.embeds import fmt
        stats = scale_stats_for_realm_change(p, realm_idx, 1)
        new_s = stats["new"]

        # Áp dụng buff chuyển sinh (+20% mỗi lần CS)
        prestige = int(p.get("prestige", 0) or 0)
        cs_bonus = 1.0 + prestige * 0.20
        if cs_bonus > 1.0:
            new_s["atk"]     = round(new_s["atk"]    * cs_bonus, 2)
            new_s["def_"]    = round(new_s["def_"]   * cs_bonus, 2)
            new_s["hp_max"]  = round(new_s["hp_max"] * cs_bonus, 2)
            new_s["spd"]     = round(new_s["spd"]    * cs_bonus, 2)
            new_s["luc_chien"] = round(new_s["atk"] * 2 + new_s["def_"] * 1.2 + new_s["hp_max"] * 0.005 + new_s["spd"] * 0.8, 2)

        await self.bot.db.update_player(
            target.id, realm_index=realm_idx, realm_tier=1, exp=0,
            atk=new_s["atk"], def_=new_s["def_"], hp=new_s["hp_max"],
            hp_max=new_s["hp_max"], spd=new_s["spd"], luc_chien=new_s["luc_chien"])
        await sync_realm_role(self.bot, target, realm_idx)
        new_name = get_realm_name({"realm_index": realm_idx, "realm_tier": 1})
        cs_note = f"\n🔄 Buff CS x{cs_bonus:.1f} ({prestige} lần CS)" if prestige > 0 else ""
        await ctx.send(embed=success("✅ SET ĐẠI CẢNH GIỚI",
            f"**{p['name']}** → **Đại Cảnh Giới {level}**\n```{new_name}```\n"
            f"⚔️ ATK: `{fmt(stats['old']['atk'])}` → `{fmt(new_s['atk'])}`\n"
            f"🛡️ DEF: `{fmt(stats['old']['def_'])}` → `{fmt(new_s['def_'])}`\n"
            f"❤️ HP: `{fmt(stats['old']['hp_max'])}` → `{fmt(new_s['hp_max'])}`\n"
            f"⚡ Lực Chiến: `{fmt(new_s['luc_chien'])}`{cs_note}"))

    @set_group.command(name="dao")
    @is_admin()
    async def set_dao(self, ctx, dao_key: str, target: discord.Member = None):
        """[ADMIN] Gán Đạo đặc biệt (thiendao/thiensu) cho người chơi"""
        target = target or ctx.author
        dao_key = dao_key.lower()
        p = await self.bot.db.get_player(target.id)
        if not p:
            await ctx.send(embed=error(f"{target.display_name} chưa nhập môn!")); return
        if dao_key not in DAO:
            valid = ", ".join(DAO.keys())
            await ctx.send(embed=warn(f"Đạo không hợp lệ! Dùng: `{valid}`")); return
        await self.bot.db.update_player(target.id, dao=dao_key)
        dao_info = DAO[dao_key]
        await ctx.send(embed=success("✅ SET ĐẠO",
            f"**{p['name']}** → {dao_info['icon']} **{dao_info['name']}**\n_{dao_info['desc']}_"))


    # ══ RELOAD / RESTART ════════════════════════════════════
    @admin.command(name="reload", aliases=["rl"])
    @is_owner()
    async def reload_cog(self, ctx, cog: str = None):
        """Reload 1 cog hoặc tất cả cogs"""
        import os, importlib
        # Reload game_data trước để dữ liệu mới nhất
        try:
            import utils.game_data as gd
            importlib.reload(gd)
        except Exception as e:
            pass

        if cog:
            # Reload 1 cog cụ thể
            ext = f"cogs.{cog}" if not cog.startswith("cogs.") else cog
            try:
                await self.bot.reload_extension(ext)
                await ctx.send(embed=success("🔄 RELOAD XONG", f"`{ext}` đã được reload!"))
            except Exception as e:
                await ctx.send(embed=error(f"❌ Lỗi reload `{ext}`:\n`{e}`"))
        else:
            # Reload tất cả cogs
            failed = []
            done = []
            for ext in list(self.bot.extensions.keys()):
                try:
                    await self.bot.reload_extension(ext)
                    done.append(ext.replace("cogs.", ""))
                except Exception as e:
                    failed.append(f"`{ext}`: {e}")
            msg = f"✅ Reload xong: {', '.join(done)}"
            if failed:
                msg += f"\n❌ Lỗi: {chr(10).join(failed)}"
            await ctx.send(embed=success("🔄 RELOAD TẤT CẢ", msg))

    @admin.command(name="restart", aliases=["reboot"])
    @is_owner()
    async def restart_bot(self, ctx):
        """Restart toàn bộ bot"""
        import os, sys
        await ctx.send(embed=success("🔁 RESTART", "Bot đang khởi động lại..."))
        os.execv(sys.executable, [sys.executable] + sys.argv)

    @admin.command(name="realmrole", aliases=["dotpharole", "rolecanhgioi"])
    async def admin_realmrole(self, ctx, trang_thai: str = None):
        """[ADMIN SERVER] Bật/tắt tự động gán role Discord theo đại cảnh giới.
        Khi bật: bot tự tạo role `🌌 <Tên Cảnh Giới>` và gán cho người chơi mỗi khi
        họ đột phá lên đại cảnh giới mới (cần quyền Manage Roles cho bot)."""
        if not ctx.guild:
            await ctx.send(embed=warn("Lệnh này chỉ dùng được trong server.")); return
        is_owner_ = ctx.author.id == ctx.guild.owner_id or await ctx.bot.is_owner(ctx.author)
        if not (is_owner_ or ctx.author.guild_permissions.administrator):
            await ctx.send(embed=warn("🚫 Cần quyền **Quản Trị Viên** của server để đổi cài đặt này!"))
            return

        cfg = await self.bot.db.get_guild_config(ctx.guild.id)
        cur = bool(cfg.get("realm_role_enabled"))

        if trang_thai is None:
            await ctx.send(embed=discord.Embed(
                title="🌌 ROLE THEO CẢNH GIỚI",
                description=(
                    f"Trạng thái hiện tại: {'🟢 **ĐANG BẬT**' if cur else '🔴 **ĐANG TẮT**'}\n\n"
                    f"Dùng `,tl admin realmrole on` hoặc `off` để đổi.\n\n"
                    f"💡 Khi bật, bot tự tạo role dạng `🌌 <Tên Cảnh Giới>` và gán cho "
                    f"người chơi mỗi khi họ đột phá đại cảnh giới (cần quyền **Manage Roles**, "
                    f"và role của bot phải nằm **trên** vị trí role cảnh giới)."
                ),
                color=0x9C6BFF
            ))
            return

        new_state = trang_thai.lower() in ("on", "bat", "true", "1", "enable")
        if not new_state and trang_thai.lower() not in ("off", "tat", "false", "0", "disable"):
            await ctx.send(embed=warn("Dùng `on` hoặc `off`.")); return

        if new_state and not ctx.guild.me.guild_permissions.manage_roles:
            await ctx.send(embed=warn(
                "⚠️ Bot chưa có quyền **Manage Roles** trong server này!\n"
                "Cấp quyền đó trước rồi thử bật lại."
            )); return

        await self.bot.db.set_guild_config(ctx.guild.id, realm_role_enabled=1 if new_state else 0)
        await ctx.send(embed=success(
            "✅ ĐÃ CẬP NHẬT",
            f"Role theo cảnh giới: {'🟢 **BẬT**' if new_state else '🔴 **TẮT**'}"
        ))

    @admin.error
    async def admin_error(self, ctx, err):
        if isinstance(err, commands.CheckFailure):
            await ctx.send(embed=discord.Embed(
                description="🚫 Chỉ Admin mới dùng được lệnh này!",
                color=0xF44336
            ))

    @set_group.error
    async def set_group_error(self, ctx, err):
        if isinstance(err, commands.CheckFailure):
            await ctx.send(embed=discord.Embed(
                description="🚫 Chỉ Admin mới dùng được lệnh này!",
                color=0xF44336
            ))



    def _is_creator_only():
        """Chỉ bot owner (Đấng Sáng Thế) mới dùng được — không phải admin thường."""
        async def predicate(ctx):
            # Chỉ chấp nhận bot owner theo Discord app
            if await ctx.bot.is_owner(ctx.author):
                return True
            raise commands.CheckFailure("vothuong_not_creator")
        return commands.check(predicate)

    @commands.command(name="vothuong", aliases=["vt", "phong_vothuong", "sangthe_cap"])
    @_is_creator_only()
    async def vothuong(self, ctx, target: discord.Member = None):
        """[☯️ ĐẤNG SÁNG THẾ] Phong Vô Thượng Đạo Tổ — stats vô cực, one-hit tất cả."""
        target = target or ctx.author
        p = await self.bot.db.get_player(target.id)
        if not p:
            await ctx.send(embed=error(f"**{target.display_name}** chưa nhập môn!")); return

        old_realm = get_realm_name(p)

        # Float 1e200 — đủ 1-hit bất kỳ ai, không gây overflow
        _MAX = 1e200

        await self.bot.db.update_player(
            target.id,
            realm_index      = 49,          # Đại Cảnh Giới 50 — tối thượng
            realm_tier       = 1,
            dao              = "thiendao",  # ×10,000 toàn bộ stats
            atk              = _MAX,
            def_             = _MAX,
            hp               = _MAX,
            hp_max           = _MAX,
            spd              = _MAX,
            crit             = 100.0,       # 100% crit mọi đòn
            luck             = 999_999,
            linh_thach_ha    = 9_223_372_036_854_775,
            linh_thach_trung = 9_223_372_036_854_775,
            linh_thach_cuc   = 9_223_372_036_854_775,
            exp              = 0,
            luc_chien        = _MAX,
            # Đánh dấu Vô Thượng để chặn scale_stats override
            vt_locked        = 1,
        )

        new_realm = get_realm_name({"realm_index": 49, "realm_tier": 1})

        embed = discord.Embed(
            title="☯️ VÔ THƯỢNG ĐẠO TỔ 🌌",
            description=(
                f"**{p['name']}** đã được **Đấng Sáng Thế** ban phong\n"
                f"đạt đến cõi **VÔ THƯỢNG** siêu việt Tam Giới!"
            ),
            color=0xFFFFFF
        )
        embed.add_field(name="Cảnh Giới",  value=f"`{old_realm}` → ✨ **{new_realm}**", inline=False)
        embed.add_field(name="⚔️ ATK",     value="`∞ Vô Cực`",   inline=True)
        embed.add_field(name="🛡️ DEF",     value="`∞ Vô Cực`",   inline=True)
        embed.add_field(name="❤️ HP",      value="`∞ Vô Cực`",   inline=True)
        embed.add_field(name="⚡ SPD",     value="`∞ Vô Cực`",   inline=True)
        embed.add_field(name="💥 CRIT",    value="`100% — Mọi đòn đều Bạo Kích`", inline=True)
        embed.add_field(name="🌠 Đạo",     value="`Thiên Đạo ×10,000`",           inline=True)
        embed.add_field(
            name="📜 Thiên Cơ",
            value="_Nhất kiếm phá hư không — vạn pháp bất khả xâm._",
            inline=False
        )
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.set_footer(text="☯️ Ban phong bởi Đấng Sáng Thế  •  Tu Tiên Bot v4")
        await ctx.send(embed=embed)

    @commands.command(name="thu_vothuong", aliases=["thuvt", "thu_vt", "huy_vothuong"])
    @_is_creator_only()
    async def thu_vothuong(self, ctx, target: discord.Member = None):
        """[☯️ ĐẤNG SÁNG THẾ] Thu hồi Vô Thượng — reset về căn cơ ban đầu."""
        target = target or ctx.author
        p = await self.bot.db.get_player(target.id)
        if not p:
            await ctx.send(embed=error(f"**{target.display_name}** chưa nhập môn!")); return

        # Reset về Luyện Khí tầng 1, stats mặc định
        await self.bot.db.update_player(
            target.id,
            realm_index = 0,
            realm_tier  = 1,
            dao         = "nhapdao",   # Chính Đạo mặc định
            atk         = 100,
            def_        = 50,
            hp          = 1000,
            hp_max      = 1000,
            spd         = 50,
            crit        = 5.0,
            luck        = 0,
            exp         = 0,
            luc_chien   = 0,
        )
        embed = discord.Embed(
            title="🌑 THU HỒI VÔ THƯỢNG",
            description=(
                f"Đấng Sáng Thế đã thu hồi Vô Thượng của **{p['name']}**.\n"
                f"Nhân vật đã trở về **Luyện Khí Tầng 1**."
            ),
            color=0x607D8B
        )
        embed.set_footer(text="☯️ Thu hồi bởi Đấng Sáng Thế  •  Tu Tiên Bot v4")
        await ctx.send(embed=embed)

    @vothuong.error
    async def vothuong_error(self, ctx, err):
        if isinstance(err, commands.CheckFailure):
            await ctx.send(embed=discord.Embed(
                description="☯️ **Lệnh này chỉ dành cho Đấng Sáng Thế!**\nNgươi chưa đủ tư cách.",
                color=0xF44336
            ))

    @thu_vothuong.error
    async def thu_vothuong_error(self, ctx, err):
        if isinstance(err, commands.CheckFailure):
            await ctx.send(embed=discord.Embed(
                description="☯️ **Lệnh này chỉ dành cho Đấng Sáng Thế!**\nNgươi chưa đủ tư cách.",
                color=0xF44336
            ))


async def setup(bot):
    await bot.add_cog(Admin(bot))

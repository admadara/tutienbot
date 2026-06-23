"""cogs/pvp.py v5 - PvP nâng cấp: pk menu + stats + top daily"""
import discord
from discord.ext import commands
import random, asyncio, time, aiohttp

from utils.helpers import require_player, require_idle, now
from utils.embeds import *
from utils.embeds import bar, bar_color, realm_icon
from utils.game_data import get_realm_name, ITEMS, REALMS
from utils.persistent_cache import PersistentCache

def _s(n):
    return fmt(n)

def _safe(p, k, d=0):
    v = p.get(k); return v if v is not None else d

THIENDAO_MULT = 10000  # Thiên Đạo nhân 10000 lần

def _get_effective_stats(p, eq=None, bf=None):
    """Trả về stats hiệu dụng, nhân 10000 nếu là Thiên Đạo.
    eq = dict trang bị từ get_equipment()
    bf = dict buff_type->pct từ bảng buffs (bf_atk_pct, bf_def_pct, bf_hp_pct, bf_spd_pct, bf_crit)"""
    mult = THIENDAO_MULT if p.get("dao","") == "thiendao" else 1
    atk    = float(_safe(p,"atk",100)) * mult
    def_   = float(_safe(p,"def_",50)) * mult
    hp_max = float(_safe(p,"hp_max",1000)) * mult
    spd    = float(_safe(p,"spd",50)) * mult
    crit   = float(_safe(p,"crit",5.0))   # % (5.0 = 5%)
    luck   = float(_safe(p,"luck",0))
    life_steal  = 0.0  # % hút máu
    ignore_def  = 0.0  # % phá giáp

    # Cộng chỉ số từ trang bị
    if eq:
        for slot_data in eq.values():
            itm = ITEMS.get(slot_data.get("item_id",""), {})
            enh = slot_data.get("enhance", 0)
            enh_mult = 1 + enh * 0.05
            atk  += float(itm.get("base_atk", 0)) * enh_mult * mult
            def_ += float(itm.get("base_def", 0)) * enh_mult * mult
            crit += float(itm.get("crit_bonus", 0)) * 100
            life_steal += float(itm.get("life_steal", 0))
            ignore_def += float(itm.get("ignore_def", 0))

    # Cộng buff từ bi_kíp / đan dược
    if bf:
        atk    = atk    * (1 + bf.get("atk_pct", 0) / 100)
        def_   = def_   * (1 + bf.get("def_pct", 0) / 100)
        hp_max = hp_max * (1 + bf.get("hp_pct",  0) / 100)
        spd    = spd    * (1 + bf.get("spd_pct",  0) / 100)
        crit  += bf.get("crit", 0)

    # Giới hạn crit tối đa 100%
    crit = min(crit, 100.0)
    return {
        "atk":        atk,
        "def_":       def_,
        "hp_max":     hp_max,
        "spd":        spd,
        "crit":       crit,
        "luck":       luck,
        "life_steal": life_steal,
        "ignore_def": ignore_def,
    }

def _calc_luc_chien(p):
    ri   = int(_safe(p,"realm_index",0))
    tier = int(_safe(p,"realm_tier",1))
    eff  = _get_effective_stats(p)
    atk  = eff["atk"]; def_ = eff["def_"]; hp = eff["hp_max"]
    spd  = eff["spd"]; crit = eff["crit"]; luck = eff["luck"]
    base = atk*2 + def_ + hp*0.5 + spd*0.3 + crit*10 + luck*0.1
    tier_mult  = (1.20)**(tier-1) if tier>1 else 1.0
    realm_mult = 2**ri if ri>0 else 1.0
    import math
    result = base * tier_mult * realm_mult
    if math.isinf(result) or math.isnan(result):
        return 1e18
    return result

def _simulate_battle(A, B, eq_a=None, eq_b=None, bf_a=None, bf_b=None):
    """Mô phỏng trận đấu chi tiết, trả về (winner, loser, log, a_hp_pct, b_hp_pct)
    eq_a, eq_b: dict trang bị từ get_equipment() để tính hút máu, phá giáp, crit_bonus"""
    ea = _get_effective_stats(A, eq_a, bf_a)
    eb = _get_effective_stats(B, eq_b, bf_b)
    a_hp_max = ea["hp_max"]; b_hp_max = eb["hp_max"]
    a_hp = a_hp_max; b_hp = b_hp_max
    a_def= ea["def_"];   b_def= eb["def_"]
    log  = []

    def _calc_dmg(atk, def_, ignore_def, crit):
        """Tính sát thương với công thức tỉ lệ — không bao giờ ra 0 hay 1 vô lý"""
        effective_def = def_ * (1.0 - ignore_def)
        # Damage reduction tối đa 85%, tỉ lệ theo DEF/(DEF+ATK)
        dr = min(0.85, effective_def / (effective_def + atk + 1))
        base = atk * random.uniform(0.85, 1.15) * (1 - dr)
        if crit:
            base *= 2
        return max(int(atk * 0.01), int(base))  # tối thiểu 1% ATK

    MAX_ROUNDS = 100
    for rnd in range(1, MAX_ROUNDS + 1):
        if a_hp <= 0 or b_hp <= 0: break
        # A đánh B
        ac = random.random() < ea["crit"] / 100.0
        ad = _calc_dmg(ea["atk"], b_def, ea["ignore_def"], ac)
        b_hp -= ad
        if ea["life_steal"] > 0:
            heal = int(ad * ea["life_steal"])
            a_hp = min(a_hp + heal, a_hp_max)
        extras = ""
        if ac: extras += " **BẠO KÍCH!**"
        if ea["life_steal"] > 0: extras += f" 🩸+{_s(int(ad*ea['life_steal']))}"
        log.append(f"`Hiệp {rnd}` {'💥' if ac else '⚔️'} **{A['name']}** đánh `{_s(ad)}`{extras}")
        if b_hp<=0: break
        # B đánh A
        bc = random.random() < eb["crit"] / 100.0
        bd = _calc_dmg(eb["atk"], a_def, eb["ignore_def"], bc)
        a_hp -= bd
        if eb["life_steal"] > 0:
            heal = int(bd * eb["life_steal"])
            b_hp = min(b_hp + heal, b_hp_max)
        extras2 = ""
        if bc: extras2 += " **BẠO KÍCH!**"
        if eb["life_steal"] > 0: extras2 += f" 🩸+{_s(int(bd*eb['life_steal']))}"
        log.append(f"`Hiệp {rnd}` {'💥' if bc else '⚔️'} **{B['name']}** đánh `{_s(bd)}`{extras2}")
    # Sau 100 hiệp mà cả 2 còn sống: xét dame trung bình so với máu
    if a_hp > 0 and b_hp > 0:
        # Tính dame trung bình mỗi bên gây ra (không crit, không rand)
        a_avg_dmg = _calc_dmg(ea["atk"], b_def, ea["ignore_def"], False)
        b_avg_dmg = _calc_dmg(eb["atk"], a_def, eb["ignore_def"], False)
        # Số hiệp cần để tiêu diệt đối thủ (dame/máu)
        a_kills_in = b_hp / a_avg_dmg if a_avg_dmg > 0 else float("inf")
        b_kills_in = a_hp / b_avg_dmg if b_avg_dmg > 0 else float("inf")
        # Ai giết nhanh hơn (cần ít hiệp hơn) thắng; hòa thì xét HP % còn lại
        if a_kills_in < b_kills_in:
            winner_overtime = A
        elif b_kills_in < a_kills_in:
            winner_overtime = B
        else:
            winner_overtime = A if (a_hp / a_hp_max) >= (b_hp / b_hp_max) else B
        log.append(
            f"⏰ **HẾT 100 HIỆP!** Phán quyết: **{winner_overtime['name']}** "
            f"thắng nhờ tốc độ hạ địch vượt trội! "
            f"(Cần `{a_kills_in:.1f}` vs `{b_kills_in:.1f}` hiệp)"
        )
        # Ép máu để winner/loser logic bên dưới đúng
        if winner_overtime == A:
            b_hp = 0
        else:
            a_hp = 0
    winner = A if a_hp > b_hp else B
    loser  = B if winner == A else A
    a_pct = max(0.0, a_hp / a_hp_max) if a_hp_max > 0 else 0.0
    b_pct = max(0.0, b_hp / b_hp_max) if b_hp_max > 0 else 0.0
    return winner, loser, log, a_pct, b_pct

class PvP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._pending = PersistentCache(bot, "pvp_pending")       # challenger_id -> {target_id, expire, bet}
        self._daily_wins = PersistentCache(bot, "pvp_daily_wins") # uid -> {wins, date}

    async def cog_load(self):
        await self._pending.load()
        await self._daily_wins.load()

    async def cog_unload(self):
        await self._pending.save()
        await self._daily_wins.save()

    def _today(self):
        import datetime
        return datetime.datetime.utcnow().strftime("%Y-%m-%d")

    def _add_daily_win(self, uid):
        today = self._today()
        uid = str(uid)
        if uid not in self._daily_wins or self._daily_wins[uid]["date"] != today:
            self._daily_wins[uid] = {"wins": 0, "date": today, "name": ""}
        self._daily_wins[uid]["wins"] += 1

    def _set_daily_name(self, uid, name):
        uid = str(uid)
        if uid in self._daily_wins:
            self._daily_wins[uid]["name"] = name

    # ── ,tl pk  (menu) ──────────────────────────────────────────
    @commands.group(name="pk", aliases=["duel","pvp"], invoke_without_command=True)
    async def pk(self, ctx, target: discord.Member = None, bet: int = 0):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        if target:
            await self._do_challenge(ctx, target, bet, player)
            return
        # Hiện menu
        embed = discord.Embed(
            title="⚔️  HỆ THỐNG PK  ⚔️",
            color=0xFF5722
        )
        embed.description = (
            "**👊 `,tl pk @user`** — Thách đấu ngay (không cược)\n"
            "**👊 `,tl pk @user [số LT]`** — Thách đấu có cược (trừ thẳng LT)\n"
            "**📊 `,tl pk stats`** — Xem hồ sơ chiến lực của bạn\n"
            "**🏆 `,tl pk top`** — BXH Cao Thủ (Toàn Cầu)\n"
            "**📅 `,tl pk top daily`** — BXH Chiến Thần (Hôm Nay)\n\n"
            "⚡ _Đánh ngay — không cần chấp nhận. Cược bị trừ thẳng!_"
        )
        embed.set_footer(text="Tu Tiên Bot v4  •  ,tl pk @user để thách đấu")
        await ctx.send(embed=embed)

    @pk.command(name="stats", aliases=["stat","info","hoso"])
    async def pk_stats(self, ctx):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        """Xem hồ sơ chiến lực PK"""
        ri   = int(_safe(player,"realm_index",0))
        lc   = _calc_luc_chien(player)
        wins = int(_safe(player,"total_pk_win",0))
        # Daily wins
        uid  = str(ctx.author.id)
        today= self._today()
        d_wins = 0
        if uid in self._daily_wins and self._daily_wins[uid]["date"] == today:
            d_wins = self._daily_wins[uid]["wins"]

        embed = discord.Embed(title="📊 HỒ SƠ CHIẾN LỰC", color=realm_color(ri))
        embed.set_author(name=player["name"], icon_url=ctx.author.display_avatar.url)
        embed.add_field(name="🌌 Cảnh Giới",    value=get_realm_name(player), inline=True)
        embed.add_field(name="⚡ Lực Chiến",    value=f"`{_s(lc)}`",          inline=True)
        embed.add_field(name="\u200b",           value="\u200b",               inline=True)
        embed.add_field(name="⚔️ ATK",          value=f"`{_s(_safe(player,'atk',100))}`",   inline=True)
        embed.add_field(name="🛡️ DEF",          value=f"`{_s(_safe(player,'def_',50))}`",   inline=True)
        embed.add_field(name="❤️ HP",           value=f"`{_s(_safe(player,'hp_max',1000))}`",inline=True)
        embed.add_field(name="⚡ SPD",          value=f"`{_s(_safe(player,'spd',50))}`",    inline=True)
        embed.add_field(name="💥 CRIT",         value=f"`{_safe(player,'crit',5):.1f}%`",   inline=True)
        embed.add_field(name="\u200b",           value="\u200b",               inline=True)
        embed.add_field(name="🏆 PK Thắng (Tổng)", value=f"`{wins:,}`",        inline=True)
        embed.add_field(name="📅 Thắng Hôm Nay",  value=f"`{d_wins}`",         inline=True)
        embed.set_footer(text="Tu Tiên Bot v4  •  ,tl pk top — BXH")
        await ctx.send(embed=embed)

    @pk.command(name="top", aliases=["bxh","rank","leaderboard"])
    async def pk_top(self, ctx, scope: str = ""):
        if scope.lower() in ("daily","ngay","today","hom_nay"):
            await self._top_daily(ctx)
        else:
            await self._top_global(ctx)

    async def _top_global(self, ctx):
        rows = await self.bot.db.get_leaderboard(order="total_pk_win", limit=10)
        embed = discord.Embed(title="🏆 BXH CAO THỦ TOÀN CẦU", color=0xFFD700)
        medals = ["🥇","🥈","🥉"] + ["🏅"]*7
        for i, p in enumerate(rows):
            lc  = _calc_luc_chien(p)
            wins= int(_safe(p,"total_pk_win",0))
            embed.add_field(
                name=f"{medals[i]} {p['name']}",
                value=f"⚔️ `{wins:,}` thắng  |  🌌 {get_realm_name(p)}  |  ⚡ `{_s(lc)}`",
                inline=False
            )
        if not rows:
            embed.description = "_Chưa có người chơi nào._"
        embed.set_footer(text=",tl pk top daily — BXH hôm nay  •  Tu Tiên Bot v4")
        await ctx.send(embed=embed)

    async def _top_daily(self, ctx):
        today = self._today()
        daily = [
            (uid, data) for uid, data in self._daily_wins.items()
            if data["date"] == today and data["wins"] > 0
        ]
        daily.sort(key=lambda x: x[1]["wins"], reverse=True)
        daily = daily[:10]

        embed = discord.Embed(title="📅 BXH CHIẾN THẦN HÔM NAY", color=0xFF9800)
        medals = ["🥇","🥈","🥉"] + ["🏅"]*7
        if not daily:
            embed.description = "_Chưa có trận đấu nào hôm nay._"
        for i, (uid, data) in enumerate(daily):
            p = await self.bot.db.get_player(uid)
            name = (p["name"] if p else data.get("name","?"))
            embed.add_field(
                name=f"{medals[i]} {name}",
                value=f"⚔️ `{data['wins']}` trận thắng hôm nay",
                inline=False
            )
        embed.set_footer(text=f"Ngày: {today}  •  ,tl pk top — BXH tổng  •  Tu Tiên Bot v4")
        await ctx.send(embed=embed)

    # ── Thách đấu ────────────────────────────────────────────────
    async def _do_challenge(self, ctx, target, bet, player):
        if target.id == ctx.author.id:
            await ctx.send(embed=warn("Không thể tự đấu!")); return
        if target.bot:
            await ctx.send(embed=warn("Không thể đấu với bot!")); return

        defender = await self.bot.db.get_player(target.id)
        if not defender:
            await ctx.send(embed=error(f"**{target.display_name}** chưa nhập môn!")); return
        if defender["status"] != "idle":
            await ctx.send(embed=warn(f"**{defender['name']}** đang bận!")); return

        bet = max(0, min(bet, int(_safe(player,"linh_thach_ha",0)),
                         int(_safe(defender,"linh_thach_ha",0))))

        if bet > 0:
            if _safe(player,"linh_thach_ha",0) < bet:
                await ctx.send(embed=error(f"Không đủ LT để cược **{bet:,} Hạ**!")); return
            if _safe(defender,"linh_thach_ha",0) < bet:
                await ctx.send(embed=warn(
                    f"**{defender['name']}** không đủ LT để cược **{bet:,} Hạ**!"
                )); return

        await self._do_battle(ctx, player, defender, target, bet)

    @commands.command(name="chap_nhan", aliases=["chapnhan","accept_pk","ok_pk"])
    async def chap_nhan(self, ctx, challenger: discord.Member = None):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        if not challenger:
            await ctx.send(embed=warn("Dùng: `,tl chap_nhan @người`")); return

        pending = self._pending.get(challenger.id)
        if not pending or pending["target"] != ctx.author.id:
            await ctx.send(embed=warn("Không có lời thách đấu từ người này!")); return
        if now() > pending["expire"]:
            del self._pending[challenger.id]
            await ctx.send(embed=warn("Lời thách đấu đã hết hạn!")); return

        bet = pending["bet"]
        if _safe(player,"linh_thach_ha",0) < bet:
            await ctx.send(embed=error(f"Không đủ LT! Cần **{bet:,} Hạ**")); return

        del self._pending[challenger.id]
        c_player = await self.bot.db.get_player(challenger.id)
        if not c_player:
            await ctx.send(embed=error("Người thách đấu không tồn tại!")); return

        await self._do_battle(ctx, c_player, player, ctx.author, bet)

    async def _do_battle(self, ctx, A, B, target_member, bet):
        # Lấy trang bị và buff trước khi chiến đấu
        eq_a = await self.bot.db.get_equipment(A["user_id"])
        eq_b = await self.bot.db.get_equipment(B["user_id"])

        async def _load_bf(uid):
            bf = {"atk_pct":0,"def_pct":0,"hp_pct":0,"spd_pct":0,"crit":0}
            try:
                import time as _t
                rows = await self.bot.db.fetchall(
                    "SELECT buff_type, value FROM buffs WHERE user_id=? AND expires_at > ?",
                    (str(uid), int(_t.time()))
                )
                for r in rows:
                    bt, bv = r["buff_type"], float(r["value"])
                    if bt == "atk":          bf["atk_pct"] += bv
                    elif bt == "def":        bf["def_pct"] += bv
                    elif bt in ("hp","hp_max"): bf["hp_pct"] += bv
                    elif bt == "spd":        bf["spd_pct"] += bv
                    elif bt == "crit_pct":   bf["crit"]    += bv
            except Exception:
                pass
            return bf

        bf_a = await _load_bf(A["user_id"])
        bf_b = await _load_bf(B["user_id"])
        winner, loser, log, a_pct, b_pct = _simulate_battle(A, B, eq_a, eq_b, bf_a, bf_b)
        is_a_win = (winner["user_id"] == A["user_id"])

        # Không cược -> không có LT nào đổi chủ. Có cược -> người thắng lấy
        # đúng số LT đã cược của người thua (không tự động "ăn" thêm % LT
        # ngoài thỏa thuận cược).
        reward = bet if bet > 0 else 0

        if is_a_win:
            upd_a = {"total_pk_win": int(_safe(A,"total_pk_win",0))+1}
            if reward > 0:
                upd_a["linh_thach_ha"] = int(_safe(A,"linh_thach_ha"))+reward
            await self.bot.db.update_player(A["user_id"], **upd_a)
            if reward > 0:
                await self.bot.db.update_player(B["user_id"],
                    linh_thach_ha=max(0,int(_safe(B,"linh_thach_ha"))-reward))
            self._add_daily_win(A["user_id"])
            self._set_daily_name(A["user_id"], A["name"])
        else:
            upd_b = {"total_pk_win": int(_safe(B,"total_pk_win",0))+1}
            if reward > 0:
                upd_b["linh_thach_ha"] = int(_safe(B,"linh_thach_ha"))+reward
            await self.bot.db.update_player(B["user_id"], **upd_b)
            if reward > 0:
                await self.bot.db.update_player(A["user_id"],
                    linh_thach_ha=max(0,int(_safe(A,"linh_thach_ha"))-reward))
            self._add_daily_win(B["user_id"])
            self._set_daily_name(B["user_id"], B["name"])

        lc_a = _s(_calc_luc_chien(A))
        lc_b = _s(_calc_luc_chien(B))
        ri_w = int(_safe(winner,"realm_index",0))

        # eq_a/eq_b đã được lấy trước khi battle để tính crit/hút máu/phá giáp

        def _weapon_name(eq):
            w = eq.get("weapon")
            if not w: return "_Tay không_"
            itm = ITEMS.get(w["item_id"], {})
            return f"{itm.get('name', w['item_id'])} `+{w['enhance']}`"

        def _armor_name(eq):
            a = eq.get("armor")
            if not a: return "_Không_"
            itm = ITEMS.get(a["item_id"], {})
            return f"{itm.get('name', a['item_id'])} `+{a['enhance']}`"

        def _stat_block(p, lc, hp_pct, eq):
            mult = THIENDAO_MULT if p.get("dao","") == "thiendao" else 1
            atk  = int(float(_safe(p,"atk",100)) * mult)
            def_ = int(float(_safe(p,"def_",50)) * mult)
            hp   = int(float(_safe(p,"hp_max",1000)) * mult)
            spd  = int(float(_safe(p,"spd",50)) * mult)
            crit = float(_safe(p,"crit",5.0))
            return (
                f"🌌 {get_realm_name(p)}\n"
                f"⚡ **Lực Chiến:** `{lc}`\n"
                f"⚔️ ATK: `{_s(atk)}`  🛡️ DEF: `{_s(def_)}`\n"
                f"❤️ HP: `{_s(hp)}`  🏃 SPD: `{_s(spd)}`\n"
                f"💥 Crit: `{crit:.1f}%`\n"
                f"🗡️ Vũ Khí: {_weapon_name(eq)}\n"
                f"🛡️ Giáp: {_armor_name(eq)}\n"
                f"❤️ HP Cuối: {bar_color(hp_pct)} `{hp_pct*100:.0f}%`"
            )

        # ── Kết quả ──────────────────────────────────────────────
        if reward > 0:
            result_txt = (
                f"🏆 **{winner['name']}** giành chiến thắng!\n"
                f"💔 **{loser['name']}** thất bại, lui về tu luyện.\n"
                f"💰 Thắng cược: **+{reward:,} Hạ LT** từ {loser['name']}"
            )
        else:
            result_txt = (
                f"🏆 **{winner['name']}** giành chiến thắng!\n"
                f"💔 **{loser['name']}** thất bại, lui về tu luyện.\n"
                f"🎖️ _Trận giao hữu (không cược) — không LT nào đổi chủ._"
            )

        # ── Embed 1: Thông tin chiến lực + Kết quả ───────────────
        winner_member = ctx.guild.get_member(int(winner["user_id"])) if ctx.guild else None
        embed = discord.Embed(
            title=f"{realm_icon(ri_w)} ⚔️  ĐẤU TRƯỜNG PK  ⚔️ {realm_icon(ri_w)}",
            description=f"## 🔵 {A['name']}  𝒱𝒮  🔴 {B['name']}",
            color=realm_color(ri_w)
        )
        embed.add_field(name=f"🔵 {A['name']}", value=_stat_block(A, lc_a, a_pct, eq_a), inline=True)
        embed.add_field(name=f"🔴 {B['name']}", value=_stat_block(B, lc_b, b_pct, eq_b), inline=True)
        embed.add_field(name="🎯 Kết Quả", value=result_txt, inline=False)
        if winner_member:
            embed.set_thumbnail(url=winner_member.display_avatar.url)
        embed.set_footer(text="Tu Tiên Bot v4  •  ,tl pk top — BXH cao thủ")
        await ctx.send(embed=embed)

        # ── Embed 2+: Diễn biến trận đấu (mỗi embed ≤ 5500 ký tự) ──
        log_lines = log if log else ["_Bất phân thắng bại ngay hiệp đầu!_"]
        # Gom thành các page, mỗi page nhiều field ≤ 1000 ký tự, tổng embed ≤ 5000
        FIELD_LIMIT = 1000
        EMBED_LIMIT = 5000
        pages = []   # list of list-of-(name, value)
        cur_fields = []
        cur_embed_len = 0
        cur_chunk_lines = []
        cur_chunk_len = 0
        field_idx = 0

        def flush_chunk():
            nonlocal cur_chunk_lines, cur_chunk_len, cur_fields, cur_embed_len, field_idx
            if not cur_chunk_lines:
                return
            val = "\n".join(cur_chunk_lines)
            name = "📜 Diễn Biến Trận Đấu" if field_idx == 0 else "📜 (tiếp)"
            cur_fields.append((name, val))
            cur_embed_len += len(name) + len(val)
            field_idx += 1
            cur_chunk_lines = []
            cur_chunk_len = 0

        def flush_page():
            nonlocal cur_fields, cur_embed_len, pages
            if cur_fields:
                pages.append(cur_fields)
            cur_fields = []
            cur_embed_len = 0

        for line in log_lines:
            line_len = len(line) + 1
            # Nếu thêm dòng này vượt field limit → flush chunk
            if cur_chunk_len + line_len > FIELD_LIMIT:
                flush_chunk()
                # Nếu thêm field mới vượt embed limit → flush page
                next_name = "📜 Diễn Biến Trận Đấu" if field_idx == 0 else "📜 (tiếp)"
                if cur_embed_len + FIELD_LIMIT + len(next_name) > EMBED_LIMIT:
                    flush_page()
            cur_chunk_lines.append(line)
            cur_chunk_len += line_len

        flush_chunk()
        flush_page()

        for pi, fields in enumerate(pages):
            log_embed = discord.Embed(
                title=f"📜 Diễn Biến Trận Đấu {'(trang ' + str(pi+1) + ')' if len(pages)>1 else ''}",
                color=0x5865F2
            )
            for fname, fval in fields:
                log_embed.add_field(name=fname, value=fval, inline=False)
            log_embed.set_footer(text=f"{A['name']} ⚔️ {B['name']}")
            await ctx.send(embed=log_embed)

        # GIF cảm xúc từ nekos.best (no auth, free)
        try:
            # Thắng → vui / Thua → buồn, dựa theo người gọi lệnh (A)
            caller_won = is_a_win
            category = random.choice(["happy", "smile", "dance"]) if caller_won else random.choice(["cry", "sad", "pout"])
            async with aiohttp.ClientSession() as s:
                async with s.get(
                    f"https://nekos.best/api/v2/{category}",
                    timeout=aiohttp.ClientTimeout(total=4)
                ) as r:
                    if r.status == 200:
                        data = await r.json()
                        gif_url = data["results"][0]["url"]
                        mood = "🎉 Chiến thắng vinh quang!" if caller_won else "💔 Thất bại... hãy mạnh hơn!"
                        gif_embed = discord.Embed(description=f"**{mood}**", color=0xFFD700 if caller_won else 0xF44336)
                        gif_embed.set_image(url=gif_url)
                        await ctx.send(embed=gif_embed)
        except Exception:
            pass  # Không có GIF cũng không sao

    @commands.command(name="dau_truong", aliases=["dautruong","arena","dt2"])
    async def dau_truong(self, ctx):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        """Tham gia đấu trường ngẫu nhiên"""
        ri = player["realm_index"]
        others = await self.bot.db.fetchall(
            "SELECT * FROM players WHERE realm_index BETWEEN ? AND ? "
            "AND user_id != ? AND status='idle' ORDER BY RANDOM() LIMIT 1",
            (max(0,ri-1), ri+1, str(ctx.author.id))
        )

        if others:
            opp = others[0]; is_npc = False
            npc_avatar = None
        else:
            # Gọi Random User API để lấy tên + avatar NPC ngẫu nhiên
            npc_avatar = None
            opp_name = None
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        "https://randomuser.me/api/?nat=us,gb,au,ca&inc=name,picture",
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as resp:
                        rdata = await resp.json()
                        user = rdata["results"][0]
                        fn = user["name"]["first"]
                        ln = user["name"]["last"]
                        opp_name  = f"{fn} {ln}"
                        npc_avatar = user["picture"]["medium"]
            except Exception:
                pass

            # Fallback nếu API lỗi
            if not opp_name:
                NPC_NAMES = ["Phong Vũ","Huyết Long","Thiên Sát","Vô Danh","Tử Ảnh","Hàn Băng","Lôi Thần","Diêm La"]
                opp_name = random.choice(NPC_NAMES)

            lc_mul = random.uniform(0.75, 1.35)
            opp = {
                "user_id": "npc_0", "name": opp_name,
                "realm_index": ri, "realm_tier": player["realm_tier"],
                "atk": _safe(player,"atk",100)*lc_mul,
                "def_": _safe(player,"def_",50)*lc_mul,
                "hp_max": _safe(player,"hp_max",1000)*lc_mul,
                "spd": _safe(player,"spd",50),
                "crit": _safe(player,"crit",5),
                "linh_thach_ha": 0,
            }
            is_npc = True

        winner, loser, log, p_pct, o_pct = _simulate_battle(player, opp)
        won = (winner["user_id"] == str(ctx.author.id))

        reward_ha  = random.randint(1000*(ri+1), 3000*(ri+1))
        reward_exp = random.randint(500*(ri+1),  1500*(ri+1))

        embed = discord.Embed(
            title=f"🏟️ ĐẤU TRƯỜNG: {player['name']} vs {opp['name']}",
            color=0xFFD700 if won else 0xF44336
        )
        # Hiện avatar NPC nếu lấy được từ API
        if is_npc and npc_avatar:
            embed.set_thumbnail(url=npc_avatar)
        embed.add_field(
            name="❤️ HP Cuối Trận",
            value=f"{player['name']}: {bar_color(p_pct)} `{p_pct*100:.0f}%`   •   {opp['name']}: {bar_color(o_pct)} `{o_pct*100:.0f}%`",
            inline=False
        )
        embed.add_field(name="📜 Diễn Biến", value="\n".join(log[-5:]), inline=False)
        if won:
            from utils.game_data import get_exp_req
            new_exp = min(_safe(player,"exp")+reward_exp, get_exp_req(player))
            await self.bot.db.update_player(ctx.author.id,
                linh_thach_ha=_safe(player,"linh_thach_ha")+reward_ha,
                exp=new_exp,
                total_pk_win=_safe(player,"total_pk_win",0)+1)
            self._add_daily_win(str(ctx.author.id))
            self._set_daily_name(str(ctx.author.id), player["name"])
            embed.add_field(name="🏆 CHIẾN THẮNG!",
                value=f"💰 +{reward_ha:,} Hạ\n✨ +{fmt(reward_exp)} EXP", inline=False)
        else:
            embed.add_field(name="💔 THẤT BẠI!", value="Cần tăng sức mạnh hơn!", inline=False)

        badge = "_(NPC)_" if is_npc else "_(Người chơi thật)_"
        embed.set_footer(text=f"Đối thủ: {opp['name']} {badge}  •  Tu Tiên Bot v4")
        await ctx.send(embed=embed)

    @commands.command(name="bxh", aliases=["bxh_all","top_all","xephang"])
    async def bxh(self, ctx, cat: str = "realm", pham_vi: str = None):
        CAT = {
            "realm": ("realm_index",       "🌌 BXH CẢNH GIỚI"),
            "giau":  ("linh_thach_cuc",    "💰 BXH TÀI PHÚ"),
            "exp":   ("exp",               "✨ BXH TU VI"),
            "pk":    ("total_pk_win",      "⚔️ BXH PK THẮNG"),
            "boss":  ("total_boss_attack", "👹 BXH BOSS"),
            "luc":   ("luc_chien",         "💪 BXH LỰC CHIẾN"),
            "cs":    ("prestige",          "🔄 BXH CHUYỂN SINH"),
        }
        order, title = CAT.get(cat.lower(), CAT["realm"])

        # Alias "bxh_all"/"top_all" hoặc tham số "all" -> xem toàn server (global)
        is_global = (ctx.invoked_with in ("bxh_all", "top_all")) or (pham_vi and pham_vi.lower() in ("all", "global", "toancau"))
        guild_id = None if is_global else (ctx.guild.id if ctx.guild else None)

        rows = await self.bot.db.get_leaderboard(order=order, limit=10, guild_id=guild_id)
        embed = discord.Embed(title=title + (" (Toàn Server Bot)" if is_global else ""), color=0xFFD700)
        medals = ["🥇","🥈","🥉"]+["🏅"]*7
        for i, p in enumerate(rows):
            lc  = _s(_calc_luc_chien(p))
            rn  = get_realm_name(p)
            val = f"🌌 {rn} | ⚔️ `{lc}` | 💰 {_safe(p,'linh_thach_cuc',0):,} Cực"
            if cat=="pk":    val = f"⚔️ {_safe(p,'total_pk_win',0):,} lần thắng"
            elif cat=="boss": val = f"👹 {_safe(p,'total_boss_attack',0):,} lần đánh"
            elif cat=="luc":  val = f"⚔️ `{lc}`"
            elif cat=="cs":   val = f"🔄 `{_safe(p,'prestige',0)}` lần | 🌌 {rn}"
            embed.add_field(name=f"{medals[i]} {p['name']}", value=val, inline=False)
        if not rows:
            embed.description = "_Chưa có người chơi trong server này._" if not is_global else "_Chưa có người chơi._"
        embed.set_footer(text=",tl bxh realm/giau/exp/pk/boss/luc/cs [all]  •  Tu Tiên Bot v4")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(PvP(bot))

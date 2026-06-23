"""cogs/cultivation.py v4 - Tu luyện đầy đủ"""
import discord
from discord.ext import commands
import time, random, json

from utils.helpers import require_player, require_idle, now, sync_realm_role
from utils.embeds import *
from utils.game_data import *
from utils.persistent_cache import PersistentCache

def _s(n):
    return fmt(n)

def _safe(p, k, d=0):
    v = p.get(k); return v if v is not None else d

def _calc_lc(atk, def_, hp, spd, crit):
    import math
    result = atk*2.0 + def_*1.2 + hp*0.005 + spd*0.8 + crit*50
    if math.isinf(result) or math.isnan(result):
        return 1e18
    return round(result, 2)

def _gacha_all():
    return gacha(LINH_CAN), gacha(THE_CHAT), gacha(HUYET_MACH)

class Cultivation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._buffs = PersistentCache(bot, "cultivation_buffs")  # uid -> {buff: expire_ts}

    async def cog_load(self):
        await self._buffs.load()

    async def cog_unload(self):
        await self._buffs.save()

    def get_exp_rate(self, player: dict) -> float:
        """EXP/giây dựa theo cảnh giới.
        Mục tiêu: người thường (Ngũ Hành, Bình Thường) mất ~10 phút/tier.
        exp_rate_base = exp_req / 600  (600 giây = 10 phút)
        Bonus nhân vật có thể giảm xuống ~2-5 phút/tier.
        Dưới 3 phút (180s) = không tính exp (check ở tl stop).
        """
        from utils.game_data import get_exp_req as _get_exp_req
        exp_req = _get_exp_req(player)
        if exp_req <= 0:
            return 1.0

        # Base: exp_req / 600 → đủ 1 tier sau đúng 10 phút bế quan
        base = exp_req / 600.0

        ngo  = float(_safe(player, "ngo_tinh", 50))
        dao  = DAO.get(player.get("dao",""), {})

        # Ngộ tính bonus: x1.0 → x1.5 (ngo 0→200)
        ngo_mult = 1.0 + min(ngo, 200) / 400

        # Linh căn bonus
        LC_BONUS = {
            "Ngũ Hành Tạp Linh Căn": 1.0, "Tứ Hệ Linh Căn": 1.2,
            "Tam Hệ Linh Căn": 1.4,        "Song Hệ Linh Căn": 1.6,
            "Đơn Hệ Linh Căn": 1.9,        "Biến Linh Căn": 2.2,
            "Thiên Linh Căn": 2.6,          "Thiên Đạo Linh Căn": 3.5,
        }
        lc_mult = LC_BONUS.get(_safe(player, "linh_can", ""), 1.0)

        # Thể chất bonus
        TC_BONUS = {
            "Bình Thường": 1.0,           "Thiên Sinh Thần Lực Thể": 1.3,
            "Băng Hỏa Song Linh Thể": 1.5,"Thiên Ma Thể": 1.8,
            "Thái Sơ Thiên Đạo Thể": 3.0,
        }
        tc_mult = TC_BONUS.get(_safe(player, "the_chat", ""), 1.0)

        # Đạo tâm bonus
        dao_mult = dao.get("exp_rate", 1.0)
        if player.get("dao","") == "thiendao":
            dao_mult = 2.0

        total = base * ngo_mult * lc_mult * tc_mult * dao_mult * prestige_exp_mult(_safe(player,"prestige",0))

        # Buff thời gian
        uid = str(player.get("user_id",""))
        buffs = self._buffs.get(uid, {})
        if now() < buffs.get("thien_dinh",  0): total *= 1.5
        if now() < buffs.get("tich_tu_dan", 0): total *= 1.5

        return round(total, 4)

    def set_buff(self, uid: str, buff_name: str, duration: int):
        existing = self._buffs.get(uid, {})
        existing[buff_name] = now() + duration
        self._buffs[uid] = existing

    async def _nhap(self, ctx, dao_key: str):
        if await self.bot.db.get_player(ctx.author.id):
            await ctx.send(embed=warn("Da nhap mon roi! Dung ,tl de xem ho so.")); return
        dao = DAO[dao_key]
        lc, tc, hm = _gacha_all()
        ngo = random.randint(35, 95); phuoc = random.randint(35, 95)
        b_atk  = 100  * dao.get("atk",1.0) * lc.get("atk",1.0) * tc.get("atk",1.0) * hm.get("atk",1.0)
        b_def  = 50   * dao.get("def",1.0) * tc.get("def",1.0) * hm.get("def",1.0)
        b_hp   = 1000 * dao.get("hp",1.0)  * tc.get("hp",1.0)  * hm.get("hp",1.0)
        b_spd  = 50   * dao.get("spd",1.0)
        b_crit = 5.0  + dao.get("crit",0.0) + tc.get("crit",0.0)
        b_luck = dao.get("luck",0) + lc.get("luck",0) + hm.get("luck",0)
        lc_val = _calc_lc(b_atk, b_def, b_hp, b_spd, b_crit)
        await self.bot.db.create_player(ctx.author.id, ctx.author.display_name, guild_id=ctx.guild.id if ctx.guild else None)
        await self.bot.db.update_player(ctx.author.id,
            dao=dao_key, atk=b_atk, def_=b_def, hp=b_hp, hp_max=b_hp,
            spd=b_spd, crit=b_crit, luck=b_luck,
            linh_can=lc["name"], the_chat=tc["name"], huyet_mach=hm["name"],
            ngo_tinh=ngo, phuc_duyen=phuoc, linh_thach_ha=1000, luc_chien=lc_val)
        for iid, qty in [("105",1),("202",5),("201",3)]:
            await self.bot.db.add_item(ctx.author.id, iid, qty)
        R = RARITY_EMOJI
        embed = discord.Embed(
            title=f"{dao['icon']} NHAP MON THANH CONG!",
            description=f"Chao mung **{ctx.author.display_name}** buoc vao **{dao['name']}**!\n_{dao['desc']}_",
            color=0x6A0DAD)
        embed.add_field(name="Dac Tinh Khai Sinh", value=(
            f"{R.get(lc['rarity'],'?')} Linh Can: {lc['name']}\n"
            f"{R.get(tc['rarity'],'?')} The Chat: {tc['name']}\n"
            f"{R.get(hm['rarity'],'?')} Huyet Mach: {hm['name']}\n"
            f"Ngo Tinh: **{ngo}**  Phuc Duyen: **{phuoc}**"), inline=False)
        embed.add_field(name="Chi So Khoi Dau", value=(
            f"ATK: `{_s(b_atk)}`  DEF: `{_s(b_def)}`\n"
            f"HP: `{_s(b_hp)}`  SPD: `{_s(b_spd)}`\n"
            f"CRIT: `{b_crit:.1f}%`  Luc Chien: `{_s(lc_val)}`"), inline=False)
        embed.add_field(name="Qua Tan Thu", value="1000 Ha LT + Ruong Tan Thu + 5x Dan + 3x Phuc Tinh Dan", inline=False)
        embed.set_footer(text="Go ,tl start de bat dau be quan tu luyen!")
        await ctx.send(embed=embed)

    @commands.command(name="nhapma")
    async def nhapma(self, ctx): await self._nhap(ctx,"nhapma")
    @commands.command(name="nhapdao")
    async def nhapdao(self,ctx): await self._nhap(ctx,"nhapdao")
    @commands.command(name="nhapnho")
    async def nhapnho(self,ctx): await self._nhap(ctx,"nhapnho")
    @commands.command(name="nhapquy")
    async def nhapquy(self,ctx): await self._nhap(ctx,"nhapquy")
    @commands.command(name="nhapyeu")
    async def nhapyeu(self,ctx): await self._nhap(ctx,"nhapyeu")
    @commands.command(name="nhaplo")
    async def nhaplo(self, ctx): await self._nhap(ctx,"nhaplo")

    @commands.command(name="start", aliases=["bequan","tu"])
    async def start(self, ctx):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao` để bắt đầu.")); return
        if player.get("status","idle") != "idle":
            STATUS = {"beQuan":"🧘 Đang Bế Quan","thamHiem":"⚔️ Đang Thám Hiểm",
                      "pk":"🥊 Đang PK","luyen_dan":"⚗️ Đang Luyện Đan"}
            msg = STATUS.get(player["status"], f"Trạng thái: {player['status']}")
            await ctx.send(embed=warn(f"{msg}\nDùng lệnh kết thúc trước!")); return
        await self.bot.db.update_player(ctx.author.id, status="beQuan", status_start=now())
        dao   = DAO.get(player.get("dao",""), {"name":"?","icon":"?"})
        exp_s = self.get_exp_rate(player)
        uid   = str(player.get("user_id", str(ctx.author.id)))
        buffs = self._buffs.get(uid, {})
        active = []
        if now() < buffs.get("thien_dinh", 0):
            active.append(f"Thiên Đỉnh: +50% EXP ({fmt_time(buffs['thien_dinh']-now())})")
        if now() < buffs.get("tich_tu_dan", 0):
            active.append(f"Tích Tu Đan: +50% EXP ({fmt_time(buffs['tich_tu_dan']-now())})")
        ri = int(player.get("realm_index", 0))
        embed = discord.Embed(
            title="🧘 BẾ QUAN TU LUYỆN",
            description="Đang tu luyện... Gõ `,tl stop` để kết thúc nhận Tu Vi.\n_Tối thiểu **3 phút**._",
            color=realm_color(ri)
        )
        embed.set_author(name=player["name"], icon_url=ctx.author.display_avatar.url)
        embed.add_field(name="🌊 Đạo",     value=f"`{dao['name']}`",                 inline=True)
        embed.add_field(name="✨ EXP/giây", value=f"`{exp_s}`",                       inline=True)
        embed.add_field(name="🧠 Ngộ Tính", value=f"`{_safe(player,'ngo_tinh',50)}`", inline=True)
        if active:
            embed.add_field(name="🔥 Buff", value="\n".join(active), inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="stop", aliases=["ketthuc","dungtu"])
    async def stop(self, ctx):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn!")); return
        try:
            if player.get("status") != "beQuan":
                await ctx.send(embed=warn("Không đang bế quan! Dùng `,tl start` để tu luyện.")); return
            elapsed = now() - int(_safe(player,"status_start",now()))
            if elapsed < 180:
                await ctx.send(embed=warn(f"Tối thiểu 3 phút! Còn `{fmt_time(180-elapsed)}`.")); return
            exp_s   = self.get_exp_rate(player)
            exp_got = int(elapsed * exp_s)
            # Bonus EXP từ sự kiện theo mùa
            try:
                from cogs.events import _event_exp_bonus
                ev_bonus = _event_exp_bonus()
            except Exception:
                ev_bonus = 1.0
            if ev_bonus > 1.0:
                exp_got = int(exp_got * ev_bonus)
            # Bonus EXP từ Sư Đạo (+10% nếu có sư phụ)
            su_dao_bonus = 1.0
            try:
                su_row = await self.bot.db.fetchone(
                    "SELECT * FROM su_dao WHERE do_de_id=?", (str(ctx.author.id),)
                )
                if su_row:
                    su_dao_bonus = 1.0 + 0.10
                    exp_got = int(exp_got * su_dao_bonus)
            except Exception:
                pass
            exp_req = get_exp_req(player)
            # Tích lũy exp thực, không bị cap - dp mới reset
            new_exp = int(_safe(player,"exp",0)) + exp_got
            new_ct  = int(_safe(player,"total_cultivate_time",0)) + elapsed
            await self.bot.db.update_player(ctx.author.id,
                status="idle", status_start=0, exp=new_exp, total_cultivate_time=new_ct)
            await self._add_quest(ctx.author.id, "cultivation_time", elapsed)
            ri = int(player.get("realm_index", 0))
            embed = discord.Embed(title="⏹️ KẾT THÚC BẾ QUAN", color=realm_color(ri))
            embed.set_author(name=player["name"], icon_url=ctx.author.display_avatar.url)
            _exp_bonuses = []
            if ev_bonus > 1.0:     _exp_bonuses.append(f"×{ev_bonus:.1f}🎉")
            if su_dao_bonus > 1.0: _exp_bonuses.append("+10%🏯")
            _exp_str = f"`+{_s(exp_got)}`" + (f" _({' '.join(_exp_bonuses)})_" if _exp_bonuses else "")
            embed.add_field(name="⏱️ Thời Gian", value=f"`{fmt_time(elapsed)}`",  inline=True)
            embed.add_field(name="✨ Tu Vi",      value=_exp_str,                  inline=True)
            embed.add_field(name="📈 EXP/s",      value=f"`{exp_s}`",              inline=True)
            _disp = min(new_exp, exp_req)
            _pct  = f"{min(new_exp/exp_req*100,100):.1f}%" if exp_req > 0 else "100%"
            _over = f" _(+{_s(new_exp-exp_req)} dư - đủ đột phá!)_" if new_exp > exp_req else ""
            embed.add_field(name="📊 Tiến Độ",
                value=f"{bar(_disp,exp_req,18)} {_pct}\n`{_s(_disp)}/{_s(exp_req)}`{_over}", inline=False)
            if new_exp >= exp_req:
                if _safe(player, "auto_dotpha", 0):
                    fresh = await self.bot.db.get_player(ctx.author.id)
                    dp_embed = await self._do_dotpha(ctx.author.id, fresh, member=ctx.author)
                    embed.add_field(name="⚡ Tự Động Đột Phá", value="Tu Vi đầy, đang tự động đột phá...", inline=False)
                    embed.set_footer(text=f"Tổng: {fmt_time(int(new_ct))}  •  Tu Tiên Bot v4")
                    await ctx.send(embed=embed)
                    await ctx.send(embed=dp_embed)
                    return
                embed.add_field(name="", value="⚡ **Tu Vi đầy! Gõ `,tl dp` để đột phá!**", inline=False)
            embed.set_footer(text=f"Tổng: {fmt_time(int(new_ct))}  •  Tu Tiên Bot v4")
            await ctx.send(embed=embed)
        except Exception as e:
            import traceback; traceback.print_exc()
            await ctx.send(embed=error(f"Lỗi lệnh stop: `{e}`"))

    @commands.command(name="dotpha", aliases=["dp","breakthrough"])
    async def dotpha(self, ctx, arg: str = None):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn!")); return
        if arg and arg.lower() == "auto":
            await self._toggle_auto_dotpha(ctx, player)
            return
        if player.get("status","idle") != "idle":
            await ctx.send(embed=warn("Đang bận! Kết thúc hoạt động hiện tại trước.")); return
        exp_req = get_exp_req(player)
        cur_exp = int(_safe(player,"exp",0))
        if cur_exp < exp_req:
            await ctx.send(embed=warn(
                f"⚠️ Tu Vi chưa đủ!\n"
                f"Còn thiếu: `{_s(exp_req - cur_exp)}`\n"
                f"Tiến độ: `{_s(cur_exp)}/{_s(exp_req)}`"
            )); return
        embed = await self._do_dotpha(ctx.author.id, player, member=ctx.author)
        await ctx.send(embed=embed)

    async def _toggle_auto_dotpha(self, ctx, player):
        cur = _safe(player, "auto_dotpha", 0)
        new_state = 0 if cur else 1
        await self.bot.db.update_player(ctx.author.id, auto_dotpha=new_state)
        if new_state:
            embed = discord.Embed(
                title="⚡ [TỰ ĐỘNG ĐỘT PHÁ] ⚡",
                description=(
                    "🟢 Trạng thái: **ĐÃ BẬT**\n\n"
                    "💡 Khi Tu Vi đầy, đạo hữu chỉ cần gõ `,tl dp` để tự động đột phá.\n"
                    "Hệ thống sẽ tự dùng **Đột Phá Đan** (tăng tỷ lệ thành công) nếu có trong túi đồ, "
                    "không có thì đột phá chay."
                ),
                color=0x4CAF50
            )
        else:
            embed = discord.Embed(
                title="⚡ [TỰ ĐỘNG ĐỘT PHÁ] ⚡",
                description=(
                    "🔴 Trạng thái: **ĐÃ TẮT**\n\n"
                    "💡 Đạo hữu sẽ phải tự thực hiện đột phá thủ công bằng lệnh `,dp` hoặc `,tl dotpha`."
                ),
                color=0xF44336
            )
        await ctx.send(embed=embed)

    async def _do_dotpha(self, user_id, player, member: discord.Member = None) -> discord.Embed:
        """Thực hiện đột phá, trả về embed kết quả. Tự dùng Đột Phá Đan nếu có."""
        realm  = REALMS[player["realm_index"]]
        fail   = realm.get("fail", 0.0)
        is_maj = player["realm_tier"] >= realm["tiers"]
        dan    = await self.bot.db.get_item_count(user_id, "203")
        phuoc  = _safe(player,"phuc_duyen",50)
        used_dan = False
        if dan > 0 and fail > 0:
            fail = max(0.0, fail - ITEMS.get("203",{}).get("breakthrough",0.10))
            await self.bot.db.remove_item(user_id, "203", 1)
            used_dan = True
        fail = max(0.0, fail - phuoc*0.001)
        if random.random() < fail:
            lost = int(_safe(player,"exp")*0.30)
            await self.bot.db.update_player(user_id, exp=_safe(player,"exp")-lost)
            desc = f"Mat **{_s(lost)}** Tu Vi!\nFail: `{fail*100:.1f}%`"
            if used_dan: desc += "\n_(Đã dùng 1x Đột Phá Đan)_"
            return discord.Embed(title="DOT PHA THAT BAI!", color=0xF44336, description=desc)
        ni = player["realm_index"]; nt = player["realm_tier"] + 1
        if nt > REALMS[ni]["tiers"]: ni += 1; nt = 1
        if ni >= len(REALMS):
            return success("🏆 ĐỈNH CỰC!",
                f"Đã đạt **{REALMS[-1]['name']}** — cảnh giới tối cao!\n\n"
                f"💫 Dùng `,tl chuyensinh` để **Chuyển Sinh**: quay về Luyện Thể "
                f"nhưng nhận buff tu luyện **vĩnh viễn**, tích lũy qua từng kiếp!")
        # Tính equipment bonus để trừ ra, chỉ tăng base stats
        _eq = await self.bot.db.get_equipment(user_id)
        _eq_atk = _eq_def = _eq_hp = _eq_spd = 0.0
        for _sl, _ed in _eq.items():
            _itm = ITEMS.get(_ed["item_id"], {})
            _m = 1 + _ed["enhance"] * 0.05
            _eq_atk += float(_itm.get("base_atk", _itm.get("atk", 0))) * _m
            _eq_def += float(_itm.get("base_def", _itm.get("def_", 0))) * _m
            _eq_hp  += float(_itm.get("base_hp",  _itm.get("hp",  0))) * _m
            _eq_spd += float(_itm.get("base_spd", _itm.get("spd", 0))) * _m
        # Base stats = DB stats - equipment bonus
        oa=max(1.0, float(_safe(player,"atk",100)) - _eq_atk);  na=round(oa*1.22 + _eq_atk, 2)
        od=max(0.0, float(_safe(player,"def_",50)) - _eq_def);  nd=round(od*1.22 + _eq_def, 2)
        oh=max(1.0, float(_safe(player,"hp_max",1000)) - _eq_hp); nh=round(oh*1.28 + _eq_hp, 2)
        os_=max(0.0, float(_safe(player,"spd",50)) - _eq_spd); ns=round(os_*1.05 + _eq_spd, 2)
        nl=_calc_lc(na,nd,nh,ns,_safe(player,"crit",5))
        # Giữ lại exp dư sau dp (không reset về 0)
        cur_exp  = int(_safe(player, "exp", 0))
        old_req  = get_exp_req(player)
        leftover = max(0, cur_exp - old_req)  # Exp dư chuyển sang tier mới
        await self.bot.db.update_player(user_id,
            realm_index=ni, realm_tier=nt, exp=leftover,
            atk=na, def_=nd, hp_max=nh, hp=nh, spd=ns, luc_chien=nl)
        await self._add_quest(user_id, "breakthrough", 1)
        # Hook Sư Đạo: sư phụ nhận EXP khi đồ đệ đột phá
        try:
            from cogs.sudao import on_dotpha_success
            await on_dotpha_success(self.bot, user_id, float(old_req))
        except Exception:
            pass
        # Đổi Discord role theo cảnh giới khi lên ĐẠI cảnh giới mới (ni thay đổi).
        # An toàn tuyệt đối: sync_realm_role tự bỏ qua nếu tắt/thiếu quyền/lỗi.
        if member is not None and ni != player["realm_index"]:
            await sync_realm_role(self.bot, member, ni)
        new_name = get_realm_name({**player,"realm_index":ni,"realm_tier":nt})
        next_req  = get_exp_req({"realm_index":ni,"realm_tier":nt})
        embed = discord.Embed(
            title="⚡ ĐỘT PHÁ THÀNH CÔNG!",
            description=f"**{player['name']}** nghịch thiên cải mệnh!",
            color=realm_color(ni)
        )
        embed.add_field(name="🌌 Cảnh Giới Mới", value=f"```{new_name}```", inline=False)
        embed.add_field(name="📈 Tăng Chỉ Số", value=(
            f"⚔️ ATK: `{_s(oa)}`→`{_s(na)}`\n"
            f"🛡️ DEF: `{_s(od)}`→`{_s(nd)}`\n"
            f"❤️ HP: `{_s(oh)}`→`{_s(nh)}`"
        ), inline=True)
        embed.add_field(name="⚡ Lực Chiến", value=f"`{_s(nl)}`", inline=True)
        leftover_pct = f"{leftover/next_req*100:.1f}%" if next_req > 0 and leftover > 0 else ""
        next_val = f"Cần: `{_s(next_req)}` EXP"
        if leftover > 0:
            next_val += f"\n✅ Mang sang: `{_s(leftover)}` EXP ({leftover_pct})"
        embed.add_field(name="📊 Tu Vi Tiếp Theo", value=next_val, inline=False)
        if used_dan:
            embed.add_field(name="💊 Đột Phá Đan", value="Đã dùng 1x _(Giảm tỉ lệ thất bại)_", inline=False)
        if is_maj:
            embed.add_field(name="🌟 ĐẠI CẢNH GIỚI!", value="Sức mạnh đột biến vượt bậc!", inline=False)
        return embed

    @commands.command(name="chuyensinh", aliases=["prestige", "cs", "luanhoi"])
    @require_player
    async def chuyensinh(self, ctx):
        """🔄 Chuyển Sinh — quay về Luyện Thể khi đã đạt cảnh giới tối cao,
        nhận buff tu luyện vĩnh viễn tích lũy qua từng kiếp."""
        player = await self.bot.db.get_player(ctx.author.id)
        max_ri = len(REALMS) - 1
        if int(player.get("realm_index", 0)) < max_ri:
            await ctx.send(embed=warn(
                f"⚠️ Chỉ có thể Chuyển Sinh khi đã đạt **{REALMS[max_ri]['name']}**!\n"
                f"Cảnh giới hiện tại: `{get_realm_name(player)}`"
            )); return
        if player.get("status", "idle") != "idle":
            await ctx.send(embed=warn("Đang bận! Kết thúc hoạt động hiện tại trước.")); return
        if int(player.get("vt_locked", 0) or 0) == 1:
            await ctx.send(embed=warn(
                "**Vô Thượng Đạo Tổ** đã vượt khỏi vòng luân hồi — không cần Chuyển Sinh nữa!"
            )); return

        old_prestige = int(_safe(player, "prestige", 0))
        new_prestige = old_prestige + 1
        old_mult = prestige_exp_mult(old_prestige)
        new_mult = prestige_exp_mult(new_prestige)

        # Reset stats về gốc (realm_index=0, tier=1) nhưng vẫn áp dụng bonus
        # Đạo/Linh Căn/Thể Chất/Huyết Mạch hiện có của người chơi.
        stats = scale_stats_for_realm_change(player, 0, 1)
        new_s = stats["new"]

        # Mỗi lần chuyển sinh tăng thêm 20% chỉ số (tích lũy cộng dồn)
        cs_bonus = 1.0 + new_prestige * 0.20
        boosted_atk     = round(new_s["atk"]     * cs_bonus, 2)
        boosted_def     = round(new_s["def_"]    * cs_bonus, 2)
        boosted_hp      = round(new_s["hp_max"]  * cs_bonus, 2)
        boosted_spd     = round(new_s["spd"]     * cs_bonus, 2)
        boosted_lc      = _calc_lc(boosted_atk, boosted_def, boosted_hp, boosted_spd, _safe(player,"crit",5))

        await self.bot.db.update_player(
            ctx.author.id,
            realm_index=0, realm_tier=1, exp=0,
            atk=boosted_atk, def_=boosted_def, hp=boosted_hp,
            hp_max=boosted_hp, spd=boosted_spd, luc_chien=boosted_lc,
            prestige=new_prestige
        )
        await self._add_quest(ctx.author.id, "prestige", 1)
        # Reset role cảnh giới về Luyện Thể (an toàn, tự bỏ qua nếu tắt/lỗi quyền)
        await sync_realm_role(self.bot, ctx.author, 0)

        title = get_prestige_title(new_prestige)
        embed = discord.Embed(
            title="🔄 CHUYỂN SINH THÀNH CÔNG!",
            description=(
                f"**{player['name']}** tự tan rã thân thể, đầu thai chuyển kiếp...\n"
                f"Mang theo ký ức và đạo tâm, bắt đầu lại từ **Luyện Thể**!"
            ),
            color=0xFFD700
        )
        embed.add_field(name="🔁 Số Lần Chuyển Sinh", value=f"`{new_prestige}`", inline=True)
        if title:
            embed.add_field(name="🏅 Danh Hiệu Mới", value=f"**{title}**", inline=True)
        embed.add_field(
            name="⚡ Tốc Độ Tu Luyện Vĩnh Viễn",
            value=f"`x{old_mult}` → `x{new_mult}` _(áp dụng mọi kiếp sau)_",
            inline=False
        )
        old_cs_bonus = 1.0 + old_prestige * 0.20
        new_cs_bonus = 1.0 + new_prestige * 0.20
        embed.add_field(
            name="💪 Buff Chỉ Số Vĩnh Viễn",
            value=f"`x{old_cs_bonus:.1f}` → `x{new_cs_bonus:.1f}` _(+20% ATK/DEF/HP/SPD mỗi lần CS)_",
            inline=False
        )
        embed.add_field(
            name="💡 Lưu Ý",
            value="Linh thạch, trang bị, vật phẩm, tông môn, danh hiệu cũ **được giữ nguyên**.\nChỉ tu vi và cảnh giới reset về vạch xuất phát.",
            inline=False
        )
        embed.set_footer(text=",tl chuyensinh_info để xem chi tiết buff  •  Tu Tiên Bot v4")
        await ctx.send(embed=embed)

    @commands.command(name="chuyensinh_info", aliases=["cs_info", "prestige_info"])
    @require_player
    async def chuyensinh_info(self, ctx):
        """📊 Xem thông tin Chuyển Sinh của bản thân"""
        player = await self.bot.db.get_player(ctx.author.id)
        p = int(_safe(player, "prestige", 0))
        max_ri = len(REALMS) - 1
        cur_mult = prestige_exp_mult(p)
        next_mult = prestige_exp_mult(p + 1)
        title = get_prestige_title(p)
        can_prestige = int(player.get("realm_index", 0)) >= max_ri

        embed = discord.Embed(title="🔄 THÔNG TIN CHUYỂN SINH", color=0xFFD700)
        embed.add_field(name="🔁 Đã Chuyển Sinh", value=f"`{p}` lần", inline=True)
        if title:
            embed.add_field(name="🏅 Danh Hiệu", value=f"**{title}**", inline=True)
        embed.add_field(name="⚡ Buff Tu Luyện Hiện Tại", value=f"`x{cur_mult}`", inline=False)
        embed.add_field(name="📈 Buff Nếu Chuyển Sinh Thêm 1 Lần", value=f"`x{next_mult}`", inline=False)
        if can_prestige:
            embed.add_field(name="✅ Trạng Thái", value="Đủ điều kiện! Dùng `,tl chuyensinh` ngay.", inline=False)
        else:
            embed.add_field(
                name="🔒 Trạng Thái",
                value=f"Cần đạt **{REALMS[max_ri]['name']}** trước.\nHiện tại: `{get_realm_name(player)}`",
                inline=False
            )
        await ctx.send(embed=embed)

    @commands.command(name="diemdanh", aliases=["daily","dd"])
    async def diemdanh(self, ctx):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn!")); return
        try:
            sd    = await self.bot.db.get_streak(ctx.author.id)
            today = int(now()//86400)
            last  = int((sd.get("last_daily") or 0)//86400)
            if last == today:
                await ctx.send(embed=warn(
                    f"Đã điểm danh hôm nay!\n"
                    f"Reset sau: **{fmt_time((today+1)*86400-now())}**"
                )); return
            streak = (sd.get("streak",0)+1) if last == today-1 else 1
            total  = 1000 + min(streak*300, 8000)
            gifts  = []
            if streak>=3:  gifts.append(("201",1))
            if streak>=7:  gifts.append(("101",1))
            if streak>=14: gifts.append(("102",1))
            if streak>=21: gifts.append(("203",1))
            if streak>=30: gifts.append(("103",1))
            if streak>=60: gifts.append(("104",1))
            await self.bot.db.update_player(ctx.author.id,
                linh_thach_ha=int(_safe(player,"linh_thach_ha",0))+total)
            await self.bot.db.update_streak(ctx.author.id, streak, now())
            for iid,qty in gifts:
                await self.bot.db.add_item(ctx.author.id, iid, qty)
            embed = discord.Embed(title="📅 ĐIỂM DANH!", color=0xFFD700)
            embed.set_author(name=player["name"], icon_url=ctx.author.display_avatar.url)
            embed.add_field(name="🔥 Streak",  value=f"**{streak} ngày**", inline=True)
            embed.add_field(name="💰 Nhận",    value=f"**+{total:,}** Hạ LT", inline=True)
            if gifts:
                g_str = " | ".join(f"+{q}x {ITEMS.get(i,{}).get('name',i)}" for i,q in gifts)
                embed.add_field(name="🎁 Bonus", value=g_str, inline=False)
            embed.set_footer(text=f"Streak {streak} ngày  •  Đăng nhập mỗi ngày để duy trì streak!")
            await ctx.send(embed=embed)
        except Exception as e:
            import traceback; traceback.print_exc()
            await ctx.send(embed=error(f"Lỗi điểm danh: `{e}`"))

    @commands.command(name="nhiem_vu", aliases=["nhiemvu","nv","quest"])
    async def nhiem_vu(self, ctx, action: str = "xem"):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn!")); return
        if action in ("nhan","claim","lay"): await self._claim(ctx,player)
        else: await self._show_nv(ctx,player)

    async def _show_nv(self,ctx,player):
        today=int(now()//86400)
        db_qs={q["quest_id"]:q for q in await self.bot.db.get_quests(ctx.author.id)}
        embed=discord.Embed(title="NHIEM VU HANG NGAY",color=0x2196F3)
        embed.set_author(name=player["name"],icon_url=ctx.author.display_avatar.url)
        lines=[]; claimable=0
        for q in DAILY_QUESTS:
            dq=db_qs.get(q["id"],{}); reset=dq.get("reset_day",0)
            prog=dq.get("progress",0) if reset>=today else 0
            done=dq.get("completed",0) if reset>=today else 0
            tgt=q["target"]
            if done==2: icon="OK"
            elif done==1: icon="NHAN"; claimable+=1
            elif prog>0: icon="..."
            else: icon="--"
            rw=f"{q.get('reward_ha',0):,} Ha"
            lines.append(f"[{icon}] **{q['name']}** `{prog}/{tgt}` -> {rw}")
        embed.description="\n".join(lines)
        if claimable:
            embed.add_field(name="",value=f"{claimable} nhiem vu xong! Go `,tl nv nhan`",inline=False)
        await ctx.send(embed=embed)

    async def _claim(self,ctx,player):
        today=int(now()//86400)
        db_qs={q["quest_id"]:q for q in await self.bot.db.get_quests(ctx.author.id)}
        claimed=0; ha=0; trung=0
        for q in DAILY_QUESTS:
            dq=db_qs.get(q["id"],{})
            if dq.get("reset_day",0)<today or dq.get("completed",0)!=1: continue
            ha+=q.get("reward_ha",0); trung+=q.get("reward_trung",0); claimed+=1
            await self.bot.db.update_quest(ctx.author.id,q["id"],q["target"],2,today)
        if not claimed:
            await ctx.send(embed=warn("Khong co nhiem vu hoan thanh!")); return
        await self.bot.db.update_player(ctx.author.id,
            linh_thach_ha=_safe(player,"linh_thach_ha")+ha,
            linh_thach_trung=_safe(player,"linh_thach_trung")+trung)
        embed=success(f"NHAN {claimed} NHIEM VU!")
        embed.description=f"+**{ha:,}** Ha"+(f" +**{trung}** Trung" if trung else "")
        await ctx.send(embed=embed)

    @commands.command(name="buff", aliases=["xem_buff","buffs"])
    async def buff(self, ctx):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn!")); return
        uid=str(player.get("user_id",""))
        buffs=self._buffs.get(uid,{})
        active=[(k,v) for k,v in buffs.items() if now()<v]
        embed=discord.Embed(title="BUFF DANG HOAT DONG",color=0x9C27B0)
        embed.set_author(name=player["name"],icon_url=ctx.author.display_avatar.url)
        if not active:
            embed.description="_Khong co buff nao._"
        else:
            BNAMES={"thien_dinh":"Thien Dinh (+50% EXP)","tich_tu_dan":"Tich Tu Dan (+50% EXP)"}
            for k,v in active:
                embed.add_field(name=BNAMES.get(k,k),value=f"Con: `{fmt_time(v-now())}`",inline=True)
        embed.add_field(name="EXP/giay",value=f"`{self.get_exp_rate(player)}`",inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="tuvi", aliases=["xem_tuvi","tv"])
    async def tuvi(self, ctx):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn!")); return
        ri=player["realm_index"]; rt=player["realm_tier"]
        exp_cur=_safe(player,"exp",0); exp_req=get_exp_req(player)
        exp_s=self.get_exp_rate(player); remain=max(0,exp_req-exp_cur)
        eta=int(remain/exp_s) if exp_s>0 else 0
        embed=discord.Embed(title="TIEN DO TU VI",color=realm_color(ri))
        embed.set_author(name=player["name"],icon_url=ctx.author.display_avatar.url)
        embed.add_field(name="Thanh EXP",
            value=f"{bar(exp_cur,exp_req,20)}\n`{_s(exp_cur)}/{_s(exp_req)}`",inline=False)
        embed.add_field(name="Con Thieu",value=f"`{_s(remain)}`",inline=True)
        embed.add_field(name="EXP/giay", value=f"`{exp_s}`",    inline=True)
        embed.add_field(name="Can Be Quan",value=f"`{fmt_time(eta)}`",inline=True)
        lines=[]
        for t in range(rt,min(rt+4,REALMS[ri]["tiers"]+1)):
            if t>REALMS[ri]["tiers"]: break
            need=int(REALMS[ri]["exp"]*(t**REALMS[ri]["mult"]))
            lines.append(f"Tang {t}: `{_s(need)}`")
        if lines: embed.add_field(name="EXP Cac Tang",value="\n".join(lines),inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="doi_ten", aliases=["doiten","rename"])
    async def doi_ten(self, ctx, *, ten: str = None):
        player = await self.bot.db.get_player(ctx.author.id)
        if not ten:
            await ctx.send(embed=warn("Dung: `,tl doi_ten [ten moi]`")); return
        ten=ten.strip()[:20]
        if len(ten)<2:
            await ctx.send(embed=warn("Ten phai co it nhat 2 ky tu!")); return
        COST=5000
        if player["linh_thach_ha"]<COST:
            await ctx.send(embed=warn(f"Can **{COST:,} Ha LT**!")); return
        old=player["name"]
        await self.bot.db.update_player(ctx.author.id,name=ten,linh_thach_ha=player["linh_thach_ha"]-COST)
        embed=success("DOI TEN THANH CONG!")
        embed.description=f"`{old}` -> **{ten}**\n-5,000 Ha LT"
        await ctx.send(embed=embed)

    @commands.command(name="server_stats", aliases=["server","sv"])
    async def server_stats(self,ctx):
        total=await self.bot.db.fetchone("SELECT COUNT(*) as c FROM players")
        top=await self.bot.db.fetchone("SELECT COUNT(*) as c FROM players WHERE realm_index>=10")
        rich=await self.bot.db.fetchone("SELECT SUM(linh_thach_ha) as s FROM players")
        embed=discord.Embed(title="THONG KE SERVER",color=0x2196F3)
        embed.add_field(name="Tong Tu Si",  value=f"`{(total or {}).get('c',0):,}`",inline=True)
        embed.add_field(name="Dat Tien+",   value=f"`{(top or {}).get('c',0):,}`",  inline=True)
        embed.add_field(name="Tong LT",     value=f"`{_s((rich or {}).get('s') or 0)} Ha`",inline=True)
        await ctx.send(embed=embed)

    async def _add_quest(self,uid,qtype,amount):
        today=int(now()//86400)
        db_qs={q["quest_id"]:q for q in await self.bot.db.get_quests(uid)}
        for q in DAILY_QUESTS:
            if q["type"]!=qtype: continue
            dq=db_qs.get(q["id"],{}); reset=dq.get("reset_day",0)
            prog=dq.get("progress",0) if reset>=today else 0
            done=dq.get("completed",0) if reset>=today else 0
            if done: continue
            np=min(prog+amount,q["target"])
            await self.bot.db.update_quest(uid,q["id"],np,1 if np>=q["target"] else 0,today)

async def setup(bot):
    await bot.add_cog(Cultivation(bot))

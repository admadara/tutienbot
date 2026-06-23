"""cogs/boss.py + Tower v3"""
import discord
from discord.ext import commands
import time, random

from utils.helpers import require_player, require_idle, now
from utils.embeds import *
from utils.game_data import WORLD_BOSS, get_tower_boss, TOWER_SHOP, ITEMS

class Boss(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # State được load từ DB trong cog_load, không lưu trong RAM nữa

    async def cog_load(self):
        """Tạo bảng boss_state nếu chưa có và load state hiện tại."""
        await self.bot.db.execute("""
            CREATE TABLE IF NOT EXISTS world_boss_state (
                boss_id   TEXT PRIMARY KEY,
                hp        REAL NOT NULL,
                alive     INTEGER NOT NULL DEFAULT 1,
                respawn_at INTEGER NOT NULL DEFAULT 0
            )
        """)
        row = await self.bot.db.fetchone(
            "SELECT * FROM world_boss_state WHERE boss_id=?", (WORLD_BOSS["id"],)
        )
        if not row:
            await self.bot.db.execute(
                "INSERT INTO world_boss_state(boss_id,hp,alive,respawn_at) VALUES(?,?,1,0)",
                (WORLD_BOSS["id"], float(WORLD_BOSS["hp"]))
            )

    async def _get_state(self):
        row = await self.bot.db.fetchone(
            "SELECT * FROM world_boss_state WHERE boss_id=?", (WORLD_BOSS["id"],)
        )
        return row

    async def _set_state(self, hp, alive, respawn_at):
        await self.bot.db.execute(
            "UPDATE world_boss_state SET hp=?, alive=?, respawn_at=? WHERE boss_id=?",
            (hp, 1 if alive else 0, respawn_at, WORLD_BOSS["id"])
        )

    @commands.group(name="boss", invoke_without_command=True)
    async def boss_cmd(self, ctx):
        state = await self._get_state()
        embed = discord.Embed(title=f"👹 BOSS THẾ GIỚI — {WORLD_BOSS['name']}", color=0xF44336)
        if not state["alive"]:
            # Tự động hồi sinh nếu đã hết thời gian
            if now() >= state["respawn_at"]:
                await self._set_state(float(WORLD_BOSS["hp"]), True, 0)
                state = await self._get_state()
            else:
                rem = state["respawn_at"] - now()
                embed.description = f"💀 **Boss đã bị tiêu diệt!**\nHồi sinh sau: **{fmt_time(max(0,rem))}**"
                embed.color = 0x607D8B
                await ctx.send(embed=embed); return
        pct  = state["hp"] / WORLD_BOSS["hp"]
        bclr = "🟩" if pct > 0.6 else "🟨" if pct > 0.3 else "🟥"
        embed.add_field(name="❤️ HP Boss",
            value=f"{bclr} `{fmt(state['hp'])}` / `{fmt(WORLD_BOSS['hp'])}` ({pct*100:.1f}%)",
            inline=False)
        embed.add_field(name="⚔️ ATK", value=f"`{fmt(WORLD_BOSS['atk'])}`", inline=True)
        embed.add_field(name="🛡️ DEF", value=f"`{fmt(WORLD_BOSS['def'])}`", inline=True)
        embed.add_field(name="🔄 Hồi Sinh", value=f"Sau {WORLD_BOSS['respawn_h']}h khi bị giết", inline=True)
        embed.set_footer(text=",tl boss fight (20 TL)  •  ,tl boss top  •  Tu Tiên Bot v3")
        await ctx.send(embed=embed)

    @boss_cmd.command(name="fight", aliases=["attack","f","danh"])
    async def boss_fight(self, ctx):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        COST = WORLD_BOSS["stamina_cost"]

        state = await self._get_state()
        # Kiểm tra hồi sinh tự động
        if not state["alive"]:
            if now() >= state["respawn_at"]:
                await self._set_state(float(WORLD_BOSS["hp"]), True, 0)
                state = await self._get_state()
            else:
                await ctx.send(embed=warn("Boss chưa hồi sinh!")); return

        if player["stamina"] < COST:
            await ctx.send(embed=warn(f"Cần **{COST} TL**! Có: {player['stamina']}")); return

        atk  = float(player["atk"])
        crit = random.random() < player["crit"] / 100
        dmg  = atk * random.uniform(0.85, 1.15) * (2.0 if crit else 1.0)
        dmg  = max(1.0, dmg - float(WORLD_BOSS["def"]) * 0.1)

        new_hp = max(0, state["hp"] - dmg)

        await self.bot.db.update_player(ctx.author.id,
            stamina=player["stamina"]-COST,
            total_boss_attack=player.get("total_boss_attack",0)+1
        )
        await self.bot.db.add_boss_damage(WORLD_BOSS["id"], ctx.author.id, dmg)

        # Quest
        from utils.game_data import DAILY_QUESTS
        today = int(now()//86400)
        db_qs = {q["quest_id"]:q for q in await self.bot.db.get_quests(ctx.author.id)}
        for q in DAILY_QUESTS:
            if q["type"] != "boss_attack": continue
            dq=db_qs.get(q["id"],{}); reset=dq.get("reset_day",0)
            prog=dq.get("progress",0) if reset>=today else 0
            done=dq.get("completed",0) if reset>=today else 0
            if done: continue
            np=min(prog+1,q["target"])
            await self.bot.db.update_quest(ctx.author.id,q["id"],np,1 if np>=q["target"] else 0,today)

        embed = discord.Embed(color=0xF44336)
        crit_txt = " 💥 **CRIT!**" if crit else ""
        embed.description = (
            f"⚔️ **{player['name']}** tấn công **{WORLD_BOSS['name']}**!{crit_txt}\n"
            f"Gây **{fmt(dmg)}** sát thương!"
        )

        if new_hp <= 0:
            respawn_at = int(now() + WORLD_BOSS["respawn_h"] * 3600)
            await self._set_state(float(WORLD_BOSS["hp"]), False, respawn_at)
            r = WORLD_BOSS
            await self.bot.db.update_player(ctx.author.id,
                linh_thach_ha=player["linh_thach_ha"]+r["reward_ha"],
                linh_thach_trung=player["linh_thach_trung"]+r["reward_trung"]
            )
            embed.color = 0xFFD700
            embed.add_field(name="💀 BOSS BỊ TIÊU DIỆT!", value=(
                f"**{player['name']}** đã kết liễu Boss!\n"
                f"🏆 +**{r['reward_ha']:,}** Hạ  +**{r['reward_trung']}** Trung LT"
            ), inline=False)
        else:
            await self._set_state(new_hp, True, 0)
            pct = new_hp / WORLD_BOSS["hp"]
            embed.add_field(name="❤️ HP Còn Lại",
                value=f"`{fmt(new_hp)}` ({pct*100:.1f}%)", inline=True)
            embed.add_field(name="🔋 TL Còn Lại",
                value=f"`{player['stamina']-COST}`", inline=True)
        await ctx.send(embed=embed)

    @boss_cmd.command(name="top", aliases=["bxh"])
    async def boss_top(self, ctx):
        rows = await self.bot.db.get_boss_top(WORLD_BOSS["id"], 10)
        embed = discord.Embed(title="🏆 BXH SÁT THƯƠNG BOSS", color=0xFF9800)
        medals = ["🥇","🥈","🥉"]+["🏅"]*7
        for i, r in enumerate(rows):
            p = await self.bot.db.get_player(r["user_id"])
            name = p["name"] if p else f"ID:{r['user_id']}"
            embed.add_field(name=f"{medals[i]} {name}",
                value=f"Tổng DMG: `{fmt(r['total'])}`", inline=False)
        if not rows: embed.description = "_Chưa ai tấn công Boss._"
        await ctx.send(embed=embed)


class Tower(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @commands.group(name="thap", aliases=["tower"], invoke_without_command=True)
    async def thap(self, ctx):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        tw = await self.bot.db.get_tower(ctx.author.id)
        total = tw["total_attempts"]
        wins  = tw["total_wins"]
        wr    = f"{wins/total*100:.0f}%" if total else "0%"
        stamina_val = player.get("stamina", 0)
        stamina_max = player.get("stamina_max", 100)
        conquered = tw["weekly_floor"] > 0 and tw["weekly_floor"] >= tw["best_floor"]
        status_line = "👑 TRẠNG THÁI: ĐÃ CHINH PHỤC (Chờ reset tuần)" if conquered else "⚔️ TRẠNG THÁI: Đang leo tháp"
        desc = (
            f"{status_line}\n"
            f"🏆 Cao nhất: Tầng {tw['best_floor']} (Tuần này: {tw['weekly_floor']})\n"
            f"⚡ Stamina: {stamina_val}/{stamina_max}\n\n"
            f"📊 Thống kê:\n"
            f"   • Tổng lần thử: {total:,}\n"
            f"   • Tỷ lệ thắng: {wr}\n\n"
            f"🎟️ Ma Tôn Lệnh: {tw['ma_ton_lenh']:,}\n\n"
        )
        if conquered:
            desc += "🎉 Bạn đã nhận hết phần thưởng tuần này!\n\n"
        desc += (
            "Lệnh:\n"
            "• `,tuluyen thap challenge` - Thách đấu\n"
            "• `,tuluyen thap auto` - Tự động leo tháp ⚡\n"
            "• `,tuluyen thap top` - Bảng xếp hạng\n"
            "• `,tuluyen thap shop` - Cửa hàng đổi Ma Tôn Lệnh\n"
            "• `,tuluyen thap rewards [tầng]` - Xem rewards"
        )
        embed = discord.Embed(title="🗼 THIÊN TẦNG THÁP 🗼", description=desc, color=0x9C27B0)
        embed.set_author(name=player["name"], icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

    @thap.command(name="challenge", aliases=["c","fight","danh"])
    async def challenge(self, ctx):
        import math as _m
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        tw    = await self.bot.db.get_tower(ctx.author.id)
        floor = tw["best_floor"] + 1
        if floor > 300:
            await ctx.send(embed=warn("👑 Đã chinh phục đỉnh tháp 300!")); return
        boss  = get_tower_boss(floor)
        STAMINA_COST = 15

        stamina = player.get("stamina", 0)
        if stamina < STAMINA_COST:
            await ctx.send(embed=warn(f"⚡ Không đủ thể lực! Cần **{STAMINA_COST}**, có **{stamina}**.")); return

        # ── Thống số ──────────────────────────────────
        p_atk  = float(player.get("atk", 100))
        p_def  = float(player.get("def_", 50))
        p_hp   = float(player.get("hp_max", 1000))
        p_crit = float(player.get("crit", 5))
        b_atk  = float(boss["atk"])
        b_def  = float(boss["def"])
        b_hp   = float(boss["hp"])

        # ── Chiến đấu theo lượt ───────────────────────
        def calc_dmg(atk, def_, is_crit):
            dr   = min(0.85, def_ / (def_ + atk + 1))
            base = atk * random.uniform(0.85, 1.15) * (1 - dr)
            return max(int(atk * 0.01), int(base * (2 if is_crit else 1)))

        cur_p_hp = p_hp
        cur_b_hp = b_hp
        log = []
        MAX_ROUNDS = 20  # hiện tối đa 20 hiệp trong embed

        for rnd in range(1, 101):
            if cur_p_hp <= 0 or cur_b_hp <= 0: break
            # Boss đánh người
            b_crit = random.random() < 0.15
            b_dmg  = calc_dmg(b_atk, p_def, b_crit)
            cur_p_hp -= b_dmg
            b_line = f"{'💥 [Bạo Kích] ' if b_crit else ''}🗡️ Boss Tháp chém trúng **{player['name']}**, gây `{fmt(b_dmg)}` sát thương!"
            # Người đánh boss
            p_crit_hit = random.random() < p_crit / 100.0
            p_dmg = calc_dmg(p_atk, b_def, p_crit_hit)
            cur_b_hp -= p_dmg
            p_line = f"{'💥 [Bạo Kích] ' if p_crit_hit else ''}⚔️ **{player['name']}** chém trúng Boss Tháp, gây `{fmt(p_dmg)}` sát thương!"
            if len(log) < MAX_ROUNDS * 2:
                log.append(f"--- Hiệp {rnd} ---")
                log.append(b_line)
                log.append(p_line)

        won = cur_p_hp > 0
        new_attempts = tw["total_attempts"] + 1
        mt_reward    = floor * 10

        # Tính EXP/LT thưởng
        A_EXP, R_EXP = 138888.0, 1.08
        A_LT,  R_LT  = 36.0,     1.06
        floor_exp = int(A_EXP * (R_EXP ** floor))
        floor_lt  = int(A_LT  * (R_LT  ** floor))

        battle_log = "\n".join(log[:40])  # tối đa ~20 hiệp
        if len(log) > 40:
            skipped = len(log) - 40
            battle_log += f"\n... _(lược bớt {skipped} dòng)_ ..."
            battle_log += "\n" + "\n".join(log[-6:])

        if won:
            await self.bot.db.update_tower(ctx.author.id,
                best_floor=floor, weekly_floor=max(tw["weekly_floor"], floor),
                total_attempts=new_attempts, total_wins=tw["total_wins"]+1,
                ma_ton_lenh=tw["ma_ton_lenh"]+mt_reward,
            )
            await self.bot.db.update_player(ctx.author.id,
                stamina=max(0, stamina - STAMINA_COST),
                exp=player.get("exp",0)+floor_exp,
                linh_thach_ha=player.get("linh_thach_ha",0)+floor_lt,
            )
            result_text = (
                f"\n\n🏆 **THẮNG!**\n"
                f"❤️ HP còn lại: `{fmt(max(0,cur_p_hp))}/{fmt(p_hp)}`\n"
                f"🎟️ +{mt_reward} Ma Tôn Lệnh | 📚 +{fmt(floor_exp)} EXP | 💰 +{fmt(floor_lt)} LT\n"
                f"🏆 Tầng cao nhất: **{floor}** | ⚡ Mất {STAMINA_COST} Stamina"
            )
            color = 0xFFD700
            title = f"✅ THÁCH ĐẤU THÁP TẦNG {floor} THÀNH CÔNG!"
        else:
            await self.bot.db.update_tower(ctx.author.id, total_attempts=new_attempts)
            await self.bot.db.update_player(ctx.author.id, stamina=max(0, stamina - STAMINA_COST))
            result_text = (
                f"\n\n💀 **THẤT BẠI!**\n"
                f"Boss còn `{fmt(max(0,cur_b_hp))}` HP.\n"
                f"💔 Bạn đã bị trọng thương (HP = 0)!\n"
                f"⚡ Mất {STAMINA_COST} Stamina | 💡 Nâng cấp trang bị hoặc đột phá cảnh giới!"
            )
            color = 0xF44336
            title = f"💥 THÁCH ĐẤU THÁP TẦNG {floor} THẤT BẠI!"

        header = (
            f"🔥 Boss: **{boss['name']}**\n"
            f"💪 Boss HP: `{fmt(b_hp)}` | ATK: `{fmt(b_atk)}` | DEF: `{fmt(b_def)}`\n"
            f"🧑 Bạn: HP `{fmt(p_hp)}` | ATK: `{fmt(p_atk)}` | DEF: `{fmt(p_def)}`\n\n"
        )
        desc = header + battle_log + result_text
        # Discord embed tối đa 4096 ký tự
        if len(desc) > 4000:
            desc = header + "_(log chiến đấu quá dài, rút gọn)_\n" + "\n".join(log[-10:]) + result_text
        embed = discord.Embed(title=title, description=desc, color=color)
        await ctx.send(embed=embed)

    @thap.command(name="auto", aliases=["a"])
    async def auto(self, ctx):
        """Auto leo tháp dựa trên stamina, tối đa 50 tầng/lần, tháp max 300 tầng."""
        import math as _m
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return

        tw = await self.bot.db.get_tower(ctx.author.id)
        cur_floor = tw["best_floor"]
        TOWER_MAX = 300
        STAMINA_PER_FLOOR = 1
        MAX_FLOORS = 50

        if cur_floor >= TOWER_MAX:
            await ctx.send(embed=warn("👑 Đã chinh phục đỉnh tháp! Chờ reset tuần.")); return

        stamina = player.get("stamina", 0)
        if stamina < STAMINA_PER_FLOOR:
            await ctx.send(embed=warn(f"⚡ Không đủ thể lực! Cần ít nhất **{STAMINA_PER_FLOOR}**.")); return

        max_by_stamina = stamina // STAMINA_PER_FLOOR
        max_by_tower   = TOWER_MAX - cur_floor
        so_tang = min(MAX_FLOORS, max_by_stamina, max_by_tower)

        MILESTONES = {
            10:  {"item": "Tháp Thần Kiếm",     "lt": 50_000,           "exp": 0},
            20:  {"item": "Tháp Linh Y",         "lt": 0,                "exp": 2_000_000},
            30:  {"item": "Thăng Thiên Đan",     "lt": 150_000,          "exp": 0},
            40:  {"item": "Thiên Long Thương",   "lt": 0,                "exp": 10_000_000},
            50:  {"item": "Phong Thần Giáp",     "lt": 500_000,          "exp": 0},
            60:  {"item": "Hắc Long Kiếm",       "lt": 0,                "exp": 50_000_000},
            70:  {"item": "Thần Phong Đao",      "lt": 1_000_000,        "exp": 0},
            80:  {"item": "Thiên Tàm Ty",        "lt": 0,                "exp": 200_000_000},
            90:  {"item": "Cửu Thiên Huyền Thể", "lt": 2_000_000,        "exp": 0},
            100: {"item": "Vạn Tượng Thiên Kinh","lt": 0,                "exp": 1_000_000_000},
            150: {"item": "Hỗn Độn Linh Châu",  "lt": 10_000_000,       "exp": 10_000_000_000},
            200: {"item": "Thái Cực Thần Ấn",   "lt": 0,                "exp": 100_000_000_000},
            250: {"item": "Vô Cực Thiên Đao",   "lt": 50_000_000,       "exp": 500_000_000_000},
            300: {"item": "Vô Thượng Linh Bảo", "lt": 100_000_000,      "exp": 1_000_000_000_000},
        }

        def calc_dmg(atk, def_, is_crit):
            dr   = min(0.85, def_ / (def_ + atk + 1))
            base = atk * random.uniform(0.85, 1.15) * (1 - dr)
            return max(int(atk * 0.01), int(base * (2 if is_crit else 1)))

        def simulate_floor(p, boss):
            p_atk = float(p.get("atk", 100))
            p_def = float(p.get("def_", 50))
            p_hp  = float(p.get("hp_max", 1000))
            p_crit= float(p.get("crit", 5))
            b_atk = float(boss["atk"])
            b_def = float(boss["def"])
            cur_p = p_hp; cur_b = float(boss["hp"])
            for _ in range(200):
                if cur_p <= 0 or cur_b <= 0: break
                cur_p -= calc_dmg(b_atk, p_def, random.random() < 0.15)
                if cur_p <= 0: break
                cur_b -= calc_dmg(p_atk, b_def, random.random() < p_crit/100)
            return cur_p > 0  # True = thắng

        A_EXP, R_EXP = 138888.0, 1.08
        A_LT,  R_LT  = 36.0,     1.06

        wins = 0; total_exp = 0; total_lt = 0; mt_total = 0
        milestones_hit = []; stop_reason = ""
        start = cur_floor + 1

        for f in range(start, start + so_tang):
            boss = get_tower_boss(f)
            if not simulate_floor(player, boss):
                stop_reason = f"❌ Thất bại tại tầng **{f}**"
                break
            wins += 1; mt_total += f * 10
            total_exp += int(A_EXP * (R_EXP ** f))
            total_lt  += int(A_LT  * (R_LT  ** f))
            if f % 10 == 0 and f in MILESTONES:
                ms = MILESTONES[f]
                total_lt  += ms["lt"]
                total_exp += ms["exp"]
                milestones_hit.append((f, ms))

        if wins == 0:
            embed = discord.Embed(
                title="🤖 KẾT QUẢ AUTO LEO THÁP 🤖",
                description=f"{stop_reason}\nCần nâng cấp trang bị & Linh Thú.",
                color=0xF44336
            )
            await ctx.send(embed=embed)
            return

        new_best = cur_floor + wins
        stamina_used = wins * STAMINA_PER_FLOOR
        new_stamina  = max(0, stamina - stamina_used)

        if new_best >= TOWER_MAX:
            stop_reason = "👑 Đã chinh phục đỉnh tháp!"
        elif not stop_reason:
            stop_reason = f"⚡ Hết thể lực (còn {new_stamina})"

        await self.bot.db.update_tower(ctx.author.id,
            best_floor=new_best,
            weekly_floor=max(tw["weekly_floor"], new_best),
            total_attempts=tw["total_attempts"] + wins,
            total_wins=tw["total_wins"] + wins,
            ma_ton_lenh=tw["ma_ton_lenh"] + mt_total,
        )
        await self.bot.db.update_player(ctx.author.id,
            exp=player.get("exp", 0) + total_exp,
            linh_thach_ha=player.get("linh_thach_ha", 0) + total_lt,
            stamina=new_stamina,
        )

        desc = (
            f"✅ Đã vượt qua: **{wins}** tầng (Tầng {cur_floor} → {new_best})\n"
            f"💰 Tổng Linh Thạch: **+{fmt(total_lt)}**\n"
            f"📚 Tổng EXP: **+{fmt(total_exp)}**\n"
            f"🎟️ Ma Tôn Lệnh: **+{mt_total:,}**\n"
            f"⚡ Thể lực dùng: **{stamina_used}** (còn {new_stamina})\n\n"
            f"🛑 Dừng lại: {stop_reason}"
        )
        if milestones_hit:
            desc += "\n\n🎁 **MILESTONE ĐẠT ĐƯỢC:**\n"
            for (mf, ms) in milestones_hit:
                bonus = f"+{fmt(ms['lt'])} LT" if ms["lt"] else f"+{fmt(ms['exp'])} EXP"
                desc += f"  • Tầng {mf}: **{ms['item']}** ({bonus})\n"

        embed = discord.Embed(title="🤖 KẾT QUẢ AUTO LEO THÁP 🤖", description=desc, color=0xFFD700)
        embed.set_footer(text=f"🏆 Tầng cao nhất: {new_best}/300  •  Tu Tiên Bot v4")
        await ctx.send(embed=embed)

    @thap.command(name="top")
    async def thap_top(self, ctx, pham_vi: str = None):
        is_global = (pham_vi and pham_vi.lower() in ("all", "global", "toancau")) or not ctx.guild
        if is_global:
            rows = await self.bot.db.fetchall(
                "SELECT * FROM tower ORDER BY best_floor DESC LIMIT 10"
            )
        else:
            rows = await self.bot.db.fetchall(
                "SELECT t.* FROM tower t JOIN players p ON p.user_id = t.user_id "
                "WHERE p.guild_id=? ORDER BY t.best_floor DESC LIMIT 10",
                (str(ctx.guild.id),)
            )
        title = "🏆 BXH THIÊN TẦNG THÁP" + (" (Toàn Server Bot)" if is_global else "")
        embed = discord.Embed(title=title, color=0xFFD700)
        medals = ["🥇","🥈","🥉"]+["🏅"]*7
        for i, r in enumerate(rows):
            p = await self.bot.db.get_player(r["user_id"])
            name = p["name"] if p else f"ID:{r['user_id']}"
            wr = f"{r['total_wins']/max(r['total_attempts'],1)*100:.0f}%"
            embed.add_field(name=f"{medals[i]} {name}",
                value=f"Tầng **{r['best_floor']}**  •  Tỉ lệ thắng: {wr}", inline=False)
        if not rows:
            embed.description = "_Chưa ai leo tháp trong server này._" if not is_global else "_Chưa ai leo tháp._"
        embed.set_footer(text=",tl thap top [all]")
        await ctx.send(embed=embed)

    @thap.command(name="shop", aliases=["store"])
    async def thap_shop(self, ctx):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        tw = await self.bot.db.get_tower(ctx.author.id)
        embed = discord.Embed(title="🛒 SHOP MA TÔN LỆNH", color=0x9C27B0)
        embed.description = f"🎟️ Bạn có **{tw['ma_ton_lenh']:,}** Ma Tôn Lệnh"
        for i, item in enumerate(TOWER_SHOP, 1):
            embed.add_field(
                name=f"{i}. {item['name']}",
                value=f"🎟️ **{item['cost']:,}** MTL  •  Nhận: {item['qty']}x",
                inline=True
            )
        embed.set_footer(text=",tl thap shop mua [số] để mua")
        await ctx.send(embed=embed)

    @thap.command(name="mua", aliases=["buy"])
    async def thap_mua(self, ctx, so: int):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        tw = await self.bot.db.get_tower(ctx.author.id)
        if so < 1 or so > len(TOWER_SHOP):
            await ctx.send(embed=warn(f"Chọn 1-{len(TOWER_SHOP)}!")); return
        item = TOWER_SHOP[so-1]
        if tw["ma_ton_lenh"] < item["cost"]:
            await ctx.send(embed=warn(f"Không đủ Ma Tôn Lệnh! Cần **{item['cost']:,}**")); return
        await self.bot.db.update_tower(ctx.author.id, ma_ton_lenh=tw["ma_ton_lenh"]-item["cost"])
        await self.bot.db.add_item(ctx.author.id, item["id"], item["qty"])
        embed = success("✅ MUA THÀNH CÔNG",
            f"**{item['qty']}x {item['name']}** — 🎟️ -{item['cost']:,} MTL"
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Boss(bot))
    await bot.add_cog(Tower(bot))

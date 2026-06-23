"""cogs/exploration.py - Bí cảnh v3 FIX KEY"""
import discord
from discord.ext import commands
import time, random, json

from utils.helpers import require_player, require_idle, now
from utils.embeds import fmt, fmt_time, make, warn, error, success, bar, realm_color
from utils.game_data import AREAS, ITEMS, get_exp_req

class Exploration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._menu: dict = {}  # user_id -> (areas_list, timestamp)

    @commands.group(name="bicanh", aliases=["bc","explore"], invoke_without_command=True)
    async def bicanh(self, ctx):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        await self.bicanh_list(ctx, player=player)

    @bicanh.command(name="list", aliases=["ls","map","xem"])
    async def bicanh_list(self, ctx):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        ri   = player["realm_index"]
        stam = player["stamina"]; smax = player["stamina_max"]

        # Tất cả khu vực + tính thời gian theo cảnh giới (mỗi realm +20 phút base)
        all_areas = AREAS  # Hiện tất cả, đánh dấu khóa nếu chưa đủ cảnh giới
        embed = discord.Embed(title="🗺️ BẢN ĐỒ BÍ CẢNH TU TIÊN", color=0x2196F3)
        embed.description = (
            f"🔋 **Thể Lực:** `{stam}/{smax}`  |  "
            f"🌌 **Cảnh Giới:** `{player.get('realm_index',0)}`\n"
            f"Gõ `,tl bc di [số]` để xuất phát!"
        )
        available = []
        for i, a in enumerate(all_areas, 1):
            can_enter = ri >= a["min_realm"]
            can_stam  = stam >= a["stamina_cost"]
            dmin, dmax = a["duration_min"], a["duration_max"]

            if can_enter:
                status = "✅" if can_stam else f"❌ TL"
                available.append(a)
            else:
                from utils.game_data import REALMS
                need_realm = REALMS[a["min_realm"]]["name"] if a["min_realm"] < len(REALMS) else "?"
                status = f"🔒 Cần {need_realm}"

            embed.add_field(
                name=f"`{i}.` {a['name']}",
                value=(
                    f"_{a['desc']}_\n"
                    f"⏱️ `{a['duration_min']}-{a['duration_max']}` phút  {status} `{a['stamina_cost']} TL`\n"
                    f"💰 `{fmt(a['lt_min'])}`-`{fmt(a['lt_max'])}` Hạ  "
                    f"✨ `{fmt(a['exp_min'])}`-`{fmt(a['exp_max'])}` EXP"
                ),
                inline=False
            )

        embed.set_footer(text=",tl bc di [số 1-6] | ,tl bc ve để về | Thời gian tăng theo cảnh giới")
        await ctx.send(embed=embed)
        self._menu[ctx.author.id] = (all_areas, time.time())

    @bicanh.command(name="di", aliases=["go","vao","enter"])
    async def bicanh_di(self, ctx, area_id: str = None):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        # Số thứ tự nhanh
        if area_id and area_id.isdigit():
            ctx_data = self._menu.get(ctx.author.id)
            if ctx_data and time.time() - ctx_data[1] < 300:
                idx = int(area_id) - 1
                if 0 <= idx < len(ctx_data[0]):
                    area_id = ctx_data[0][idx]["id"]

        # Tìm khu vực
        area = None
        if area_id:
            area = next((a for a in AREAS if a["id"] == area_id), None)
        if not area:
            # Auto chọn cao nhất phù hợp
            ri = player["realm_index"]
            avail = [a for a in AREAS if a["min_realm"] <= ri <= a["max_realm"]]
            if not avail:
                await ctx.send(embed=error("Không có bí cảnh phù hợp với cảnh giới của bạn!"))
                return
            area = avail[-1]

        # Kiểm tra cảnh giới
        if player["realm_index"] < area["min_realm"]:
            from utils.game_data import REALMS
            need = REALMS[area["min_realm"]]["name"]
            await ctx.send(embed=error(f"Cần đạt **{need}** mới vào được **{area['name']}**!"))
            return

        # Kiểm tra thể lực
        if player["stamina"] < area["stamina_cost"]:
            await ctx.send(embed=warn(
                f"Không đủ Thể Lực!\n"
                f"Cần: **{area['stamina_cost']} TL** | Có: **{player['stamina']} TL**\n"
                f"Dùng `,tl use phuc_tinh_dan` để hồi TL"
            ))
            return

        duration = random.randint(area["duration_min"], area["duration_max"])
        await self.bot.db.update_player(
            ctx.author.id,
            status="thamHiem",
            status_start=now(),
            status_data=json.dumps({"area_id": area["id"], "duration": duration}),
            stamina=player["stamina"] - area["stamina_cost"],
        )

        embed = discord.Embed(
            title=f"⚔️ BẮT ĐẦU THÁM HIỂM",
            description=f"**{player['name']}** tiến vào **{area['name']}**!",
            color=0xFF9800
        )
        embed.add_field(name="⏱️ Dự Kiến",   value=f"`{duration} phút`",           inline=True)
        embed.add_field(name="⚡ Thể Lực",    value=f"`-{area['stamina_cost']} TL`", inline=True)
        embed.add_field(name="💰 Thưởng Dự Kiến",
            value=f"EXP: `{fmt(area['exp_min'])}`-`{fmt(area['exp_max'])}`\nLT: `{fmt(area['lt_min'])}`-`{fmt(area['lt_max'])}` Hạ",
            inline=False
        )
        embed.set_footer(text=f"Gõ ,tl bicanh ve sau {area['duration_min']} phút để nhận thưởng!")
        await ctx.send(embed=embed)

    @bicanh.command(name="ve", aliases=["return","back","ra"])
    async def bicanh_ve(self, ctx):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        if player["status"] != "thamHiem":
            await ctx.send(embed=warn("Không đang thám hiểm! Dùng `,tl bicanh di` để bắt đầu."))
            return

        elapsed_s  = now() - player["status_start"]
        elapsed_m  = elapsed_s / 60
        data       = json.loads(player.get("status_data") or "{}")
        duration   = data.get("duration", 10)
        area_id    = data.get("area_id", "rung_linh_moc")
        area       = next((a for a in AREAS if a["id"] == area_id), AREAS[0])
        min_time   = area["duration_min"]

        if elapsed_m < min_time:
            rem = int((min_time - elapsed_m) * 60)
            await ctx.send(embed=warn(f"Chưa đủ thời gian! Còn **{fmt_time(rem)}** nữa."))
            return

        # Tính ratio theo thời gian (tối đa 120% nếu ở lâu)
        ratio      = min(elapsed_m / max(duration, 1), 1.2)

        exp_gained = int(random.randint(area["exp_min"], area["exp_max"]) * ratio)
        lt_gained  = int(random.randint(area["lt_min"],  area["lt_max"])  * ratio)

        # Drop vật phẩm
        drops = []
        drop_log = []

        # Drops thông thường
        num_drops = int(elapsed_m / 10) + 1  # Mỗi 10 phút thêm 1 lần drop
        for _ in range(min(num_drops, 8)):
            if random.random() < area["drop_rate"]:
                item_id = random.choice(area["drop_items"])
                qty = random.randint(1, 3)
                await self.bot.db.add_item(ctx.author.id, item_id, qty)
                iname = ITEMS.get(item_id, {}).get("name", item_id)
                # Gộp cùng loại
                found = next((d for d in drops if d[0]==item_id), None)
                if found: found[1] += qty
                else: drops.append([item_id, qty, iname])

        # Rare drop
        if random.random() < 0.05:
            await self.bot.db.add_item(ctx.author.id, "101", 1)
            drops.append(["101", 1, "Rương Bạc"])

        # Sự kiện ngẫu nhiên
        events = []
        for _ in range(int(elapsed_m / 15)):
            roll = random.random()
            if roll < 0.15:
                bonus_exp = int(exp_gained * 0.1)
                exp_gained += bonus_exp
                events.append(f"✨ Gặp lão ăn mày bí ẩn, được truyền thụ **{fmt(bonus_exp)}** EXP.")
            elif roll < 0.25:
                bonus_lt = int(lt_gained * 0.2)
                lt_gained += bonus_lt
                events.append(f"💰 Tìm thấy linh thạch ẩn, thu được **{fmt(bonus_lt)}** Hạ LT.")
            elif roll < 0.30:
                boss_exp = int(exp_gained * 0.15)
                boss_lt  = random.randint(50, 200)
                exp_gained += boss_exp
                lt_gained  += boss_lt
                events.append(f"🔥 Đánh bại Boss bí cảnh: **+{fmt(boss_exp)}** EXP, **+{boss_lt}** LT!")

        exp_req   = get_exp_req(player)
        new_exp   = min(int(player.get("exp", 0)) + exp_gained, exp_req)
        new_lt    = int(player.get("linh_thach_ha", 0)) + lt_gained
        new_explore = player.get("total_explore", 0) + 1

        await self.bot.db.update_player(
            ctx.author.id,
            status="idle", status_start=0, status_data="{}",
            exp=new_exp,
            linh_thach_ha=new_lt,
            total_explore=new_explore,
        )
        await self._quest(ctx.author.id, "explore_count", 1)

        embed = discord.Embed(
            title=f"🏁 THÁM HIỂM: {area['name']} 🏁",
            color=0x4CAF50
        )
        embed.set_author(name=player["name"], icon_url=ctx.author.display_avatar.url)
        embed.add_field(name="⏱️ Thời Gian",   value=f"`{fmt_time(int(elapsed_s))}`", inline=True)
        embed.add_field(name="🆙 EXP",          value=f"`+{fmt(exp_gained)}`",         inline=True)
        embed.add_field(name="💰 Linh Thạch",   value=f"`+{fmt(lt_gained)} Hạ`",       inline=True)
        embed.add_field(
            name="📊 Tiến Độ EXP",
            value=f"{bar(new_exp, exp_req, 18)}\n`{fmt(new_exp)}/{fmt(exp_req)}`",
            inline=False
        )
        if drops:
            drop_str = ", ".join(f"**{d[2]}** x{d[1]}" for d in drops)
            embed.add_field(name="🎒 Vật Phẩm", value=drop_str, inline=False)
        if events:
            embed.add_field(name="📝 Nhật Ký Sự Kiện", value="\n".join(events[:6]), inline=False)
        if new_exp >= exp_req:
            embed.add_field(name="⚡", value="**Tu Vi đầy! Gõ `,tl dp` để đột phá!**", inline=False)
        embed.set_footer(text=f"Tổng thám hiểm: {new_explore} lần  •  Tu Tiên Bot v4")
        await ctx.send(embed=embed)

    async def _quest(self, uid, qtype, amount):
        """Update quest progress"""
        from utils.game_data import DAILY_QUESTS
        today = int(now() // 86400)
        db_qs = {q["quest_id"]: q for q in await self.bot.db.get_quests(uid)}
        for q in DAILY_QUESTS:
            if q["type"] != qtype: continue
            dq    = db_qs.get(q["id"], {})
            reset = dq.get("reset_day", 0)
            prog  = dq.get("progress", 0) if reset >= today else 0
            done  = dq.get("completed", 0) if reset >= today else 0
            if done: continue
            new_p = min(prog + amount, q["target"])
            await self.bot.db.update_quest(uid, q["id"], new_p, 1 if new_p >= q["target"] else 0, today)

    # Số thứ tự nhanh
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot: return
        data = self._menu.get(message.author.id)
        if not data: return
        content = message.content.strip()
        for pf in (",tl ", ",tuluyen "):
            if content.startswith(pf):
                arg = content[len(pf):].strip()
                if arg.isdigit() and time.time() - data[1] < 300:
                    idx = int(arg) - 1
                    if 0 <= idx < len(data[0]):
                        del self._menu[message.author.id]
                        ctx2 = await self.bot.get_context(message)
                        await self.bicanh_di(ctx2, area_id=data[0][idx]["id"])
                break

async def setup(bot):
    await bot.add_cog(Exploration(bot))

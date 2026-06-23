"""cogs/extra_commands.py - 10 lệnh mới v3"""
import discord
from discord.ext import commands
import random, time, json

from utils.helpers import require_player, require_idle, now
from utils.embeds import *
from utils.game_data import (
    REALMS, DAO, ITEMS, LINHTHU_DATA, AREAS,
    get_realm_name, get_exp_req, fmt_number
)
from utils.persistent_cache import PersistentCache

class ExtraCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._meditation = PersistentCache(bot, "meditation_buffs")  # user_id -> expire_time

    async def cog_load(self):
        await self._meditation.load()

    async def cog_unload(self):
        await self._meditation.save()

    # ══ 1. ,tl thien_dinh ════════════════════════════════
    @commands.command(name="thien_dinh", aliases=["thiendinh","td","meditate"])
    async def thien_dinh(self, ctx):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        """Thiền định 10 phút: +50% EXP rate trong 1 giờ (cooldown 6h)"""
        uid = str(ctx.author.id)
        expire = self._meditation.get(uid, 0)
        if now() < expire:
            rem = expire - now()
            await ctx.send(embed=warn(f"Thiền định đang hồi chiêu!\nCòn **{fmt_time(rem)}** nữa."))
            return

        cost_stam = 20
        if player["stamina"] < cost_stam:
            await ctx.send(embed=warn(f"Cần **{cost_stam} TL** để thiền định!"))
            return

        # Buff 1 giờ
        self._meditation[uid] = now() + 3600
        cooldown_end = now() + 6 * 3600

        await self.bot.db.update_player(ctx.author.id,
            status="beQuan",
            status_start=now(),
            stamina=player["stamina"] - cost_stam,
        )

        embed = discord.Embed(
            title="🧘 THIỀN ĐỊNH",
            description=(
                f"**{player['name']}** nhập vào trạng thái thiền sâu...\n\n"
                f"✨ **+50% EXP Rate** trong 1 giờ\n"
                f"🔋 **-{cost_stam} TL**\n"
                f"⏱️ Hồi chiêu sau **6 giờ**"
            ),
            color=0x9C27B0
        )
        embed.set_footer(text="Gõ ,tl stop để kết thúc bế quan và nhận EXP")
        await ctx.send(embed=embed)

    # ══ 2. ,tl kham_pha ══════════════════════════════════
    @commands.command(name="kham_pha", aliases=["khampha","khamphacanh"])
    async def kham_pha(self, ctx):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        """Khám phá ngẫu nhiên - có thể tìm thấy đồ, LT hoặc gặp hiểm nguy"""
        COST = 15
        if player["stamina"] < COST:
            await ctx.send(embed=warn(f"Cần **{COST} TL** để khám phá!"))
            return
        if player["status"] != "idle":
            await ctx.send(embed=warn("Đang bận! Kết thúc hoạt động hiện tại trước."))
            return

        await self.bot.db.update_player(ctx.author.id, stamina=player["stamina"] - COST)

        roll = random.random()
        embed = discord.Embed(title="🔍 KHÁM PHÁ NGẪU NHIÊN", color=0x2196F3)

        if roll < 0.05:  # 5% - Đại may mắn
            reward_ha = random.randint(10000, 50000)
            await self.bot.db.update_player(ctx.author.id,
                linh_thach_ha=player["linh_thach_ha"] + reward_ha)
            embed.color = 0xFFD700
            embed.description = (
                f"✨ **ĐẠI MAY MẮN!**\n"
                f"Tìm thấy **Linh Thạch Cổ Đại**!\n"
                f"💰 +**{reward_ha:,}** Hạ LT"
            )
        elif roll < 0.20:  # 15% - Vật phẩm hiếm
            items_pool = ["102", "203", "403", "204"]
            item_id = random.choice(items_pool)
            qty = random.randint(1, 2)
            await self.bot.db.add_item(ctx.author.id, item_id, qty)
            iname = ITEMS.get(item_id, {}).get("name", item_id)
            embed.color = 0xFF9800
            embed.description = f"🎁 Tìm thấy **{qty}x {iname}**!"
        elif roll < 0.50:  # 30% - Vật phẩm thường
            items_pool = ["202", "201", "301", "101"]
            item_id = random.choice(items_pool)
            qty = random.randint(1, 3)
            await self.bot.db.add_item(ctx.author.id, item_id, qty)
            iname = ITEMS.get(item_id, {}).get("name", item_id)
            embed.description = f"📦 Tìm thấy **{qty}x {iname}**!"
        elif roll < 0.65:  # 15% - LT nhỏ
            reward = random.randint(500, 3000)
            await self.bot.db.update_player(ctx.author.id,
                linh_thach_ha=player["linh_thach_ha"] + reward)
            embed.description = f"💰 Tìm thấy **{reward:,} Hạ LT** rải rác!"
        elif roll < 0.80:  # 15% - Không có gì
            embed.color = 0x607D8B
            embed.description = "🌫️ Chẳng tìm thấy gì đặc biệt trong lần này..."
        else:  # 20% - Gặp nạn, mất TL
            lost = random.randint(10, 30)
            new_stam = max(0, player["stamina"] - COST - lost)
            await self.bot.db.update_player(ctx.author.id, stamina=new_stam)
            embed.color = 0xF44336
            embed.description = (
                f"💀 **PHỤC KÍCH!**\n"
                f"Gặp Ma Thú bất ngờ!\n"
                f"🔋 Mất thêm **{lost} TL**"
            )

        embed.set_footer(text=f"TL còn lại: {player['stamina'] - COST}  •  -15 TL mỗi lần khám phá")
        await ctx.send(embed=embed)

    # ══ 3. ,tl bang_hoi ══════════════════════════════════
    @commands.command(name="bang_hoi", aliases=["banghoi","bh","guild_info"])
    async def bang_hoi(self, ctx):
        """Xem top 5 Tông Môn mạnh nhất"""
        sects = await self.bot.db.fetchall(
            "SELECT tm.*, COUNT(p.user_id) as member_count "
            "FROM tong_mon tm LEFT JOIN players p ON p.tong_mon_id = tm.id "
            "GROUP BY tm.id ORDER BY tm.level DESC, member_count DESC LIMIT 5"
        )
        embed = discord.Embed(title="⛩️ BẢNG XẾP HẠNG TÔNG MÔN", color=0x795548)
        if not sects:
            embed.description = "_Chưa có Tông Môn nào được thành lập._"
        else:
            medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
            for i, s in enumerate(sects):
                leader = await self.bot.db.get_player(s["leader_id"])
                ln = leader["name"] if leader else "???"
                embed.add_field(
                    name=f"{medals[i]} {s['name']}",
                    value=(
                        f"👑 Môn Chủ: **{ln}**\n"
                        f"⭐ Cấp: **{s['level']}**  "
                        f"👥 TV: **{s['member_count']}**"
                    ),
                    inline=False
                )
        embed.set_footer(text=",tl tongmon tao [tên] để lập tông môn  •  Tu Tiên Bot v3")
        await ctx.send(embed=embed)

    # ══ 4. ,tl hanh_trinh ════════════════════════════════
    @commands.command(name="hanh_trinh", aliases=["hanhtrinh","ht","journey"])
    async def hanh_trinh(self, ctx):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        """Xem hành trình tu tiên tổng quan"""
        ri    = player["realm_index"]
        rt    = player["realm_tier"]
        total = sum(r["tiers"] for r in REALMS)
        done  = sum(r["tiers"] for r in REALMS[:ri]) + rt

        embed = discord.Embed(
            title="🌌 HÀNH TRÌNH TU TIÊN",
            color=realm_color(ri)
        )
        embed.set_author(name=player["name"], icon_url=ctx.author.display_avatar.url)

        # Tiến độ tổng
        embed.add_field(
            name="📊 Tiến Độ Tổng",
            value=f"{bar(done, total, 20)}\n`{done}/{total}` tầng đã vượt",
            inline=False
        )

        # Cảnh giới hiện tại
        embed.add_field(
            name="🌌 Hiện Tại",
            value=f"`{get_realm_name(player)}`",
            inline=True
        )

        # Cảnh giới tiếp theo
        if ri < len(REALMS) - 1:
            next_r = REALMS[ri]
            if rt < next_r["tiers"]:
                next_name = f"{next_r['name']} - Tầng {rt+1}"
            else:
                next_r2 = REALMS[ri+1]
                next_name = f"{next_r2['name']} - Tầng 1"
            embed.add_field(name="🎯 Mục Tiêu", value=f"`{next_name}`", inline=True)

        # Mốc quan trọng đã qua
        milestones = []
        realm_names = [r["name"] for r in REALMS[:ri]]
        for rn in realm_names[-3:]:
            milestones.append(f"✅ {rn}")
        if milestones:
            embed.add_field(name="🏆 Đã Vượt Qua", value="\n".join(milestones), inline=True)

        # Stats tổng
        ct  = int(player.get("total_cultivate_time") or 0)
        exp = int(player.get("total_explore") or 0)
        embed.add_field(
            name="📈 Thống Kê",
            value=(
                f"⏱️ Tổng tu luyện: `{fmt_time(ct)}`\n"
                f"🗺️ Tổng thám hiểm: `{exp:,} lần`\n"
                f"⚔️ Lực chiến: `{_s(player.get('luc_chien', player['atk']))}`"
            ),
            inline=False
        )
        embed.set_footer(text="Tu Tiên Bot v3  •  Mỗi bước là một truyền thuyết")
        await ctx.send(embed=embed)

    # ══ 5. ,tl thi_dau ═══════════════════════════════════
    @commands.command(name="thi_dau", aliases=["thidau","tournament"])
    async def thi_dau(self, ctx):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        """Thi đấu với NPC ngẫu nhiên theo cảnh giới - nhận thưởng"""
        COST = 10
        if player["stamina"] < COST:
            await ctx.send(embed=warn(f"Cần **{COST} TL**!"))
            return

        ri = player["realm_index"]
        # Tạo NPC cùng cảnh giới
        npc_names = ["Vương Thiên","Lý Phong","Trương Vũ","Hồ Huyền","Bạch Long",
                     "Hắc Phong","Kim Điêu","Ngọc Linh","Thanh Vân","Tử Hà"]
        npc_name  = random.choice(npc_names)
        npc_power = player.get("luc_chien", player["atk"]) * random.uniform(0.7, 1.3)
        my_power  = player.get("luc_chien", player["atk"])

        # Tính tỉ lệ thắng
        luck_bonus = player.get("luck", 0) * 0.0005
        win_rate   = min(0.85, max(0.15, my_power / (my_power + npc_power) + luck_bonus))
        won        = random.random() < win_rate

        await self.bot.db.update_player(ctx.author.id, stamina=player["stamina"] - COST)

        embed = discord.Embed(
            title=f"⚔️ THI ĐẤU: {player['name']} vs {npc_name}",
            color=0xFFD700 if won else 0xF44336
        )
        embed.add_field(name="⚔️ Lực Chiến Bạn", value=f"`{_s(my_power)}`",  inline=True)
        embed.add_field(name="⚔️ Lực Chiến NPC",  value=f"`{_s(npc_power)}`", inline=True)
        embed.add_field(name="📊 Tỉ Lệ Thắng",    value=f"`{win_rate*100:.0f}%`", inline=True)

        if won:
            reward_ha    = int(500 * (ri + 1) * random.uniform(1, 2))
            reward_exp   = int(1000 * (ri + 1) * random.uniform(1, 1.5))
            new_exp      = min(player["exp"] + reward_exp, get_exp_req(player))
            new_pk       = int(player.get("total_pk_win") or 0) + 1
            await self.bot.db.update_player(ctx.author.id,
                linh_thach_ha=player["linh_thach_ha"] + reward_ha,
                exp=new_exp,
                total_pk_win=new_pk,
            )
            embed.add_field(
                name="🏆 CHIẾN THẮNG!",
                value=f"💰 +{reward_ha:,} Hạ  •  ✨ +{fmt(reward_exp)} EXP",
                inline=False
            )
        else:
            embed.add_field(name="💔 THẤT BẠI!", value="Cần luyện tập thêm!", inline=False)

        embed.set_footer(text=f"Lực Vận Khí: +{player.get('luck',0)*0.05:.1f}% thắng  •  Tu Tiên Bot v3")
        await ctx.send(embed=embed)

    # ══ 6. ,tl boi_bai ═══════════════════════════════════
    @commands.command(name="boi_bai", aliases=["boibai","xemboi","fortune"])
    async def boi_bai(self, ctx):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        """Bói bài tiên tri - xem vận may hôm nay"""
        FORTUNES = [
            ("🌟 Đại Cát",    0x4CAF50, "Hôm nay vận khí cực mạnh! EXP +20%, tỉ lệ drop tăng.", True),
            ("✨ Tiểu Cát",   0x8BC34A, "Ngày tốt để tu luyện và thám hiểm.", True),
            ("⚖️ Bình Thường", 0x9E9E9E, "Ngày bình thường, cẩn thận trong chiến đấu.", False),
            ("🌧️ Tiểu Hung",  0xFF9800, "Không may mắn, tránh đánh boss hôm nay.", False),
            ("⚡ Đại Hung",   0xF44336, "Ngày xấu! Cẩn thận mọi thứ!", False),
        ]
        WEIGHTS = [0.15, 0.35, 0.30, 0.15, 0.05]

        # Seed theo ngày + user để cùng ngày ra cùng kết quả
        import datetime
        today = datetime.date.today().toordinal()
        seed  = (today + int(ctx.author.id)) % 1000
        random.seed(seed)
        idx   = random.choices(range(5), weights=WEIGHTS)[0]
        random.seed()  # Reset seed

        title, color, desc, is_good = FORTUNES[idx]

        ADVICES = {
            True:  ["📿 Đeo Tinh Hồn Lệnh để tăng may mắn",
                    "🧘 Thiền định trước khi bế quan",
                    "🗺️ Thám hiểm bí cảnh cao nhất có thể"],
            False: ["🛡️ Không nên PK hôm nay",
                    "💊 Trữ đan dược phòng thân",
                    "⚗️ Tập trung luyện đan hôm nay"],
        }

        embed = discord.Embed(
            title=f"🔮 BÓI BÀI TIÊN TRI — {title}",
            description=desc,
            color=color
        )
        embed.add_field(
            name="💡 Lời Khuyên",
            value="\n".join(f"• {a}" for a in random.sample(ADVICES[is_good], 2)),
            inline=False
        )
        embed.add_field(
            name="🍀 Vận Số Hôm Nay",
            value=f"Phúc Duyên của bạn: **{player.get('phuc_duyen',50)}** điểm",
            inline=True
        )

        import datetime
        embed.set_footer(text=f"Bói bài ngày {datetime.date.today()}  •  Tu Tiên Bot v3")
        await ctx.send(embed=embed)

    # ══ 7. ,tl linh_khi ══════════════════════════════════
    @commands.command(name="linh_khi", aliases=["linhkhi","lk","absorb"])
    async def linh_khi(self, ctx):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        """Hấp thụ linh khí môi trường - nhận ít EXP + TL miễn phí (cooldown 1h)"""
        CD_KEY = f"linhkhi_{ctx.author.id}"
        # Dùng status_data để lưu cooldown
        import json as _json
        status_data = {}
        try:
            status_data = _json.loads(player.get("status_data") or "{}")
        except Exception:
            pass

        last_lk = status_data.get("last_linh_khi", 0)
        if now() - last_lk < 3600:
            rem = 3600 - (now() - last_lk)
            await ctx.send(embed=warn(f"Linh Khí chưa tụ lại!\nCoodown: **{fmt_time(rem)}**"))
            return

        ngo     = player.get("ngo_tinh", 50)
        exp_get = random.randint(50, 200) * (1 + ngo / 100)
        tl_get  = random.randint(5, 20)
        new_exp = min(player["exp"] + int(exp_get), get_exp_req(player))
        new_stam= min(player["stamina"] + tl_get, player["stamina_max"])

        status_data["last_linh_khi"] = now()
        await self.bot.db.update_player(ctx.author.id,
            exp=new_exp,
            stamina=new_stam,
            status_data=_json.dumps(status_data),
        )

        embed = discord.Embed(
            title="🌬️ HẤP THỤ LINH KHÍ",
            description=(
                f"**{player['name']}** hít thở linh khí từ trời đất...\n\n"
                f"✨ +**{int(exp_get):,}** Tu Vi\n"
                f"🔋 +**{tl_get}** Thể Lực\n"
                f"_(Ngộ Tính cao → thu linh khí tốt hơn)_"
            ),
            color=0x4CAF50
        )
        embed.set_footer(text="Cooldown 1 giờ  •  Ngộ Tính ảnh hưởng lượng linh khí hấp thụ")
        await ctx.send(embed=embed)

    # ══ 8. ,tl mua_sat ═══════════════════════════════════
    @commands.command(name="mua_sat", aliases=["muasat","bloodrain","ms"])
    async def mua_sat(self, ctx):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        """Sự kiện Mưa Sát ngẫu nhiên - đánh nhau với quái vật"""
        COST = 30
        if player["stamina"] < COST:
            await ctx.send(embed=warn(f"Cần **{COST} TL** để tham chiến!"))
            return

        ri = player["realm_index"]
        MONSTERS = [
            ("🐗 Linh Trư",    1.0), ("🐍 Độc Xà",   1.2),
            ("🦁 Sư Tử Phong", 1.5), ("🐲 Tiểu Long", 2.0),
            ("👿 Quỷ Tướng",   2.5), ("💀 Tử Thần",   3.0),
        ]
        tier    = min(ri // 3, len(MONSTERS) - 1)
        monster = MONSTERS[min(tier + random.randint(0,1), len(MONSTERS)-1)]
        m_power = player.get("luc_chien", player["atk"]) * monster[1] * random.uniform(0.8, 1.2)
        my_pow  = player.get("luc_chien", player["atk"])
        win_r   = min(0.85, max(0.1, my_pow / (my_pow + m_power)))
        won     = random.random() < win_r

        await self.bot.db.update_player(ctx.author.id, stamina=player["stamina"] - COST)

        embed = discord.Embed(
            title=f"🌧️ MƯA SÁT — {monster[0]}",
            color=0xFF5722
        )
        embed.add_field(name="👹 Quái Vật",      value=f"`{monster[0]}`",        inline=True)
        embed.add_field(name="⚡ Sức Mạnh Quái", value=f"`{_s(m_power)}`",       inline=True)
        embed.add_field(name="📊 Tỉ Lệ",         value=f"`{win_r*100:.0f}%`",   inline=True)

        if won:
            base_r  = 2000 * (ri + 1)
            reward  = random.randint(base_r, base_r * 3)
            bonus   = random.random() < 0.2  # 20% drop item
            await self.bot.db.update_player(ctx.author.id,
                linh_thach_ha=player["linh_thach_ha"] + reward)
            desc = f"💀 Đã tiêu diệt {monster[0]}!\n💰 +**{reward:,}** Hạ LT"
            if bonus:
                item_id = random.choice(["101","201","301"])
                await self.bot.db.add_item(ctx.author.id, item_id, 1)
                iname = ITEMS.get(item_id, {}).get("name", item_id)
                desc += f"\n🎁 +**1x {iname}** (may mắn!)"
            embed.add_field(name="🏆 CHIẾN THẮNG!", value=desc, inline=False)
            embed.color = 0xFFD700
        else:
            lost = random.randint(5, 20)
            new_stam = max(0, player["stamina"] - COST - lost)
            await self.bot.db.update_player(ctx.author.id, stamina=new_stam)
            embed.add_field(
                name="💔 THẤT BẠI!",
                value=f"Bị {monster[0]} đánh lui!\n🔋 Mất thêm **{lost} TL**",
                inline=False
            )
        embed.set_footer(text=f"TL: {max(0, player['stamina'] - COST)}  •  Tu Tiên Bot v3")
        await ctx.send(embed=embed)

    # ══ 9. ,tl phong_than ════════════════════════════════
    @commands.command(name="phong_than", aliases=["phongthan","pt","deify"])
    async def phong_than(self, ctx, target: discord.Member = None):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        """Tôn vinh người chơi khác - tặng danh hiệu"""
        if not target:
            await ctx.send(embed=warn("Dùng: `,tl phong_than @người`"))
            return
        if target.id == ctx.author.id:
            await ctx.send(embed=warn("Không thể phong thần cho chính mình!"))
            return

        other = await self.bot.db.get_player(target.id)
        if not other:
            await ctx.send(embed=error(f"**{target.display_name}** chưa nhập môn!"))
            return

        # Cooldown per pair per day
        TITLES = [
            "Vô Song Thiên Hạ", "Nghịch Thiên Cải Mệnh", "Thiên Tài Tu Tiên",
            "Cái Thế Thiên Kiêu", "Bất Thế Kỳ Tài", "Vạn Cổ Độc Tôn",
            "Thần Bí Cường Giả", "Truyền Thuyết Sống", "Đệ Nhất Tiên Nhân",
        ]
        title = random.choice(TITLES)

        embed = discord.Embed(
            title="👑 PHONG THẦN NGHI LỄ",
            description=(
                f"**{player['name']}** long trọng tôn vinh:\n\n"
                f"# {realm_icon(other['realm_index'])} {other['name']}\n"
                f"## 「{title}」\n\n"
                f"🌌 {get_realm_name(other)}\n"
                f"⚔️ Lực Chiến: **{_s(other.get('luc_chien', other['atk']))}**"
            ),
            color=0xFFD700
        )
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.set_footer(text="Thiên Đạo chứng giám!  •  Tu Tiên Bot v3")
        await ctx.send(embed=embed)

    # ══ 10. ,tl help_me ══════════════════════════════════
    @commands.command(name="help_me", aliases=["helpme","cuuu","sos"])
    async def help_me(self, ctx):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        """Kêu cứu - nhận gợi ý cá nhân hóa dựa trên tình trạng hiện tại"""
        ri      = player["realm_index"]
        exp_cur = player["exp"]
        exp_req = get_exp_req(player)
        stam    = player["stamina"]
        ha      = player["linh_thach_ha"]
        status  = player["status"]

        tips = []
        urgent = []

        # Phân tích tình trạng
        if exp_cur >= exp_req:
            urgent.append("🚀 **Tu Vi đầy!** Gõ `,tl dp` để đột phá ngay!")
        elif exp_cur / exp_req < 0.3:
            tips.append("📉 Tu Vi còn ít → Gõ `,tl start` bế quan")

        if stam < 20:
            urgent.append("🔋 **Thể Lực thấp!** Dùng `,tl use phuc_tinh_dan` để hồi")
        elif stam >= 80:
            tips.append("⚡ TL dồi dào → Đi `,tl bicanh di` hoặc `,tl boss fight`")

        if status != "idle":
            STATUS_HINT = {
                "beQuan":   "🧘 Đang bế quan → `,tl stop` để nhận EXP",
                "thamHiem": "⚔️ Đang thám hiểm → `,tl bicanh ve` để nhận thưởng",
            }
            urgent.append(STATUS_HINT.get(status, f"Đang {status}"))

        if ha < 1000:
            tips.append("💰 LT thấp → Gõ `,tl daily` điểm danh, chơi `,tl dt`")

        # Gợi ý theo level
        if ri < 3:
            tips.append("🌱 Tân thủ → `,tl nv` xem nhiệm vụ hàng ngày")
        elif ri < 8:
            tips.append("⚔️ Trung cấp → Cường hóa trang bị `,tl cuonghoa weapon`")
        else:
            tips.append("👑 Cao cấp → Leo `,tl thap auto` kiếm Ma Tôn Lệnh")

        if not tips and not urgent:
            tips.append("✅ Mọi thứ đều ổn! Tiếp tục tu luyện nhé~")

        embed = discord.Embed(
            title="💡 GỢI Ý CÁ NHÂN",
            color=realm_color(ri)
        )
        embed.set_author(name=player["name"], icon_url=ctx.author.display_avatar.url)

        if urgent:
            embed.add_field(name="🚨 Cần Làm Ngay!", value="\n".join(urgent), inline=False)
        if tips:
            embed.add_field(name="💡 Gợi Ý", value="\n".join(tips), inline=False)

        embed.add_field(
            name="📊 Tình Trạng",
            value=(
                f"EXP: `{exp_cur/exp_req*100:.1f}%`  "
                f"TL: `{stam}/{player['stamina_max']}`  "
                f"LT: `{ha:,} Hạ`"
            ),
            inline=False
        )
        embed.set_footer(text="Tu Tiên Bot v3  •  Gõ ,tl help để xem hướng dẫn đầy đủ")
        await ctx.send(embed=embed)

# ══ DAOLY — AnimeChan quote hàng ngày ════════════════════════════════
    # Map tên nhân vật anime → tên xianxia
    _XIANXIA_NAMES = {
        "default": ["Lão Tổ Vô Danh", "Thái Thượng Lão Quân", "Thiên Đế",
                    "Cổ Hoàng", "Vạn Kiếp Tôn Giả", "Hỗn Độn Chí Tôn",
                    "Vô Cực Đại Đế", "Bất Diệt Thần Vương"],
        # anime nổi tiếng → nhân vật xianxia tương ứng
        "Naruto Uzumaki": "Thiên Đạo Lục Đạo Tiên Nhân",
        "Itachi Uchiha":  "Huyết Luân Nhãn Chí Tôn",
        "Madara Uchiha":  "Vạn Hoa Đồng Đại Ma Tôn",
        "Goku":           "Chiến Thần Vô Cực",
        "Vegeta":         "Kiêu Ngạo Vương Giả",
        "Zoro":           "Tam Kiếm Lưu Đại Nhân",
        "Luffy":          "Vô Hình Hải Vương",
        "Levi Ackerman":  "Nhân Loại Tối Cường",
        "Eren Yeager":    "Tự Do Đạo Thần",
        "Light Yagami":   "Tử Thần Lệnh Chủ",
        "L":              "Vô Danh Thiên Tài",
        "Edward Elric":   "Kim Thuật Đại Sư",
        "Spike Spiegel":  "Tiêu Dao Giang Hồ Khách",
    }

    _DAOLY_COOLDOWN = {}  # user_id -> last_used timestamp

    @commands.command(name="daoly", aliases=["dl", "daongon", "laotonoi"])
    async def daoly(self, ctx):
        """Nghe Lão Tổ truyền đạo lý hàng ngày (AnimeChan API)"""
        uid = str(ctx.author.id)
        # Cooldown 60s để tránh spam
        last = self._DAOLY_COOLDOWN.get(uid, 0)
        if now() - last < 60:
            rem = int(60 - (now() - last))
            await ctx.send(embed=warn(f"Lão Tổ đang hồi công lực! Chờ **{rem}s** nữa."))
            return

        import aiohttp
        quote_text = None
        char_name  = None

        # Thử AnimeChan v2
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(
                    "https://animechan.io/api/v1/quotes/random",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as r:
                    if r.status == 200:
                        data = await r.json()
                        # API trả về {"status":"success","data":{"content":"...","anime":{"name":"..."},"character":{"name":"..."}}}
                        d = data.get("data", {})
                        quote_text = d.get("content", "")
                        char_name  = d.get("character", {}).get("name", "")
        except Exception:
            pass

        # Fallback quotes xianxia nếu API lỗi
        FALLBACK = [
            ("Thiên Đạo vô tình, nhưng người tu tiên phải hữu tình.", "Thái Thượng Lão Quân"),
            ("Cảnh giới không đo bằng tu vi, mà đo bằng tâm cảnh.", "Vô Cực Đại Đế"),
            ("Một kiếm phá vạn pháp — tâm vô tạp niệm mới là đạo.", "Thiên Đế"),
            ("Ngàn năm tu luyện chẳng bằng một giây ngộ đạo.", "Hỗn Độn Chí Tôn"),
            ("Kẻ mạnh không sợ thiên kiếp, kẻ yếu sợ chính mình.", "Cổ Hoàng"),
            ("Linh khí vô hạn, nhưng thời gian của người tu tiên hữu hạn.", "Vạn Kiếp Tôn Giả"),
            ("Đạo tâm kiên định, vạn ma bất xâm.", "Bất Diệt Thần Vương"),
            ("Thất bại chỉ là bước đệm trên con đường vạn kiếp tu tiên.", "Lão Tổ Vô Danh"),
        ]

        if not quote_text:
            quote_text, char_name = random.choice(FALLBACK)
            from_api = False
        else:
            from_api = True

        # Chuyển tên nhân vật → tên xianxia
        xianxia_name = self._XIANXIA_NAMES.get(
            char_name,
            random.choice(self._XIANXIA_NAMES["default"])
        )

        # Lấy player để hiển thị realm
        player = await self.bot.db.get_player(ctx.author.id)
        ri = int(player.get("realm_index", 0)) if player else 0

        self._DAOLY_COOLDOWN[uid] = now()

        embed = discord.Embed(
            title="📜 ĐẠO LÝ TRUYỀN THỪA",
            description=f"*\"{quote_text}\"*",
            color=0xFFD700
        )
        embed.add_field(
            name="— Lão Tổ truyền dạy",
            value=f"**{xianxia_name}**" + (f"\n_({char_name})_" if from_api and char_name != xianxia_name else ""),
            inline=False
        )
        if player:
            embed.set_author(
                name=f"{player['name']} lắng nghe đạo lý",
                icon_url=ctx.author.display_avatar.url
            )
        embed.set_footer(text=("📡 AnimeChan API" if from_api else "📜 Kho Đạo Lý Cổ Đại") + "  •  ,tl daoly")
        await ctx.send(embed=embed)


    @commands.command(name="id", aliases=["myid","userid","uid"])
    async def get_id(self, ctx, target: discord.Member = None):
        """Xem Discord User ID của bản thân hoặc người khác."""
        user = target or ctx.author
        embed = discord.Embed(
            title="🪪 DISCORD USER ID",
            color=0x5865F2
        )
        embed.add_field(name="👤 Người dùng", value=f"**{user.display_name}**", inline=True)
        embed.add_field(name="🔢 User ID",    value=f"`{user.id}`",            inline=True)
        embed.set_footer(text="Dùng ID này để xem profile trên web dashboard")
        await ctx.send(embed=embed)


# Helper cục bộ
def _s(n) -> str:
    return fmt(n)

async def setup(bot):
    await bot.add_cog(ExtraCommands(bot))

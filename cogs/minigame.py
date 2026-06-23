"""cogs/minigame.py - Mini game đầy đủ v4"""
import discord
from discord.ext import commands
import random, asyncio, aiohttp, html, time

from utils.helpers import require_player, now
from utils.embeds import *
from utils.game_data import ITEMS, DAILY_QUESTS, REALMS

def _s(n):
    return fmt(n)

def _safe(p,k,d=0):
    v=p.get(k); return v if v is not None else d

class Minigame(commands.Cog):
    def __init__(self, bot): self.bot = bot
    
    async def _add_quest(self, uid, qtype, amount):
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

    # ══ ĐỔ THẠCH ════════════════════════════════════════════
    # ══ PHÒNG ĐỔ THẠCH TU TIÊN ════════════════════════════════
    @commands.command(name="dt", aliases=["dothach","phongdt","pdt"])
    async def dt(self, ctx, loai: str = None, so_luong: int = 1):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        """🎲 Phòng Đổ Thạch Tu Tiên"""
        # Nếu không có args, hiện menu
        if loai is None:
            embed = discord.Embed(
                title="🎲 PHÒNG ĐỔ THẠCH TU TIÊN 🎲",
                description=(
                    "Nơi thử vận may, một bước thành tiên hoặc trắng tay!\n\n"
                    "1️⃣ **Linh Thạch Thô:** 2,000,000 LT\n"
                    "2️⃣ **Thiên Thạch Thô:** 20,000,000 LT\n"
                    "3️⃣ **Thần Thạch Thô:** 100,000,000 LT\n\n"
                    "📝 **Cú pháp:** `,tl dt <linh|thien|than> [số lượng]`\n"
                    "Ví dụ: `,tl dt linh 5`\n\n"
                    "🎰 **Jackpot (x5 LT):**\n"
                    "• Linh: 1% → **100,000,000 LT**\n"
                    "• Thiên: 3% → **500,000,000 LT**\n"
                    "• Thần: 5% → **1,000,000,000 LT**\n"
                    "⚠️ Tối đa **10 viên/lượt**"
                ),
                color=0xFFD700
            )
            embed.set_footer(text="Tu Tiên Bot v4  •  ,tl dt linh 1 để bắt đầu")
            await ctx.send(embed=embed)
            return

        loai = loai.lower()
        LOAI_CONFIG = {
            "linh":  {"name": "Linh Thạch Thô",  "icon": "1️⃣", "gia": 2_000_000,
                      "jackpot_lt": 100_000_000, "jackpot_ty": 0.01,
                      "bang": [
                          ("💨 Mất trắng",           0.40, {}),
                          ("💰 Hoàn 50% LT",          0.20, {"ha_mult": 0.5}),
                          ("💰 Hoàn vốn",             0.14, {"ha_mult": 1.0}),
                          ("💰 x1.5 LT",             0.10, {"ha_mult": 1.5}),
                          ("💎 x2 LT",               0.07, {"ha_mult": 2.0}),
                          ("🌟 x3 LT",               0.05, {"ha_mult": 3.0}),
                          ("🔮 Rương Vàng",           0.03, {"item": "102"}),
                      ]},
            "thien": {"name": "Thiên Thạch Thô", "icon": "2️⃣", "gia": 20_000_000,
                      "jackpot_lt": 500_000_000, "jackpot_ty": 0.03,
                      "bang": [
                          ("💨 Mất trắng",           0.35, {}),
                          ("💰 Hoàn 50% LT",          0.18, {"ha_mult": 0.5}),
                          ("💰 Hoàn vốn",             0.14, {"ha_mult": 1.0}),
                          ("💰 x1.5 LT",             0.12, {"ha_mult": 1.5}),
                          ("💎 x2 LT",               0.08, {"ha_mult": 2.0}),
                          ("🌟 x3 LT",               0.06, {"ha_mult": 3.0}),
                          ("🔮 Rương Kim Cương",       0.04, {"item": "103"}),
                          ("👑 x5 LT",               0.02, {"ha_mult": 5.0}),
                      ]},
            "than":  {"name": "Thần Thạch Thô",  "icon": "3️⃣", "gia": 100_000_000,
                      "jackpot_lt": 1_000_000_000, "jackpot_ty": 0.05,
                      "bang": [
                          ("💨 Mất trắng",           0.30, {}),
                          ("💰 Hoàn 50% LT",          0.16, {"ha_mult": 0.5}),
                          ("💰 Hoàn vốn",             0.13, {"ha_mult": 1.0}),
                          ("💰 x1.5 LT",             0.12, {"ha_mult": 1.5}),
                          ("💎 x2 LT",               0.10, {"ha_mult": 2.0}),
                          ("🌟 x3 LT",               0.08, {"ha_mult": 3.0}),
                          ("🔮 Rương Thần",           0.05, {"item": "104"}),
                          ("💊 Đột Phá Đan ×3",       0.04, {"item": "203", "qty": 3}),
                          ("👑 x5 LT",               0.03, {"ha_mult": 5.0}),
                      ]},
        }

        if loai not in LOAI_CONFIG:
            await ctx.send(embed=warn(
                "Loại không hợp lệ! Dùng: `linh` | `thien` | `than`\n"
                "Ví dụ: `,tl dt linh 5`"
            )); return

        so_luong = max(1, min(10, so_luong))
        cfg = LOAI_CONFIG[loai]
        tong_gia = cfg["gia"] * so_luong
        lt_hien = int(_safe(player, "linh_thach_ha", 0))

        if lt_hien < tong_gia:
            await ctx.send(embed=error(
                f"Không đủ LT!\n"
                f"Cần: **{tong_gia:,} Hạ** | Có: **{lt_hien:,} Hạ**"
            )); return

        # Tính kết quả từng viên
        tong_ha_nhan = 0
        items_nhan = {}
        jackpot_count = 0
        ket_qua_list = []

        for i in range(so_luong):
            # Check jackpot trước
            if random.random() < cfg["jackpot_ty"]:
                jackpot_count += 1
                tong_ha_nhan += cfg["jackpot_lt"]
                ket_qua_list.append(f"✨ **JACKPOT x5!** +{cfg['jackpot_lt']//1_000_000}M LT")
                continue

            # Quay bảng thường
            bang = cfg["bang"]
            total_w = sum(b[1] for b in bang)
            roll = random.uniform(0, total_w)
            cum = 0
            chosen = bang[0]
            for entry in bang:
                cum += entry[1]
                if roll <= cum:
                    chosen = entry; break

            label, _, reward = chosen
            if reward.get("ha_mult"):
                nhan = int(cfg["gia"] * reward["ha_mult"])
                tong_ha_nhan += nhan
                ket_qua_list.append(f"{label} +{nhan:,} Hạ")
            elif reward.get("item"):
                it = reward["item"]; qty = reward.get("qty", 1)
                items_nhan[it] = items_nhan.get(it, 0) + qty
                ket_qua_list.append(f"{label}")
            else:
                ket_qua_list.append(f"{label}")

        # Tính delta LT (đã trừ vốn)
        delta_ha = tong_ha_nhan - tong_gia
        new_ha = max(0, lt_hien + delta_ha)
        await self.bot.db.update_player(ctx.author.id, linh_thach_ha=new_ha)

        # Thêm vật phẩm
        for item_id, qty in items_nhan.items():
            try:
                await self.bot.db.add_item(ctx.author.id, item_id, qty)
            except Exception:
                pass

        await self._add_quest(ctx.author.id, "dt_play", so_luong)

        # Hiển thị kết quả
        color = 0xFFD700 if jackpot_count > 0 else (0x4CAF50 if delta_ha >= 0 else 0xF44336)
        embed = discord.Embed(
            title=f"🎲 ĐỔ THẠCH — {cfg['icon']} {cfg['name']}",
            color=color
        )

        if so_luong == 1:
            embed.description = ket_qua_list[0] if ket_qua_list else "Mất trắng"
        else:
            # Rút gọn nếu nhiều
            show = ket_qua_list[:10]
            embed.description = "\n".join(f"`{i+1}.` {r}" for i, r in enumerate(show))

        if jackpot_count > 0:
            embed.add_field(
                name="🎉 JACKPOT!",
                value=f"x**{jackpot_count}** lần! Nhận **{jackpot_count*cfg['jackpot_lt']//1_000_000}M LT**!",
                inline=False
            )

        if items_nhan:
            item_txt = ", ".join(f"**{k}** ×{v}" for k,v in items_nhan.items())
            embed.add_field(name="🎁 Vật Phẩm", value=item_txt, inline=False)

        sign = "+" if delta_ha >= 0 else ""
        embed.add_field(name="💸 Chi phí",   value=f"-{tong_gia:,} Hạ",              inline=True)
        embed.add_field(name="💰 Nhận về",   value=f"+{tong_ha_nhan:,} Hạ",           inline=True)
        embed.add_field(name="📊 Lãi/Lỗ",    value=f"{sign}{delta_ha:,} Hạ",          inline=True)
        embed.add_field(name="👛 Số Dư",      value=f"{new_ha:,} Hạ",                  inline=False)
        embed.set_footer(text=f"Đã mở {so_luong} viên  •  Max 10/lượt  •  Tu Tiên Bot v4")
        await ctx.send(embed=embed)

    # ══ VÒNG QUAY ════════════════════════════════════════════
    @commands.command(name="quay", aliases=["spin","vongquay","vq"])
    async def quay(self, ctx):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        COST = 5000
        if _safe(player,"linh_thach_ha") < COST:
            await ctx.send(embed=warn(f"Cần **{COST:,} Hạ LT** để quay!")); return

        PRIZES = [
            ("💰 5,000 Hạ LT",      0.25, {"ha":5000}),
            ("💰 10,000 Hạ LT",     0.18, {"ha":10000}),
            ("💰 25,000 Hạ LT",     0.10, {"ha":25000}),
            ("💎 1 Trung Phẩm LT",  0.12, {"trung":1}),
            ("💎 5 Trung Phẩm LT",  0.07, {"trung":5}),
            ("👑 1 Cực Phẩm LT",    0.03, {"cuc":1}),
            ("🎁 Rương Vàng",        0.10, {"item":"102"}),
            ("🎁 Rương Kim Cương",   0.05, {"item":"103"}),
            ("💊 Đột Phá Đan ×2",    0.06, {"item":"203","qty":2}),
            ("🌟 Rương Thần",        0.02, {"item":"104"}),
            ("💸 Trượt (mất tiền)",  0.02, {"ha":-5000}),
        ]

        total_w = sum(p[1] for p in PRIZES)
        roll    = random.uniform(0, total_w)
        acc     = 0; prize = PRIZES[0]
        for p in PRIZES:
            acc += p[1]
            if roll <= acc: prize = p; break

        await self.bot.db.update_player(ctx.author.id,
            linh_thach_ha=_safe(player,"linh_thach_ha")-COST)

        r = prize[2]
        if "item" in r:
            qty = r.get("qty",1)
            await self.bot.db.add_item(ctx.author.id, r["item"], qty)
        else:
            updates = {}
            if r.get("ha"):    updates["linh_thach_ha"]   = max(0,_safe(player,"linh_thach_ha")-COST+r["ha"])
            if r.get("trung"): updates["linh_thach_trung"] = _safe(player,"linh_thach_trung")+r["trung"]
            if r.get("cuc"):   updates["linh_thach_cuc"]   = _safe(player,"linh_thach_cuc")+r["cuc"]
            if updates: await self.bot.db.update_player(ctx.author.id, **updates)

        # Animation
        SPIN_FRAMES = ["🎰 | 🍒 🍋 🍊", "🎰 | 💎 🌟 🎁", "🎰 | 🔥 💰 ✨"]
        msg = await ctx.send(f"{random.choice(SPIN_FRAMES)}\n*Đang quay...*")
        await asyncio.sleep(1.2)

        color = 0xFFD700 if not r.get("ha",-1) == -5000 else 0xF44336
        embed = discord.Embed(
            title="🎡 VÒNG QUAY VẬN MỆNH",
            description=f"✨ Kết quả:\n## {prize[0]}",
            color=color
        )
        embed.add_field(name="💸 Chi Phí", value=f"{COST:,} Hạ", inline=True)
        embed.set_footer(text="Xác suất: Càng hiếm càng nhỏ!  •  Tu Tiên Bot v3")
        await msg.edit(content=None, embed=embed)

    # ══ XÌ DÁCH ═════════════════════════════════════════════
    @commands.command(name="bai", aliases=["blackjack","xidach","xd"])
    async def bai(self, ctx, bet: int = 1000):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        MIN_BET = 500
        if bet < MIN_BET:
            await ctx.send(embed=warn(f"Cược tối thiểu **{MIN_BET:,} Hạ**!")); return
        if bet > _safe(player,"linh_thach_ha"):
            await ctx.send(embed=error("Không đủ LT!")); return

        def draw(): return random.choice([2,3,4,5,6,7,8,9,10,10,10,10,11])
        def hand_val(h):
            v=sum(h); aces=h.count(11)
            while v>21 and aces: v-=10; aces-=1
            return v

        ph=[draw(),draw()]; dh=[draw(),draw()]
        pv=hand_val(ph); dv=hand_val(dh)
        while dv<17: dh.append(draw()); dv=hand_val(dh)

        ph_str=" + ".join(str(c) for c in ph)
        dh_str=" + ".join(str(c) for c in dh)

        blackjack = len(ph)==2 and pv==21
        if pv>21:    result,delta,color="💸 Xì!",              -bet,0xF44336
        elif blackjack: result,delta,color="🎉 BLACKJACK! (×2.5)",int(bet*1.5),0xFFD700
        elif dv>21 or pv>dv: result,delta,color="🏆 Thắng! (×2)", bet,0x4CAF50
        elif pv==dv: result,delta,color="🤝 Hòa",              0,0x9E9E9E
        else:        result,delta,color="💸 Thua",             -bet,0xF44336

        new_ha=max(0,_safe(player,"linh_thach_ha")+delta)
        await self.bot.db.update_player(ctx.author.id, linh_thach_ha=new_ha)

        embed=discord.Embed(title="🃏 XÌ DÁCH TIÊN GIỚI",color=color)
        embed.add_field(name=f"👤 Bạn ({pv})",    value=ph_str, inline=True)
        embed.add_field(name=f"🤖 Dealer ({dv})", value=dh_str, inline=True)
        embed.add_field(name="🏆 Kết Quả",        value=result, inline=False)
        embed.add_field(name="💰 Thay Đổi",
            value=f"{'+'if delta>=0 else ''}{delta:,} Hạ", inline=True)
        embed.add_field(name="👛 Số Dư",value=f"{new_ha:,} Hạ",inline=True)
        await ctx.send(embed=embed)

    # ══ ĐUA LINH THÚ ════════════════════════════════════════
    @commands.command(name="dua", aliases=["race","cuarua","linhthu_race"])
    async def dua(self, ctx, bet: int = 1000):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        MIN_BET=200
        if bet<MIN_BET:
            await ctx.send(embed=warn(f"Cược tối thiểu **{MIN_BET:,} Hạ**!")); return
        if bet>_safe(player,"linh_thach_ha"):
            await ctx.send(embed=error("Không đủ LT!")); return

        animals=[
            ("🐉 Thanh Long",   0.12),("🦅 Thần Ưng",   0.18),
            ("🐯 Bạch Hổ",     0.22),("🦊 Hỏa Hồ Ly",  0.20),
            ("🐢 Huyền Vũ",    0.15),("🔥 Hỏa Kỳ Lân",  0.13),
        ]
        
        # Người dùng đặt cược vào con nào? Random nếu không chỉ định
        luck = _safe(player,"luck",0)
        # Phúc Duyên ảnh hưởng nhẹ
        your_idx = random.randint(0, len(animals)-1)
        
        # Chọn winner theo weights
        winner_idx = random.choices(
            range(len(animals)),
            weights=[a[1] for a in animals]
        )[0]

        msg = await ctx.send("🏁 **Đua Linh Thú đang diễn ra...**\n*Đang tải...*")
        await asyncio.sleep(1.5)

        lines=[]
        for i,(name,_) in enumerate(animals):
            pos = 10 if i==winner_idx else random.randint(1,9)
            bar_r="▓"*pos+"░"*(10-pos)
            trophy="  🏆" if i==winner_idx else ""
            you="  ← Bạn" if i==your_idx else ""
            lines.append(f"{name} `{bar_r}`{trophy}{you}")

        won=(your_idx==winner_idx)
        # Tỉ lệ × 5 nếu thắng
        delta=bet*4 if won else -bet
        new_ha=max(0,_safe(player,"linh_thach_ha")+delta)
        await self.bot.db.update_player(ctx.author.id, linh_thach_ha=new_ha)

        embed=discord.Embed(
            title="🏁 KẾT QUẢ ĐUA LINH THÚ",
            description="\n".join(lines),
            color=0xFFD700 if won else 0xF44336
        )
        embed.add_field(name="🎯 Bạn Đặt", value=animals[your_idx][0],  inline=True)
        embed.add_field(name="🏆 Về Đích", value=animals[winner_idx][0],inline=True)
        embed.add_field(
            name="💰 Kết Quả",
            value=f"{'🎉 +' if won else '💸 '}{abs(delta):,} Hạ LT",
            inline=False
        )
        await msg.edit(content=None,embed=embed)

    # ══ ĐỔ XU ════════════════════════════════════════════════
    @commands.command(name="doxu", aliases=["flip","xu","coinflip"])
    async def doxu(self, ctx, bet: int = 500, mat: str = "ngua"):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        """Đồng xu - 50/50, ×2 nếu thắng"""
        if bet<100:
            await ctx.send(embed=warn("Cược tối thiểu 100 Hạ!")); return
        if bet>_safe(player,"linh_thach_ha"):
            await ctx.send(embed=error("Không đủ LT!")); return
        mat=mat.lower()
        if mat not in ("ngua","sap","n","s"):
            await ctx.send(embed=warn("Chọn `ngua` hoặc `sap`!")); return

        result = random.choice(["ngua","sap"])
        icon   = "🦅 NGỰA" if result=="ngua" else "👑 SẤP"
        won    = result in (mat, mat[0])
        delta  = bet if won else -bet
        new_ha = max(0, _safe(player,"linh_thach_ha")+delta)
        await self.bot.db.update_player(ctx.author.id, linh_thach_ha=new_ha)

        embed=discord.Embed(
            title=f"🪙 ĐỒNG XU — {icon}",
            color=0x4CAF50 if won else 0xF44336
        )
        embed.description=(
            f"**{'THẮNG! +' if won else 'THUA -'}{abs(delta):,} Hạ**\n"
            f"Số dư: `{new_ha:,} Hạ`"
        )
        await ctx.send(embed=embed)

    # ══ SỐ MAY MẮN ══════════════════════════════════════════
    @commands.command(name="so_may", aliases=["lucky_number","somay","lucky"])
    async def so_may(self, ctx, guess: int = None, bet: int = 1000):
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return
        """Đoán số 1-10, thắng ×8"""
        if guess is None:
            await ctx.send(embed=warn("Dùng: `,tl so_may [1-10] [cược]`")); return
        if not 1<=guess<=10:
            await ctx.send(embed=warn("Số phải từ **1 đến 10**!")); return
        if bet<500:
            await ctx.send(embed=warn("Cược tối thiểu 500 Hạ!")); return
        if bet>_safe(player,"linh_thach_ha"):
            await ctx.send(embed=error("Không đủ LT!")); return

        result = random.randint(1,10)
        won    = result==guess
        delta  = bet*7 if won else -bet
        new_ha = max(0, _safe(player,"linh_thach_ha")+delta)
        await self.bot.db.update_player(ctx.author.id, linh_thach_ha=new_ha)

        embed=discord.Embed(
            title="🔢 SỐ MAY MẮN",
            color=0xFFD700 if won else 0xF44336
        )
        embed.add_field(name="🎯 Bạn Đoán", value=f"**{guess}**",  inline=True)
        embed.add_field(name="🎲 Kết Quả",  value=f"**{result}**", inline=True)
        embed.add_field(name="💰",
            value=f"{'🎉 +' if won else '💸 '}{abs(delta):,} Hạ",
            inline=False
        )
        embed.set_footer(text="Tỉ lệ 1/10 → thắng ×8  •  Tu Tiên Bot v3")
        await ctx.send(embed=embed)

    # ══ ĐỐ KINH VIỆN (TRIVIA) ═══════════════════════════════
    _doka_cooldowns: dict = {}

    DOKA_CATEGORY_MAP = {
        "9":  "🧠 Kiến Thức Chung",
        "17": "🔬 Khoa Học Tự Nhiên",
        "18": "💻 Máy Tính",
        "19": "⚗️ Toán Học",
        "22": "🌍 Địa Lý",
        "23": "📜 Lịch Sử",
        "27": "🐾 Động Vật Học",
        "21": "🏟️ Thể Thao",
    }

    @commands.command(name="doka", aliases=["dokinhvien","travia","trivia","dkv"])
    async def doka(self, ctx):
        """🎓 Đố Kinh Viện — trả lời trắc nghiệm nhận LT thưởng"""
        player = await self.bot.db.get_player(ctx.author.id)
        if not player:
            await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`.")); return

        uid = str(ctx.author.id)
        now_ts = time.time()
        COOLDOWN = 300  # 5 phút

        last = self._doka_cooldowns.get(uid, 0)
        remaining = COOLDOWN - (now_ts - last)
        if remaining > 0:
            mins = int(remaining // 60); secs = int(remaining % 60)
            await ctx.send(embed=warn(
                f"⏳ Đố Kinh Viện hồi chiêu!\n"
                f"Còn **{mins}:{secs:02d}** phút nữa có thể làm bài."
            )); return

        # Tính thưởng theo cảnh giới
        ri = int(_safe(player, "realm_index", 0))
        realm_mult = max(1, ri + 1)
        base_reward = 5_000 * realm_mult  # 5K → 300K+ theo cảnh giới

        # Gọi Open Trivia DB API
        loading = await ctx.send("📚 *Đang lấy câu hỏi từ Đố Kinh Viện...*")
        cat_id = random.choice(list(self.DOKA_CATEGORY_MAP.keys()))
        url = f"https://opentdb.com/api.php?amount=1&category={cat_id}&type=multiple&encode=url3986"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                    data = await resp.json()
        except Exception:
            await loading.delete()
            await ctx.send(embed=warn("❌ Không kết nối được Đố Kinh Viện. Thử lại sau!")); return

        if not data.get("results"):
            await loading.delete()
            await ctx.send(embed=warn("❌ Đố Kinh Viện không trả về câu hỏi. Thử lại sau!")); return

        q = data["results"][0]
        # URL decode
        from urllib.parse import unquote
        question_text = unquote(q["question"])
        correct_ans   = unquote(q["correct_answer"])
        wrong_ans     = [unquote(a) for a in q["incorrect_answers"]]
        difficulty    = q.get("difficulty", "medium")

        # Phần thưởng theo độ khó
        diff_mult = {"easy": 1, "medium": 2, "hard": 4}.get(difficulty, 2)
        reward = base_reward * diff_mult
        diff_icon = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}.get(difficulty, "🟡")
        diff_vn   = {"easy": "Dễ", "medium": "Trung Bình", "hard": "Khó"}.get(difficulty, "Trung Bình")

        # Xáo đáp án
        answers = wrong_ans + [correct_ans]
        random.shuffle(answers)
        correct_idx = answers.index(correct_ans)
        labels = ["🅐", "🅑", "🅒", "🅓"]

        cat_name = self.DOKA_CATEGORY_MAP.get(cat_id, "📚 Đố Kinh Viện")

        await loading.delete()
        embed = discord.Embed(
            title=f"🎓 ĐỐ KINH VIỆN — {cat_name}",
            description=f"**{question_text}**",
            color=0x6B48FF
        )
        choices_text = "\n".join(f"{labels[i]} {a}" for i, a in enumerate(answers))
        embed.add_field(name="📝 Đáp Án", value=choices_text, inline=False)
        embed.add_field(
            name=f"{diff_icon} Độ Khó: {diff_vn}",
            value=f"💰 Thưởng nếu đúng: **{reward:,} Hạ LT**",
            inline=False
        )
        embed.set_footer(text="Gõ A / B / C / D để trả lời • Thời gian: 30 giây")
        await ctx.send(embed=embed)

        def check(m):
            return (
                m.author.id == ctx.author.id
                and m.channel == ctx.channel
                and m.content.strip().upper() in ("A", "B", "C", "D")
            )

        try:
            msg = await self.bot.wait_for("message", check=check, timeout=30.0)
        except asyncio.TimeoutError:
            await ctx.send(embed=warn(
                f"⏰ Hết thời gian! Đáp án đúng là: **{labels[correct_idx]} {correct_ans}**\n"
                f"_(Cooldown không tính vì hết giờ)_"
            )); return

        chosen_idx = "ABCD".index(msg.content.strip().upper())
        self._doka_cooldowns[uid] = now_ts  # Set cooldown sau khi trả lời

        if chosen_idx == correct_idx:
            # Thắng
            new_ha = int(_safe(player, "linh_thach_ha", 0)) + reward
            await self.bot.db.update_player(ctx.author.id, linh_thach_ha=new_ha)
            embed_result = discord.Embed(
                title="✅ CHÍNH XÁC!",
                description=(
                    f"🎉 Đáp án đúng: **{labels[correct_idx]} {correct_ans}**\n\n"
                    f"💰 Nhận: **+{reward:,} Hạ LT**\n"
                    f"👛 Số dư: **{new_ha:,} Hạ**"
                ),
                color=0x4CAF50
            )
            embed_result.set_footer(text=f"Cooldown 5 phút • {diff_vn} × {diff_mult} • Tu Tiên Bot v4")
        else:
            embed_result = discord.Embed(
                title="❌ SAI RỒI!",
                description=(
                    f"💔 Đáp án đúng là: **{labels[correct_idx]} {correct_ans}**\n"
                    f"Bạn đã chọn: **{labels[chosen_idx]} {answers[chosen_idx]}**\n\n"
                    f"_Học thêm và thử lại sau 5 phút nhé!_"
                ),
                color=0xF44336
            )
            embed_result.set_footer(text=f"Cooldown 5 phút • Tu Tiên Bot v4")

        await ctx.send(embed=embed_result)

    # ══ BẢNG THỐNG KÊ GAME ══════════════════════════════════
    @commands.command(name="game_info", aliases=["minigame_info","trochoi"])
    async def game_info(self, ctx):
        embed=discord.Embed(title="🎮 MINI GAME — HƯỚNG DẪN", color=0xE91E63)
        embed.add_field(name="🎲 Đổ Thạch (`,tl dt [bet]`)", value=(
            "3 xúc xắc | Min: 100 Hạ\n"
            "Tam Sát ×5 | Cao×3 | Trung×1.5 | Hòa×1"
        ), inline=False)
        embed.add_field(name="🎡 Vòng Quay (`,tl quay`)", value=(
            "10 phần thưởng | Chi 5K Hạ\n"
            "Rương Thần (2%) → Cực Phẩm LT (3%)"
        ), inline=False)
        embed.add_field(name="🃏 Xì Dách (`,tl bai [bet]`)", value=(
            "Đánh Dealer | Min: 500 Hạ\n"
            "Thắng ×2 | Blackjack ×2.5"
        ), inline=False)
        embed.add_field(name="🏁 Đua Linh Thú (`,tl dua [bet]`)", value=(
            "6 linh thú | Min: 200 Hạ\n"
            "Thắng ×5"
        ), inline=False)
        embed.add_field(name="🪙 Đồng Xu (`,tl doxu [bet] [ngua/sap]`)", value=(
            "50/50 | Min: 100 Hạ | Thắng ×2"
        ), inline=False)
        embed.add_field(name="🔢 Số May Mắn (`,tl so_may [1-10] [bet]`)", value=(
            "Đoán 1-10 | Min: 500 Hạ | Thắng ×8"
        ), inline=False)
        embed.add_field(name="🎓 Đố Kinh Viện (`,tl doka`)", value=(
            "Trắc nghiệm 4 đáp án | Cooldown 5 phút\n"
            "Thưởng theo cảnh giới & độ khó: Dễ×1 / TB×2 / Khó×4"
        ), inline=False)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Minigame(bot))

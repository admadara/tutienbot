"""cogs/core.py - help, lenh, ping, update, thongtin v3"""
import discord
from discord.ext import commands
import time, sys

START_TIME = time.time()

class Core(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @commands.command(name="help", aliases=["h"])
    async def help_main(self, ctx, cat: str = None):
        if cat: await self._cat(ctx, cat.lower())
        else:   await self._index(ctx)

    async def _index(self, ctx):
        embed = discord.Embed(
            title="📜 BÍ TỊCH TU TIÊN — MỤC LỤC",
            description="Gõ `,tl help [danh mục]` để xem chi tiết",
            color=0x6A0DAD
        )
        embed.add_field(name="🔰 `,tl help coban`",    value="Tân thủ, tu luyện, đột phá",      inline=True)
        embed.add_field(name="💰 `,tl help kinhte`",   value="Shop, mua bán, Linh Thạch",        inline=True)
        embed.add_field(name="⚔️ `,tl help pk`",       value="Chiến đấu, bảng xếp hạng",        inline=True)
        embed.add_field(name="🏞️ `,tl help bicanh`",   value="Bí cảnh, Boss, Thiên Tầng Tháp",  inline=True)
        embed.add_field(name="⛩️ `,tl help tongmon`",  value="Tông Môn, Công Pháp",              inline=True)
        embed.add_field(name="🔮 `,tl help trangbi`",  value="Trang bị, cường hóa, ngọc",       inline=True)
        embed.add_field(name="⚗️ `,tl help luyen`",    value="Luyện Đan từ nguyên liệu",         inline=True)
        embed.add_field(name="🐾 `,tl help linhthu`",  value="Linh Thú — nuôi, chiến đấu",       inline=True)
        embed.add_field(name="🎲 `,tl help minigame`", value="Đổ Thạch, Quay, Bài, Đua",        inline=True)
        embed.add_field(name="💡 `,tl help tips`",     value="Mẹo & cơ chế game",               inline=True)
        embed.add_field(name="⚖️ `,tl help luat`",     value="Điều lệ server",                   inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=True)
        embed.set_footer(text="📋 ,tl lenh — Xem tất cả lệnh  •  Tu Tiên Bot v3")
        await ctx.send(embed=embed)

    async def _cat(self, ctx, cat):
        H = {
            "coban":    self._coban,
            "kinhte":   self._kinhte,
            "pk":       self._pk,
            "bicanh":   self._bicanh,
            "tongmon":  self._tongmon,
            "trangbi":  self._trangbi,
            "luyen":    self._luyen,
            "linhthu":  self._linhthu_help,
            "minigame": self._minigame,
            "tips":     self._tips,
            "luat":     self._luat,
        }
        fn = H.get(cat)
        if fn: await fn(ctx)
        else: await ctx.send(embed=discord.Embed(
            description=f"❓ Không có danh mục `{cat}`.\nGõ `,tl help` để xem danh sách.",
            color=0xFF5722))

    async def _coban(self, ctx):
        embed = discord.Embed(title="🔰 HƯỚNG DẪN TÂN THỦ", color=0x4CAF50)
        embed.add_field(name="1️⃣ Chọn Đạo (1 lần duy nhất)", value=(
            "🌑 `,tl nhapma`  — Ma Đạo *(ATK +30%, CRIT +10%)*\n"
            "☀️ `,tl nhapdao` — Chính Đạo *(ATK/DEF/HP +10%)*\n"
            "📖 `,tl nhapnho` — Nho Đạo *(DEF +50%, HP +30%)*\n"
            "👻 `,tl nhapquy` — Quỷ Đạo *(SPD +50%, CRIT +15%)*\n"
            "🐾 `,tl nhapyeu` — Yêu Đạo *(HP +60%, SPD +5%)*\n"
            "🧴 `,tl nhaplo`  — Lọ Đạo *(EXP +25%, LUCK +50)*"
        ), inline=False)
        embed.add_field(name="2️⃣ Tu Luyện hàng ngày", value=(
            "⚡ `,tl start` — Bắt đầu bế quan\n"
            "🛑 `,tl stop` — Kết thúc nhận EXP\n"
            "📅 `,tl daily` — Điểm danh nhận Linh Thạch\n"
            "📋 `,tl nv` — Xem nhiệm vụ hàng ngày"
        ), inline=False)
        embed.add_field(name="3️⃣ Đột Phá cảnh giới", value=(
            "🚀 `,tl dp` — Đột phá khi đầy EXP\n"
            "⚠️ Từ Chân Tiên trở lên có tỉ lệ thất bại!\n"
            "💊 Dùng Đột Phá Đan để tăng tỉ lệ thành công"
        ), inline=False)
        embed.add_field(name="4️⃣ Xem thông tin", value=(
            "👤 `,tl` — Hồ sơ tu tiên\n"
            "📊 `,tl i` — Chỉ số chi tiết + trang bị\n"
            "🎒 `,tl bag` — Xem túi đồ"
        ), inline=False)
        await ctx.send(embed=embed)

    async def _kinhte(self, ctx):
        embed = discord.Embed(title="💰 KINH TẾ & VẬT PHẨM", color=0xFF9800)
        embed.add_field(name="💱 Tiền Tệ", value=(
            "💰 Hạ Phẩm → 💎 Trung Phẩm → 👑 Cực Phẩm\n"
            "1000 Hạ = 1 Trung | 1000 Trung = 1 Cực\n"
            "`,tl doi ha [số/all]` — Đổi Hạ → Trung\n"
            "`,tl doi trung [số/all]` — Đổi Trung → Cực"
        ), inline=False)
        embed.add_field(name="🛒 Cửa Hàng", value=(
            "`,tl shop` — Xem danh mục\n"
            "`,tl shop danduoc/vukhi/giap/ngoc/nguyen_lieu`\n"
            "`,tl buy [item_id] [số]` — Mua hàng\n"
            "`,tl use [item_id] [số]` — Dùng vật phẩm\n"
            "`,tl tracuu [item_id]` — Tra cứu thông tin"
        ), inline=False)
        embed.add_field(name="🏛️ Đấu Giá P2P", value=(
            "`,tl daugia list` — Xem chợ\n"
            "`,tl daugia ban [id] [sl] [giá]` — Rao bán\n"
            "`,tl daugia mua [#ID]` — Mua ngay\n"
            "`,tl daugia huy [#ID]` — Huỷ đơn\n"
            "📋 Phí rao 2% | Thuế 15% | Trần ×50"
        ), inline=False)
        await ctx.send(embed=embed)

    async def _pk(self, ctx):
        embed = discord.Embed(title="⚔️ CHIẾN ĐẤU & BXH", color=0xF44336)
        embed.add_field(name="⚔️ PK", value=(
            "`,tl pk @người` — Thách đấu 1v1\n"
            "Thắng nhận 5% Linh Thạch của đối thủ\n"
            "Thua mất 5% Linh Thạch của mình"
        ), inline=False)
        embed.add_field(name="🏆 Bảng Xếp Hạng", value=(
            "`,tl bxh` — BXH cảnh giới\n"
            "`,tl bxh giau` — BXH tài phú\n"
            "`,tl bxh exp` — BXH Tu Vi\n"
            "`,tl boss top` — BXH sát thương Boss"
        ), inline=False)
        await ctx.send(embed=embed)

    async def _bicanh(self, ctx):
        embed = discord.Embed(title="🏞️ BÍ CẢNH & BOSS & THÁP", color=0x2196F3)
        embed.add_field(name="🗺️ Bí Cảnh", value=(
            "`,tl bicanh list` — Xem bản đồ\n"
            "`,tl bicanh di [ID]` — Thám hiểm *(tốn Thể Lực)*\n"
            "`,tl bicanh ve` — Về nhận thưởng\n"
            "⚡ Thể Lực hồi 1/phút tự động"
        ), inline=False)
        embed.add_field(name="👹 Boss Thế Giới", value=(
            "`,tl boss` — Xem trạng thái Boss\n"
            "`,tl boss fight` — Tấn công *(20 TL)*\n"
            "`,tl boss top` — BXH sát thương"
        ), inline=False)
        embed.add_field(name="🗼 Thiên Tầng Tháp", value=(
            "`,tl thap` — Xem tiến độ\n"
            "`,tl thap challenge` — Thách đấu tầng tiếp\n"
            "`,tl thap auto` — Tự động leo *(tối đa 10 tầng)*\n"
            "`,tl thap top [all]` — BXH leo tháp *(server/toàn cục)*\n"
            "`,tl thap shop` — Shop Ma Tôn Lệnh 🎟️"
        ), inline=False)
        await ctx.send(embed=embed)

    async def _tongmon(self, ctx):
        embed = discord.Embed(title="🏰 HỆ THỐNG TÔNG MÔN 🏰", color=0x8B4513)
        embed.description = (
            "🔷 `,tl sect create [Tên]` — Tạo Tông Môn *(500.000.000 LT)*\n"
            "🔷 `,tl sect info` — Xem thông tin Tông Môn\n"
            "🔷 `,tl sect list` — Danh sách Tông Môn server\n"
            "🔷 `,tl sect donate [Số tiền]` — Cống hiến xây dựng Tông Môn\n"
            "🔷 `,tl sect upgrade [Mã]` — Nâng cấp kiến trúc *(Tông Chủ/Phó)*\n"
            "🔷 `,tl sect phongchuc [@Tag] [pho/truonglao/thanhvien]` — Phong chức vụ\n"
            "🔷 `,tl sect invite [@Tag]` — Mời thành viên\n"
            "🔷 `,tl sect join` — Chấp nhận lời mời\n"
            "🔷 `,tl sect apply [ID/Tên]` — Xin gia nhập Tông Môn\n"
            "🔷 `,tl sect accept [@Tag/ID]` — Duyệt đơn xin gia nhập\n"
            "🔷 `,tl sect reject [@Tag/ID]` — Từ chối đơn\n"
            "🔷 `,tl sect apps` — Xem danh sách đơn xin vào\n"
            "🔷 `,tl sect leave` — Rời Tông Môn *(Mất cống hiến)*\n"
            "🔷 `,tl sect kick [@Tag]` — Trục xuất *(Tông Chủ/Phó)*\n"
            "🔷 `,tl sect transfer [@Tag]` — Chuyển nhượng chức Tông Chủ\n"
            "🔷 `,tl sect disband` — Giải tán Tông Môn *(Tông Chủ)*\n"
            "🔷 `,tl sect members` — Xem danh sách thành viên\n"
            "🔷 `,tl sect mission` — Nhiệm vụ Tông Môn hàng ngày\n"
            "🔷 `,tl sect congkich [ID_vùng]` — Tấn công chiếm Lãnh địa\n"
            "🔷 `,tl sect tuyenchien [ID_vùng]` — Tuyên chiến *(5 phút trước khi công kích)*\n"
            "🔷 `,tl sect beast [ID_vùng] [loại]` — Triệu hồi/Nâng cấp Thần Thú\n"
            "🔷 `,tl sect tubo [ID_vùng] [LT]` — Bơm máu/Nâng cấp Trận Pháp\n"
            "🔷 `,tl sect shop` — Mở cửa hàng Tông môn"
        )
        embed.add_field(name="🎖️ Cấp Bậc", value="👑 Tông Chủ → ⚔️ Phó Tông Chủ → 🧓 Trưởng Lão → 👤 Thành Viên", inline=False)
        embed.set_footer(text="Alias: ,tl sect | ,tl tm | ,tl tongmon  •  Tu Tiên Bot v6")
        await ctx.send(embed=embed)

    async def _trangbi(self, ctx):
        embed = discord.Embed(title="🔮 TRANG BỊ & CƯỜNG HÓA", color=0x9C27B0)
        embed.add_field(name="🎽 Quản Lý Trang Bị", value=(
            "`,tl trangbi` — Xem trang bị + bonus đang mặc\n"
            "`,tl equip [item_id]` — Trang bị vật phẩm\n"
            "`,tl thao [slot]` — Tháo *(weapon/armor/hat/...)*"
        ), inline=False)
        embed.add_field(name="⚡ Cường Hóa", value=(
            "`,tl cuonghoa [slot]` — Nâng cấp +1\n"
            "**+0→+9:** 100% | **+10→+14:** 80%\n"
            "**+15→+19:** 60% | **+20→+24:** 40% | **+25:** 20%\n"
            "Chi phí tăng dần theo cấp +"
        ), inline=False)
        await ctx.send(embed=embed)

    async def _luyen(self, ctx):
        embed = discord.Embed(title="⚗️ LUYỆN ĐAN", color=0xFF6F00)
        embed.add_field(name="📜 Lệnh", value=(
            "`,tl luyendan congthuc` — Xem công thức\n"
            "`,tl luyendan luyen [dan_id] [số]` — Luyện đan\n\n"
            "**Nguyên Liệu:** Mua tại `,tl shop nguyen_lieu`"
        ), inline=False)
        embed.add_field(name="⚗️ Công Thức Tóm Tắt", value=(
            "**Tầng 1:** 3x Linh Thảo → Luyện Khí Đan\n"
            "**Tầng 2:** 3x Hỏa Tinh + 2x Linh Thảo → Trúc Cơ Đan\n"
            "**Tầng 3:** 4x Thiên Nhẫn + 2x Hỏa Tinh → Kim Đan\n"
            "**Tầng 4:** 3x Long Khí Tượng + 3x Thiên Nhẫn → Đột Phá Đan\n"
            "**Tầng 5:** 2x Hỗn Độn Tinh + 5x Long Khí → Trường Sinh Đan"
        ), inline=False)
        await ctx.send(embed=embed)

    async def _linhthu_help(self, ctx):
        embed = discord.Embed(title="🐾 LINH THÚ", color=0xFF9800)
        embed.add_field(name="🥚 Nhận Linh Thú", value=(
            "Mua trứng tại `,tl shop linhthu`\n"
            "Dùng: `,tl use [trung_id]` để ấp\n"
            "Mỗi người chỉ có **1 Linh Thú**"
        ), inline=False)
        embed.add_field(name="💗 Chăm Sóc", value=(
            "`,tl linhthu` — Xem thông tin Linh Thú\n"
            "`,tl linhthu cho` — Cho ăn *(+10 tình cảm, 500 Hạ)*\n"
            "`,tl linhthu tap` — Huấn luyện *(+EXP, 1000 Hạ)*"
        ), inline=False)
        embed.add_field(name="✨ Bonus Cho Chủ", value=(
            "🐉 Thần Long: +20% ATK, +10% DEF, +15% HP\n"
            "🦅 Phượng Hoàng: +25% SPD, +10% CRIT\n"
            "🐢 Thần Quy: +30% DEF, +25% HP"
        ), inline=False)
        await ctx.send(embed=embed)

    async def _minigame(self, ctx):
        embed = discord.Embed(title="🎲 MINI GAME", color=0xE91E63)
        embed.add_field(name="🎮 Trò Chơi", value=(
            "🎲 `,tl dt [bet]` — Đổ 3 xúc xắc *(min 100 Hạ)*\n"
            "   Tam sát ×5 | Cao ×2 | Trung ×1.5 | Thấp thua\n\n"
            "🎡 `,tl quay` — Vòng Quay Vận Mệnh *(5K Hạ)*\n"
            "   8 phần thưởng khác nhau\n\n"
            "🃏 `,tl bai [bet]` — Xì Dách Tiên Giới *(min 500 Hạ)*\n"
            "   Thắng ×2 | Xì ×2.5\n\n"
            "🏁 `,tl dua [bet]` — Đua Linh Thú *(min 200 Hạ)*\n"
            "   Thắng ×4 | Thua mất tiền cược"
        ), inline=False)
        await ctx.send(embed=embed)

    async def _tips(self, ctx):
        embed = discord.Embed(title="💡 MẸO & CƠ CHẾ GAME", color=0xFFD700)
        embed.add_field(name="⚡ EXP", value=(
            "• EXP/giây = 10 × Ngộ Tính/200 × Bonus Đạo\n"
            "• Lọ Đạo có EXP rate +25% cao nhất\n"
            "• Bí Cảnh cho thêm EXP + vật phẩm drop"
        ), inline=False)
        embed.add_field(name="💪 Lực Chiến", value=(
            "• Tăng khi đột phá, mặc trang bị tốt, cường hóa\n"
            "• Linh Thú bonus thêm % theo loài\n"
            "• Ngọc khảm vào trang bị tăng stat"
        ), inline=False)
        embed.add_field(name="🔋 Thể Lực", value=(
            "• Hồi 1/phút tự động\n"
            "• Phục Tinh Đan +50 TL | Đại Hoàn Đan +200 TL\n"
            "• Streak điểm danh 7+ ngày tặng thêm đan dược"
        ), inline=False)
        embed.add_field(name="🎯 Ưu Tiên Hàng Ngày", value=(
            "1. `,tl daily` — Điểm danh\n"
            "2. `,tl nv` — Nhận nhiệm vụ\n"
            "3. `,tl bicanh di` — Thám hiểm\n"
            "4. `,tl boss fight` — Đánh Boss\n"
            "5. `,tl start/stop` — Bế quan"
        ), inline=False)
        await ctx.send(embed=embed)

    async def _luat(self, ctx):
        embed = discord.Embed(title="⚖️ TIÊN QUY & ĐIỀU LỆ", color=0x607D8B)
        embed.description = (
            "**1.** 🚫 Không spam lệnh liên tục\n"
            "**2.** 🚫 Không dùng tool/hack/exploit\n"
            "**3.** ⚠️ Mọi giao dịch đấu giá tự chịu trách nhiệm\n"
            "**4.** 👑 Admin có quyền reset/ban nhân vật vi phạm\n"
            "**5.** 🐛 Báo bug tại kênh #bao-loi\n"
            "**6.** 🤝 Tôn trọng người chơi khác"
        )
        await ctx.send(embed=embed)

    # ── ,tl lenh ─────────────────────────────────────────────
    @commands.command(name="lenh", aliases=["commands", "cmd"])
    async def lenh(self, ctx):
        embed = discord.Embed(
            title="📋 TẤT CẢ LỆNH — TU TIÊN BOT v4",
            description="Prefix: `,tl` hoặc `,tuluyen`",
            color=0x2196F3
        )
        embed.add_field(name="👤 Nhân Vật", value=(
            "`,tl` `,tl i` `,tl tuvi`\n"
            "`,tl hanh_trinh` `,tl thongtin`\n"
            "`,tl co_do @ng` `,tl so_sanh @ng`\n"
            "`,tl doi_ten [tên]` `,tl server_stats`"
        ), inline=True)
        embed.add_field(name="🌿 Tu Luyện", value=(
            "`,tl nhapma/dao/nho/quy/yeu/lo`\n"
            "`,tl start` `,tl stop`\n"
            "`,tl dp` `,tl daily`\n"
            "`,tl nv` `,tl nv nhan`\n"
            "`,tl buff` `,tl thien_dinh`\n"
            "`,tl linh_khi`\n"
            "`,tl chuyensinh` — Reset, buff vĩnh viễn\n"
            "`,tl chuyensinh_info` — Xem tiến độ"
        ), inline=True)
        embed.add_field(name="🗺️ Khám Phá", value=(
            "`,tl bicanh list/di/ve`\n"
            "`,tl boss fight/top`\n"
            "`,tl thap challenge/auto`\n"
            "`,tl thap top/shop/mua`\n"
            "`,tl kham_pha`"
        ), inline=True)
        embed.add_field(name="💰 Kinh Tế", value=(
            "`,tl shop [loại]` `,tl buy/use`\n"
            "`,tl bag` `,tl tracuu [id]`\n"
            "`,tl doi [tier] [sl]`\n"
            "`,tl daugia list/ban/mua/huy`\n"
            "`,tl ngan_hang` `,tl vay [sl]`\n"
            "`,tl tra_no` `,tl gia_ca [id]`\n"
            "`,tl lich_su` `,tl top_giau [all]`\n"
            "`,tl tang_kinh` — Mua công pháp mới"
        ), inline=True)
        embed.add_field(name="⚔️ Chiến Đấu", value=(
            "`,tl pk @ng [cược]`\n"
            "`,tl chap_nhan @ng`\n"
            "`,tl dau_truong`\n"
            "`,tl bxh [realm/giau/exp/pk/boss/luc/cs] [all]`\n"
            "`,tl thi_dau` `,tl mua_sat`\n"
            "`,tl ky_nang` `,tl uk [id]`"
        ), inline=True)
        embed.add_field(name="🔮 Trang Bị", value=(
            "`,tl trangbi` `,tl equip [id]`\n"
            "`,tl thao [slot]`\n"
            "`,tl cuonghoa [slot] [sl]`\n"
            "`,tl xem_cuong` `,tl compare_eq @ng`\n"
            "`,tl kham [slot] [ngoc]`\n"
            "`,tl thao_ngoc [slot]` `,tl ngoc`"
        ), inline=True)
        embed.add_field(name="⚗️ Luyện & Chế", value=(
            "`,tl luyendan congthuc`\n"
            "`,tl luyendan luyen [id] [sl]`\n"
            "`,tl cheta congthuc`\n"
            "`,tl cheta lam [id] [sl]`\n"
            "`,tl cheta nguyen_lieu`"
        ), inline=True)
        embed.add_field(name="📜 Công Pháp & Kỹ Năng", value=(
            "`,tl cong_phap danh_sach`\n"
            "`,tl cong_phap mua [id]`\n"
            "`,tl cong_phap kich_hoat [id]`\n"
            "`,tl cong_phap cua_toi`\n"
            "`,tl ky_nang` `,tl uk [id]`"
        ), inline=True)
        embed.add_field(name="🐾 Linh Thú", value=(
            "`,tl linhthu` `,tl linhthu cho`\n"
            "`,tl linhthu tap` `,tl linhthu danh`\n"
            "`,tl linhthu thong_tin`\n"
            "`,tl linhthu phong_thich`\n"
            "`,tl shop linhthu`"
        ), inline=True)
        embed.add_field(name="⛩️ Tông Môn", value=(
            "`,tl sect create/info/list`\n"
            "`,tl sect apply/join/leave`\n"
            "`,tl sect members/donate/mission`\n"
            "`,tl sect invite/accept/reject/apps`\n"
            "`,tl sect kick/transfer/disband`\n"
            "`,tl sect upgrade/phongchuc/shop`\n"
            "`,tl sect tuyenchien/congkich`\n"
            "`,tl sect beast/tubo`\n"
            "`,tl bang_hoi`"
        ), inline=True)
        embed.add_field(name="🎲 Mini Game", value=(
            "`,tl dt [bet]` `,tl quay`\n"
            "`,tl bai [bet]` `,tl dua [bet]`\n"
            "`,tl doxu [bet]` `,tl so_may [n] [bet]`\n"
            "`,tl doka` — Đố Kinh Viện (CD 5p)\n"
            "`,tl game_info`"
        ), inline=True)
        embed.add_field(name="🌍 Thế Giới & Sự Kiện", value=(
            "`,tl thoi_tiet` `,tl setloc [tp]`\n"
            "`,tl su_kien` `,tl ban_do`\n"
            "`,tl tin_tuc` `,tl boi_bai`\n"
            "`,tl diary`"
        ), inline=True)
        embed.add_field(name="🏆 Thành Tựu & Xã Hội", value=(
            "`,tl danh_hieu xem/mac`\n"
            "`,tl give @ng [id] [sl]`\n"
            "`,tl doi_lt @ng [sl]`\n"
            "`,tl phong_than @ng`\n"
            "`,tl nap_the [mã]`"
        ), inline=True)
        embed.add_field(name="📖 Wiki & Tra Cứu", value=(
            "`,tl wiki [từ khóa]` — Tra cứu mọi thứ\n"
            "`,tl daoly` — Đạo lý ngẫu nhiên"
        ), inline=True)
        embed.add_field(name="🎣 Câu Cá (`,cc`)", value=(
            "`,cc start/stop/map` — Buông cần\n"
            "`,cc shop/buy/sell/bag`\n"
            "`,cc daily/quest/trophy/stats`\n"
            "`,cc island` — Đảo AFK\n"
            "`,cc boss/top [all]/gacha/vip`\n"
            "_(gõ `,cc` để xem đầy đủ)_"
        ), inline=True)
        embed.add_field(name="🔮 Thiên Cơ Các", value=(
            "`,tl thienco` — Lời tiên tri hằng ngày\n"
            "`,tl trieuhoi` — Triệu hồi Hộ Pháp/Linh Sứ\n"
            "`,tl linhthudo [tag]` — Linh Thú Đồ\n"
            "`,tl thiencoc` — Hướng dẫn chi tiết"
        ), inline=True)
        embed.add_field(name="ℹ️ Hệ Thống", value=(
            "`,tl help [nhóm]` `,tl ping`\n"
            "`,tl update` `,tl lenh`\n"
            "`,tl help_me` `,tl server_stats`"
        ), inline=True)
        embed.set_footer(text="Tu Tiên Bot v5  •  ,tl help [nhóm] để xem chi tiết  •  Tổng ~100 lệnh")
        await ctx.send(embed=embed)

    @commands.command(name="thongtin", aliases=["about", "botinfo"])
    async def thongtin(self, ctx):
        up = int(time.time() - START_TIME)
        h, r = divmod(up, 3600); m, s = divmod(r, 60)
        try:
            row = await self.bot.db.fetchone("SELECT COUNT(*) as c FROM players")
            players = row["c"] if row else 0
        except: players = 0
        lat = round(self.bot.latency * 1000)
        color = 0x4CAF50 if lat < 100 else 0xFF9800 if lat < 200 else 0xF44336

        embed = discord.Embed(title="ℹ️ THÔNG TIN BOT TU TIÊN", color=0x6A0DAD)
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.add_field(name="🤖 Tên Bot",     value=f"`{self.bot.user.name}`",          inline=True)
        embed.add_field(name="📌 Phiên Bản",   value="`v3.0`",                           inline=True)
        embed.add_field(name="🏓 Ping",        value=f"`{lat}ms`",                       inline=True)
        embed.add_field(name="⏱️ Uptime",      value=f"`{h}h {m}m {s}s`",               inline=True)
        embed.add_field(name="🌐 Servers",     value=f"`{len(self.bot.guilds)}`",         inline=True)
        embed.add_field(name="⚔️ Tu Sĩ",      value=f"`{players:,}`",                   inline=True)
        embed.add_field(name="🐍 Python",      value=f"`{sys.version[:6]}`",             inline=True)
        embed.add_field(name="📚 discord.py",  value=f"`{discord.__version__}`",         inline=True)
        embed.add_field(name="💾 Database",    value="`SQLite`",                         inline=True)
        embed.add_field(name="📋 Prefix",      value="`,tl` hoặc `,tuluyen`",            inline=False)
        embed.set_footer(text="Tu Tiên Bot v3  •  Gõ ,tl lenh để xem tất cả lệnh")
        await ctx.send(embed=embed)

    @commands.command(name="ping")
    async def ping(self, ctx):
        lat = round(self.bot.latency * 1000)
        color = 0x4CAF50 if lat < 100 else 0xFF9800 if lat < 200 else 0xF44336
        bars = "▓" * min(int(lat/20), 10) + "░" * max(0, 10 - int(lat/20))
        embed = discord.Embed(
            title="🏓 PONG!",
            description=f"```{bars}```\n**{lat}ms** {'🟢 Tốt' if lat<100 else '🟡 Bình thường' if lat<200 else '🔴 Chậm'}",
            color=color
        )
        await ctx.send(embed=embed)

    @commands.command(name="update")
    async def update(self, ctx):
        embed = discord.Embed(title="🆕 NHẬT KÝ CẬP NHẬT", color=0x6A0DAD)
        embed.add_field(name="v3.0 — Đại Cập Nhật", value=(
            "✅ 41 lệnh đầy đủ\n"
            "✅ Embed đẹp theo cảnh giới\n"
            "✅ Lực chiến K/M/T/B format\n"
            "✅ Nhiệm vụ hàng ngày\n"
            "✅ Luyện Đan từ nguyên liệu\n"
            "✅ Linh Thú — nuôi & huấn luyện\n"
            "✅ Tông Môn đầy đủ\n"
            "✅ Cường hóa trang bị +25\n"
            "✅ 4 Mini Game\n"
            "✅ Đấu giá P2P\n"
            "✅ ,tl rỗng → hiện hồ sơ"
        ), inline=False)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Core(bot))

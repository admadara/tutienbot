"""cogs/wiki.py - Lệnh ,tl wiki [loại] [trang] - Từ điển Tu Tiên"""
import discord
from discord.ext import commands
from utils.embeds import warn

# ══ DỮ LIỆU WIKI ════════════════════════════════════════════

WIKI_CANHGIOI = {
    "title": "🌌 CẢNH GIỚI TU TIÊN",
    "pages": [
        [
            ("🔰 Sơ Cấp (1-8)", ""),
            ("1. Luyện Thể (9 tầng)",  "EXP base: 200/tầng"),
            ("2. Tụ Khí (9 tầng)",     "EXP base: 1,000/tầng"),
            ("3. Luyện Khí (9 tầng)",  "EXP base: 5,000/tầng"),
            ("4. Ngưng Khí (9 tầng)",  "EXP base: 20,000/tầng"),
            ("5. Trúc Cơ (9 tầng)",    "EXP base: 80,000/tầng"),
            ("6. Tử Phủ (9 tầng)",     "EXP base: 300,000/tầng"),
            ("7. Đạo Cung (9 tầng)",   "EXP base: 1,000,000/tầng"),
            ("8. Kim Đan (9 tầng)",    "EXP base: 4,000,000/tầng"),
        ],
        [
            ("⚡ Trung Cấp (9-14)", ""),
            ("9.  Nguyên Anh (9 tầng)", "EXP base: 15,000,000/tầng"),
            ("10. Hóa Thần (9 tầng)",   "EXP base: 60,000,000/tầng"),
            ("11. Luyện Hư (9 tầng)",   "EXP base: 250,000,000/tầng"),
            ("12. Hợp Thể (9 tầng)",    "EXP base: 1,000,000,000/tầng"),
            ("13. Đại Thừa (9 tầng)",   "EXP base: 4B/tầng"),
            ("14. Độ Kiếp (9 tầng)",    "EXP base: 15B/tầng"),
        ],
        [
            ("✨ Tiên Cấp (15-23)", "Bắt đầu có tỉ lệ thất bại đột phá"),
            ("15. Bán Tiên (9 tầng)",      "Fail: 10%"),
            ("16. Nhân Tiên (9 tầng)",     "Fail: 12%"),
            ("17. Địa Tiên (9 tầng)",      "Fail: 14%"),
            ("18. Thiên Tiên (9 tầng)",    "Fail: 16%"),
            ("19. Chân Tiên (9 tầng)",     "Fail: 18%"),
            ("20. Huyền Tiên (9 tầng)",    "Fail: 20%"),
            ("21. Kim Tiên (9 tầng)",      "Fail: 22%"),
            ("22. Thái Ất Tiên (9 tầng)", "Fail: 24%"),
            ("23. Đại La Tiên (9 tầng)",   "Fail: 26%"),
        ],
        [
            ("👑 Tiên Vương (24-30)", ""),
            ("24. Tiên Quân (9 tầng)",  "Fail: 28%"),
            ("25. Tiên Vương (9 tầng)", "Fail: 30%"),
            ("26. Tiên Hoàng (9 tầng)", "Fail: 32%"),
            ("27. Tiên Tôn (9 tầng)",   "Fail: 34%"),
            ("28. Tiên Đế (9 tầng)",    "Fail: 36%"),
            ("29. Tiên Thánh (9 tầng)", "Fail: 38%"),
            ("30. Tiên Tổ (3 tầng)",    "Fail: 40%"),
        ],
        [
            ("⚡ Thần Cấp (31-39)", ""),
            ("31. Chân Thần (9 tầng)",  "Fail: 42%"),
            ("32. Thiên Thần (9 tầng)", "Fail: 44%"),
            ("33. Cổ Thần (9 tầng)",    "Fail: 46%"),
            ("34. Thần Vương (9 tầng)", "Fail: 48%"),
            ("35. Thần Hoàng (9 tầng)", "Fail: 50%"),
            ("36. Thần Đế (9 tầng)",    "Fail: 52%"),
            ("37. Thần Tôn (9 tầng)",   "Fail: 54%"),
            ("38. Thần Thánh (9 tầng)", "Fail: 56%"),
            ("39. Thần Tổ (3 tầng)",    "Fail: 58%"),
        ],
        [
            ("🌀 Hỗn Độn / Vô Thủy (40-49)", ""),
            ("40. Hỗn Độn (9 tầng)",          "Fail: 60%"),
            ("41. Hồng Mông (9 tầng)",         "Fail: 62%"),
            ("42. Thái Sơ (9 tầng)",           "Fail: 64%"),
            ("43. Khởi Nguyên (9 tầng)",       "Fail: 66%"),
            ("44. Tạo Hóa (9 tầng)",           "Fail: 68%"),
            ("45. Chưởng Đạo (9 tầng)",        "Fail: 70%"),
            ("46. Bất Hủy (9 tầng)",           "Fail: 72%"),
            ("47. Vĩnh Hằng (9 tầng)",         "Fail: 74%"),
            ("48. Siêu Thoát (9 tầng)",        "Fail: 76%"),
            ("49. Chúa Tể (9 tầng)",           "Fail: 78%"),
        ],
        [
            ("🌑 Vô Thượng Cấp (50-59)", ""),
            ("50. Vô Thượng Đạo Tổ (9 tầng)", "Fail: 80%"),
            ("51. Hư Không Thần (9 tầng)",     "Fail: 82%"),
            ("52. Hư Không Thánh (9 tầng)",    "Fail: 82%"),
            ("53. Hư Không Vương (9 tầng)",    "Fail: 84%"),
            ("54. Hư Không Đế (9 tầng)",       "Fail: 84%"),
            ("55. Hư Không Tổ (9 tầng)",       "Fail: 86%"),
            ("56. Thiên Đạo Giả (9 tầng)",     "Fail: 86%"),
            ("57. Thiên Đạo Thần (9 tầng)",    "Fail: 88%"),
            ("58. Thiên Đạo Thánh (9 tầng)",   "Fail: 88%"),
            ("59. Thiên Đạo Đế (9 tầng)",      "Fail: 90%"),
        ],
        [
            ("♾️ Vạn Giới Cấp (60-70)", ""),
            ("60. Thiên Đạo Tổ (9 tầng)",      "Fail: 90%"),
            ("61. Vũ Trụ Thần (9 tầng)",       "Fail: 92%"),
            ("62. Vũ Trụ Thánh (9 tầng)",      "Fail: 92%"),
            ("63. Vũ Trụ Đế (9 tầng)",         "Fail: 94%"),
            ("64. Vũ Trụ Tổ (9 tầng)",         "Fail: 94%"),
            ("65. Bản Nguyên Thần (9 tầng)",   "Fail: 95%"),
            ("66. Bản Nguyên Thánh (9 tầng)",  "Fail: 95%"),
            ("67. Bản Nguyên Đế (9 tầng)",     "Fail: 96%"),
            ("68. Bản Nguyên Tổ (9 tầng)",     "Fail: 96%"),
            ("69. Vô Cực Đạo Thần (9 tầng)",   "Fail: 98%"),
            ("70. Vạn Giới Chí Tôn",           "🏆 Đỉnh tuyệt đối vũ trụ — 1 tầng duy nhất"),
        ],
    ]
}

WIKI_CHUYENSINH = {
    "title": "🔄 CẨM NANG CHUYỂN SINH",
    "pages": [
        [
            ("📜 Chuyển Sinh là gì?",
                "Khi đạt **Vạn Giới Chí Tôn** (cảnh giới cuối), dùng `,tl chuyensinh` "
                "để quay về **Luyện Thể** và bắt đầu tu luyện lại từ đầu."),
            ("⚡ Phần thưởng",
                "Mỗi lần Chuyển Sinh cộng dồn **+15%** tốc độ tu luyện vĩnh viễn "
                "(giảm dần hiệu quả ở số lần cao để tránh lạm phát, hội tụ quanh x2.9)."),
            ("✅ Giữ lại gì?",
                "Linh thạch, trang bị, vật phẩm, tông môn, danh hiệu, thành tựu — "
                "**toàn bộ** vẫn được giữ nguyên."),
            ("🔁 Mất gì?",
                "Chỉ tu vi (EXP) và cảnh giới (realm) reset về vạch xuất phát.\n"
                "Chỉ số ATK/DEF/HP/SPD scale lại theo công thức gốc (Đạo/Linh Căn/Thể Chất "
                "vẫn được tính đúng như khi nhập môn)."),
            ("🏅 Danh hiệu",
                "Nhất Chuyển Đạo Nhân → Cửu Chuyển Diệt Thế (9 lần), "
                "sau đó là Thập Chuyển+N Vĩnh Hằng."),
            ("📊 Theo dõi",
                "`,tl chuyensinh_info` — xem số lần đã chuyển sinh và buff hiện tại.\n"
                "`,tl bxh cs` — bảng xếp hạng theo số lần Chuyển Sinh."),
        ],
    ]
}

WIKI_THECHAT = {
    "title": "💪 CẨM NANG THỂ CHẤT",
    "pages": [
        [
            ("🔘 PHÀM PHẨM", "Common — Đây là tư chất phổ biến nhất"),
            ("⬜ Bình Thường",          "Không bonus chỉ số"),
            ("⬜ Phàm Nhân Chi Thể",    "DEF +5% | HP +5%"),
            ("⬜ Hàn Độc Chi Thể",      "DEF -10% | HP -10% | SPD -10% ⚠️"),
            ("⬜ Thiên Tuyệt Chi Thể",  "DEF -10% | HP -10% | SPD -10% ⚠️"),
        ],
        [
            ("🟢 HẠ PHẨM", "Uncommon — Bắt đầu có bonus tốt"),
            ("🟢 Đồng Bì Thiết Cốt",    "DEF +18% | HP +15%"),
            ("🟢 Bách Mạch Thông Suốt", "DEF +12% | HP +18% | SPD +5%"),
            ("🟢 Cường Hồn Thể",        "HP +22% | DEF +8%"),
            ("🟢 Thiên Sinh Thần Lực",   "ATK +20% | DEF +50% | HP +50% | SPD +15% | KCrit +10%"),
        ],
        [
            ("🔵 TRUNG & THƯỢNG PHẨM", "Rare/Epic — Bonus đáng kể"),
            ("🔵 Kim Cương Thể",         "DEF +30% | HP +15% | KCrit +8%"),
            ("🔵 Thiết Huyết Cương Thể", "ATK +15% | DEF +25% | HP +20%"),
            ("🟣 Long Huyết Thể",        "ATK +35% | HP +30% | Crit +8%"),
            ("🟣 Thần Lực Cổ Thể",      "ATK +30% | DEF +25% | HP +25% | SPD +12%"),
        ],
        [
            ("🟡 ĐỊA PHẨM", "Legendary — Cực mạnh, siêu hiếm"),
            ("🟡 Thương Thiên Bá Thể",      "ATK +50% | DEF +35% | HP +40% | Luck +20"),
            ("🟡 Huyền Vũ Bất Diệt Thể",    "ATK +40% | DEF +60% | HP +55% | KCrit +20 | Luck +15"),
        ],
        [
            ("🔴 THIÊN PHẨM", "Mythic — Thiên Tài cực hiếm"),
            ("🔴 Thiên Ma Thể",           "ATK +80% | SPD +40% | Crit +25 | Luck +50"),
            ("🔴 Cửu Dương Thần Thể",     "ATK +70% | DEF +50% | HP +60% | Crit +18 | Luck +40"),
            ("🟠 Vô Cực Đế Thể",          "ATK x2.2 | DEF +70% | HP x2.2 | Luck +120"),
            ("🟠 Hỗn Nguyên Bất Hoại Thể","ATK x2.5 | DEF x2 | HP x2.5 | SPD +30% | Crit +20 | Luck +150"),
        ],
        [
            ("✨ VÔ THƯỢNG PHẨM", "Transcendent — Chỉ 0.1% có được"),
            ("✨ Khai Thiên Thần Thể",      "ATK x3.2 | DEF x2.5 | HP x3 | SPD +50% | Crit +30 | Luck +250"),
            ("🌟 Vạn Cổ Bất Diệt Thần Thể","ATK x4 | DEF x3 | HP x4 | SPD +80% | Crit +40 | Luck +400"),
            ("📊 Tỉ Lệ Roll", "Phàm: 31% | Hạ: 31% | Trung: 20%\nThượng: 10% | Địa: 5.5% | Thiên: 2%\nThánh: 0.4% | Vô Thượng: 0.1%"),
            ("💡 Tip", "Thể Chất hiếm → ATK/DEF/HP cao vượt trội\nDùng ,tl tayxuong để roll lại"),
        ],
    ]
}

WIKI_HUYETMACH = {
    "title": "🩸 CẨM NANG HUYẾT MẠCH",
    "pages": [
        [
            ("⬜ PHÀM / HẠ PHẨM", "Common/Uncommon"),
            ("⬜ Huyết Mạch Phàm Nhân",       "Crit +3%"),
            ("⬜ Huyết Mạch Hoàng Tộc",       "DEF +5% | HP +5% | Crit +5 | Luck +5"),
            ("🟢 Huyết Mạch Yêu Thú (Tạp)",   "ATK +12% | SPD +18% | Crit +8 | Né +8%"),
            ("🔵 Lang Tộc Huyết Mạch",        "ATK +20% | SPD +22% | Crit +10 | Né +12%"),
        ],
        [
            ("🟣 TRUNG & THƯỢNG PHẨM", "Epic — Bắt đầu uy lực"),
            ("🟣 Thanh Khâu Hồ Tộc (Cửu Vĩ)", "ATK +25% | SPD +30% | Crit +12 | Né +15% | Luck +15"),
            ("🟣 Hùng Vương Địa Huyết",        "ATK +25% | DEF +22% | HP +22% | KCrit +15"),
            ("🟡 Giao Long Huyết Mạch",        "ATK +50% | DEF +40% | HP +40% | SPD +20% | Crit +15 | KCrit +12"),
            ("🟡 Long Tộc Huyết Mạch",         "ATK +45% | HP +35% | Crit +12 | Luck +20"),
            ("🟡 Phượng Hoàng Huyết",          "ATK +35% | SPD +40% | Crit +18 | Luck +25"),
        ],
        [
            ("🔴 ĐỊA & THIÊN PHẨM", "Mythic/Divine — Siêu mạnh"),
            ("🔴 Thần Long Cổ Huyết",    "ATK +75% | DEF +50% | HP +55% | Crit +20 | Luck +50"),
            ("🔴 Bất Tử Tiên Hoàng",     "HP +80% | DEF +60% | KCrit +25 | Luck +45"),
            ("🟠 Hỗn Độn Cổ Huyết",      "ATK x2 | HP x2 | DEF +50% | Luck +100"),
            ("🟠 Thái Cổ Thần Huyết",    "ATK x2.3 | HP x2.3 | DEF +80% | SPD +20% | Crit +20 | Luck +160"),
        ],
        [
            ("✨ THÁNH PHẨM / VÔ THƯỢNG", "Transcendent — Cực kỳ hiếm"),
            ("✨ Nguyên Thủy Ma Thần Huyết",   "ATK x3 | HP x2.8 | DEF x2.2 | SPD +40% | Crit +28 | Luck +250"),
            ("🌟 Khai Thiên Hỗn Nguyên Huyết", "ATK x4 | HP x3.5 | DEF x2.8 | SPD +60% | Crit +38 | Né +25% | Luck +400"),
            ("📊 Tỉ Lệ Roll", "Phàm: 25% | Hạ: 22% | Trung: 16%\nThượng: 14% | Địa: 10% | Thiên: 8%\nThánh: 4% | Vô Thượng: 1%"),
            ("💡 Tip", "Né tránh giúp tránh hoàn toàn 1 đòn PvP\nKháng Crit giảm damage bị bạo kích\nCàng hiếm → bonus Luck/Crit càng cao"),
        ],
    ]
}

WIKI_LINHCAN = {
    "title": "🌱 CẨM NANG LINH CĂN",
    "pages": [
        [
            ("⬜ PHẾ & HẠ PHẨM", "Thường gặp nhất"),
            ("⬜ Phế Linh Căn",           "EXP x0.5 — Khó tu luyện nhất"),
            ("⬜ Ngũ Hành Tạp Linh Căn",  "EXP x0.6"),
            ("🟢 Tứ Hệ Linh Căn",        "EXP x0.8"),
            ("🟢 Tam Hệ Linh Căn",        "EXP x1.0 | ATK +3%"),
            ("🔵 Song Hệ Linh Căn",       "EXP x1.1 | ATK +8% | Luck +5"),
        ],
        [
            ("🟣 ĐỊA PHẨM — Bắt đầu mạnh", "Epic — Hiếm"),
            ("🟣 Đơn Hệ Linh Căn",        "EXP x1.2 | ATK +10% | DEF +5%"),
            ("🟣 Dị Linh Căn (Lôi)",      "EXP x1.4 | ATK +15% | Crit +12 | Luck +10"),
            ("🟣 Dị Linh Căn (Băng)",     "EXP x1.4 | ATK +10% | DEF +18% | HP +10%"),
            ("🟣 Dị Linh Căn (Phong)",    "EXP x1.4 | ATK +10% | SPD +22% | Crit +8"),
            ("🟣 Dị Linh Căn (Hỏa)",      "EXP x1.45 | ATK +20% | Crit +15 | Luck +8"),
        ],
        [
            ("🟡 THIÊN PHẨM", "Legendary — Siêu hiếm, cực kỳ lợi thế"),
            ("🟡 Thiên Linh Căn",         "EXP x1.5 | ATK +25% | DEF +10% | Luck +30"),
            ("🟡 Cửu Biến Dị Căn",        "EXP x1.6 | ATK +30% | SPD +10% | Crit +15 | Luck +25"),
            ("🔴 Âm Dương Hỗn Độn Căn",   "EXP x1.8 | ATK +50% | DEF +20% | HP +20% | Luck +60"),
            ("🔴 Hỗn Độn Linh Căn",       "EXP x2.0 | ATK +60% | Crit +20 | Luck +80"),
        ],
        [
            ("✨ THẦN & VÔ THƯỢNG PHẨM", "Divine/Transcendent — Cực kỳ cực kỳ hiếm"),
            ("✨ Vô Thủy Linh Căn",         "EXP x2.5 | ATK +90% | DEF +30% | HP +30% | Luck +120"),
            ("✨ Thái Cổ Hỗn Nguyên Căn",   "EXP x3.0 | ATK x2.2 | DEF +40% | HP +40% | SPD +20% | Crit +25 | Luck +180"),
            ("🌟 Vạn Đạo Quy Nhất Căn",    "EXP x4.0 | ATK x2.8 | DEF +60% | HP +60% | SPD +30% | Crit +30 | Luck +300"),
            ("🌟 Khai Thiên Thần Căn",      "EXP x5.0 | ATK x3.5 | DEF x2 | HP x2 | SPD +50% | Crit +40 | Luck +500"),
            ("📊 Tỉ Lệ Roll", "Phế: 5% | Ngũ: 14% | Tứ: 18% | Tam: 16%\nSong: 12% | Đơn: 8% | Dị×4: 15%\nThiên: 2% | Cửu: 1.5% | Hỗn: 0.8%\nVô/Thái: 0.4% | Vạn/Khai: 0.1%"),
        ],
    ]
}

WIKI_MENHCACH = {
    "title": "🌟 CẨM NANG MỆNH CÁCH",
    "pages": [
        [
            ("🔘 1. THIÊN SÁT CÔ TINH", "Không có hiệu ứng đặc biệt"),
            ("🔘 2. PHÁO HÔI", "DEF +10% | HP +10% | Phúc Duyên ±20"),
            ("🔘 3. NGƯỜI QUA ĐƯỜNG GIÁP", "DEF +10% | HP +10% | Phúc Duyên ±20"),
            ("🔘 4. NHÂN VẬT PHỤ", "DEF +10% | HP +10% | Phúc Duyên ±20"),
            ("🔵 5. ĐÀO HOA KIẾP", "HP +50% | Phúc Duyên ±50"),
            ("🟣 6. KẺ PHẢN DIỆN BỨC CÁCH", "ATK +50% | Crit +15% | Hút máu +5%"),
        ],
        [
            ("🟢 7. THIÊN MỆNH CHI TỬ", "EXP +10% | Phúc Duyên +30"),
            ("🟢 8. KIM LAN KẾT NGHĨA", "HP +20% | DEF +15%"),
            ("🟣 9. NGHỊCH THIÊN CẢI MỆNH", "ATK +30% | Crit +10% | EXP +5%"),
            ("🟡 10. THIÊN KIÊU CHI MỆNH", "ATK +40% | DEF +30% | HP +40%"),
            ("🟡 11. VẠN CỔ ĐỘC TÔN", "ATK +60% | Crit +20% | Phúc Duyên +50"),
            ("🔴 12. HỒNG HOANG THỦY TỔ", "ATK +80% | HP +80% | DEF +50% | Phúc Duyên +100"),
        ],
        [
            ("📊 Phẩm Cấp Mệnh Cách", ""),
            ("🔘 Phàm Phẩm", "Thiên Sát, Pháo Hôi, Người Qua Đường, Nhân Vật Phụ"),
            ("🔵 Hạ Phẩm", "Đào Hoa Kiếp, Thiên Mệnh Chi Tử, Kim Lan Kết Nghĩa"),
            ("🟣 Trung Phẩm", "Kẻ Phản Diện Bức Cách, Nghịch Thiên Cải Mệnh"),
            ("🟡 Thượng Phẩm", "Thiên Kiêu Chi Mệnh, Vạn Cổ Độc Tôn"),
            ("🔴 Thánh Phẩm", "Hồng Hoang Thủy Tổ"),
        ],
    ]
}

WIKI_VATPHAM = {
    "title": "💊 CẨM NANG VẬT PHẨM",
    "pages": [
        [
            ("Luyện Khí Đan", "💰 500 LT | +1,000 EXP"),
            ("Trúc Cơ Đan",   "💰 5,000 LT | +10,000 EXP"),
            ("Kim Đan",        "💰 50,000 LT | +100,000 EXP"),
            ("Tích Tụ Đan",   "💰 2,000 LT | +50% EXP Rate trong 1 giờ"),
            ("Phục Tinh Đan",  "💰 3,000 LT | +50 Thể Lực"),
            ("Đại Hoàn Đan",  "💰 8,000 LT | +200 Thể Lực"),
        ],
        [
            ("Đột Phá Đan",    "💰 20,000 LT | +20% tỉ lệ đột phá"),
            ("Trường Sinh Đan","💰 100,000 LT | +5,000,000 EXP"),
            ("Thần Hóa Đan",  "💰 500,000 LT | +50,000,000 EXP"),
            ("Hồng Ngọc",      "💰 5,000 LT | ATK Ngọc +5%"),
            ("Lam Ngọc",       "💰 5,000 LT | DEF Ngọc +5%"),
            ("Lục Ngọc",       "💰 5,000 LT | HP Ngọc +5%"),
        ],
        [
            ("Thần Ngọc",      "💰 50,000 LT | ATK +15% | DEF +10%"),
            ("Sát Tiên Kiếm",  "💰 10,000 LT | ATK cơ bản +500"),
            ("Thần Long Kiếm", "💰 80,000 LT | ATK cơ bản +2,000"),
            ("Khai Thiên Phủ", "💰 500,000 LT | ATK cơ bản +8,000"),
            ("Tinh Hồn Lệnh",  "💰 60,000 LT | ATK +600 | DEF +400"),
            ("💡 Cách Mua", "Dùng ,tl shop để xem cửa hàng\n,tl buy [item_id] [số lượng]"),
        ],
    ]
}

WIKI_BICANH = {
    "title": "🗺️ CẨM NANG BÍ CẢNH",
    "pages": [
        [
            ("🗺️ Cách Thám Hiểm", "`,tl bicanh di [tên_khu]` — Vào bí cảnh\n`,tl bicanh ve` — Trở về nhận thưởng"),
            ("Phân Loại Khu Vực", ""),
            ("🌿 Rừng Nguyên Thủy", "Cảnh giới thấp | Thưởng thấp | An toàn"),
            ("🏔️ Núi Tuyết Vạn Năm", "Yêu cầu cảnh giới Trúc Cơ+"),
            ("🌋 Núi Lửa Tà Diệm", "Yêu cầu Kim Đan+ | Thưởng cao"),
            ("🌊 Vực Sâu Huyền Bí", "Yêu cầu Nguyên Anh+ | Thưởng rất cao"),
        ],
        [
            ("🏜️ Sa Mạc Linh Hồn", "Yêu cầu Hóa Thần+ | Thưởng cực cao"),
            ("🌌 Hư Không Thánh Địa", "Yêu cầu Luyện Hư+ | Thưởng Thiên Phẩm"),
            ("⚡ Cơ Chế Thưởng", "Thời gian thám hiểm → EXP + LT + vật phẩm\nThám hiểm lâu hơn = thưởng cao hơn"),
            ("💀 Rủi Ro", "Khu vực cao có thể gặp Ma Thú\n→ Mất TL hoặc bị thương\n→ Cần TL đủ để thám hiểm"),
            ("🔋 Thể Lực", "Mỗi lần thám hiểm tốn TL\nTL cạn → Không thể tiếp tục"),
            ("💡 Tip", "Đi `,tl bicanh` để xem danh sách khu vực\nChọn khu phù hợp cảnh giới để hiệu quả nhất"),
        ],
    ]
}

WIKI_CONGPHAP = {
    "title": "📜 CẨM NANG CÔNG PHÁP",
    "pages": [
        [
            ("📜 Công Pháp là gì?", "Võ học mà nhân vật tu luyện\nẢnh hưởng đến stat và kỹ năng chiến đấu"),
            ("🔥 Hỏa Hệ Công Pháp", "ATK +20% | Crit +10%\nPhù hợp: Tấn công mạnh"),
            ("❄️ Băng Hệ Công Pháp", "SPD -10% | DEF +30% | Làm chậm địch\nPhù hợp: Phòng thủ"),
            ("⚡ Lôi Hệ Công Pháp", "ATK +15% | SPD +25% | Crit +15%\nPhù hợp: Tốc chiến"),
            ("🌿 Mộc Hệ Công Pháp", "HP +30% | Hồi máu +5%/turn\nPhù hợp: Trường thọ"),
            ("🌊 Thủy Hệ Công Pháp", "DEF +20% | HP +20% | Phản đòn\nPhù hợp: Cân bằng"),
        ],
        [
            ("🌪️ Phong Hệ Công Pháp", "SPD +40% | Né tránh +15%\nPhù hợp: Né đòn, tốc độ"),
            ("🌑 Âm Hệ Công Pháp", "Crit +25% | Hút máu +10%\nPhù hợp: Sát thương crit"),
            ("☀️ Dương Hệ Công Pháp", "ATK +30% | Miễn dịch điều kiện bất lợi\nPhù hợp: Ổn định"),
            ("🔮 Hỗn Độn Công Pháp", "Tất cả stat +10% | EXP +5%\nPhù hợp: Toàn năng — Rất hiếm"),
            ("💡 Cách Học", "Dùng: ,tl skill learn [tên]\nXem danh sách: ,tl skill list"),
        ],
    ]
}

WIKI_LUYENDAN = {
    "title": "⚗️ CẨM NANG LUYỆN ĐAN",
    "pages": [
        [
            ("⚗️ Luyện Đan là gì?", "Chế tạo đan dược từ nguyên liệu\n→ Hiệu quả hơn mua shop + kiếm thêm thu nhập"),
            ("🌿 Nguyên Liệu Cơ Bản", "Linh Thảo (Tier 1) — Rẻ, dễ kiếm\nLinh Hoa (Tier 2) — Trung bình\nCổ Dược (Tier 3) — Hiếm\nThần Thảo (Tier 4) — Cực hiếm"),
            ("📋 Công Thức Luyện Khí Đan", "2x Linh Thảo → 1 Luyện Khí Đan\nTỉ lệ thành công: 90%"),
            ("📋 Công Thức Trúc Cơ Đan", "2x Linh Hoa + 1x Linh Thảo → 1 Trúc Cơ Đan\nTỉ lệ thành công: 70%"),
            ("📋 Công Thức Kim Đan", "2x Cổ Dược + 1x Linh Hoa → 1 Kim Đan\nTỉ lệ thành công: 50%"),
            ("📋 Công Thức Đan Đặc Biệt", "Thần Thảo x3 → Đột Phá Đan\nTỉ lệ thành công: 30%"),
        ],
        [
            ("🏆 Cấp Độ Đan Sư", "Cấp 1: Đan Tử | Cấp 2: Đan Sĩ\nCấp 3: Đan Sư | Cấp 4: Đan Vương\nCấp 5: Đan Đế | Cấp 6: Đan Thần"),
            ("📈 EXP Đan Sư", "Luyện đan thành công → nhận EXP Đan Sư\nLên cấp → tỉ lệ thành công tăng"),
            ("⚠️ Thất Bại", "Thất bại → mất nguyên liệu\nCấp Đan Sư cao → ít thất bại hơn"),
            ("💡 Cách Luyện", "Dùng: ,tl luyendan [công_thức]\nXem CT: ,tl luyendan list\nXem EXP: ,tl luyendan info"),
        ],
    ]
}

WIKI_LUYENKHI = {
    "title": "🔨 CẨM NANG LUYỆN KHÍ (RÈN)",
    "pages": [
        [
            ("🔨 Luyện Khí là gì?", "Nâng cấp / Rèn trang bị từ nguyên liệu\nTăng ATK, DEF, HP cho vũ khí và giáp"),
            ("⚒️ Nguyên Liệu Rèn", "Thiết Khoáng (Tier 1) — Phổ thông\nLinh Thép (Tier 2) — Hiếm\nThần Kim (Tier 3) — Cực hiếm\nHỗn Độn Tinh (Tier 4) — Thần Phẩm"),
            ("📈 Cường Hóa", "Cường hóa +1 đến +10: dùng nguyên liệu thường\nCường hóa +11 đến +20: cần nguyên liệu hiếm\n+21 trở lên: nguyên liệu Thần Phẩm"),
            ("⚠️ Rủi Ro", "+1 đến +5: 100% thành công\n+6 đến +10: 70% | +11 đến +15: 50%\n+16 trở lên: 30% — Thất bại giảm 1 cấp!"),
            ("🛡️ Phong Ấn Rèn", "Mua Đá Bảo Hộ để không mất cấp khi thất bại\nGiá: 50,000 LT / viên"),
            ("💡 Cách Rèn", "Dùng: ,tl cuonghoa [weapon/armor/...]\nXem trang bị hiện tại: ,tl gear"),
        ],
        [
            ("🏅 Cấp +1 đến +5", "ATK/DEF tăng 10% mỗi cấp"),
            ("🥇 Cấp +6 đến +10", "ATK/DEF tăng 15% mỗi cấp"),
            ("💎 Cấp +11 đến +15", "ATK/DEF tăng 20% mỗi cấp | Thêm hiệu ứng phụ"),
            ("🌟 Cấp +16 đến +20", "ATK/DEF tăng 25% mỗi cấp | Phát sáng Linh Khí"),
            ("🔥 Cấp +21 trở lên", "Biến đổi hình dạng | Stat khủng | Cực hiếm"),
            ("💡 Tip", "Nên cường hóa đến +10 trước\nSau đó dùng Đá Bảo Hộ để lên cao hơn"),
        ],
    ]
}

WIKI_TRANGBI = {
    "title": "🛡️ HƯỚNG DẪN TRANG BỊ",
    "pages": [
        [
            ("📦 Các Slot Trang Bị", "⚔️ Vũ Khí (weapon) — ATK chính\n🛡️ Giáp (armor) — DEF chính\n👒 Mũ (hat) — DEF phụ\n📿 Vòng Cổ (necklace) — ATK + DEF\n🧤 Găng Tay (gloves) — ATK phụ\n👟 Giày (boots) — SPD"),
            ("🔮 Pháp Bảo (phapbao)", "Trang bị đặc biệt — Hiệu ứng mạnh nhất\nRất hiếm — Chỉ từ Boss hoặc Shop VIP"),
            ("💎 Ngọc Khảm", "Khảm vào trang bị để tăng stat phần trăm\nMỗi trang bị có thể khảm 1-3 ngọc"),
            ("⚡ Cường Hóa", "Xem wiki luyenkhi để biết cách rèn\nCường hóa cao → trang bị mạnh hơn rất nhiều"),
            ("💡 Cách Trang Bị", "Dùng: ,tl equip [item_id]\nTháo: ,tl unequip [slot]\nXem trang bị: ,tl gear"),
        ],
        [
            ("🏆 Độ Hiếm Trang Bị", "🔘 Thường | 🔵 Hiếm | 🟣 Sử Thi\n🟡 Huyền Thoại | 🔴 Thần Thoại"),
            ("📊 Nguồn Kiếm Trang Bị", "Shop: Mua bằng LT\nDrop Boss: Tỉ lệ thấp nhưng chất lượng cao\nLuyện Đan / Craft: Tự chế"),
            ("⚔️ Stat Trang Bị", "base_atk: ATK cơ bản của vũ khí\nbase_def: DEF cơ bản của giáp\nbase_spd: SPD cơ bản của giày"),
            ("🔮 Hiệu Ứng Đặc Biệt", "Một số trang bị có hiệu ứng riêng:\n• Tinh Hồn Lệnh: Buff Phúc Duyên\n• Bàn Cổ Thần Ấn: ATK + DEF cực cao"),
            ("💡 Tip Build", "Tấn công: Vũ Khí + Hồng Ngọc + Cường Hóa cao\nPhòng thủ: Giáp + Lam Ngọc + Lục Ngọc\nCân bằng: Tinh Hồn Lệnh + Thần Ngọc"),
        ],
    ]
}

WIKI_DATA = {
    "canhgioi": WIKI_CANHGIOI,
    "chuyensinh": WIKI_CHUYENSINH,
    "thechat":  WIKI_THECHAT,
    "huyetmach":WIKI_HUYETMACH,
    "linhcan":  WIKI_LINHCAN,
    "menhcach": WIKI_MENHCACH,
    "vatpham":  WIKI_VATPHAM,
    "bicanh":   WIKI_BICANH,
    "congphap": WIKI_CONGPHAP,
    "luyendan": WIKI_LUYENDAN,
    "luyenkhi": WIKI_LUYENKHI,
    "trangbi":  WIKI_TRANGBI,
}

WIKI_COLORS = {
    "canhgioi":  0x9C27B0,
    "chuyensinh":0xFFD700,
    "thechat":   0xFF5722,
    "huyetmach": 0xF44336,
    "linhcan":   0x4CAF50,
    "menhcach":  0xFFD700,
    "vatpham":   0x2196F3,
    "bicanh":    0x00BCD4,
    "congphap":  0x795548,
    "luyendan":  0xFF9800,
    "luyenkhi":  0x607D8B,
    "trangbi":   0x3F51B5,
}

TOPIC_LIST = (
    "1. `canhgioi`   — Cảnh giới & EXP\n"
    "2. `chuyensinh` — Chuyển Sinh (sau cảnh giới max)\n"
    "3. `thechat`    — Thể chất & Thời gian tu\n"
    "4. `huyetmach`  — Huyết mạch & Tỉ lệ bạo kích\n"
    "5. `linhcan`    — Linh căn & Hệ số EXP\n"
    "6. `menhcach`   — Các loại mệnh cách\n"
    "7. `vatpham`    — Các loại đan dược & trang bị\n"
    "8. `bicanh`     — Cơ chế thám hiểm\n"
    "9. `congphap`   — Hệ thống công pháp\n"
    "10. `luyendan`  — Hệ thống luyện đan\n"
    "11. `luyenkhi`  — Hệ thống luyện khí (Rèn)\n"
    "12. `trangbi`   — Hướng dẫn trang bị"
)

# ══ COG ═════════════════════════════════════════════════════

class Wiki(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="wiki", aliases=["w"])
    async def wiki(self, ctx, loai: str = None, trang: int = 1):
        """📖 Tra cứu wiki tu tiên. Dùng: ,tl wiki [loại] [trang]"""

        # Không có loại → hiện menu
        if not loai:
            embed = discord.Embed(
                title="📖 WIKI TU TIÊN 📖",
                description=(
                    "Sử dụng lệnh: `,tl wiki [loại] [trang]`\n\n"
                    "**Các loại tra cứu:**\n"
                    f"{TOPIC_LIST}"
                ),
                color=0xFFD700
            )
            embed.set_footer(text="Ví dụ: ,tl wiki thechat  •  ,tl wiki linhcan 2")
            await ctx.send(embed=embed)
            return

        loai = loai.lower()
        if loai not in WIKI_DATA:
            embed = discord.Embed(
                title="❓ Không tìm thấy wiki",
                description=(
                    f"Loại `{loai}` không tồn tại.\n\n"
                    f"**Các loại hợp lệ:**\n{TOPIC_LIST}"
                ),
                color=0xF44336
            )
            await ctx.send(embed=embed)
            return

        data   = WIKI_DATA[loai]
        pages  = data["pages"]
        trang  = max(1, min(trang, len(pages)))
        color  = WIKI_COLORS.get(loai, 0xFFD700)
        fields = pages[trang - 1]

        embed = discord.Embed(
            title=f"{data['title']} (Trang {trang}/{len(pages)})",
            color=color
        )
        for name, value in fields:
            if value:
                embed.add_field(name=name, value=value, inline=False)
            else:
                # Separator field (no value)
                embed.add_field(name=f"── {name} ──", value="\u200b", inline=False)

        footer_parts = []
        if trang < len(pages):
            footer_parts.append(f",tl wiki {loai} {trang+1} → Trang tiếp")
        if trang > 1:
            footer_parts.append(f",tl wiki {loai} {trang-1} → Trang trước")
        footer_parts.append("Tu Tiên Bot v3")
        embed.set_footer(text="  •  ".join(footer_parts))

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Wiki(bot))

"""utils/fish_data.py - Dữ liệu cho Hệ Thống Câu Cá v6.0+

Chứa: BAITS (mồi câu), MAPS (bản đồ/vùng câu), FISH (các loại cá),
FISH_RODS (cần câu), FISH_BOATS (thuyền), WEATHER (thời tiết),
FISH_QUESTS (nhiệm vụ hàng ngày), FISH_ADVENTURE (nhiệm vụ phiêu lưu),
FISH_TROPHIES (thành tựu), FISH_BOSS (boss thế giới câu cá).
"""
import random

# ══ MỒI CÂU ══════════════════════════════════════════════════
BAITS = {
    "bait_bot":        {"name":"🪱 Mồi Bột",            "price":100,     "bite_bonus":0.05, "luck_bonus":0,    "big_bonus":0,    "desc":"Tăng 5% cơ hội dính cá."},
    "bait_trung":      {"name":"🩸 Mồi Trùng Huyết",     "price":500,     "bite_bonus":0.10, "luck_bonus":0.05, "big_bonus":0,    "desc":"Tăng 10% dính cá, 5% may mắn."},
    "bait_tom":        {"name":"🦐 Mồi Tôm Tươi",        "price":2000,    "bite_bonus":0.05, "luck_bonus":0,    "big_bonus":0.20, "desc":"Tăng 20% tỉ lệ gặp cá lớn (Big/Giant)."},
    "bait_gia":        {"name":"🎣 Mồi Giả Chuyên Nghiệp","price":50000,  "bite_bonus":0.08, "luck_bonus":0.03, "big_bonus":0.05, "desc":"Mồi nhựa, dùng vĩnh viễn.", "permanent": True},
    "bait_bi_truyen":  {"name":"✨ Thính Bí Truyền",      "price":10000,  "bite_bonus":0.15, "luck_bonus":0.10, "big_bonus":0.10, "desc":"Thu hút cá hiếm cực mạnh."},
    "bait_bang":       {"name":"❄️ Phấn Băng Hà",         "price":25000,  "bite_bonus":0.10, "luck_bonus":0.10, "big_bonus":0,    "desc":"Hiệu quả đặc biệt ở Biển Băng Tuyết.", "map_bonus":"bien_bang"},
    "bait_lam_ngoc":   {"name":"💠 Lam Ngọc Tinh",        "price":50000,  "bite_bonus":0.10, "luck_bonus":0.12, "big_bonus":0,    "desc":"Thu hút cá vùng Biển Ngọc Thần.", "map_bonus":"bien_ngoc"},
    "bait_nham":       {"name":"🌋 Hỏa Nham Mồi",         "price":30000,  "bite_bonus":0.10, "luck_bonus":0.10, "big_bonus":0,    "desc":"Kích thích cá lửa trồi lên cắn câu.", "map_bonus":"bien_lua"},
    "bait_than":       {"name":"⛩️ Ngọc Thánh Hương",     "price":500000, "bite_bonus":0.20, "luck_bonus":0.20, "big_bonus":0.15, "desc":"Hương thơm thánh khiết, thu hút cá thần."},
    "bait_thien_la":   {"name":"🌌 Thiên La Địa Võng",    "price":1000000,"bite_bonus":0.30, "luck_bonus":0.25, "big_bonus":0.25, "desc":"Bủa vây cả vùng, tỉ lệ câu tăng vọt."},
}

# ══ THUYỀN ════════════════════════════════════════════════════
FISH_BOATS = {
    "boat_default": {"name":"🛶 Thúng Câu Nhỏ",         "price":0,                "capacity":200,       "desc":"Thuyền khởi đầu.", "hidden": True},
    "boat1":        {"name":"🛶 Thúng Câu Nhỏ",         "price":0,                "capacity":200,       "desc":"Thuyền khởi đầu."},
    "boat2":        {"name":"🚣 Thuyền Gỗ Trống",       "price":100_000,          "capacity":1_000,     "desc":"Thuyền gỗ chắc chắn hơn."},
    "boat3":        {"name":"⛵ Thuyền Động Cơ Nhỏ",     "price":1_000_000,        "capacity":3_000,     "desc":"Có động cơ, đi xa hơn."},
    "boat4":        {"name":"🚤 Thuyền Máy Lớn",         "price":5_000_000,        "capacity":10_000,    "desc":"Sức chứa lớn hơn hẳn."},
    "boat5":        {"name":"🛥️ Tàu Ráp Lưới",          "price":20_000_000,       "capacity":30_000,    "desc":"Trang bị lưới đánh bắt."},
    "boat6":        {"name":"🚢 Tàu Viễn Dương",         "price":100_000_000,      "capacity":100_000,   "desc":"Có thể đi xa bờ."},
    "boat7":        {"name":"🛳️ Tàu Đánh Cá Siêu Cấp",  "price":500_000_000,      "capacity":500_000,   "desc":"Trang bị hiện đại, sức chứa khủng."},
    "boat8":        {"name":"🚀 Du Thuyền Siêu Tốc",     "price":2_000_000_000,    "hai_tran":1,  "capacity":2_000_000,   "desc":"Tốc độ vượt trội."},
    "boat9":        {"name":"🛸 Siêu Tàu Vũ Trụ",        "price":10_000_000_000,   "hai_tran":2,  "capacity":10_000_000,  "desc":"Công nghệ vượt thời đại."},
    "boat10":       {"name":"⚓ Chiến Hạm Đại Dương",    "price":30_000_000_000,   "hai_tran":5,  "capacity":50_000_000,  "desc":"Sức chứa khổng lồ."},
    "boat11":       {"name":"🏰 Pháo Đài Biển Sâu",      "price":100_000_000_000,  "hai_tran":10, "capacity":200_000_000, "desc":"Thuyền tối thượng của cần thủ."},
}

# ══ CẦN CÂU ═══════════════════════════════════════════════════
FISH_RODS = {
    "rod_default":  {"name":"🎣 Cần Câu Gỗ",            "price":0,                  "luck_mult":1,    "fish_bonus":0, "desc":"Cần câu khởi đầu.", "hidden": True},
    "rod1":         {"name":"🎋 Cần Tre Thường",        "price":5_000,              "luck_mult":1,    "fish_bonus":0, "desc":"Cần câu cơ bản dành cho người mới."},
    "rod2":         {"name":"🪝 Cần Thép",               "price":50_000,             "luck_mult":1.05, "fish_bonus":0, "desc":"Chắc chắn hơn cần tre."},
    "rod3":         {"name":"🥇 Cần Vàng",                "price":200_000,            "luck_mult":1.1,  "fish_bonus":0, "desc":"Mạ vàng sang trọng, tăng may mắn."},
    "rod4":         {"name":"⚡ Cần Thần",                "price":1_000_000,          "luck_mult":1.15, "fish_bonus":0, "desc":"Mang sức mạnh thần bí."},
    "rod5":         {"name":"💚 Cần Ngọc Lục Bảo",        "price":5_000_000,          "luck_mult":1.2,  "fish_bonus":0, "desc":"Khảm ngọc lục bảo quý hiếm."},
    "rod6":         {"name":"🐲 Cần Rồng",                "price":15_000_000,         "luck_mult":1.3,  "fish_bonus":1, "desc":"Mang linh khí của loài rồng."},
    "rod7":         {"name":"🦴 Cần Long Cốt",            "price":50_000_000,         "luck_mult":1.6,  "fish_bonus":2, "desc":"Chế tác từ xương rồng cổ đại."},
    "rod8":         {"name":"⚫ Cần Huyền Thiết",         "price":150_000_000,        "luck_mult":1.8,  "fish_bonus":2, "desc":"Rèn từ huyền thiết quý hiếm."},
    "rod9":         {"name":"🔮 Cần Linh Thạch",          "price":400_000_000,        "luck_mult":2,    "fish_bonus":3, "desc":"Hấp thụ linh khí từ linh thạch."},
    "rod10":        {"name":"⭐ Cần Thiên Tinh",          "price":1_000_000_000,      "luck_mult":2.2,  "fish_bonus":3, "desc":"Tinh hoa hội tụ từ trời cao."},
    "rod11":        {"name":"🏺 Cần Thái Cổ",             "price":3_000_000_000,      "luck_mult":1.8,  "fish_bonus":1, "desc":"Di vật sót lại từ thời thái cổ."},
    "rod12":        {"name":"🐉 Cần Chân Long",           "price":6_000_000_000,      "luck_mult":1.9,  "fish_bonus":1, "desc":"Mang sức mạnh của chân long."},
    "rod13":        {"name":"👼 Cần Thần Linh",           "price":12_000_000_000,     "luck_mult":2,    "fish_bonus":1, "desc":"Được thần linh ban phước."},
    "rod14":        {"name":"☯️ Cần Thiên Đạo",           "price":25_000_000_000,     "hai_tran":1,  "luck_mult":2.1,  "fish_bonus":2, "desc":"Thấu hiểu thiên đạo vạn vật."},
    "rod15":        {"name":"🔯 Cần Vận Mệnh",            "price":60_000_000_000,     "hai_tran":2,  "luck_mult":2.2,  "fish_bonus":2, "desc":"Nắm giữ vận mệnh câu cá."},
    "rod16":        {"name":"♾️ Cần Luân Hồi",            "price":150_000_000_000,    "hai_tran":3,  "luck_mult":2.3,  "fish_bonus":2, "desc":"Xoay chuyển vòng luân hồi."},
    "rod17":        {"name":"🌀 Cần Hỗn Độn",             "price":300_000_000_000,    "hai_tran":5,  "luck_mult":2.4,  "fish_bonus":2, "desc":"Sức mạnh nguyên thủy từ hỗn độn."},
    "rod18":        {"name":"🕳️ Cần Hư Không",            "price":700_000_000_000,    "hai_tran":10, "luck_mult":2.45, "fish_bonus":2, "desc":"Triệu hồi sức mạnh từ cõi hư không."},
    "rod19":        {"name":"🌌 Cần Nguyên Sơ",           "price":1_500_000_000_000,  "hai_tran":20, "luck_mult":2.48, "fish_bonus":2, "desc":"Mang sức mạnh nguyên sơ tối thượng."},
    "rod20":        {"name":"🌠 Cần Vạn Giới",            "price":8_000_000_000_000,  "hai_tran":50, "luck_mult":2.5,  "fish_bonus":2, "desc":"Thống lĩnh vạn giới câu cá."},
    "rod_vip1":     {"name":"👑 Cần Ngư Tôn",             "price":0,                  "luck_mult":2.2,  "fish_bonus":2, "desc":"Chỉ tặng khi đăng ký VIP lần đầu.", "vip_only": True},
    "rod_gacha_ss": {"name":"🔱 Hải Vương Chân Khí Cần",  "price":0,                  "luck_mult":3,    "fish_bonus":3, "desc":"Cần câu huyền thoại, chỉ có được qua Gacha.", "gacha_only": True},
}

# ══ BẢN ĐỒ / VÙNG CÂU ════════════════════════════════════════
MAPS = {
    # ── Trang 1/2 ──────────────────────────────────────────────
    "ho":          {"name":"🏞️ Hồ Nước Ngọt",      "req":"Cơ bản",        "fish_pool":"common",    "desc":"Khu vực cơ bản, yên tĩnh và đầy cá thường."},
    "song":        {"name":"🌿 Sông Amazon",         "req":"Cần Ngọc Lục Bảo","fish_pool":"uncommon", "desc":"Dòng sông hung dữ, nơi sinh sống của cá lớn."},
    "bien":        {"name":"🌊 Biển Khơi",           "req":"Cần Thiên Tinh", "fish_pool":"uncommon",  "desc":"Vùng biển rộng lớn, sóng to gió lớn."},
    "dam_lay":     {"name":"🌑 Đầm Lầy Cổ Đại",     "req":"Cần Huyền Thiết","fish_pool":"rare",      "desc":"Vùng đầm lầy huyền bí, cây cổ thụ ngàn năm. Cá kỳ lạ ẩn mình."},
    "bang_tuyet":  {"name":"❄️ Biển Băng Tuyết",    "req":"Cần Linh Thạch", "fish_pool":"rare",      "desc":"Vùng cực bắc giá lạnh, cá băng cực hiếm sinh sống."},
    "nham_thach":  {"name":"🌋 Hồ Nham Thạch",      "req":"Cần Thái Cổ",   "fish_pool":"epic",      "desc":"Miệng núi lửa còn âm ỉ. Cá lửa sống trong điều kiện khắc nghiệt."},
    # ── Trang 2/2 ──────────────────────────────────────────────
    "vuc":         {"name":"🕳️ Vực Sâu Tối Tăm",   "req":"Cần Thiên Đạo", "fish_pool":"epic",      "desc":"Nơi ánh sáng không thể chạm tới. Cá quỷ cổ đại sinh sống."},
    "ngoc_bien":   {"name":"💠 Biển Ngọc Thần",     "req":"Cần Thần Linh", "fish_pool":"epic",      "desc":"Vùng biển phát ánh sáng ma mị xanh ngọc, chứa đựng cá thần."},
    "rung_ngap":   {"name":"🌴 Rừng Ngập Mặn",      "req":"Cần Chân Long", "fish_pool":"legendary", "desc":"Rừng ngập mặn nhiệt đới với hệ sinh thái phong phú bậc nhất."},
    "vu_tru":      {"name":"🌌 Biển Sao Vũ Trụ",    "req":"Cần Hư Không",  "fish_pool":"legendary", "desc":"Câu cá giữa ngân hà. Đặc sản: Hải Trân và cá siêu nhiên."},
    "than_than":   {"name":"⛩️ Thánh Thần Chi Vực", "req":"Cần Nguyên Sơ", "fish_pool":"mythic",    "desc":"Vùng biển thần thánh giữa cõi trời. Chỉ Ngư Tôn tột đỉnh mới câu được."},
    "long_cung":   {"name":"🐉 Long Cung Thủy Phủ", "req":"Thẻ VIP Đặc Quyền","fish_pool":"mythic", "desc":"Cung điện Long Vương. Đặc quyền VIP: Rơi Hải Trân cực cao & Bảo vật hiếm.", "vip_only": True},
}

# Thứ tự hiển thị bản đồ theo trang
MAP_PAGES = [
    ["ho", "song", "bien", "dam_lay", "bang_tuyet", "nham_thach"],  # Trang 1
    ["vuc", "ngoc_bien", "rung_ngap", "vu_tru", "than_than", "long_cung"],  # Trang 2
]

# ══ ĐỘ HIẾM ═══════════════════════════════════════════════════
RARITY = {
    "common":    {"emoji":"🐟", "name":"Thường",    "weight":50, "value_mult":1,   "min_kg":0.3, "max_kg":2},
    "uncommon":  {"emoji":"🐠", "name":"Khá Hiếm",  "weight":28, "value_mult":3,   "min_kg":1,   "max_kg":5},
    "rare":      {"emoji":"🐡", "name":"Hiếm",      "weight":13, "value_mult":10,  "min_kg":3,   "max_kg":15},
    "epic":      {"emoji":"🦑", "name":"Sử Thi",    "weight":6,  "value_mult":35,  "min_kg":8,   "max_kg":40},
    "legendary": {"emoji":"🐉", "name":"Huyền Thoại","weight":2.5,"value_mult":120, "min_kg":20,  "max_kg":120},
    "mythic":    {"emoji":"👑", "name":"Thần Thoại","weight":0.5,"value_mult":500, "min_kg":50,  "max_kg":500},
}

# Tên cá theo từng map / độ hiếm (rút gọn, lặp lại được nhân ID theo map)
FISH_NAMES = {
    "common":    ["Cá Trê Trắng","Cá Diếc Vàng","Cá Mè Hoa","Cá Trôi Đen","Cá Mè Trắng","Cá Trôi Trắng","Cá Rô Đồng","Cá Lóc"],
    "uncommon":  ["Cá Chình Đồng","Cá Koi Trắng","Cá Chép Nhật","Cá Hồng Vện","Cá Lăng Bạc"],
    "rare":      ["Cá Ma Hồ","Cá Kiếm Bạc","Cá Mặt Trăng","Cá Hổ Vằn"],
    "epic":      ["Cá Rồng Lửa","Bạch Tuộc Yêu","Cá Mập Băng","Cá Sấu Thần"],
    "legendary": ["Cá Voi Cổ Đại","Rồng Biển Sâu","Cá Phượng Hoàng Biển"],
    "mythic":    ["Long Vương Ngư","Hỗn Độn Cự Ngư","Thái Cổ Thần Long"],
}

def fish_base_price(rarity: str) -> int:
    """Giá FishCoin cơ bản / kg theo độ hiếm."""
    base = {"common":50,"uncommon":150,"rare":500,"epic":2000,"legendary":10000,"mythic":50000}
    return base.get(rarity, 50)


def roll_fish(map_id: str, bait_id: str = None, weather_bonus: float = 0):
    """
    Quay ngẫu nhiên 1 con cá khi câu, trả về dict:
    {fish_id, name, rarity, weight, value}
    fish_id format: "{map_id}:{rarity_short}{index}" để định danh duy nhất theo map.
    """
    pool_default = MAPS.get(map_id, {}).get("fish_pool", "common")
    bait = BAITS.get(bait_id, {}) if bait_id else {}
    luck_bonus = bait.get("luck_bonus", 0) + weather_bonus
    big_bonus = bait.get("big_bonus", 0)

    # Trọng số độ hiếm, may mắn từ mồi sẽ kéo xác suất lên các bậc hiếm hơn
    weights = {k: v["weight"] for k, v in RARITY.items()}
    if luck_bonus:
        # Giảm trọng số common, tăng dần các bậc hiếm hơn theo luck_bonus
        shift = min(0.9, luck_bonus)
        weights["common"] *= (1 - shift)
        for k in ("uncommon", "rare", "epic", "legendary", "mythic"):
            weights[k] *= (1 + shift * 2)

    rarities = list(weights.keys())
    wts = list(weights.values())
    rarity = random.choices(rarities, weights=wts, k=1)[0]

    names = FISH_NAMES.get(rarity, FISH_NAMES["common"])
    name = random.choice(names)
    idx = names.index(name)
    fish_id = f"{rarity[0]}{idx+1}{abs(hash(map_id)) % 9}"

    rconf = RARITY[rarity]
    min_kg, max_kg = rconf["min_kg"], rconf["max_kg"]
    if random.random() < big_bonus:
        weight = round(random.uniform(max_kg * 0.7, max_kg * 1.5), 1)
    else:
        weight = round(random.uniform(min_kg, max_kg), 1)

    value = int(weight * fish_base_price(rarity))
    return {
        "fish_id": fish_id, "name": name, "rarity": rarity,
        "emoji": rconf["emoji"], "weight": weight, "value": value,
    }


# ══ THỜI TIẾT ═════════════════════════════════════════════════
WEATHER_TYPES = [
    {"name":"Nắng Gắt",   "emoji":"☀️", "effect":"Tăng 10% tốc độ câu.",        "speed_bonus":0.10, "luck_bonus":0},
    {"name":"Mưa Phùn",   "emoji":"🌦️", "effect":"Tăng 15% tỉ lệ dính cá hiếm.", "speed_bonus":0,    "luck_bonus":0.15},
    {"name":"Âm U",       "emoji":"☁️", "effect":"Không có hiệu ứng đặc biệt.", "speed_bonus":0,    "luck_bonus":0},
    {"name":"Bão Nhẹ",    "emoji":"🌧️", "effect":"Giảm 10% tốc độ, tăng 20% may mắn.", "speed_bonus":-0.10,"luck_bonus":0.20},
    {"name":"Sương Mù",   "emoji":"🌫️", "effect":"Tăng 25% tỉ lệ gặp cá hiếm vào sáng sớm.", "speed_bonus":0,"luck_bonus":0.25},
    {"name":"Trăng Tròn", "emoji":"🌕", "effect":"Tăng mạnh tỉ lệ cá Huyền Thoại/Thần Thoại về đêm.", "speed_bonus":0,"luck_bonus":0.30},
]

def current_weather():
    """Thời tiết thay đổi mỗi 4 tiếng, dựa theo giờ UTC hiện tại."""
    import time
    slot = int(time.time() // (4 * 3600)) % len(WEATHER_TYPES)
    return WEATHER_TYPES[slot]


# ══ SỰ KIỆN THEO MÙA (theo tháng) ════════════════════════════
SEASONAL_EVENTS = {
    1:  {"name":"❄️ Băng Tuyết Khai Xuân", "desc":"Cá vùng băng xuất hiện nhiều hơn 50%.", "bonus":"Tăng 50% cá Biển Băng Tuyết."},
    2:  {"name":"🧧 Tết Ngư Phúc",          "desc":"Tỉ lệ rương đỏ may mắn tăng vọt.",     "bonus":"x2 tỉ lệ rương khi câu."},
    3:  {"name":"🌸 Xuân Hải Hoa",          "desc":"Cá Koi và cá cảnh xuất hiện nhiều.",   "bonus":"+30% tỉ lệ cá Koi/Chép."},
    4:  {"name":"🌧️ Mưa Ngâu Đầu Hạ",      "desc":"Mưa liên tục, cá hiếm dễ cắn câu hơn.", "bonus":"+20% tỉ lệ cá Hiếm."},
    5:  {"name":"🔥 Hỏa Nham Thức Tỉnh",    "desc":"Biển Hỏa Nham hoạt động mạnh.",        "bonus":"+40% cá Biển Hỏa Nham."},
    6:  {"name":"⛈️ Đại Ôn Kiếp",          "desc":"Biển nổi cơn thịnh nộ, Boss xuất hiện thường xuyên hơn và khỏe hơn!", "bonus":"Bonus Boss: x1.5 sát thương."},
    7:  {"name":"🌞 Đại Hạn Viêm Hạ",       "desc":"Nắng nóng cực điểm, cá lớn trồi lên mặt nước.", "bonus":"+25% tỉ lệ cá Big/Giant."},
    8:  {"name":"🌊 Triều Cường Bát Nguyệt", "desc":"Nước dâng cao mở ra vùng câu tạm thời.", "bonus":"Mở map ẩn 'Vực Xoáy' trong tháng."},
    9:  {"name":"🍁 Thu Phong Ngư Hội",     "desc":"Giải đấu câu cá mùa thu khởi tranh.",  "bonus":"x2 điểm Tournament."},
    10: {"name":"🎃 Vạn Thánh Hải Yêu",     "desc":"Cá yêu dị xuất hiện vào ban đêm.",     "bonus":"+30% cá Epic/Legendary ban đêm."},
    11: {"name":"🍂 Sương Giáng Tĩnh Hải",  "desc":"Biển lặng, dễ câu cá hiếm hơn.",       "bonus":"+15% tỉ lệ dính cá tất cả độ hiếm."},
    12: {"name":"🎄 Đông Chí Ngư Tiệc",     "desc":"Sự kiện cuối năm, quà tặng dồn dập.",  "bonus":"Đăng nhập đủ 7 ngày nhận Cần Ngư Tôn."},
}

def get_seasonal_event(month: int = None):
    import datetime
    m = month or datetime.datetime.now().month
    return SEASONAL_EVENTS.get(m, SEASONAL_EVENTS[6])


# ══ NHIỆM VỤ HÀNG NGÀY (CÂU CÁ) ═══════════════════════════════
FISH_DAILY_QUESTS = [
    {"id":"fish_cast_5",   "name":"🎣 Câu cá 5 lần",        "type":"fish_count",  "target":5,  "reward_coin":5000,   "reward_bait":("bait_bot",5)},
    {"id":"fish_sell_10",  "name":"💰 Bán 10 con cá",       "type":"fish_sell",   "target":10, "reward_coin":8000},
    {"id":"fish_rare_1",   "name":"🐡 Câu được 1 cá Hiếm",  "type":"fish_rare",   "target":1,  "reward_coin":15000, "reward_bait":("bait_tom",2)},
    {"id":"fish_boss_1",   "name":"🌊 Tham chiến Boss 1 lần","type":"fish_boss",  "target":1,  "reward_coin":10000},
]

# ══ NHIỆM VỤ PHIÊU LƯU ═══════════════════════════════════════
FISH_ADVENTURE = [
    {"id":"adv_1","name":"Ngư Dân Sơ Xuất",    "desc":"Câu được tổng cộng 10 con cá.",          "type":"total_fish",  "target":10,   "reward_coin":10000},
    {"id":"adv_2","name":"Ngư Thủ Tinh Anh",   "desc":"Câu được 1 con cá độ hiếm Hiếm trở lên.", "type":"rare_fish",   "target":1,    "reward_coin":30000},
    {"id":"adv_3","name":"Đấu Thủy Quái",      "desc":"Tham chiến Boss Thủy Quái 5 lần.",        "type":"boss_fight",  "target":5,    "reward_coin":80000, "reward_hai_tran":2},
    {"id":"adv_4","name":"Khai Thác Vực Sâu",  "desc":"Câu cá ở Biển Ngọc Thần hoặc Hỏa Nham 10 lần.", "type":"deep_fish","target":10,"reward_coin":150000,"reward_hai_tran":3},
    {"id":"adv_5","name":"Chạm Đến Huyền Thoại","desc":"Câu được 1 con cá Huyền Thoại trở lên.", "type":"legendary_fish","target":1, "reward_coin":500000,"reward_hai_tran":5},
]

# ══ THÀNH TỰU / TROPHY ════════════════════════════════════════
FISH_TROPHIES = [
    {"id":"t_first_fish",  "name":"🎣 Cần Thủ Tập Sự",  "desc":"Câu được con cá đầu tiên.",        "type":"total_fish",  "target":1},
    {"id":"t_100_fish",    "name":"🐟 Ngư Dân Chăm Chỉ", "desc":"Câu đủ 100 con cá.",               "type":"total_fish",  "target":100},
    {"id":"t_1000_fish",   "name":"🏆 Đại Sư Câu Cá",    "desc":"Câu đủ 1,000 con cá.",             "type":"total_fish",  "target":1000},
    {"id":"t_first_epic",  "name":"🦑 Thợ Săn Sử Thi",   "desc":"Câu được 1 cá độ hiếm Sử Thi.",    "type":"epic_fish",   "target":1},
    {"id":"t_first_myth",  "name":"👑 Ngư Vương",        "desc":"Câu được 1 cá Thần Thoại.",        "type":"mythic_fish", "target":1},
    {"id":"t_boss_10",     "name":"⚔️ Sát Thủ Thủy Quái","desc":"Đánh bại Boss 10 lần.",            "type":"boss_kill",   "target":10},
]

# ══ BOSS THẾ GIỚI (CÂU CÁ) ════════════════════════════════════
FISH_BOSS = {
    "id": "thuy_quai_vuong",
    "name": "🌊 Thủy Quái Vương",
    "hp": 5_000_000,
    "atk": 50_000,
    "reward_coin": 200_000,
    "reward_hai_tran": 5,
}

# ══ GIÁ THỊ TRƯỜNG (dao động theo ngày) ═══════════════════════
def market_price_today(rarity: str):
    """Giá cá hôm nay dao động ±20% so với giá cơ bản, theo ngày hiện tại (seed cố định/ngày)."""
    import time
    today = int(time.time() // 86400)
    rnd = random.Random(today * 31 + hash(rarity) % 1000)
    base = fish_base_price(rarity)
    mult = rnd.uniform(0.8, 1.2)
    return int(base * mult)

# ══ ĐẢO CÁ — NPC DATA ════════════════════════════════════════
ISLAND_NPCS = {
    "npc_newbie": {
        "name": "Ngư Dân Tập Sự",
        "emoji": "🔸",
        "desc": "Câu cá nhỏ ven bờ.",
        "price": 5_000_000,
        "income_per_hour": 500_000,
    },
    "npc_veteran": {
        "name": "Lão Ngư Lành Nghề",
        "emoji": "🔸",
        "desc": "Câu cá lớn ngoài khơi.",
        "price": 20_000_000,
        "income_per_hour": 4_000_000,
    },
    "npc_master": {
        "name": "Thánh Ngư Huyền Cổ",
        "emoji": "🔸",
        "desc": "Chuyên săn lùng thủy quái.",
        "price": 100_000_000,
        "income_per_hour": 22_250_000,
    },
}
ISLAND_NPC_MAX = 5  # tối đa mỗi loại

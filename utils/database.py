"""utils/database.py - Lớp Database (SQLite, async qua aiosqlite)

Cung cấp toàn bộ method mà các cog gọi qua self.bot.db.*:
  get_player, create_player, update_player,
  add_item, remove_item, get_item_count, get_inventory,
  equip_item, get_equipment,
  get_linhthu,
  get_quests, update_quest,
  get_streak, update_streak,
  get_tower, update_tower,
  add_boss_damage, get_boss_top,
  get_leaderboard,
  is_bot_admin, add_bot_admin, remove_bot_admin, list_bot_admins,
  execute, fetchone, fetchall (truy vấn SQL thô, dùng cho auction/v.v.)
"""
import json
import time
import aiosqlite

# ── Cấu trúc cột bảng players ───────────────────────────────────
# (tên cột, kiểu SQL, giá trị mặc định khi tạo người chơi mới)
PLAYER_COLUMNS = [
    ("user_id",               "TEXT PRIMARY KEY", None),
    ("name",                  "TEXT",    ""),
    ("guild_id",              "TEXT",    None),  # server Discord nơi nhập môn — dùng lọc BXH theo server
    ("exp",                   "REAL",    0),
    ("realm_index",           "INTEGER", 0),
    ("realm_tier",            "INTEGER", 1),
    ("dao",                   "TEXT",    ""),
    ("linh_can",              "TEXT",    ""),
    ("the_chat",              "TEXT",    ""),
    ("huyet_mach",            "TEXT",    ""),
    ("atk",                   "REAL",    10),
    ("def_",                  "REAL",    5),
    ("hp",                    "REAL",    100),
    ("hp_max",                "REAL",    100),
    ("spd",                   "REAL",    10),
    ("crit",                  "REAL",    5),
    ("luck",                  "REAL",    5),
    ("ngo_tinh",              "REAL",    5),
    ("phuc_duyen",            "REAL",    5),
    ("luc_chien",             "REAL",    0),
    ("stamina",               "INTEGER", 100),
    ("stamina_max",           "INTEGER", 100),
    ("linh_thach_ha",         "INTEGER", 1000),
    ("linh_thach_trung",      "INTEGER", 0),
    ("linh_thach_cuc",        "INTEGER", 0),
    ("status",                "TEXT",    "idle"),
    ("status_data",           "TEXT",    "{}"),
    ("status_start",          "REAL",    0),
    ("tong_mon_id",           "INTEGER", None),
    ("sect_rank",             "TEXT",    ""),
    ("sect_apply_id",         "INTEGER", None),
    ("sect_invite_id",        "INTEGER", None),
    ("sect_mission_date",     "INTEGER", 0),
    ("auto_dotpha",           "INTEGER", 0),
    ("vt_locked",             "INTEGER", 0),
    ("prestige",              "INTEGER", 0),  # Số lần Chuyển Sinh — mở khóa khi đạt cảnh giới tối đa
    ("passport",              "TEXT",    ""),
    ("total_cultivate_time",  "REAL",    0),
    ("total_explore",         "INTEGER", 0),
    ("total_boss_attack",     "INTEGER", 0),
    ("total_pk_win",          "INTEGER", 0),
    # ── Hệ thống Câu Cá ──────────────────────────────────────
    ("fish_coin",             "INTEGER", 0),
    ("hai_tran",              "INTEGER", 0),
    ("fish_rod",              "TEXT",    "rod_default"),
    ("fish_rod_enhance",      "INTEGER", 0),
    ("fish_boat",              "TEXT",   "boat_default"),
    ("fish_status",           "TEXT",    "idle"),
    ("fish_map",              "TEXT",    ""),
    ("fish_bait",              "TEXT",   ""),
    ("fish_start",            "REAL",    0),
    ("fish_pity",             "INTEGER", 0),
    ("fish_vip_until",        "REAL",    0),
    ("fish_nguthanh",         "INTEGER", 0),
    ("fish_daily_streak",     "INTEGER", 0),
    ("fish_daily_last",       "INTEGER", 0),
    ("fish_clan_id",          "INTEGER", None),
    # ── Đảo cá AFK ───────────────────────────────────────────
    ("island_npcs",           "TEXT",    "{}"),   # JSON: {"npc_newbie":3,"npc_veteran":2,...}
    ("island_last_collect",   "REAL",    0),
]

PLAYER_DEFAULTS = {c[0]: c[2] for c in PLAYER_COLUMNS}


class Database:
    def __init__(self, path: str):
        self.path = path
        self._conn: aiosqlite.Connection = None

    async def init(self):
        self._conn = await aiosqlite.connect(self.path)
        self._conn.row_factory = aiosqlite.Row
        await self._create_tables()
        await self._migrate_columns()
        await self._conn.commit()

    async def _migrate_columns(self):
        """Thêm cột mới vào bảng players nếu chưa có (cho DB cũ)."""
        cur = await self._conn.execute("PRAGMA table_info(players)")
        existing = {row[1] for row in await cur.fetchall()}
        for name, coltype, default in PLAYER_COLUMNS:
            if name not in existing:
                if default is None:
                    await self._conn.execute(f"ALTER TABLE players ADD COLUMN {name} {coltype}")
                else:
                    safe_default = f"'{default}'" if isinstance(default, str) else default
                    await self._conn.execute(f"ALTER TABLE players ADD COLUMN {name} {coltype} DEFAULT {safe_default}")

        # Kiểm tra bảng equipment có đủ cột không (DB cũ có thể thiếu slot_id)
        cur2 = await self._conn.execute("PRAGMA table_info(equipment)")
        eq_cols = {row[1] for row in await cur2.fetchall()}
        if "slot_id" not in eq_cols:
            # Backup dữ liệu cũ rồi recreate
            await self._conn.execute("DROP TABLE IF EXISTS equipment_old")
            await self._conn.execute("ALTER TABLE equipment RENAME TO equipment_old")
            await self._conn.execute("""
                CREATE TABLE equipment (
                    user_id TEXT NOT NULL,
                    slot_id TEXT NOT NULL,
                    item_id TEXT NOT NULL,
                    enhance INTEGER DEFAULT 0,
                    gems TEXT DEFAULT '[]',
                    PRIMARY KEY (user_id, slot_id)
                )
            """)
            # Không migrate data cũ vì schema khác hoàn toàn
            await self._conn.execute("DROP TABLE IF EXISTS equipment_old")

    async def _create_tables(self):
        cols_sql = ",\n".join(f"{name} {coltype}" for name, coltype, _ in PLAYER_COLUMNS)
        await self._conn.execute(f"CREATE TABLE IF NOT EXISTS players (\n{cols_sql}\n)")

        await self._conn.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                user_id TEXT NOT NULL,
                item_id TEXT NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (user_id, item_id)
            )
        """)

        await self._conn.execute("""
            CREATE TABLE IF NOT EXISTS equipment (
                user_id TEXT NOT NULL,
                slot_id TEXT NOT NULL,
                item_id TEXT NOT NULL,
                enhance INTEGER DEFAULT 0,
                gems TEXT DEFAULT '[]',
                PRIMARY KEY (user_id, slot_id)
            )
        """)

        await self._conn.execute("""
            CREATE TABLE IF NOT EXISTS linhthu (
                user_id TEXT PRIMARY KEY,
                thu_type TEXT,
                level INTEGER DEFAULT 1,
                exp REAL DEFAULT 0,
                happiness REAL DEFAULT 100
            )
        """)

        await self._conn.execute("""
            CREATE TABLE IF NOT EXISTS pets (
                user_id     TEXT NOT NULL,
                slot        INTEGER NOT NULL,
                pet_type    TEXT NOT NULL,
                level       INTEGER DEFAULT 1,
                exp         REAL DEFAULT 0,
                equipped    INTEGER DEFAULT 0,
                awakened    INTEGER DEFAULT 0,
                evolved     INTEGER DEFAULT 0,
                nickname    TEXT DEFAULT '',
                equip_vuot  TEXT DEFAULT '',
                equip_giap  TEXT DEFAULT '',
                equip_chau  TEXT DEFAULT '',
                explore_end INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, slot)
            )
        """)

        await self._conn.execute("""
            CREATE TABLE IF NOT EXISTS quests (
                user_id TEXT NOT NULL,
                quest_id TEXT NOT NULL,
                progress INTEGER DEFAULT 0,
                completed INTEGER DEFAULT 0,
                reset_day INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, quest_id)
            )
        """)

        await self._conn.execute("""
            CREATE TABLE IF NOT EXISTS streaks (
                user_id TEXT PRIMARY KEY,
                streak INTEGER DEFAULT 0,
                last_time REAL DEFAULT 0
            )
        """)

        await self._conn.execute("""
            CREATE TABLE IF NOT EXISTS tower (
                user_id TEXT PRIMARY KEY,
                best_floor INTEGER DEFAULT 0,
                weekly_floor INTEGER DEFAULT 0,
                total_attempts INTEGER DEFAULT 0,
                total_wins INTEGER DEFAULT 0,
                ma_ton_lenh INTEGER DEFAULT 0
            )
        """)

        await self._conn.execute("""
            CREATE TABLE IF NOT EXISTS boss_damage (
                boss_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                damage REAL DEFAULT 0,
                PRIMARY KEY (boss_id, user_id)
            )
        """)

        await self._conn.execute("""
            CREATE TABLE IF NOT EXISTS bot_admins (
                user_id TEXT PRIMARY KEY
            )
        """)

        # Cấu hình riêng theo từng server (vd: bật/tắt auto-role cảnh giới)
        await self._conn.execute("""
            CREATE TABLE IF NOT EXISTS guild_config (
                guild_id TEXT PRIMARY KEY,
                realm_role_enabled INTEGER DEFAULT 0
            )
        """)

        await self._conn.execute("""
            CREATE TABLE IF NOT EXISTS auction (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                seller_id TEXT NOT NULL,
                item_id TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price INTEGER NOT NULL,
                status TEXT DEFAULT 'active',
                listed_at INTEGER DEFAULT (strftime('%s','now')),
                expires_at INTEGER DEFAULT 0
            )
        """)

        # ── Bảng riêng cho hệ thống Câu Cá ──────────────────────
        await self._conn.execute("""
            CREATE TABLE IF NOT EXISTS fish_inventory (
                user_id TEXT NOT NULL,
                fish_id TEXT NOT NULL,
                count INTEGER DEFAULT 0,
                total_weight REAL DEFAULT 0,
                PRIMARY KEY (user_id, fish_id)
            )
        """)

        await self._conn.execute("""
            CREATE TABLE IF NOT EXISTS fish_baits (
                user_id TEXT NOT NULL,
                bait_id TEXT NOT NULL,
                quantity INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, bait_id)
            )
        """)

        await self._conn.execute("""
            CREATE TABLE IF NOT EXISTS fish_clans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                leader_id TEXT NOT NULL,
                fund INTEGER DEFAULT 0,
                created_at INTEGER DEFAULT (strftime('%s','now'))
            )
        """)

    # ══════════════════════════════════════════════════════════
    # ── RAW QUERIES ─────────────────────────────────────────────
    async def execute(self, sql: str, params: tuple = ()):
        cur = await self._conn.execute(sql, params)
        await self._conn.commit()
        return cur.rowcount

    async def fetchone(self, sql: str, params: tuple = ()):
        cur = await self._conn.execute(sql, params)
        row = await cur.fetchone()
        return dict(row) if row else None

    async def fetchall(self, sql: str, params: tuple = ()):
        cur = await self._conn.execute(sql, params)
        rows = await cur.fetchall()
        return [dict(r) for r in rows]

    # ── PLAYER ──────────────────────────────────────────────────
    async def get_player(self, user_id) -> dict | None:
        row = await self.fetchone("SELECT * FROM players WHERE user_id=?", (str(user_id),))
        return row

    async def create_player(self, user_id, name: str, guild_id=None):
        cols = [c[0] for c in PLAYER_COLUMNS]
        vals = []
        for c in PLAYER_COLUMNS:
            if c[0] == "user_id":
                vals.append(str(user_id))
            elif c[0] == "name":
                vals.append(name)
            elif c[0] == "guild_id":
                vals.append(str(guild_id) if guild_id is not None else None)
            else:
                vals.append(c[2])
        placeholders = ",".join("?" for _ in cols)
        await self._conn.execute(
            f"INSERT OR IGNORE INTO players ({','.join(cols)}) VALUES ({placeholders})",
            vals
        )
        await self._conn.commit()
        return await self.get_player(user_id)

    async def update_player(self, user_id, **kwargs):
        if not kwargs:
            return
        set_clause = ",".join(f"{k}=?" for k in kwargs)
        vals = list(kwargs.values()) + [str(user_id)]
        await self._conn.execute(
            f"UPDATE players SET {set_clause} WHERE user_id=?", vals
        )
        await self._conn.commit()

    # ── INVENTORY (vật phẩm tu tiên chung) ─────────────────────
    async def add_item(self, user_id, item_id: str, quantity: int = 1):
        await self._conn.execute("""
            INSERT INTO inventory (user_id, item_id, quantity) VALUES (?,?,?)
            ON CONFLICT(user_id, item_id) DO UPDATE SET quantity = quantity + excluded.quantity
        """, (str(user_id), item_id, quantity))
        await self._conn.commit()

    async def remove_item(self, user_id, item_id: str, quantity: int = 1):
        await self._conn.execute("""
            UPDATE inventory SET quantity = MAX(0, quantity - ?)
            WHERE user_id=? AND item_id=?
        """, (quantity, str(user_id), item_id))
        await self._conn.commit()

    async def get_item_count(self, user_id, item_id: str) -> int:
        row = await self.fetchone(
            "SELECT quantity FROM inventory WHERE user_id=? AND item_id=?",
            (str(user_id), item_id)
        )
        return row["quantity"] if row else 0

    async def get_inventory(self, user_id) -> list:
        return await self.fetchall(
            "SELECT item_id, quantity FROM inventory WHERE user_id=? ORDER BY item_id",
            (str(user_id),)
        )

    # ── EQUIPMENT ───────────────────────────────────────────────
    async def equip_item(self, user_id, slot_id: str, item_id: str):
        await self._conn.execute("""
            INSERT INTO equipment (user_id, slot_id, item_id, enhance, gems)
            VALUES (?,?,?,0,'[]')
            ON CONFLICT(user_id, slot_id) DO UPDATE SET item_id = excluded.item_id, enhance = 0, gems = '[]'
        """, (str(user_id), slot_id, item_id))
        await self._conn.commit()

    async def get_equipment(self, user_id) -> dict:
        rows = await self.fetchall(
            "SELECT slot_id, item_id, enhance, gems FROM equipment WHERE user_id=?",
            (str(user_id),)
        )
        return {r["slot_id"]: r for r in rows}

    # ── LINH THÚ ────────────────────────────────────────────────
    async def get_linhthu(self, user_id) -> dict | None:
        return await self.fetchone(
            "SELECT * FROM linhthu WHERE user_id=?", (str(user_id),)
        )

    async def set_linhthu(self, user_id, **kwargs):
        existing = await self.get_linhthu(user_id)
        if existing:
            set_clause = ",".join(f"{k}=?" for k in kwargs)
            vals = list(kwargs.values()) + [str(user_id)]
            await self._conn.execute(f"UPDATE linhthu SET {set_clause} WHERE user_id=?", vals)
        else:
            cols = ["user_id"] + list(kwargs.keys())
            vals = [str(user_id)] + list(kwargs.values())
            placeholders = ",".join("?" for _ in cols)
            await self._conn.execute(
                f"INSERT INTO linhthu ({','.join(cols)}) VALUES ({placeholders})", vals
            )
        await self._conn.commit()

    # ── QUESTS ──────────────────────────────────────────────────
    async def get_quests(self, user_id) -> list:
        return await self.fetchall(
            "SELECT * FROM quests WHERE user_id=?", (str(user_id),)
        )

    async def update_quest(self, user_id, quest_id: str, progress: int, completed: int, reset_day: int):
        await self._conn.execute("""
            INSERT INTO quests (user_id, quest_id, progress, completed, reset_day)
            VALUES (?,?,?,?,?)
            ON CONFLICT(user_id, quest_id) DO UPDATE SET
                progress=excluded.progress, completed=excluded.completed, reset_day=excluded.reset_day
        """, (str(user_id), quest_id, progress, completed, reset_day))
        await self._conn.commit()

    # ── STREAK (điểm danh / bế quan liên tục) ──────────────────
    async def get_streak(self, user_id) -> dict:
        row = await self.fetchone("SELECT * FROM streaks WHERE user_id=?", (str(user_id),))
        return row or {"user_id": str(user_id), "streak": 0, "last_time": 0}

    async def update_streak(self, user_id, streak: int, last_time: float):
        await self._conn.execute("""
            INSERT INTO streaks (user_id, streak, last_time) VALUES (?,?,?)
            ON CONFLICT(user_id) DO UPDATE SET streak=excluded.streak, last_time=excluded.last_time
        """, (str(user_id), streak, last_time))
        await self._conn.commit()

    # ── TOWER (Thiên Tầng Tháp) ─────────────────────────────────
    async def get_tower(self, user_id) -> dict:
        row = await self.fetchone("SELECT * FROM tower WHERE user_id=?", (str(user_id),))
        if row:
            return row
        await self._conn.execute(
            "INSERT INTO tower (user_id) VALUES (?)", (str(user_id),)
        )
        await self._conn.commit()
        return await self.fetchone("SELECT * FROM tower WHERE user_id=?", (str(user_id),))

    async def update_tower(self, user_id, **kwargs):
        await self.get_tower(user_id)  # đảm bảo có row
        if not kwargs:
            return
        set_clause = ",".join(f"{k}=?" for k in kwargs)
        vals = list(kwargs.values()) + [str(user_id)]
        await self._conn.execute(f"UPDATE tower SET {set_clause} WHERE user_id=?", vals)
        await self._conn.commit()

    # ── BOSS ────────────────────────────────────────────────────
    async def add_boss_damage(self, boss_id: str, user_id, damage):
        await self._conn.execute("""
            INSERT OR IGNORE INTO boss_damage (boss_id, user_id, damage) VALUES (?,?,0.0)
        """, (boss_id, str(user_id)))
        await self._conn.execute("""
            UPDATE boss_damage SET damage = damage + ? WHERE boss_id=? AND user_id=?
        """, (float(damage), boss_id, str(user_id)))
        await self._conn.commit()

    async def get_boss_top(self, boss_id: str, limit: int = 10, guild_id=None) -> list:
        if guild_id is not None:
            return await self.fetchall("""
                SELECT bd.* FROM boss_damage bd
                JOIN players p ON p.user_id = bd.user_id
                WHERE bd.boss_id=? AND p.guild_id=?
                ORDER BY bd.damage DESC LIMIT ?
            """, (boss_id, str(guild_id), limit))
        return await self.fetchall(
            "SELECT * FROM boss_damage WHERE boss_id=? ORDER BY damage DESC LIMIT ?",
            (boss_id, limit)
        )

    # ── LEADERBOARD ─────────────────────────────────────────────
    async def get_leaderboard(self, order: str = "exp", limit: int = 10, guild_id=None) -> list:
        valid_cols = {c[0] for c in PLAYER_COLUMNS}
        col = order if order in valid_cols else "exp"
        if guild_id is not None:
            return await self.fetchall(
                f"SELECT * FROM players WHERE guild_id=? ORDER BY {col} DESC LIMIT ?",
                (str(guild_id), limit)
            )
        return await self.fetchall(
            f"SELECT * FROM players ORDER BY {col} DESC LIMIT ?", (limit,)
        )

    # ── BOT ADMIN ───────────────────────────────────────────────
    async def is_bot_admin(self, user_id) -> bool:
        row = await self.fetchone(
            "SELECT 1 FROM bot_admins WHERE user_id=?", (str(user_id),)
        )
        return row is not None

    async def add_bot_admin(self, user_id, added_by=None):
        await self._conn.execute(
            "INSERT OR IGNORE INTO bot_admins (user_id) VALUES (?)", (str(user_id),)
        )
        await self._conn.commit()

    async def remove_bot_admin(self, user_id):
        await self._conn.execute(
            "DELETE FROM bot_admins WHERE user_id=?", (str(user_id),)
        )
        await self._conn.commit()

    async def list_bot_admins(self) -> list:
        return await self.fetchall("SELECT user_id FROM bot_admins")

    # ── GUILD CONFIG (cấu hình theo từng server) ─────────────────
    async def get_guild_config(self, guild_id) -> dict:
        row = await self.fetchone(
            "SELECT * FROM guild_config WHERE guild_id=?", (str(guild_id),)
        )
        if row:
            return row
        return {"guild_id": str(guild_id), "realm_role_enabled": 0}

    async def set_guild_config(self, guild_id, **kwargs):
        existing = await self.fetchone(
            "SELECT 1 FROM guild_config WHERE guild_id=?", (str(guild_id),)
        )
        if not existing:
            await self._conn.execute(
                "INSERT INTO guild_config (guild_id) VALUES (?)", (str(guild_id),)
            )
        if kwargs:
            set_clause = ", ".join(f"{k}=?" for k in kwargs)
            await self._conn.execute(
                f"UPDATE guild_config SET {set_clause} WHERE guild_id=?",
                (*kwargs.values(), str(guild_id))
            )
        await self._conn.commit()

    # ══════════════════════════════════════════════════════════
    # ── HỆ THỐNG CÂU CÁ ─────────────────────────────────────────
    async def get_fish_inventory(self, user_id) -> list:
        return await self.fetchall(
            "SELECT * FROM fish_inventory WHERE user_id=? ORDER BY count DESC",
            (str(user_id),)
        )

    async def add_fish(self, user_id, fish_id: str, count: int = 1, weight: float = 0):
        await self._conn.execute("""
            INSERT INTO fish_inventory (user_id, fish_id, count, total_weight) VALUES (?,?,?,?)
            ON CONFLICT(user_id, fish_id) DO UPDATE SET
                count = count + excluded.count,
                total_weight = total_weight + excluded.total_weight
        """, (str(user_id), fish_id, count, weight))
        await self._conn.commit()

    async def remove_fish(self, user_id, fish_id: str, count: int = 1):
        await self._conn.execute("""
            UPDATE fish_inventory SET count = MAX(0, count - ?) WHERE user_id=? AND fish_id=?
        """, (count, str(user_id), fish_id))
        await self._conn.commit()

    async def get_bait_count(self, user_id, bait_id: str) -> int:
        row = await self.fetchone(
            "SELECT quantity FROM fish_baits WHERE user_id=? AND bait_id=?",
            (str(user_id), bait_id)
        )
        return row["quantity"] if row else 0

    async def get_baits(self, user_id) -> list:
        return await self.fetchall(
            "SELECT * FROM fish_baits WHERE user_id=? AND quantity > 0 ORDER BY bait_id",
            (str(user_id),)
        )

    async def add_bait(self, user_id, bait_id: str, quantity: int = 1):
        await self._conn.execute("""
            INSERT INTO fish_baits (user_id, bait_id, quantity) VALUES (?,?,?)
            ON CONFLICT(user_id, bait_id) DO UPDATE SET quantity = quantity + excluded.quantity
        """, (str(user_id), bait_id, quantity))
        await self._conn.commit()

    async def remove_bait(self, user_id, bait_id: str, quantity: int = 1):
        await self._conn.execute("""
            UPDATE fish_baits SET quantity = MAX(0, quantity - ?) WHERE user_id=? AND bait_id=?
        """, (quantity, str(user_id), bait_id))
        await self._conn.commit()

    async def get_fish_leaderboard(self, order: str = "fish_coin", limit: int = 10, guild_id=None) -> list:
        valid_cols = {c[0] for c in PLAYER_COLUMNS}
        col = order if order in valid_cols else "fish_coin"
        if guild_id is not None:
            return await self.fetchall(
                f"SELECT * FROM players WHERE {col} > 0 AND guild_id=? ORDER BY {col} DESC LIMIT ?",
                (str(guild_id), limit)
            )
        return await self.fetchall(
            f"SELECT * FROM players WHERE {col} > 0 ORDER BY {col} DESC LIMIT ?", (limit,)
        )

    async def close(self):
        if self._conn:
            await self._conn.close()

"""utils/persistent_cache.py - Lưu dữ liệu in-memory vào SQLite để không bị mất khi restart/update"""
import json
import time
import asyncio
import logging

log = logging.getLogger("persistent_cache")

# ──────────────────────────────────────────────────────────────
#  PersistentCache: wrapper lưu dict vào bảng bot_cache trong DB
# ──────────────────────────────────────────────────────────────

class PersistentCache:
    """
    Quản lý các dict in-memory quan trọng, tự động lưu xuống SQLite.

    Cách dùng trong cog:
        from utils.persistent_cache import PersistentCache

        class MyCog(commands.Cog):
            def __init__(self, bot):
                self.bot = bot
                self._cache = PersistentCache(bot, "my_cog_key")

            async def cog_load(self):          # gọi khi cog được load
                await self._cache.load()

            async def cog_unload(self):        # gọi khi cog bị unload
                await self._cache.save()
    """

    def __init__(self, bot, namespace: str):
        self.bot = bot
        self.namespace = namespace
        self._data: dict = {}

    # ── Truy cập dict như bình thường ─────────────────────────
    def get(self, key, default=None):
        return self._data.get(str(key), default)

    def set(self, key, value):
        self._data[str(key)] = value

    def delete(self, key):
        self._data.pop(str(key), None)

    def __contains__(self, key):
        return str(key) in self._data

    def __getitem__(self, key):
        return self._data[str(key)]

    def __setitem__(self, key, value):
        self._data[str(key)] = value

    def __delitem__(self, key):
        del self._data[str(key)]

    def items(self):
        return self._data.items()

    def pop(self, key, *args):
        return self._data.pop(str(key), *args)

    # ── Load/Save từ DB ────────────────────────────────────────
    async def load(self):
        """Load dữ liệu từ DB vào memory khi khởi động."""
        try:
            await _ensure_table(self.bot)
            row = await self.bot.db.fetchone(
                "SELECT data FROM bot_cache WHERE namespace=?", (self.namespace,)
            )
            if row and row["data"]:
                loaded = json.loads(row["data"])
                # Lọc bỏ dữ liệu đã hết hạn (nếu là timestamp dict)
                self._data = _prune_expired(loaded)
                log.info(f"[Cache] Loaded '{self.namespace}': {len(self._data)} entries")
            else:
                self._data = {}
        except Exception as e:
            log.error(f"[Cache] Load error '{self.namespace}': {e}")
            self._data = {}

    async def save(self):
        """Lưu dữ liệu từ memory xuống DB."""
        try:
            await _ensure_table(self.bot)
            # Lọc hết hạn trước khi lưu
            clean = _prune_expired(self._data)
            payload = json.dumps(clean, ensure_ascii=False)
            await self.bot.db.execute(
                """INSERT INTO bot_cache(namespace, data, updated_at)
                   VALUES(?,?,?)
                   ON CONFLICT(namespace) DO UPDATE SET
                       data=excluded.data,
                       updated_at=excluded.updated_at""",
                (self.namespace, payload, int(time.time()))
            )
            log.info(f"[Cache] Saved '{self.namespace}': {len(clean)} entries")
        except Exception as e:
            log.error(f"[Cache] Save error '{self.namespace}': {e}")


# ── Helpers ────────────────────────────────────────────────────

_table_ensured = False

async def _ensure_table(bot):
    """Tạo bảng bot_cache nếu chưa có."""
    global _table_ensured
    if _table_ensured:
        return
    await bot.db.execute("""
        CREATE TABLE IF NOT EXISTS bot_cache (
            namespace  TEXT PRIMARY KEY,
            data       TEXT NOT NULL DEFAULT '{}',
            updated_at INTEGER NOT NULL DEFAULT 0
        )
    """)
    _table_ensured = True


def _prune_expired(data: dict) -> dict:
    """
    Xoá các entry đã hết hạn.
    Hỗ trợ cấu trúc:
      - { uid: expire_timestamp }           → meditation, buff đơn giản
      - { uid: { key: expire_timestamp } }  → skill_cd, buffs
      - { uid: { "due": timestamp, ... } }  → loans
      - { uid: { "date": "...", ... } }     → daily_wins (không có expire, giữ nguyên)
    """
    now = int(time.time())
    result = {}
    for uid, val in data.items():
        if isinstance(val, (int, float)):
            # expire_timestamp trực tiếp
            if val > now:
                result[uid] = val
        elif isinstance(val, dict):
            if "due" in val:
                # Khoản vay: giữ lại dù quá hạn (để phạt)
                result[uid] = val
            elif "date" in val:
                # daily_wins: giữ ngày hôm nay
                import datetime
                today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
                if val.get("date") == today:
                    result[uid] = val
            else:
                # dict of { key: expire_ts } — skill_cd, buffs
                pruned = {k: v for k, v in val.items()
                          if isinstance(v, (int, float)) and v > now}
                if pruned:
                    result[uid] = pruned
        else:
            result[uid] = val
    return result


async def save_all_caches(bot):
    """Lưu tất cả caches của tất cả cog đang chạy."""
    saved = 0
    for cog in bot.cogs.values():
        # Tìm tất cả attribute là PersistentCache
        for attr_name in dir(cog):
            if attr_name.startswith("__"):
                continue
            try:
                attr = getattr(cog, attr_name)
                if isinstance(attr, PersistentCache):
                    await attr.save()
                    saved += 1
            except Exception:
                pass
    return saved

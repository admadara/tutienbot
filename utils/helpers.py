"""utils/helpers.py - Hàm tiện ích dùng chung cho các cog

Cung cấp: now(), require_player(), require_idle(), sync_realm_role()
"""
import time
import functools
import discord
from utils.embeds import warn
from utils.game_data import REALMS, migrate_realm_index


def now() -> float:
    """Trả về timestamp hiện tại (epoch seconds)."""
    return time.time()


def require_player(func=None):
    """
    Decorator đảm bảo người chơi đã nhập môn (có record trong DB)
    trước khi chạy lệnh. Tự lấy `player` từ DB và truyền lại cho
    hàm gốc nếu hàm gốc nhận tham số `player`.

    Có thể dùng dạng @require_player hoặc @require_player().
    An toàn ngay cả khi cog tự kiểm tra `player` thủ công bên trong
    (trường hợp đó decorator chỉ là pass-through không đổi hành vi).
    """
    def decorator(f):
        @functools.wraps(f)
        async def wrapper(self, ctx, *args, **kwargs):
            player = await self.bot.db.get_player(ctx.author.id)
            if not player:
                await ctx.send(embed=warn("Chưa nhập môn! Dùng `,tl nhapdao`."))
                return
            return await f(self, ctx, *args, **kwargs)
        return wrapper

    if func is not None and callable(func):
        return decorator(func)
    return decorator


def require_idle(func=None):
    """
    Decorator đảm bảo người chơi không đang trong trạng thái bận
    (bế quan / đang câu cá / đang thám hiểm...) trước khi cho thực
    hiện hành động khác. Dựa vào field `status` của player ("idle"
    nếu rảnh, khác "idle"/None thì coi là đang bận).

    Dùng dạng @require_idle hoặc @require_idle().
    """
    def decorator(f):
        @functools.wraps(f)
        async def wrapper(self, ctx, *args, **kwargs):
            player = await self.bot.db.get_player(ctx.author.id)
            status = (player or {}).get("status")
            if status and status not in ("idle", "", None):
                await ctx.send(embed=warn(
                    f"Bạn đang bận (`{status}`)! Hoàn thành việc hiện tại trước đã."
                ))
                return
            return await f(self, ctx, *args, **kwargs)
        return wrapper

    if func is not None and callable(func):
        return decorator(func)
    return decorator


# ── ROLE PREFIX để nhận diện role cảnh giới do bot tự quản lý ───
# (tránh đụng role khác admin server tự đặt tên trùng tình cờ)
REALM_ROLE_PREFIX = "🌌 "
REALM_ROLE_COLOR = 0x9C6BFF


async def sync_realm_role(bot, member: discord.Member, realm_index: int):
    """
    Đồng bộ Discord role theo đại cảnh giới hiện tại của người chơi:
    xóa role cảnh giới cũ (nếu có) và gán role cảnh giới mới.

    An toàn tuyệt đối — không bao giờ raise lỗi ra ngoài (bọc try/except
    toàn bộ) để 1 lỗi quyền/role không bao giờ làm hỏng lệnh đột phá.
    Bỏ qua êm nếu: tính năng đang tắt cho server, bot thiếu quyền
    Manage Roles, hoặc role mục tiêu nằm trên role cao nhất của bot.
    """
    if not member or not member.guild:
        return
    guild = member.guild
    try:
        cfg = await bot.db.get_guild_config(guild.id)
        if not cfg.get("realm_role_enabled"):
            return

        ri = int(realm_index)
        if ri >= len(REALMS):
            ri = migrate_realm_index(ri)
        ri = max(0, min(ri, len(REALMS) - 1))
        target_name = REALM_ROLE_PREFIX + REALMS[ri]["name"]

        if not guild.me.guild_permissions.manage_roles:
            return

        # Xóa mọi role cảnh giới cũ khác (member chỉ giữ đúng 1 role cảnh giới)
        old_realm_roles = [
            r for r in member.roles
            if r.name.startswith(REALM_ROLE_PREFIX) and r.name != target_name
        ]
        if old_realm_roles:
            try:
                await member.remove_roles(*old_realm_roles, reason="Đồng bộ role cảnh giới")
            except discord.Forbidden:
                pass

        # Đã có đúng role rồi thì thôi
        if any(r.name == target_name for r in member.roles):
            return

        role = discord.utils.get(guild.roles, name=target_name)
        if role is None:
            try:
                role = await guild.create_role(
                    name=target_name, color=discord.Color(REALM_ROLE_COLOR),
                    reason="Tự tạo role cảnh giới tu tiên"
                )
            except discord.Forbidden:
                return
            except discord.HTTPException:
                return

        try:
            await member.add_roles(role, reason="Đột phá cảnh giới")
        except discord.Forbidden:
            pass
    except Exception:
        # Không bao giờ để lỗi role làm hỏng luồng chính (đột phá, set cảnh giới...)
        pass

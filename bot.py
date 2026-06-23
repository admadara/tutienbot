import discord
from discord.ext import commands
import asyncio, os
from difflib import get_close_matches

def load_env():
    try:
        with open('.env') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ[k.strip()] = v.strip()
    except FileNotFoundError:
        pass

load_env()
from utils.database import Database

PREFIXES = [",tuluyen ", ",tl ", ",sect ", ",tm "]
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix=PREFIXES,
    intents=intents,
    help_command=None,
    case_insensitive=True,
)
bot.db: Database = None

COGS = [
    "cogs.core", "cogs.profile", "cogs.cultivation",
    "cogs.exploration", "cogs.boss", "cogs.economy",
    "cogs.tasks", "cogs.tongmon", "cogs.equipment",
    "cogs.minigame", "cogs.linhthu", "cogs.luyen_dan",
    "cogs.social", "cogs.shop_extra", "cogs.admin",
    "cogs.extra_commands", "cogs.world", "cogs.pvp",
    "cogs.achievement", "cogs.craft", "cogs.skill",
    "cogs.market", "cogs.wiki", "cogs.fishing", "cogs.mystic",
    "cogs.events", "cogs.sudao",
]

# ── Hàm gợi ý lệnh gần giống ─────────────────────────────
def suggest_commands(bot_instance, input_cmd: str) -> list[str]:
    """Tìm lệnh gần giống nhất với input"""
    all_names = []
    for cmd in bot_instance.walk_commands():
        all_names.append(cmd.qualified_name)
        for alias in cmd.aliases:
            # Thêm alias với prefix group nếu có
            if hasattr(cmd, 'parent') and cmd.parent:
                all_names.append(f"{cmd.parent.qualified_name} {alias}")
            else:
                all_names.append(alias)
    
    # Tìm gần giống (cutoff 0.6 = 60% giống)
    matches = get_close_matches(input_cmd, all_names, n=3, cutoff=0.55)
    return matches

@bot.event
async def on_ready():
    print(f"✅ {bot.user} (ID: {bot.user.id})")
    total = len(list(bot.walk_commands()))
    print(f"📋 Tổng lệnh: {total}")
    await bot.change_presence(
        activity=discord.Game(name=f",tl help | Tu Tiên Bot v4 | {total} lệnh")
    )

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    content = message.content.strip()
    # ,tl rỗng → hiện profile
    if content in (",tl", ",tuluyen", ",sect", ",tm"):
        ctx = await bot.get_context(message)
        cmd = bot.get_command("status")
        if cmd:
            await message.add_reaction("👍")
            await ctx.invoke(cmd)
        return

    # ,cc [subcommand] [args...] → prefix riêng, hoàn toàn độc lập với ,tl
    # Không đi qua bot.process_commands (tránh đụng namespace lệnh ,tl shop, ,tl boss, ...)
    if content == ",cc" or content.startswith(",cc "):
        cc_group = bot.get_command("cc")  # group "cc" định nghĩa trong cogs/fishing.py
        if cc_group is None:
            return
        rest = content[len(",cc"):].strip()  # vd: "shop" / "buy bait_bot 5" / ""
        view = commands.view.StringView(rest)
        ctx = await bot.get_context(message)
        ctx.command = cc_group
        ctx.view = view
        ctx.invoked_with = "cc"
        ctx.prefix = ",cc "
        try:
            await message.add_reaction("👍")
        except Exception:
            pass
        try:
            await cc_group.invoke(ctx)
        except commands.CommandError as e:
            await bot.on_command_error(ctx, e)
        except Exception as e:
            await bot.on_command_error(ctx, commands.CommandInvokeError(e))
        return

    await bot.process_commands(message)

@bot.event
async def on_command(ctx):
    """Reaction 👍 khi bot nhận được lệnh hợp lệ"""
    try:
        await ctx.message.add_reaction("👍")
    except Exception:
        pass
    # Vá guild_id cho người chơi cũ (tạo trước khi cột này tồn tại) —
    # đảm bảo họ xuất hiện lại trong BXH theo server. Chạy ở đây (1 chỗ
    # trung tâm) để phủ mọi lệnh, kể cả cog không dùng @require_player.
    if ctx.guild:
        try:
            player = await bot.db.get_player(ctx.author.id)
            if player and not player.get("guild_id"):
                await bot.db.update_player(ctx.author.id, guild_id=str(ctx.guild.id))
        except Exception:
            pass

@bot.event
async def on_member_join(member):
    """Khôi phục role cảnh giới nếu người chơi đã từng nhập môn trên server này
    (Discord tự xóa hết role khi rời server, nên cần gán lại lúc quay về)."""
    try:
        from utils.helpers import sync_realm_role
        player = await bot.db.get_player(member.id)
        if player and str(player.get("guild_id")) == str(member.guild.id):
            await sync_realm_role(bot, member, int(player.get("realm_index", 0)))
    except Exception:
        pass

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        # Lấy tên lệnh người dùng gõ
        parts = ctx.message.content.strip().split()
        if len(parts) < 2:
            return
        # Lấy phần sau prefix
        prefix_used = ""
        for pf in PREFIXES:
            if ctx.message.content.lower().startswith(pf.lower()):
                prefix_used = pf
                break
        raw = ctx.message.content[len(prefix_used):].strip()
        cmd_input = raw.split()[0] if raw else ""

        # Thêm reaction ❓ khi không tìm thấy lệnh
        try:
            await ctx.message.add_reaction("❓")
        except Exception:
            pass

        # Tìm gợi ý
        suggestions = suggest_commands(bot, cmd_input)

        embed = discord.Embed(
            title="❓ Lệnh Không Tồn Tại",
            description=f"Lệnh **`,tl {cmd_input}`** không tồn tại!",
            color=0xFF5722
        )
        if suggestions:
            sug_str = "\n".join(f"• `,tl {s}`" for s in suggestions)
            embed.add_field(
                name="💡 Có phải bạn muốn dùng?",
                value=sug_str,
                inline=False
            )
        embed.add_field(
            name="📋 Xem tất cả lệnh",
            value="`,tl lenh` — Danh sách đầy đủ\n`,cc` — Hướng dẫn câu cá",
            inline=False
        )
        embed.set_footer(text="Tu Tiên Bot v4")
        await ctx.send(embed=embed)
        return

    if isinstance(error, commands.MissingRequiredArgument):
        try: await ctx.message.add_reaction("⚠️")
        except: pass
        await ctx.send(embed=discord.Embed(
            description=f"⚠️ **Thiếu tham số!** Gõ `,tl help` để xem cách dùng.",
            color=0xFF9800
        ))
        return

    if isinstance(error, commands.CommandOnCooldown):
        try: await ctx.message.add_reaction("⏳")
        except: pass
        await ctx.send(embed=discord.Embed(
            description=f"⏳ **Hồi chiêu!** Thử lại sau `{error.retry_after:.1f}s`",
            color=0xFF9800
        ))
        return

    if isinstance(error, (commands.BadArgument, commands.MemberNotFound, commands.UserNotFound)):
        try: await ctx.message.add_reaction("⚠️")
        except: pass
        await ctx.send(embed=discord.Embed(
            description="⚠️ **Sai tham số!** Dùng `,tl help` để xem cú pháp.",
            color=0xFF9800
        ))
        return

    if isinstance(error, commands.CheckFailure):
        try: await ctx.message.add_reaction("🚫")
        except: pass
        return

    # Lỗi không xác định - vẫn in ra console để debug
    import traceback
    print(f"[ERROR] {ctx.command}: {error}")
    traceback.print_exception(type(error), error, error.__traceback__)
    try: await ctx.message.add_reaction("❌")
    except: pass

async def main():
    bot.db = Database("data/tuluyen.db")
    await bot.db.init()
    # Migration: thêm column vt_locked nếu chưa có
    try:
        await bot.db._conn.execute("ALTER TABLE players ADD COLUMN vt_locked INTEGER DEFAULT 0")
        await bot.db._conn.commit()
        print("[Migration] ✅ Đã thêm column vt_locked vào bảng players")
    except Exception:
        pass  # Column đã tồn tại, bỏ qua
    # Migration: thêm các cột hệ thống Câu Cá (fish_*) nếu DB được tạo từ bản cũ chưa có
    from utils.database import PLAYER_COLUMNS
    for col_name, col_type, col_default in PLAYER_COLUMNS:
        if not col_name.startswith("fish_") and col_name != "hai_tran":
            continue
        try:
            default_sql = "NULL" if col_default is None else repr(col_default) if isinstance(col_default, str) else str(col_default)
            await bot.db._conn.execute(
                f"ALTER TABLE players ADD COLUMN {col_name} {col_type} DEFAULT {default_sql}"
            )
            await bot.db._conn.commit()
            print(f"[Migration] ✅ Đã thêm column {col_name} vào bảng players")
        except Exception:
            pass  # Column đã tồn tại, bỏ qua
    for cog in COGS:
        try:
            await bot.load_extension(cog)
            print(f"  📦 {cog}")
        except Exception as e:
            print(f"  ❌ {cog}: {e}")
    token = os.getenv("DISCORD_TOKEN", "")
    if not token or token in ("paste_token_here", "token_cua_ban_o_day"):
        print("\n❌ Chưa điền DISCORD_TOKEN trong .env!\n")
        return
    print("🚀 Đang kết nối Discord...")
    try:
        await bot.start(token)
    finally:
        # Lưu toàn bộ cache trước khi tắt
        try:
            from utils.persistent_cache import save_all_caches
            count = await save_all_caches(bot)
            print(f"[Shutdown] ✅ Đã lưu {count} cache(s) trước khi tắt.")
        except Exception as e:
            print(f"[Shutdown] ⚠️ Không lưu được cache: {e}")

if __name__ == "__main__":
    asyncio.run(main())

def run_web():
    import sys
    sys.path.insert(0, '/app')
    from web.app import app
    app.run(host='0.0.0.0', port=5000, debug=False)

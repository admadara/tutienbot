"""web/app.py — Tu Tiên Bot Web Dashboard + Admin Panel"""
from flask import (Flask, render_template, jsonify, abort,
                   request, session, redirect, url_for)
import sqlite3, os, subprocess, signal, hashlib, time, glob

app = Flask(__name__)
app.secret_key = "tutien_secret_2026_ndz"   # đổi nếu muốn

# ══ CẤU HÌNH ADMIN ════════════════════════════════════════
# Thêm sub-admin: {"tên": "mật khẩu"}
ADMINS = {
    "admin":   "tutien2026",
    "subadmin": "ndz1234",
}

BOT_DIR  = os.path.join(os.path.dirname(__file__), "..")
DB_PATH  = os.path.join(BOT_DIR, "data", "tuluyen.db")
PID_FILE = os.path.join(BOT_DIR, "bot.pid")

# ══ HELPERS ═══════════════════════════════════════════════
REALMS = [
    "Luyện Thể","Tụ Khí","Luyện Khí","Ngưng Khí","Trúc Cơ","Tử Phủ","Đạo Cung","Kim Đan",
    "Nguyên Anh","Hóa Thần","Luyện Hư","Hợp Thể","Đại Thừa","Độ Kiếp",
    "Bán Tiên","Nhân Tiên","Địa Tiên","Thiên Tiên","Chân Tiên","Huyền Tiên",
    "Kim Tiên","Thái Ất Tiên","Đại La Tiên","Tiên Quân","Tiên Vương","Tiên Hoàng",
    "Tiên Tôn","Tiên Đế","Tiên Thánh","Tiên Tổ","Chân Thần","Thiên Thần","Cổ Thần",
    "Thần Vương","Thần Hoàng","Thần Đế","Thần Tôn","Thần Thánh","Thần Tổ",
    "Hỗn Độn","Hồng Mông","Thái Sơ","Khởi Nguyên","Tạo Hóa","Chưởng Đạo",
    "Bất Hủy","Vĩnh Hằng","Siêu Thoát","Chúa Tể","Vô Thượng Đạo Tổ",
    "Hư Không Thần","Hư Không Thánh","Hư Không Vương","Hư Không Đế","Hư Không Tổ",
    "Thiên Đạo Giả","Thiên Đạo Thần","Thiên Đạo Thánh","Thiên Đạo Đế","Thiên Đạo Tổ",
    "Vũ Trụ Thần","Vũ Trụ Thánh","Vũ Trụ Đế","Vũ Trụ Tổ",
    "Bản Nguyên Thần","Bản Nguyên Thánh","Bản Nguyên Đế","Bản Nguyên Tổ",
    "Vô Cực Đạo Thần","Vạn Giới Chí Tôn",
]

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def realm_name(ri, rt):
    if ri >= len(REALMS): return "∞ Thiên Đạo"
    return f"{REALMS[ri]} tầng {rt}"

def fmt_num(n):
    try:
        n = float(n)
        if n >= 1e12: return f"{n/1e12:.1f}T"
        if n >= 1e9:  return f"{n/1e9:.1f}B"
        if n >= 1e6:  return f"{n/1e6:.1f}M"
        if n >= 1e3:  return f"{n/1e3:.1f}K"
        return str(int(n))
    except: return "0"

def realm_color(ri):
    colors = [
        "#9E9E9E","#9E9E9E","#9E9E9E","#9E9E9E",
        "#4CAF50","#4CAF50","#4CAF50","#4CAF50",
        "#2196F3","#2196F3","#2196F3","#2196F3","#2196F3","#2196F3",
        "#9C27B0","#9C27B0","#9C27B0","#9C27B0","#9C27B0","#9C27B0","#9C27B0","#9C27B0","#9C27B0",
        "#FF9800","#FF9800","#FF9800","#FF9800","#FF9800","#FF9800","#FF9800",
        "#F44336","#F44336","#F44336","#F44336","#F44336","#F44336","#F44336","#F44336","#F44336",
    ]
    if ri >= len(colors): return "#FFD700"
    return colors[ri]

def is_logged_in():
    return session.get("admin_user") in ADMINS

def bot_status():
    """Kiểm tra bot có đang chạy không qua PID file."""
    try:
        if not os.path.exists(PID_FILE):
            return "stopped"
        with open(PID_FILE) as f:
            pid = int(f.read().strip())
        os.kill(pid, 0)   # signal 0 = kiểm tra process tồn tại
        return "running"
    except (ProcessLookupError, ValueError, PermissionError):
        return "stopped"

def start_bot():
    if bot_status() == "running":
        return False, "Bot đang chạy rồi!"
    try:
        proc = subprocess.Popen(
            ["python", "bot.py"],
            cwd=BOT_DIR,
            stdout=open(os.path.join(BOT_DIR, "bot.log"), "a"),
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        with open(PID_FILE, "w") as f:
            f.write(str(proc.pid))
        return True, f"Bot đã khởi động (PID: {proc.pid})"
    except Exception as e:
        return False, str(e)

def stop_bot():
    if bot_status() == "stopped":
        return False, "Bot không chạy!"
    try:
        with open(PID_FILE) as f:
            pid = int(f.read().strip())
        os.kill(pid, signal.SIGTERM)
        time.sleep(1)
        os.remove(PID_FILE)
        return True, f"Bot đã dừng (PID: {pid})"
    except Exception as e:
        return False, str(e)

def get_log(lines=50):
    log_path = os.path.join(BOT_DIR, "bot.log")
    try:
        with open(log_path, "r", errors="replace") as f:
            all_lines = f.readlines()
            return "".join(all_lines[-lines:])
    except:
        return "(Chưa có log)"

# ══ PUBLIC ROUTES ══════════════════════════════════════════
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/profile/<user_id>")
def profile(user_id):
    return render_template("profile.html", user_id=user_id)

@app.route("/bxh")
def bxh():
    return render_template("bxh.html")

# ══ ADMIN LOGIN ════════════════════════════════════════════
@app.route("/admin", methods=["GET","POST"])
def admin_login():
    if is_logged_in():
        return redirect(url_for("admin_panel"))
    error = None
    if request.method == "POST":
        username = request.form.get("username","").strip()
        password = request.form.get("password","").strip()
        if username in ADMINS and ADMINS[username] == password:
            session["admin_user"] = username
            session.permanent = True
            return redirect(url_for("admin_panel"))
        error = "Sai tài khoản hoặc mật khẩu!"
    return render_template("admin_login.html", error=error)

@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))

# ══ ADMIN PANEL ════════════════════════════════════════════
@app.route("/admin/panel")
def admin_panel():
    if not is_logged_in():
        return redirect(url_for("admin_login"))
    db = get_db()
    stats = {
        "total_players": db.execute("SELECT COUNT(*) FROM players WHERE name != ''").fetchone()[0],
        "online_today":  db.execute(
            "SELECT COUNT(*) FROM players WHERE status != 'idle'"
        ).fetchone()[0],
    }
    db.close()
    return render_template("admin_panel.html",
        user=session["admin_user"],
        status=bot_status(),
        stats=stats,
        log=get_log(30),
    )

# ══ ADMIN API ══════════════════════════════════════════════
@app.route("/admin/api/status")
def admin_api_status():
    if not is_logged_in(): abort(403)
    return jsonify({"status": bot_status()})

@app.route("/admin/api/start", methods=["POST"])
def admin_api_start():
    if not is_logged_in(): abort(403)
    ok, msg = start_bot()
    return jsonify({"ok": ok, "msg": msg})

@app.route("/admin/api/stop", methods=["POST"])
def admin_api_stop():
    if not is_logged_in(): abort(403)
    ok, msg = stop_bot()
    return jsonify({"ok": ok, "msg": msg})

@app.route("/admin/api/restart", methods=["POST"])
def admin_api_restart():
    if not is_logged_in(): abort(403)
    stop_bot()
    time.sleep(2)
    ok, msg = start_bot()
    return jsonify({"ok": ok, "msg": "Restart: " + msg})

@app.route("/admin/api/log")
def admin_api_log():
    if not is_logged_in(): abort(403)
    return jsonify({"log": get_log(80)})

@app.route("/admin/api/players")
def admin_api_players():
    if not is_logged_in(): abort(403)
    db = get_db()
    rows = db.execute(
        "SELECT user_id,name,realm_index,realm_tier,luc_chien,status FROM players "
        "WHERE name != '' ORDER BY luc_chien DESC LIMIT 50"
    ).fetchall()
    db.close()
    result = []
    for r in rows:
        ri = int(r["realm_index"] or 0)
        rt = int(r["realm_tier"] or 1)
        result.append({
            "user_id": r["user_id"],
            "name":    r["name"],
            "realm":   realm_name(ri, rt),
            "luc_chien": fmt_num(r["luc_chien"]),
            "status":  r["status"] or "idle",
        })
    return jsonify(result)

# ══ PUBLIC API ═════════════════════════════════════════════
@app.route("/api/profile/<user_id>")
def api_profile(user_id):
    db = get_db()
    p = db.execute("SELECT * FROM players WHERE user_id=?", (str(user_id),)).fetchone()
    if not p: abort(404)
    p = dict(p)
    su_info = None
    try:
        su_row = db.execute("SELECT * FROM su_dao WHERE do_de_id=?", (str(user_id),)).fetchone()
        if su_row:
            sp = db.execute("SELECT name,realm_index,realm_tier FROM players WHERE user_id=?",
                            (su_row["su_phu_id"],)).fetchone()
            if sp:
                su_info = {"name": sp["name"], "realm": realm_name(sp["realm_index"], sp["realm_tier"]),
                           "exp_shared": fmt_num(su_row["exp_shared"])}
    except: pass
    do_de_list = []
    try:
        for r in db.execute("SELECT * FROM su_dao WHERE su_phu_id=?", (str(user_id),)).fetchall():
            dp = db.execute("SELECT name,realm_index,realm_tier FROM players WHERE user_id=?",
                            (r["do_de_id"],)).fetchone()
            if dp:
                do_de_list.append({"name": dp["name"], "realm": realm_name(dp["realm_index"], dp["realm_tier"])})
    except: pass
    sect_name = None
    try:
        if p.get("tong_mon_id"):
            s = db.execute("SELECT name FROM sects WHERE id=?", (p["tong_mon_id"],)).fetchone()
            if s: sect_name = s["name"]
    except: pass
    db.close()
    ri = int(p.get("realm_index", 0))
    rt = int(p.get("realm_tier", 1))
    return jsonify({
        "user_id": p["user_id"], "name": p["name"] or "???",
        "realm": realm_name(ri, rt), "realm_color": realm_color(ri), "realm_index": ri,
        "dao": p.get("dao") or "—", "linh_can": p.get("linh_can") or "—",
        "the_chat": p.get("the_chat") or "—", "huyet_mach": p.get("huyet_mach") or "—",
        "atk": fmt_num(p.get("atk",0)), "def_": fmt_num(p.get("def_",0)),
        "hp": fmt_num(p.get("hp_max",0)), "spd": fmt_num(p.get("spd",0)),
        "crit": f"{p.get('crit',0):.1f}%", "luck": fmt_num(p.get("luck",0)),
        "luc_chien": fmt_num(p.get("luc_chien",0)), "exp": fmt_num(p.get("exp",0)),
        "prestige": int(p.get("prestige",0)),
        "lt_ha": fmt_num(p.get("linh_thach_ha",0)), "lt_trung": fmt_num(p.get("linh_thach_trung",0)),
        "lt_cuc": fmt_num(p.get("linh_thach_cuc",0)),
        "total_pk_win": int(p.get("total_pk_win",0)), "total_explore": int(p.get("total_explore",0)),
        "total_boss": int(p.get("total_boss_attack",0)),
        "fish_coin": fmt_num(p.get("fish_coin",0)), "hai_tran": fmt_num(p.get("hai_tran",0)),
        "sect": sect_name, "su_phu": su_info, "do_de": do_de_list,
        "stamina": int(p.get("stamina",0)), "stamina_max": int(p.get("stamina_max",100)),
    })

@app.route("/api/bxh/<loai>")
def api_bxh(loai):
    ORDER = {"exp":"exp","luc_chien":"luc_chien","pk":"total_pk_win","fish":"fish_coin","haitran":"hai_tran"}
    col = ORDER.get(loai, "exp")
    db = get_db()
    rows = db.execute(
        f"SELECT user_id,name,realm_index,realm_tier,{col} FROM players "
        f"WHERE name != '' ORDER BY {col} DESC LIMIT 20"
    ).fetchall()
    db.close()
    result = []
    for i, r in enumerate(rows):
        ri = int(r["realm_index"] or 0); rt = int(r["realm_tier"] or 1)
        result.append({"rank":i+1,"name":r["name"],"realm":realm_name(ri,rt),
                       "color":realm_color(ri),"value":fmt_num(r[col]),"user_id":r["user_id"]})
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

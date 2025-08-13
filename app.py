import os
import time
import sqlite3
from pathlib import Path
from datetime import timedelta
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = BASE_DIR / "static" / "uploads"
DB_PATH = BASE_DIR / "instance" / "app.db"

ALLOWED_EXT = {"png", "jpg", "jpeg", "webp"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT

def init_db():
    os.makedirs(BASE_DIR / "instance", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Create table with phone + profile_pic columns (if not exists)
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash TEXT,
            phone TEXT DEFAULT '',
            profile_pic TEXT DEFAULT ''
        )
    """)
    conn.commit()

    # Ensure columns exist for older DBs (safe ALTER)
    c.execute("PRAGMA table_info(users)")
    cols = [row[1] for row in c.fetchall()]
    if "phone" not in cols:
        try:
            c.execute("ALTER TABLE users ADD COLUMN phone TEXT DEFAULT ''")
        except Exception:
            pass
    if "profile_pic" not in cols:
        try:
            c.execute("ALTER TABLE users ADD COLUMN profile_pic TEXT DEFAULT ''")
        except Exception:
            pass
    conn.commit()
    conn.close()

class User(UserMixin):
    def __init__(self, id_, username):
        self.id = id_
        self.username = username

    @staticmethod
    def get(user_id):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id, username FROM users WHERE id = ?", (user_id,))
        row = c.fetchone()
        conn.close()
        if row:
            return User(row[0], row[1])
        return None

    @staticmethod
    def find_by_username(username):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id, username, password_hash FROM users WHERE username = ?", (username,))
        row = c.fetchone()
        conn.close()
        if row:
            return {"id": row[0], "username": row[1], "password_hash": row[2]}
        return None

    @staticmethod
    def create(username, password):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        pw_hash = generate_password_hash(password)
        try:
            c.execute("INSERT INTO users(username, password_hash) VALUES (?,?)", (username, pw_hash))
            conn.commit()
            user_id = c.lastrowid
            return User(user_id, username)
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()

# Helper: get settings record for user (returns dict)
def get_user_settings(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT username, phone, profile_pic FROM users WHERE id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {"username": row[0], "phone": row[1] or "", "profile_pic": row[2] or ""}
    return {"username": "", "phone": "", "profile_pic": ""}

# Helper: update phone/profile_pic (profile_pic should be relative path under static/)
def update_user_settings(user_id, phone=None, profile_pic_relpath=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if phone is not None and profile_pic_relpath is not None:
        c.execute("UPDATE users SET phone = ?, profile_pic = ? WHERE id = ?", (phone, profile_pic_relpath, user_id))
    elif phone is not None:
        c.execute("UPDATE users SET phone = ? WHERE id = ?", (phone, user_id))
    elif profile_pic_relpath is not None:
        c.execute("UPDATE users SET profile_pic = ? WHERE id = ?", (profile_pic_relpath, user_id))
    conn.commit()
    conn.close()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "replace-this-secret")
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

# ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
init_db()

# debug prints (optional)
print("APP BASE_DIR:", BASE_DIR)
print("STATIC FOLDER:", app.static_folder)
print("styles.css exists:", (BASE_DIR / "static" / "styles.css").exists())

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.get(int(user_id))
    except Exception:
        return None

@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return render_template("login.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        if not username or not password:
            flash("Provide username and password", "danger")
            return redirect(url_for("register"))
        created = User.create(username, password)
        if created:
            flash("Account created. Please log in.", "success")
            return redirect(url_for("login"))
        else:
            flash("Username already exists", "danger")
            return redirect(url_for("register"))
    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        u = User.find_by_username(username)
        if u and check_password_hash(u["password_hash"], password):
            user = User(u["id"], u["username"])
            login_user(user)
            return redirect(url_for("dashboard"))
        flash("Invalid username or password", "danger")
        return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out", "info")
    return redirect(url_for("login"))

@app.route("/dashboard", methods=["GET","POST"])
@login_required
def dashboard():
    # get user settings for sidebar
    settings = get_user_settings(current_user.id)
    # determine profile image URL (fallback to default)
    if settings.get("profile_pic"):
        # profile_pic stored relative to static root, e.g. "uploads/3/profile_123.png"
        profile_pic_url = url_for("static", filename=settings["profile_pic"])
    else:
        profile_pic_url = url_for("static", filename="images/default_profile.png")

    # If image upload (enhancement) POST (existing behavior)
    if request.method == "POST":
        file = request.files.get("image")
        if not file or file.filename == "":
            flash("No file selected", "danger")
            return redirect(url_for("dashboard"))
        if not allowed_file(file.filename):
            flash("Unsupported file type", "danger")
            return redirect(url_for("dashboard"))

        filename = secure_filename(file.filename)
        user_folder = Path(app.config["UPLOAD_FOLDER"]) / str(current_user.id)
        user_folder.mkdir(parents=True, exist_ok=True)

        src_path = user_folder / filename
        file.save(src_path)

        # PLACEHOLDER: AI enhancement (no-op for now)
        processed_path = src_path

        # Compute path relative to static for url_for
        static_root = BASE_DIR / "static"
        rel_to_static = os.path.relpath(processed_path, start=static_root).replace("\\", "/")
        enhanced_url = url_for("static", filename=rel_to_static)
        flash("Image uploaded successfully (no enhancement applied yet)", "success")
        # render template with settings + enhanced image
        return render_template("dashboard.html",
                               enhanced=enhanced_url,
                               enhanced_filename=rel_to_static,
                               username=settings.get("username"),
                               profile_pic_url=profile_pic_url,
                               phone=settings.get("phone", ""))
    # GET: normal render
    return render_template("dashboard.html",
                           enhanced=None,
                           enhanced_filename=None,
                           username=settings.get("username"),
                           profile_pic_url=profile_pic_url,
                           phone=settings.get("phone", ""))

# Endpoint to save settings (profile picture and phone). Expects multipart/form-data
@app.route("/save_settings", methods=["POST"])
@login_required
def save_settings():
    phone = request.form.get("phone", "").strip()
    profile_file = request.files.get("profile_pic")
    rel_path = None

    if profile_file and profile_file.filename != "":
        if not allowed_file(profile_file.filename):
            return jsonify({"status": "error", "message": "Unsupported profile image type"}), 400
        filename = secure_filename(profile_file.filename)
        # prefix with timestamp to reduce collisions
        timestamp = int(time.time())
        filename = f"profile_{timestamp}_{filename}"
        user_folder = Path(app.config["UPLOAD_FOLDER"]) / str(current_user.id)
        user_folder.mkdir(parents=True, exist_ok=True)
        save_path = user_folder / filename
        profile_file.save(save_path)
        # compute relative path for storage: relative to static folder
        rel_path = os.path.relpath(save_path, start=BASE_DIR / "static").replace("\\", "/")

    # Update DB
    if rel_path and phone:
        update_user_settings(current_user.id, phone=phone, profile_pic_relpath=rel_path)
    elif rel_path:
        update_user_settings(current_user.id, profile_pic_relpath=rel_path)
    else:
        update_user_settings(current_user.id, phone=phone)

    # Return updated values (including absolute static URL)
    profile_pic_db = get_user_settings(current_user.id).get("profile_pic") or ""
    if profile_pic_db:
        profile_pic_url = url_for("static", filename=profile_pic_db)
    else:
        profile_pic_url = url_for("static", filename="images/default_profile.png")

    return jsonify({
        "status": "success",
        "username": get_user_settings(current_user.id).get("username"),
        "phone": phone,
        "profile_pic_url": profile_pic_url
    })

# simpler download route using static folder + path param
@app.route("/download/<path:filename>")
@login_required
def download(filename):
    return send_from_directory(directory=app.static_folder, path=filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, port=5000)

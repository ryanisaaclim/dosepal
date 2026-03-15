import sqlite3
from flask import Flask, render_template, request, redirect, jsonify, session
import re
from datetime import datetime
import pytz
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = "dosepal_secret_key"

# 🔗 Database connection
def get_db():
    conn = sqlite3.connect("dosepal.db")
    conn.row_factory = sqlite3.Row
    return conn


# 🏠 Homepage
@app.route("/")
def index():
    if "user_id" not in session:
        return redirect("/login")

    daily_rollover()
    log_missed_doses()

    db = get_db()
    meds = db.execute(
        "SELECT * FROM meds WHERE user_id = ? ORDER BY time ASC",
        (session["user_id"],)
    ).fetchall()

    sg = pytz.timezone("Asia/Singapore")
    current_time = datetime.now(sg)
    now = current_time.strftime("%H:%M")

    selected_filter = request.args.get("filter", "all")

    all_processed_meds = []

    for med in meds:
        status = "upcoming"

        if med["taken"] == 1:
            status = "taken"
        elif med["time"] < now:
            status = "overdue"

        all_processed_meds.append({
            "id": med["id"],
            "name": med["name"],
            "dosage": med["dosage"],
            "time": med["time"],
            "taken": med["taken"],
            "repeat_daily": med["repeat_daily"],
            "start_date": med["start_date"],
            "end_date": med["end_date"],
            "notes": med["notes"],
            "status": status
        })

    total = len(all_processed_meds)
    taken_count = sum(1 for m in all_processed_meds if m["status"] == "taken")
    percent = round((taken_count / total) * 100) if total > 0 else 0

    next_med = None
    for med in all_processed_meds:
        if med["status"] == "upcoming":
            next_med = med
            break

    if selected_filter == "all":
        display_meds = all_processed_meds
    else:
        display_meds = [m for m in all_processed_meds if m["status"] == selected_filter]

    return render_template(
        "index.html",
        meds=display_meds,
        next_med=next_med,
        now=now,
        total=total,
        taken_count=taken_count,
        percent=percent,
        selected_filter=selected_filter
    )

# ➕ Add medication
@app.route("/add", methods=["GET", "POST"])
def add():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        dosage = request.form.get("dosage", "").strip()
        time = request.form.get("time", "").strip()
        repeat_daily = 1 if request.form.get("repeat_daily") == "1" else 0
        start_date = request.form.get("start_date", "").strip()
        end_date = request.form.get("end_date", "").strip()
        notes = request.form.get("notes", "").strip()

        if not name or not time:
            return render_template("add.html", error="Please fill in all required fields.")

        db = get_db()
        db.execute(
            """
            INSERT INTO meds (user_id, name, dosage, time, repeat_daily, start_date, end_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session["user_id"],
                name,
                dosage if dosage else None,
                time,
                repeat_daily,
                start_date if start_date else None,
                end_date if end_date else None,
                notes if notes else None
            )
        )
        db.commit()

        return redirect("/")

    return render_template("add.html")


@app.route("/delete/<int:id>")
def delete(id):
    if "user_id" not in session:
        return redirect("/login")

    db = get_db()
    db.execute(
        "DELETE FROM meds WHERE id = ? AND user_id = ?",
        (id, session["user_id"])
    )
    db.commit()
    return redirect("/")

@app.route("/delete_log/<int:log_id>", methods=["POST"])
def delete_log(log_id):
    if "user_id" not in session:
        return redirect("/login")

    db = get_db()
    db.execute("""
        DELETE FROM logs
        WHERE id = ?
          AND med_id IN (
              SELECT id FROM meds WHERE user_id = ?
          )
    """, (log_id, session["user_id"]))
    db.commit()
    return redirect("/history")


@app.route("/take/<int:id>")
def take(id):
    db = get_db()

    sg = pytz.timezone("Asia/Singapore")
    current_time = datetime.now(sg)
    ts = current_time.strftime("%Y-%m-%d %H:%M:%S")
    now = current_time.strftime("%H:%M")
    today = current_time.strftime("%Y-%m-%d")

    med = db.execute(
        "SELECT * FROM meds WHERE id = ? AND user_id = ?",
        (id, session["user_id"])
    ).fetchone()

    if not med:
        return redirect("/")

    action = "taken_late" if med["time"] < now else "taken"

    db.execute("UPDATE meds SET taken = 1 WHERE id = ?", (id,))

    db.execute("""
        DELETE FROM logs
        WHERE med_id = ?
          AND action = 'missed'
          AND date(ts) = ?
    """, (id, today))

    db.execute(
        "INSERT INTO logs (med_id, action, ts) VALUES (?, ?, ?)",
        (id, action, ts)
    )

    db.commit()
    return redirect("/")

@app.route("/api/schedule/today")
def api_schedule_today():
    if "user_id" not in session:
        return jsonify([]), 401

    db = get_db()
    meds = db.execute(
        "SELECT id, name, time, taken FROM meds WHERE user_id = ? ORDER BY time ASC",
        (session["user_id"],)
    ).fetchall()

    data = []
    for m in meds:
        data.append({
            "id": m["id"],
            "name": m["name"],
            "time": m["time"],
            "taken": m["taken"]
        })

    return jsonify(data)


@app.route("/api/take/<int:id>", methods=["POST"])
def api_take(id):
    if "user_id" not in session:
        return jsonify({"ok": False, "error": "Unauthorized"}), 401

    db = get_db()

    med = db.execute(
        "SELECT * FROM meds WHERE id = ? AND user_id = ?",
        (id, session["user_id"])
    ).fetchone()

    if not med:
        return jsonify({"ok": False, "error": "Medication not found"}), 404

    sg = pytz.timezone("Asia/Singapore")
    current_time = datetime.now(sg)
    ts = current_time.strftime("%Y-%m-%d %H:%M:%S")
    now = current_time.strftime("%H:%M")
    today = current_time.strftime("%Y-%m-%d")

    action = "taken_late" if med["time"] < now else "taken"

    db.execute("UPDATE meds SET taken = 1 WHERE id = ?", (id,))
    db.execute("""
        DELETE FROM logs
        WHERE med_id = ?
          AND action = 'missed'
          AND date(ts) = ?
    """, (id, today))
    db.execute(
        "INSERT INTO logs (med_id, action, ts) VALUES (?, ?, ?)",
        (id, action, ts)
    )
    db.commit()

    return jsonify({"ok": True, "id": id})

@app.route("/device")
def device():
    return render_template("device.html")

@app.route("/api/health")
def api_health():
    return jsonify({"ok": True})

@app.route("/history")
def history():
    if "user_id" not in session:
        return redirect("/login")

    db = get_db()
    rows = db.execute("""
        SELECT logs.ts, logs.action, logs.id,
               COALESCE(meds.name, '[Deleted medication]') AS name,
               meds.time,
               meds.dosage
        FROM logs
        LEFT JOIN meds ON meds.id = logs.med_id
        WHERE logs.med_id IN (
            SELECT id FROM meds WHERE user_id = ?
        )
        OR meds.user_id = ?
        ORDER BY logs.ts DESC
        LIMIT 50
    """, (session["user_id"], session["user_id"])).fetchall()

    return render_template("history.html", rows=rows)

@app.route("/clear_history", methods=["POST"])
def clear_history():
    if "user_id" not in session:
        return redirect("/login")

    db = get_db()
    db.execute("""
        DELETE FROM logs
        WHERE med_id IN (
            SELECT id FROM meds WHERE user_id = ?
        )
    """, (session["user_id"],))
    db.commit()
    return redirect("/history")

def daily_rollover():
    sg = pytz.timezone("Asia/Singapore")
    today = datetime.now(sg).strftime("%Y-%m-%d")
    db = get_db()

    row = db.execute("SELECT value FROM app_state WHERE key = 'last_rollover'").fetchone()
    last = row["value"] if row else None

    if last != today:
        db.execute("UPDATE meds SET taken = 0 WHERE repeat_daily = 1")
        db.execute(
            "INSERT OR REPLACE INTO app_state (key, value) VALUES ('last_rollover', ?)",
            (today,)
        )
        db.commit()

    return render_template("history.html", rows=row)

@app.route("/edit/<int:med_id>", methods=["GET", "POST"])
def edit(med_id):
    db = get_db()
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        dosage = request.form.get("dosage", "").strip()
        time = request.form.get("time", "").strip()
        repeat_daily = 1 if request.form.get("repeat_daily") else 0
        start_date = request.form.get("start_date", "").strip()
        end_date = request.form.get("end_date", "").strip()
        notes = request.form.get("notes", "").strip()

        db.execute(
            """
            UPDATE meds
            SET name=?, dosage=?, time=?, repeat_daily=?, start_date=?, end_date=?, notes=?
            WHERE id=? AND user_id=?
            """,
            (
                name,
                dosage if dosage else None,
                time,
                repeat_daily,
                start_date if start_date else None,
                end_date if end_date else None,
                notes if notes else None,
                med_id,
                session["user_id"]
            )
        )
        db.commit()

        return redirect("/")

    med = db.execute(
        "SELECT * FROM meds WHERE id = ? AND user_id = ?",
        (med_id, session["user_id"])
    ).fetchone()

    if not med:
        return redirect("/")

    return render_template("edit.html", med=med)


@app.route("/analytics")
def analytics():
    db = get_db()
    if "user_id" not in session:
        return redirect("/login")

    taken = db.execute("""
    SELECT COUNT(*) AS count
    FROM logs
    JOIN meds ON meds.id = logs.med_id
    WHERE action IN ('taken','taken_late')
    AND meds.user_id = ?
    """, (session["user_id"],)).fetchone()["count"]

    missed = db.execute("""
    SELECT COUNT(*) AS count
    FROM logs
    JOIN meds ON meds.id = logs.med_id
    WHERE action = 'missed'
    AND meds.user_id = ?
    """, (session["user_id"],)).fetchone()["count"]

    total = taken + missed
    adherence = round((taken / total) * 100, 1) if total > 0 else 0

    recent_logs = db.execute("""
    SELECT logs.ts, logs.action,
           COALESCE(meds.name, '[Deleted medication]') AS name,
           meds.time,
           meds.dosage
    FROM logs
    LEFT JOIN meds ON meds.id = logs.med_id
    WHERE meds.user_id = ?
    ORDER BY logs.ts DESC
    LIMIT 20
    """, (session["user_id"],)).fetchall()

    return render_template(
        "analytics.html",
        taken=taken,
        missed=missed,
        total=total,
        adherence=adherence,
        recent_logs=recent_logs
    )

def log_missed_doses():
    if "user_id" not in session:
        return

    db = get_db()

    sg = pytz.timezone("Asia/Singapore")
    current_time = datetime.now(sg)
    today = current_time.strftime("%Y-%m-%d")
    now = current_time.strftime("%H:%M")
    ts = current_time.strftime("%Y-%m-%d %H:%M:%S")

    overdue_meds = db.execute("""
        SELECT id
        FROM meds
        WHERE user_id = ?
          AND taken = 0
          AND time < ?
    """, (session["user_id"], now)).fetchall()

    for med in overdue_meds:
        already_logged = db.execute("""
            SELECT 1
            FROM logs
            WHERE med_id = ?
              AND action = 'missed'
              AND date(ts) = ?
        """, (med["id"], today)).fetchone()

        if not already_logged:
            db.execute(
                "INSERT INTO logs (med_id, action, ts) VALUES (?, ?, ?)",
                (med["id"], "missed", ts)
            )

    db.commit()

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return render_template("register.html", error="Missing fields")

        db = get_db()

        try:
            db.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, generate_password_hash(password))
            )
            db.commit()
        except:
            return render_template("register.html", error="Username already exists")

        return redirect("/login")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        db = get_db()

        user = db.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        if not user or not check_password_hash(user["password_hash"], password):
            return render_template("login.html", error="Invalid login")

        session["user_id"] = user["id"]

        return redirect("/")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ▶️ Run app
if __name__ == "__main__":
    app.run(debug=True)

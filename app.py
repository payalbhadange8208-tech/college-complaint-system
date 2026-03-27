from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

college = "Matoshri College of Engineering and Research Centre, Nashik"

def get_db():
    return sqlite3.connect("database.db", check_same_thread=False)

def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        password TEXT,
        role TEXT
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS complaints(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_name TEXT,
        complaint TEXT
    )""")

    conn.commit()
    conn.close()

init_db()

# ✅ CREATE ADMIN
def create_admin():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("DELETE FROM users WHERE role='admin'")
    cur.execute("INSERT INTO users(name,email,password,role) VALUES(?,?,?,?)",
                ("Admin","payalbhadange806@gmail.com","Payal@1234","admin"))

    conn.commit()
    conn.close()

create_admin()

# ------------------ ROUTES ------------------

@app.route("/")
def home():
    return render_template("login.html", college=college)

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO users(name,email,password,role) VALUES(?,?,?,?)",
                    (name,email,password,"student"))
        conn.commit()
        conn.close()

        return redirect("/")
    return render_template("register.html", college=college)

@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email=? AND password=?", (email,password))
    user = cur.fetchone()
    conn.close()

    if user:
        session["name"] = user[1]
        session["role"] = user[4]

        if user[4] == "admin":
            return redirect("/admin")
        else:
            return redirect("/user")
    else:
        return "Login Failed"

# ✅ FIXED USER ROUTE
@app.route("/user")
def user():
    if "name" not in session:
        return redirect("/")
    return render_template("user_dashboard.html", name=session["name"], college=college)

@app.route("/complaint", methods=["GET","POST"])
def complaint():
    if "name" not in session:
        return redirect("/")

    if request.method == "POST":
        comp = request.form["complaint"]

        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO complaints(student_name,complaint) VALUES(?,?)",
                    (session["name"], comp))
        conn.commit()
        conn.close()

        return "Complaint Submitted Successfully"

    return render_template("complaint_form.html", college=college)

# ✅ FIXED ADMIN ROUTE
@app.route("/admin")
def admin():
    if "name" not in session or session.get("role") != "admin":
        return redirect("/")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM complaints")
    data = cur.fetchall()
    conn.close()

    return render_template("admin_dashboard.html", data=data, college=college)

# 🔴 DELETE FEATURE
@app.route("/delete/<int:id>")
def delete(id):
    if "name" not in session or session.get("role") != "admin":
        return redirect("/")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM complaints WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/admin")

# ✅ RUN FOR RENDER
app.run(host='0.0.0.0', port=10000)
    return redirect("/admin")

# ✅ RUN FOR RENDER
app.run(host='0.0.0.0', port=10000)

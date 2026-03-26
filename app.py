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

@app.route("/user")
def user():
    return render_template("user_dashboard.html", name=session["name"], college=college)

@app.route("/complaint", methods=["GET","POST"])
def complaint():
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

@app.route("/admin")
def admin():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM complaints")
    data = cur.fetchall()
    conn.close()

    return render_template("admin_dashboard.html", data=data, college=college)

# 🔴 DELETE FEATURE
@app.route("/delete/<int:id>")
def delete(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM complaints WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/admin")

app.run(debug=True)
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from contextlib import contextmanager

app = Flask(__name__)
DB_PATH = "database.db"

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)")
        conn.commit()

init_db()

@app.route("/")
def home():
    with get_db() as conn:
        users = conn.execute("SELECT * FROM users").fetchall()
    return render_template("index.html", users=users)

@app.route("/save", methods=["POST"])
def save():
    name = request.form["name"]
    with get_db() as conn:
        conn.execute("INSERT INTO users (name) VALUES (?)", (name,))
        conn.commit()
    return redirect(url_for("home"))

@app.route("/update/<int:id>", methods=["POST"])
def update(id):
    name = request.form["name"]
    with get_db() as conn:
        conn.execute("UPDATE users SET name = ? WHERE id = ?", (name, id))
        conn.commit()
    return redirect(url_for("home"))

@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    with get_db() as conn:
        conn.execute("DELETE FROM users WHERE id = ?", (id,))
        conn.commit()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
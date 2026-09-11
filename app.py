from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash
from werkzeug.security import generate_password_hash, check_password_hash
from fpdf import FPDF
import io
import sqlite3

app = Flask(__name__)
app.secret_key = "super_secret_saas_key_change_in_production"

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect("quotes.db")
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # Quotes table linked to user_id
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            client TEXT,
            gross TEXT,
            expenses TEXT,
            tax TEXT,
            take_home TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- HELPER DATABASE FUNCTIONS ---
def save_quote_to_db(user_id, client, gross, expenses, tax, take_home):
    conn = sqlite3.connect("quotes.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO quotes (user_id, client, gross, expenses, tax, take_home)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, client, gross, expenses, tax, take_home))
    conn.commit()
    conn.close()

def get_user_quotes(user_id):
    conn = sqlite3.connect("quotes.db")
    cursor = conn.cursor()
    cursor.execute('SELECT client, gross, expenses, tax, take_home FROM quotes WHERE user_id = ? ORDER BY id DESC', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

# --- AUTH ROUTES ---
@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username").strip().lower()
    password = request.form.get("password")
    hashed_pw = generate_password_hash(password)

    try:
        conn = sqlite3.connect("quotes.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
        conn.commit()
        conn.close()
        flash("Registration successful! Please log in.", "success")
    except sqlite3.IntegrityError:
        flash("Username already exists! Choose another.", "danger")

    return redirect(url_for("home"))

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username").strip().lower()
    password = request.form.get("password")

    conn = sqlite3.connect("quotes.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user[1], password):
        session["user_id"] = user[0]
        session["username"] = username
        flash("Welcome back!", "success")
    else:
        flash("Invalid username or password!", "danger")

    return redirect(url_for("home"))

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))

# --- MAIN DASHBOARD ROUTE ---
@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    user_quotes = []

    if "user_id" in session:
        user_quotes = get_user_quotes(session["user_id"])

        if request.method == "POST":
            client_name = request.form.get("client_name")
            hourly_rate = float(request.form.get("hourly_rate", 0))
            hours = float(request.form.get("hours", 0))
            expenses = float(request.form.get("expenses", 0))

            gross_income = hourly_rate * hours
            net_profit = gross_income - expenses
            tax_estimate = net_profit * 0.20
            take_home = net_profit - tax_estimate

            gross_str = f"${gross_income:,.2f}"
            expenses_str = f"${expenses:,.2f}"
            tax_str = f"${tax_estimate:,.2f}"
            take_home_str = f"${take_home:,.2f}"

            result = {
                "client": client_name,
                "gross": gross_str,
                "expenses": expenses_str,
                "tax": tax_str,
                "take_home": take_home_str
            }

            # Save quote under logged-in user's ID
            save_quote_to_db(session["user_id"], client_name, gross_str, expenses_str, tax_str, take_home_str)
            user_quotes = get_user_quotes(session["user_id"])

    return render_template("index.html", result=result, history=user_quotes)

@app.route("/download_pdf", methods=["POST"])
def download_pdf():
    client = request.form.get("client")
    gross = request.form.get("gross")
    expenses = request.form.get("expenses")
    tax = request.form.get("tax")
    take_home = request.form.get("take_home")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=18, style="B")
    pdf.cell(0, 12, txt="OFFICIAL PROJECT QUOTE", ln=True, align="C")
    
    pdf.set_font("Helvetica", size=10)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 6, txt="Generated via Freelance Quote Tool", ln=True, align="C")
    pdf.ln(6)

    pdf.set_draw_color(200, 200, 200)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(8)

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", size=12, style="B")
    pdf.cell(0, 10, txt=f"Client / Project: {client}", ln=True)
    pdf.ln(4)

    pdf.set_font("Helvetica", size=11)
    pdf.cell(100, 8, txt="Gross Project Total:", border=0)
    pdf.cell(90, 8, txt=f"{gross}", border=0, ln=True, align="R")

    pdf.cell(100, 8, txt="Estimated Direct Expenses:", border=0)
    pdf.cell(90, 8, txt=f"-{expenses}", border=0, ln=True, align="R")

    pdf.cell(100, 8, txt="Estimated Taxes (20%):", border=0)
    pdf.cell(90, 8, txt=f"-{tax}", border=0, ln=True, align="R")

    pdf.ln(6)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(8)

    pdf.set_font("Helvetica", size=14, style="B")
    pdf.set_text_color(39, 174, 96)
    pdf.cell(100, 10, txt="Estimated Net Take-Home:", border=0)
    pdf.cell(90, 10, txt=f"{take_home}", border=0, ln=True, align="R")

    pdf_bytes = pdf.output()
    buffer = io.BytesIO(pdf_bytes)
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"Quote_{client.replace(' ', '_')}.pdf",
        mimetype="application/pdf"
    )

if __name__ == "__main__":
    app.run(debug=True)
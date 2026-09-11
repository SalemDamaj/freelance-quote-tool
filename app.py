from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash
from werkzeug.security import generate_password_hash, check_password_hash
from fpdf import FPDF
import io
import os
import sqlite3
from datetime import datetime

# Import PostgreSQL library if on cloud
try:
    import psycopg2
except ImportError:
    psycopg2 = None

app = Flask(__name__)
app.secret_key = "super_secret_saas_key_change_in_production"

YOUR_WHISH_PHONE = "+961 70 041 203"
YOUR_WHISH_NAME = "Salem Damaj"
PRO_PLAN_PRICE = "$10.00 Fresh USD"

# Check if running on Cloud with PostgreSQL
DATABASE_URL = os.environ.get("DATABASE_URL")

# --- TRANSLATION DICTIONARIES ---
TRANSLATIONS = {
    "en": {
        "app_title": "💼 QuoteSaaS 🇱🇧",
        "welcome": "Welcome",
        "pro_badge": "PRO PLAN",
        "free_badge": "FREE PLAN",
        "admin_link": "Admin Panel",
        "logout": "Logout",
        "login": "Login",
        "register": "Register",
        "username": "Username",
        "password": "Password",
        "login_btn": "Log In",
        "register_btn": "Create Account",
        "whish_title": "⚡ Upgrade to PRO via Whish Money",
        "whish_desc": "Unlock Unlimited PDF Downloads and official quote exports!",
        "whish_step1": "Send 10.00 Fresh USD via Whish Money App to:",
        "whish_step2": "Enter your Whish Transfer Reference # below:",
        "whish_ref_ph": "e.g. Ref # / Transaction ID",
        "whish_submit": "Submit Whish Reference",
        "create_quote_title": "Create Project Quote",
        "client_label": "Client / Project Name:",
        "rate_label": "Hourly Rate ($):",
        "hours_label": "Estimated Hours:",
        "expenses_label": "Direct Project Expenses ($):",
        "calc_btn": "Calculate & Save Quote",
        "summary_title": "Summary for",
        "gross_label": "Gross Quote:",
        "expenses_summary": "Expenses:",
        "tax_label": "Estimated Tax (20%):",
        "takehome_label": "Estimated Take-Home:",
        "download_pdf_btn": "📥 Download PDF Quote",
        "pdf_locked": "🔒 PDF Downloads are locked. Upgrade to PRO via Whish Money above!",
        "history_title": "📜 Saved Quotes History",
        "no_history": "No quotes saved yet.",
        "th_client": "Client",
        "th_gross": "Gross",
        "th_expenses": "Expenses",
        "th_tax": "Tax",
        "th_takehome": "Take-Home"
    },
    "ar": {
        "app_title": "💼 تسعير المشاريع 🇱🇧",
        "welcome": "أهلاً بك",
        "pro_badge": "الحساب الاحترافي PRO",
        "free_badge": "الحساب المجاني",
        "admin_link": "لوحة الأدمن",
        "logout": "تسجيل الخروج",
        "login": "تسجيل الدخول",
        "register": "إنشاء حساب جديد",
        "username": "اسم المستخدم",
        "password": "كلمة المرور",
        "login_btn": "دخول",
        "register_btn": "إنشاء الحساب",
        "whish_title": "⚡ الترقية إلى الحساب الاحترافي عبر Whish Money",
        "whish_desc": "افتح صلاحية تحميل عروض الأسعار بصيغة PDF بدون حدود!",
        "whish_step1": "أرسل 10.00 دولار كاش (Fresh USD) عبر Whish إلى:",
        "whish_step2": "أدخل رقم المرجع (Reference #) للتحويل أدناه:",
        "whish_ref_ph": "مثال: رقم المرجع / Transaction ID",
        "whish_submit": "إرسال رقم المرجع لتأكيد الدفع",
        "create_quote_title": "إنشاء عرض سعر للمشروع",
        "client_label": "اسم العميل / المشروع:",
        "rate_label": "سعر الساعة ($):",
        "hours_label": "عدد الساعات المتوقعة:",
        "expenses_label": "المصاريف المباشرة للمشروع ($):",
        "calc_btn": "حساب وحفظ عرض السعر",
        "summary_title": "ملخص عرض السعر لـ",
        "gross_label": "إجمالي القيمة:",
        "expenses_summary": "المصاريف:",
        "tax_label": "الضريبة التقديرية (20%):",
        "takehome_label": "الربح الصافي التقديري:",
        "download_pdf_btn": "📥 تحميل عرض السعر PDF",
        "pdf_locked": "🔒 تحميل الـ PDF مقفل. قم بالترقية عبر Whish Money أعلاه!",
        "history_title": "📜 سجل العروض المحفوظة",
        "no_history": "لا توجد عروض محفوظة حتى الآن.",
        "th_client": "العميل",
        "th_gross": "الإجمالي",
        "th_expenses": "المصاريف",
        "th_tax": "الضريبة",
        "th_takehome": "الصافي"
    }
}

# --- UNIVERSAL DB HELPER ---
def get_db():
    if DATABASE_URL and psycopg2:
        # Connect to PostgreSQL on Render
        conn = psycopg2.connect(DATABASE_URL, sslmode="require")
        return conn, "pg"
    else:
        # Connect to SQLite Locally
        conn = sqlite3.connect("quotes.db")
        return conn, "sqlite"

def execute_query(conn, db_type, query, params=()):
    cursor = conn.cursor()
    if db_type == "pg":
        query = query.replace("?", "%s")
        query = query.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY")
        cursor.execute(query, params)
    else:
        cursor.execute(query, params)
    return cursor

def init_db():
    conn, db_type = get_db()
    
    execute_query(conn, db_type, '''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_pro INTEGER DEFAULT 0,
            is_admin INTEGER DEFAULT 0
        )
    ''')
    
    execute_query(conn, db_type, '''
        CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            client TEXT,
            gross TEXT,
            expenses TEXT,
            tax TEXT,
            take_home TEXT
        )
    ''')

    execute_query(conn, db_type, '''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            whish_ref TEXT NOT NULL,
            amount TEXT NOT NULL,
            status TEXT DEFAULT 'PENDING',
            created_at TEXT NOT NULL
        )
    ''')

    cur = execute_query(conn, db_type, "SELECT * FROM users WHERE username = 'admin'")
    if not cur.fetchone():
        admin_pw = generate_password_hash("admin123")
        execute_query(conn, db_type, "INSERT INTO users (username, password, is_pro, is_admin) VALUES ('admin', ?, 1, 1)", (admin_pw,))
    
    conn.commit()
    conn.close()

init_db()

def get_user_by_id(user_id):
    try:
        conn, db_type = get_db()
        cur = execute_query(conn, db_type, "SELECT id, username, is_pro, is_admin FROM users WHERE id = ?", (user_id,))
        user = cur.fetchone()
        conn.close()
        return user
    except Exception:
        return None

def save_quote_to_db(user_id, client, gross, expenses, tax, take_home):
    conn, db_type = get_db()
    execute_query(conn, db_type, '''
        INSERT INTO quotes (user_id, client, gross, expenses, tax, take_home)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, client, gross, expenses, tax, take_home))
    conn.commit()
    conn.close()

def get_user_quotes(user_id):
    conn, db_type = get_db()
    cur = execute_query(conn, db_type, 'SELECT client, gross, expenses, tax, take_home FROM quotes WHERE user_id = ? ORDER BY id DESC', (user_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

@app.route("/toggle_language")
def toggle_language():
    current_lang = session.get("lang", "en")
    session["lang"] = "ar" if current_lang == "en" else "en"
    return redirect(request.referrer or url_for("home"))

@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username", "").strip().lower()
    password = request.form.get("password", "")
    if not username or not password:
        flash("Username and password required!", "danger")
        return redirect(url_for("home"))

    hashed_pw = generate_password_hash(password)
    try:
        conn, db_type = get_db()
        execute_query(conn, db_type, "INSERT INTO users (username, password, is_pro, is_admin) VALUES (?, ?, 0, 0)", (username, hashed_pw))
        conn.commit()
        conn.close()
        flash("Registration successful! Please log in.", "success")
    except Exception:
        flash("Username already exists or registration failed!", "danger")

    return redirect(url_for("home"))

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "").strip().lower()
    password = request.form.get("password", "")

    conn, db_type = get_db()
    cur = execute_query(conn, db_type, "SELECT id, password FROM users WHERE username = ?", (username,))
    user = cur.fetchone()
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
    flash("Logged out successfully.", "info")
    return redirect(url_for("home"))

@app.route("/submit_whish_payment", methods=["POST"])
def submit_whish_payment():
    if "user_id" not in session:
        return redirect(url_for("home"))

    whish_ref = request.form.get("whish_ref", "").strip()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    conn, db_type = get_db()
    execute_query(conn, db_type, '''
        INSERT INTO payments (user_id, username, whish_ref, amount, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (session["user_id"], session["username"], whish_ref, PRO_PLAN_PRICE, now_str))
    conn.commit()
    conn.close()

    flash("Payment Reference Submitted! Verification in progress.", "info")
    return redirect(url_for("home"))

@app.route("/admin")
def admin_panel():
    if "user_id" not in session:
        return redirect(url_for("home"))
    
    current_user = get_user_by_id(session["user_id"])
    if not current_user or current_user[3] != 1:
        flash("Access Denied!", "danger")
        return redirect(url_for("home"))

    conn, db_type = get_db()
    cur = execute_query(conn, db_type, "SELECT id, user_id, username, whish_ref, amount, status, created_at FROM payments ORDER BY id DESC")
    all_payments = cur.fetchall()
    conn.close()

    return render_template("admin.html", payments=all_payments)

@app.route("/admin/approve/<int:payment_id>")
def approve_payment(payment_id):
    if "user_id" not in session:
        return redirect(url_for("home"))
    
    current_user = get_user_by_id(session["user_id"])
    if not current_user or current_user[3] != 1:
        return redirect(url_for("home"))

    conn, db_type = get_db()
    cur = execute_query(conn, db_type, "SELECT user_id FROM payments WHERE id = ?", (payment_id,))
    pay = cur.fetchone()
    if pay:
        user_to_upgrade = pay[0]
        execute_query(conn, db_type, "UPDATE payments SET status = 'APPROVED' WHERE id = ?", (payment_id,))
        execute_query(conn, db_type, "UPDATE users SET is_pro = 1 WHERE id = ?", (user_to_upgrade,))
        conn.commit()
        flash(f"Payment #{payment_id} Approved! User upgraded to PRO 🎉", "success")

    conn.close()
    return redirect(url_for("admin_panel"))

@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    user_quotes = []
    user_info = None

    lang = session.get("lang", "en")
    t = TRANSLATIONS.get(lang, TRANSLATIONS["en"])

    if "user_id" in session:
        user_info = get_user_by_id(session["user_id"])
        if not user_info:
            session.clear()
            return redirect(url_for("home"))

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

            save_quote_to_db(session["user_id"], client_name, gross_str, expenses_str, tax_str, take_home_str)
            user_quotes = get_user_quotes(session["user_id"])

    return render_template(
        "index.html",
        result=result,
        history=user_quotes,
        user=user_info,
        whish_phone=YOUR_WHISH_PHONE,
        whish_name=YOUR_WHISH_NAME,
        price=PRO_PLAN_PRICE,
        t=t,
        lang=lang
    )

@app.route("/download_pdf", methods=["POST"])
def download_pdf():
    if "user_id" not in session:
        flash("Please log in to download PDFs.", "danger")
        return redirect(url_for("home"))

    user_info = get_user_by_id(session["user_id"])
    if not user_info or user_info[2] != 1:
        flash("PDF Export is a PRO Feature!", "danger")
        return redirect(url_for("home"))

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
    pdf.cell(0, 6, txt="Generated via Freelance Quote Tool Pro", ln=True, align="C")
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
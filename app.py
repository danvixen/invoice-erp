import streamlit as st
import sqlite3
import google.generativeai as genai
import json
import os
import pandas as pd
import hashlib
import random
import secrets
import socket
import imaplib
import email
from email.header import decode_header
from datetime import date, timedelta
import notifier

# ==================== ХРАНИЛИЩЕ И СЕТЬ ====================
STORAGE_DIR = r"C:\invoice_assistant\storage"
ADMIN_EMAIL = "aleksei.gusev@mail.ee"

def get_public_url():
    if os.path.exists(r"C:\invoice_assistant\tunnel_url.txt"):
        try:
            with open(r"C:\invoice_assistant\tunnel_url.txt", "r", encoding="utf-8") as f:
                url = f.read().strip()
                if url:
                    return url
        except Exception:
            pass
    return "https://estates-victoria-inspection-considerable.trycloudflare.com"

PUBLIC_URL = get_public_url()

st.set_page_config(
    page_title="Invoice ERP • Finance Hub",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== СТИЛИЗАЦИЯ И ДИЗАЙН (CSS) ====================
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
}

.main .block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    max-width: 1400px;
}

h1, h2, h3, h4 {
    font-weight: 700 !important;
    letter-spacing: -0.02em;
}

/* Карточки KPI вверху */
[data-testid="stMetric"] {
    background: linear-gradient(145deg, rgba(30, 41, 59, 0.5) 0%, rgba(15, 23, 42, 0.7) 100%);
    border: 1px solid rgba(148, 163, 184, 0.15);
    border-radius: 12px;
    padding: 14px 18px;
    box-shadow: 0 4px 18px rgba(0,0,0,0.2);
}
[data-testid="stMetricLabel"] {
    font-size: 12px !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #94a3b8 !important;
}
[data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace;
    font-weight: 800 !important;
    color: #f8fafc !important;
    font-size: 24px !important;
}

/* Карточка счета */
.invoice-card {
    background: linear-gradient(145deg, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.8) 100%);
    border: 1px solid rgba(148, 163, 184, 0.16);
    border-radius: 12px;
    padding: 14px 18px;
    margin-bottom: 8px;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.15);
}

.invoice-header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 6px;
}

.invoice-sender {
    font-size: 16px;
    font-weight: 700;
    color: #f1f5f9;
}

.invoice-amount {
    font-family: 'JetBrains Mono', monospace;
    font-size: 19px;
    font-weight: 800;
    color: #38bdf8;
}

.invoice-meta {
    font-size: 12.5px;
    color: #94a3b8;
    margin-bottom: 4px;
    display: flex;
    gap: 14px;
    align-items: center;
    flex-wrap: wrap;
}

.invoice-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 5px;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
.badge-pending { background: rgba(234, 179, 8, 0.18); color: #fde047; border: 1px solid rgba(234, 179, 8, 0.4); }
.badge-paid { background: rgba(34, 197, 94, 0.18); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.4); }
.badge-archived { background: rgba(148, 163, 184, 0.15); color: #cbd5e1; border: 1px solid rgba(148, 163, 184, 0.3); }

/* АККУРАТНЫЕ ПЛАШКИ IBAN И VIITENUMBER С ВЫДЕЛЕНИЕМ И КОПИРОВАНИЕМ МЫШКОЙ */
.req-container {
    display: inline-flex;
    align-items: stretch;
    background: #090e1c;
    border: 1px solid rgba(56, 189, 248, 0.35);
    border-radius: 8px;
    margin: 6px 0 8px 0;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    max-width: 100%;
}

.req-pill {
    display: flex;
    flex-direction: column;
    padding: 6px 14px;
}

.req-tag {
    font-size: 10px;
    font-weight: 800;
    color: #38bdf8;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-bottom: 2px;
    user-select: none;
}

.req-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 13.5px;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: 0.03em;
    user-select: all !important;
    -webkit-user-select: all !important;
    cursor: text !important;
}

.req-sep {
    width: 1px;
    background: rgba(148, 163, 184, 0.22);
}

/* Банки-чипы */
.bank-chip {
    display: inline-flex;
    align-items: center;
    padding: 3px 9px;
    border-radius: 5px;
    font-size: 11.5px;
    font-weight: 700;
    text-decoration: none !important;
    transition: transform 0.15s ease, filter 0.15s ease;
    border: 1px solid transparent;
}
.bank-chip:hover {
    transform: translateY(-1px);
    filter: brightness(1.2);
}
.bank-lhv { background: #000000; color: #ffffff !important; border-color: #334155; }
.bank-swed { background: #ea580c; color: #ffffff !important; }
.bank-seb { background: #16a34a; color: #ffffff !important; }
.bank-coop { background: #0284c7; color: #ffffff !important; }
.bank-luminor { background: #4a044e; color: #ffffff !important; }

/* Кнопки без многоточий */
div[data-testid="column"] button {
    white-space: nowrap !important;
    text-overflow: clip !important;
    overflow: visible !important;
    border-radius: 7px !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    padding: 4px 8px !important;
    min-height: 36px !important;
}

div[data-testid="column"] button p {
    white-space: nowrap !important;
    text-overflow: clip !important;
    overflow: visible !important;
    font-size: 13px !important;
    font-weight: 700 !important;
}

[data-testid="stSidebar"] {
    background-color: #0b1120 !important;
    border-right: 1px solid rgba(255,255,255,0.06);
}

.user-profile-box {
    background: linear-gradient(135deg, rgba(56, 189, 248, 0.12) 0%, rgba(99, 102, 241, 0.06) 100%);
    border: 1px solid rgba(56, 189, 248, 0.25);
    border-radius: 12px;
    padding: 12px 15px;
    margin-bottom: 18px;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AQ.Ab8RN6KlxXOXSAI2MKVgKI_NBphJmXb4ben_A9-PKqOOSZbZvg")
genai.configure(api_key=GEMINI_API_KEY)

def get_lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "localhost"

# ==================== БАЗА ДАННЫХ И МИГРАЦИИ ====================
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def init_db():
    conn = sqlite3.connect("invoices_local.db", check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            is_active INTEGER DEFAULT 1,
            approval_token TEXT,
            imap_server TEXT,
            imap_port INTEGER DEFAULT 993,
            imap_user TEXT,
            imap_password TEXT,
            imap_folder TEXT DEFAULT 'INBOX'
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            payer TEXT DEFAULT 'Основной плательщик',
            sender TEXT,
            amount REAL,
            due_date TEXT,
            status TEXT DEFAULT 'Ожидает оплаты',
            paid_date TEXT,
            created_by TEXT,
            file_path TEXT,
            iban TEXT,
            ref_number TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS reset_tokens (
            email TEXT PRIMARY KEY,
            token TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cur.execute("PRAGMA table_info(users)")
    u_cols = [c[1] for c in cur.fetchall()]
    if "is_active" not in u_cols:
        cur.execute("ALTER TABLE users ADD COLUMN is_active INTEGER DEFAULT 1")
    if "approval_token" not in u_cols:
        cur.execute("ALTER TABLE users ADD COLUMN approval_token TEXT")
    for col in ["imap_server", "imap_user", "imap_password", "imap_folder"]:
        if col not in u_cols:
            cur.execute(f"ALTER TABLE users ADD COLUMN {col} TEXT")
    if "imap_port" not in u_cols:
        cur.execute("ALTER TABLE users ADD COLUMN imap_port INTEGER DEFAULT 993")

    cur.execute("PRAGMA table_info(invoices)")
    i_cols = [c[1] for c in cur.fetchall()]
    if "file_path" not in i_cols:
        cur.execute("ALTER TABLE invoices ADD COLUMN file_path TEXT")
    if "iban" not in i_cols:
        cur.execute("ALTER TABLE invoices ADD COLUMN iban TEXT")
    if "ref_number" not in i_cols:
        cur.execute("ALTER TABLE invoices ADD COLUMN ref_number TEXT")

    cur.execute("SELECT id FROM users WHERE email = 'admin@local'")
    if not cur.fetchone():
        cur.execute(
            "INSERT INTO users (email, password_hash, name, role, is_active) VALUES (?, ?, ?, ?, 1)",
            ("admin@local", hash_password("admin123"), "Главный Администратор", "superadmin")
        )
    conn.commit()
    return conn

conn = init_db()

# ==================== АКТИВАЦИЯ ПО ССЫЛКЕ В 1 КЛИК ====================
approve_token = None
try:
    if "approve" in st.query_params:
        approve_token = st.query_params["approve"]
except Exception:
    params = st.experimental_get_query_params()
    if "approve" in params:
        approve_token = params["approve"][0]

if approve_token:
    cur = conn.cursor()
    cur.execute("SELECT id, name, email FROM users WHERE approval_token = ? AND is_active = 0", (approve_token,))
    pending = cur.fetchone()
    if pending:
        u_id, u_name, u_email = pending
        cur.execute("UPDATE users SET is_active = 1, approval_token = NULL WHERE id = ?", (u_id,))
        conn.commit()
        st.success(f"🎉 Пользователь **{u_name}** ({u_email}) успешно активирован!")
        notify_body = f"<p>Здравствуйте, {u_name}!</p><p>Ваша учетная запись в <b>Invoice ERP</b> активирована.</p>"
        notifier.send_email(u_email, "Доступ в Invoice ERP активирован", notify_body)
    else:
        st.info("ℹ️ Заявка уже была активирована ранее.")
    try:
        del st.query_params["approve"]
    except Exception:
        pass

# ==================== ФАЙЛЫ И GEMINI ====================
def save_file_to_storage(file_bytes: bytes, original_filename: str, sender: str) -> str:
    try:
        os.makedirs(STORAGE_DIR, exist_ok=True)
    except Exception:
        return ""
    safe_sender = "".join([c for c in sender if c.isalnum() or c in (' ', '_', '-')]).strip() or "Invoice"
    timestamp = date.today().strftime("%Y%m%d")
    unique_name = f"{timestamp}_{safe_sender}_{original_filename}"
    full_path = os.path.join(STORAGE_DIR, unique_name)
    counter = 1
    base_name, file_ext = os.path.splitext(unique_name)
    while os.path.exists(full_path):
        full_path = os.path.join(STORAGE_DIR, f"{base_name}_{counter}{file_ext}")
        counter += 1
    try:
        with open(full_path, "wb") as f:
            f.write(file_bytes)
        return full_path
    except Exception:
        return ""

def extract_invoice_data(file_bytes: bytes, mime_type: str):
    model = genai.GenerativeModel("gemini-3.8-flash")
    inline_doc = {"mime_type": mime_type, "data": file_bytes}
    prompt = """
    Извлеки реквизиты и данные из счета/чека. Ответ строго JSON без markdown:
    {
      "payer": "Плательщик",
      "sender": "Поставщик (получатель)",
      "amount": 0.00,
      "due_date": "YYYY-MM-DD",
      "iban": "IBAN получателя без пробелов",
      "reference_number": "Viitenumber без слова Viitenumber"
    }
    """
    resp = model.generate_content([inline_doc, prompt])
    raw = resp.text.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(raw)

def decode_mime_words(s):
    if not s:
        return ""
    parts = decode_header(s)
    res = []
    for frag, enc in parts:
        if isinstance(frag, bytes):
            res.append(frag.decode(enc or "utf-8", errors="ignore"))
        else:
            res.append(str(frag))
    return "".join(res)

def fetch_invoices_via_imap(server, port, user, password, folder, user_email):
    pulled, errors = [], []
    try:
        imap = imaplib.IMAP4_SSL(server, int(port), timeout=15)
        imap.login(user, password)
        status, _ = imap.select(f'"{folder}"' if " " in folder else folder)
        if status != "OK":
            return 0, [f"Папка '{folder}' не найдена."]
        status, search_data = imap.search(None, "UNSEEN")
        if status != "OK" or not search_data[0]:
            imap.logout()
            return 0, []
        for m_id in search_data[0].split():
            res, msg_data = imap.fetch(m_id, "(RFC822)")
            if res != "OK":
                continue
            msg = email.message_from_bytes(msg_data[0][1])
            for part in msg.walk():
                if part.get_content_maintype() == "multipart" or part.get("Content-Disposition") is None:
                    continue
                raw_filename = part.get_filename()
                if not raw_filename:
                    continue
                filename = decode_mime_words(raw_filename).strip()
                ext = os.path.splitext(filename.lower())[1]
                if ext in [".pdf", ".png", ".jpg", ".jpeg"]:
                    f_bytes = part.get_payload(decode=True)
                    if not f_bytes:
                        continue
                    m_type = "application/pdf" if ext == ".pdf" else "image/jpeg"
                    try:
                        data = extract_invoice_data(f_bytes, m_type)
                        s_name = data.get("sender") or "Не указан"
                        amt = float(data.get("amount") or 0.0)
                        d_date = data.get("due_date") or (date.today() + timedelta(days=7)).strftime("%Y-%m-%d")
                        p_name = data.get("payer") or "Основной плательщик"
                        iban_v = (data.get("iban") or "").replace(" ", "").strip()
                        ref_v = (str(data.get("reference_number") or "")).replace(" ", "").strip()
                        s_path = save_file_to_storage(f_bytes, filename, s_name)
                        cur = conn.cursor()
                        cur.execute("""
                            INSERT INTO invoices (payer, sender, amount, due_date, status, created_by, file_path, iban, ref_number)
                            VALUES (?, ?, ?, ?, 'Ожидает оплаты', ?, ?, ?, ?)
                        """, (p_name, s_name, amt, d_date, user_email, s_path, iban_v, ref_v))
                        conn.commit()
                        pulled.append(f"{s_name} ({amt:.2f} €)")
                    except Exception as e:
                        errors.append(f"{filename}: {e}")
        imap.logout()
        return len(pulled), errors
    except Exception as e:
        return 0, [f"Ошибка IMAP: {e}"]

def notify_admin_new_user(name: str, email: str, token: str):
    global_link = f"{PUBLIC_URL}/?approve={token}" if PUBLIC_URL else f"http://{get_lan_ip()}:8501/?approve={token}"
    subject = f"🔔 Новая заявка на регистрацию: {name}"
    html_body = f"""
    <div style="font-family: Arial, sans-serif; color: #2c3e50; line-height: 1.6; max-width: 580px; padding: 20px; border: 1px solid #e2e8f0; border-radius: 10px;">
        <h3 style="color: #0f172a; margin-top: 0;">Новая заявка на доступ в Invoice ERP</h3>
        <p>Сотрудник подал заявку на регистрацию в системе:</p>
        <div style="background: #f8fafc; padding: 12px 16px; border-left: 4px solid #38bdf8; border-radius: 4px; margin: 15px 0;">
            <div style="margin: 3px 0;"><b>Имя:</b> {name}</div>
            <div style="margin: 3px 0;"><b>Email:</b> {email}</div>
        </div>
        <div style="text-align: center; margin: 25px 0;">
            <a href="{global_link}" style="background-color: #10b981; color: white; padding: 12px 26px; text-decoration: none; font-size: 15px; font-weight: bold; border-radius: 6px; display: inline-block;">
                ✅ Активировать доступ в 1 клик
            </a>
        </div>
    </div>
    """
    notifier.send_email(ADMIN_EMAIL, subject, html_body)

# ==================== АВТОРИЗАЦИЯ ====================
if "user" not in st.session_state:
    st.session_state.user = None

def login_user(email, password):
    cur = conn.cursor()
    cur.execute(
        "SELECT id, email, name, role, is_active FROM users WHERE email = ? AND password_hash = ?",
        (email.strip().lower(), hash_password(password))
    )
    return cur.fetchone()

def apply_for_registration(email, password, name):
    cur = conn.cursor()
    try:
        token = secrets.token_urlsafe(16)
        cur.execute(
            "INSERT INTO users (email, password_hash, name, role, is_active, approval_token) VALUES (?, ?, ?, 'user', 0, ?)",
            (email.strip().lower(), hash_password(password), name.strip(), token)
        )
        conn.commit()
        notify_admin_new_user(name.strip(), email.strip().lower(), token)
        return True, "Заявка отправлена! Администратор активирует ваш доступ."
    except sqlite3.IntegrityError:
        return False, "Пользователь с таким email уже существует."

# Экран логина
if not st.session_state.user:
    st.markdown("<div style='text-align: center; margin-top: 50px; margin-bottom: 25px;'><h1 style='font-size: 36px; margin-bottom: 4px;'>💳 Invoice ERP</h1><p style='color: #94a3b8; font-size: 15px;'>Smart Accounts Payable & Invoicing Hub</p></div>", unsafe_allow_html=True)
    _, col_auth, _ = st.columns([1.5, 1.4, 1.5])
    
    with col_auth:
        tab_login, tab_signup = st.tabs(["Вход в систему", "Подать заявку на доступ"])
        
        with tab_login:
            with st.form("login_form"):
                log_email = st.text_input("Рабочий Email:", placeholder="name@firma.ee")
                log_pass = st.text_input("Пароль:", type="password", placeholder="••••••••")
                submit_btn = st.form_submit_button("Войти в кабинет", width='stretch', type="primary")
                if submit_btn:
                    user_data = login_user(log_email, log_pass)
                    if user_data:
                        u_id, u_email, u_name, u_role, u_active = user_data
                        if u_active == 1:
                            st.session_state.user = {"id": u_id, "email": u_email, "name": u_name, "role": u_role}
                            st.rerun()
                        else:
                            st.warning("⏳ Ваша заявка ожидает подтверждения администратором.")
                    else:
                        st.error("Неверный email или пароль.")

            with st.expander("Забыли пароль?"):
                t1, t2 = st.tabs(["Запросить код", "Сменить"])
                with t1:
                    r_email = st.text_input("Email:", key="r_mail")
                    if st.button("Выслать код", width='stretch'):
                        cur = conn.cursor()
                        cur.execute("SELECT id, is_active FROM users WHERE email = ?", (r_email.strip().lower(),))
                        row = cur.fetchone()
                        if row and row[1] == 1:
                            code = str(random.randint(100000, 999999))
                            cur.execute("REPLACE INTO reset_tokens (email, token) VALUES (?, ?)", (r_email.strip().lower(), code))
                            conn.commit()
                            notifier.send_email(r_email.strip().lower(), "Сброс пароля Invoice ERP", f"<p>Код: <b>{code}</b></p>")
                            st.success(f"Код отправлен на {r_email}!")
                        else:
                            st.error("Пользователь не найден или не активен.")
                with t2:
                    v_mail = st.text_input("Email:", key="v_mail")
                    v_code = st.text_input("Код:", key="v_code")
                    v_pass = st.text_input("Новый пароль:", type="password", key="v_pass")
                    if st.button("Сохранить пароль", width='stretch'):
                        cur = conn.cursor()
                        cur.execute("SELECT token FROM reset_tokens WHERE email = ?", (v_mail.strip().lower(),))
                        r = cur.fetchone()
                        if r and r[0] == v_code.strip():
                            cur.execute("UPDATE users SET password_hash = ? WHERE email = ?", (hash_password(v_pass), v_mail.strip().lower()))
                            cur.execute("DELETE FROM reset_tokens WHERE email = ?", (v_mail.strip().lower(),))
                            conn.commit()
                            st.success("Пароль обновлен! Войдите.")
                        else:
                            st.error("Неверный код.")

        with tab_signup:
            with st.form("signup_form"):
                st.caption("Регистрация нового сотрудника в системе:")
                reg_name = st.text_input("Имя и фамилия:")
                reg_email = st.text_input("Рабочий Email:")
                reg_pass = st.text_input("Придумайте пароль:", type="password")
                signup_btn = st.form_submit_button("Отправить заявку", width='stretch', type="primary")
                if signup_btn:
                    if reg_name.strip() and reg_email.strip() and reg_pass:
                        ok, msg = apply_for_registration(reg_email, reg_pass, reg_name)
                        if ok:
                            st.success(msg)
                        else:
                            st.error(msg)
                    else:
                        st.warning("Заполните все поля.")
    st.stop()

current_user = st.session_state.user
if not current_user:
    st.stop()

# ==================== БОКОВАЯ ПАНЕЛЬ ====================
with st.sidebar:
    role_icon = "👑" if current_user['role'] == "superadmin" else "💼"
    role_label = "Главный Администратор" if current_user['role'] == "superadmin" else "Сотрудник"
    
    st.markdown(f"""
    <div class="user-profile-box">
        <div style="font-size: 15px; font-weight: 700; color: #f8fafc; margin-bottom: 2px;">{role_icon} {current_user['name']}</div>
        <div style="font-size: 11.5px; color: #94a3b8; margin-bottom: 7px;">{current_user['email']}</div>
        <span class="invoice-badge" style="background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3);">{role_label}</span>
    </div>
    """, unsafe_allow_html=True)
    
    view_all_users = False
    if current_user["role"] == "superadmin":
        view_all_users = st.toggle("👁️ Режим руководителя (все счета)", value=False)
        st.caption("Сводный просмотр счетов всех сотрудников" if view_all_users else "Отображаются только ваши личные счета")

    if st.button("🚪 Выйти из системы", width='stretch'):
        st.session_state.user = None
        st.rerun()

    # --- НАСТРОЙКИ ПОЧТЫ (IMAP) ---
    st.markdown("<hr style='border-color: rgba(255,255,255,0.08); margin: 16px 0;'>", unsafe_allow_html=True)
    cur = conn.cursor()
    cur.execute("SELECT imap_server, imap_port, imap_user, imap_password, imap_folder FROM users WHERE id = ?", (current_user["id"],))
    u_imap = cur.fetchone()
    
    cur_server = u_imap[0] or "imap.mail.ee"
    cur_port = u_imap[1] or 993
    cur_user = u_imap[2] or current_user["email"]
    cur_pass = u_imap[3] or ""
    cur_folder = u_imap[4] or "INBOX"

    with st.expander("⚙️ Моя почта (IMAP для счетов)"):
        st.caption("Параметры ящика для автоматического скачивания счетов:")
        with st.form("imap_settings_form"):
            new_srv = st.text_input("IMAP Сервер:", value=cur_server)
            new_port = st.number_input("Порт (SSL):", value=int(cur_port), step=1)
            new_usr = st.text_input("Логин/Email:", value=cur_user)
            new_pwd = st.text_input("Пароль приложения:", value=cur_pass, type="password")
            new_fld = st.text_input("Папка для проверки:", value=cur_folder)
            
            if st.form_submit_button("Сохранить параметры", width='stretch'):
                cur.execute("""
                    UPDATE users
                    SET imap_server = ?, imap_port = ?, imap_user = ?, imap_password = ?, imap_folder = ?
                    WHERE id = ?
                """, (new_srv.strip(), int(new_port), new_usr.strip(), new_pwd.strip(), new_fld.strip(), current_user["id"]))
                conn.commit()
                st.success("Настройки сохранены!")
                st.rerun()

    # Панель подтверждения заявок
    if current_user["role"] == "superadmin":
        st.markdown("<hr style='border-color: rgba(255,255,255,0.08); margin: 16px 0;'>", unsafe_allow_html=True)
        cur.execute("SELECT id, name, email FROM users WHERE is_active = 0")
        pending_requests = cur.fetchall()
        req_count = len(pending_requests)
        header_text = f"🔔 Заявки на доступ ({req_count})" if req_count > 0 else "🔔 Заявки на доступ"
        
        with st.expander(header_text, expanded=(req_count > 0)):
            if pending_requests:
                for req in pending_requests:
                    p_id, p_name, p_email = req
                    st.markdown(f"**{p_name}**<br><small style='color: #94a3b8;'>{p_email}</small>", unsafe_allow_html=True)
                    c_appr, c_rej = st.columns(2)
                    if c_appr.button("✅ Одобрить", key=f"appr_{p_id}", width='stretch'):
                        cur.execute("UPDATE users SET is_active = 1, approval_token = NULL WHERE id = ?", (p_id,))
                        conn.commit()
                        st.success(f"{p_name} активирован!")
                        st.rerun()
                    if c_rej.button("❌ Отклонить", key=f"rej_{p_id}", width='stretch'):
                        cur.execute("DELETE FROM users WHERE id = ?", (p_id,))
                        conn.commit()
                        st.warning("Отклонено.")
                        st.rerun()
                    st.markdown("<hr style='margin: 8px 0; border-color: rgba(255,255,255,0.06);'>", unsafe_allow_html=True)
            else:
                st.info("Новых заявок нет.")

# ==================== УВЕДОМЛЕНИЯ О СРОКАХ ====================
def render_reminders():
    today_str = date.today().strftime("%Y-%m-%d")
    tomorrow_str = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    cur = conn.cursor()
    
    user_clause = "" if view_all_users else " AND created_by = ?"
    params_tomorrow = (tomorrow_str,) if view_all_users else (tomorrow_str, current_user["email"])
    params_overdue = (today_str,) if view_all_users else (today_str, current_user["email"])

    cur.execute(f"SELECT id, sender, amount, payer FROM invoices WHERE due_date = ? AND status NOT IN ('Оплачен', 'В архиве'){user_clause}", params_tomorrow)
    due_tomorrow = cur.fetchall()
    
    cur.execute(f"SELECT id, sender, amount, due_date FROM invoices WHERE due_date < ? AND status NOT IN ('Оплачен', 'В архиве'){user_clause}", params_overdue)
    overdue = cur.fetchall()

    if due_tomorrow or overdue:
        for inv in due_tomorrow:
            st.warning(f"⏰ **Срок оплаты завтра ({tomorrow_str}):** Счет #{inv[0]} от **{inv[1]}** на сумму **{inv[2]:.2f} €** (Плательщик: {inv[3]})")
        for inv in overdue:
            st.error(f"🚨 **Просрочен платеж!** Срок был {inv[3]}. Счет #{inv[0]} от **{inv[1]}** на сумму **{inv[2]:.2f} €**")

render_reminders()

# ==================== СТАТИСТИКА (KPI METRICS) ====================
cur = conn.cursor()
user_kpi_filter = "" if view_all_users else f" AND created_by = '{current_user['email']}'"
kpi_df = pd.read_sql_query(f"SELECT amount, status, due_date FROM invoices WHERE status != 'В архиве'{user_kpi_filter}", conn)

m_total = kpi_df["amount"].sum() if not kpi_df.empty else 0.0
m_paid = kpi_df[kpi_df["status"] == "Оплачен"]["amount"].sum() if not kpi_df.empty else 0.0
m_pending = kpi_df[kpi_df["status"] != "Оплачен"]["amount"].sum() if not kpi_df.empty else 0.0

today_iso = date.today().strftime("%Y-%m-%d")
m_overdue = kpi_df[(kpi_df["status"] != "Оплачен") & (kpi_df["due_date"] < today_iso)]["amount"].sum() if not kpi_df.empty else 0.0

col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric("Всего по счетам", f"{m_total:,.2f} €".replace(",", " "))
col_m2.metric("Оплачено", f"{m_paid:,.2f} €".replace(",", " "))
col_m3.metric("К оплате", f"{m_pending:,.2f} €".replace(",", " "))
col_m4.metric("Просрочено", f"{m_overdue:,.2f} €".replace(",", " "), delta=f"-{m_overdue:,.2f} €" if m_overdue > 0 else None, delta_color="inverse")

st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

# ==================== ОСНОВНЫЕ ВКЛАДКИ ====================
tab_registry, tab_archive, tab_senders, tab_payers = st.tabs([
    "🧾 Реестр и обработка",
    "📦 Архив счетов",
    "🏢 Поставщики (Кому)",
    "👤 Плательщики (Кто)"
])

# -------------------- ВКЛАДКА 1: РЕЕСТР И ДОБАВЛЕНИЕ --------------------
with tab_registry:
    col_up, col_table = st.columns([1.0, 2.0])
    
    with col_up:
        st.markdown("<h4 style='margin-bottom: 10px;'>📥 Внести счет</h4>", unsafe_allow_html=True)
        mode = st.radio("Способ добавления:", ["⚡ AI-распознавание файла", "✍️ Вручную", "📧 Стянуть из личной почты"], horizontal=True)
        
        if mode == "⚡ AI-распознавание файла":
            up_file = st.file_uploader("Загрузите PDF или фото счета:", type=["pdf", "png", "jpg", "jpeg"], key="auto_file")
            if up_file and st.button("✨ Распознать и сохранить в реестр", width='stretch', type="primary"):
                with st.spinner("AI анализирует документ и извлекает реквизиты..."):
                    try:
                        raw_bytes = up_file.getvalue()
                        m_type = "application/pdf" if up_file.name.lower().endswith(".pdf") else "image/jpeg"
                        data = extract_invoice_data(raw_bytes, m_type)
                        
                        sender_name = data.get("sender") or "Не указан"
                        amt = float(data.get("amount") or 0.0)
                        d_date = data.get("due_date") or (date.today() + timedelta(days=7)).strftime("%Y-%m-%d")
                        payer_name = data.get("payer") or "Основной плательщик"
                        iban_val = (data.get("iban") or "").replace(" ", "").strip()
                        ref_val = (str(data.get("reference_number") or "")).replace(" ", "").strip()
                        
                        saved_path = save_file_to_storage(raw_bytes, up_file.name, sender_name)
                        
                        cur = conn.cursor()
                        cur.execute("""
                            INSERT INTO invoices (payer, sender, amount, due_date, status, created_by, file_path, iban, ref_number)
                            VALUES (?, ?, ?, ?, 'Ожидает оплаты', ?, ?, ?, ?)
                        """, (payer_name, sender_name, amt, d_date, current_user["email"], saved_path, iban_val, ref_val))
                        conn.commit()
                        st.success(f"Добавлено: {sender_name} | {amt:.2f} €")
                        st.rerun()
                    except Exception as err:
                        st.error(f"Ошибка распознавания: {err}")

        elif mode == "✍️ Вручную":
            with st.form("manual_invoice_form", clear_on_submit=True):
                m_sender = st.text_input("Поставщик (Кому):")
                m_payer = st.text_input("Плательщик:", value="Основной плательщик")
                m_amount = st.number_input("Сумма (€):", min_value=0.01, step=0.01, format="%.2f")
                m_due_date = st.date_input("Срок оплаты:", value=date.today() + timedelta(days=7))
                m_iban = st.text_input("IBAN получателя (необязательно):", placeholder="EE...")
                m_ref = st.text_input("Viitenumber (необязательно):")
                m_file = st.file_uploader("Файл (необязательно):", type=["pdf", "png", "jpg", "jpeg"])
                
                if st.form_submit_button("Сохранить в реестр", width='stretch', type="primary"):
                    if m_sender.strip():
                        s_path = ""
                        if m_file:
                            s_path = save_file_to_storage(m_file.getvalue(), m_file.name, m_sender)
                        cur = conn.cursor()
                        cur.execute("""
                            INSERT INTO invoices (payer, sender, amount, due_date, status, created_by, file_path, iban, ref_number)
                            VALUES (?, ?, ?, ?, 'Ожидает оплаты', ?, ?, ?, ?)
                        """, (m_payer.strip(), m_sender.strip(), float(m_amount), m_due_date.strftime("%Y-%m-%d"), current_user["email"], s_path, m_iban.strip(), m_ref.strip()))
                        conn.commit()
                        st.success("Счет сохранен!")
                        st.rerun()
                    else:
                        st.error("Укажите поставщика.")

        else:
            cur = conn.cursor()
            cur.execute("SELECT imap_server, imap_port, imap_user, imap_password, imap_folder FROM users WHERE id = ?", (current_user["id"],))
            user_mail = cur.fetchone()
            
            srv, prt, usr, pwd, fld = user_mail if user_mail else (None, None, None, None, None)
            is_configured = bool(srv and usr and pwd)

            with st.expander("📖 Памятка: Как подключить почту и стягивать счета", expanded=not is_configured):
                st.markdown("""
                ### 🚀 3 шага для автозабора счетов:
                1. В меню слева откройте **«⚙️ Моя почта (IMAP)»** и введите сервер (`imap.mail.ee`, `imap.gmail.com`), логин и пароль приложения.
                2. Оставьте входящее письмо от поставщика **непрочитанным** (`UNSEEN`) с прикрепленным файлом **PDF / JPG**.
                3. Нажмите кнопку **«📥 Проверить почту и загрузить новые счета»** ниже.
                """)

            if not is_configured:
                st.warning("⚠️ Почта еще не настроена в боковом меню слева.")
            else:
                st.success(f"Подключен ящик: **{usr}** | Папка: **{fld or 'INBOX'}**")
                if st.button("📥 Проверить почту и загрузить новые счета", width='stretch', type="primary"):
                    with st.spinner("Считывание непрочитанных вложений из ящика..."):
                        count_added, err_list = fetch_invoices_via_imap(
                            srv, prt or 993, usr, pwd, fld or "INBOX", current_user["email"]
                        )
                        if count_added > 0:
                            st.success(f"🎉 Успешно добавлено счетов: **{count_added}**!")
                            st.rerun()
                        elif not err_list:
                            st.info("ℹ️ Непрочитанных писем со счетами не найдено.")
                        if err_list:
                            for err_msg in err_list:
                                st.error(err_msg)

    with col_table:
        st.markdown("<h4 style='margin-bottom: 10px;'>📋 Текущие счета к оплате</h4>", unsafe_allow_html=True)
        
        cur = conn.cursor()
        query_cols = "id, sender, amount, due_date, status, payer, created_by, file_path, iban, ref_number"
        
        where_parts = ["status != 'В архиве'"]
        sql_params = []
        if not view_all_users:
            where_parts.append("created_by = ?")
            sql_params.append(current_user["email"])
            
        where_sql = "WHERE " + " AND ".join(where_parts)
        cur.execute(f"SELECT {query_cols} FROM invoices {where_sql} ORDER BY id DESC", tuple(sql_params))
        rows = cur.fetchall()

        if rows:
            for r in rows:
                inv_id, sender, amount, due_d, status, payer, author, f_path, iban, ref_no = r
                
                b_cls = "badge-paid" if status == "Оплачен" else "badge-pending"
                author_badge = f" • Автор: <b style='color:#e2e8f0;'>{author}</b>" if view_all_users else ""
                
                # Карточка счета
                st.markdown(f'<div class="invoice-card"><div class="invoice-header"><div class="invoice-sender">#{inv_id} {sender}</div><div class="invoice-amount">{amount:,.2f} €</div></div><div class="invoice-meta"><span class="invoice-badge {b_cls}">{status}</span><span>📅 Срок: <b style="color: #f1f5f9;">{due_d or "Без срока"}</b></span><span>👤 Плательщик: <b style="color: #f1f5f9;">{payer}</b></span>{author_badge}</div></div>', unsafe_allow_html=True)

                c_details, c_action = st.columns([2.3, 1.7])

                with c_details:
                    # ПЛАШКИ IBAN И VIITENUMBER: ПОДПИСЬ СВЕРХУ, ЦИФРЫ СНИЗУ, ВЫДЕЛЕНИЕ МЫШКОЙ
                    if iban or ref_no:
                        parts = ['<div class="req-container">']
                        if iban:
                            parts.append(f'<div class="req-pill"><div class="req-tag">IBAN</div><div class="req-val">{iban}</div></div>')
                        if iban and ref_no:
                            parts.append('<div class="req-sep"></div>')
                        if ref_no:
                            parts.append(f'<div class="req-pill"><div class="req-tag">VIITENUMBER</div><div class="req-val">{ref_no}</div></div>')
                        parts.append('</div>')
                        st.markdown("".join(parts), unsafe_allow_html=True)

                        if status == "Ожидает оплаты":
                            st.markdown(
                                '<div style="display: flex; gap: 6px; align-items: center; margin-top: 2px; margin-bottom: 6px; flex-wrap: wrap;">'
                                '<span style="font-size: 11.5px; color: #94a3b8; font-weight: 600;">Банк:</span>'
                                '<a class="bank-chip bank-lhv" href="https://www.lhv.ee/ru" target="_blank">LHV</a>'
                                '<a class="bank-chip bank-swed" href="https://www.swedbank.ee" target="_blank">Swed</a>'
                                '<a class="bank-chip bank-seb" href="https://www.seb.ee" target="_blank">SEB</a>'
                                '<a class="bank-chip bank-coop" href="https://www.cooppank.ee" target="_blank">Coop</a>'
                                '<a class="bank-chip bank-luminor" href="https://www.luminor.ee" target="_blank">Luminor</a>'
                                '</div>',
                                unsafe_allow_html=True
                            )

                    if f_path and os.path.exists(f_path):
                        fname = os.path.basename(f_path)
                        mime_t = "application/pdf" if fname.lower().endswith(".pdf") else "image/jpeg"
                        with open(f_path, "rb") as f_obj:
                            st.download_button(
                                label=f"📄 Файл ({fname})",
                                data=f_obj.read(),
                                file_name=fname,
                                mime=mime_t,
                                key=f"dl_file_{inv_id}",
                                width='stretch'
                            )

                with c_action:
                    row1_c1, row1_c2 = st.columns(2)
                    if status == "Ожидает оплаты":
                        if row1_c1.button("💳 Оплачен", key=f"pay_{inv_id}", width='stretch'):
                            cur.execute("UPDATE invoices SET status = 'Оплачен', paid_date = ? WHERE id = ?", (date.today().strftime("%Y-%m-%d"), inv_id))
                            conn.commit()
                            st.rerun()
                    
                    if row1_c2.button("📦 В архив", key=f"arch_{inv_id}", width='stretch'):
                        cur.execute("UPDATE invoices SET status = 'В архиве' WHERE id = ?", (inv_id,))
                        conn.commit()
                        st.rerun()

                    row2_c1, row2_c2 = st.columns(2)
                    with row2_c1:
                        with st.popover("⏰ Срок"):
                            st.markdown(f"**#{inv_id} {sender}**")
                            new_rem_date = st.date_input("Новая дата:", value=date.today() + timedelta(days=3), key=f"rem_date_{inv_id}")
                            if st.button("Сохранить", key=f"save_rem_{inv_id}", width='stretch'):
                                cur.execute("UPDATE invoices SET due_date = ? WHERE id = ?", (new_rem_date.strftime("%Y-%m-%d"), inv_id))
                                conn.commit()
                                st.rerun()
                    with row2_c2:
                        if current_user["role"] == "superadmin" or current_user["email"] == author:
                            with st.popover("🗑️ Удалить"):
                                st.write("Удалить счет?")
                                if st.button("Да", key=f"del_{inv_id}", type="primary", width='stretch'):
                                    cur.execute("DELETE FROM invoices WHERE id = ?", (inv_id,))
                                    conn.commit()
                                    st.rerun()

                st.markdown("<hr style='border-color: rgba(255,255,255,0.06); margin: 8px 0 12px 0;'>", unsafe_allow_html=True)
        else:
            st.info("Активных счетов нет.")

# -------------------- ВКЛАДКА 2: АРХИВ СЧЕТОВ --------------------
with tab_archive:
    st.markdown("<h4 style='margin-bottom: 12px;'>📦 Архив счетов</h4>", unsafe_allow_html=True)
    
    cur = conn.cursor()
    arch_query_cols = "id, sender, amount, due_date, status, payer, created_by, file_path, iban, ref_number, paid_date"
    
    arch_where = ["status = 'В архиве'"]
    arch_params = []
    if not view_all_users:
        arch_where.append("created_by = ?")
        arch_params.append(current_user["email"])
        
    arch_sql = "WHERE " + " AND ".join(arch_where)
    cur.execute(f"SELECT {arch_query_cols} FROM invoices {arch_sql} ORDER BY id DESC", tuple(arch_params))
    arch_rows = cur.fetchall()

    if arch_rows:
        total_arch_amt = sum(x[2] for x in arch_rows)
        st.caption(f"Всего счетов в архиве: **{len(arch_rows)}** | Общая сумма: **{total_arch_amt:,.2f} €**".replace(",", " "))
        
        for r in arch_rows:
            inv_id, sender, amount, due_d, status, payer, author, f_path, iban, ref_no, paid_d = r
            author_badge = f" • Автор: <b style='color:#e2e8f0;'>{author}</b>" if view_all_users else ""
            paid_info = f" • Оплачен: {paid_d}" if paid_d else ""
            
            st.markdown(f'<div class="invoice-card" style="opacity: 0.88; border-color: rgba(148, 163, 184, 0.2);"><div class="invoice-header"><div class="invoice-sender">#{inv_id} {sender}</div><div class="invoice-amount" style="color: #94a3b8;">{amount:,.2f} €</div></div><div class="invoice-meta"><span class="invoice-badge badge-archived">В АРХИВЕ</span><span>📅 Дедлайн: {due_d or "Без срока"}{paid_info}</span><span>👤 Плательщик: {payer}</span>{author_badge}</div></div>', unsafe_allow_html=True)

            c_arch_det, c_arch_act = st.columns([2.5, 1.5])
            with c_arch_det:
                if iban or ref_no:
                    parts = ['<div class="req-container" style="border-color: rgba(148,163,184,0.25);">']
                    if iban:
                        parts.append(f'<div class="req-pill"><div class="req-tag" style="color: #94a3b8;">IBAN</div><div class="req-val">{iban}</div></div>')
                    if iban and ref_no:
                        parts.append('<div class="req-sep"></div>')
                    if ref_no:
                        parts.append(f'<div class="req-pill"><div class="req-tag" style="color: #94a3b8;">VIITENUMBER</div><div class="req-val">{ref_no}</div></div>')
                    parts.append('</div>')
                    st.markdown("".join(parts), unsafe_allow_html=True)

                if f_path and os.path.exists(f_path):
                    fname = os.path.basename(f_path)
                    mime_t = "application/pdf" if fname.lower().endswith(".pdf") else "image/jpeg"
                    with open(f_path, "rb") as f_obj:
                        st.download_button(
                            label=f"📄 Оригинал ({fname})",
                            data=f_obj.read(),
                            file_name=fname,
                            mime=mime_t,
                            key=f"dl_arch_{inv_id}",
                            width='stretch'
                        )

            with c_arch_act:
                c_ret, c_del = st.columns(2)
                if c_ret.button("↩️ Вернуть", key=f"rest_{inv_id}", width='stretch'):
                    cur.execute("UPDATE invoices SET status = 'Ожидает оплаты' WHERE id = ?", (inv_id,))
                    conn.commit()
                    st.success("Счет возвращен в работу!")
                    st.rerun()

                if current_user["role"] == "superadmin" or current_user["email"] == author:
                    with c_del.popover("🗑️ Удалить"):
                        st.write("Удалить навсегда?")
                        if st.button("Да", key=f"del_arch_{inv_id}", type="primary", width='stretch'):
                            cur.execute("DELETE FROM invoices WHERE id = ?", (inv_id,))
                            conn.commit()
                            st.rerun()

            st.markdown("<hr style='border-color: rgba(255,255,255,0.05); margin: 8px 0 12px 0;'>", unsafe_allow_html=True)
    else:
        st.info("Архив пуст. Чтобы отправить счет сюда, нажмите «📦 В архив» в основном списке счетов.")

# -------------------- ВКЛАДКА 3: ПОСТАВЩИКИ --------------------
with tab_senders:
    st.markdown("<h4 style='margin-bottom: 12px;'>🏢 Аналитика по поставщикам</h4>", unsafe_allow_html=True)
    if view_all_users:
        df = pd.read_sql_query("SELECT * FROM invoices WHERE status != 'В архиве'", conn)
    else:
        df = pd.read_sql_query("SELECT * FROM invoices WHERE status != 'В архиве' AND created_by = ?", conn, params=(current_user["email"],))
    
    if not df.empty and "sender" in df.columns:
        senders_list = sorted([s for s in df["sender"].dropna().unique() if str(s).strip()])
        if senders_list:
            selected_sender = st.selectbox("Выберите поставщика:", senders_list)
            s_df = df[df["sender"] == selected_sender]
            
            total_s = s_df["amount"].sum()
            paid_s = s_df[s_df["status"] == "Оплачен"]["amount"].sum()
            pending_s = s_df[s_df["status"] != "Оплачен"]["amount"].sum()

            m1, m2, m3 = st.columns(3)
            m1.metric(f"Всего ({selected_sender})", f"{total_s:,.2f} €".replace(",", " "))
            m2.metric("Выплачено", f"{paid_s:,.2f} €".replace(",", " "))
            m3.metric("Остаток к оплате", f"{pending_s:,.2f} €".replace(",", " "))

            cols_show = ["id", "due_date", "payer", "amount", "iban", "ref_number", "status"]
            cols_exist = [c for c in cols_show if c in s_df.columns]
            table_display = s_df[cols_exist].rename(
                columns={"id": "№", "due_date": "Срок оплаты", "payer": "Плательщик", "amount": "Сумма (€)", "iban": "IBAN", "ref_number": "Viitenumber", "status": "Статус"}
            )
            st.dataframe(table_display, width='stretch', hide_index=True)
        else:
            st.info("Нет данных о поставщиках.")
    else:
        st.info("Реестр пуст.")

# -------------------- ВКЛАДКА 4: ПЛАТЕЛЬЩИКИ --------------------
with tab_payers:
    st.markdown("<h4 style='margin-bottom: 12px;'>👤 Аналитика по плательщикам и проектам</h4>", unsafe_allow_html=True)
    if view_all_users:
        df = pd.read_sql_query("SELECT * FROM invoices WHERE status != 'В архиве'", conn)
    else:
        df = pd.read_sql_query("SELECT * FROM invoices WHERE status != 'В архиве' AND created_by = ?", conn, params=(current_user["email"],))
    
    if not df.empty and "payer" in df.columns:
        payers_list = sorted([p for p in df["payer"].dropna().unique() if str(p).strip()])
        if payers_list:
            selected_payer = st.selectbox("Выберите плательщика:", payers_list)
            p_df = df[df["payer"] == selected_payer]
            
            total_p = p_df["amount"].sum()
            paid_p = p_df[p_df["status"] == "Оплачен"]["amount"].sum()
            pending_p = p_df[p_df["status"] != "Оплачен"]["amount"].sum()

            p1, p2, p3 = st.columns(3)
            p1.metric(f"Всего ({selected_payer})", f"{total_p:,.2f} €".replace(",", " "))
            p2.metric("Оплачено", f"{paid_p:,.2f} €".replace(",", " "))
            p3.metric("Ожидает оплаты", f"{pending_p:,.2f} €".replace(",", " "))

            cols_p_show = ["id", "due_date", "sender", "amount", "iban", "ref_number", "status"]
            cols_p_exist = [c for c in cols_p_show if c in p_df.columns]
            table_payer = p_df[cols_p_exist].rename(
                columns={"id": "№", "due_date": "Срок оплаты", "sender": "Поставщик", "amount": "Сумма (€)", "iban": "IBAN", "ref_number": "Viitenumber", "status": "Статус"}
            )
            st.dataframe(table_payer, width='stretch', hide_index=True)

            csv_data = p_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label=f"📥 Скачать выписку по {selected_payer} (CSV)",
                data=csv_data,
                file_name=f"report_{selected_payer}_{date.today().strftime('%Y-%m-%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("Нет данных о плательщиках.")
    else:
        st.info("Реестр пуст.")
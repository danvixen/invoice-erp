import os
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date, timedelta
import keyring

SMTP_SERVER = "mail.ee"
SMTP_PORT = 465
SMTP_USER = "aleksei.gusev@mail.ee"
ADMIN_EMAIL = "aleksei.gusev@mail.ee"
DB_PATH = "C:\\invoice_assistant\\invoices_local.db"

# Пароль безопасно достается из сейфа Windows
SMTP_PASSWORD = keyring.get_password("invoice_erp", SMTP_USER)

def send_email(to_email: str, subject: str, html_body: str):
    if not SMTP_PASSWORD:
        print("[ERROR] Пароль не найден в Credential Manager Windows.")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"Invoice ERP <{SMTP_USER}>"
    msg["To"] = to_email
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=15) as server:
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, to_email, msg.as_string())
        print(f"[OK] Письмо успешно отправлено на {to_email}")
        return True
    except Exception as e:
        print(f"[ERROR] Ошибка отправки на {to_email}: {e}")
        return False

def check_and_notify():
    tomorrow_str = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    if not os.path.exists(DB_PATH):
        print(f"База данных не найдена: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Счета к оплате на завтра
    cur.execute("""
        SELECT id, sender, amount, payer, created_by 
        FROM invoices 
        WHERE due_date = ? AND status != 'Оплачен'
    """, (tomorrow_str,))
    
    invoices = cur.fetchall()
    conn.close()

    if not invoices:
        print(f"На завтра ({tomorrow_str}) счетов к оплате нет.")
        return

    # Отправка администратору сводки
    all_rows = "".join([
        f"<tr><td style='padding:6px;border:1px solid #ccc;'>#{it[0]}</td>"
        f"<td style='padding:6px;border:1px solid #ccc;'><b>{it[1]}</b></td>"
        f"<td style='padding:6px;border:1px solid #ccc;color:#c0392b;'><b>{it[2]:.2f} €</b></td>"
        f"<td style='padding:6px;border:1px solid #ccc;'>{it[3]}</td>"
        f"<td style='padding:6px;border:1px solid #ccc;'>{it[4]}</td></tr>"
        for it in invoices
    ])

    html = f"""
    <div style="font-family: Arial, sans-serif;">
        <h2 style="color: #e67e22;">⏰ Дедлайн завтра ({tomorrow_str})</h2>
        <table style="width: 100%; border-collapse: collapse;">
            <tr style="background: #f2f2f2;">
                <th style="padding:6px;border:1px solid #ccc;">№</th>
                <th style="padding:6px;border:1px solid #ccc;">Поставщик</th>
                <th style="padding:6px;border:1px solid #ccc;">Сумма</th>
                <th style="padding:6px;border:1px solid #ccc;">Плательщик</th>
                <th style="padding:6px;border:1px solid #ccc;">Загрузил</th>
            </tr>
            {all_rows}
        </table>
    </div>
    """
    send_email(ADMIN_EMAIL, f"[Invoice ERP] Счета к оплате на {tomorrow_str}", html)

if __name__ == "__main__":
    check_and_notify()
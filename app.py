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

# ==================== СЛОВАРЬ ПЕРЕВОДОВ ====================
TRANSLATIONS = {
    "en": {
        "lang_en": "🇬🇧 EN", "lang_et": "🇪🇪 ET", "lang_ru": "🇷🇺 RU",
        "auth_title": "💳 Invoice ERP",
        "auth_subtitle": "Smart Accounts Payable & Invoicing Hub",
        "login_tab": "🔑 Sign In",
        "signup_tab": "📝 Register",
        "email_label": "Work Email:",
        "email_placeholder": "name@firma.ee",
        "password_label": "Password:",
        "login_btn": "Sign In",
        "pending_approval": "⏳ Your application is awaiting administrator approval.",
        "invalid_credentials": "Invalid email or password.",
        "forgot_pwd": "Forgot password?",
        "tab_req_code": "Request Code",
        "tab_new_pwd": "Set Password",
        "send_code_btn": "Send Code",
        "code_sent": "Code sent to {email}!",
        "user_not_found": "User not found or inactive.",
        "code_label": "Code:",
        "new_pass_label": "New password:",
        "save_pass_btn": "Save Password",
        "pass_updated": "Password updated! Please sign in.",
        "invalid_code": "Invalid verification code.",
        "signup_caption": "Register new employee:",
        "name_label": "Full Name:",
        "create_pass_label": "Create Password:",
        "signup_btn": "Submit Application",
        "fill_all_fields": "Please fill in all fields.",
        "role_admin": "Superadmin",
        "role_user": "Employee",
        "manager_mode": "👁️ Manager Mode (all invoices)",
        "caption_all": "Viewing all employees' invoices",
        "caption_my": "Viewing only your personal invoices",
        "logout_btn": "🚪 Sign Out",
        "imap_expander": "⚙️ My Email (IMAP for invoices)",
        "imap_caption": "Mailbox settings for auto-fetching invoices:",
        "imap_server": "IMAP Server:",
        "imap_port": "Port (SSL):",
        "imap_login": "Login / Email:",
        "imap_pass": "App Password:",
        "imap_folder": "Folder to check:",
        "imap_save_btn": "Save Settings",
        "imap_saved": "Settings saved!",
        "access_requests": "🔔 Access Requests",
        "btn_approve": "✅ Approve",
        "btn_reject": "❌ Reject",
        "user_activated": "{name} activated!",
        "user_rejected": "Request rejected.",
        "no_requests": "No pending requests.",
        "due_tomorrow_alert": "⏰ **Payment due tomorrow ({date}):** Invoice #{id} from **{sender}** for **{amount} €** (Payer: {payer})",
        "overdue_alert": "🚨 **Overdue payment!** Due was {date}. Invoice #{id} from **{sender}** for **{amount} €**",
        "kpi_total": "TOTAL INVOICES",
        "kpi_paid": "PAID",
        "kpi_pending": "TO PAY",
        "kpi_overdue": "OVERDUE",
        "tab_registry": "🧾 Registry & Processing",
        "tab_archive": "📦 Invoice Archive",
        "tab_senders": "🏢 Vendors",
        "tab_payers": "👤 Payers & Projects",
        "add_hdr": "📥 Add Invoice",
        "mode_label": "Method:",
        "mode_ai": "⚡ AI File Parsing",
        "mode_manual": "✍️ Manual",
        "mode_mail": "📧 Fetch from Email",
        "attach_label": "Upload invoice (PDF, PNG, JPG)",
        "btn_save_invoice": "Save invoice",
        "ai_processing": "AI is analyzing document and extracting details...",
        "ai_added": "Added: {sender} | {amount} €",
        "ai_error": "Recognition error: {err}",
        "field_vendor": "Vendor (Pay to):",
        "field_payer": "Payer:",
        "default_payer": "Main Payer",
        "field_amount": "Amount (€):",
        "field_due_date": "Due date:",
        "field_iban": "Beneficiary IBAN (optional):",
        "field_ref": "Reference number (optional):",
        "err_specify_vendor": "Please specify vendor.",
        "invoice_saved": "Invoice saved!",
        "mail_guide_title": "📖 Guide: Auto-fetching invoices via Email",
        "mail_guide_body": "### 🚀 3 steps for email auto-fetch:\n1. Open **«⚙️ My Email (IMAP)»** in the left sidebar.\n2. Keep vendor incoming email **unread** (`UNSEEN`) with attached **PDF/JPG**.\n3. Click button below.",
        "mail_not_configured": "⚠️ Email is not configured yet in the left sidebar.",
        "mail_connected": "Connected mailbox: **{user}** | Folder: **{folder}**",
        "btn_check_mail": "📥 Check email and fetch new invoices",
        "mail_scanning": "Scanning unread invoice attachments...",
        "mail_success": "🎉 Successfully added invoices: **{count}**!",
        "mail_empty": "ℹ️ No unread emails with invoices found.",
        "pending_hdr": "📋 Pending Invoices",
        "status_pending": "PENDING",
        "status_paid": "PAID",
        "status_archived": "ARCHIVED",
        "meta_due": "📅 Due:",
        "meta_no_due": "No due date",
        "meta_payer": "👤 Payer:",
        "meta_author": "• Author:",
        "bank_label": "Bank:",
        "btn_view_file": "📄 File ({name})",
        "btn_paid": "💳 Paid",
        "btn_archive": "📦 To Archive",
        "pop_due_btn": "⏰ Due",
        "pop_new_date": "New date:",
        "pop_save_btn": "Save",
        "pop_del_btn": "🗑️ Delete",
        "pop_del_confirm": "Delete invoice?",
        "btn_yes": "Yes",
        "no_pending_invoices": "No pending invoices.",
        "arch_hdr": "📦 Invoice Archive",
        "arch_summary": "Total archived invoices: **{count}** | Total sum: **{total} €**",
        "arch_badge": "ARCHIVED",
        "arch_paid_on": "• Paid on: {date}",
        "btn_restore": "↩️ Restore",
        "pop_del_perm": "Delete permanently?",
        "arch_restored": "Invoice restored to pending!",
        "arch_empty": "Archive is empty.",
        "senders_hdr": "🏢 Vendor Analytics",
        "select_vendor": "Select vendor:",
        "kpi_vendor_total": "Total ({name})",
        "kpi_vendor_paid": "Paid",
        "kpi_vendor_pending": "Balance to pay",
        "th_num": "№", "th_due": "Due date", "th_payer": "Payer", "th_amount": "Amount (€)", "th_iban": "IBAN", "th_ref": "Reference no", "th_status": "Status", "th_vendor": "Vendor",
        "no_vendor_data": "No vendor data.",
        "registry_empty": "Registry is empty.",
        "payers_hdr": "👤 Analytics by Payers & Projects",
        "select_payer": "Select payer:",
        "kpi_payer_total": "Total ({name})",
        "kpi_payer_paid": "Paid",
        "kpi_payer_pending": "Pending payment",
        "btn_csv_export": "📥 Download statement for {name} (CSV)",
        "no_payer_data": "No payer data."
    },
    "et": {
        "lang_en": "🇬🇧 EN", "lang_et": "🇪🇪 ET", "lang_ru": "🇷🇺 RU",
        "auth_title": "💳 Invoice ERP",
        "auth_subtitle": "Nutikas ostuarvete ja finantshalduskeskus",
        "login_tab": "🔑 Logi sisse",
        "signup_tab": "📝 Registreeru",
        "email_label": "Töö e-post:",
        "email_placeholder": "nimi@firma.ee",
        "password_label": "Parool:",
        "login_btn": "Sisene süsteemi",
        "pending_approval": "⏳ Teie registreerimistaotlus ootab administraatori kinnitust.",
        "invalid_credentials": "Vale e-posti aadress või parool.",
        "forgot_pwd": "Unustasid parooli?",
        "tab_req_code": "Koodi taotlemine",
        "tab_new_pwd": "Uus parool",
        "send_code_btn": "Saada kood",
        "code_sent": "Kinnituskood saadeti aadressile {email}!",
        "user_not_found": "Kasutajat ei leitud või konto pole aktiivne.",
        "code_label": "Kood:",
        "new_pass_label": "Uus parool:",
        "save_pass_btn": "Salvesta parool",
        "pass_updated": "Parool uuendatud! Logige sisse.",
        "invalid_code": "Vale kinnituskood.",
        "signup_caption": "Uue töötaja registreerimine:",
        "name_label": "Ees- ja perekonnanimi:",
        "create_pass_label": "Mõtle välja parool:",
        "signup_btn": "Saada taotlus",
        "fill_all_fields": "Palun täitke kõik väljad.",
        "role_admin": "Peaadministraator",
        "role_user": "Töötaja",
        "manager_mode": "👁️ Juhi režiim (kõik arved)",
        "caption_all": "Kõigi töötajate arvete koondvaade",
        "caption_my": "Kuvatakse ainult teie isiklikke arveid",
        "logout_btn": "🚪 Logi välja",
        "imap_expander": "⚙️ Minu e-post (IMAP arvete jaoks)",
        "imap_caption": "Postkasti seaded arvete automaatseks allalaadimiseks:",
        "imap_server": "IMAP Server:",
        "imap_port": "Port (SSL):",
        "imap_login": "Kasutaja / E-post:",
        "imap_pass": "Rakenduse parool:",
        "imap_folder": "Kaust kontrollimiseks:",
        "imap_save_btn": "Salvesta seaded",
        "imap_saved": "Seaded on salvestatud!",
        "access_requests": "🔔 Juurdepääsutaotlused",
        "btn_approve": "✅ Kinnita",
        "btn_reject": "❌ Lükka tagasi",
        "user_activated": "{name} on aktiveeritud!",
        "user_rejected": "Taotlus tagasi lükatud.",
        "no_requests": "Uusi taotlusi ei ole.",
        "due_tomorrow_alert": "⏰ **Maksetähtaeg homme ({date}):** Arve #{id} tarnijalt **{sender}** summale **{amount} €** (Maksja: {payer})",
        "overdue_alert": "🚨 **Tähtaja ületanud makse!** Tähtaeg oli {date}. Arve #{id} tarnijalt **{sender}** summale **{amount} €**",
        "kpi_total": "ARVEID KOKKU",
        "kpi_paid": "MAKSTUD",
        "kpi_pending": "MAKSTOPEAL",
        "kpi_overdue": "TÄHTAJA ÜLETANUD",
        "tab_registry": "🧾 Register ja töötlemine",
        "tab_archive": "📦 Arhiiv",
        "tab_senders": "🏢 Tarnijad",
        "tab_payers": "👤 Maksjad ja projektid",
        "add_hdr": "📥 Lisa arve",
        "mode_label": "Lisamise viis:",
        "mode_ai": "⚡ AI dokumendi tuvastus",
        "mode_manual": "✍️ Käsitsi",
        "mode_mail": "📧 Tõmba e-postist",
        "attach_label": "Laadi arve üles (PDF, PNG, JPG)",
        "btn_save_invoice": "Salvesta arve",
        "ai_processing": "AI analüüsib dokumenti ja loeb andmeid...",
        "ai_added": "Lisatud: {sender} | {amount} €",
        "ai_error": "Tuvastamise viga: {err}",
        "field_vendor": "Tarnija (Kellele):",
        "field_payer": "Maksja:",
        "default_payer": "Põhimaksja",
        "field_amount": "Summa (€):",
        "field_due_date": "Maksetähtaeg:",
        "field_iban": "Saaja IBAN (valikuline):",
        "field_ref": "Viitenumber (valikuline):",
        "err_specify_vendor": "Palun märkige tarnija.",
        "invoice_saved": "Arve salvestatud!",
        "mail_guide_title": "📖 Juhend: Arvete automaatne vastuvõtmine e-postist",
        "mail_guide_body": "### 🚀 3 sammu arvete automaatseks laadimiseks:\n1. Ava **«⚙️ Minu e-post (IMAP)»** vasakmenüüs.\n2. Jäta kiri **lugemata** (`UNSEEN`) koos **PDF/JPG**-ga.\n3. Klõpsa nuppu allpool.",
        "mail_not_configured": "⚠️ E-post pole veel vasakpoolses menüüs seadistatud.",
        "mail_connected": "Ühendatud postkast: **{user}** | Kaust: **{folder}**",
        "btn_check_mail": "📥 Kontrolli e-posti ja laadi uued arved",
        "mail_scanning": "Loetakse postkastist lugemata manuseid...",
        "mail_success": "🎉 Edukalt lisatud arveid: **{count}**!",
        "mail_empty": "ℹ️ Lugemata arvetega kirju ei leitud.",
        "pending_hdr": "📋 Tasumisele kuuluvad arved",
        "status_pending": "OOTAB TASUMIST",
        "status_paid": "MAKSTUD",
        "status_archived": "ARHIIVIS",
        "meta_due": "📅 Tähtaeg:",
        "meta_no_due": "Ilma tähtajata",
        "meta_payer": "👤 Maksja:",
        "meta_author": "• Autor:",
        "bank_label": "Pank:",
        "btn_view_file": "📄 Fail ({name})",
        "btn_paid": "💳 Makstud",
        "btn_archive": "📦 Arhiivi",
        "pop_due_btn": "⏰ Tähtaeg",
        "pop_new_date": "Uus kuupäev:",
        "pop_save_btn": "Salvesta",
        "pop_del_btn": "🗑️ Kustuta",
        "pop_del_confirm": "Kas kustutada arve?",
        "btn_yes": "Jah",
        "no_pending_invoices": "Tasumist ootavaid arveid ei ole.",
        "arch_hdr": "📦 Arhiiv",
        "arch_summary": "Arveid arhiivis kokku: **{count}** | Kogusumma: **{total} €**",
        "arch_badge": "ARHIIVIS",
        "arch_paid_on": "• Makstud: {date}",
        "btn_restore": "↩️ Taasta",
        "pop_del_perm": "Kustutada lõplikult?",
        "arch_restored": "Arve tagastatud töösse!",
        "arch_empty": "Arhiiv on tühi.",
        "senders_hdr": "🏢 Tarnijate analüütika",
        "select_vendor": "Vali tarnija:",
        "kpi_vendor_total": "Kokku ({name})",
        "kpi_vendor_paid": "Välja makstud",
        "kpi_vendor_pending": "Jääk maksmisele",
        "th_num": "№", "th_due": "Maksetähtaeg", "th_payer": "Maksja", "th_amount": "Summa (€)", "th_iban": "IBAN", "th_ref": "Viitenumber", "th_status": "Olek", "th_vendor": "Tarnija",
        "no_vendor_data": "Tarnija andmed puuduvad.",
        "registry_empty": "Register on tühi.",
        "payers_hdr": "👤 Maksjate ja projektide analüütika",
        "select_payer": "Vali maksja:",
        "kpi_payer_total": "Kokku ({name})",
        "kpi_payer_paid": "Makstud",
        "kpi_payer_pending": "Ootab maksmist",
        "btn_csv_export": "📥 Laadi alla väljavõte maksja {name} kohta (CSV)",
        "no_payer_data": "Maksjate andmed puuduvad."
    },
    "ru": {
        "lang_en": "🇬🇧 EN", "lang_et": "🇪🇪 ET", "lang_ru": "🇷🇺 RU",
        "auth_title": "💳 Invoice ERP",
        "auth_subtitle": "Smart Accounts Payable & Invoicing Hub",
        "login_tab": "🔑 Вход",
        "signup_tab": "📝 Регистрация",
        "email_label": "Рабочий Email:",
        "email_placeholder": "name@firma.ee",
        "password_label": "Пароль:",
        "login_btn": "Войти в кабинет",
        "pending_approval": "⏳ Ваша заявка ожидает подтверждения администратором.",
        "invalid_credentials": "Неверный email или пароль.",
        "forgot_pwd": "Забыли пароль?",
        "tab_req_code": "Запрос кода",
        "tab_new_pwd": "Смена пароля",
        "send_code_btn": "Выслать код",
        "code_sent": "Код отправлен на {email}!",
        "user_not_found": "Пользователь не найден или не активен.",
        "code_label": "Код:",
        "new_pass_label": "Новый пароль:",
        "save_pass_btn": "Сохранить пароль",
        "pass_updated": "Пароль обновлен! Войдите.",
        "invalid_code": "Неверный код.",
        "signup_caption": "Регистрация нового сотрудника в системе:",
        "name_label": "Имя и фамилия:",
        "create_pass_label": "Придумайте пароль:",
        "signup_btn": "Отправить заявку",
        "fill_all_fields": "Заполните все поля.",
        "role_admin": "Главный Администратор",
        "role_user": "Сотрудник",
        "manager_mode": "👁️ Режим руководителя (все счета)",
        "caption_all": "Сводный просмотр счетов всех сотрудников",
        "caption_my": "Отображаются только ваши личные счета",
        "logout_btn": "🚪 Выйти из системы",
        "imap_expander": "⚙️ Моя почта (IMAP для счетов)",
        "imap_caption": "Параметры ящика для автоматического скачивания счетов:",
        "imap_server": "IMAP Сервер:",
        "imap_port": "Порт (SSL):",
        "imap_login": "Логин / Email:",
        "imap_pass": "Пароль приложения:",
        "imap_folder": "Папка для проверки:",
        "imap_save_btn": "Сохранить параметры",
        "imap_saved": "Настройки сохранены!",
        "access_requests": "🔔 Заявки на доступ",
        "btn_approve": "✅ Одобрить",
        "btn_reject": "❌ Отклонить",
        "user_activated": "{name} активирован!",
        "user_rejected": "Отклонено.",
        "no_requests": "Новых заявок нет.",
        "due_tomorrow_alert": "⏰ **Срок оплаты завтра ({date}):** Счет #{id} от **{sender}** на сумму **{amount} €** (Плательщик: {payer})",
        "overdue_alert": "🚨 **Просрочен платеж!** Срок был {date}. Счет #{id} от **{sender}** на сумму **{amount} €**",
        "kpi_total": "ВСЕГО ПО СЧЕТАМ",
        "kpi_paid": "ОПЛАЧЕНО",
        "kpi_pending": "К ОПЛАТЕ",
        "kpi_overdue": "ПРОСРОЧЕНО",
        "tab_registry": "🧾 Реестр и обработка",
        "tab_archive": "📦 Архив счетов",
        "tab_senders": "🏢 Поставщики (Кому)",
        "tab_payers": "👤 Плательщики (Кто)",
        "add_hdr": "📥 Внести счет",
        "mode_label": "Способ добавления:",
        "mode_ai": "⚡ AI-распознавание файла",
        "mode_manual": "✍️ Вручную",
        "mode_mail": "📧 Стянуть из личной почты",
        "attach_label": "Загрузить счет (PDF, PNG, JPG)",
        "btn_save_invoice": "Сохранить счет",
        "ai_processing": "AI анализирует документ и извлекает реквизиты...",
        "ai_added": "Добавлено: {sender} | {amount} €",
        "ai_error": "Ошибка распознавания: {err}",
        "field_vendor": "Поставщик (Кому):",
        "field_payer": "Плательщик:",
        "default_payer": "Основной плательщик",
        "field_amount": "Сумма (€):",
        "field_due_date": "Срок оплаты:",
        "field_iban": "IBAN получателя (необязательно):",
        "field_ref": "Viitenumber (необязательно):",
        "err_specify_vendor": "Укажите поставщика.",
        "invoice_saved": "Счет сохранен!",
        "mail_guide_title": "📖 Памятка: Как подключить почту и стягивать счета",
        "mail_guide_body": "### 🚀 3 шага для автозабора счетов:\n1. В меню слева откройте **«⚙️ Моя почта (IMAP)»**.\n2. Оставьте письмо **непрочитанным** (`UNSEEN`) с вложением **PDF/JPG**.\n3. Нажмите кнопку ниже.",
        "mail_not_configured": "⚠️ Почта еще не настроена в боковом меню слева.",
        "mail_connected": "Подключен ящик: **{user}** | Папка: **{folder}**",
        "btn_check_mail": "📥 Проверить почту и загрузить новые счета",
        "mail_scanning": "Считывание непрочитанных вложений из ящика...",
        "mail_success": "🎉 Успешно добавлено счетов: **{count}**!",
        "mail_empty": "ℹ️ Непрочитанных писем со счетами не найдено.",
        "pending_hdr": "📋 Текущие счета к оплате",
        "status_pending": "ОЖИДАЕТ ОПЛАТЫ",
        "status_paid": "ОПЛАЧЕН",
        "status_archived": "В АРХИВЕ",
        "meta_due": "📅 Срок:",
        "meta_no_due": "Без срока",
        "meta_payer": "👤 Плательщик:",
        "meta_author": "• Автор:",
        "bank_label": "Банк:",
        "btn_view_file": "📄 Файл ({name})",
        "btn_paid": "💳 Оплачен",
        "btn_archive": "📦 В архив",
        "pop_due_btn": "⏰ Срок",
        "pop_new_date": "Новая дата:",
        "pop_save_btn": "Сохранить",
        "pop_del_btn": "🗑️ Удалить",
        "pop_del_confirm": "Удалить счет?",
        "btn_yes": "Да",
        "no_pending_invoices": "Активных счетов нет.",
        "arch_hdr": "📦 Архив счетов",
        "arch_summary": "Всего счетов в архиве: **{count}** | Общая сумма: **{total} €**",
        "arch_badge": "В АРХИВЕ",
        "arch_paid_on": "• Оплачен: {date}",
        "btn_restore": "↩️ Вернуть",
        "pop_del_perm": "Удалить навсегда?",
        "arch_restored": "Счет возвращен в работу!",
        "arch_empty": "Архив пуст.",
        "senders_hdr": "🏢 Аналитика по поставщикам",
        "select_vendor": "Выберите поставщика:",
        "kpi_vendor_total": "Всего ({name})",
        "kpi_vendor_paid": "Выплачено",
        "kpi_vendor_pending": "Остаток к оплате",
        "th_num": "№", "th_due": "Срок оплаты", "th_payer": "Плательщик", "th_amount": "Сумма (€)", "th_iban": "IBAN", "th_ref": "Viitenumber", "th_status": "Статус", "th_vendor": "Поставщик",
        "no_vendor_data": "Нет данных о поставщиках.",
        "registry_empty": "Реестр пуст.",
        "payers_hdr": "👤 Аналитика по плательщикам и проектам",
        "select_payer": "Выберите плательщика:",
        "kpi_payer_total": "Всего ({name})",
        "kpi_payer_paid": "Оплачено",
        "kpi_payer_pending": "Ожидает оплаты",
        "btn_csv_export": "📥 Скачать выписку по {name} (CSV)",
        "no_payer_data": "Нет данных о плательщиках."
    }
}

def get_lang():
    if "lang" not in st.session_state:
        st.session_state["lang"] = "en"
    return st.session_state["lang"]

def t(key: str, **kwargs) -> str:
    lang = get_lang()
    text = TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)
    if kwargs and isinstance(text, str):
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text

def render_top_language_bar():
    c_empty, c_lang = st.columns([3.8, 1.2])
    with c_lang:
        current = get_lang()
        options = ["en", "et", "ru"]
        labels = {
            "en": TRANSLATIONS["en"]["lang_en"],
            "et": TRANSLATIONS["et"]["lang_et"],
            "ru": TRANSLATIONS["ru"]["lang_ru"]
        }
        selected = st.radio(
            "Lang",
            options=options,
            index=options.index(current),
            format_func=lambda x: labels[x],
            horizontal=True,
            label_visibility="collapsed"
        )
        if selected != current:
            st.session_state["lang"] = selected
            st.rerun()

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
render_top_language_bar()

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
        st.success(f"🎉 {u_name} ({u_email}) activated!")
        notify_body = f"<p>Hello, {u_name}!</p><p>Your account in <b>Invoice ERP</b> has been activated.</p>"
        notifier.send_email(u_email, "Invoice ERP access approved", notify_body)
    else:
        st.info("ℹ️ Already activated.")
    try:
        del st.query_params["approve"]
    except Exception:
        pass

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
    model = genai.GenerativeModel("gemini-2.5-flash")
    inline_doc = {"mime_type": mime_type, "data": file_bytes}
    prompt = """
    Extract invoice fields. Return STRICT JSON without markdown:
    {
      "payer": "Payer name",
      "sender": "Vendor / Sender",
      "amount": 0.00,
      "due_date": "YYYY-MM-DD",
      "iban": "IBAN without spaces",
      "reference_number": "Reference number without word Viitenumber"
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
            return 0, [f"Folder '{folder}' not found."]
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
                        s_name = data.get("sender") or "Vendor"
                        amt = float(data.get("amount") or 0.0)
                        d_date = data.get("due_date") or (date.today() + timedelta(days=7)).strftime("%Y-%m-%d")
                        p_name = data.get("payer") or t("default_payer")
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
        return 0, [f"IMAP Error: {e}"]

def notify_admin_new_user(name: str, email: str, token: str):
    global_link = f"{PUBLIC_URL}/?approve={token}" if PUBLIC_URL else f"http://{get_lan_ip()}:8501/?approve={token}"
    subject = f"🔔 New registration: {name}"
    html_body = f"""
    <div style="font-family: Arial, sans-serif; padding: 20px;">
        <h3>New access request in Invoice ERP</h3>
        <p><b>Name:</b> {name}<br><b>Email:</b> {email}</p>
        <p><a href="{global_link}" style="background: #10b981; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Approve 1-Click</a></p>
    </div>
    """
    notifier.send_email(ADMIN_EMAIL, subject, html_body)

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
        return True, t("signup_caption")
    except sqlite3.IntegrityError:
        return False, "User exists"

if not st.session_state.user:
    st.markdown(f"<div style='text-align: center; margin-top: 50px; margin-bottom: 25px;'><h1 style='font-size: 36px; margin-bottom: 4px;'>{t('auth_title')}</h1><p style='color: #94a3b8; font-size: 15px;'>{t('auth_subtitle')}</p></div>", unsafe_allow_html=True)
    _, col_auth, _ = st.columns([1.5, 1.4, 1.5])
    
    with col_auth:
        tab_login, tab_signup = st.tabs([t("login_tab"), t("signup_tab")])
        
        with tab_login:
            with st.form("login_form"):
                log_email = st.text_input(t("email_label"), placeholder=t("email_placeholder"))
                log_pass = st.text_input(t("password_label"), type="password", placeholder="••••••••")
                submit_btn = st.form_submit_button(t("login_btn"), width='stretch', type="primary")
                if submit_btn:
                    user_data = login_user(log_email, log_pass)
                    if user_data:
                        u_id, u_email, u_name, u_role, u_active = user_data
                        if u_active == 1:
                            st.session_state.user = {"id": u_id, "email": u_email, "name": u_name, "role": u_role}
                            st.rerun()
                        else:
                            st.warning(t("pending_approval"))
                    else:
                        st.error(t("invalid_credentials"))

            with st.expander(t("forgot_pwd")):
                t1, t2 = st.tabs([t("tab_req_code"), t("tab_new_pwd")])
                with t1:
                    r_email = st.text_input(t("email_label"), key="r_mail")
                    if st.button(t("send_code_btn"), width='stretch'):
                        cur = conn.cursor()
                        cur.execute("SELECT id, is_active FROM users WHERE email = ?", (r_email.strip().lower(),))
                        row = cur.fetchone()
                        if row and row[1] == 1:
                            code = str(random.randint(100000, 999999))
                            cur.execute("REPLACE INTO reset_tokens (email, token) VALUES (?, ?)", (r_email.strip().lower(), code))
                            conn.commit()
                            notifier.send_email(r_email.strip().lower(), "Reset Code", f"<p>Code: <b>{code}</b></p>")
                            st.success(t("code_sent", email=r_email))
                        else:
                            st.error(t("user_not_found"))
                with t2:
                    v_mail = st.text_input(t("email_label"), key="v_mail")
                    v_code = st.text_input(t("code_label"), key="v_code")
                    v_pass = st.text_input(t("new_pass_label"), type="password", key="v_pass")
                    if st.button(t("save_pass_btn"), width='stretch'):
                        cur = conn.cursor()
                        cur.execute("SELECT token FROM reset_tokens WHERE email = ?", (v_mail.strip().lower(),))
                        r = cur.fetchone()
                        if r and r[0] == v_code.strip():
                            cur.execute("UPDATE users SET password_hash = ? WHERE email = ?", (hash_password(v_pass), v_mail.strip().lower()))
                            cur.execute("DELETE FROM reset_tokens WHERE email = ?", (v_mail.strip().lower(),))
                            conn.commit()
                            st.success(t("pass_updated"))
                        else:
                            st.error(t("invalid_code"))

        with tab_signup:
            with st.form("signup_form"):
                st.caption(t("signup_caption"))
                reg_name = st.text_input(t("name_label"))
                reg_email = st.text_input(t("email_label"))
                reg_pass = st.text_input(t("create_pass_label"), type="password")
                signup_btn = st.form_submit_button(t("signup_btn"), width='stretch', type="primary")
                if signup_btn:
                    if reg_name.strip() and reg_email.strip() and reg_pass:
                        ok, msg = apply_for_registration(reg_email, reg_pass, reg_name)
                        if ok:
                            st.success(t("pending_approval"))
                        else:
                            st.error(msg)
                    else:
                        st.warning(t("fill_all_fields"))
    st.stop()

current_user = st.session_state.user
if not current_user:
    st.stop()

with st.sidebar:
    role_icon = "👑" if current_user['role'] == "superadmin" else "💼"
    role_label = t("role_admin") if current_user['role'] == "superadmin" else t("role_user")
    
    st.markdown(f"""
    <div class="user-profile-box">
        <div style="font-size: 15px; font-weight: 700; color: #f8fafc; margin-bottom: 2px;">{role_icon} {current_user['name']}</div>
        <div style="font-size: 11.5px; color: #94a3b8; margin-bottom: 7px;">{current_user['email']}</div>
        <span class="invoice-badge" style="background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3);">{role_label}</span>
    </div>
    """, unsafe_allow_html=True)
    
    view_all_users = False
    if current_user["role"] == "superadmin":
        view_all_users = st.toggle(t("manager_mode"), value=False)
        st.caption(t("caption_all") if view_all_users else t("caption_my"))

    if st.button(t("logout_btn"), width='stretch'):
        st.session_state.user = None
        st.rerun()

    st.markdown("<hr style='border-color: rgba(255,255,255,0.08); margin: 16px 0;'>", unsafe_allow_html=True)
    cur = conn.cursor()
    cur.execute("SELECT imap_server, imap_port, imap_user, imap_password, imap_folder FROM users WHERE id = ?", (current_user["id"],))
    u_imap = cur.fetchone()
    
    cur_server = u_imap[0] or "imap.mail.ee"
    cur_port = u_imap[1] or 993
    cur_user = u_imap[2] or current_user["email"]
    cur_pass = u_imap[3] or ""
    cur_folder = u_imap[4] or "INBOX"

    with st.expander(t("imap_expander")):
        st.caption(t("imap_caption"))
        with st.form("imap_settings_form"):
            new_srv = st.text_input(t("imap_server"), value=cur_server)
            new_port = st.number_input(t("imap_port"), value=int(cur_port), step=1)
            new_usr = st.text_input(t("imap_login"), value=cur_user)
            new_pwd = st.text_input(t("imap_pass"), value=cur_pass, type="password")
            new_fld = st.text_input(t("imap_folder"), value=cur_folder)
            
            if st.form_submit_button(t("imap_save_btn"), width='stretch'):
                cur.execute("""
                    UPDATE users
                    SET imap_server = ?, imap_port = ?, imap_user = ?, imap_password = ?, imap_folder = ?
                    WHERE id = ?
                """, (new_srv.strip(), int(new_port), new_usr.strip(), new_pwd.strip(), new_fld.strip(), current_user["id"]))
                conn.commit()
                st.success(t("imap_saved"))
                st.rerun()

    if current_user["role"] == "superadmin":
        st.markdown("<hr style='border-color: rgba(255,255,255,0.08); margin: 16px 0;'>", unsafe_allow_html=True)
        cur.execute("SELECT id, name, email FROM users WHERE is_active = 0")
        pending_requests = cur.fetchall()
        req_count = len(pending_requests)
        header_text = f"{t('access_requests')} ({req_count})" if req_count > 0 else t('access_requests')
        
        with st.expander(header_text, expanded=(req_count > 0)):
            if pending_requests:
                for req in pending_requests:
                    p_id, p_name, p_email = req
                    st.markdown(f"**{p_name}**<br><small style='color: #94a3b8;'>{p_email}</small>", unsafe_allow_html=True)
                    c_appr, c_rej = st.columns(2)
                    if c_appr.button(t("btn_approve"), key=f"appr_{p_id}", width='stretch'):
                        cur.execute("UPDATE users SET is_active = 1, approval_token = NULL WHERE id = ?", (p_id,))
                        conn.commit()
                        st.success(t("user_activated", name=p_name))
                        st.rerun()
                    if c_rej.button(t("btn_reject"), key=f"rej_{p_id}", width='stretch'):
                        cur.execute("DELETE FROM users WHERE id = ?", (p_id,))
                        conn.commit()
                        st.warning(t("user_rejected"))
                        st.rerun()
                    st.markdown("<hr style='margin: 8px 0; border-color: rgba(255,255,255,0.06);'>", unsafe_allow_html=True)
            else:
                st.info(t("no_requests"))

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
            st.warning(t("due_tomorrow_alert", date=tomorrow_str, id=inv[0], sender=inv[1], amount=f"{inv[2]:.2f}", payer=inv[3]))
        for inv in overdue:
            st.error(t("overdue_alert", date=inv[3], id=inv[0], sender=inv[1], amount=f"{inv[2]:.2f}"))

render_reminders()

cur = conn.cursor()
user_kpi_filter = "" if view_all_users else f" AND created_by = '{current_user['email']}'"
kpi_df = pd.read_sql_query(f"SELECT amount, status, due_date FROM invoices WHERE status != 'В архиве'{user_kpi_filter}", conn)

m_total = kpi_df["amount"].sum() if not kpi_df.empty else 0.0
m_paid = kpi_df[kpi_df["status"] == "Оплачен"]["amount"].sum() if not kpi_df.empty else 0.0
m_pending = kpi_df[kpi_df["status"] != "Оплачен"]["amount"].sum() if not kpi_df.empty else 0.0

today_iso = date.today().strftime("%Y-%m-%d")
m_overdue = kpi_df[(kpi_df["status"] != "Оплачен") & (kpi_df["due_date"] < today_iso)]["amount"].sum() if not kpi_df.empty else 0.0

col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric(t("kpi_total"), f"{m_total:,.2f} €".replace(",", " "))
col_m2.metric(t("kpi_paid"), f"{m_paid:,.2f} €".replace(",", " "))
col_m3.metric(t("kpi_pending"), f"{m_pending:,.2f} €".replace(",", " "))
col_m4.metric(t("kpi_overdue"), f"{m_overdue:,.2f} €".replace(",", " "), delta=f"-{m_overdue:,.2f} €" if m_overdue > 0 else None, delta_color="inverse")

st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

tab_registry, tab_archive, tab_senders, tab_payers = st.tabs([
    t("tab_registry"),
    t("tab_archive"),
    t("tab_senders"),
    t("tab_payers")
])

with tab_registry:
    col_up, col_table = st.columns([1.0, 2.0])
    
    with col_up:
        st.markdown(f"<h4 style='margin-bottom: 10px;'>{t('add_hdr')}</h4>", unsafe_allow_html=True)
        mode = st.radio(t("mode_label"), [t("mode_ai"), t("mode_manual"), t("mode_mail")], horizontal=True)
        
        if mode == t("mode_ai"):
            up_file = st.file_uploader(t("attach_label"), type=["pdf", "png", "jpg", "jpeg"], key="auto_file")
            if up_file and st.button(t("btn_save_invoice"), width='stretch', type="primary"):
                with st.spinner(t("ai_processing")):
                    try:
                        raw_bytes = up_file.getvalue()
                        m_type = "application/pdf" if up_file.name.lower().endswith(".pdf") else "image/jpeg"
                        data = extract_invoice_data(raw_bytes, m_type)
                        
                        sender_name = data.get("sender") or "Vendor"
                        amt = float(data.get("amount") or 0.0)
                        d_date = data.get("due_date") or (date.today() + timedelta(days=7)).strftime("%Y-%m-%d")
                        payer_name = data.get("payer") or t("default_payer")
                        iban_val = (data.get("iban") or "").replace(" ", "").strip()
                        ref_val = (str(data.get("reference_number") or "")).replace(" ", "").strip()
                        
                        saved_path = save_file_to_storage(raw_bytes, up_file.name, sender_name)
                        
                        cur = conn.cursor()
                        cur.execute("""
                            INSERT INTO invoices (payer, sender, amount, due_date, status, created_by, file_path, iban, ref_number)
                            VALUES (?, ?, ?, ?, 'Ожидает оплаты', ?, ?, ?, ?)
                        """, (payer_name, sender_name, amt, d_date, current_user["email"], saved_path, iban_val, ref_val))
                        conn.commit()
                        st.success(t("ai_added", sender=sender_name, amount=f"{amt:.2f}"))
                        st.rerun()
                    except Exception as err:
                        st.error(t("ai_error", err=err))

        elif mode == t("mode_manual"):
            with st.form("manual_invoice_form", clear_on_submit=True):
                m_sender = st.text_input(t("field_vendor"))
                m_payer = st.text_input(t("field_payer"), value=t("default_payer"))
                m_amount = st.number_input(t("field_amount"), min_value=0.01, step=0.01, format="%.2f")
                m_due_date = st.date_input(t("field_due_date"), value=date.today() + timedelta(days=7))
                m_iban = st.text_input(t("field_iban"), placeholder="EE...")
                m_ref = st.text_input(t("field_ref"))
                m_file = st.file_uploader(t("attach_label"), type=["pdf", "png", "jpg", "jpeg"])
                
                if st.form_submit_button(t("btn_save_invoice"), width='stretch', type="primary"):
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
                        st.success(t("invoice_saved"))
                        st.rerun()
                    else:
                        st.error(t("err_specify_vendor"))

        else:
            cur = conn.cursor()
            cur.execute("SELECT imap_server, imap_port, imap_user, imap_password, imap_folder FROM users WHERE id = ?", (current_user["id"],))
            user_mail = cur.fetchone()
            
            srv, prt, usr, pwd, fld = user_mail if user_mail else (None, None, None, None, None)
            is_configured = bool(srv and usr and pwd)

            with st.expander(t("mail_guide_title"), expanded=not is_configured):
                st.markdown(t("mail_guide_body"))

            if not is_configured:
                st.warning(t("mail_not_configured"))
            else:
                st.success(t("mail_connected", user=usr, folder=fld or 'INBOX'))
                if st.button(t("btn_check_mail"), width='stretch', type="primary"):
                    with st.spinner(t("mail_scanning")):
                        count_added, err_list = fetch_invoices_via_imap(
                            srv, prt or 993, usr, pwd, fld or "INBOX", current_user["email"]
                        )
                        if count_added > 0:
                            st.success(t("mail_success", count=count_added))
                            st.rerun()
                        elif not err_list:
                            st.info(t("mail_empty"))
                        if err_list:
                            for err_msg in err_list:
                                st.error(err_msg)

    with col_table:
        st.markdown(f"<h4 style='margin-bottom: 10px;'>{t('pending_hdr')}</h4>", unsafe_allow_html=True)
        
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
                status_text = t("status_paid") if status == "Оплачен" else t("status_pending")
                author_badge = f" {t('meta_author')} <b style='color:#e2e8f0;'>{author}</b>" if view_all_users else ""
                due_label = due_d or t("meta_no_due")
                
                st.markdown(f'<div class="invoice-card"><div class="invoice-header"><div class="invoice-sender">#{inv_id} {sender}</div><div class="invoice-amount">{amount:,.2f} €</div></div><div class="invoice-meta"><span class="invoice-badge {b_cls}">{status_text}</span><span>{t("meta_due")} <b style="color: #f1f5f9;">{due_label}</b></span><span>{t("meta_payer")} <b style="color: #f1f5f9;">{payer}</b></span>{author_badge}</div></div>', unsafe_allow_html=True)

                c_details, c_action = st.columns([2.3, 1.7])

                with c_details:
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
                                f'<div style="display: flex; gap: 6px; align-items: center; margin-top: 2px; margin-bottom: 6px; flex-wrap: wrap;">'
                                f'<span style="font-size: 11.5px; color: #94a3b8; font-weight: 600;">{t("bank_label")}</span>'
                                '<a class="bank-chip bank-lhv" href="https://www.lhv.ee" target="_blank">LHV</a>'
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
                                label=t("btn_view_file", name=fname),
                                data=f_obj.read(),
                                file_name=fname,
                                mime=mime_t,
                                key=f"dl_file_{inv_id}",
                                width='stretch'
                            )

                with c_action:
                    row1_c1, row1_c2 = st.columns(2)
                    if status == "Ожидает оплаты":
                        if row1_c1.button(t("btn_paid"), key=f"pay_{inv_id}", width='stretch'):
                            cur.execute("UPDATE invoices SET status = 'Оплачен', paid_date = ? WHERE id = ?", (date.today().strftime("%Y-%m-%d"), inv_id))
                            conn.commit()
                            st.rerun()
                    
                    if row1_c2.button(t("btn_archive"), key=f"arch_{inv_id}", width='stretch'):
                        cur.execute("UPDATE invoices SET status = 'В архиве' WHERE id = ?", (inv_id,))
                        conn.commit()
                        st.rerun()

                    row2_c1, row2_c2 = st.columns(2)
                    with row2_c1:
                        with st.popover(t("pop_due_btn")):
                            st.markdown(f"**#{inv_id} {sender}**")
                            new_rem_date = st.date_input(t("pop_new_date"), value=date.today() + timedelta(days=3), key=f"rem_date_{inv_id}")
                            if st.button(t("pop_save_btn"), key=f"save_rem_{inv_id}", width='stretch'):
                                cur.execute("UPDATE invoices SET due_date = ? WHERE id = ?", (new_rem_date.strftime("%Y-%m-%d"), inv_id))
                                conn.commit()
                                st.rerun()
                    with row2_c2:
                        if current_user["role"] == "superadmin" or current_user["email"] == author:
                            with st.popover(t("pop_del_btn")):
                                st.write(t("pop_del_confirm"))
                                if st.button(t("btn_yes"), key=f"del_{inv_id}", type="primary", width='stretch'):
                                    cur.execute("DELETE FROM invoices WHERE id = ?", (inv_id,))
                                    conn.commit()
                                    st.rerun()

                st.markdown("<hr style='border-color: rgba(255,255,255,0.06); margin: 8px 0 12px 0;'>", unsafe_allow_html=True)
        else:
            st.info(t("no_pending_invoices"))

with tab_archive:
    st.markdown(f"<h4 style='margin-bottom: 12px;'>{t('arch_hdr')}</h4>", unsafe_allow_html=True)
    
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
        st.caption(t("arch_summary", count=len(arch_rows), total=f"{total_arch_amt:,.2f}".replace(",", " ")))
        
        for r in arch_rows:
            inv_id, sender, amount, due_d, status, payer, author, f_path, iban, ref_no, paid_d = r
            author_badge = f" {t('meta_author')} <b style='color:#e2e8f0;'>{author}</b>" if view_all_users else ""
            paid_info = f" {t('arch_paid_on', date=paid_d)}" if paid_d else ""
            due_label = due_d or t("meta_no_due")
            
            st.markdown(f'<div class="invoice-card" style="opacity: 0.88; border-color: rgba(148, 163, 184, 0.2);"><div class="invoice-header"><div class="invoice-sender">#{inv_id} {sender}</div><div class="invoice-amount" style="color: #94a3b8;">{amount:,.2f} €</div></div><div class="invoice-meta"><span class="invoice-badge badge-archived">{t("arch_badge")}</span><span>{t("meta_due")} {due_label}{paid_info}</span><span>{t("meta_payer")} {payer}</span>{author_badge}</div></div>', unsafe_allow_html=True)

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
                            label=t("btn_view_file", name=fname),
                            data=f_obj.read(),
                            file_name=fname,
                            mime=mime_t,
                            key=f"dl_arch_{inv_id}",
                            width='stretch'
                        )

            with c_arch_act:
                c_ret, c_del = st.columns(2)
                if c_ret.button(t("btn_restore"), key=f"rest_{inv_id}", width='stretch'):
                    cur.execute("UPDATE invoices SET status = 'Ожидает оплаты' WHERE id = ?", (inv_id,))
                    conn.commit()
                    st.success(t("arch_restored"))
                    st.rerun()

                if current_user["role"] == "superadmin" or current_user["email"] == author:
                    with c_del.popover(t("pop_del_btn")):
                        st.write(t("pop_del_perm"))
                        if st.button(t("btn_yes"), key=f"del_arch_{inv_id}", type="primary", width='stretch'):
                            cur.execute("DELETE FROM invoices WHERE id = ?", (inv_id,))
                            conn.commit()
                            st.rerun()

            st.markdown("<hr style='border-color: rgba(255,255,255,0.05); margin: 8px 0 12px 0;'>", unsafe_allow_html=True)
    else:
        st.info(t("arch_empty"))

with tab_senders:
    st.markdown(f"<h4 style='margin-bottom: 12px;'>{t('senders_hdr')}</h4>", unsafe_allow_html=True)
    if view_all_users:
        df = pd.read_sql_query("SELECT * FROM invoices WHERE status != 'В архиве'", conn)
    else:
        df = pd.read_sql_query("SELECT * FROM invoices WHERE status != 'В архиве' AND created_by = ?", conn, params=(current_user["email"],))
    
    if not df.empty and "sender" in df.columns:
        senders_list = sorted([s for s in df["sender"].dropna().unique() if str(s).strip()])
        if senders_list:
            selected_sender = st.selectbox(t("select_vendor"), senders_list)
            s_df = df[df["sender"] == selected_sender]
            
            total_s = s_df["amount"].sum()
            paid_s = s_df[s_df["status"] == "Оплачен"]["amount"].sum()
            pending_s = s_df[s_df["status"] != "Оплачен"]["amount"].sum()

            m1, m2, m3 = st.columns(3)
            m1.metric(t("kpi_vendor_total", name=selected_sender), f"{total_s:,.2f} €".replace(",", " "))
            m2.metric(t("kpi_vendor_paid"), f"{paid_s:,.2f} €".replace(",", " "))
            m3.metric(t("kpi_vendor_pending"), f"{pending_s:,.2f} €".replace(",", " "))

            cols_show = ["id", "due_date", "payer", "amount", "iban", "ref_number", "status"]
            cols_exist = [c for c in cols_show if c in s_df.columns]
            table_display = s_df[cols_exist].rename(
                columns={
                    "id": t("th_num"),
                    "due_date": t("th_due"),
                    "payer": t("th_payer"),
                    "amount": t("th_amount"),
                    "iban": t("th_iban"),
                    "ref_number": t("th_ref"),
                    "status": t("th_status")
                }
            )
            st.dataframe(table_display, width='stretch', hide_index=True)
        else:
            st.info(t("no_vendor_data"))
    else:
        st.info(t("registry_empty"))

with tab_payers:
    st.markdown(f"<h4 style='margin-bottom: 12px;'>{t('payers_hdr')}</h4>", unsafe_allow_html=True)
    if view_all_users:
        df = pd.read_sql_query("SELECT * FROM invoices WHERE status != 'В архиве'", conn)
    else:
        df = pd.read_sql_query("SELECT * FROM invoices WHERE status != 'В архиве' AND created_by = ?", conn, params=(current_user["email"],))
    
    if not df.empty and "payer" in df.columns:
        payers_list = sorted([p for p in df["payer"].dropna().unique() if str(p).strip()])
        if payers_list:
            selected_payer = st.selectbox(t("select_payer"), payers_list)
            p_df = df[df["payer"] == selected_payer]
            
            total_p = p_df["amount"].sum()
            paid_p = p_df[p_df["status"] == "Оплачен"]["amount"].sum()
            pending_p = p_df[p_df["status"] != "Оплачен"]["amount"].sum()

            p1, p2, p3 = st.columns(3)
            p1.metric(t("kpi_payer_total", name=selected_payer), f"{total_p:,.2f} €".replace(",", " "))
            p2.metric(t("kpi_payer_paid"), f"{paid_p:,.2f} €".replace(",", " "))
            p3.metric(t("kpi_payer_pending"), f"{pending_p:,.2f} €".replace(",", " "))

            cols_p_show = ["id", "due_date", "sender", "amount", "iban", "ref_number", "status"]
            cols_p_exist = [c for c in cols_p_show if c in p_df.columns]
            table_payer = p_df[cols_p_exist].rename(
                columns={
                    "id": t("th_num"),
                    "due_date": t("th_due"),
                    "sender": t("th_vendor"),
                    "amount": t("th_amount"),
                    "iban": t("th_iban"),
                    "ref_number": t("th_ref"),
                    "status": t("th_status")
                }
            )
            st.dataframe(table_payer, width='stretch', hide_index=True)

            csv_data = p_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label=t("btn_csv_export", name=selected_payer),
                data=csv_data,
                file_name=f"report_{selected_payer}_{date.today().strftime('%Y-%m-%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info(t("no_payer_data"))
    else:
        st.info(t("registry_empty"))

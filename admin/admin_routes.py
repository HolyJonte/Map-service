# Denna modul innehåller Flask-rutter för adminflödet i Trafikvida
# Den ansvarar för:
# - Att visa inloggningssidan och hanterera POST-anrop
# - Att styra flödet genom sessionhantering (lösenord, QR och TOTP)
# - Att rendera adminpanelen med funktioner för att hantera tidningar
# - Adminpanel för att hantera tidningar (lägga till/ ta bort / se lista med tidningar)
# - Utloggning


# Flask-importer
from flask import Blueprint, render_template, request, redirect, url_for, session
from admin.admin_logic import (
    get_admin_password,
    get_all_newspapers,
    add_newspaper,
    delete_newspaper,
    verify_totp_code,
    get_totp_uri
)


# Importera nödvändiga moduler för QR-kodsgenerering
import base64
from io import BytesIO
import qrcode

# Skapar en Blueprint för admin-rutter och kopplar till templates-mappen
admin_routes = Blueprint('admin', __name__, template_folder='../frontend/templates')



# ==============================================================================================
# Inloggning
# ==============================================================================================
@admin_routes.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('password') == get_admin_password():
            session['awaiting_2fa'] = True
            session['show_qr'] = True  # 🔁 Visa QR först
            return redirect(url_for('admin.show_qr'))
        else:
            return render_template('admin_login.html', error="Fel lösenord")
    return render_template('admin_login.html')



# ==============================================================================================
# Tvåfaktorsautentisering (2FA)
# ==============================================================================================
@admin_routes.route('/admin/2fa', methods=['GET', 'POST'])
def two_factor():
    if not session.get('awaiting_2fa'):
        return redirect(url_for('admin.admin_login'))

    if request.method == 'POST':
        code = request.form.get('code')
        if verify_totp_code(code):
            session.pop('awaiting_2fa', None)
            session['admin_logged_in'] = True
            return redirect(url_for('admin.admin_dashboard'))
        else:
            return render_template('admin_two_factor.html', error="Fel kod")

    return render_template('admin_two_factor.html')



# ==============================================================================================
# Adminpanel för tidningar
# ==============================================================================================
@admin_routes.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))

    from admin.admin_logic import get_all_newspapers, add_newspaper, delete_newspaper

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add':
            name = request.form.get('name')
            contact_email = request.form.get('contact_email')
            sms_quota = request.form.get('sms_quota')
            sms_quota_int = int(sms_quota) if sms_quota and sms_quota.isdigit() else None
            if name:
                add_newspaper(name, contact_email, sms_quota_int)

        #  Funktion för att ta bort tidning (har print för debugning)
        elif action == 'delete':
            newspaper_id = request.form.get('id')
            print("🗑️ Försöker ta bort id:", newspaper_id)  # <-- debug
            if newspaper_id:
                delete_newspaper(int(newspaper_id))


    newspapers = get_all_newspapers()
    return render_template('admin_dashboard.html', newspapers=newspapers)


# ================================================================================================
# Visa QR-kod för 2FA
# ================================================================================================
@admin_routes.route('/admin/show-qr')
def show_qr():
    if not session.get('awaiting_2fa') or not session.get('show_qr'):
        return redirect(url_for('admin.admin_login'))

    # Skapa QR-bild
    uri = get_totp_uri()
    img = qrcode.make(uri)
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    # Efter visning rensar vi show_qr-flaggan
    session.pop('show_qr', None)

    return render_template('admin_show_qr.html', qr_data=img_base64)



# =================================================================================================
# Logga ut
# =================================================================================================
@admin_routes.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('serve_index'))
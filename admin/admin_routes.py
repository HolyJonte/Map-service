from flask import Blueprint, render_template, request, redirect, url_for, session
from admin.admin_logic import (
    get_admin_password,
    load_newspapers,
    save_newspapers,
    verify_totp_code,
    get_totp_uri
)

import base64
from io import BytesIO
import qrcode

admin_routes = Blueprint('admin', __name__, template_folder='../frontend/templates')

# ===============================
# Inloggning
# ===============================
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


# ===============================
# Tvåfaktorsautentisering (2FA)
# ===============================
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
            return render_template('two_factor.html', error="Fel kod")

    return render_template('two_factor.html')

# ===============================
# Adminpanel för tidningar
# ===============================
@admin_routes.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))

    newspapers = load_newspapers()

    if request.method == 'POST':
        action = request.form.get('action')
        name = request.form.get('name')

        if action == 'add' and name and name not in newspapers:
            newspapers.append(name)
        elif action == 'delete' and name in newspapers:
            newspapers.remove(name)

        save_newspapers(newspapers)

    return render_template('admin_dashboard.html', newspapers=newspapers)

# ===============================
# Visa QR-kod för 2FA
# ===============================
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

    return render_template('show_qr.html', qr_data=img_base64)

# ===============================
# Logga ut
# ===============================
@admin_routes.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin.admin_login'))
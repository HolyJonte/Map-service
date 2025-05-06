# Denna modul innehåller Flask-rutter för adminflödet i Trafikvida
# Den ansvarar för:
# - Att styra flödet genom sessionhantering (lösenord och QR)
# - Adminpanel för att hantera tidningar (lägga till/ ta bort / se lista med tidningar / antal SMS per tidning)
# - Utloggning

# Flask-importer
from flask import Blueprint, render_template, request, redirect, url_for, session

# Importerar funktioner från admin_logic
from admin.admin_logic import (
    get_all_newspapers,
    add_newspaper,
    delete_newspaper,
    update_admin_password
)

# Skapar en Blueprint för admin-rutter och kopplar till templates-mappen
admin_routes = Blueprint('admin', __name__, template_folder='../frontend/templates')

# ==============================================================================================
# Adminpanel för tidningar
# ==============================================================================================
@admin_routes.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('user_routes.login'))

    if request.method == 'POST':
        action = request.form.get('action')

        # Lägg till tidning
        if action == 'add':
            name = request.form.get('name')
            contact_email = request.form.get('contact_email')
            sms_quota = request.form.get('sms_quota')
            sms_quota_int = int(sms_quota) if sms_quota and sms_quota.isdigit() else None
            if name:
                add_newspaper(name, contact_email, sms_quota_int)

        # Ta bort tidning
        elif action == 'delete':
            newspaper_id = request.form.get('id')
            if newspaper_id:
                delete_newspaper(int(newspaper_id))

        # Ändra lösenord
        elif action == 'change_password':
            pw1 = request.form.get('new_password')
            pw2 = request.form.get('confirm_password')
            if pw1 and pw2 and pw1 == pw2:
                update_admin_password(pw1)
            else:
                return render_template('admin_dashboard.html', newspapers=get_all_newspapers(), error="Lösenorden matchar inte.")

    # Hämtar alla tidningar
    newspapers = get_all_newspapers()
    return render_template('admin_dashboard.html', newspapers=newspapers)

# =================================================================================================
# Logga ut
# =================================================================================================
@admin_routes.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('serve_index'))


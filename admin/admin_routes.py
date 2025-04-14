from flask import Blueprint, render_template, request, redirect, url_for, session
from admin.admin_logic import (
    get_admin_password,
    load_newspapers,
    save_newspapers
)

admin_routes = Blueprint('admin', __name__, template_folder='../frontend/templates')

# ===============================
@admin_routes.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('password') == get_admin_password():
            session['admin_logged_in'] = True
            return redirect(url_for('admin.admin_dashboard'))
        else:
            return render_template('admin_login.html', error="Fel lösenord")
    return render_template('admin_login.html')

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
@admin_routes.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin.admin_login'))

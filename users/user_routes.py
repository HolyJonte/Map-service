from flask import Blueprint, render_template, request, redirect, url_for, session
from users.user_logic import (
    find_user_by_email,
    register_user,
    generate_user_qr_base64,
    validate_login,
    verify_totp_code
)

user_routes = Blueprint('user_routes', __name__, template_folder='../frontend/templates')

# ===============================
# Registrering
# ===============================
@user_routes.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if find_user_by_email(email):
            return render_template('user_register.html', error="E-post finns redan")

        register_user(email, password)

        session['user_email'] = email
        session['user_awaiting_2fa'] = True
        session['show_user_qr'] = True
        return redirect(url_for('user_routes.show_user_qr'))

    return render_template('user_register.html')

# ===============================
# Inloggning
# ===============================
@user_routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = validate_login(email, password)

        if user:
            session['user_email'] = email
            session['user_awaiting_2fa'] = True
            session['show_user_qr'] = True
            return redirect(url_for('user_routes.show_user_qr'))

        return render_template('user_login.html', error="Fel e-post eller lösenord")
    return render_template('user_login.html')

# ===============================
# Visa QR-kod
# ===============================
@user_routes.route('/show-qr')
def show_user_qr():
    if not session.get('user_awaiting_2fa') or not session.get('show_user_qr'):
        return redirect(url_for('user_routes.login'))

    email = session.get('user_email')
    user = find_user_by_email(email)

    if not user:
        return redirect(url_for('user_routes.login'))

    qr_data = generate_user_qr_base64(user)

    session.pop('show_user_qr', None)
    return render_template('user_show_qr.html', qr_data=qr_data)

# ===============================
# Verifiera 2FA-kod
# ===============================
@user_routes.route('/2fa', methods=['GET', 'POST'])
def verify_user_2fa():
    if not session.get('user_awaiting_2fa'):
        return redirect(url_for('user_routes.login'))

    email = session.get('user_email')
    user = find_user_by_email(email)

    if request.method == 'POST':
        code = request.form.get('code')
        if user and verify_totp_code(user, code):
            session.pop('user_awaiting_2fa', None)
            session['user_logged_in'] = True
            return redirect('/')

        return render_template('user_two_factor.html', error="Fel kod")
    return render_template('user_two_factor.html')

# ===============================
# Logga ut
# ===============================
@user_routes.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('serve_index'))

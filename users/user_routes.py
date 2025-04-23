from flask import Blueprint, render_template, request, redirect, url_for, session
from users.user_logic import (
    find_user_by_email,
    register_user,
    generate_user_qr_base64,
    validate_login,
    verify_totp_code
)

user_routes = Blueprint('user_routes', __name__, template_folder='../frontend/templates')


# ======================================================
# Logga in som admin, user eller registera ny användare
# ======================================================

@user_routes.route('/login-choice')
def serve_login_choice():
    return render_template('login_choice.html')

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

        # Skapa användaren
        register_user(email, password)

        # Spara session
        session['user_email'] = email
        session['user_awaiting_2fa'] = True
        session['show_user_qr'] = True

        # Kolla om vi har en sparad redirect efter 2FA
        next_page = session.pop('next', None)
        if next_page:
            session['after_2fa_redirect'] = next_page

        return redirect(url_for('user_routes.register_confirmation'))

    return render_template('user_register.html')


# ===============================
# Registrering Bekräftelse
# ===============================
@user_routes.route('/register-confirmation')
def register_confirmation():
    if not session.get('user_email'):
        return redirect(url_for('user_routes.login'))
    return render_template('user_register_confirmation.html')


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
            # Spara användaruppgifter i session
            session['user_email'] = email
            session['user_awaiting_2fa'] = True
            session['show_user_qr'] = True

            # Kontrollera om vi har en redirect-sida sparad
            next_page = session.pop('next', None)
            if next_page:
                session['after_2fa_redirect'] = next_page

            # Skicka till QR-sidan för 2FA
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
            session['user_id'] = user.id
            redirect_url = session.pop('after_2fa_redirect', '/')
            return redirect(redirect_url)


        return render_template('user_two_factor.html', error="Fel kod")
    return render_template('user_two_factor.html')

# ===============================
# Logga ut
# ===============================
@user_routes.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('serve_index'))

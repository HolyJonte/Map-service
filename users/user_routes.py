# Denna modul hanterar alla routes för användarinloggning, registrering och 2FA-verifiering i Trafikvida.
# Funktionalitet:
# - Registrering
# - Inloggning med lösenord
# - 2FA med TOTP + QR-kod
# - Utloggning

# Flask-importer
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify

# Importerar funktioner från lokigen i user_logic.py
from users.user_logic import (
    find_user_by_email,
    register_user,
    generate_user_qr_base64,
    validate_login,
    verify_totp_code
)
from database.crud.subscriber_crud import get_subscriber_by_user_id, update_subscriber_county, delete_subscriber
from database.county_utils import get_counties


# Skapar en Bluepring för användarrelaterade rutter
user_routes = Blueprint('user_routes', __name__, template_folder='../frontend/templates')


# =================================================================================================
# Logga in som admin, user eller registera ny användare
# =================================================================================================

@user_routes.route('/login-choice')
def serve_login_choice():
    return render_template('login_choice.html')

# =================================================================================================
# Registrering
# =================================================================================================
@user_routes.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        confirm_email = request.form['confirm_email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if email != confirm_email:
            return render_template('user_register.html', error="E-postadresserna matchar inte")

        if password != confirm_password:
            return render_template('user_register.html', error="Lösenorden matchar inte")

        if find_user_by_email(email):
            return render_template('user_register.html', error="E-post finns redan")

        register_user(email, password)

        session['user_email'] = email
        session['user_awaiting_2fa'] = True
        session['show_user_qr'] = True

        next_page = session.pop('next', None)
        if next_page:
            session['after_2fa_redirect'] = next_page

        return redirect(url_for('user_routes.register_confirmation'))

    return render_template('user_register.html')


# =================================================================================================
# Bekräftelse efter registrering
# =================================================================================================
@user_routes.route('/register-confirmation')
def register_confirmation():
    if not session.get('user_email'):
        return redirect(url_for('user_routes.login'))
    return render_template('user_register_confirmation.html')


# =================================================================================================
# Inloggning
# =================================================================================================
@user_routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = validate_login(email, password)


        if user:
            # Spara användarinfo i session
            session['user_email'] = user.email
            session['user_awaiting_2fa'] = True
            session['is_admin'] = user.is_admin
            session['show_user_qr'] = True

            return redirect(url_for('user_routes.show_user_qr'))

        return render_template('user_login.html', error="Fel e-post eller lösenord")

    return render_template('user_login.html')


# ====================================================================================================
# Visa QR-kod
# ====================================================================================================
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

# =====================================================================================================
# Verifiera 2FA-kod
# =====================================================================================================
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

            if session.get('is_admin'):
                session['admin_logged_in'] = True
                return redirect(url_for('admin.admin_dashboard'))

            redirect_url = session.pop('after_2fa_redirect', '/')
            return redirect(redirect_url)

        return render_template('user_two_factor.html', error="Fel kod")

    return render_template('user_two_factor.html')


# =====================================================================================================
# Mina sidor
# =====================================================================================================
@user_routes.route('/profile')
def profile():
    user_id = session.get('user_id')

    subscriber = get_subscriber_by_user_id(user_id)
    is_active_subscriber = subscriber and subscriber.active == 1

    # Mappa numeriskt county-värde till text
    county_map = get_counties()
    county_text = county_map.get(subscriber.county, "Okänt län") if subscriber else None

    subscriber_data = {
        'is_active_subscriber': is_active_subscriber,
        'subscriber_id': subscriber.id if subscriber else None,
        'phone_number': subscriber.phone_number if subscriber else None,
        'county': county_text  # Skicka text istället för siffra
    }
    return render_template('user_profile.html', **subscriber_data)

# =====================================================================================================
# Uppdatering av län på Mina sidor
# =====================================================================================================
@user_routes.route('/profile/update-county', methods=['POST'])
def update_county():
    user_id = session.get('user_id')

    subscriber = get_subscriber_by_user_id(user_id)
    if not subscriber or not subscriber.active:
        return jsonify({"error": "Ingen aktiv prenumeration hittades"}), 404

    data = request.get_json()
    new_county = data.get('county')
    if not new_county:
        return jsonify({"error": "Inget län angivet"}), 400

    try:
        new_county_int = int(new_county)
    except (ValueError, TypeError):
        return jsonify({"error": "Ogiltigt län (måste vara ett nummer)"}), 400

    county_map = get_counties()
    if new_county_int not in county_map:
        return jsonify({"error": "Ogiltigt län"}), 400

    success = update_subscriber_county(subscriber.id, subscriber.phone_number, new_county_int)
    if success:
        return jsonify({"message": "Län uppdaterat", "county_name": county_map[new_county_int]}), 200
    else:
        return jsonify({"error": "Kunde inte uppdatera län"}), 500
    
#=====================================================================================================
# Avsluta prenumeration
# =====================================================================================================
@user_routes.route('/profile/unsubscribe', methods=['POST'])
def unsubscribe():
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"error": "Användaren är inte inloggad"}), 401

        subscriber = get_subscriber_by_user_id(user_id)
        if not subscriber:
            return jsonify({"error": "Ingen aktiv prenumeration hittades"}), 404

        # Logga subscriber.id för felsökning
        print(f"Subscriber ID: {subscriber.id}, Typ: {type(subscriber.id)}")

        if not subscriber.active:
            return jsonify({"error": "Ingen aktiv prenumeration hittades"}), 404

        success = delete_subscriber(subscriber.id)
        if not success:
            return jsonify({"error": "Kunde inte avsluta prenumerationen"}), 500

        return jsonify({"message": "Prenumeration avslutad", "reload": True}), 200
    except Exception as e:
        print(f"Fel i unsubscribe: {str(e)}")
        return jsonify({"error": f"Serverfel: {str(e)}"}), 500

# =====================================================================================================
# Logga ut
# =====================================================================================================
@user_routes.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('serve_index'))

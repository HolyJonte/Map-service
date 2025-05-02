# Denna klass representerar en användare i systemet.
# Används för inloggning, 2FA-verifiering och hantering av kopplad prenumerationsdata.

class User:
    def __init__(self, id, email, password, totp_secret, is_admin=False):
        self.id = id
        self.email = email
        self.password = password
        self.totp_secret = totp_secret
        self.is_admin = bool(is_admin)

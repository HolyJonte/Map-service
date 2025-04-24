# Denna klass representerar en användare i systemet.
# Används för inloggning, 2FA-verifiering och hantering av kopplad prenumerationsdata.

class User:
    def __init__(self, id, email, password, totp_secret):
        self.id = id
        self.email = email
        self.password = password
        self.totp_secret = totp_secret

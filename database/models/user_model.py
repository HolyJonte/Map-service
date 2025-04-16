class User:
    def __init__(self, id, email, password, totp_secret):
        self.id = id
        self.email = email
        self.password = password
        self.totp_secret = totp_secret

# Denna klass representerar en aktiv (eller tidigare) prenumerant i systemet.
# Används för att hantera information om prenumerationer.

class Subscriber:
    def __init__(self, id, user_id, phone_number, email, county, newspaper_id, active, subscription_start, last_payment, klarna_token):
        self.id = id
        self.user_id = user_id
        self.phone_number = phone_number
        self.email = email
        self.county = county
        self.newspaper_id = newspaper_id
        self.active = active
        self.subscription_start = subscription_start
        self.last_payment = last_payment
        self.klarna_token = klarna_token

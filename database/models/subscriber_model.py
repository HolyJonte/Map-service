class Subscriber:
    def __init__(self, id, phone_number, county, active, subscription_start, last_payment, klarna_token):
        self.id = id
        self.phone_number = phone_number
        self.county = county
        self.active = active
        self.subscription_start = subscription_start
        self.last_payment = last_payment
        self.klarna_token = klarna_token

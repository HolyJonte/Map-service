# database/models/sms_model.py

class Subscriber:
    def __init__(self, id, user_id, phone_number, county, newspaper_id, active, subscription_start, last_payment, klarna_token):
        self.id = id
        self.user_id = user_id
        self.phone_number = phone_number
        self.county = county
        self.newspaper_id = newspaper_id
        self.active = active
        self.subscription_start = subscription_start
        self.last_payment = last_payment
        self.klarna_token = klarna_token

    @classmethod
    def from_row(cls, row):
        return cls(
            id=row["id"],
            user_id=row["user_id"],
            phone_number=row["phone_number"],
            county=row["county"],
            newspaper_id=row["newspaper_id"],
            active=row["active"],
            subscription_start=row["subscription_start"],
            last_payment=row["last_payment"],
            klarna_token=row["klarna_token"]
        )


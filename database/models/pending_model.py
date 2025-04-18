class PendingSubscriber:
    def __init__(self, session_id, phone_number, county, newspaper_id, created_at):
        self.session_id = session_id
        self.phone_number = phone_number
        self.county = county
        self.newspaper_id = newspaper_id
        self.created_at = created_at

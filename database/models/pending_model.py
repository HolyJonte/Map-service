# Denna klass representerar en väntande prenumerant.
# Objektet används innan prenumerationen har bekräftats.

class PendingSubscriber:
    def __init__(self, session_id, user_id, phone_number, county, newspaper_id, created_at):
        self.session_id = session_id
        self.user_id = user_id
        self.phone_number = phone_number
        self.county = county
        self.newspaper_id = newspaper_id
        self.created_at = created_at

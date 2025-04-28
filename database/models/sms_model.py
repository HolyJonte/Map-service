# database/models/sms_model.py

class SMSLog:
    def __init__(self, id, newspaper_id, subscriber_id, recipient, message, sent_at):
        self.id = id
        self.newspaper_id = newspaper_id
        self.subscriber_id = subscriber_id
        self.recipient = recipient
        self.message = message
        self.sent_at = sent_at

    @classmethod
    def from_row(cls, row):
        return cls(
            id=row["id"],
            newspaper_id=row["newspaper_id"],
            subscriber_id=row["subscriber_id"],
            recipient=row["recipient"],
            message=row["message"],
            sent_at=row["sent_at"]
        )

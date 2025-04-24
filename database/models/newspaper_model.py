# Denna klass representerar en tidning i systemet.
# Objekt av denna klass används för att hantera och skicka
# information om tidningar från databasen till applikationen.
class Newspaper:
    def __init__(self, id, name, contact_email, sms_quota):
        self.id = id
        self.name = name
        self.contact_email = contact_email
        self.sms_quota = sms_quota

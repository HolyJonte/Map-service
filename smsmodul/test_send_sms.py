from database.crud.sms_crud import log_sms
from send_sms import send_sms

# OBS! Justera dessa ID:n till riktiga värden i databasen
newspaper_id = 1
subscriber_id = 1
to = "+46701234567"  # Telefonnummer till subscriber
message = "Testmeddelande från Trafikvida!"

success = send_sms(to, message, testMode=True)

if success:
    log_sms(newspaper_id, subscriber_id, to, message)
    print("✅ SMS skickat och loggat!")
else:
    print("❌ Misslyckades skicka SMS.")

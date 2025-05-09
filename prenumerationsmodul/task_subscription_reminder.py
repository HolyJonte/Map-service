# Denna modul kör tre olika funktioner:
# 1. Används för att påminna användare om att deras prenumerationer snart går ut (14 dagar).
# 2. Avaktiverar prenumerationer som inte har betalat på ett år.
# 3. Tar bort inaktiva prenumerationer som inte betalat på två år.
# Dessa körs i bakgrunden på PythonAnywhere, automatiskt en gång per dag.

import sys
import os
sys.path.append("/home/MaMaJoViDa/Map-service")
os.chdir("/home/MaMaJoViDa/Map-service")


from prenumerationsmodul.notifications import check_expiring_subscriptions
from database.crud.subscriber_crud import (
    deactivate_expired_subscribers,
    remove_inactive_subscribers
    )

if __name__ == "__main__":
    check_expiring_subscriptions()
    deactivate_expired_subscribers()
    remove_inactive_subscribers()
    print("Checkat om prenumerationer, avaktiverat och tagit bort inaktiva prenumerationer.")


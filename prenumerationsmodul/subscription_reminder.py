# Denna modul används för att påminna användare om att deras prenumerationer snart går ut.
# Körs i bakgrunden på PythonAnywhere, automatiskt en gång per dag.

from notifications import check_expiring_subscriptions

if __name__ == "__main__":
    check_expiring_subscriptions()

# Denna modul innehåller logik för admin-funktioner i Trafikvida
# Den ansvarar för:
# - Hantering av tidningar via databasen (CRUD), (Hämta, lägga till och ta bort dagstidningar från adminpanelen)
# - Hantering av adminlösenord (uppdatera lösenord för adminanvändare)

# Importerar databasmoduler för CRUD-operationer
from database.crud.newspaper_crud import (
    get_all_newspapers as db_get_all_newspapers,
    add_newspaper as db_add_newspaper,
    delete_newspaper as db_delete_newspaper
)

# Importerar moduler för att generera hashade lösenord
from werkzeug.security import generate_password_hash
# Importerar databasmoduler för att hämta databasanslutning
from database.database import get_db_connection

# Definierar en funktion för att byta lösenord och sparar det i databasen
def update_admin_password(new_password):
    hashed_password = generate_password_hash(new_password, method='scrypt')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET password = ? WHERE is_admin = 1",
        (hashed_password,)
    )
    conn.commit()
    conn.close()


# =========================================================================
# Tidningshantering (via databas)
# =========================================================================
# Hämtar alla tidningar från databasen
def get_all_newspapers():
    return db_get_all_newspapers()

# Lägg till en tidning i databasen
def add_newspaper(name, contact_email=None, sms_quota=None):
    return db_add_newspaper(name, contact_email, sms_quota)

# Ta bort en tidning från databasen
def delete_newspaper(newspaper_id):
    return db_delete_newspaper(newspaper_id)



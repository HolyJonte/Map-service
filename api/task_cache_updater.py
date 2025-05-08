# Denna fil hanterar schemalagda uppgifter för att uppdatera cache-minnet.
from api.logic import update_cache

if __name__ == "__main__":
    update_cache()
    print("Cache uppdaterad genom schemalagd uppdatering.")

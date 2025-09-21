FLASK_HOST = "127.0.0.1"
FLASK_PORT = 5000
FLASK_BASE = f"http://{FLASK_HOST}:{FLASK_PORT}"
DB_PATH = "moviebooker.db"

SECRET_KEY = "supersecret"
DB_NAME = "moviebot.db"

USERS = {
    "admin": "admin123",
    "test": "1234"
}

# Selenium settings
# When running on Jenkins or headless server, set HEADLESS = True
HEADLESS = False

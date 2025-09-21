import sqlite3
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import DB_PATH, FLASK_BASE, HEADLESS


DB = DB_PATH


def get_pending_requests():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    rows = c.execute("SELECT * FROM requests WHERE status = 'PENDING' ORDER BY created_at").fetchall()
    conn.close()
    print(f"Found {len(rows)} pending requests.")
    return rows


def mark_request_processed(request_id, status):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("UPDATE requests SET status = ?, processed_at = CURRENT_TIMESTAMP WHERE id = ?",
              (status, request_id))
    conn.commit()
    conn.close()


def log_booking(request_id, username, movie, showtime, status):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO bookings (request_id, username, movie, showtime, status) VALUES (?, ?, ?, ?, ?)",
              (request_id, username, movie, showtime, status))
    conn.commit()
    conn.close()


def setup_driver():
    options = Options()
    if HEADLESS:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    if not HEADLESS:
        options.add_argument("--start-maximized")

    service = Service(r"C:\Windows\chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def process_request(req, driver):
    req_id = req["id"]
    username = req["username"]
    movie = req["movie"]
    showtime = req["showtime"]

    try:
        print(f"Processing Request ID: {req_id} for user: {username}, movie: {movie}, showtime: {showtime}")

        # Visit homepage to check server availability
        driver.get(FLASK_BASE + "/")
        time.sleep(0.5)

        # Go to login page
        driver.get(FLASK_BASE + "/login")

        # Explicit wait for username field presence
        wait = WebDriverWait(driver, 10)
        username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))

        # Enter username and submit login
        username_field.clear()
        username_field.send_keys(username)
        driver.find_element(By.CSS_SELECTOR, "button").click()
        time.sleep(0.5)

        # Navigate to movie page (escape spaces)
        movie_escaped = movie.replace(" ", "%20")
        driver.get(FLASK_BASE + f"/movie/{movie_escaped}")
        time.sleep(0.5)

        # Select appropriate showtime
        select = driver.find_element(By.NAME, "showtime")
        for option in select.find_elements(By.TAG_NAME, "option"):
            if option.text.strip() == showtime.strip():
                option.click()
                break

        # Submit booking form
        driver.find_element(By.CSS_SELECTOR, "button").click()
        time.sleep(0.5)

        # Mark as booked in DB
        mark_request_processed(req_id, "BOOKED")
        log_booking(req_id, username, movie, showtime, "BOOKED")
        print(f"[OK] Successfully booked request {req_id} by {username} movie '{movie}' at {showtime}")
        return True

    except Exception as e:
        print(f"[ERR] Failed to process request {req_id}: {e}")
        try:
            mark_request_processed(req_id, "FAILED")
            log_booking(req_id, username, movie, showtime, "FAILED")
        except:
            pass
        return False


def main():
    print("Worker started, scanning pending requests...")
    rows = get_pending_requests()
    if not rows:
        print("No pending requests found. Exiting.")
        return

    driver = setup_driver()
    try:
        for r in rows:
            process_request(r, driver)
    finally:
        driver.quit()
        print("Worker finished.")


if __name__ == "__main__":
    main()

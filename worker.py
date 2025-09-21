import sqlite3
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from config import DB_PATH, FLASK_BASE, HEADLESS

DB = DB_PATH

def get_pending_requests():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    rows = c.execute("SELECT * FROM requests WHERE status = 'PENDING' ORDER BY created_at").fetchall()
    conn.close()
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
    # create driver via webdriver-manager
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def process_request(req, driver):
    req_id = req["id"]
    username = req["username"]
    movie = req["movie"]
    showtime = req["showtime"]

    try:
        # 1) Visit index to ensure site up
        driver.get(FLASK_BASE + "/")
        time.sleep(3)

        # 2) Login page — simple flow: go to /login, enter username, submit
        driver.get(FLASK_BASE + "/login")
        username_field = driver.find_element(By.NAME, "username")
        username_field.clear()
        username_field.send_keys(username)
        driver.find_element(By.CSS_SELECTOR, "button").click()
        time.sleep(3)

        # 3) Navigate to movie page
        driver.get(FLASK_BASE + f"/movie/{movie}")
        time.sleep(3)

        # 4) select showtime and submit form (the site expects a POST)
        select = driver.find_element(By.NAME, "showtime")
        # choose option with matching text
        for option in select.find_elements(By.TAG_NAME, "option"):
            if option.text.strip() == showtime.strip():
                option.click()
                break

        # click the submit button
        driver.find_element(By.CSS_SELECTOR, "button").click()
        time.sleep(3)

        # success: update DB
        mark_request_processed(req_id, "BOOKED")
        log_booking(req_id, username, movie, showtime, "BOOKED")
        print(f"[OK] Request {req_id} by {username} booked {movie} {showtime}")
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
    print("Worker started, looking for pending requests...")
    rows = get_pending_requests()
    if not rows:
        print("No pending requests. Exiting.")
        return

    driver = setup_driver()
    try:
        for r in rows:
            process_request(r, driver)
    finally:
        driver.quit()
        print("Worker finished.")

if __name__ == "_main_":
    main()

import sqlite3
from config import DB_PATH

def generate_report():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Query to get summary of bookings grouped by username, movie, showtime, and status
    query = """
    SELECT username, movie, showtime, status, COUNT(*) as count
    FROM bookings
    GROUP BY username, movie, showtime, status
    ORDER BY username, movie, showtime
    """

    c.execute(query)
    rows = c.fetchall()
    conn.close()

    report_lines = []
    report_lines.append("Booking Report Summary")
    report_lines.append("="*50)
    report_lines.append(f"{'User':15} | {'Movie':15} | {'Showtime':10} | {'Status':10} | {'Count':5}")
    report_lines.append("-"*50)

    for row in rows:
        username, movie, showtime, status, count = row
        line = f"{username:15} | {movie:15} | {showtime:10} | {status:10} | {count:5}"
        report_lines.append(line)

    report = "\n".join(report_lines)
    print(report)

    # Optionally write to a file
    with open("booking_report.txt", "w") as file:
        file.write(report)

if __name__ == "__main__":
    generate_report()

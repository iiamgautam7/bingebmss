pipeline {
    agent any

    environment {
        PYTHON = 'C:\\Users\\DELL\\AppData\\Local\\Programs\\Python\\Python310\\python.exe'
        VENV   = "${WORKSPACE}\\venv"
        DB     = "${WORKSPACE}\\moviebooker.db"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup Python') {
            steps {
                bat """
                if not exist "%VENV%" (%PYTHON% -m venv "%VENV%")
                "%VENV%\\Scripts\\python.exe" -m pip install --upgrade pip
                "%VENV%\\Scripts\\python.exe" -m pip install flask flask_sqlalchemy
                """
            }
        }

        stage('Start Flask (background)') {
            steps {
                bat """
                start "" /B "%VENV%\\Scripts\\python.exe" app.py > flask.log 2>&1
                powershell -Command "Start-Sleep -Seconds 5"
                """
            }
        }

        stage('Run Worker') {
            steps {
                bat """
                if exist worker.py ("%VENV%\\Scripts\\python.exe" worker.py)
                """
            }
        }

        stage('Archive DB & Logs') {
            steps {
                archiveArtifacts artifacts: '*.db', fingerprint: true
                archiveArtifacts artifacts: '*.log', allowEmptyArchive: true
            }
        }
    }

    post {
        always {
            bat "taskkill /F /IM python.exe /T || exit 0"
        }

        success {
            script {
                // Extract latest bookings into an HTML table
                bat """
                "%VENV%\\Scripts\\python.exe" - <<EOF
import sqlite3, html

conn = sqlite3.connect(r'%DB%')
cursor = conn.cursor()
cursor.execute("SELECT id, username, movie, showtime, created_at FROM requests ORDER BY created_at DESC LIMIT 10")
rows = cursor.fetchall()

html_content = ["<h2>Latest Booking Details</h2>",
                "<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse;'>",
                "<tr><th>ID</th><th>User</th><th>Movie</th><th>Showtime</th><th>Created At</th></tr>"]

for row in rows:
    html_content.append("<tr>" + "".join(f"<td>{html.escape(str(col))}</td>" for col in row) + "</tr>")

html_content.append("</table>")
with open("booking_report.html", "w", encoding="utf-8") as f:
    f.write("".join(html_content))
conn.close()
EOF
                """

                def report = readFile('booking_report.html')

                emailext (
                    to: 'gauatambanoth@gmail.com',
                    subject: "✅ Movie Booker - Build SUCCESS",
                    body: """<p>Build completed successfully!</p>${report}""",
                    mimeType: 'text/html'
                )
            }
        }

        failure {
            emailext (
                to: 'gauatambanoth@gmail.com',
                subject: "❌ Movie Booker - Build FAILED",
                body: """<p>Build failed. Please check Jenkins logs.</p>""",
                mimeType: 'text/html'
            )
        }
    }
}

pipeline {
    agent any

    environment {
        PYTHON = 'C:\\Users\\DELL\\AppData\\Local\\Programs\\Python\\Python310\\python.exe'
        VENV   = "${WORKSPACE}\\venv"
        DB     = "${WORKSPACE}\\shopbot.db"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup Python & Venv') {
            steps {
                bat """
                if not exist "${VENV}" (${PYTHON} -m venv "${VENV}")
                "${VENV}\\Scripts\\python.exe" -m pip install --upgrade pip
                if exist requirements.txt (
                    "${VENV}\\Scripts\\python.exe" -m pip install -r requirements.txt
                ) else (
                    echo No requirements.txt found, installing basics...
                    "${VENV}\\Scripts\\python.exe" -m pip install flask flask_sqlalchemy
                )
                """
            }
        }

        stage('Init Database') {
            steps {
                bat """
                "${VENV}\\Scripts\\python.exe" db_init.py
                """
            }
        }

        stage('Start Flask (background)') {
            steps {
                bat """
                REM Run Flask app in background
                start "" /B "${VENV}\\Scripts\\python.exe" app.py > flask.log 2>&1

                REM Give Flask some time to boot
                powershell -Command "Start-Sleep -Seconds 5"

                REM Check if Flask responds
                powershell -Command ^
                \"$url='http://127.0.0.1:5000'; $t=0; while ($t -lt 30) { try { $r=Invoke-WebRequest -UseBasicParsing -Uri $url -TimeoutSec 3; if ($r.StatusCode -eq 200) { Write-Host 'Flask is UP'; exit 0 } } catch {}; Start-Sleep -Seconds 1; $t++ }; Write-Error 'Flask did not respond'; exit 1\"
                """
            }
        }

        stage('Run Worker') {
            steps {
                bat """
                "${VENV}\\Scripts\\python.exe" worker.py
                """
            }
        }

        stage('Archive DB') {
            steps {
                archiveArtifacts artifacts: 'shopbot.db', fingerprint: true
            }
        }
    }

    post {
        always {
            bat """
            REM Clean up: kill Python processes started by Jenkins (optional)
            taskkill /F /IM python.exe /T || exit 0
            """
            echo "🧹 Cleanup done"
        }
        success {
            script {
                // Generate HTML table of booking details
                bat """
                "${VENV}\\Scripts\\python.exe" - <<EOF
import sqlite3

conn = sqlite3.connect(r'${DB}')
cursor = conn.cursor()

# Change 'bookings' and columns according to your schema
cursor.execute("SELECT id, user, movie, seats, date FROM bookings LIMIT 10")
rows = cursor.fetchall()

html = ["<h3>Booking Details (Top 10)</h3>"]
html.append("<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse;'>")
html.append("<tr><th>ID</th><th>User</th><th>Movie</th><th>Seats</th><th>Date</th></tr>")
for row in rows:
    html.append("<tr>" + "".join([f"<td>{str(col)}</td>" for col in row]) + "</tr>")
html.append("</table>")

with open("booking_report.html", "w", encoding="utf-8") as f:
    f.write("".join(html))

conn.close()
EOF
                """
            }

            emailext (
                to: 'gauatambanoth@gmail.com',
                subject: "✅ Jenkins Build Successful - Booking Details",
                body: """<p>Hello,</p>
                         <p>The Jenkins pipeline has completed successfully.</p>
                         ${FILE,path="booking_report.html"}""",
                mimeType: 'text/html'
            )
        }
        failure {
            emailext (
                to: 'gauatambanoth@gmail.com',
                subject: "❌ Jenkins Build Failed",
                body: """<p>Hello,</p>
                         <p>The Jenkins pipeline has <b>FAILED</b>.</p>
                         <p>Please check Jenkins console logs for details.</p>""",
                mimeType: 'text/html'
            )
        }
    }
}

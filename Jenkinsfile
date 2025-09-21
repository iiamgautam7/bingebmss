pipeline {
    agent any

    environment {
        PYTHON = 'C:\\Users\\DELL\\AppData\\Local\\Programs\\Python\\Python310\\python.exe'
        VENV = "${WORKSPACE}\\venv"
        FLASK_HOST = '127.0.0.1'
        FLASK_PORT = '5000'
        FLASK_BASE_URL = "http://${FLASK_HOST}:${FLASK_PORT}"
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
                    if not exist "${VENV}" (
                        \"${PYTHON}\" -m venv \"${VENV}\"
                    )
                    \"${VENV}\\Scripts\\python.exe\" -m pip install --upgrade pip
                    \"${VENV}\\Scripts\\python.exe\" -m pip install -r requirements.txt
                """
            }
        }

        stage('Start Flask (background)') {
            steps {
                bat """
                    REM Start Flask in background using START (non-blocking)
                    start "" /B \"${VENV}\\Scripts\\python.exe\" app.py > flask.log 2>&1
                    powershell -Command "Start-Sleep -Seconds 3"
                    REM Wait until Flask site responds (timeout 30s)
                    powershell -Command ^
                    \"$url='http://${FLASK_HOST}:${FLASK_PORT}'; $t=0; while ($t -lt 30) { try { $r=Invoke-WebRequest -UseBasicParsing -Uri $url -TimeoutSec 3; if ($r.StatusCode -eq 200) { Write-Host 'Flask ready'; exit 0 } } catch {}; Start-Sleep -Seconds 1; $t++ }; Write-Error 'Flask did not respond'; exit 1\"
                """
            }
        }

        stage('Run Worker') {
            steps {
                bat """
                    \"${VENV}\\Scripts\\python.exe\" worker.py
                """
            }
        }

        stage('Archive DB and Logs') {
            steps {
                archiveArtifacts artifacts: 'moviebooker.db', fingerprint: true
                archiveArtifacts artifacts: '*.log', allowEmptyArchive: true
            }
        }
    }

    post {
        always {
            bat """
                REM Clean up: kill any python.exe processes started by Jenkins
                taskkill /F /IM python.exe /T || exit 0
            """
        }

        success {
            echo 'Pipeline completed successfully!'
            script {
                try {
                    def bookingLog = readFile('booking_results.log').trim()
                    def emailBody = """
                        <h2>🎉 Build Completed Successfully!</h2>
                        <h3>Booking Details:</h3>
                        <pre>${bookingLog}</pre>
                        <h3>Build Details:</h3>
                        <ul>
                            <li><strong>Project:</strong> ${JOB_NAME}</li>
                            <li><strong>Build Number:</strong> ${BUILD_NUMBER}</li>
                            <li><strong>Build URL:</strong> <a href="${BUILD_URL}">${BUILD_URL}</a></li>
                            <li><strong>Status:</strong> ${currentBuild.result ?: 'SUCCESS'}</li>
                        </ul>
                        <p><em>Automated message from Jenkins CI/CD Pipeline</em></p>
                    """
                    emailext (
                        subject: "✅ Movie Booker Build SUCCESS - Build #${BUILD_NUMBER}",
                        body: emailBody,
                        mimeType: 'text/html',
                        to: 'gautambanoth@gmail.com'
                    )
                } catch (Exception e) {
                    echo "Failed to send success email: ${e.getMessage()}"
                }
            }
        }

        failure {
            echo 'Pipeline failed. Check the logs above for details.'
            script {
                try {
                    emailext (
                        subject: "❌ Movie Booker Build FAILED - Build #${BUILD_NUMBER}",
                        body: """
                        <h2>🚨 Build Failed!</h2>
                        <h3>Build Details:</h3>
                        <ul>
                            <li><strong>Project:</strong> ${JOB_NAME}</li>
                            <li><strong>Build Number:</strong> ${BUILD_NUMBER}</li>
                            <li><strong>Build URL:</strong> <a href="${BUILD_URL}">${BUILD_URL}</a></li>
                            <li><strong>Console Log:</strong> <a href="${BUILD_URL}console">View Logs</a></li>
                            <li><strong>Status:</strong> ${currentBuild.result ?: 'FAILED'}</li>
                        </ul>
                        <h3>Error Details:</h3>
                        <p>Please check the build logs for detailed error information.</p>
                        <p><em>Automated message from Jenkins CI/CD Pipeline</em></p>
                        """,
                        mimeType: 'text/html',
                        to: 'gautambanoth@gmail.com'
                    )
                } catch (Exception e) {
                    echo "Failed to send failure email: ${e.getMessage()}"
                }
            }
        }
    }
}

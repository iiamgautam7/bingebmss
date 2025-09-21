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

        stage('Init DB') {
            steps {
                bat """
                    "${VENV}\\Scripts\\python.exe" db_init.py
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
        bat """
        "${VENV}\\Scripts\\python.exe" generate_report.py
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


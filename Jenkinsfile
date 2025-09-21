pipeline {
    agent any
    
    environment {
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
                bat '''
                    if not exist "venv" (
                        python -m venv venv
                    )
                    venv\\Scripts\\python.exe -m pip install --upgrade pip
                    venv\\Scripts\\python.exe -m pip install -r requirements.txt
                '''
            }
        }
        
        stage('Initialize Database') {
            steps {
                bat '''
                    venv\\Scripts\\python.exe db_init.py
                '''
            }
        }
        
        stage('Start Flask (background)') {
            steps {
                script {
                    bat '''
                        start /b venv\\Scripts\\python.exe app.py
                        ping 127.0.0.1 -n 6 > nul
                    '''
                }
            }
        }
        
        stage('Run Worker') {
            steps {
                bat '''
                    venv\\Scripts\\python.exe worker.py
                '''
            }
        }
        
        stage('Archive DB and Logs') {
            steps {
                archiveArtifacts artifacts: 'moviebooker.db', allowEmptyArchive: true
                archiveArtifacts artifacts: '*.log', allowEmptyArchive: true
            }
        }
    }
    
    post {
        always {
            bat '''
                taskkill /F /IM python.exe /T || exit 0
            '''
        }
        success {
            echo 'Pipeline completed successfully!'
            script {
                try {
                    emailext (
                        subject: "✅ Movie Booker Build SUCCESS - Build #${BUILD_NUMBER}",
                        body: """
                        <h2>🎉 Build Completed Successfully!</h2>
                        
                        <h3>Build Details:</h3>
                        <ul>
                            <li><strong>Project:</strong> ${JOB_NAME}</li>
                            <li><strong>Build Number:</strong> ${BUILD_NUMBER}</li>
                            <li><strong>Build URL:</strong> <a href="${BUILD_URL}">${BUILD_URL}</a></li>
                            <li><strong>Status:</strong> ${currentBuild.result ?: 'SUCCESS'}</li>
                        </ul>
                        
                        <h3>Changes:</h3>
                        <p>${env.GIT_COMMIT ? "Commit: ${env.GIT_COMMIT}" : "No commit info available"}</p>
                        
                        <h3>Stages Completed:</h3>
                        <p>✅ Python Setup<br>
                        ✅ Database Initialization<br>
                        ✅ Flask Server Started<br>
                        ✅ Worker Execution<br>
                        ✅ Artifact Archiving</p>
                        
                        <p>Database file has been archived and is available for download.</p>
                        
                        <p><em>Automated message from Jenkins CI/CD Pipeline</em></p>
                        """,
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

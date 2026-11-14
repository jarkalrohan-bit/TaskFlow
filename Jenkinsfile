pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }
    environment{
        IMAGE_TAG = "${BUILD_NUMBER}"
        BACKEND_IMAGE = "taskflow-backend"
        FRONTEND_IMAGE = "taskflow-frontend"
        SONAR_HOME = tool "SonarQube"
    }
    stages {
        stage('Checkout Source Code') {
            steps {
                git(
                    url: "https://github.com/jarkalrohan-bit/TaskFlow.git/",
                    branch: "main"
                )
            }
        }
        stage('Backend Tests') {
            steps {
                sh '''
                    cd backend
                    
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    
                    pytest test_app.py --cov=. --cov-report=xml
                    
                    # Rewrite the <source> element so SonarQube resolves paths correctly
                    sed -i 's|<source>/var/lib/jenkins/workspace/Demo-TaskFolw-App/backend</source>|<source>backend</source>|' coverage.xml
                    
                    # Move to project root
                    mv coverage.xml ../coverage.xml
                '''
            }
        }

        stage('Frontend Checks') {
            steps {
                dir('frontend') {
                    sh '''
                        npm ci
                        npm run lint
                        npm run build
                    '''
                }
            }
        }
        
        stage('SonarQube: Static Code Analysis') {
            steps {
                withSonarQubeEnv('SonarQube') {
                    sh '''
                        $SONAR_HOME/bin/sonar-scanner \
                            -Dsonar.projectKey=taskflow \
                            -Dsonar.projectName=TaskFlow \
                            -Dsonar.sources=backend,frontend \
                            -Dsonar.sourceEncoding=UTF-8 \
                            -Dsonar.exclusions=**/node_modules/**,**/.venv/**,**/__pycache__/**,**/dist/**,**/test_*.py,**/init_db.py,**/wait_for_db.py \
                            -Dsonar.python.version=3 \
                            -Dsonar.python.coverage.reportPaths=coverage.xml
                    '''
                }
            }
        }
        
        stage('SonarQube Quality Gate') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }
        
        stage('OWASP: Dependency Vulnerability Scan') {
            steps {
                dependencyCheck(
                    additionalArguments: '''
                        --scan ./
                        --format HTML
                        --format XML
                        --noupdate
                    ''',
                    odcInstallation: 'OWASP-Check'
                )
        
                dependencyCheckPublisher(
                    pattern: 'dependency-check-report.xml'
                )
            }
        }
        
        stage('Build Docker Image') {
            steps {
                sh "docker build -t ${BACKEND_IMAGE}:${env.BUILD_NUMBER} ./backend"
                sh "docker build -t ${FRONTEND_IMAGE}:${env.BUILD_NUMBER} ./frontend"
            }
        }
        
        stage('Trivy: Container Image Scan') {
            steps {
                sh '''
                    echo "========== Backend Image Scan =========="
        
                    trivy image \
                      --scanners vuln \
                      --severity HIGH,CRITICAL \
                      --ignore-unfixed \
                      --exit-code 1 \
                      ${BACKEND_IMAGE}:${BUILD_NUMBER}
        
                    echo "========== Frontend Image Scan =========="
        
                    trivy image \
                      --scanners vuln \
                      --severity HIGH,CRITICAL \
                      --ignore-unfixed \
                      --exit-code 1 \
                      ${FRONTEND_IMAGE}:${BUILD_NUMBER}
        
                    echo "========== Security Scan Completed =========="
                '''
            }
        }
        stage('Push Docker Image to Docker Hub'){
            steps{
                withCredentials([usernamePassword(
                    credentialsId: "dockerHubCreds",
                    passwordVariable: "dockerHubPass",
                    usernameVariable: "dockerHubUser"
                    )]){
                    // 
                sh """
                    printf '%s' "$dockerHubPass" |
                    docker login -u "$dockerHubUser" --password-stdin
                """
                // Push frontend and backend concurrently
            script{
                parallel(
                    "Push Frontend": {
                        sh """
                            docker image tag ${FRONTEND_IMAGE}:${env.BUILD_NUMBER} "\$dockerHubUser/${FRONTEND_IMAGE}:${env.BUILD_NUMBER}"
                            docker push "\$dockerHubUser/${FRONTEND_IMAGE}:${env.BUILD_NUMBER}"
                        """
                        },
                    "Push Backend": {
                        sh """
                            docker image tag ${BACKEND_IMAGE}:${env.BUILD_NUMBER} "\$dockerHubUser/${BACKEND_IMAGE}:${env.BUILD_NUMBER}"
                            docker push "\$dockerHubUser/${BACKEND_IMAGE}:${env.BUILD_NUMBER}"
                        """
                                }

                            )
                        }
                    }
                } 
        }
    }

        post {
            always {
                // 1. Email Notification (Runs on Success, Failure, or Unstable)
                script {
                    def color = (currentBuild.currentResult == 'SUCCESS') ? '#2ecc71' : (currentBuild.currentResult == 'UNSTABLE' ? '#f1c40f' : '#e74c3c')
                    def statusText = currentBuild.currentResult
                    def duration = "${currentBuild.durationString.replace(' and counting', '')}"
                    
                    emailext(
                        attachLog: (currentBuild.currentResult != 'SUCCESS'),
                        from: 'jarkalrohan@gmail.com',
                        to: 'jarkalrohan@gmail.com',
                        subject: "${statusText}: ${env.JOB_NAME} [Build #${env.BUILD_NUMBER}]",
                        mimeType: 'text/html',
                        body: """
                            <html>
                            <body style="font-family: Arial, sans-serif; color: #333;">
                                <div style="border-left: 6px solid ${color}; padding-left: 16px; margin-bottom: 20px;">
                                    <h2 style="color: ${color}; margin: 0;">Build ${statusText}</h2>
                                    <p style="margin: 4px 0;"><strong>Job:</strong> ${env.JOB_NAME}</p>
                                    <p style="margin: 4px 0;"><strong>Build Number:</strong> #${env.BUILD_NUMBER}</p>
                                    <p style="margin: 4px 0;"><strong>Duration:</strong> ${duration}</p>
                                </div>
                                <p><strong>Console Output:</strong><br/><a href="${env.BUILD_URL}console">${env.BUILD_URL}console</a></p>
                            </body>
                            </html>
                        """
                    )
                }
            }
            
            success {
                // 2. Trigger the CD Pipeline ONLY on Success
                archiveArtifacts artifacts: '*.xml', followSymlinks: false
                build job: "TaskFolw-CD", wait: false, parameters: [
                    string(name: 'IMAGE_TAG', value: "${env.BUILD_NUMBER}"),
                    string(name: 'DOCKERHUB_USER', value: 'rohanjarkal'),
                    string(name: 'BACKEND_IMAGE', value: 'taskflow-backend'),
                    string(name: 'FRONTEND_IMAGE', value: 'taskflow-frontend')
                ]
            }
        }
}
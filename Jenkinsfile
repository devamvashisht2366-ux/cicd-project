pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        // Replace with your Docker Hub username/repository.
        DOCKERHUB_REPO = 'YOUR_DOCKERHUB_USERNAME/virtual-mouse-keyboard'
        DOCKERHUB_CREDENTIALS = 'dockerhub-creds'
        K8S_NAMESPACE = 'default'
        DEPLOYMENT_NAME = 'virtual-mouse-keyboard'
        CONTAINER_NAME = 'virtual-mouse-keyboard'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    env.GIT_SHORT_SHA = sh(script: 'git rev-parse --short=7 HEAD', returnStdout: true).trim()
                    echo "Building source commit ${env.GIT_SHORT_SHA}"
                }
            }
        }

        stage('Build and Test') {
            steps {
                sh '''
                    python3 --version
                    python3 -m compileall -q app.py hand.py track.py tests
                    python3 -m venv .ci-venv
                    . .ci-venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pytest -v
                '''
            }
            post {
                always {
                    sh 'rm -rf .ci-venv || true'
                }
            }
        }

        stage('Docker Build') {
            steps {
                sh '''
                    docker build --pull -t ${DOCKERHUB_REPO}:${GIT_SHORT_SHA} -t ${DOCKERHUB_REPO}:latest .
                '''
            }
        }

        stage('Push Image') {
            steps {
                withCredentials([usernamePassword(credentialsId: "${DOCKERHUB_CREDENTIALS}", usernameVariable: 'DH_USER', passwordVariable: 'DH_TOKEN')]) {
                    sh '''
                        set +x
                        printf '%s' "$DH_TOKEN" | docker login --username "$DH_USER" --password-stdin
                        docker push ${DOCKERHUB_REPO}:${GIT_SHORT_SHA}
                        docker push ${DOCKERHUB_REPO}:latest
                        docker logout
                    '''
                }
            }
        }

        stage('Deploy to Minikube') {
            steps {
                sh '''
                    kubectl config current-context
                    kubectl get nodes
                    sed "s|DOCKERHUB_USERNAME/virtual-mouse-keyboard|${DOCKERHUB_REPO}|g" k8s/deployment.yaml | kubectl apply -f -
                    kubectl apply -f k8s/service.yaml
                    kubectl set image deployment/${DEPLOYMENT_NAME} ${CONTAINER_NAME}=${DOCKERHUB_REPO}:${GIT_SHORT_SHA}
                    kubectl rollout status deployment/${DEPLOYMENT_NAME} --timeout=180s
                '''
            }
        }

        stage('Verify Deployment') {
            steps {
                sh '''
                    kubectl get deployment ${DEPLOYMENT_NAME}
                    kubectl get pods -o wide
                    kubectl get service ${DEPLOYMENT_NAME}
                    POD=$(kubectl get pods -l app=${DEPLOYMENT_NAME} -o jsonpath='{.items[0].metadata.name}')
                    kubectl wait --for=condition=Ready pod/${POD} --timeout=120s
                    kubectl exec "$POD" -- python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:5000/health').read().decode())"
                '''
            }
        }
    }

    post {
        success {
            echo 'CI/CD pipeline succeeded: tested, built, pushed and deployed the application.'
        }
        failure {
            echo 'Pipeline failed. Review the first failed stage and Jenkins console output.'
        }
        always {
            sh 'docker image prune -f || true'
        }
    }
}

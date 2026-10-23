# Virtual Mouse and Keyboard — CI/CD deployment (CCA-2)

This repository packages the existing hand-gesture virtual mouse/keyboard academic project and provides a small HTTP status page so the deployment can be checked in a headless Kubernetes cluster.

> **Runtime limitation:** `hand.py` uses a physical webcam, OpenCV windows, and desktop-control libraries (`pyautogui`/`pynput`). A normal headless Minikube pod cannot control the host desktop or access its webcam automatically. The Kubernetes-deployed web page is a health/status companion for verifying the CI/CD deployment; run `python hand.py` on a desktop with a camera to use the original gesture-control interface. The original `hand.py` and `track.py` are retained in this repository.

## Repository contents

- `hand.py`, `track.py` — original project source
- `app.py` — small web status/health page used for Kubernetes verification
- `tests/` — unit tests for gesture math and web health route
- `Dockerfile` — container image for the deployable status app
- `Jenkinsfile` — declarative CI/CD pipeline
- `k8s/` — Kubernetes Deployment and Service manifests

## CI/CD flow

1. Jenkins checks out the GitHub repository.
2. Python syntax checks and automated tests run.
3. Docker image is built and tagged with the Git commit and `latest`.
4. Jenkins authenticates to Docker Hub using a Jenkins credential and pushes both tags.
5. Jenkins applies the Kubernetes manifests to Minikube and updates the deployment image.
6. Jenkins waits for rollout and checks pods, deployment, and service.

## One-time setup

### 1. GitHub

Create a GitHub repository, then from this folder run:

```bash
git init
git add .
git commit -m "Add virtual mouse project and CI/CD pipeline"
git branch -M main
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

### 2. Docker Hub

Create a public repository named `virtual-mouse-keyboard` on Docker Hub.

### 3. Jenkins credentials and job

Install Jenkins plugins: **Pipeline**, **Git**, and **Credentials Binding** (Docker Pipeline is optional because this Jenkinsfile uses the Docker CLI).

Add a Jenkins credential:
- Kind: **Username with password**
- ID: `dockerhub-creds`
- Username: your Docker Hub username
- Password: a Docker Hub access token (recommended, rather than account password)

Create a **Pipeline** job, configure **Pipeline script from SCM**, select Git, enter your repository URL and branch `*/main`, and select `Jenkinsfile` as the script path.

### 4. Jenkins execution host / AWS

The machine/EC2 instance running Jenkins needs Git, Docker Engine, Python 3, `kubectl`, and Minikube installed. Ensure the Jenkins service account can use Docker and can access the Minikube kubeconfig/context. Start Minikube under the same account/context Jenkins uses, for example:

```bash
minikube start --driver=docker
kubectl config current-context
kubectl get nodes
```

If Minikube is started as a different Linux user, Jenkins may not see its kubeconfig; configure a dedicated Jenkins-owned kubeconfig/context instead. Configure AWS security group inbound rules narrowly: allow SSH from your IP and Jenkins web access only from trusted IPs/VPN. Do not expose Docker or Kubernetes control ports publicly.

### 5. Update Jenkinsfile configuration

Set `DOCKERHUB_REPO` in the Jenkinsfile to `YOUR_DOCKERHUB_USERNAME/virtual-mouse-keyboard`. Keep the credential ID as `dockerhub-creds` unless you change it in both places.

### 6. Run and verify

Run **Build Now** in Jenkins. On success, verify from the same Kubernetes context Jenkins uses:

```bash
kubectl get deployments
kubectl get pods
kubectl get services
minikube service virtual-mouse-keyboard --url
```

Open the URL returned by the final command. The Service is NodePort-based; the exact URL depends on the Minikube driver/environment.

## Required second-run demonstration

After the first successful pipeline run, change a visible message in `app.py`, for example the page subtitle. Commit and push the change:

```bash
git add app.py
git commit -m "Update status page for second deployment"
git push
```

Run the Jenkins job again. Show the new commit in Jenkins, successful image push, rollout completion, and updated page in the browser. Capture screenshots of the Jenkins stages, Docker Hub image tags, `kubectl get pods/deployments/services`, and the updated page.

## Notes

- The pipeline's test stage uses `compileall` plus `pytest`; it does not pretend that a webcam/desktop integration test ran in Kubernetes.
- Image tags are the Git commit short SHA and `latest`.
- Never commit Docker Hub passwords/tokens or AWS secrets into GitHub.

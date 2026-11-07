# CI/CD Pipeline with GitHub Actions & Docker (No Cloud Needed)

This is my 2-week DevOps internship project based on **Project 4** of the Elevate Labs internship guidelines.

The goal of this project is to build an end-to-end CI/CD pipeline that tests a Python Flask API, packages it into a Docker container, and publishes the image to Docker Hub using GitHub Actions—without using any paid cloud services.

---

## Architecture Overview

```mermaid
flowchart LR
    Dev([Developer]) -->|git push| GH[GitHub Repository]
    GH -->|Trigger| GHA[GitHub Actions Runner]

    subgraph CI["Stage 1: Continuous Integration"]
        GHA --> Setup[Setup Python 3.12]
        Setup --> Install[Install Dependencies]
        Install --> Tests[Run Pytest Suite]
    end

    subgraph CD["Stage 2: Continuous Deployment"]
        Tests -->|Passed on main branch| Buildx[Setup Docker Buildx]
        Buildx --> Login[Docker Hub Login via Secrets]
        Login --> BuildPush[Build & Push Image]
    end

    BuildPush --> Hub[(Docker Hub Registry\nmythreyan26/devops-cicd-service)]
```

---

## Tools Used

- **Python 3.12 / Flask 3.1**: Simple, modular REST API.
- **Gunicorn 26.2**: Production WSGI HTTP server inside the container.
- **Pytest 9.1**: Automated unit tests, integration tests, and failure handling verification.
- **Docker**: Containerization using an official `python:3.12-slim` base image.
- **Docker Compose**: Local multi-container orchestration and port mapping.
- **GitHub Actions**: CI/CD pipeline automation for testing on pushes/pull requests and publishing on main pushes.
- **Docker Hub**: Container registry for hosting built images (`mythreyan26/devops-cicd-service`).

---

## Project Structure

```
DevOps-CICD-Project/
├── .github/
│   └── workflows/
│       └── ci-cd.yml          # GitHub Actions CI/CD workflow
├── app/
│   ├── static/
│   │   ├── css/dashboard.css  # Responsive dashboard styles (dark & light themes)
│   │   └── js/dashboard.js    # Health polling & interactive API calculation logic
│   ├── templates/
│   │   └── dashboard.html     # Web dashboard template
│   ├── __init__.py            # Flask application factory (create_app)
│   ├── config.py              # Environment configuration classes
│   ├── routes.py              # API routes, web dashboard & JSON error handlers
│   └── utils.py               # Timezone-aware UTC timestamping and math functions
├── screenshots/
│   ├── 01-service-dashboard.png            # Web dashboard & real-time monitoring
│   ├── 02-api-endpoints-testing.png        # CLI execution & API endpoint validation
│   └── 03-github-actions-cicd-pipeline.png # Passing GitHub Actions CI/CD workflows
├── tests/
│   ├── conftest.py            # Pytest test client fixtures
│   ├── test_api.py            # Math tests and deliberate failure-handling tests
│   ├── test_dashboard.py      # Automated tests for dashboard rendering
│   └── test_health.py         # Tests for /health and /api/v1/info
├── .dockerignore              # Excludes .venv, cache, and secrets from Docker builds
├── .gitignore                 # Excludes local environments and test artifacts from git
├── Dockerfile                 # Container build instructions (non-root user, curl health check)
├── docker-compose.yml         # Local container orchestration file
├── PROJECT_STANDARDS.md       # Permanent engineering principles and guidelines
├── pytest.ini                 # Pytest root path and test discovery configuration
├── requirements.txt           # Python dependencies
├── wsgi.py                    # Entrypoint for running the app
└── README.md                  # Project documentation and setup guide
```

---

## Local Setup & Testing

### 1. Prerequisites
- Python 3.12+ (compatible with Python 3.14)
- Git
- Docker Desktop (with Docker Compose)

### 2. Set Up Virtual Environment
```bash
# Clone the repository
git clone https://github.com/mythreyan26/devops-cicd-project.git
cd devops-cicd-project

# Create and activate virtual environment
python -m venv .venv

# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1

# On Linux/macOS:
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Test Suite
```bash
pytest -v
```
All 24 automated tests pass. The test suite covers positive calculation cases, invalid inputs, division by zero, booleans passed as numbers, unknown routes, and dashboard rendering.

### 5. Run the Flask App Locally
```bash
python wsgi.py
```
The application runs locally on `http://127.0.0.1:5000`.

---

## Running with Docker & Docker Compose

### 1. Build the Docker Image
```bash
docker compose build
```

### 2. Start the Container
```bash
docker compose up -d
```

### 3. Verify Container Health
```bash
docker compose ps
```
The container status will show `Up (healthy)` once the internal `/health` check succeeds.

### 4. View Container Logs
```bash
docker compose logs -f
```

### 5. Stop the Container
```bash
docker compose down
```

---

## Web Dashboard & API Endpoints

### 1. Interactive DevOps Dashboard (`GET /dashboard` or `GET /`)
Access the web dashboard in any browser at `http://localhost:5000/dashboard` or `http://localhost:5000`:
- **Real-time Health Monitoring:** Live status indicator, UTC timestamp, and measured round-trip latency polling every 30 seconds.
- **Runtime Environment Metadata:** Displays application name, version, Python runtime, and environment (`production` / `development`).
- **Interactive API Calculator:** Allows executing real calculations and testing error handling directly against `/api/v1/calculate` with formatted JSON inspection.
- **CI/CD Pipeline Tracker:** Visual representation of pipeline stages with links to GitHub repository, Actions workflows, and Docker Hub tags.
- **Theme Support:** Dark and light mode toggle with system preference detection and `localStorage` persistence.

---

### 2. Health Check (`GET /health`)
Used by Docker health checks and monitoring probes.
```bash
curl -i http://localhost:5000/health
```
**Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2026-11-01T13:26:58.501190+00:00"
}
```

### 3. Application Info (`GET /api/v1/info`)
Returns application name, version, Python runtime version, and environment.
```bash
curl -i http://localhost:5000/api/v1/info
```
**Response (200 OK):**
```json
{
  "app_name": "DevOps-CICD-Service",
  "environment": "development",
  "python_version": "3.14.7",
  "timestamp": "2026-11-01T13:27:15.731266+00:00",
  "version": "1.0.0"
}
```

### 4. Arithmetic Calculator (`POST /api/v1/calculate`)
Supports `add`, `subtract`, `multiply`, and `divide`.
```bash
curl -i -X POST http://localhost:5000/api/v1/calculate \
  -H "Content-Type: application/json" \
  -d '{"operation": "multiply", "num1": 8, "num2": 9}'
```
**Response (200 OK):**
```json
{
  "operation": "multiply",
  "num1": 8.0,
  "num2": 9.0,
  "result": 72,
  "timestamp": "2026-11-01T13:26:15.784862+00:00"
}
```

### 5. Failure Handling Demo (Division by Zero)
```bash
curl -i -X POST http://localhost:5000/api/v1/calculate \
  -H "Content-Type: application/json" \
  -d '{"operation": "divide", "num1": 10, "num2": 0}'
```
**Response (400 Bad Request):**
```json
{
  "error": "Bad Request",
  "message": "Division by zero is not allowed.",
  "timestamp": "2026-11-01T13:26:22.645597+00:00"
}
```

---

## Screenshots / Project Output

The following screenshots capture genuine outputs and operational verification of the running application, API endpoints, and CI/CD pipeline:

### 1. Interactive DevOps Service Dashboard (`GET /dashboard`)
The responsive web interface running locally on `http://localhost:5000/dashboard`, demonstrating real-time health status polling, 19 ms round-trip latency, runtime environment metadata (`DevOps-CICD-Service v1.0.0`, `Python 3.14.7`), and the interactive API calculator.

![DevOps Service Dashboard](screenshots/01-service-dashboard.png)

---

### 2. REST API Endpoint Execution & Verification (CLI)
Automated and manual validation of API routes via PowerShell `Invoke-RestMethod` against `http://127.0.0.1:5000`, including arithmetic operations (`add`, `subtract`, `multiply`, `divide`), service health probe (`GET /health`), and runtime metadata inspection (`GET /api/v1/info`).

![REST API Endpoints Testing](screenshots/02-api-endpoints-testing.png)

---

### 3. GitHub Actions CI/CD Pipeline
Continuous Integration and Deployment workflow execution on GitHub Actions (`mythreyan26/devops-cicd-project`). Successful runs on the `main` branch verify the automated Pytest suite (24/24 passed), Docker build, and container publishing stages.

![GitHub Actions CI/CD Pipeline](screenshots/03-github-actions-cicd-pipeline.png)

---

## CI/CD Pipeline & GitHub Secrets

### GitHub Repository Secrets Needed
To allow GitHub Actions to push the built Docker image to Docker Hub, add these secrets under **Repository Settings > Secrets and variables > Actions**:

| Secret Name | Purpose | Example |
| :--- | :--- | :--- |
| `DOCKERHUB_USERNAME` | Docker Hub username | `mythreyan26` |
| `DOCKERHUB_TOKEN` | Docker Hub Personal Access Token (Read/Write) | `dckr_pat_...` |

> [!NOTE]
> Generate the access token in Docker Hub via **Account Settings > Security > Personal access tokens**. Never use your account password.

### Workflow Logic
- **Pull Requests to `main`**: Runs the `test` job only. If any test fails, the pull request check fails. Secrets are not exposed to PR runs.
- **Pushes to `main`**: Runs the `test` job first. If all tests pass, it proceeds to the `publish` job, logs into Docker Hub, builds the container, and tags it with `:latest` and `:${{ github.sha }}`.

---

## Security & Container Practices

1. **Non-Root User**: Inside the container, the application runs as `appuser` (UID 1000) instead of root to minimize host security risks.
2. **Lean Base Image**: Uses `python:3.12-slim` to reduce container footprint by omitting compiler toolchains and development packages not needed at runtime (verified at 226 MB uncompressed local disk usage, 54.8 MB compressed content size).
3. **No Hardcoded Secrets**: Docker Hub credentials are never stored in source code or committed configuration. They are configured as GitHub Actions repository secrets (`DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`) and supplied only at pipeline runtime.
4. **Sanitized Error Responses**: Application errors return clean JSON messages without leaking internal tracebacks.

---

## Current Verification Status

- **Local Tests**: Verified (24/24 tests passing locally via pytest).
- **Local Container**: Verified (Docker Compose runs container healthy on port 5000).
- **Remote GitHub Actions**: Verified (CI/CD pipeline passing on `main` branch).
- **Docker Hub Publish**: Verified (`mythreyan26/devops-cicd-service` image published).
- **Project Outputs**: Verified (Live dashboard, API validation, and workflow screenshots embedded).

# DevOps Report — Django Channels Chat

This document explains the DevOps choices made for packaging and CI/CD.

Technologies used
- Docker + Docker Compose (web, postgres, redis)
- Django 2.x + Channels (ASGI) with Daphne
- PostgreSQL (official image)
- Redis (for Channels pub/sub)
- GitHub Actions for CI/CD
- Docker Hub for container registry (push via secrets)

Pipeline design
- Stages implemented in GitHub Actions:
  1. Build & Install — set up Python and install requirements
  2. Lint & Security Scan — flake8 + bandit (non-blocking)
  3. Test — runs Django tests with Postgres & Redis services provided by Actions
  4. Docker Build / Push — builds the image and pushes to Docker Hub (main branch only)
  5. Deploy — placeholder to call Render/Railway or other provider; guarded by secrets

Secret management strategy
- Secrets are stored in GitHub repository secrets (DOCKERHUB_USERNAME, DOCKERHUB_TOKEN, RENDER_API_KEY). The pipeline references these secrets; they are not stored in the repo.

Testing process
- The `test` job starts postgres and redis as services; migrations are applied and Django's test suite is executed. Test job is required for docker build and push.

Lessons learned / Next steps
- Replace hard-coded defaults with secure secret injection in production.
- Add integration tests for WebSocket behavior (e.g., using channels testing utilities).
- Optionally add image scanning (Trivy) and security policies.

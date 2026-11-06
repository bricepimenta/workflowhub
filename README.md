# WorkFlowHub — SOFT806 assignment starter

## Scope
Django REST Framework + token-authenticated task CRUD, React/Vite client, two Docker images, GitHub Actions and CircleCI configurations. This is **source code**, not proof that any external pipeline has run.

## Local commands
1. Install Docker and start Docker Desktop/Engine.
2. From repository root run `docker compose up --build`.
3. Open http://localhost:8080 and register a user. Backend API is at http://localhost:8000/api/.
4. Run backend tests locally: `cd backend && pip install -r requirements.txt && python manage.py test tasks`.
5. Run frontend tests locally: `cd frontend && npm install && npm test`.
6. Build separately if needed: `docker build -t workflowhub-backend ./backend` and `docker build -t workflowhub-frontend ./frontend`.

## Automated testing
- **Backend (Django test runner, 18 tests):** registration, login, logout, token access, task CRUD, default and invalid status, and users only seeing their own tasks. Files: `backend/tasks/tests.py` and `backend/tasks/test_auth.py`.
- **Frontend (Vitest + React Testing Library, 11 tests):** navbar states, the New task Status dropdown (defaults to Pending), login/logout, and task list/status updates. The API is faked, so no server is needed. File: `frontend/src/App.test.jsx`.
- **Automatic runs:** GitHub Actions (`.github/workflows/ci.yml`) and CircleCI (`.circleci/config.yml`) run both test suites on every push and pull request, alongside the Docker image builds.

## GitHub / CircleCI
Create a GitHub repository and push this code as **incremental, honest commits**. Enable Actions. Link that repository in CircleCI to run `.circleci/config.yml`. Set required branch protections and open feature branches/pull requests; seek genuine review from an authorized classmate. Create a GitHub Project board with Backlog / To Do / In Progress / In Review / Done. Track real issue movement. CircleCI `setup_remote_docker` is needed to build Docker images from its Docker executor.

## Known limitations / next improvements
This is a coursework-scale starter, not a production deployment. Token stored in sessionStorage is vulnerable to XSS; production should use a stronger session/auth pattern. SQLite is suited for local demonstration, not clustered SaaS deployment. Pin dependencies and GitHub Actions by immutable digest for production; introduce linting, scans, tests, PostgreSQL, HTTPS, CSRF/CORS review, protected environments and deployment approvals. Frontend environment variables are compiled into build artifacts, so never put secrets into `VITE_` values. The frontend Docker build uses npm install because no lockfile has been generated; run `npm install` and commit `package-lock.json` then migrate to `npm ci` for reproducibility.

## Recent Updates
- Added task validation to prevent empty or whitespace-only titles
- Improved data integrity with model-level validation

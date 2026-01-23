# HealthCheck-Task

React + FastAPI + Postgres based web application with Docker Compose orchestration 


## Architecture

```
┌─────────────────┐    HTTP    ┌─────────────────┐    SQL     ┌──────────────┐
│   Frontend      │◄──────────►│   Backend       │◄──────────►│  Postgres    │
│   React App     │  /health   │   FastAPI       │            │ status_logs  │
│                 │  /status   │   APIs          │            │   table      │
│  Health Status  │            │                 │            │              │
│  + Logs Table   │            │                 │            │              │
└─────────────────┘            └─────────────────┘            └──────────────┘
        │                               │
        └───────────────────────────────┤
                                        │
                           ┌──────────────────┐
                           │  docker-compose  │
                           │  3 Containers    │
                           └──────────────────┘
```



**Components:**
- **Frontend**: React app showing backend health + status logs table
- **Backend**: FastAPI with `/health` and `/status` endpoints  
- **Database**: Postgres `status_logs` table
- **Orchestration**: Docker Compose (3 containers- frontend, backend, postgres)



## How to run locally

**Prerequisites:** Docker and Docker Compose

1. **Clone repository**
   ```bash
   git clone <repository-link>
   cd HealthCheck-Task

2. **Setup environment**
- Copy `.env.example` to `.env` in root, backend, and frontend folder
  ```
  #for copying .env of root
  cp .env.example .env

  #for copying .env of backend
  cd backend
  cp .env.example .env

  #for copying .env of frontend
  cd frontend
  cp .env.example .env

  ```
- Update credentials in it.

3. **Run Application**
- For running whole application, open command prompt(Terminal) for the folder in which `docker-compose.yaml` is present and then run the following commands,
   ```
   docker compose build
   docker compose up -d
   ```

4. **Access Application**
- Open `http://localhost:5173`

5. **Stop Containers**
  ```bash
  docker compose down
  ```

## Backend ↔ Database Contract
- This application uses PostgreSQL for storing connection logs.

**Database Table Creation**
-To ensure the database schema is created automatically, an `init` script is used:
  -File:[`backend/init.sql`](./backend/init.sql)

- Mounted in `docker-compose.yml` under `postgres` service:
  - ./backend/db/init.sql:/docker-entrypoint-initdb.d/init.sql

- When PostgreSQL starts for the first time, it executes init.sql and creates the `connection_logs` table.

**Backend ↔ DB Behavior on every call**
- POST /status
  - Inserts a new record into `connection_logs table`
  - Returns the latest `10(N) logs` from the database

- GET /health
  - Returns `200 OK` if DB is reachable
  - Returns `503 Service Unavailable` if DB is unreachable
  - This ensures that `/health` will fail gracefully if DB is unreachable

## Observability & Failure Simulation

**How To Observe**
- Run Backend and see `terminal` or `./logs/logs.txt` file to see the logs.
- Backend prints the structured logs for:
  - Backend Startup
  - Database Connection Status
  - Request lifecycle (request started → completed with status_code + duration(ms))

**Failure Simulation**
- Backend supports failure simulation using `environment flags` to test observability and error handling.
- Two flags are available in the `.env` file:
  1. `SIMULATE_DB_DOWN` → simulates database unavailability (`/health` returns `503`)
  2. `SIMULATE_CRASH` → simulates a backend crash
- To simulate failures, set either (or both) flags to `true` and `restart` the backend.

## CI/CD Pipeline
- Automated GitHub Actions for code quality and Docker image preparation whenever any changes are made into the `main` branch.

**Pipeline Flow**
  ```
  Push to main --→ Lint --→ Build --→ Docker Build and Image Tagging
  ```

**Pipeline Triggers**
- The Pipeline runs on:
  - `push` to `main` branch 
  - `pull_request` to the `main` branch

**Pipeline Stages**
- This workflow is designed to fail fast and stop execution if any stage fails.

1. **Lint**
- Runs backend linting using flake8
- Runs frontend linting using ESLint
- Ensures code quality and consistent formatting

2. **Build**
- Installs backend dependencies (Python)
- Installs frontend dependencies (Node.js)
- Builds the frontend application to ensure it compiles successfully

3. **Docker Image Build & Image tagging**
- Builds Docker images using docker compose build
- Tags images with:
  - `latest`
  - The current commit `SHA` (for traceability and rollback readiness)

**CI/CD failure paths**
- Our CI pipeline is strict and runs in a fixed order.
- Each step depends on the previous one, so if any step fails, the pipeline stops and fails immediately and the remaining steps are skipped.

### Pipeline Order
1. Lint
    - flake8
    - eslint
2. Build
    - frontend build runs only if lint passes
3. Docker Build and version strategy
    - Docker images build only if build passes

**Failure Behavior**
- If Lint fails → pipeline fails and Build + Docker Build will NOT run
- If Build fails → pipeline fails and Docker Build will NOT run
- If Docker Build fails → pipeline fails at image build stage

**Failure Handling**
- The pipeline fails cleanly with clear logs if:
  - dependency installation fails
  - build fails
  - lint checks fail
  - docker image build fails
  
 **Pipeline File Location:**
- [`.github/workflows/ci.yml`](./.github/workflows/ci.yml)



## Cloud Readiness (AWS EC2)

**AWS EC2 Instance Configs**
- EC2 Configuration for GPU-accelerated Docker workloads:
  - Target OS: Ubuntu `20.04` / `22.04`
  - Instance types: `g4dn.xlarge`, `g5.xlarge`, `p3/p4 series`

1. **EC2 Deployment Script**
- [`deployment_ready/aws-ec2.sh`](./deployment_ready/aws-ec2.sh)

2. **GPU Setup Script**
- [`deployment_ready/gpu-setup.sh`](./deployment_ready/gpu-setup.sh)

3. **NGINX Reverse Proxy**
- [`deployment_ready/nginx.config`](./deployment_ready/nginx.config)

## Zero-Downtime Restart Strategy
- There are healthchecks and restart policies included inside `docker-compose.yaml` to ensure safe restarts with minimal downtime.

  - Backend container has a healthcheck calling `/health`
  - Postgres container has a healthcheck using `pg_isready`
  - Backend starts only when Postgres becomes healthy
  - Frontend starts only when backend becomes healthy
  - All containers use `restart: always` for auto recovery
- We can also restart a single container with minimal downtime by,
  ```
  docker compose up -d --no-deps backend/frontend/postgres

  ```

## Rollback Strategy (Local Build)
- Here Docker image tagging is used for rollback.

### How rollback works
- Every build produces a Docker image which will be stored locally in Docker engine.
- Images can be tagged with:
  - `latest` (current version) & a unique version tag

### Steps for rollbacking previous image
  ```
  docker pull "image_name(backend/frontend)":"tag of previous image you want to rollback"
  docker compose down 
  docker compose up -d
  ``` 
  - Here, after pulling old version restart is important.


## Failure Handling

### Backend Crash
- `restart: always` restarts the backend automatically
- Healthcheck marks backend unhealthy if `/health` fails
- Frontend detects if backend is unhealthy or crashed and displays it.

### DB Not Reachable
- Backend depends on Postgres health.
- Backend returns error if DB connection fails
- Postgres healthcheck ensures DB readiness

### Port Conflicts

- It would happen if any port which the app needs is already in use by other services. For resolving it we can,
  - Stop the conflicting service OR change host port mapping in `docker-compose.yml`

### Health Check Strategy
Health is validated in 3 layers:
1. Backend `/health` endpoint
2. Docker healthcheck (backend + postgres)
3. Frontend pulling and displaying backend health status


## Screen Recording

- below is link of screen recording with local build, containers running and health-check working.
  - [Screen Recording](https://drive.google.com/file/d/1SRzQI1E2KtjmeoSooIKrCzTtbSu06n0F/view?usp=sharing)

  

## Allowed DevOps Touchpoints

### Docker
- Dockerfiles 
- Docker Compose
  - Service restart setups
  - Container dependencies

#### Reason:
Ensures controlled restarts without impacting frontend availability.

### Backend Container
- Structured logging for observability
- Health Checks of all endpoints

#### Reason:
Ensures reliable observability of application state and early detection of errors or faults.

### CI/CD Pipeline
- Job ordering
- Failure enforcement

#### Reason:
Ensures failures are detected early and prevents unstable builds from progressing to later stages.

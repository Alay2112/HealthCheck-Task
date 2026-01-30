# ROLLBACK-PLAYBOOK
This file describes the rollback procedure for the application in case of a failed deployment or unstable or unwanted behavior.

Rollback restores the previous known-good image without affecting the frontend UI.

## When To Rollback 

Perform rollback if:
- Backend fails to start after deployment
- DB connectivity errors persist after recovery
- Error rate increases after a new image released

## Preconditions
- Previous stable backend image tag is known
- Docker Compose is running on the host
- Frontend must remain running during rollback

## Rollback Procedure

1. Stop backend services
  ```
  docker compose down <service_name>
  ```

2. Pull previous stable image
  ```
  docker compose pull <service_name : prev_TAG>
  ```

3. Start services with previous image
  ```
  docker compose up -d
  ```

## Verification Steps
1. Check running containers
  ```
  docker compose ps
  ```

2. Verify backend health
  ```
  curl <service endpoint URL>
  ```

3. Confirm logs are clean
  ```
  docker compose logs <service_name> --tail=20
  ```

## Expected Outcome
- Backend starts successfully
- DB connectivity is restored from previous version
- UI remains up and accessible

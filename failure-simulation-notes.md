# Failure Simulation
This setup allows controlled failure simulations to observe and verify system behavior under fault conditions.

- Two controlled failure scenarios are configured:
  1. Backend Crash Simulation
  2. DB Failure Simulation

1. Backend Crash Simulation
### Action:
- Enable backend crash simulation (`SIMULATE_CRASH=true`)

### Observation:
- Backend exited intentionally with error logs
- UI remaines accessible

### Recovery:
- Disable simulation (`SIMULATE_CRASH=false`)
- Recreate backend container
- Backend will start normally

2. DB Failure Simulation
### Action:
- Enable DB failure simulation (`SIMULATE_DB_DOWN=true`)

### Observation:
- Backend returns 503 with clear error logs
- UI remaines accessible

### Recovery:
- Disable simulation (`SIMULATE_DB_DOWN=false`)
- Recreate backend container
- Backend will reconnect to DB successfully

## Outcome
System behaves predictably under failure and recovers safely without UI disruption.
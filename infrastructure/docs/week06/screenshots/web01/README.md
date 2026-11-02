# WEB01 - Week 6 Evidence

## Case 1 - Auto Remediation Success

- `01-web01-baseline-healthy.png`
- `02-web01-nginx-down-ssh-up.png`
- `03-web01-remediation-success.png`

Nginx was stopped while SSH remained available. The production remediation playbook successfully restarted Nginx and restored HTTP service.

## Case 2 - Execution Failed

- `04-web01-invalid-config.png`
- `05-web01-invalid-config-service-down.png`
- `06-web01-auto-execution-failed.png`
- `07-web01-retry-failed-manual-required.png`

An invalid Nginx configuration prevented the production remediation playbook from restarting Nginx.

The first execution failed and the retry also failed, resulting in manual intervention.

## Case 3 - Management Channel Blocked

- `08-web01-blocked-unreachable-warning.png`
- `09-web01-restored-after-blocked.png`

Nginx and SSH were stopped at the same time.

The server became unreachable through the management channel, so remediation was blocked and manual intervention was required.

## Case 4 - Verification Failed

- `10-web01-verification-failed-real.png`

Nginx configuration remained valid but was changed to listen on port 8081 instead of port 80.

The restart command succeeded, but the production playbook verification on port 80 failed.

Result:

```
Execution SUCCESS
Verification FAILED
Manual intervention required
```

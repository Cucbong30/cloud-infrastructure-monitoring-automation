# Week 9 Remediation Playbooks

This folder contains the remediation playbooks prepared for the Week 9 Approval and High-risk Action Control implementation.

## Playbooks

### restart-docker-service.yml

Target:

```text
APP01
```

Action:

```text
restart_docker_service
```

Risk:

```text
MEDIUM
```

Purpose:

Restart the Docker service on APP01 and verify that the Docker runtime, application container, and application service return to the expected operational state.

---

### reboot-azure01.yml

Target:

```text
AZURE01
```

Action:

```text
reboot_server
```

Risk:

```text
HIGH
```

Purpose:

Reboot the AZURE01 server and verify that the host, Nginx service, Node Exporter, HTTP service, and monitoring endpoint recover successfully after the reboot.

## Approval Mapping

```text
restart_docker_service
→ MEDIUM
→ Approval Required
```

```text
reboot_server
→ HIGH
→ Admin Approval Required
```

These playbooks are used as the real infrastructure actions for Week 9 approval workflow validation.

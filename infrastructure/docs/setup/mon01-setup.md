# MON01 Setup

## 1. Server Information
- Hostname: MON01
- OS: Ubuntu Server 24.04.3 LTS
- IP Address: 192.168.10.10
- Subnet: 192.168.10.0/24
- Default Gateway: 192.168.10.2
- Role: Monitoring / Automation / Operations Portal

## 2. Network Configuration
- Static IP configured successfully.
- Internet connectivity verified.
- Internal connectivity to WEB01, APP01 and WIN01 verified.

## 3. Remote Access
- OpenSSH Server installed and running.
- SSH connection to WEB01 verified.
- SSH connection to APP01 verified.
- SSH key authentication configured from MON01 to WEB01 and APP01.

## 4. Windows Remote Management Connectivity
- Connectivity from MON01 to WIN01 verified.
- WinRM port 5985 reachable from MON01.

## 5. Monitoring Connectivity
MON01 successfully accessed:
- WEB01 Node Exporter: `192.168.10.11:9100`
- APP01 Node Exporter: `192.168.10.12:9100`
- WIN01 Windows Exporter: `192.168.10.13:9182`

## 6. Verification Status
- Network: Success
- SSH: Success
- SSH Key Authentication: Success
- WinRM connectivity: Success
- Exporter connectivity: Success

## 7. Notes
Prometheus, Grafana, Alertmanager and Ansible will be deployed in the next phase.

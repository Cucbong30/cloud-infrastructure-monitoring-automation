# Bảng cấu hình máy chủ ảo

| Hostname | Vai trò | Hệ điều hành | vCPU | RAM | Disk |
|---|---|---|---:|---:|---:|
| MON01 | Monitoring & Automation Server | Ubuntu Server 24.04 LTS | 4 | 8 GB | 100 GB |
| WEB01 | Web Server | Ubuntu Server 24.04 LTS | 2 | 4 GB | 50 GB |
| APP01 | Application Server | Ubuntu Server 24.04 LTS | 2 | 4 GB | 50 GB |
| WIN01 | Windows Server | Windows Server 2022 | 2 | 4 GB | 60 GB |

## Vai trò dự kiến

### MON01
- Prometheus
- Grafana
- Alertmanager
- Ansible
- Flask Web Portal
- Tailscale

### WEB01
- Nginx
- Docker
- Node Exporter

### APP01
- Application / Database workload
- Docker
- Node Exporter

### WIN01
- Windows Service
- Windows Exporter
- WinRM / PowerShell Remoting

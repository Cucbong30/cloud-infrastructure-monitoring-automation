# Bảng cấu hình server ảo

| Hostname | Vai trò | Hệ điều hành | vCPU | RAM | Disk |
|---|---|---|---:|---:|---:|
| MGMT01 | Management / Remote Access Gateway | Ubuntu Server 24.04.3 LTS | 1–2 | 2 GB | 20–30 GB |
| MON01 | Monitoring & Automation Server | Ubuntu Server 24.04.3 LTS | 4 | 8 GB | 100 GB |
| WEB01 | Web Server | Ubuntu Server 24.04.3 LTS | 2 | 4 GB | 50 GB |
| APP01 | Application Server | Ubuntu Server 24.04.3 LTS | 2 | 4 GB | 50 GB |
| WIN01 | Windows Server | Windows Server 2022 | 2 | 4 GB | 60 GB |

## Vai trò dự kiến

### MGMT01
- Tailscale
- Tailscale Subnet Router
- Remote Access Gateway
- Kết nối từ xa vào mạng Lab `192.168.10.0/24`

### MON01
- Prometheus
- Grafana
- Alertmanager
- Ansible

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

## Ghi chú kiến trúc

- MGMT01 được bổ sung để tách chức năng remote access khỏi MON01.
- MGMT01 đóng vai trò Tailscale Subnet Router cho mạng Lab `192.168.10.0/24`.
- MON01 chỉ đảm nhiệm Monitoring và Automation.
- Flask Web Portal không còn chạy trên MON01.
- Trong giai đoạn phát triển và tích hợp, Flask Web Portal chạy độc lập trên máy của thành viên Application.
- Việc tách các thành phần giúp giảm phụ thuộc giữa Remote Access, Monitoring và Application khi xảy ra sự cố.

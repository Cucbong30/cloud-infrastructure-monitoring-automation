# APP01 Setup

## 1. Server Information
- Hostname: APP01
- OS: Ubuntu Server 24.04.3 LTS
- IP Address: 192.168.10.12
- Subnet: 192.168.10.0/24
- Default Gateway: 192.168.10.2
- Role: Application Workload / Container Host / Monitoring Target

## 2. Server Role and Function

APP01 được sử dụng làm máy chủ chạy workload ứng dụng trong môi hình thử nghiệm.

Chức năng chính:
- Chạy workload ứng dụng thông qua Docker container.
- Mô phỏng một application server độc lập với WEB01.
- Cung cấp metrics hệ thống thông qua Node Exporter.
- Là monitoring target của Prometheus.
- Được MON01 quản lý từ xa thông qua SSH.
- Được sử dụng cho các kịch bản kiểm thử về container và application availability.

Các kịch bản dự kiến:
- Container bị dừng.
- Application không phản hồi.
- Port dịch vụ không reachable.
- High CPU / memory usage.
- Server connectivity failure.

## 3. Network Configuration
- Static IP: `192.168.10.12`
- Network: `192.168.10.0/24`
- Gateway: `192.168.10.2`
- DNS:
  - `8.8.8.8`
  - `1.1.1.1`

Connectivity has been verified with:
- MON01
- WEB01
- WIN01
- Internet access

## 4. Remote Access

### SSH
OpenSSH Server has been installed and enabled.

Configuration:
- Service: `ssh`
- Port: `22`
- Status: Running

MON01 can connect to APP01 through SSH.

### SSH Key Authentication
SSH key authentication has been configured from MON01 to APP01.

This configuration allows:
- Passwordless administrative access from MON01.
- Future Ansible automation.
- Automated health checks.
- Remote execution of operational tasks.

## 5. Docker

Docker has been installed and enabled on APP01.

Main function:
- Provides container runtime for application workloads.
- Supports application deployment and recovery testing.
- Allows the system to demonstrate automation against container-based services.

Docker verification:
- Docker service is running.
- Docker image pulling is successful.
- `hello-world` container executed successfully.

## 6. Application Workload

A lightweight Nginx container has been deployed to simulate an application workload.

Container information:
- Container Name: `app01-web`
- Image: `nginx:alpine`
- Host Port: `8080`
- Container Port: `80`
- Restart Policy: `unless-stopped`

Service endpoint:

`http://192.168.10.12:8080`

Purpose:
- Provides a simple application endpoint for availability monitoring.
- Supports HTTP health-check scenarios.
- Can be intentionally stopped to simulate service failure.
- Can later be restarted automatically using Ansible.

Verification:
- Container is running.
- Local HTTP access is successful.
- MON01 can access the application endpoint successfully.

## 7. Node Exporter

Prometheus Node Exporter has been installed and configured as a systemd service.

Main function:
- Exposes Linux operating system metrics for monitoring.

Metrics include:
- CPU usage
- Memory usage
- Disk usage
- Filesystem information
- Network statistics
- System load
- Uptime

Configuration:
- Service: `node_exporter`
- Port: `9100`
- Metrics endpoint:

`http://192.168.10.12:9100/metrics`

Verification:
- Node Exporter service is running.
- Port `9100` is listening.
- MON01 successfully retrieved metrics from APP01.

## 8. Verification Status

- Static IP: Success
- Internet connectivity: Success
- Internal connectivity: Success
- SSH access from MON01: Success
- SSH key authentication: Success
- Docker service: Success
- Docker container test: Success
- Application container: Success
- HTTP access from MON01: Success
- Node Exporter: Success
- Metrics access from MON01: Success

## 9. Planned Usage

APP01 will be used in later phases for:
- Prometheus monitoring.
- Grafana visualization.
- Alertmanager alerting.
- Ansible automation.
- Container availability monitoring.
- Container restart automation.
- Application health checks.
- Auto-remediation demonstration.

One planned remediation scenario is:

`Container Down → Alert Detected → Ansible Restart → HTTP Health Check → Service Recovered`

# WEB01 Setup

## 1. Server Information
- Hostname: WEB01
- OS: Ubuntu Server 24.04.3 LTS
- IP Address: 192.168.10.11
- Subnet: 192.168.10.0/24
- Default Gateway: 192.168.10.2
- Role: Web Service / Container Workload / Monitoring Target

## 2. Server Role and Function

WEB01 được sử dụng làm máy chủ web trong mô hình thử nghiệm.

Chức năng chính:
- Cung cấp web service thông qua Nginx.
- Chạy Docker để mô phỏng workload dạng container.
- Cung cấp system metrics thông qua Node Exporter.
- Là một trong các monitoring target của hệ thống Prometheus.
- Được MON01 quản lý từ xa thông qua SSH.
- Được sử dụng cho các kịch bản kiểm thử như:
  - Nginx service down.
  - Docker service down.
  - High CPU / memory usage.
  - Server connectivity failure.

## 3. Network Configuration
- Static IP: `192.168.10.11`
- Network: `192.168.10.0/24`
- Gateway: `192.168.10.2`
- DNS:
  - `8.8.8.8`
  - `1.1.1.1`

Network connectivity has been verified with:
- MON01
- APP01
- WIN01
- Internet access

## 4. Remote Access

### SSH
OpenSSH Server has been installed and enabled.

SSH service status:
- Service: `ssh`
- Port: `22`
- Status: Running

MON01 can connect to WEB01 using SSH.

### SSH Key Authentication
SSH key authentication has been configured between MON01 and WEB01.

This allows MON01 to perform remote administration without entering the user password for every connection.

This configuration will later be used by Ansible for infrastructure automation.

## 5. Nginx Web Server

Nginx has been installed on WEB01.

Main function:
- Provides HTTP service for testing availability monitoring.
- Acts as a simple web workload for alert and remediation scenarios.

Service:
- Service Name: `nginx`
- Port: `80`
- Protocol: HTTP

Verification:
- Nginx service is running.
- Local HTTP access is successful.
- MON01 can access WEB01 through:
  `http://192.168.10.11`

## 6. Docker

Docker has been installed and enabled.

Main function:
- Provides container runtime for workload testing.
- Supports future automation and remediation scenarios.
- Allows deployment of lightweight test services without additional virtual machines.

Docker verification:
- Docker service is running.
- `hello-world` container executed successfully.
- Docker can pull images from Docker Hub.

## 7. Node Exporter

Prometheus Node Exporter has been installed and configured as a systemd service.

Main function:
- Exposes operating system and hardware metrics for monitoring.

Default metrics include:
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
  `http://192.168.10.11:9100/metrics`

Verification:
- Node Exporter service is running.
- Port 9100 is listening.
- MON01 successfully retrieved metrics from WEB01.

## 8. Verification Status

- Static IP: Success
- Internet connectivity: Success
- Internal connectivity: Success
- SSH access from MON01: Success
- SSH key authentication: Success
- Nginx service: Success
- HTTP access from MON01: Success
- Docker service: Success
- Docker container test: Success
- Node Exporter: Success
- Metrics access from MON01: Success

## 9. Planned Usage

WEB01 will be used in later phases for:
- Prometheus monitoring.
- Grafana visualization.
- Alertmanager alerts.
- Ansible automation.
- Nginx restart automation.
- Docker/container recovery scenarios.
- Availability and performance testing.

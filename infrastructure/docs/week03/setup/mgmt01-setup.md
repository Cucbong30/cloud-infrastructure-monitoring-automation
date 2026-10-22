# MGMT01 Setup

## Mục tiêu
Triển khai MGMT01 làm Management / Remote Access Gateway cho môi trường Lab.

## Cấu hình dự kiến
- Hostname: MGMT01
- OS: Ubuntu Server 24.04.3 LTS
- vCPU: 1–2
- RAM: 2 GB
- Disk: 20–30 GB
- IP: 192.168.10.5
- Subnet: 192.168.10.0/24
- Gateway: 192.168.10.2
- DNS: 8.8.8.8 / 1.1.1.1

## Vai trò
- Tailscale Client
- Tailscale Subnet Router
- Remote Access Gateway

## Trạng thái
- [ ] Tạo VM
- [ ] Cấu hình static IP
- [ ] Kiểm tra network
- [ ] Cài Tailscale
- [ ] Enable IP forwarding
- [ ] Advertise route 192.168.10.0/24
- [ ] Approve subnet route
- [ ] Kiểm tra remote access từ Application laptop

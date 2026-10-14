# Kế hoạch mạng và địa chỉ IP

## 1. Mạng nội bộ

- Subnet: `192.168.10.0/24`
- Gateway: `192.168.10.1`
- DNS dự kiến: `8.8.8.8` / `1.1.1.1`

## 2. Plan địa chỉ IP

| Hostname | Vai trò | IP Address |
|---|---|---|
| MON01 | Monitoring & Automation Server | 192.168.10.10 |
| WEB01 | Web Server | 192.168.10.11 |
| APP01 | Application Server | 192.168.10.12 |
| WIN01 | Windows Server | 192.168.10.13 |

## 3. Kết nối quản trị

### Linux
- Sử dụng SSH để quản trị WEB01 và APP01.
- MON01 đóng vai trò Ansible Controller.
- Dự kiến sử dụng SSH Key để giảm phụ thuộc vào password.

### Windows
- Sử dụng WinRM / PowerShell Remoting để quản trị WIN01.
- MON01 sẽ thực thi automation task tới WIN01 thông qua Ansible/WinRM.

## 4. Kết nối từ xa giữa hai thành viên

Tailscale được sử dụng để tạo overlay network phục vụ:
- Truy cập MON01 từ xa.
- Kiểm tra Web Portal.
- Phối hợp phát triển giữa thành viên System/Cloud và Application/Integration.

Các node dự kiến tham gia Tailscale:
- Laptop thành viên A.
- Laptop thành viên B.
- MON01.

## 5. Kết nối Cloud

Cloud VM sẽ được triển khai trên Azure hoặc nền tảng cloud tương đương khi có đủ tài nguyên.

Cloud VM dự kiến:
- Ubuntu Server.
- Cài Node Exporter.
- Có thể được giám sát bởi Prometheus.
- Có thể thực thi automation bằng Ansible.

# Plan mạng và địa chỉ IP

## 1. Mạng nội bộ

- Subnet: `192.168.10.0/24`
- VMware NAT Gateway: `192.168.10.2`
- DNS: `8.8.8.8` / `1.1.1.1`

## 2. Plan địa chỉ IP

| Hostname | Vai trò | IP Address |
|---|---|---|
| MGMT01 | Management / Remote Access Gateway | 192.168.10.5 |
| MON01 | Monitoring & Automation Server | 192.168.10.10 |
| WEB01 | Web Server | 192.168.10.11 |
| APP01 | Application Server | 192.168.10.12 |
| WIN01 | Windows Server | 192.168.10.13 |

## 3. Kết nối quản trị

### Linux
- Sử dụng SSH để quản trị MGMT01, WEB01 và APP01.
- MON01 đóng vai trò Ansible Controller.
- Sử dụng SSH Key để giảm phụ thuộc vào password.
- MON01 có thể thực thi automation task tới các Linux target thông qua SSH.

### Windows
- Sử dụng WinRM / PowerShell Remoting để quản trị WIN01.
- MON01 thực thi automation task tới WIN01 thông qua Ansible/WinRM.

## 4. Kết nối từ xa giữa hai thành viên

Tailscale được sử dụng để tạo overlay network phục vụ kết nối giữa môi trường Application và hạ tầng Lab.

### MGMT01
MGMT01 được bổ sung làm Tailscale Subnet Router và Remote Access Gateway.

MGMT01 quảng bá mạng nội bộ:

`192.168.10.0/24`

Thông qua MGMT01, thành viên Application có thể truy cập các máy chủ trong Lab mà không cần cài Tailscale trực tiếp trên từng VM.

### Các node tham gia Tailscale

- Laptop thành viên Infrastructure/System/Cloud.
- Laptop thành viên Application/Integration.
- MGMT01.

### Luồng truy cập từ xa

`Application Laptop → Tailscale → MGMT01 → 192.168.10.0/24`

Từ đó có thể truy cập:

- MON01 `192.168.10.10`
- WEB01 `192.168.10.11`
- APP01 `192.168.10.12`
- WIN01 `192.168.10.13`

Flask Web Portal chạy độc lập trên laptop của thành viên Application trong giai đoạn phát triển và tích hợp.

Portal có thể truy cập Prometheus API trên MON01 thông qua Tailscale Subnet Router.

Ví dụ:

`Application Portal → Tailscale → MGMT01 → MON01:9090`

Alertmanager trên MON01 cũng có thể gửi alert tới webhook của Flask Portal thông qua kết nối Tailscale.

## 5. Phân tách chức năng mạng

Kiến trúc được tinh chỉnh để tách Remote Access khỏi Monitoring Server.

### MGMT01
- Tailscale Subnet Router.
- Remote Access Gateway.
- Cung cấp đường truy cập vào mạng Lab.

### MON01
- Prometheus.
- Grafana.
- Alertmanager.
- Ansible Controller.
- Không còn đóng vai trò Tailscale Gateway.

Việc tách MGMT01 khỏi MON01 giúp duy trì khả năng truy cập từ xa vào Lab khi MON01 gặp sự cố.

Nếu MGMT01 gặp sự cố, Flask Portal trên laptop Application vẫn có thể hoạt động nhưng sẽ mất kết nối trực tiếp tới mạng Lab cho đến khi MGMT01 được khôi phục.

## 6. Kết nối Cloud

Cloud VM dự kiến được triển khai trên Azure hoặc nền tảng cloud tương đương khi có đủ tài nguyên.

Cloud VM dự kiến:
- Ubuntu Server.
- Cài Node Exporter.
- Có thể được giám sát bởi Prometheus.
- Có thể thực thi automation bằng Ansible.
- Có thể kết nối thông qua Tailscale hoặc mạng phù hợp với kiến trúc triển khai thực tế.

# Báo cáo tiến độ Tuần 2

## 1. Đỗ Đăng Thái Bảo – Infrastructure / System / Cloud

### Công việc được phân công
- Triển khai các máy chủ MON01, WEB01, APP01 và WIN01.
- Cấu hình địa chỉ IP tĩnh và kết nối mạng giữa các máy chủ.
- Cấu hình SSH và SSH Key Authentication giữa MON01 với WEB01 và APP01.
- Cấu hình WinRM trên WIN01 để phục vụ quản trị và automation từ xa.
- Cài đặt Nginx và Docker trên các Linux Server.
- Triển khai workload container trên APP01.
- Cài đặt Node Exporter trên WEB01 và APP01.
- Cài đặt Windows Exporter trên WIN01.
- Thực hiện kiểm tra kết nối và thu thập bằng chứng triển khai.

### Kết quả thực hiện
- Hoàn thành triển khai 4 máy chủ:
  - MON01: `192.168.10.10`
  - WEB01: `192.168.10.11`
  - APP01: `192.168.10.12`
  - WIN01: `192.168.10.13`
- Các máy chủ được cấu hình trong cùng mạng `192.168.10.0/24`.
- MON01 có thể kết nối SSH tới WEB01 và APP01.
- SSH Key Authentication đã được cấu hình để chuẩn bị cho Ansible automation.
- WIN01 đã được cấu hình WinRM trên port `5985` và MON01 có thể kiểm tra kết nối tới WinRM.
- Nginx trên WEB01 hoạt động và có thể truy cập từ MON01.
- Docker hoạt động trên WEB01 và APP01.
- APP01 đã triển khai container `app01-web` trên port `8080`.
- Node Exporter hoạt động trên WEB01 và APP01 thông qua port `9100`.
- Windows Exporter hoạt động trên WIN01 thông qua port `9182`.
- MON01 đã truy cập thành công metrics endpoint của các monitoring target.

### Kết quả trên GitHub

| Kết quả | Link |
|---|---|
| MON01 Setup |  |
| WEB01 Setup |  |
| APP01 Setup |  |
| WIN01 Setup |  |
| Minh chứng triển khai Tuần 2 |  |

**Trạng thái:** Hoàn thành nội dung Infrastructure / System của Tuần 2.

---

## 2. Nguyễn Thế Gia Bảo – Application / Integration

### Công việc được phân công
- Hoàn thiện Flask app cơ bản.
- Xây dựng Login/RBAC.
- Xây dựng Server Inventory.
- Xây dựng Dashboard.
- Xây dựng trang Alerts.
- Xây dựng Automation Jobs.

### Kết quả thực hiện
- Hoàn thiện Flask application cơ bản và lưu dữ liệu bằng SQLite.
- Hoàn thành Login/RBAC với các mức quyền Viewer, Operator và Administrator.
- Hoàn thành Server Inventory:
  - Xem danh sách server.
  - Xem chi tiết.
  - Thêm server.
  - Chỉnh sửa server.
  - Disable/Enable server.
- Hoàn thành Dashboard:
  - Hiển thị số lượng server.
  - Hiển thị số cảnh báo đang mở.
  - Hiển thị các automation job gần đây.
- Hoàn thành trang Alerts.
- Hoàn thành trang Automation Jobs.
- Automation Jobs hiện đang sử dụng cơ chế mô phỏng, chưa thực thi Ansible trên hạ tầng thật.

### Kết quả trên GitHub

| Kết quả | Link |
|---|---|
| Flask app và SQLite | (https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/tree/application/application) |
| Login / RBAC | (https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/application/application/app/blueprints/auth.py) |
| Server Inventory | (https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/application/application/app/blueprints/servers.py) |
| Dashboard | (https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/application/application/app/blueprints/dashboard.py) |
| Alerts | (https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/application/application/app/blueprints/alerts.py) |
| Automation Jobs | (https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/application/application/app/blueprints/automation.py) |

**Trạng thái:** Hoàn thành nội dung Application / Integration của Tuần 2.

---

## 3. Kết quả chung của nhóm

Trong Tuần 2, nhóm đã hoàn thành nền tảng ban đầu cho cả hai thành phần chính của hệ thống:

- Hạ tầng lab gồm Linux Server và Windows Server đã được triển khai.
- Kết nối quản trị từ MON01 tới các target server đã được thiết lập.
- Các monitoring exporter đã được cài đặt và kiểm tra.
- Web Portal đã có các module cơ bản gồm Login/RBAC, Server Inventory, Dashboard, Alerts và Automation Jobs.
- Hạ tầng và ứng dụng đã sẵn sàng để bắt đầu tích hợp với Prometheus và Ansible trong các tuần tiếp theo.

## 4. Kế hoạch Tuần 3

### Đỗ Đăng Thái Bảo – Infrastructure / System / Cloud
- Cài đặt Prometheus trên MON01.
- Cấu hình scrape Node Exporter và Windows Exporter.
- Cài đặt Grafana.
- Cài đặt Alertmanager.
- Xây dựng dashboard monitoring ban đầu.
- Thiết lập Tailscale phục vụ truy cập từ xa.

### Nguyễn Thế Gia Bảo – Application / Integration
- Chuẩn bị tích hợp Web Portal với Prometheus API.
- Xây dựng service layer lấy dữ liệu monitoring.
- Hiển thị trạng thái server và metrics trên Dashboard.
- Chuẩn bị cấu trúc tích hợp Ansible.
- Hoàn thiện xử lý lỗi và giao diện các module hiện tại.

# TUẦN 03 – Monitoring & Portal Integration

## 1. Mục tiêu trong tuần

Triển khai hệ thống monitoring tập trung trên môi trường lab đã xây dựng ở Tuần 2. Kết nối Operations Portal với Prometheus để hiển thị dữ liệu thực tế, đồng thời kiểm tra khả năng phát hiện lỗi máy chủ và dịch vụ.

## 2. Phân công công việc

### 2.1. Đỗ Đăng Thái Bảo – Infrastructure / System / Cloud

| STT | Công việc được phân công | Kết quả thực hiện |
|---|---|---|
| 1 | Triển khai MGMT01 và cấu hình Tailscale. | MGMT01 hoạt động như Subnet Router, cho phép máy chạy Application truy cập lab từ xa. |
| 2 | Cài đặt và cấu hình Prometheus trên MON01. | Thu thập được metrics từ MON01, WEB01, APP01 và WIN01. |
| 3 | Kiểm tra và chuẩn hóa Monitoring Exporter. | Node Exporter và Windows Exporter hoạt động, Prometheus thu thập được dữ liệu. |
| 4 | Triển khai Grafana. | Kết nối thành công với Prometheus và hiển thị các metrics của máy chủ. |
| 5 | Triển khai Alertmanager và Alert Rule. | Alertmanager nhận được cảnh báo từ Prometheus, kiểm thử thành công rule InstanceDown. |
| 6 | Chuẩn bị Prometheus API cho Application. | Portal có thể truy cập API và lấy dữ liệu monitoring thực tế. |
| 7 | Kiểm thử các trường hợp lỗi máy chủ và dịch vụ. | Kiểm tra lỗi Nginx, Docker Container, Grafana và WIN01. Phân biệt được service failure và host failure. |
| 8 | Cập nhật tài liệu triển khai. | Hoàn thành tài liệu cấu hình monitoring, remote access và kết quả kiểm thử. |

**Trạng thái: Hoàn thành.**

### 2.2. Nguyễn Thế Gia Bảo – Application / Integration

| STT | Công việc được phân công | Kết quả thực hiện |
|---|---|---|
| 1 | Tích hợp Prometheus API vào Portal. | Lấy được dữ liệu monitoring thực tế từ môi trường lab. |
| 2 | Xây dựng service layer xử lý metrics. | Thu thập và hiển thị CPU, RAM, Disk, Uptime và trạng thái exporter. |
| 3 | Ánh xạ dữ liệu monitoring với Server Inventory. | Liên kết đúng dữ liệu của MON01, WEB01, APP01 và WIN01. |
| 4 | Cập nhật Dashboard và giao diện Portal. | Hiển thị trạng thái Healthy, Degraded, Unreachable và tình trạng từng dịch vụ. |
| 5 | Tích hợp Alertmanager Webhook. | Tiếp nhận cảnh báo, chống trùng fingerprint và cập nhật trạng thái Firing/Resolved. |
| 6 | Xử lý trường hợp monitoring mất kết nối. | Portal hiển thị N/A hoặc Unavailable, các module khác vẫn hoạt động bình thường. |
| 7 | Chuẩn bị cấu trúc tích hợp Ansible. | Xây dựng adapter và action allow-list, tiếp tục sử dụng mock executor. |
| 8 | Kiểm thử Portal với môi trường lab. | Hiển thị đúng trạng thái trong các trường hợp Nginx, Container, Grafana và WIN01 gặp lỗi. |

**Trạng thái: Hoàn thành.**

## 3. Công việc phối hợp giữa hai thành viên

| Công việc | Infrastructure | Application |
|---|---|---|
| Kết nối môi trường lab | Cấu hình Tailscale và kiểm tra kết nối. | Kiểm tra khả năng truy cập lab từ máy chạy Portal. |
| Tích hợp Monitoring | Cung cấp Prometheus API và metrics endpoint. | Lấy dữ liệu và hiển thị trên Dashboard. |
| Tích hợp cảnh báo | Cấu hình Prometheus và Alertmanager. | Tiếp nhận và xử lý cảnh báo qua Webhook. |
| Kiểm thử sự cố | Tạo lỗi thực tế trên máy chủ và dịch vụ. | Kiểm tra trạng thái và cảnh báo hiển thị trên Portal. |

## 4. Kết quả cuối tuần

Hệ thống monitoring đã hoạt động với dữ liệu thực tế từ bốn máy chủ. Portal có thể hiển thị metrics, tiếp nhận cảnh báo và phân biệt lỗi dịch vụ với lỗi máy chủ.

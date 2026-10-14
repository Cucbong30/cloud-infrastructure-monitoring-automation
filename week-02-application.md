# Báo cáo tiến độ Tuần 2

## 1. Phân công công việc

| Thành viên | Vai trò | Công việc | Trạng thái |
|---|---|---|---|
| Nguyễn Thế Gia Bảo | Application / Integration | Hoàn thiện Flask app cơ bản; Login/RBAC; Server Inventory; Dashboard, Alerts và Automation Jobs | Hoàn thành |

## 2. Kết quả thực hiện

### Nguyễn Thế Gia Bảo
- Hoàn thiện Flask app cơ bản. Ứng dụng chạy được và lưu dữ liệu trong SQLite.
- Hoàn thành Login/RBAC. Người xem chỉ xem, người vận hành xác nhận cảnh báo và chạy job, quản trị quản lý máy chủ.
- Hoàn thành Server Inventory: xem danh sách, xem chi tiết, thêm, sửa, tắt và bật lại máy chủ.
- Hoàn thành Dashboard. Trang hiện số máy chủ, cảnh báo đang mở và job gần đây từ SQLite.
- Hoàn thành trang Alerts và trang Automation Jobs. Job chạy bằng bộ giả lập, chưa chạy Ansible trên máy thật.

## 3. Kết quả trên GitHub

### Nguyễn Thế Gia Bảo
- [Flask app và SQLite](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/tree/application/application)
- [Login/RBAC](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/application/application/app/blueprints/auth.py)
- [Server Inventory](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/application/application/app/blueprints/servers.py)
- [Dashboard](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/application/application/app/blueprints/dashboard.py)
- [Alerts](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/application/application/app/blueprints/alerts.py)
- [Automation Jobs](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/application/application/app/blueprints/automation.py)

## 4. Khai báo sử dụng AI

- Công cụ: Cursor
- Mục đích: Soạn báo cáo tuần 2 theo khung mục đã thống nhất.
- Nội dung đã được rà soát và chỉnh lại cho khớp với phần việc application đã làm.

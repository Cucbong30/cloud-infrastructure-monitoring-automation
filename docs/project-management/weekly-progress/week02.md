# TUẦN 02 – INFRASTRUCTURE SETUP & PORTAL FOUNDATION

## 1. Mục tiêu trong tuần

Sau khi thống nhất kiến trúc hệ thống, công nghệ sử dụng và cách phân chia công việc ở Tuần 1, nhóm bắt đầu triển khai môi trường lab và xây dựng Web Operations Portal.

Phần Infrastructure tập trung dựng các máy chủ, cấu hình mạng, triển khai dịch vụ và chuẩn bị môi trường monitoring. Phần Application xây dựng các chức năng nền tảng của Portal, trước mắt sử dụng dữ liệu demo để có thể phát triển song song mà không phải chờ hệ thống Infrastructure hoàn thành.

## 2. Đỗ Đặng Thái Bảo – Infrastructure / System / Cloud

### Công việc được phân công

- Triển khai bốn máy chủ MON01, WEB01, APP01 và WIN01 theo kiến trúc đã thiết kế ở Tuần 1.
- Cấu hình network, static IP và kiểm tra kết nối giữa các máy chủ.
- Thiết lập SSH và SSH Key Authentication cho Linux Server.
- Cấu hình WinRM và PowerShell Remoting cho Windows Server.
- Cài đặt Nginx, Docker và triển khai application workload để phục vụ các bài test sau này.
- Cài đặt Node Exporter và Windows Exporter, chuẩn bị cho việc thu thập metrics bằng Prometheus.
- Kiểm tra khả năng quản trị tập trung từ MON01.
- Ghi lại cấu hình, các bước triển khai và kết quả kiểm tra trên từng máy chủ.

### Kết quả thực hiện

| Hạng mục | Kết quả thực hiện | Trạng thái |
|---|---|---|
| MON01 | Triển khai Ubuntu Server 24.04.3 LTS, IP 192.168.10.10. Cài OpenSSH, tạo SSH Key để quản trị các Linux Server. Đây là máy chủ trung tâm phục vụ Monitoring và Automation. | Hoàn thành |
| WEB01 | Triển khai Ubuntu Server 24.04.3 LTS, IP 192.168.10.11. Cài Nginx, Docker và Node Exporter. Kiểm tra Docker bằng container hello-world. | Hoàn thành |
| APP01 | Triển khai Ubuntu Server 24.04.3 LTS, IP 192.168.10.12. Cài Docker, chạy container app01-web sử dụng nginx:alpine trên port 8080 và cài Node Exporter. | Hoàn thành |
| WIN01 | Triển khai Windows Server 2022, IP 192.168.10.13. Cấu hình WinRM qua port 5985 và cài Windows Exporter 0.31.9 trên port 9182. | Hoàn thành |
| Network | Cấu hình bốn máy chủ trong cùng mạng 192.168.10.0/24, sử dụng static IP để thuận tiện cho việc quản trị và tích hợp. | Hoàn thành |
| Remote Management | MON01 kết nối được WEB01 và APP01 qua SSH Key, đồng thời kiểm tra thành công kết nối WinRM tới WIN01. | Hoàn thành |
| Service Connectivity | Kiểm tra từ MON01 tới Nginx trên WEB01 và application container trên APP01. Các dịch vụ đều có thể truy cập. | Hoàn thành |
| Monitoring Exporter | Node Exporter trên Linux và Windows Exporter trên WIN01 đã hoạt động. MON01 có thể truy cập các metrics endpoint. | Hoàn thành |
| Documentation | Lưu tài liệu triển khai từng máy chủ, cấu hình mạng và hình ảnh kiểm tra kết nối, dịch vụ. | Hoàn thành |

Kết thúc Tuần 2, cả bốn máy chủ đã hoạt động trong cùng môi trường lab. MON01 có thể kết nối và quản trị các máy còn lại.

Các dịch vụ Nginx, Docker Container và Monitoring Exporter đã được chuẩn bị sẵn. Sang Tuần 3 có thể triển khai Prometheus, Grafana và Alertmanager trên nền hạ tầng này.

## 3. Nguyễn Thế Gia Bảo – Application / Integration

### Công việc được phân công

- Xây dựng Flask Web Operations Portal dựa trên thiết kế ở Tuần 1.
- Thiết lập cấu trúc project, database SQLite, migration và dữ liệu demo.
- Xây dựng chức năng đăng nhập và phân quyền Admin, Operator, Viewer.
- Xây dựng Server Inventory để quản lý danh sách máy chủ.
- Xây dựng Dashboard hiển thị trạng thái hệ thống, cảnh báo và các automation job.
- Xây dựng các module Alerts, Automation Jobs và Audit Log.
- Chuẩn bị cấu trúc tích hợp với Prometheus, Grafana và Ansible.
- Kiểm thử các chức năng cơ bản của Portal trước khi kết nối với môi trường lab thật.

### Kết quả thực hiện

| Hạng mục | Kết quả thực hiện | Trạng thái |
|---|---|---|
| Flask Application | Xây dựng Portal chạy trên Python 3.11 và Flask, sử dụng Bootstrap cho giao diện. Ứng dụng đã có thể chạy cục bộ. | Hoàn thành |
| Database | Sử dụng SQLite kết hợp Flask-SQLAlchemy để lưu dữ liệu và Flask-Migrate để quản lý thay đổi database schema. | Hoàn thành |
| Login | Xây dựng chức năng đăng nhập, quản lý session bằng Flask-Login và bảo vệ biểu mẫu bằng CSRF. | Hoàn thành |
| RBAC | Phân quyền ba vai trò. Viewer chỉ xem dữ liệu, Operator có thể acknowledge alert và chạy automation job, Admin có thêm quyền quản lý Server Inventory. | Hoàn thành |
| Server Inventory | Cho phép xem, tìm kiếm, lọc, thêm, sửa, kích hoạt và vô hiệu hóa máy chủ. Kiểm tra IP, hostname và monitoring target trước khi lưu. | Hoàn thành |
| Dashboard | Hiển thị tổng số server, trạng thái hệ thống, cảnh báo đang mở và các automation job gần nhất. Khi chưa kết nối được Prometheus, giao diện hiển thị N/A thay vì báo lỗi toàn bộ Portal. | Hoàn thành |
| Alerts | Hiển thị danh sách cảnh báo, lọc theo severity và status. Admin và Operator có thể acknowledge cảnh báo. | Hoàn thành |
| Automation Jobs | Xây dựng chức năng tạo và theo dõi job. Giới hạn action trong allow-list như restart_service, restart_container và disk_cleanup. Hiện tại sử dụng mock executor, chưa chạy trên máy chủ thật. | Hoàn thành |
| Audit Log | Ghi lại lịch sử đăng nhập, thay đổi Server Inventory, acknowledge alert và kết quả automation job. | Hoàn thành |
| Integration Adapter | Chuẩn bị cấu trúc tích hợp Prometheus, Grafana và Ansible để kết nối với Infrastructure ở các tuần tiếp theo. | Hoàn thành |
| Testing | Tạo dữ liệu demo và bổ sung pytest cho database, authentication, RBAC, giao diện, alert và automation. | Hoàn thành |

Kết thúc Tuần 2, Portal đã có các chức năng quản trị cơ bản và có thể chạy độc lập bằng dữ liệu demo.

Phần monitoring chưa sử dụng dữ liệu thật từ lab. Automation cũng chỉ chạy qua mock executor để kiểm tra luồng tạo job, phân quyền và ghi nhận kết quả, chưa thực hiện bất kỳ thay đổi nào trên máy chủ.

## 4. Công việc phối hợp giữa hai thành viên

| Nội dung | Infrastructure | Application |
|---|---|---|
| Server Inventory | Chuẩn bị danh sách máy chủ, IP, hệ điều hành và vai trò từng máy. | Xây dựng chức năng quản lý thông tin máy chủ trên Portal. |
| Monitoring | Triển khai Node Exporter, Windows Exporter và kiểm tra metrics endpoint. | Chuẩn bị cấu trúc lấy dữ liệu monitoring và hiển thị trên Dashboard. |
| Service Monitoring | Triển khai Nginx, Docker Container và các dịch vụ cần giám sát. | Chuẩn bị giao diện hiển thị trạng thái máy chủ và dịch vụ. |
| Automation | Thiết lập SSH, WinRM và môi trường quản trị từ MON01. | Xây dựng Automation Jobs, action allow-list và mock executor. |
| Integration | Chuẩn bị môi trường lab và các endpoint phục vụ tích hợp. | Chuẩn bị các adapter để kết nối với hệ thống Infrastructure. |

Hai thành viên triển khai song song theo phần việc đã phân công. Infrastructure chuẩn bị môi trường thật, Application xây dựng các chức năng cần thiết để khi hệ thống monitoring hoạt động thì có thể bắt đầu tích hợp ngay.

## 5. Tổng kết Tuần 2

**Trạng thái: Hoàn thành.**

Các công việc chính theo kế hoạch Tuần 2 đã được thực hiện:

- Hoàn thành triển khai bốn máy chủ trong môi trường lab.
- Thiết lập quản trị tập trung qua SSH và WinRM.
- Triển khai các dịch vụ và Monitoring Exporter.
- Xây dựng phiên bản đầu tiên của Web Operations Portal.
- Hoàn thành Login, RBAC, Server Inventory, Dashboard, Alerts, Automation Jobs và Audit Log.

Ở tuần này, Infrastructure và Application vẫn đang hoạt động tương đối độc lập. Đây là giai đoạn xây dựng nền tảng, chưa thực hiện tích hợp monitoring và automation end-to-end.

## 6. Kế hoạch Tuần 3 – Monitoring & Portal Integration

**Đỗ Đặng Thái Bảo – Infrastructure / System / Cloud**

- Cài đặt và cấu hình Prometheus trên MON01.
- Thu thập metrics từ các máy chủ trong lab.
- Triển khai Grafana và Alertmanager.
- Xây dựng các Alert Rule cơ bản.
- Thiết lập Tailscale để hỗ trợ truy cập lab từ xa.
- Chuẩn bị Prometheus API phục vụ tích hợp với Portal.

**Nguyễn Thế Gia Bảo – Application / Integration**

- Kết nối Portal với Prometheus API.
- Xây dựng service layer lấy dữ liệu monitoring.
- Thay dữ liệu demo trên Dashboard bằng metrics thực tế.
- Hiển thị trạng thái máy chủ và dịch vụ.
- Chuẩn bị tích hợp cảnh báo từ Alertmanager.
- Kiểm tra cách Portal xử lý khi monitoring backend mất kết nối.

Mục tiêu của Tuần 3 là kết nối hai phần Infrastructure và Application, đưa dữ liệu monitoring thực tế từ môi trường lab lên Web Operations Portal.

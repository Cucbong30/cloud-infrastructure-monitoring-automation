# Khai báo sử dụng AI - Tuần 2

## Công cụ sử dụng
- ChatGPT
- Model: GPT-5.5

## Mục đích sử dụng

AI được sử dụng chủ yếu để hỗ trợ tham khảo ý tưởng triển khai, cách tổ chức nội dung kỹ thuật và cách trình bày bằng chứng trên GitHub.

AI không thay thế phần triển khai hệ thống, cấu hình server hoặc kiểm tra kết quả thực tế.

## Nội dung sử dụng AI

### 1. Gợi ý cách tổ chức triển khai các server trong Tuần 2

Prompt:
`Gợi ý thứ tự triển khai MON01, WEB01, APP01 và WIN01 cho giai đoạn dựng môi trường lab.`

Nội dung AI hỗ trợ:
- Gợi ý thứ tự triển khai các server.
- Gợi ý cách phân chia vai trò giữa monitoring server và target server.
- Gợi ý các hạng mục nên hoàn thành trước khi sang giai đoạn monitoring.

Phần tự thực hiện:
- Tự tạo và cấu hình các máy ảo.
- Tự cấu hình network và static IP.
- Tự kiểm tra kết nối giữa các server.
- Tự điều chỉnh cấu hình theo môi trường VMware thực tế.

### 2. Gợi ý các thành phần cần triển khai cho monitoring target

Prompt:
`Gợi ý các thành phần cần cài trên Linux Server và Windows Server để chuẩn bị cho Prometheus monitoring.`

Nội dung AI hỗ trợ:
- Gợi ý sử dụng Node Exporter trên Linux.
- Gợi ý sử dụng Windows Exporter trên Windows Server.
- Gợi ý các endpoint và port cần kiểm tra trước khi cấu hình Prometheus.

Phần tự thực hiện:
- Tự cài đặt Node Exporter trên WEB01 và APP01.
- Tự cài đặt Windows Exporter trên WIN01.
- Tự kiểm tra service, port và metrics endpoint.
- Tự xác minh MON01 có thể truy cập metrics từ các target server.

### 3. Gợi ý cách tổ chức workload thử nghiệm

Prompt:
`Gợi ý một workload đơn giản trên WEB01 và APP01 để sau này có thể dùng cho monitoring và automation scenario.`

Nội dung AI hỗ trợ:
- Gợi ý sử dụng Nginx làm web service.
- Gợi ý sử dụng Docker container để tạo workload thử nghiệm.
- Gợi ý một số scenario như service down hoặc container down.

Phần tự thực hiện:
- Tự cài đặt Nginx trên WEB01.
- Tự cài đặt Docker trên WEB01 và APP01.
- Tự triển khai container app01-web.
- Tự kiểm tra HTTP endpoint từ MON01.

### 4. Gợi ý cách tổ chức tài liệu và bằng chứng GitHub

Prompt:
`Gợi ý cách tổ chức tài liệu setup và screenshot theo từng server và từng tuần để dễ truy vết kết quả triển khai.`

Nội dung AI hỗ trợ:
- Gợi ý tạo file setup riêng cho từng server.
- Gợi ý lưu screenshot theo thư mục tuần.
- Gợi ý đặt tên file theo server và nội dung kiểm tra.
- Gợi ý liên kết file setup, screenshot và commit trong báo cáo tuần.

Phần tự thực hiện:
- Tự tạo tài liệu cho MON01, WEB01, APP01 và WIN01.
- Tự lựa chọn ảnh minh chứng phù hợp.
- Tự upload file lên GitHub.
- Tự rà soát và liên kết các kết quả với báo cáo tuần.

## Ứng dụng AI cho phần Application / Integration

AI hỗ trợ gợi ý cách hoàn thiện Web Operations Portal bằng Flask, bao gồm:
- Cấu trúc blueprint.
- Service layer.
- Executor.
- SQLite model.
- Forms.
- Bootstrap templates.

AI hỗ trợ đề xuất luồng Login/Logout và phân quyền RBAC cho ba vai trò:
- Admin.
- Operator.
- Viewer.

Các gợi ý tập trung vào:
- Kiểm soát quyền quản lý server.
- Xác nhận cảnh báo.
- Chạy automation job.
- Hạn chế thao tác theo đúng vai trò người dùng.

AI hỗ trợ gợi ý các chức năng:
- Server Inventory.
- Dashboard.
- Alerts.
- Automation Jobs.
- Audit Log.

AI cũng đề xuất:
- Validation cho IP.
- Validation cho hostname.
- Validation cho monitoring target.
- Cách xử lý lỗi và thông báo trên giao diện.

AI hỗ trợ đề xuất cơ chế tích hợp Prometheus, Grafana và Ansible thông qua adapter/service layer.

Đối với automation, AI gợi ý:
- Sử dụng mock executor trong giai đoạn chưa kết nối hạ tầng thật.
- Sử dụng allow-list action để giới hạn các tác vụ được phép thực thi.
- Tách phần gọi automation khỏi route Flask để chuẩn bị tích hợp Ansible ở các tuần sau.

AI hỗ trợ tạo bản nháp cho:
- Test case pytest.
- Nội dung báo cáo tiến độ.
- Bảng link GitHub và commit.
- Chú thích ảnh minh chứng giao diện Login, Dashboard và Server Inventory.

Phần sinh viên tự thực hiện:
- Rà soát và điều chỉnh các đề xuất của AI.
- Tự tích hợp và chỉnh sửa mã nguồn.
- Tự chạy và kiểm tra ứng dụng.
- Tự chuẩn bị dữ liệu demo.
- Tự kiểm tra phân quyền và luồng nghiệp vụ.
- Tự chụp ảnh minh chứng giao diện.
- Tự lựa chọn và hoàn thiện nội dung cuối cùng.
- Chịu trách nhiệm về toàn bộ mã nguồn, kết quả kiểm thử và nội dung báo cáo.

## Ghi chú

AI được sử dụng ở mức tham khảo ý tưởng, cấu trúc và cách tổ chức công việc.

Toàn bộ thao tác triển khai server, cấu hình hệ thống, kiểm thử kết nối, kiểm tra service và xác minh kết quả đều được thực hiện trực tiếp trên môi trường lab bởi nhóm.

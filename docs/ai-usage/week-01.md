# Khai báo sử dụng AI - Tuần 1

## Công cụ sử dụng
- ChatGPT
- Model: GPT-5.5

## Mục đích sử dụng

AI được sử dụng để hỗ trợ ở mức gợi ý ý tưởng và tổ chức nội dung, không thay thế phần triển khai và quyết định kỹ thuật của nhóm.

Các nội dung sử dụng AI trong Tuần 1 gồm:


Prompt:
`hỗ trợ phân tích yêu cầu, đề xuất cấu trúc Flask, mô hình dữ liệu/ERD, wireframe, dịch vụ tích hợp Prometheus–Ansible, kiểm thử và biên soạn tài liệu kỹ thuật`

Nội dung AI xử lý:
AI hỗ trợ đề xuất cấu trúc dự án Flask theo các lớp blueprint, service, executor và template; gợi ý các module Login, Dashboard, Server Inventory, Alerts, Automation Jobs và Audit Log.

AI đề xuất mô hình dữ liệu SQLite gồm các bảng users, servers, alerts, automation_jobs và audit_logs; xác định các khóa chính, khóa ngoại và quan hệ giữa server, alert, job và người dùng.

AI hỗ trợ bản nháp xử lý xác thực, phân quyền theo admin/operator/viewer; validation cho IP, hostname, monitoring target; cơ chế ghi audit log và xử lý lỗi cơ bản.

AI gợi ý lớp tích hợp Prometheus để lấy metrics và đồng bộ cảnh báo; khung automation với Mock, Shell, PowerShell và Ansible executor, trong đó mock executor được dùng mặc định để bảo đảm an toàn.

AI hỗ trợ tạo bản nháp tài liệu Application Architecture, ERD, UI Wireframe, kế hoạch tích hợp Prometheus–Ansible và các test case pytest cho xác thực, schema, automation, Prometheus và các trang chính.

Phần nhóm tự thực hiện:
lựa chọn phạm vi chức năng, kiểm tra tính phù hợp với đề tài, tích hợp/chỉnh sửa mã nguồn và tài liệu, cấu hình môi trường, rà soát luồng nghiệp vụ, phân quyền và cơ chế automation an toàn.

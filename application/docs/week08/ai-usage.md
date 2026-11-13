# Khai báo sử dụng AI — Tuần 8 (Application)

## Công cụ sử dụng

Cursor (Grok), dùng khi viết code.

## Mục đích sử dụng

Nhờ cho Admin và Operator chạy Manual Remediation, chặn Viewer bằng giao diện và HTTP 403, ghi audit đủ actor, role, mode, target, action và result. Chặn job trùng. Gửi mail Execution Failed, Retry và Blocked. Bỏ SSH key của AZURE01 khỏi lệnh portal.

Commit code tuần 8: https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/4960f041ed12294b595016e993720ba209fd6bf8.

Commit tuần 7 còn dùng cho Entra và Graph: https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/c13696e4d637f098e2b3806b7f92937bf43ddf79.

## Nội dung AI hỗ trợ

AI gợi ý job MANUAL lưu email và role của người đăng nhập. Job AUTO giữ actor SYSTEM.

AI gợi ý lệnh trên MON01 là `ansible-playbook -i /etc/ansible/hosts`. Portal chỉ truyền key SSH tới MON01 khi file đó có trên máy portal. Key của AZURE01 ở lại inventory.

AI gợi ý duplicate trả DUPLICATE_SKIPPED và không gọi executor. Manual execution failed không tự tạo attempt 2. Kênh SSH down thì MANAGEMENT_BLOCKED trước playbook.

## Phần em tự làm

Em đăng nhập Admin, Operator và Viewer tối 13/11. Em sửa inventory trên MON01, chạy manual trên WEB01 và AZURE01, gây lỗi Nginx và tắt SSH, chụp 21 ảnh, và giữ job 60 đến job 78. Em chịu trách nhiệm về mã nguồn, kết quả test trên lab và nội dung báo cáo này. Private key không commit.

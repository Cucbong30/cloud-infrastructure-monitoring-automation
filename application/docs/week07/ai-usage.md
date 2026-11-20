# Khai báo sử dụng AI — Tuần 7 (Application)

## Công cụ sử dụng

Cursor (Grok), dùng khi viết code.

## Mục đích sử dụng

Nhờ gắn đăng nhập Microsoft Entra ID, lấy Admin, Operator và Viewer từ App Role trên token. Gửi mail cảnh báo bằng Microsoft Graph app-only tới ba distribution group. Thêm AZURE01 và giữ cooldown, retry, chặn duplicate, blocked và chạy tay của tuần 6. Đóng gói Docker, loại `.env` khỏi image.

Commit code tuần 7: https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/c13696e4d637f098e2b3806b7f92937bf43ddf79.

Commit policy tuần 6 còn dùng: https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/75601e49a81e8f4e8cf72a4e6df7ed878b5e3517.

## Nội dung AI hỗ trợ

AI gợi ý đọc role từ claim `roles`. Không có role thì user ở Viewer. Portal không có form gán role.

AI gợi ý gửi mail bằng `POST /users/{GRAPH_SENDER_MAILBOX}/sendMail`. Status 202 là accepted. Service Down, Execution Failed, Verification Failed và Manual Required đi nhóm Critical. Remediation Started, Retry và Blocked đi nhóm Warning. Remediation Success và Resolved đi nhóm Info.

AI gợi ý map Nginx trên AZURE01 vào `restart_nginx` và playbook `restart-azure-nginx.yml`, rồi dùng lại pre-check SSH, post-check cổng 80, cooldown 120 giây và retry một lần.

## Phần em tự làm

Em tạo App Registration, ba nhóm mail, và máy AZURE01. Em gây fault Nginx và SSH tối 5/11 và tối 6/11, chụp 27 ảnh, và giữ job 49 đến job 59. Em chịu trách nhiệm về mã nguồn, kết quả test trên lab và nội dung báo cáo này. Client secret chỉ nằm trong `.env` local.

# Khai báo sử dụng AI — Tuần 5 (Application)

## Công cụ sử dụng

Cursor (Grok), dùng khi viết code và khi sắp báo cáo này theo form tuần 4, từ ảnh lab em đã chụp.

## Mục đích sử dụng

Nhờ làm pre-check SSH cổng 22 cho WEB01 và APP01, WinRM cổng 5985 cho WIN01, chặn remediation khi kênh down, verification sau Ansible, Job Detail, liên kết Alert với Job, Retry bằng job mới, và audit `remediation.blocked`, `remediation.verified`, `remediation.failed`.

Commit code tuần 5: https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/a7a65e96e9265517fad7cac7c136f9e1f0825bf4. Commit này có trailer `Co-authored-by: Cursor <cursoragent@cursor.com>`.

## Nội dung AI hỗ trợ

AI gợi ý hỏi cổng management từ MON01 trước khi gọi playbook. Cổng down thì không tạo job, reason dạng `APP01 management channel SSH :22 is down`, và không đổi WEB01 hay APP01 thành Unreachable chỉ vì SSH down.

AI gợi ý Success chỉ khi post-check thấy service lên. Exit code 0 mà post-check fail thì Verification Failed. Retry tạo job mới và chạy lại pre-check.

AI gợi ý mỗi lần up hoặc down thì ghi một dòng có giờ. Dòng management kèm câu remediation available hoặc unavailable.

## Phần em tự làm

Em giữ job `restart_container` lỗi lúc 21:20 ngày 23/10, không xóa. Em tắt và bật SSH trên APP01, tắt và bật WinRM trên WIN01, bấm chạy job 20 khi SSH đã lên, và chụp các ảnh trong thư mục `screenshots`. Em chịu trách nhiệm về mã nguồn, kết quả test trên lab và nội dung báo cáo này.

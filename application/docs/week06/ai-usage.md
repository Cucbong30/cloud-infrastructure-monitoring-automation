# Khai báo sử dụng AI — Tuần 6 (Application)

## Công cụ sử dụng

Cursor (Grok), dùng khi viết code.

## Mục đích sử dụng

Nhờ làm controlled auto-remediation. Giữ pre-check SSH cổng 22 và WinRM cổng 5985, giữ post-check sau Ansible. Chỉ auto `restart_nginx`, `restart_container` và `restart_windows_exporter`. Thêm cooldown 2 phút, retry một lần, chặn duplicate job, tách incident, và giữ nút chạy tay cho operator.

Commit code tuần 6: https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/75601e49a81e8f4e8cf72a4e6df7ed878b5e3517.

Commit tuần 5, phần pre-check và verification còn dùng: https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/a7a65e96e9265517fad7cac7c136f9e1f0825bf4. Commit này có trailer `Co-authored-by: Cursor <cursoragent@cursor.com>`.

## Nội dung AI hỗ trợ

AI gợi ý flow: alert, incident hiện tại, management channel, allow-list, duplicate, cooldown, execute, verify, job và audit.

AI gợi ý cooldown 120 giây tính từ job Success gần nhất của cùng server và action. Execution failed thì retry đúng một lần, attempt 2 mang `retry_of_job_id`. Verification failed và kênh quản trị down không dùng ngân sách retry đó.

AI gợi ý incident đóng thì lần lỗi sau mở incident mới với `retry_count` bằng 0.

## Phần em tự làm

Em gây fault trên WEB01, APP01 và WIN01 tối 4/11. Em chụp các ảnh trong `screenshots` và giữ job 32 đến job 48. Em chịu trách nhiệm về mã nguồn, kết quả test trên lab và nội dung báo cáo này.

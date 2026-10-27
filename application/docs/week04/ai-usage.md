# Khai báo sử dụng AI — Tuần 4 (Application)

## Công cụ sử dụng

Cursor (Grok), dùng khi viết code và khi dựng báo cáo tuần này theo mẫu tuần 3.

## Mục đích sử dụng

Nhờ nối Portal với Ansible trên MON01, giữ allow-list ba action, lưu job history, nhãn trạng thái, audit, nút remediation, và trường hợp máy Unreachable thì không hiện nút restart. Nhờ sắp báo cáo tuần 4 từ nhật ký job trên lab và form tuần 3.

Commit code có trailer `Co-authored-by: Cursor <cursoragent@cursor.com>`.

## Nội dung AI hỗ trợ

AI gợi ý executor SSH từ laptop sang MON01 `192.168.10.10`, chỉ gọi một playbook trong allow-list `restart_nginx`, `restart_container`, `restart_windows_exporter`. Form không gửi path hay lệnh shell.

AI gợi ý lưu giờ chạy, server, action, result, output, và ghi `job.request` với `job.result`. Nhãn trên giao diện là Pending, Running, Success, Failed. Giờ hiển thị UTC+7.

AI gợi ý nút remediation trên Alert và Server Detail, và một thông báo khác khi exporter cùng dịch vụ đều DOWN. Lỗi Ansible hoặc target nằm trên job, portal không crash.

AI dựng file báo cáo này và `week-04-application.md` từ các job đã chạy trên lab.

## Phần em tự làm

Em chọn ba flow lab, bật Tailscale, điền user SSH, bấm Execute trên WEB01, APP01 và WIN01, đọc output playbook, và giữ các job Failed khi chưa có user hoặc khi máy không còn route. Em chịu trách nhiệm về mã nguồn, kết quả test trên lab và nội dung báo cáo này.

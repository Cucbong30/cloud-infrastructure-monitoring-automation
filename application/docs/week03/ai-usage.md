# Khai báo sử dụng AI — Tuần 3 (Application)

## Công cụ sử dụng

Cursor (Grok), dùng khi viết code.

## Mục đích sử dụng

Nhờ gợi ý cách nối Prometheus, cách chia service layer, câu PromQL, webhook Alertmanager, cách xử lý khi Prometheus chết, test pytest và bố cục dashboard.

AI hỗ trợ phần code. Bài báo cáo do em tự viết.

## Nội dung AI hỗ trợ

AI gợi ý cách gọi API Prometheus từ Flask, thời gian chờ, và không đưa token vào thông báo lỗi. AI cũng nhắc tách cổng 9090 (Prometheus còn sống) khỏi cổng 9100 (số liệu máy MON01).

AI gợi ý map WEB01, APP01, WIN01, MON01, các câu PromQL cho Linux và Windows, và probe Nginx cổng 80, App cổng 8080, WinRM cổng 5985, Prometheus cổng 9090, Alertmanager cổng 9093, Grafana cổng 3000.

AI gợi ý bốn nhóm trên dashboard và đường event log khi bấm dịch vụ DOWN.

AI gợi ý webhook `POST /api/alerts/webhook`, miễn CSRF, gắn `192.168.10.11:9100` với WEB01, không lưu trùng fingerprint, chuyển firing sang resolved, và ghi audit.

AI gợi ý khi Prometheus timeout hoặc trả dữ liệu sai thì dashboard vẫn HTTP 200, số liệu N/A, các trang còn lại vẫn mở. AI cũng gợi ý mock executor, chưa chạy Ansible thật, và ba action được phép.

## Phần em tự làm

Chọn cách làm, sửa code, chạy portal trên laptop qua Tailscale, test trên WEB01, APP01, WIN01 và MON01, tự chụp ảnh, đẩy nhánh `application` rồi merge vào `main`. Em chịu trách nhiệm về mã nguồn, kết quả test và bài báo cáo này.

# Khai báo sử dụng AI — Tuần 10 (Application)

## Công cụ sử dụng

Cursor (Grok), dùng khi viết code.

## Mục đích sử dụng

Nhờ làm incident lifecycle. Năm trạng thái từ OPEN đến CLOSED. Timeline ghi actor và thời gian. Incident gắn alert, job và approval. Risk lấy từ runbook. HTTP 200 mới tính là đã phục hồi.

Commit code tuần 10: https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/1ee9c98d7ea88e154ed62d783e4b11e46d18b33f.

Commit tuần 9 còn dùng cho approval: https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/b95ad447b07e58401e4296b4bd67a15852064998.

## Nội dung AI hỗ trợ

AI gợi ý auto remediation đi thẳng IN_PROGRESS, không bắt buộc acknowledge. Close chỉ nhận từ RESOLVED. Sự cố đang mở thì dùng lại incident cũ. Lần down sau khi đã resolved tạo incident mới.

AI gợi ý đọc fail theo tên task và không coi HTTP 403 là recovery.

## Phần em tự làm

Em chạy lab chiều và tối 28/11. Em chụp 48 ảnh. Em đối database để gắn OPEN, ACKNOWLEDGED, IN_PROGRESS và RESOLVED với job hoặc approval. Request 11 giữ một trạng thái APPROVAL_EXPIRED. Em chịu trách nhiệm về mã nguồn, kết quả test trên lab và nội dung báo cáo này.

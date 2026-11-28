# Báo cáo Application — Tuần 10

Nguyễn Thế Gia Bảo – Application / Integration

Trạng thái: Incident có OPEN, ACKNOWLEDGED, IN_PROGRESS, RESOLVED và CLOSED. Mỗi trạng thái trong lab 28/11 gắn job hoặc approval thật, trừ CLOSED chỉ có trong database. Request 11 giữ một trạng thái APPROVAL_EXPIRED. Evidence ở `application/docs/week10/`.

## Công việc được phân công

- Phân loại theo nguyên nhân rồi mới chọn action. Risk lấy từ runbook.
- Timeline ghi actor và thời gian. Không tạo incident mới khi sự cố cũ còn active.
- LOW chạy ngay. MEDIUM chờ Admin. Recovery là HTTP 200.
- Giữ ghi chú tuần 9: không có ảnh drawer job 71, job 72 và không có trang 403.

## Kết quả thực hiện

1. **OPEN.** INC-090 blocked, không có job. INC-088 gắn request 12, playbook chưa chạy.
2. **ACKNOWLEDGED.** INC-087, admin acknowledge 21:31, job 113 fail, status giữ nguyên.
3. **IN_PROGRESS.** INC-076 job 100 và INC-077 job 103. Auto không qua acknowledge.
4. **RESOLVED.** INC-089 job 115, Nginx HTTP 200, 610 ms. INC-088 job 114 sau khi Admin approve.
5. **CLOSED.** Database có close cho INC-069 đến INC-077. Bộ ảnh dừng ở nút Close Incident.
6. **Timeout.** Request 11 là APPROVAL_EXPIRED từ 20:25 ngày 20/11. Hàng chờ 28/11 vẫn hiện đúng status đó.

Báo cáo: [week-10-application.md](week-10-application.md). Bản Word: [week-10-application.docx](week-10-application.docx). Khai báo AI: [ai-usage.md](ai-usage.md).

## Kết quả trên GitHub

| Kết quả | Link | Commit |
| --- | --- | --- |
| Code tuần 10 | [1ee9c98](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/1ee9c98d7ea88e154ed62d783e4b11e46d18b33f) | cùng link |
| Code tuần 9 | [b95ad44](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/b95ad447b07e58401e4296b4bd67a15852064998) | cùng link |
| Báo cáo tuần 9 | [week09](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/tree/54efe804567064a26b4856a9bdf7ebc3494a552e/application/docs/week09) | [54efe80](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/54efe804567064a26b4856a9bdf7ebc3494a552e) |
| Ảnh và báo cáo tuần 10 | [week10](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/tree/6c15ef39809ceaa37ef3c160bea1bbef9242e18d/application/docs/week10) | [6c15ef39809ceaa37ef3c160bea1bbef9242e18d](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/6c15ef39809ceaa37ef3c160bea1bbef9242e18d) |

## Ảnh

Xem [screenshots/README.md](screenshots/README.md).

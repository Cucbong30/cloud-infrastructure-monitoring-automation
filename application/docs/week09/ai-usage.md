# Khai báo sử dụng AI — Tuần 9 (Application)

## Công cụ sử dụng

Cursor (Grok), dùng khi viết code.

## Mục đích sử dụng

Nhờ làm approval workflow. LOW chạy ngay. MEDIUM và HIGH chờ Admin. Operator không approve và không request HIGH. Rejected và hết hạn thì không gọi playbook. Audit và mail ghi requester, approver, decision và final status.

Commit code tuần 9: https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/b95ad447b07e58401e4296b4bd67a15852064998.

Commit tuần 8 còn dùng cho manual remediation và RBAC: https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/4960f041ed12294b595016e993720ba209fd6bf8.

## Nội dung AI hỗ trợ

AI gợi ý tách approval request khỏi job. Job chỉ được tạo sau khi Admin approve. Hết hạn mặc định 5 phút. Mail approval requested gửi tới email Admin, không gửi nhóm cảnh báo.

AI gợi ý Operator request được MEDIUM, bị 403 khi request hoặc approve HIGH.

## Phần em tự làm

Em chạy lab tối 20/11 trên WEB01, APP01 và AZURE01. Em chụp 42 ảnh portal và Outlook. Em đối database để chốt incident 46 đã đóng lúc 22:23 ngày 13/11. Em chịu trách nhiệm về mã nguồn, kết quả test trên lab và nội dung báo cáo này.

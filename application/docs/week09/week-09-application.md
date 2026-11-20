# Báo cáo Tuần 9

Nguyễn Thế Gia Bảo – Application / Integration

## Công việc được phân công

- Làm approval workflow. LOW chạy ngay. MEDIUM cần Admin xác nhận. HIGH cần Admin approve.
- Request có Pending, Approved, Rejected và Approval Expired. Hết hạn sau 5 phút.
- Operator request được MEDIUM. Operator không approve. Operator không request HIGH.
- Chỉ sau Approved mới tạo job và gọi playbook. Rejected và expired không gọi playbook.
- Audit ghi requester, approver, role, decision, timestamp, action và final status.
- Mail cho approval requested, rejected, và kết quả sau khi chạy.
- Chốt incident 46 của tuần 8. Giáo viên nhắc chụp thêm drawer job 71, job 72 và khung 403.

## Kết quả thực hiện

Tuần này em thêm cổng duyệt trước Ansible cho action không còn là LOW. `restart_nginx`, `restart_container` và `restart_windows_exporter` vẫn là LOW, chạy theo policy tuần 6. `restart_docker_service` trên APP01 là MEDIUM, playbook `restart-docker-service.yml`. `reboot_server` trên AZURE01 là HIGH, playbook `reboot-azure01.yml`. Request MEDIUM hoặc HIGH chưa có job. `APPROVAL_TIMEOUT_MINUTES=5`. Mail approval requested gửi email của Admin. Mail success và resolved vẫn vào nhóm Info.

Giờ dưới đây là giờ portal, đã cộng bảy tiếng. Lab chính chạy tối 20/11 trên `http://localhost:5000`.

### LOW vẫn chạy không cần duyệt

18/11 21:45, job 79, WEB01, `restart_nginx`, AUTO, actor SYSTEM, risk LOW, approval required No, exit code 0, final SUCCESS, incident 51. Trang Jobs ghi LOW runs after the usual checks. MEDIUM and HIGH create an approval request and do not start the playbook.

20/11 19:20, job 82 APP01 `restart_container` và job 83 WEB01 `restart_nginx` đều AUTO SUCCESS. 19:39 job 84 APP01 đang RUNNING. 19:40 job 84 EXECUTION_FAILED, job 85 attempt 2 MANUAL_REQUIRED, reason retry_limit. Drawer ghi playbook failed before verification. Incident 59 đóng 20:00 vì service restored. Mail Resolved tới KLTN-Alert-Info, role SYSTEM, action Restart App container.

### MEDIUM

19:42, operator `bui.phuong@cucbong.id.vn` tạo approval 2, APP01, `restart_docker_service`, MEDIUM, MANUAL. Status PENDING_APPROVAL. Execution NOT_RUN. Trang của Operator không có nút Approve. Dòng dưới ghi This request is waiting for an admin. Operator cannot approve it. Hết hạn 19:47, status APPROVAL_EXPIRED, không có job.

19:48, approval 3, cùng action, operator. Admin thấy nút Approve và Reject. Audit `approval.requested`, actor operator, decision PENDING_APPROVAL, reason Approval requested. The playbook was not started. Request này thành job 86. Banner ghi Approved, nhưng job 86 final EXECUTION_FAILED. Requester là operator, approver là `ntgbao@cucbong.id.vn` admin, decision APPROVED, incident 60, attempt 1. Job 87 cùng incident cũng EXECUTION_FAILED. 20:00 job 88, cùng approval path, exit code 0, final SUCCESS. Banner: Approved. Job 88 finished with status SUCCESS.

19:57 mail Approval Requested của request 5 tới BAO NGUYEN THE GIA, không phải nhóm Warning. Target APP01, Service Docker, risk MEDIUM, execution NOT_RUN, playbook has not started.

20:03, approval 6, operator request MEDIUM. 20:04 Admin reject, reason test. Status REJECTED. Job để trống. Execution NOT_RUN. Verification NOT_RUN. Audit có `approval.rejected`, actor admin, decision REJECTED, final REJECTED. Banner: The playbook was not started.

20:05, approval 7, operator request, Admin approve, job 91 SUCCESS, incident 62, retry_count 0.

20:20, approval 11, Admin tự request MEDIUM trên APP01. 20:25 hết hạn. Decision APPROVAL_EXPIRED, actor SYSTEM, role SYSTEM. Execution NOT_RUN. Job trống. Có toast Outlook Approval Expired.

Hàng chờ lúc 19:50 của Operator còn request 1, `restart_container`, MEDIUM, REJECTED ngày 18/11 bởi `operator01@cucbong.id.vn`. Đó là request cũ. Code hiện tại xếp `restart_container` là LOW và không tạo approval. Em không lấy request 1 làm evidence của policy tối 20/11.

### HIGH

20:10, Admin tạo approval 8, AZURE01, `reboot_server`, HIGH, MANUAL. Expires 20:15. Execution NOT_RUN. Audit `approval.requested`. Nút Approve và Reject chỉ hiện với Admin. Mail Approval Requested tới BAO NGUYEN THE GIA, request 8, risk HIGH, reason The playbook was not started.

20:11 Admin approve. Job 92 chạy. 20:12 job 92 SUCCESS, duration khoảng một phút, exit code 0. PLAY Reboot AZURE01, task Reboot server, changed. Verification Passed. AZURE01 is back. SSH `:22` is up and Nginx responded (203 ms). Requester và approver đều là `ntgbao@cucbong.id.vn`, role admin, decision APPROVED, incident 63 đóng vì success. Mail Remediation Success tới KLTN-Alert-Info.

20:13, approval 9, cùng HIGH reboot. Admin reject ngay, reason test. REJECTED, job trống, execution NOT_RUN. Mail Approval Rejected tới Admin, decision REJECTED, final status Rejected.

20:16, approval 10, HIGH, vẫn PENDING khi Operator mở. Không có nút Approve. Câu Operator cannot approve it. Hết hạn 20:21, APPROVAL_EXPIRED, không có approver và không có job. Mail requested của request 10 cũng tới Admin.

20:25 hàng chờ Admin không còn pending. History có request 11 và 10 expired, request 9 rejected, request 8 approved gắn job 92, request 7 approved gắn job 91.

Operator không có ảnh trang 403 khi bấm reboot. Test `test_operator_cannot_request_or_approve_a_high_risk_action` nhận 403, câu Permission denied for Operator role, và không tạo approval cũng không gọi executor.

### Chốt incident 46, job 71 và job 72

Báo cáo tuần 8 dừng lúc job 78, 22:07 ngày 13/11, incident 46 còn mở. Em đối lại database trước khi viết báo cáo này. Incident 46 đã resolved lúc 22:23 cùng ngày, reason service restored, retry_count 0. Không có job mới trên incident đó. Job 78 vẫn là MANAGEMENT_BLOCKED.

Job 71, 21:58 ngày 13/11, AZURE01 `restart_nginx`, AUTO, SYSTEM, exit code 0, final SUCCESS, incident 42. Job 72, 21:59, MANUAL, actor admin, exit code 0, final SUCCESS, incident 43. Bộ zip tối 20/11 không có drawer của job 71 và job 72. Em không tạo ảnh thay cho hai job đó.

Bộ zip cũng không có khung 403. Viewer và Operator bị chặn HIGH vẫn nằm ở test tuần 9 và test tuần 8.

## Kết quả trên GitHub

Code tuần 9 nằm ở commit `b95ad44` trên nhánh `application`. Ảnh và báo cáo nằm ở `application/docs/week09`.

| Kết quả | Commit message | Link | Commit |
| --- | --- | --- | --- |
| Code tuần 9 | Gate medium and high remediation behind admin approval. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/tree/b95ad447b07e58401e4296b4bd67a15852064998/application | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/b95ad447b07e58401e4296b4bd67a15852064998 |
| Cổng duyệt | Gate medium and high remediation behind admin approval. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/b95ad447b07e58401e4296b4bd67a15852064998/application/app/services/approval.py | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/b95ad447b07e58401e4296b4bd67a15852064998 |
| Mức risk của action | Gate medium and high remediation behind admin approval. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/b95ad447b07e58401e4296b4bd67a15852064998/application/app/executors/actions.py | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/b95ad447b07e58401e4296b4bd67a15852064998 |
| Mail approval | Gate medium and high remediation behind admin approval. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/b95ad447b07e58401e4296b4bd67a15852064998/application/app/services/notify.py | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/b95ad447b07e58401e4296b4bd67a15852064998 |
| Hàng chờ | Gate medium and high remediation behind admin approval. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/b95ad447b07e58401e4296b4bd67a15852064998/application/app/templates/automation/approvals.html | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/b95ad447b07e58401e4296b4bd67a15852064998 |
| Bảng approval | Gate medium and high remediation behind admin approval. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/b95ad447b07e58401e4296b4bd67a15852064998/application/migrations/versions/c3a9e7b21f04_approval_requests.py | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/b95ad447b07e58401e4296b4bd67a15852064998 |
| Playbook reboot AZURE01 | Gate medium and high remediation behind admin approval. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/b95ad447b07e58401e4296b4bd67a15852064998/application/automation/ansible/playbooks/reboot-azure01.yml | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/b95ad447b07e58401e4296b4bd67a15852064998 |
| Playbook Docker | Gate medium and high remediation behind admin approval. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/b95ad447b07e58401e4296b4bd67a15852064998/application/automation/ansible/playbooks/restart-docker-service.yml | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/b95ad447b07e58401e4296b4bd67a15852064998 |
| Test duyệt, reject, hết hạn, 403 | Gate medium and high remediation behind admin approval. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/b95ad447b07e58401e4296b4bd67a15852064998/application/tests/test_week9.py | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/b95ad447b07e58401e4296b4bd67a15852064998 |
| Code tuần 8 | Record who triggered a manual job and leave the AZURE01 key in the Ansible inventory. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/4960f041ed12294b595016e993720ba209fd6bf8 | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/4960f041ed12294b595016e993720ba209fd6bf8 |
| Báo cáo tuần 8 | Link the week 8 screenshots and report to their commit. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/tree/e3ad3935a71b701b96f455ffb83121fc7e619497/application/docs/week08 | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/e3ad3935a71b701b96f455ffb83121fc7e619497 |
| Thư mục tuần 9 | Add the week 9 approval workflow report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/tree/__DOCS_SHA__/application/docs/week09 | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/__DOCS_SHA__ |
| Báo cáo Word tuần 9 | Add the week 9 approval workflow report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/__DOCS_SHA__/application/docs/week09/week-09-application.docx | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/__DOCS_SHA__ |
| LOW không cần duyệt | Add the week 9 approval workflow report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/__DOCS_SHA__/application/docs/week09/screenshots/job79-low-auto-success.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/__DOCS_SHA__ |
| Operator không approve | Add the week 9 approval workflow report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/__DOCS_SHA__/application/docs/week09/screenshots/approval2-operator-cannot-approve.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/__DOCS_SHA__ |
| MEDIUM rejected | Add the week 9 approval workflow report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/__DOCS_SHA__/application/docs/week09/screenshots/approval6-rejected.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/__DOCS_SHA__ |
| MEDIUM success | Add the week 9 approval workflow report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/__DOCS_SHA__/application/docs/week09/screenshots/job88-approved-success.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/__DOCS_SHA__ |
| HIGH pending | Add the week 9 approval workflow report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/__DOCS_SHA__/application/docs/week09/screenshots/approval8-pending.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/__DOCS_SHA__ |
| HIGH success | Add the week 9 approval workflow report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/__DOCS_SHA__/application/docs/week09/screenshots/job92-approved-success.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/__DOCS_SHA__ |
| HIGH rejected mail | Add the week 9 approval workflow report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/__DOCS_SHA__/application/docs/week09/screenshots/mail-approval-rejected-9.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/__DOCS_SHA__ |
| Hết hạn | Add the week 9 approval workflow report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/__DOCS_SHA__/application/docs/week09/screenshots/approval11-expired-audit.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/__DOCS_SHA__ |
| Hàng chờ Admin | Add the week 9 approval workflow report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/__DOCS_SHA__/application/docs/week09/screenshots/admin-approval-queue.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/__DOCS_SHA__ |

## Luồng đã kiểm tra

- LOW: job 79 và job 82, job 83 SUCCESS, không có approval.
- LOW fail: job 84 rồi job 85, retry một lần, incident 59 đóng 20:00.
- MEDIUM pending: approval 2, Operator không có nút Approve. Hết hạn 19:47.
- MEDIUM approved rồi playbook fail: job 86. Lần sau job 88 SUCCESS.
- MEDIUM rejected: approval 6, reason test, không có job.
- MEDIUM approved SUCCESS: approval 7, job 91.
- MEDIUM expired: approval 11, actor SYSTEM.
- HIGH pending: approval 8, mail tới Admin, playbook chưa chạy.
- HIGH approved: job 92 reboot AZURE01, Nginx lên lại 203 ms.
- HIGH rejected: approval 9, mail Rejected, execution NOT_RUN.
- HIGH Operator: approval 10 không có nút Approve. Hết hạn 20:21.
- 403 khi Operator request HIGH: có test, không có ảnh.
- Job 71 và job 72 SUCCESS trong database ngày 13/11. Không có ảnh drawer.
- Incident 46: resolved 22:23 ngày 13/11, service restored, retry_count 0.

## Ảnh test case

![18/11 21:45. Job 79 WEB01 restart_nginx AUTO. Risk LOW. Approval required No. Final SUCCESS.](screenshots/job79-low-auto-success.jpg)

![18/11. Trang Jobs. LOW chạy sau check thường. MEDIUM và HIGH tạo approval, không start playbook.](screenshots/jobs-low-form.jpg)

![20/11 19:40. APP01 :8080 down. Retry limit của restart_container. Job 84 và job 85.](screenshots/app01-retry-limit-drawer.jpg)

![20/11 19:39. Job 84 RUNNING, restart_container, trước khi fail.](screenshots/job84-running.jpg)

![20/11 19:42. Approval 2. Operator. MEDIUM restart_docker_service. PENDING. Playbook was not started.](screenshots/approval2-operator-pending.jpg)

![Approval 2 với Operator. Không có nút Approve. Operator cannot approve it.](screenshots/approval2-operator-cannot-approve.jpg)

![19:48. Approval 3 khi Admin mở. PENDING. Nút Approve và Reject.](screenshots/approval3-admin-buttons.jpg)

![19:58. Mail Approval Requested, request 5, Docker trên APP01, MEDIUM, gửi Admin. Execution NOT_RUN.](screenshots/mail-approval-requested-5.jpg)

![20:04. Approval 6 REJECTED. Admin. Reason test. Playbook was not started.](screenshots/approval6-rejected.jpg)

![Audit approval 6. approval.rejected. Job trống. Execution NOT_RUN.](screenshots/approval6-audit.jpg)

![Job 86. Approved nhưng EXECUTION_FAILED. Requester operator, approver admin, MEDIUM.](screenshots/job86-approved-execution-failed.jpg)

![20:01. Job 88 SUCCESS. Approved. APP01 restart_docker_service. Incident 60.](screenshots/job88-approved-success.jpg)

![20:01. Mail Resolved APP01 tới KLTN-Alert-Info. Incident 59, role SYSTEM.](screenshots/mail-resolved-app01.jpg)

![20:10. Approval 8. Admin request reboot_server AZURE01. HIGH. PENDING. Expires 20:15.](screenshots/approval8-pending.jpg)

![Approval 8. Admin có Approve và Reject. Audit approval.requested. Execution NOT_RUN.](screenshots/approval8-admin-buttons.jpg)

![20:10. Mail Approval Requested request 8. HIGH reboot AZURE01. Gửi Admin.](screenshots/mail-approval-requested-8.jpg)

![20:12. Job 92. Approved SUCCESS. HIGH reboot. Requester và approver đều là admin.](screenshots/job92-approved-success.jpg)

![Job 92. PLAY Reboot AZURE01. SSH :22 up và Nginx responded 203 ms.](screenshots/job92-verified.jpg)

![20:12. Mail Remediation Success tới KLTN-Alert-Info. reboot_server. Verification PASSED.](screenshots/mail-reboot-success.jpg)

![20:13. Approval 9 REJECTED. HIGH reboot. Admin. Playbook was not started.](screenshots/approval9-rejected.jpg)

![Audit approval 9. approval.rejected, reason test. Không có job.](screenshots/approval9-audit.jpg)

![Mail Approval Rejected request 9. HIGH. Decision REJECTED. Execution NOT_RUN.](screenshots/mail-approval-rejected-9.jpg)

![Approval 10 khi Operator xem HIGH. Không có nút. Operator cannot approve it.](screenshots/approval10-operator-cannot-approve.jpg)

![20:20. Approval 11 PENDING. MEDIUM. Admin. Expires 20:25.](screenshots/approval11-pending.jpg)

![20:25. Approval 11 APPROVAL_EXPIRED. Execution NOT_RUN. Audit actor SYSTEM.](screenshots/approval11-expired-audit.jpg)

![20:25. Hàng chờ Admin. Pending trống. Request 8 gắn job 92. Request 7 gắn job 91. Request 9 rejected. Request 10 và 11 expired.](screenshots/admin-approval-queue.jpg)

![19:50. Hàng chờ Operator. Request 3 approved gắn job 86. Request 2 expired. Operator cannot approve.](screenshots/operator-approval-queue.jpg)

![20:01. Dashboard Admin. Năm host Healthy. AZURE01 SSH UP.](screenshots/admin-dashboard-healthy.jpg)

## Khai báo sử dụng AI

Công cụ: Cursor (Grok), dùng khi viết code.

Mục đích: Nhờ làm approval cho MEDIUM và HIGH. LOW giữ nguyên. Chỉ Admin approve. Operator không request HIGH. Rejected và hết hạn không gọi playbook. Audit và mail ghi đủ người yêu cầu, người duyệt và quyết định.

Commit code tuần 9: https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/b95ad447b07e58401e4296b4bd67a15852064998. Commit tuần 8: https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/4960f041ed12294b595016e993720ba209fd6bf8.

AI gợi ý chưa tạo job khi request còn pending, hết hạn 5 phút, và mail requested gửi Admin.

Phần em tự làm: Em gây fault và bấm duyệt trên APP01, AZURE01 tối 20/11, chụp 42 ảnh, và đối database để chốt incident 46 đã đóng 22:23 ngày 13/11. Em chịu trách nhiệm về mã nguồn, kết quả test trên lab và nội dung báo cáo này. Bộ ảnh không có drawer job 71, job 72 và không có trang 403.

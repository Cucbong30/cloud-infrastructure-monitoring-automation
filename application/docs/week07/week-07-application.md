# Báo cáo Tuần 7

Nguyễn Thế Gia Bảo – Application / Integration

## Công việc được phân công

- Đăng nhập Microsoft Entra ID. Role Admin, Operator, Viewer lấy từ App Role trên token, portal không gán role.
- Gửi mail cảnh báo bằng Microsoft Graph, app-only, `POST /users/{mailbox}/sendMail`. HTTP 202 là mail đã được nhận.
- Critical vào `KLTN-Alert-Critical`: Service Down, Execution Failed, Verification Failed, Manual Required. Warning vào `KLTN-Alert-Warning`: Remediation Started, Retry, Blocked. Info vào `KLTN-Alert-Info`: Remediation Success, Resolved.
- Mail là bảng HTML. Cột: Target, Service, Event Time, Event, Action, Final Status, Reason. Màu theo mức. Người gửi hiện CUCBONG Digital.
- Thêm AZURE01, environment Cloud, provider Azure, IP `20.243.24.91`. Nginx down map `restart_nginx`, playbook `restart-azure-nginx.yml`.
- Giữ policy tuần 6 trên AZURE01: pre-check SSH, post-check cổng 80, cooldown 2 phút, retry một lần khi execution failed, verification failed thì không retry, SSH down thì BLOCKED, operator vẫn chạy tay.
- Audit phân biệt AUTO, MANUAL, SYSTEM.
- Đóng gói portal bằng Docker. File `.env` không vào image.

## Kết quả thực hiện

Tuần này em gắn portal với Entra và thêm máy cloud AZURE01. Policy auto của tuần 6 không viết lại. `AUTO_REMEDIATION_COOLDOWN_SECONDS=120`, `AUTO_REMEDIATION_MAX_RETRIES=1`, executor `ansible`. Action an toàn trên AZURE01 vẫn là `restart_nginx`. Playbook trong repo là `automation/ansible/playbooks/restart-azure-nginx.yml`. Trên MON01, đường playbook mặc định là `~/ansible/playbooks/restart-azure-nginx.yml`. Task restart là `sudo -n systemctl restart nginx`, task sau mới đợi cổng 80.

Giờ dưới đây là giờ portal, đã cộng bảy tiếng so với giờ lưu trong SQLite. Lab AZURE01 chạy tối 5/11 và tối 6/11. Portal trong ảnh là `http://localhost:5000`.

Đăng nhập: khi đã có tenant, client id và client secret, trang login đưa nút Microsoft lên trước. Callback là `http://localhost:5000/auth/callback`. Role đọc từ claim `roles`. Không có role thì user ở Viewer. Trang Users ghi Roles are read from the Microsoft Entra App Role on each sign-in. This page does not assign roles. Tối 5/11 em đăng nhập `ntgbao@cucbong.id.vn`, role admin, last login 2026-11-05 22:35. Bảng còn dòng admin, operator và viewer. Client secret chỉ nằm trong `.env` local, không vào GitHub và không vào báo cáo này.

Mail đi từ mailbox generic qua Graph, không gọi `/me/sendMail`. Thiếu mailbox thì remediation vẫn chạy. Bảng mail có Target, Service, Event Time, Event, Action, Final Status, Reason. Action của Nginx hiện Restart Nginx (systemctl restart nginx). Footer là timeline Service Down, Remediation, Verification, Healthy.

### Inventory và SSO

22:37 ngày 5/11, dashboard có năm server. AZURE01 là Cloud, role Web, IP `20.243.24.91`, Healthy, SSH UP. WEB01, APP01, WIN01, MON01 vẫn là local. Em đang đăng nhập `ntgbao@cucbong.id.vn`.

### AZURE01 success và cooldown

22:41 Nginx trên AZURE01 down, SSH UP. Drawer gợi ý Restart Nginx.

22:46, job 50, incident 18, `restart_nginx`, trigger auto, attempt 1, exit code 2, final VERIFICATION_FAILED. Các alert sau vẫn trỏ về job này.

22:57, job 53, incident 21, exit code 0, verification passed, final SUCCESS. 22:58 drawer ghi cooldown. Lần auto cuối là job 53 lúc 22:57, lần auto sau được phép từ 22:59. Alert gắn Job 53 SUCCESS và Job 50 VERIFICATION_FAILED.

23:00, job 54, incident 22, exit code 0, verification passed, final SUCCESS. Drawer ghi Incident 22 resolved (success) và Nginx `:80` is up (202 ms). retry_count của incident là 0. 23:01 cooldown của job 54, next auto run 23:02. Alert gắn Job 54 SUCCESS, Job 53 SUCCESS và Job 50 VERIFICATION_FAILED.

### AZURE01 execution failed

23:02, job 55, incident 23, attempt 1, exit code 2, final EXECUTION_FAILED, verification skipped. Ảnh lúc job còn chạy ghi Job 55 RUNNING.

Job 56 là retry của job 55, attempt 2, exit code 2, final MANUAL_REQUIRED, reason `retry_limit`. Drawer ghi Playbook failed before verification. 23:04 incident 23 đóng vì service restored, retry_count 1. Nginx đã lên. Dòng retry limit còn nằm trong log. Lần lỗi sau mở incident mới, retry_count bắt đầu từ 0.

### AZURE01 SSH blocked

23:04 SSH xuống. Incident 24 BLOCKED, reason `management_channel_unavailable`, retry_count 0. Không có job playbook. Drawer ghi SSH DOWN và playbook was not started. Incident đóng lúc 23:04 vì service restored. Khi SSH lên lại, drawer ghi Restart Nginx can run, và có dòng skipped vì service is up.

### AZURE01 verification failed

23:05, job 57, incident 25, attempt 1. Ảnh lúc đang chạy ghi Job 57 RUNNING, trigger NginxDown. Execution xong, post-check cổng 80 failed, final VERIFICATION_FAILED. Không có attempt 2. 23:06 host Degraded, SSH vẫn UP. 23:07 incident 25 đóng vì service restored, Nginx lên. Dòng verification failed còn trong log.

### Mail tối 6/11

Tối 6/11 em chạy lại case verification trên AZURE01 để có mail. Job 59, incident 30, 21:53 đến 21:54, attempt 1, final VERIFICATION_FAILED. Không có attempt 2. Incident 30 mở 21:53, đóng 21:56 vì service restored, retry_count 0.

21:54 mail Service Down tới KLTN-Alert-Critical. Status OPEN. Event Time 6 Nov 2026 21:53 ICT. Nội dung Incident 30 opened.

Cùng lúc, mail Remediation Started tới kltn-alert-warning. Status Running. Event Time 21:53.

21:54 mail Verification Failed tới nhóm Critical. Reason là post-check port 80 failed, no retry.

Mail Manual Required cũng tới nhóm Critical, cùng reason.

21:56 mail Resolved tới KLTN-Alert-Info. Incident 30 service restored, retry_count 0. Drawer cùng phút ghi All checks OK và incident 30 resolved. Dòng 21:54 verification failed còn nằm phía dưới.

Bộ ảnh không có khung mail riêng cho Execution Failed, Retry và Blocked. Ba event đó vẫn đi đúng nhóm trong code: Execution Failed là critical, Retry và Blocked là warning. Test `test_alert_mail_uses_the_distribution_group_for_its_severity` kiểm tra Service Down, Remediation Success, Verification Failed, Manual Required và Remediation Started. Test `test_graph_sendmail_treats_202_as_accepted` kiểm tra URL `/users/{mailbox}/sendMail`, body HTML, và status 202.

### Cooldown, duplicate, chạy tay, Docker

Cooldown chỉ tính từ job Success gần nhất của cùng server và action. Job 53 xong 22:57 thì lần auto sau là 22:59. Job 54 xong 23:00 thì lần sau là 23:02. Trong cửa sổ đó alert vẫn hiện, job mới không được tạo.

Duplicate: cùng server và action đang queued hoặc running thì alert mới không tạo job thứ hai. Bộ ảnh 5/11 và 6/11 không có khung chữ duplicate skipped. Job 55 và job 57 đều có lúc Result RUNNING. Đó là cửa sổ lệnh sau bị chặn. Test tuần 6 vẫn còn: `test_queued_action_blocks_a_duplicate_auto_job`.

Operator vẫn chạy tay. Khi SSH lên, drawer giữ Remediation available và Restart Nginx can run. Job 49 là một lần bấm tay, status canceled, không có final result và không mở incident. Auto để MANUAL_REQUIRED không tắt đường chạy tay.

Audit ghi actor SYSTEM khi việc do portal tự làm. Nhãn trigger trên job là AUTO, MANUAL hoặc SYSTEM.

Docker: `Dockerfile` dùng `python:3.11-slim`, cài `openssh-client`, chạy `flask run --host 0.0.0.0 --port 5000`. `docker-compose.yml` map cổng 5000 và mount `instance`. `.dockerignore` loại `.env`, `.venv`, `.git` và `instance/*.db`. Em chưa chụp `docker ps`, và chưa chụp image được deploy lên AZURE01. Ảnh lab là portal trên localhost.

## Kết quả trên GitHub

Code tuần 7 nằm ở commit `c13696e` trên nhánh `application`. Ảnh và báo cáo nằm ở `application/docs/week07`. Bảng dưới ghi link tree, link file và link commit.

| Kết quả | Commit message | Link | Commit |
| --- | --- | --- | --- |
| Code tuần 7 | Add Entra SSO, alert mail, and AZURE01 on the week 6 remediation policy. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/tree/c13696e4d637f098e2b3806b7f92937bf43ddf79/application | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/c13696e4d637f098e2b3806b7f92937bf43ddf79 |
| Entra SSO và App Role | Add Entra SSO, alert mail, and AZURE01 on the week 6 remediation policy. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/c13696e4d637f098e2b3806b7f92937bf43ddf79/application/app/services/entra.py | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/c13696e4d637f098e2b3806b7f92937bf43ddf79 |
| Login Microsoft | Add Entra SSO, alert mail, and AZURE01 on the week 6 remediation policy. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/c13696e4d637f098e2b3806b7f92937bf43ddf79/application/app/blueprints/auth.py | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/c13696e4d637f098e2b3806b7f92937bf43ddf79 |
| Trang Users, không gán role | Add Entra SSO, alert mail, and AZURE01 on the week 6 remediation policy. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/c13696e4d637f098e2b3806b7f92937bf43ddf79/application/app/blueprints/users.py | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/c13696e4d637f098e2b3806b7f92937bf43ddf79 |
| Mail Graph và nhóm phân phối | Add Entra SSO, alert mail, and AZURE01 on the week 6 remediation policy. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/c13696e4d637f098e2b3806b7f92937bf43ddf79/application/app/services/notify.py | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/c13696e4d637f098e2b3806b7f92937bf43ddf79 |
| Biến Entra, Graph, AZURE01 | Add Entra SSO, alert mail, and AZURE01 on the week 6 remediation policy. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/c13696e4d637f098e2b3806b7f92937bf43ddf79/application/.env.example | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/c13696e4d637f098e2b3806b7f92937bf43ddf79 |
| Playbook Nginx AZURE01 | Add Entra SSO, alert mail, and AZURE01 on the week 6 remediation policy. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/c13696e4d637f098e2b3806b7f92937bf43ddf79/application/automation/ansible/playbooks/restart-azure-nginx.yml | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/c13696e4d637f098e2b3806b7f92937bf43ddf79 |
| Policy cooldown, retry, duplicate | Add Entra SSO, alert mail, and AZURE01 on the week 6 remediation policy. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/c13696e4d637f098e2b3806b7f92937bf43ddf79/application/app/services/remediation.py | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/c13696e4d637f098e2b3806b7f92937bf43ddf79 |
| Audit AUTO, MANUAL, SYSTEM | Add Entra SSO, alert mail, and AZURE01 on the week 6 remediation policy. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/c13696e4d637f098e2b3806b7f92937bf43ddf79/application/app/services/audit.py | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/c13696e4d637f098e2b3806b7f92937bf43ddf79 |
| Migration cloud và SSO | Add Entra SSO, alert mail, and AZURE01 on the week 6 remediation policy. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/c13696e4d637f098e2b3806b7f92937bf43ddf79/application/migrations/versions/e6f8a1c93b20_cloud_sso.py | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/c13696e4d637f098e2b3806b7f92937bf43ddf79 |
| Dockerfile | Add Entra SSO, alert mail, and AZURE01 on the week 6 remediation policy. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/c13696e4d637f098e2b3806b7f92937bf43ddf79/application/Dockerfile | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/c13696e4d637f098e2b3806b7f92937bf43ddf79 |
| .dockerignore loại .env | Add Entra SSO, alert mail, and AZURE01 on the week 6 remediation policy. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/c13696e4d637f098e2b3806b7f92937bf43ddf79/application/.dockerignore | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/c13696e4d637f098e2b3806b7f92937bf43ddf79 |
| Test SSO, mail, AZURE01, Viewer | Add Entra SSO, alert mail, and AZURE01 on the week 6 remediation policy. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/c13696e4d637f098e2b3806b7f92937bf43ddf79/application/tests/test_week7.py | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/c13696e4d637f098e2b3806b7f92937bf43ddf79 |
| Policy tuần 6 | Add controlled auto-remediation with cooldown, one retry, and per-incident state. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/75601e49a81e8f4e8cf72a4e6df7ed878b5e3517 | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/75601e49a81e8f4e8cf72a4e6df7ed878b5e3517 |
| Báo cáo tuần 6 | Add the week 6 controlled auto-remediation report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/tree/e10dbe17d5d06e81e7d2bcf4b0e4988bdf070942/application/docs/week06 | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/e10dbe17d5d06e81e7d2bcf4b0e4988bdf070942 |
| Thư mục tuần 7 | Add the week 7 cloud, SSO, and alert-mail report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/tree/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7/application/docs/week07 | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7 |
| Báo cáo Word tuần 7 | Add the week 7 cloud, SSO, and alert-mail report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7/application/docs/week07/week-07-application.docx | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7 |
| Dashboard AZURE01 | Add the week 7 cloud, SSO, and alert-mail report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7/application/docs/week07/screenshots/azure01-inventory-dashboard.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7 |
| Users và Entra role | Add the week 7 cloud, SSO, and alert-mail report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7/application/docs/week07/screenshots/users-entra-roles.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7 |
| AZURE01 Nginx down | Add the week 7 cloud, SSO, and alert-mail report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7/application/docs/week07/screenshots/azure01-nginx-down-2241.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7 |
| AZURE01 success | Add the week 7 cloud, SSO, and alert-mail report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7/application/docs/week07/screenshots/azure01-success-incident22.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7 |
| AZURE01 verified 202 ms | Add the week 7 cloud, SSO, and alert-mail report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7/application/docs/week07/screenshots/azure01-success-verified.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7 |
| Cooldown job 53 | Add the week 7 cloud, SSO, and alert-mail report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7/application/docs/week07/screenshots/azure01-cooldown-job53.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7 |
| Cooldown job 54 | Add the week 7 cloud, SSO, and alert-mail report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7/application/docs/week07/screenshots/azure01-cooldown-job54.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7 |
| Alert gắn job | Add the week 7 cloud, SSO, and alert-mail report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7/application/docs/week07/screenshots/azure01-alert-jobs.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7 |
| Job 55 đang chạy | Add the week 7 cloud, SSO, and alert-mail report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7/application/docs/week07/screenshots/azure01-job55-running.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7 |
| Execution started | Add the week 7 cloud, SSO, and alert-mail report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7/application/docs/week07/screenshots/azure01-execution-started.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7 |
| Retry limit | Add the week 7 cloud, SSO, and alert-mail report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7/application/docs/week07/screenshots/azure01-retry-limit.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7 |
| Playbook failed | Add the week 7 cloud, SSO, and alert-mail report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7/application/docs/week07/screenshots/azure01-execution-failed-detail.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7 |
| Incident 23 resolved | Add the week 7 cloud, SSO, and alert-mail report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7/application/docs/week07/screenshots/azure01-incident23-resolved.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7 |
| SSH blocked | Add the week 7 cloud, SSO, and alert-mail report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7/application/docs/week07/screenshots/azure01-ssh-blocked.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7 |
| Blocked rồi restored | Add the week 7 cloud, SSO, and alert-mail report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7/application/docs/week07/screenshots/azure01-blocked-then-restored.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7 |
| SSH lên, can run | Add the week 7 cloud, SSO, and alert-mail report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7/application/docs/week07/screenshots/azure01-ssh-up-can-run.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7 |
| Job 57 đang chạy | Add the week 7 cloud, SSO, and alert-mail report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7/application/docs/week07/screenshots/azure01-job57-running.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7 |
| Verification started | Add the week 7 cloud, SSO, and alert-mail report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7/application/docs/week07/screenshots/azure01-verification-started.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7 |
| Execution xong, verify fail | Add the week 7 cloud, SSO, and alert-mail report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7/application/docs/week07/screenshots/azure01-execution-succeeded-verify-failed.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7 |
| Verification failed | Add the week 7 cloud, SSO, and alert-mail report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7/application/docs/week07/screenshots/azure01-verification-failed.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7 |
| Incident 25 resolved | Add the week 7 cloud, SSO, and alert-mail report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7/application/docs/week07/screenshots/azure01-incident25-resolved.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7 |
| Incident 30 resolved | Add the week 7 cloud, SSO, and alert-mail report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7/application/docs/week07/screenshots/azure01-incident30-resolved.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7 |
| Mail Service Down | Add the week 7 cloud, SSO, and alert-mail report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7/application/docs/week07/screenshots/mail-service-down.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7 |
| Mail Remediation Started | Add the week 7 cloud, SSO, and alert-mail report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7/application/docs/week07/screenshots/mail-remediation-started.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7 |
| Mail Verification Failed | Add the week 7 cloud, SSO, and alert-mail report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7/application/docs/week07/screenshots/mail-verification-failed.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7 |
| Mail Manual Required | Add the week 7 cloud, SSO, and alert-mail report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7/application/docs/week07/screenshots/mail-manual-required.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7 |
| Mail Resolved | Add the week 7 cloud, SSO, and alert-mail report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7/application/docs/week07/screenshots/mail-resolved.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7 |

## Luồng đã kiểm tra

- Dashboard: AZURE01 Cloud, `20.243.24.91`, SSH UP.
- SSO: `ntgbao@cucbong.id.vn` role admin. Trang Users không gán role.
- AZURE01 Nginx down, SSH up, 22:41: gợi ý Restart Nginx.
- Job 53 SUCCESS 22:57. Cooldown đến 22:59.
- Job 54 SUCCESS 23:00, incident 22, Nginx `:80` up 202 ms. Cooldown đến 23:02.
- Job 55 EXECUTION_FAILED, job 56 MANUAL_REQUIRED, reason retry_limit, incident 23. Đóng 23:04.
- SSH down: incident 24 BLOCKED, không có job playbook. SSH lên thì Restart Nginx can run.
- Job 57 VERIFICATION_FAILED, một attempt, incident 25. Đóng 23:07.
- Tối 6/11, job 59 VERIFICATION_FAILED, incident 30. Mail Critical, Warning và Info đúng nhóm. Incident đóng 21:56.
- Duplicate skipped không có khung chữ riêng. Job 55 và job 57 có lúc RUNNING.
- Docker: Dockerfile và `.dockerignore` có trong commit. Chưa có ảnh `docker ps`.

## Ảnh test case

![22:37 ngày 5/11. Dashboard năm server. AZURE01 Cloud, Web, 20.243.24.91, Healthy, SSH UP. Đang đăng nhập ntgbao@cucbong.id.vn.](screenshots/azure01-inventory-dashboard.jpg)

![Trang Users. Roles are read from the Microsoft Entra App Role on each sign-in. This page does not assign roles. ntgbao@cucbong.id.vn là admin, last login 2026-11-05 22:35.](screenshots/users-entra-roles.jpg)

![22:41 AZURE01. Nginx down, SSH UP. Suggested action Restart Nginx.](screenshots/azure01-nginx-down-2241.jpg)

![23:00 AZURE01. Incident 22 resolved success. Job 54, restart_nginx.](screenshots/azure01-success-incident22.jpg)

![23:00 AZURE01. Nginx :80 is up (202 ms). Verification passed.](screenshots/azure01-success-verified.jpg)

![22:58 AZURE01. Cooldown. Job 53 lúc 22:57, lần auto sau từ 22:59. Alert gắn Job 53 SUCCESS và Job 50 VERIFICATION_FAILED.](screenshots/azure01-cooldown-job53.jpg)

![23:01 AZURE01. Cooldown của job 54 lúc 23:00, next auto run 23:02. Alert gắn Job 54, Job 53 và Job 50.](screenshots/azure01-cooldown-job54.jpg)

![Alert AZURE01 gắn các job SUCCESS và job 50 VERIFICATION_FAILED. Nginx down rồi up.](screenshots/azure01-alert-jobs.jpg)

![23:02 AZURE01. Job 55 RUNNING, restart_nginx.](screenshots/azure01-job55-running.jpg)

![23:02 AZURE01. Auto-remediation started, Result RUNNING.](screenshots/azure01-execution-started.jpg)

![23:02 AZURE01. Retry limit. Job 55 fail, job 56 là attempt 2. MANUAL_REQUIRED.](screenshots/azure01-retry-limit.jpg)

![Playbook failed before verification. Exit code 2. Incident 23.](screenshots/azure01-execution-failed-detail.jpg)

![23:04 AZURE01. Incident 23 resolved. Nginx up. Dòng retry limit còn trong log.](screenshots/azure01-incident23-resolved.jpg)

![SSH DOWN. BLOCKED. Playbook was not started. Incident 24.](screenshots/azure01-ssh-blocked.jpg)

![Incident 24 resolved. Dòng blocked còn phía dưới. Có skipped vì service is up.](screenshots/azure01-blocked-then-restored.jpg)

![SSH UP. Restart Nginx can run. Operator còn đường chạy tay.](screenshots/azure01-ssh-up-can-run.jpg)

![23:05 AZURE01. Job 57 RUNNING, trigger NginxDown.](screenshots/azure01-job57-running.jpg)

![23:05 AZURE01. Auto-remediation started, Result RUNNING. Incident 25.](screenshots/azure01-verification-started.jpg)

![Execution succeeded và verification failed trên cùng drawer. Không có retry.](screenshots/azure01-execution-succeeded-verify-failed.jpg)

![23:06 AZURE01 Degraded, SSH UP. Post-check port 80 failed, no retry. Job 57.](screenshots/azure01-verification-failed.jpg)

![23:07 AZURE01. Incident 25 resolved. Nginx up. Dòng verification failed còn trong log.](screenshots/azure01-incident25-resolved.jpg)

![21:56 ngày 6/11. All checks OK. Incident 30 resolved. Dòng 21:54 verification failed còn phía dưới. Job 59, một attempt.](screenshots/azure01-incident30-resolved.jpg)

![21:54 ngày 6/11. Mail Service Down tới KLTN-Alert-Critical. OPEN. Event Time 21:53 ICT. Incident 30 opened. Người gửi CUCBONG Digital.](screenshots/mail-service-down.jpg)

![Mail Remediation Started tới kltn-alert-warning. Status Running. Event Time 21:53.](screenshots/mail-remediation-started.jpg)

![Mail Verification Failed tới nhóm Critical. 21:54. Post-check port 80 failed, no retry.](screenshots/mail-verification-failed.jpg)

![Mail Manual Required tới nhóm Critical. Cùng reason post-check.](screenshots/mail-manual-required.jpg)

![21:56. Mail Resolved tới KLTN-Alert-Info. Incident 30 service restored, retry_count 0.](screenshots/mail-resolved.jpg)

## Khai báo sử dụng AI

Công cụ: Cursor (Grok), dùng khi viết code.

Mục đích: Nhờ gắn Microsoft Entra SSO, lấy role từ App Role. Gửi mail Graph app-only tới ba distribution group. Thêm AZURE01 và giữ nguyên cooldown, retry, duplicate, blocked và manual của tuần 6. Đóng gói Docker, không đưa `.env` vào image.

Commit code tuần 7: https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/c13696e4d637f098e2b3806b7f92937bf43ddf79. Commit policy tuần 6: https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/75601e49a81e8f4e8cf72a4e6df7ed878b5e3517.

AI gợi ý role lấy từ claim `roles`, mail dùng `POST /users/{mailbox}/sendMail`, 202 là accepted, và bảng HTML theo mức Critical, Warning, Info. Policy auto không tách riêng cho cloud.

Phần em tự làm: Em đăng ký app trên Entra, tạo ba nhóm mail, gây fault Nginx và SSH trên AZURE01 tối 5/11 và tối 6/11, chụp 27 ảnh portal và Outlook, và giữ job 49 đến job 59 trong database. Em chịu trách nhiệm về mã nguồn, kết quả test trên lab và nội dung báo cáo này. Client secret không được commit.

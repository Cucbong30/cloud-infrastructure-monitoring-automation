# Báo cáo Tuần 6

Nguyễn Thế Gia Bảo – Application / Integration

## Công việc được phân công

- Giữ management pre-check trước khi chạy, và post-check sau Ansible.
- Chỉ cho auto các remediation action an toàn, risk low.
- Thêm cooldown 2 phút sau job Success.
- Giới hạn retry: execution failed thì retry đúng một lần, rồi MANUAL_REQUIRED.
- Hạn chế duplicate job khi cùng target và action đang queued hoặc running.
- Kiểm tra auto-remediation success và failure trên WEB01, APP01, WIN01.
- Giữ manual remediation để operator vẫn bấm được.
- Mỗi incident mới bắt đầu lại với retry_count bằng 0.
- Verification failed thì MANUAL_REQUIRED, không dùng tiếp ngân sách retry của execution failed.
- Management channel down thì BLOCKED, playbook không chạy.

## Kết quả thực hiện

Tuần này em bật `AUTO_REMEDIATION_ENABLED`. Portal tự gọi Ansible trên MON01 `192.168.10.10` cho ba action risk low. `restart_nginx` gắn WEB01 và `restart-nginx.yml`. `restart_container` gắn APP01, container `app01-web`, playbook `restart-app-container.yml`. `restart_windows_exporter` gắn WIN01, service `windows_exporter`, playbook `restart-windows-exporter.yml`. Reboot, kill process, disk cleanup, xóa file và đổi network nằm ngoài allow-list. CPU, RAM, disk cao chỉ là cảnh báo.

Pre-check và post-check của tuần 5 vẫn chạy. WEB01 hỏi SSH `192.168.10.11` cổng 22, rồi post-check Nginx cổng 80. APP01 hỏi SSH `192.168.10.12` cổng 22, rồi post-check App cổng 8080. WIN01 hỏi WinRM `192.168.10.13` cổng 5985, rồi post-check Windows Exporter cổng 9182. Cổng quản trị down thì incident ghi BLOCKED, reason `management_channel_unavailable`, và không có dòng job playbook.

Luồng auto là: alert firing, lấy incident hiện tại của đúng server và action, bỏ qua nếu server đang maintenance, kiểm tra allow-list và risk, chặn duplicate, chặn cooldown, chạy, verify, ghi job và audit. Status cuối phân biệt SUCCESS, EXECUTION_FAILED, BLOCKED, VERIFICATION_FAILED và MANUAL_REQUIRED. Cooldown và duplicate ghi `auto_remediation.skipped`. Giờ dưới đây là giờ portal, đã cộng bảy tiếng so với giờ lưu trong SQLite. Lab chạy tối 4/11.

Cooldown để `AUTO_REMEDIATION_COOLDOWN_SECONDS=120`. Retry để `AUTO_REMEDIATION_MAX_RETRIES=1`. Executor là `ansible`.

### WEB01

20:27, job 32, incident 1, `restart_nginx`, trigger auto, attempt 1. Exit code 0, verification passed, final SUCCESS. Drawer ghi Incident 1 resolved (success) và Nginx `:80` is up (687 ms). Incident đóng, lần sau bắt đầu ở retry_count 0.

20:29 Nginx xuống lại trong cửa sổ cooldown. Drawer ghi Auto-remediation skipped: cooldown. Job 32 vừa chạy lúc 20:27, lần auto sau được phép từ 20:29. Hết cửa sổ thì incident 2 mới chạy. Job 33, 20:29:54 đến 20:29:58, attempt 1, exit code 2, final EXECUTION_FAILED, verification skipped. Job 34 retry của job 33, attempt 2, exit code 2, final MANUAL_REQUIRED, reason `retry_limit`. Output là play Recover Nginx, task Restart nginx service failed vì `systemctl restart nginx` trả control process exited. 20:32 incident 2 đóng vì service restored.

20:33 SSH xuống trong khi Nginx đã lên. Incident 3 BLOCKED, reason `management_channel_unavailable`. Không có job playbook cho incident này. Drawer ghi Remediation unavailable, WEB01 management channel SSH `:22` is down, The playbook was not started, và Manual intervention required. 20:34 Nginx vẫn up, incident 3 đóng, câu trên drawer nói next failure starts a new incident at retry_count 0. 20:36 SSH lên lại, dòng mới nói Remediation available, Restart Nginx can run.

20:36 là incident mới, không ăn retry của incident 2. Job 35 attempt 1, exit code 2, EXECUTION_FAILED. Job 36 attempt 2, retry của job 35, MANUAL_REQUIRED, reason `retry_limit`. Lúc job còn chạy, drawer thấy Result RUNNING và Job 36. 20:37 incident 4 đóng, Nginx `:80` is up.

21:40, job 48, incident 15, attempt 1, exit code 2, verification failed, final VERIFICATION_FAILED. Drawer 21:40 ghi command completed, post-check on port 80 failed, no retry, Manual intervention required. Incident 15 đóng lúc 21:43 vì service restored. Không có attempt 2.

21:45 SSH lại down. Incident 16 mở, BLOCKED, `management_channel_unavailable`, retry_count 0, manual_required. Không có job nào sau job 48.

### APP01

20:48, job 37, incident 5, `restart_container`, exit code 0, verification passed, SUCCESS. App `:8080` is up (532 ms). 20:50, job 38, incident 6, cùng kết quả SUCCESS. 20:51 alert lặp trong cooldown: last ran as job 38 lúc 20:50, next auto run 20:52. 20:52, job 39, incident 7, SUCCESS, App `:8080` is up (546 ms). 20:54 cooldown của job 39, next auto run 20:55. Alert `container_down` gắn Job 39 SUCCESS, Job 38 SUCCESS, Job 37 SUCCESS.

20:55, incident 8. Job 40 attempt 1, exit code 2, EXECUTION_FAILED. Job 41 attempt 2, retry của job 40, MANUAL_REQUIRED, reason `retry_limit`. Drawer ghi Playbook failed before verification. 20:56 App lên, incident 8 đóng, retry_count của lần sau về 0.

20:57 SSH xuống. Incident 9 BLOCKED, không có job playbook. App `:8080` vẫn up lúc 20:56, dòng management riêng nói Remediation unavailable, playbook was not started. 20:59 SSH lên, Incident 9 resolved, Remediation available, Restart container can run. Có thêm dòng Auto-remediation skipped: service is up, vì cổng 8080 đã trả lời.

21:01, incident 10. Job 42, 21:01:03 đến 21:01:24, attempt 1, exit code 2, final VERIFICATION_FAILED. Job 43, 21:01:24 đến 21:01:44, attempt 2, retry của job 42, cùng final VERIFICATION_FAILED. Drawer ghi command finished, post-check failed, Manual intervention required. 21:16 App lên, Incident 10 resolved (service restored), next incident at retry_count 0. Hai case verification phía sau, WIN01 và WEB01, mỗi incident chỉ còn một job.

21:45 incident 17 mở, BLOCKED, SSH down, không có job playbook mới.

### WIN01

21:16, job 44, incident 11, `restart_windows_exporter`, exit code 0, verification passed, SUCCESS. Windows Exporter `:9182` is up (953 ms). Incident đóng với success và retry_count 0. Cùng phút có dòng skipped vì service is up khi probe đã xanh.

21:19, incident 12. Job 45 attempt 1, exit code 2, EXECUTION_FAILED, Playbook failed before verification. Job 46 attempt 2, retry của job 45, MANUAL_REQUIRED, reason `retry_limit`. 21:21 exporter lên, Incident 12 resolved, next failure starts at retry_count 0.

21:23 WinRM `:5985` down trong khi exporter `:9182` vẫn up. Host Degraded. Dòng management: Remediation unavailable, action `restart_windows_exporter`, The playbook was not started. Khi cả exporter và WinRM đều down, drawer ghi Unreachable và Manual intervention required, reason `management_channel_unavailable`, BLOCKED. Đó là incident 13, không có job playbook. 21:24 cả hai cổng lên, Incident 13 resolved, Remediation available, Restart Windows Exporter can run.

21:26, job 47, incident 14, attempt 1, exit code 2, final VERIFICATION_FAILED. Drawer lúc đang chạy ghi Auto-remediation started và Result RUNNING. Xong job, `job.result` ghi Remediation task succeeded, but verification task Wait for Windows Exporter port 9182 failed. Dòng sau nói post-check failed, no retry, MANUAL_REQUIRED. Incident 14 còn mở, reason `verification_failed`. Không có attempt 2.

### Cooldown, duplicate và chạy tay

Cooldown chỉ tính từ job Success gần nhất của cùng server và action. WEB01 job 32 xong 20:27 thì lần auto sau là 20:29. APP01 job 38 xong 20:50 thì lần sau là 20:52, job 39 xong 20:53 thì lần sau là 20:55. Trong cửa sổ đó alert vẫn hiện, job mới không được tạo.

Duplicate: cùng server và action đang queued hoặc running thì alert mới không tạo job thứ hai. Audit ghi reason duplicate, result DUPLICATE_SKIPPED. Bộ ảnh tối 4/11 không có một khung riêng chữ duplicate skipped. Job 36, job 42 và job 47 đều có lúc Result RUNNING. Đó là cửa sổ lệnh thứ hai bị chặn. Phần này có test `test_queued_action_blocks_a_duplicate_auto_job` và `test_cooldown_is_reported_before_a_duplicate`.

Operator vẫn chạy tay. Khi SSH hoặc WinRM lên, drawer giữ dòng Remediation available và câu action can run. Bấm remediate trên alert tạo job `trigger_source=manual`. Auto để MANUAL_REQUIRED là lời gọi người vận hành, không tắt nút đó. Test `test_operator_click_stays_manual`.

Server để maintenance thì alert vẫn lưu, auto không chạy. Em chưa chụp case maintenance trong bộ ảnh này. Test `test_maintenance_still_stores_the_alert_and_skips_auto`.

## Kết quả trên GitHub

Code auto-remediation nằm ở commit `75601e4` trên nhánh `application`. Ảnh và báo cáo tuần 6 nằm ở `application/docs/week06`. Bảng dưới ghi link tree, link file và link commit.

| Kết quả | Commit message | Link | Commit |
| --- | --- | --- | --- |
| Code tuần 6 | Add controlled auto-remediation with cooldown, one retry, and per-incident state. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/tree/75601e49a81e8f4e8cf72a4e6df7ed878b5e3517/application | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/75601e49a81e8f4e8cf72a4e6df7ed878b5e3517 |
| Luồng auto, cooldown, retry, duplicate | Add controlled auto-remediation with cooldown, one retry, and per-incident state. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/75601e49a81e8f4e8cf72a4e6df7ed878b5e3517/application/app/services/remediation.py | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/75601e49a81e8f4e8cf72a4e6df7ed878b5e3517 |
| Ba action an toàn | Add controlled auto-remediation with cooldown, one retry, and per-incident state. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/75601e49a81e8f4e8cf72a4e6df7ed878b5e3517/application/app/executors/actions.py | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/75601e49a81e8f4e8cf72a4e6df7ed878b5e3517 |
| Pre-check SSH và WinRM | Add controlled auto-remediation with cooldown, one retry, and per-incident state. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/75601e49a81e8f4e8cf72a4e6df7ed878b5e3517/application/app/services/checks.py | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/75601e49a81e8f4e8cf72a4e6df7ed878b5e3517 |
| Tạo job, chặn khi kênh down | Add controlled auto-remediation with cooldown, one retry, and per-incident state. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/75601e49a81e8f4e8cf72a4e6df7ed878b5e3517/application/app/services/automation.py | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/75601e49a81e8f4e8cf72a4e6df7ed878b5e3517 |
| Nhãn SUCCESS, BLOCKED, MANUAL_REQUIRED | Add controlled auto-remediation with cooldown, one retry, and per-incident state. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/75601e49a81e8f4e8cf72a4e6df7ed878b5e3517/application/app/presentation.py | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/75601e49a81e8f4e8cf72a4e6df7ed878b5e3517 |
| Job Detail | Add controlled auto-remediation with cooldown, one retry, and per-incident state. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/75601e49a81e8f4e8cf72a4e6df7ed878b5e3517/application/app/templates/automation/detail.html | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/75601e49a81e8f4e8cf72a4e6df7ed878b5e3517 |
| Alert gắn job | Add controlled auto-remediation with cooldown, one retry, and per-incident state. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/75601e49a81e8f4e8cf72a4e6df7ed878b5e3517/application/app/templates/alerts/list.html | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/75601e49a81e8f4e8cf72a4e6df7ed878b5e3517 |
| Bảng incident | Add controlled auto-remediation with cooldown, one retry, and per-incident state. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/75601e49a81e8f4e8cf72a4e6df7ed878b5e3517/application/migrations/versions/d5e7b1c42a90_incidents.py | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/75601e49a81e8f4e8cf72a4e6df7ed878b5e3517 |
| Cooldown 120 giây, retry 1 lần | Add controlled auto-remediation with cooldown, one retry, and per-incident state. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/75601e49a81e8f4e8cf72a4e6df7ed878b5e3517/application/.env.example | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/75601e49a81e8f4e8cf72a4e6df7ed878b5e3517 |
| Test success, failure, cooldown, duplicate | Add controlled auto-remediation with cooldown, one retry, and per-incident state. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/75601e49a81e8f4e8cf72a4e6df7ed878b5e3517/application/tests/test_auto_remediation.py | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/75601e49a81e8f4e8cf72a4e6df7ed878b5e3517 |
| Allow-list playbook tuần 4 | Connect portal jobs to the MON01 Ansible allow-list. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/tree/aecb279c07407ae612b4b9476fec702ddeaa1eaf/application | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/aecb279c07407ae612b4b9476fec702ddeaa1eaf |
| Báo cáo và ảnh tuần 5 | Limit the week 5 AI note to code help. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/tree/9fb0dae6b4e5fbdbcb18c807008d1bf2eca753b2/application/docs/week05 | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/9fb0dae6b4e5fbdbcb18c807008d1bf2eca753b2 |
| Thư mục tuần 6 | Add the week 6 controlled auto-remediation report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/tree/e10dbe17d5d06e81e7d2bcf4b0e4988bdf070942/application/docs/week06 | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/e10dbe17d5d06e81e7d2bcf4b0e4988bdf070942 |
| Báo cáo Word tuần 6 | Add the week 6 controlled auto-remediation report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/e10dbe17d5d06e81e7d2bcf4b0e4988bdf070942/application/docs/week06/week-06-application.docx | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/e10dbe17d5d06e81e7d2bcf4b0e4988bdf070942 |
| WEB01 success | Add the week 6 controlled auto-remediation report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/e10dbe17d5d06e81e7d2bcf4b0e4988bdf070942/application/docs/week06/screenshots/web01-incident1-success.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/e10dbe17d5d06e81e7d2bcf4b0e4988bdf070942 |
| WEB01 cooldown | Add the week 6 controlled auto-remediation report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/e10dbe17d5d06e81e7d2bcf4b0e4988bdf070942/application/docs/week06/screenshots/web01-cooldown-job32.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/e10dbe17d5d06e81e7d2bcf4b0e4988bdf070942 |
| WEB01 execution failed | Add the week 6 controlled auto-remediation report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/e10dbe17d5d06e81e7d2bcf4b0e4988bdf070942/application/docs/week06/screenshots/web01-job34-playbook-failed.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/e10dbe17d5d06e81e7d2bcf4b0e4988bdf070942 |
| WEB01 retry limit | Add the week 6 controlled auto-remediation report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/e10dbe17d5d06e81e7d2bcf4b0e4988bdf070942/application/docs/week06/screenshots/web01-retry-limit-2030.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/e10dbe17d5d06e81e7d2bcf4b0e4988bdf070942 |
| WEB01 SSH blocked | Add the week 6 controlled auto-remediation report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/e10dbe17d5d06e81e7d2bcf4b0e4988bdf070942/application/docs/week06/screenshots/web01-ssh-blocked.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/e10dbe17d5d06e81e7d2bcf4b0e4988bdf070942 |
| WEB01 SSH lên lại | Add the week 6 controlled auto-remediation report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/e10dbe17d5d06e81e7d2bcf4b0e4988bdf070942/application/docs/week06/screenshots/web01-ssh-up-can-run.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/e10dbe17d5d06e81e7d2bcf4b0e4988bdf070942 |
| WEB01 verification failed | Add the week 6 controlled auto-remediation report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/e10dbe17d5d06e81e7d2bcf4b0e4988bdf070942/application/docs/week06/screenshots/web01-verification-failed-2140.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/e10dbe17d5d06e81e7d2bcf4b0e4988bdf070942 |
| APP01 success | Add the week 6 controlled auto-remediation report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/e10dbe17d5d06e81e7d2bcf4b0e4988bdf070942/application/docs/week06/screenshots/app01-incident5-success.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/e10dbe17d5d06e81e7d2bcf4b0e4988bdf070942 |
| APP01 cooldown | Add the week 6 controlled auto-remediation report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/e10dbe17d5d06e81e7d2bcf4b0e4988bdf070942/application/docs/week06/screenshots/app01-cooldown-job39.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/e10dbe17d5d06e81e7d2bcf4b0e4988bdf070942 |
| APP01 retry limit | Add the week 6 controlled auto-remediation report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/e10dbe17d5d06e81e7d2bcf4b0e4988bdf070942/application/docs/week06/screenshots/app01-retry-limit-2055.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/e10dbe17d5d06e81e7d2bcf4b0e4988bdf070942 |
| APP01 SSH blocked | Add the week 6 controlled auto-remediation report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/e10dbe17d5d06e81e7d2bcf4b0e4988bdf070942/application/docs/week06/screenshots/app01-ssh-down-and-app-down.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/e10dbe17d5d06e81e7d2bcf4b0e4988bdf070942 |
| APP01 verification failed | Add the week 6 controlled auto-remediation report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/e10dbe17d5d06e81e7d2bcf4b0e4988bdf070942/application/docs/week06/screenshots/app01-verification-failed.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/e10dbe17d5d06e81e7d2bcf4b0e4988bdf070942 |
| WIN01 success | Add the week 6 controlled auto-remediation report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/e10dbe17d5d06e81e7d2bcf4b0e4988bdf070942/application/docs/week06/screenshots/win01-incident11-success.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/e10dbe17d5d06e81e7d2bcf4b0e4988bdf070942 |
| WIN01 retry limit | Add the week 6 controlled auto-remediation report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/e10dbe17d5d06e81e7d2bcf4b0e4988bdf070942/application/docs/week06/screenshots/win01-retry-limit.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/e10dbe17d5d06e81e7d2bcf4b0e4988bdf070942 |
| WIN01 WinRM down | Add the week 6 controlled auto-remediation report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/e10dbe17d5d06e81e7d2bcf4b0e4988bdf070942/application/docs/week06/screenshots/win01-winrm-down-exporter-up.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/e10dbe17d5d06e81e7d2bcf4b0e4988bdf070942 |
| WIN01 unreachable blocked | Add the week 6 controlled auto-remediation report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/e10dbe17d5d06e81e7d2bcf4b0e4988bdf070942/application/docs/week06/screenshots/win01-unreachable-blocked.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/e10dbe17d5d06e81e7d2bcf4b0e4988bdf070942 |
| WIN01 verification failed | Add the week 6 controlled auto-remediation report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/e10dbe17d5d06e81e7d2bcf4b0e4988bdf070942/application/docs/week06/screenshots/win01-verification-job-result.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/e10dbe17d5d06e81e7d2bcf4b0e4988bdf070942 |

## Luồng đã kiểm tra

- WEB01 Nginx down, SSH up: job 32 SUCCESS, Nginx `:80` up 687 ms, incident 1 đóng.
- WEB01 trong 2 phút sau job 32: cooldown skipped, không có job mới cho đến job 33.
- WEB01 config làm `systemctl restart nginx` fail: job 33 rồi job 34, MANUAL_REQUIRED, reason retry_limit.
- WEB01 incident 4 sau khi incident 2 đã manual: job 35 bắt đầu ở attempt 1.
- WEB01 SSH down: incident 3 và incident 16 BLOCKED, playbook không chạy.
- WEB01 post-check cổng 80 fail: job 48 VERIFICATION_FAILED, một attempt.
- APP01 container down, SSH up: job 37, job 38, job 39 SUCCESS.
- APP01 cooldown job 38 và job 39: skipped, alert vẫn trỏ tới các job SUCCESS.
- APP01 playbook fail: job 40 rồi job 41, MANUAL_REQUIRED.
- APP01 SSH down: incident 9 và incident 17 BLOCKED.
- APP01 post-check fail: incident 10, job 42 và job 43 đều VERIFICATION_FAILED.
- WIN01 exporter down, WinRM up: job 44 SUCCESS, cổng 9182 up 953 ms.
- WIN01 playbook fail: job 45 rồi job 46, MANUAL_REQUIRED.
- WIN01 WinRM down: incident 13 BLOCKED, exporter up thì host Degraded, cả hai down thì Unreachable.
- WIN01 post-check cổng 9182 fail: job 47 VERIFICATION_FAILED, một attempt, incident 14 còn mở.
- Operator: dòng can run còn khi cổng quản trị lên. Job tay dùng trigger manual.

## Ảnh test case

![20:28 WEB01. Incident 1 resolved success. Nginx :80 is up (687 ms). Phía trên còn một dòng Nginx down lúc 20:27, trước khi job 32 verify xong.](screenshots/web01-incident1-success.jpg)

![20:29 WEB01. Auto-remediation skipped vì cooldown. restart_nginx lần cuối là job 32 lúc 20:27. Lần auto sau được phép từ 20:29.](screenshots/web01-cooldown-job32.jpg)

![20:32 WEB01. Job 34, play Recover Nginx, exit code 2, Result MANUAL_REQUIRED, verification Skipped. systemctl restart nginx failed. Retry tạo job mới từ trang job detail.](screenshots/web01-job34-playbook-failed.jpg)

![20:30 WEB01 Nginx down, SSH up. Auto-remediation failed: retry limit. Reason execution failed, playbook failed before verification. Đây là incident 2, job 34.](screenshots/web01-retry-limit-2030.jpg)

![20:38 WEB01 Healthy, SSH up. Incident 4 đã đóng, Nginx :80 is up. Dòng retry limit của restart_nginx vẫn nằm trong log. Lần lỗi sau bắt đầu incident mới.](screenshots/web01-incident4-resolved.jpg)

![20:33 WEB01 Healthy nhưng SSH down. Manual intervention required, reason management_channel_unavailable. BLOCKED. Playbook was not started. Đây là incident 3.](screenshots/web01-ssh-blocked.jpg)

![20:36 WEB01 Healthy, SSH up. Remediation available. Restart Nginx can run. Operator còn đường chạy tay sau khi kênh quản trị lên.](screenshots/web01-ssh-up-can-run.jpg)

![21:41 WEB01 Nginx :80 down, SSH up. 21:40 verification failed. Command completed, post-check port 80 failed, no retry. Job 48, incident 15.](screenshots/web01-verification-failed-2140.jpg)

![20:49 APP01 Healthy. Incident 5 resolved success. Auto-remediation verified: App :8080 is up (532 ms). Job 37.](screenshots/app01-incident5-success.jpg)

![20:54 APP01 App :8080 down, SSH up. Cooldown của job 39, next auto run 20:55. Alert container_down gắn Job 39, Job 38 và Job 37, cả ba SUCCESS.](screenshots/app01-cooldown-job39.jpg)

![20:55 APP01. Manual intervention required, retry limit cho restart_container. Job 40 fail, job 41 là attempt 2. Playbook failed before verification.](screenshots/app01-retry-limit-2055.jpg)

![20:58 APP01 App :8080 down và SSH down. BLOCKED, management channel SSH :22 is down, playbook was not started. Incident 9.](screenshots/app01-ssh-down-and-app-down.jpg)

![20:59 APP01 Healthy, SSH up. Incident 9 resolved. Remediation available, Restart container can run. Có dòng skipped vì service is up.](screenshots/app01-incident9-resolved.jpg)

![21:12 APP01 App :8080 down. 21:11 verification failed, post-check fail, manual required. Phía dưới còn dòng retry limit của restart_container từ incident 8.](screenshots/app01-verification-failed.jpg)

![21:16 APP01. Incident 10 resolved vì service restored. Probe 21:15 vẫn còn dòng App :8080 down. Lần sau retry_count về 0. Job 42 và job 43 đều đã VERIFICATION_FAILED.](screenshots/app01-incident10-resolved.jpg)

![21:17 WIN01 Healthy, WinRM up. Incident 11 resolved success. Windows Exporter :9182 is up (953 ms). Job 44.](screenshots/win01-incident11-success.jpg)

![21:19 WIN01 exporter down, WinRM up. Retry limit cho restart_windows_exporter. Playbook failed before verification. Job 45 và job 46, incident 12.](screenshots/win01-retry-limit.jpg)

![21:23 WIN01 Degraded, WinRM down, exporter :9182 vẫn up. Remediation unavailable, playbook was not started. CPU còn 1.0% nên máy không thành Unreachable.](screenshots/win01-winrm-down-exporter-up.jpg)

![21:23 WIN01 Unreachable khi cả exporter :9182 và WinRM :5985 đều down. BLOCKED, manual required, playbook was not started. Incident 13.](screenshots/win01-unreachable-blocked.jpg)

![21:25 WIN01 Healthy. Incident 13 resolved. WinRM :5985 up, exporter :9182 up, Restart Windows Exporter can run.](screenshots/win01-incident13-resolved.jpg)

![21:26 WIN01. Auto-remediation started restart_windows_exporter. Job 47 RUNNING, trigger WindowsExporterDown.](screenshots/win01-job47-running.jpg)

![21:26 WIN01. job.result: remediation task succeeded, verification task Wait for Windows Exporter port 9182 failed. MANUAL_REQUIRED, không retry tiếp. Incident 14.](screenshots/win01-verification-job-result.jpg)

## Khai báo sử dụng AI

Công cụ: Cursor (Grok), dùng khi viết code.

Mục đích: Nhờ làm auto-remediation có guardrail. Giữ pre-check và post-check. Chỉ auto ba action risk low. Cooldown 2 phút. Retry một lần khi execution failed. Chặn job trùng. Verification failed và management down thì MANUAL_REQUIRED hoặc BLOCKED. Mỗi incident mới reset retry_count. Operator vẫn chạy tay được.

Commit code tuần 6: https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/75601e49a81e8f4e8cf72a4e6df7ed878b5e3517. Commit tuần 5 cho pre-check và verification: https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/a7a65e96e9265517fad7cac7c136f9e1f0825bf4. Commit tuần 5 có trailer Co-authored-by: Cursor <cursoragent@cursor.com>.

AI gợi ý tách incident theo từng lần lỗi, cooldown 120 giây, retry tối đa một lần, và chặn duplicate khi job cùng action đang queued hoặc running. Post-check fail thì dừng ở VERIFICATION_FAILED. Kênh quản trị down thì BLOCKED trước Ansible.

Phần em tự làm: Em gây fault trên WEB01, APP01 và WIN01 tối 4/11, gồm service down, SSH hoặc WinRM down, playbook fail và post-check fail. Em chụp 44 ảnh drawer trên portal và giữ job 32 đến job 48 trong database. Em chịu trách nhiệm về mã nguồn, kết quả test trên lab và nội dung báo cáo này.

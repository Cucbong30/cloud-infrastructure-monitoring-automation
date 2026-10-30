# Báo cáo Tuần 5

Nguyễn Thế Gia Bảo – Application / Integration

## Công việc được phân công

- Từ alert, gợi ý đúng remediation action theo server và service.
- Pre-check trước khi tạo job, để biết target còn quản lý được không.
- Management channel down thì không Execute, ghi lý do blocked, không gọi playbook.
- Sau Ansible phải verification, không nhận Success chỉ vì exit code 0.
- Job Detail đủ server, action, trigger, thời gian, exit code, output và verification.
- Liên kết Alert với Job, và Retry tạo job mới khi job cũ failed.
- Audit thêm `remediation.blocked`, `remediation.verified`, `remediation.failed`.

## Kết quả thực hiện

Tuần này em nối nốt phần xử lý khi remediation không nên chạy, hoặc chạy xong nhưng service chưa thực sự lên. Portal vẫn không tự gọi playbook, vì `AUTO_REMEDIATION_ENABLED` em để `false`. Alert chỉ gợi ý một action trong allow-list. `NginxDown`, `service_down` hoặc `InstanceDown` trên WEB01 thì gợi ý Restart Nginx. `container_down` hoặc `service_down` trên APP01 thì gợi ý Restart container, container cố định là `app01-web`. `WindowsExporterDown`, `service_down` hoặc `InstanceDown` trên WIN01 thì gợi ý Restart Windows Exporter. Operator hoặc admin bấm thì job mới được tạo.

Trước khi tạo job, portal hỏi MON01 cổng điều khiển còn mở không, vì Ansible chạy trên MON01 `192.168.10.10`, không chạy trên laptop. WEB01 kiểm tra SSH `192.168.10.11` cổng 22. APP01 kiểm tra SSH `192.168.10.12` cổng 22. WIN01 kiểm tra WinRM `192.168.10.13` cổng 5985. Trạng thái này hiện riêng, dạng SSH UP, SSH DOWN, WinRM UP hoặc WinRM DOWN. SSH tắt không kéo WEB01 hay APP01 thành Unreachable. Hai máy vẫn Healthy nếu Node Exporter và dịch vụ còn UP. WIN01 khác một chỗ: WinRM vừa là đường Ansible vừa là service check, nên Windows Exporter còn UP mà WinRM tắt thì host là Degraded, không phải Unreachable.

Cổng down thì không tạo execution job và không gọi `ansible-playbook`. Portal hiện Remediation unavailable, reason kiểu `APP01 management channel SSH :22 is down`, và nói playbook was not started. Audit ghi `remediation.blocked`. Cổng lên lại thì có một dòng mới, Remediation available, action đó chạy được. Dòng cũ không bị sửa. Mỗi lần tắt hoặc bật có giờ của lần đó.

Tối 23/10, khoảng 21:20, em gặp lỗi cần giữ trong báo cáo. APP01 lúc đó vẫn Healthy, Node Exporter `:9100` và App `:8080` đều UP, nhưng SSH từ MON01 không tới `192.168.10.12`. Portal chưa chặn nên vẫn tạo job `restart_container`. Ansible fail ở tầng kết nối: `No route to host`, recap `unreachable=1`, `failed=0`. Đó là job vô ích. Em không xóa.

Tối 30/10 em tắt SSH trên APP01 trong lúc exporter và ứng dụng còn chạy. Portal vẫn để APP01 Healthy, hiện SSH DOWN, và chặn `restart_container` trước khi gọi Ansible. Log ghi 20:53 SSH up, Remediation available, rồi 20:54 SSH down, Remediation unavailable. Em bật SSH lại lúc 21:02 thì dòng mới nói Restart container can run. Em chạy thử, được job 20 lúc 21:09, năm giây, exit code 0, verification Passed, chi tiết `App :8080 is up (250 ms)`. Audit có `job.request`, `remediation.verified` và `job.result` status succeeded. Stderr chỉ cảnh báo laptop không mở được `/home/bong/.ssh/id_ed25519`. Cảnh báo đó không làm job fail, vì MON01 vẫn chạy playbook.

Cùng tối em tắt WinRM trên WIN01. Windows Exporter còn sống nên máy không thành Unreachable. Portal ghi Degraded, WinRM DOWN, Remediation unavailable, action `restart_windows_exporter`, playbook was not started. Bật WinRM lại thì host về Healthy và dòng sau nói Restart Windows Exporter can run.

WEB01 em làm cùng quy tắc với `restart_nginx`. Alert NginxDown số 8 đang firing thì gợi ý Restart Nginx và gắn job. Job 18 có trigger remediation từ alert đó, result Blocked, exit code trống vì playbook không chạy, reason `WEB01 management channel SSH :22 is down`. Audit của job có `job.result`, `remediation.blocked` và `job.request`. Em bấm Retry. Portal tạo job 19, không sửa job 18. Lúc retry cổng vẫn down nên job 19 cũng Blocked.

Em tách service down khỏi management down. App `:8080` tắt mà exporter còn UP thì APP01 là Degraded. Nếu cùng lúc SSH cũng tắt, log có cả probe `App :8080 is DOWN` và dòng Remediation unavailable. Hai việc này không bị gộp thành một câu Unreachable.

Job Detail em để server, action, trigger, giờ bắt đầu, giờ kết thúc, thời lượng, exit code, stdout, stderr và verification. Success chỉ khi post-check thấy service lên. Exit code 0 mà dịch vụ không trả lời thì là Verification Failed, audit `remediation.failed`, không phải Success. Ảnh ngày 28/10 còn chữ UTC+7. Portal hiện tại chỉ hiện giờ đã cộng bảy tiếng, không in hậu tố đó.

## Kết quả trên GitHub

Code pre-check và verification nằm trên nhánh `application`. Ảnh và báo cáo tuần 5 nằm ở `application/docs/week05/`.

| Kết quả | Commit message | Link | Commit |
| --- | --- | --- | --- |
| Code tuần 5 | Block remediation when SSH or WinRM is down, then verify the service actually returned. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/tree/a7a65e96e9265517fad7cac7c136f9e1f0825bf4/application | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/a7a65e96e9265517fad7cac7c136f9e1f0825bf4 |
| Pre-check SSH và WinRM | Probe the management port from MON01 and refuse when it is down. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/a7a65e96e9265517fad7cac7c136f9e1f0825bf4/application/app/services/checks.py | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/a7a65e96e9265517fad7cac7c136f9e1f0825bf4 |
| Không tạo job khi kênh down | Block before enqueue, then verify the service after Ansible. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/a7a65e96e9265517fad7cac7c136f9e1f0825bf4/application/app/services/automation.py | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/a7a65e96e9265517fad7cac7c136f9e1f0825bf4 |
| Hỏi cổng từ MON01 | Open the allow-listed management port from 192.168.10.10. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/a7a65e96e9265517fad7cac7c136f9e1f0825bf4/application/app/executors/ansible.py | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/a7a65e96e9265517fad7cac7c136f9e1f0825bf4 |
| Log up và down | Record a new line each time a check changes. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/a7a65e96e9265517fad7cac7c136f9e1f0825bf4/application/app/services/checklog.py | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/a7a65e96e9265517fad7cac7c136f9e1f0825bf4 |
| Gợi ý action | Map each alert to one allow-listed remediation. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/a7a65e96e9265517fad7cac7c136f9e1f0825bf4/application/app/services/remediation.py | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/a7a65e96e9265517fad7cac7c136f9e1f0825bf4 |
| Nhãn Success, Failed, Blocked | Label the job from verification, not from the exit code alone. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/a7a65e96e9265517fad7cac7c136f9e1f0825bf4/application/app/presentation.py | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/a7a65e96e9265517fad7cac7c136f9e1f0825bf4 |
| Job Detail | Show server, action, trigger, output, exit code and verification. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/a7a65e96e9265517fad7cac7c136f9e1f0825bf4/application/app/templates/automation/detail.html | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/a7a65e96e9265517fad7cac7c136f9e1f0825bf4 |
| Alert gắn job | Suggested action, blocked notice, and links to the jobs. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/a7a65e96e9265517fad7cac7c136f9e1f0825bf4/application/app/templates/alerts/list.html | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/a7a65e96e9265517fad7cac7c136f9e1f0825bf4 |
| Cột verification và retry | Store stderr, verification, block reason and retry_of_job_id. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/a7a65e96e9265517fad7cac7c136f9e1f0825bf4/application/migrations/versions/b7e2a91c4d08_job_verification_and_retry.py | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/a7a65e96e9265517fad7cac7c136f9e1f0825bf4 |
| Test chặn SSH | SSH down does not create a job and does not start the playbook. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/a7a65e96e9265517fad7cac7c136f9e1f0825bf4/application/tests/test_automation.py | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/a7a65e96e9265517fad7cac7c136f9e1f0825bf4 |
| Test log up/down | A return to up writes a new check line. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/a7a65e96e9265517fad7cac7c136f9e1f0825bf4/application/tests/test_checklog.py | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/a7a65e96e9265517fad7cac7c136f9e1f0825bf4 |
| Allow-list tuần 4 | Connect portal jobs to the MON01 Ansible allow-list. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/tree/aecb279c07407ae612b4b9476fec702ddeaa1eaf/application | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/aecb279c07407ae612b4b9476fec702ddeaa1eaf |
| Ảnh ba job tuần 4 | Add the week 4 jobs report, AI note, and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/64b6de060eb31a7b09230cf36afa0e88b6673969/application/docs/week04/screenshots/02-three-playbooks-success.png | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/64b6de060eb31a7b09230cf36afa0e88b6673969 |
| Thư mục tuần 5 | Add the week 5 failure-handling report and lab screenshots. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/tree/695b0c7635ecd46a49130311933ec64f25560d23/application/docs/week05 | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/695b0c7635ecd46a49130311933ec64f25560d23 |
| Lỗi 23/10 giữ lại | APP01 Healthy, restart_container already ran, No route to host. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/695b0c7635ecd46a49130311933ec64f25560d23/application/docs/week05/screenshots/08-app01-bug-no-precheck.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/695b0c7635ecd46a49130311933ec64f25560d23 |
| APP01 Healthy, SSH DOWN | Remediation unavailable, playbook was not started. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/695b0c7635ecd46a49130311933ec64f25560d23/application/docs/week05/screenshots/09-app01-healthy-ssh-down.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/695b0c7635ecd46a49130311933ec64f25560d23 |
| SSH APP01 lên lại | Remediation available, Restart container can run. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/695b0c7635ecd46a49130311933ec64f25560d23/application/docs/week05/screenshots/11-app01-ssh-restored.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/695b0c7635ecd46a49130311933ec64f25560d23 |
| Job 20 Success | Verification Passed, App :8080 is up. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/695b0c7635ecd46a49130311933ec64f25560d23/application/docs/week05/screenshots/12-job20-verification-success.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/695b0c7635ecd46a49130311933ec64f25560d23 |
| Audit job 20 | remediation.verified. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/695b0c7635ecd46a49130311933ec64f25560d23/application/docs/week05/screenshots/15-job20-audit-verified.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/695b0c7635ecd46a49130311933ec64f25560d23 |
| WIN01 WinRM down | Host Degraded, remediation unavailable. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/695b0c7635ecd46a49130311933ec64f25560d23/application/docs/week05/screenshots/10-win01-degraded-winrm-down.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/695b0c7635ecd46a49130311933ec64f25560d23 |
| WIN01 WinRM lên lại | WinRM UP, Restart Windows Exporter can run. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/695b0c7635ecd46a49130311933ec64f25560d23/application/docs/week05/screenshots/13-win01-winrm-restored.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/695b0c7635ecd46a49130311933ec64f25560d23 |
| App down và SSH down | Two separate log lines. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/695b0c7635ecd46a49130311933ec64f25560d23/application/docs/week05/screenshots/14-app01-degraded-app-and-ssh.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/695b0c7635ecd46a49130311933ec64f25560d23 |
| WEB01 blocked | remediation.blocked for restart_nginx. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/695b0c7635ecd46a49130311933ec64f25560d23/application/docs/week05/screenshots/16-web01-blocked-audit.jpg | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/695b0c7635ecd46a49130311933ec64f25560d23 |
| Alert gắn job | NginxDown linked to job 18 and job 19. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/695b0c7635ecd46a49130311933ec64f25560d23/application/docs/week05/screenshots/05-alert-job-link.png | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/695b0c7635ecd46a49130311933ec64f25560d23 |
| Job Detail blocked | Job 18 blocked, exit code empty. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/695b0c7635ecd46a49130311933ec64f25560d23/application/docs/week05/screenshots/02-blocked-job-detail.png | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/695b0c7635ecd46a49130311933ec64f25560d23 |
| Retry thành job mới | Job 19 retries job 18. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/695b0c7635ecd46a49130311933ec64f25560d23/application/docs/week05/screenshots/04-retry-new-job.png | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/695b0c7635ecd46a49130311933ec64f25560d23 |
| Audit job 18 | job.result, remediation.blocked, job.request. | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/695b0c7635ecd46a49130311933ec64f25560d23/application/docs/week05/screenshots/03-audit-blocked.png | https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/695b0c7635ecd46a49130311933ec64f25560d23 |

## Luồng đã kiểm tra

- APP01 còn Healthy, SSH `:22` down: không gọi `restart_container`, audit `remediation.blocked`, reason `APP01 management channel SSH :22 is down`.
- APP01 SSH lên lại: job 20 Success, exit code 0, verification Passed vì App `:8080` is up.
- WIN01 Windows Exporter còn UP, WinRM `:5985` down: host Degraded, remediation unavailable.
- WEB01 NginxDown: job 18 Blocked. Retry tạo job 19, không sửa job 18.
- Job 23/10 21:20 được giữ: APP01 Healthy nhưng Ansible đã chạy và `No route to host`.

## Ảnh test case

- [Lỗi 23/10 giữ lại](screenshots/08-app01-bug-no-precheck.jpg). APP01 Healthy nhưng `restart_container` đã chạy và UNREACHABLE.
- [APP01 Healthy, SSH DOWN](screenshots/09-app01-healthy-ssh-down.jpg). Có cả lần SSH up và lần SSH down, kèm câu remediation.
- [SSH APP01 lên lại](screenshots/11-app01-ssh-restored.jpg). Remediation available, Restart container can run.
- [Job 20 Success](screenshots/12-job20-verification-success.jpg). Verification Passed, App `:8080` is up.
- [Audit job 20](screenshots/15-job20-audit-verified.jpg). `remediation.verified`, stdout và stderr.
- [WIN01 Degraded, WinRM down](screenshots/10-win01-degraded-winrm-down.jpg).
- [WIN01 WinRM lên lại](screenshots/13-win01-winrm-restored.jpg).
- [App down và SSH down là hai dòng](screenshots/14-app01-degraded-app-and-ssh.jpg).
- [WEB01 remediation.blocked](screenshots/16-web01-blocked-audit.jpg).
- [Alert gắn job](screenshots/05-alert-job-link.png).
- [Job Detail blocked](screenshots/02-blocked-job-detail.png).
- [Retry thành job mới](screenshots/04-retry-new-job.png).
- [Audit job 18](screenshots/03-audit-blocked.png).

## Khai báo sử dụng AI

Xem [ai-usage.md](ai-usage.md).

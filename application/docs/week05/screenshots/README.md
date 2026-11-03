# Ảnh test case tuần 5

Ảnh do em chụp trên portal lab. Giờ trong ảnh mới là giờ đã cộng bảy tiếng. Ảnh ngày 28/10 còn in chữ UTC+7.

| File | Nội dung |
| --- | --- |
| `08-app01-bug-no-precheck.jpg` | 23/10 21:20. APP01 Healthy nhưng job `restart_container` đã chạy. Ansible `No route to host`, `unreachable=1`. Job được giữ. |
| `09-app01-healthy-ssh-down.jpg` | 30/10 21:01. APP01 Healthy, SSH DOWN. 20:54 Remediation unavailable. 20:53 Remediation available. |
| `11-app01-ssh-restored.jpg` | 30/10 21:02. SSH UP lại. Restart container can run. |
| `12-job20-verification-success.jpg` | Job 20 Success, exit code 0, verification Passed, App `:8080` is up (250 ms). |
| `15-job20-audit-verified.jpg` | Stdout playbook, stderr cảnh báo key, audit `remediation.verified`. |
| `10-win01-degraded-winrm-down.jpg` | WIN01 Degraded, WinRM DOWN, playbook was not started. |
| `13-win01-winrm-restored.jpg` | WIN01 Healthy, WinRM UP, Restart Windows Exporter can run. |
| `14-app01-degraded-app-and-ssh.jpg` | App `:8080` DOWN và SSH DOWN là hai dòng riêng. Host Degraded. |
| `16-web01-blocked-audit.jpg` | WEB01 Healthy. Audit `remediation.blocked` và job `restart_nginx` failed. |
| `05-alert-job-link.png` | NginxDown gợi ý Restart Nginx, gắn Job 18 và Job 19. |
| `02-blocked-job-detail.png` | Job 18, trigger remediation từ alert #8, Result Blocked. |
| `04-retry-new-job.png` | Job 19 là retry của job 18. Job cũ không bị sửa. |
| `03-audit-blocked.png` | `job.result`, `remediation.blocked`, `job.request`. |
| `01-management-blocked.png` | 28/10. Ba thông báo chặn APP01, WEB01 và WIN01. |

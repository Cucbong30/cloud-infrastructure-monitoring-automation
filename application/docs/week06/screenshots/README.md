# Ảnh test case tuần 6

Ảnh do em chụp trên portal lab tối 4/11, drawer của WEB01, APP01 và WIN01. Giờ trong ảnh là giờ đã cộng bảy tiếng. Bộ zip có 44 khung. Nhiều khung là cùng một drawer kéo lên hoặc xuống. Báo cáo Word nhúng mỗi loại một ảnh. Thư mục này giữ đủ các khung.

| File | Nội dung |
| --- | --- |
| `app01-blocked-audit.jpg` | BLOCKED, management channel unavailable, playbook was not started. |
| `app01-cooldown-job38.jpg` | Cooldown job 38. Next auto run 20:52. Alert gắn job 38 và job 37. |
| `app01-cooldown-job39.jpg` | Cooldown job 39. Alert gắn job 39, job 38, job 37 SUCCESS. |
| `app01-down-2039.jpg` | 20:39 App down. Drawer còn dòng audit của lần lỗi trước. |
| `app01-execution-failed-detail.jpg` | Retry limit và execution failed trên cùng drawer. |
| `app01-execution-failed-job-result.jpg` | job.result Playbook failed before verification. |
| `app01-incident10-resolved.jpg` | Incident 10 đóng vì service restored. Retry_count lần sau về 0. |
| `app01-incident5-success.jpg` | Incident 5 success. App :8080 up 532 ms. Job 37. |
| `app01-incident7-success.jpg` | Incident 7 success. App :8080 up 546 ms. Job 39. |
| `app01-incident8-resolved.jpg` | Incident 8 đóng. App :8080 up. Dòng retry limit còn trong log. |
| `app01-incident9-resolved.jpg` | Incident 9 đóng. App up, SSH up. |
| `app01-job42-running.jpg` | Job 42 RUNNING, restart_container, incident 10. |
| `app01-retry-limit-2055.jpg` | Incident 8. Job 40 rồi job 41, retry limit. |
| `app01-service-up-skip.jpg` | Skipped vì service is up. SSH up, Restart container can run. |
| `app01-ssh-down-and-app-down.jpg` | App down và SSH down. Incident 9 BLOCKED. |
| `app01-ssh-down-app-up.jpg` | App up, SSH down. Remediation unavailable. Incident 8 đã đóng. |
| `app01-verification-failed.jpg` | 21:11 verification failed. Manual required. Không retry tiếp theo kiểu post-check. |
| `web01-cooldown-job32.jpg` | Cooldown. Job 32 lúc 20:27, lần auto sau từ 20:29. |
| `web01-incident1-success-while-down.jpg` | WEB01 drawer vẫn đề Nginx down. Bên dưới là incident 1 success. |
| `web01-incident1-success.jpg` | WEB01 Healthy. Incident 1 success. Nginx :80 up 687 ms. Job 32. |
| `web01-incident2-resolved.jpg` | Incident 2 đóng vì service restored. Nginx up, còn dòng retry limit. |
| `web01-incident3-resolved-ssh-down.jpg` | Nginx up lại trong khi SSH vẫn down. Incident 3 đóng. |
| `web01-incident4-resolved.jpg` | Incident 4 đóng. Nginx up. |
| `web01-incident4-retry-limit.jpg` | Incident 4 tới retry limit. Attempt bắt đầu lại từ 1. |
| `web01-job34-playbook-failed.jpg` | Job 34 exit code 2, MANUAL_REQUIRED, play Recover Nginx. |
| `web01-job36-running.jpg` | Job 36 RUNNING, incident 4, attempt mới sau incident 2. |
| `web01-nginx-down-2000.jpg` | 20:00 Nginx down. Dòng retry limit cũ và SSH vẫn up. |
| `web01-retry-limit-2030.jpg` | Incident 2, retry limit, playbook failed before verification. |
| `web01-ssh-blocked.jpg` | SSH down. BLOCKED, playbook was not started. Incident 3. |
| `web01-ssh-up-can-run.jpg` | SSH up. Restart Nginx can run. |
| `web01-verification-failed-2140.jpg` | 21:40 post-check cổng 80 fail. Job 48, không có attempt 2. |
| `win01-down-after-incident12.jpg` | Incident 12 đã đóng, probe mới ghi exporter down. |
| `win01-incident11-success.jpg` | WIN01 Healthy. Incident 11 success. Job 44. |
| `win01-incident12-resolved.jpg` | Exporter up. Incident 12 đóng, retry_count lần sau về 0. |
| `win01-incident13-resolved.jpg` | Incident 13 đóng. WinRM up, exporter up, action can run. |
| `win01-job47-running.jpg` | Job 47 RUNNING, restart_windows_exporter. |
| `win01-playbook-failed.jpg` | job.result Playbook failed before verification. Incident 12. |
| `win01-retry-limit.jpg` | Job 45 rồi job 46. MANUAL_REQUIRED, retry limit. |
| `win01-success-while-down.jpg` | Drawer còn đề exporter down. Bên dưới incident 11 success, 953 ms. |
| `win01-unreachable-blocked.jpg` | Cả exporter và WinRM down. Unreachable, BLOCKED. Incident 13. |
| `win01-verification-failed.jpg` | VERIFICATION_FAILED, no retry. Incident 14. |
| `win01-verification-job-result.jpg` | Wait for Windows Exporter port 9182 failed. Job 47. |
| `win01-verification-manual.jpg` | Manual intervention required sau post-check cổng 9182. |
| `win01-winrm-down-exporter-up.jpg` | WinRM down, exporter up. Host Degraded. Playbook không chạy. |

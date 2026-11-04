# Báo cáo Application — Tuần 6

Nguyễn Thế Gia Bảo – Application / Integration

Trạng thái: Portal tự chạy ba action risk low, có pre-check, post-check, cooldown 2 phút, retry một lần, chặn job trùng, và vẫn để operator chạy tay. Evidence lab tối 4/11 nằm ở `application/docs/week06/`.

## Công việc được phân công

- Giữ management pre-check và post-check.
- Auto `restart_nginx`, `restart_container`, `restart_windows_exporter`.
- Cooldown, giới hạn retry, chặn duplicate job.
- Success, execution failed, blocked, verification failed.
- Manual remediation cho operator.

## Kết quả thực hiện

1. **WEB01.** Job 32 SUCCESS. Job 33 rồi job 34 tới MANUAL_REQUIRED. Incident 3 BLOCKED khi SSH down. Job 48 VERIFICATION_FAILED, một attempt.
2. **APP01.** Job 37, job 38, job 39 SUCCESS. Cooldown chặn alert lặp. Job 40 rồi job 41 tới retry limit. Incident 9 BLOCKED khi SSH down. Incident 10 có job 42 và job 43, cả hai VERIFICATION_FAILED.
3. **WIN01.** Job 44 SUCCESS. Job 45 rồi job 46 tới retry limit. Incident 13 BLOCKED khi WinRM down. Job 47 VERIFICATION_FAILED, incident 14 còn mở.
4. **Incident mới.** Mỗi lần resolved, drawer ghi next failure starts a new incident at retry_count 0.
5. **Chạy tay.** Dòng Remediation available còn khi SSH hoặc WinRM lên.

Báo cáo: [week-06-application.md](week-06-application.md). Bản Word: [week-06-application.docx](week-06-application.docx). Khai báo AI: [ai-usage.md](ai-usage.md).

## Kết quả trên GitHub

| Kết quả | Link | Commit |
| --- | --- | --- |
| Pre-check tuần 5 | [checks.py](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/a7a65e96e9265517fad7cac7c136f9e1f0825bf4/application/app/services/checks.py) | [a7a65e9](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/a7a65e96e9265517fad7cac7c136f9e1f0825bf4) |
| Allow-list tuần 4 | [aecb279](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/aecb279c07407ae612b4b9476fec702ddeaa1eaf) | cùng link |
| Báo cáo tuần 5 | [week05](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/tree/9fb0dae6b4e5fbdbcb18c807008d1bf2eca753b2/application/docs/week05) | [9fb0dae](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/9fb0dae6b4e5fbdbcb18c807008d1bf2eca753b2) |
| Code tuần 6 | [75601e4](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/75601e49a81e8f4e8cf72a4e6df7ed878b5e3517) | cùng link |
| Ảnh và báo cáo tuần 6 | [week06](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/tree/e10dbe17d5d06e81e7d2bcf4b0e4988bdf070942/application/docs/week06) | [e10dbe1](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/e10dbe17d5d06e81e7d2bcf4b0e4988bdf070942) |

## Ảnh

Xem [screenshots/README.md](screenshots/README.md).

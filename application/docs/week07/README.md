# Báo cáo Application — Tuần 7

Nguyễn Thế Gia Bảo – Application / Integration

Trạng thái: Portal đăng nhập bằng Microsoft Entra, role lấy từ App Role. Mail đi qua Graph tới ba distribution group. AZURE01 chạy policy tuần 6. Evidence lab tối 5/11 và tối 6/11 nằm ở `application/docs/week07/`.

## Công việc được phân công

- SSO Entra. Admin, Operator, Viewer không gán trên portal.
- Mail Graph. Critical, Warning, Info đi ba nhóm khác nhau.
- AZURE01 Cloud, `restart_nginx`, cooldown, retry, blocked, manual.
- Docker. `.env` không vào image.

## Kết quả thực hiện

1. **SSO.** `ntgbao@cucbong.id.vn` vào với role admin. Trang Users chỉ đọc role từ token.
2. **AZURE01 success.** Job 53 và job 54 SUCCESS. Cooldown 2 phút. Nginx `:80` up 202 ms ở incident 22.
3. **Execution failed.** Job 55 rồi job 56 tới MANUAL_REQUIRED, reason retry_limit. Incident 23 đóng 23:04.
4. **SSH down.** Incident 24 BLOCKED, không có job playbook. SSH lên thì Restart Nginx can run.
5. **Verification failed.** Job 57 và job 59, mỗi incident một attempt. Mail tối 6/11 của incident 30 đi đúng nhóm.
6. **Docker.** Có Dockerfile và `.dockerignore`. Chưa có ảnh `docker ps`.

Báo cáo: [week-07-application.md](week-07-application.md). Bản Word: [week-07-application.docx](week-07-application.docx). Khai báo AI: [ai-usage.md](ai-usage.md).

## Kết quả trên GitHub

| Kết quả | Link | Commit |
| --- | --- | --- |
| Code tuần 7 | [c13696e](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/c13696e4d637f098e2b3806b7f92937bf43ddf79) | cùng link |
| Policy tuần 6 | [75601e4](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/75601e49a81e8f4e8cf72a4e6df7ed878b5e3517) | cùng link |
| Báo cáo tuần 6 | [week06](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/tree/e10dbe17d5d06e81e7d2bcf4b0e4988bdf070942/application/docs/week06) | [e10dbe1](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/e10dbe17d5d06e81e7d2bcf4b0e4988bdf070942) |
| Ảnh và báo cáo tuần 7 | [week07](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/tree/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7/application/docs/week07) | [d2ac3919e00f6afc05b9d05f66a37e31ff5739e7](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/d2ac3919e00f6afc05b9d05f66a37e31ff5739e7) |

## Ảnh

Xem [screenshots/README.md](screenshots/README.md).

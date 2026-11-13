# Báo cáo Application — Tuần 8

Nguyễn Thế Gia Bảo – Application / Integration

Trạng thái: Admin và Operator chạy được Manual Remediation. Viewer bị chặn. Audit ghi actor và mode. Job trùng thành DUPLICATE_SKIPPED. Mail Execution Failed, Retry và Blocked đi đúng nhóm. Key SSH của AZURE01 nằm trong inventory Ansible, không nằm trong portal. Evidence tối 13/11 ở `application/docs/week08/`.

## Công việc được phân công

- RBAC cho manual remediation.
- Audit MANUAL và AUTO.
- Duplicate, retry một lần, management blocked.
- Không hardcode key AZURE01 trong portal.

## Kết quả thực hiện

1. **Admin.** Job 64, WEB01, MANUAL, SUCCESS. Actor `ntgbao@cucbong.id.vn`.
2. **Operator.** Job 65 và job 66, WEB01, MANUAL, SUCCESS. Audit job 66 đủ field.
3. **Viewer.** Trang Jobs ghi manual remediation is not available for this role.
4. **AZURE01.** Job 71 và job 72 SUCCESS sau khi inventory dùng đúng key. Job 74 fail ở `systemctl restart nginx`. Không có ảnh job 71 và job 72.
5. **Duplicate.** Job 67 DUPLICATE_SKIPPED, execution không chạy, active job 60.
6. **Mail.** Execution Failed tới Critical. Retry và Blocked tới Warning.

Báo cáo: [week-08-application.md](week-08-application.md). Bản Word: [week-08-application.docx](week-08-application.docx). Khai báo AI: [ai-usage.md](ai-usage.md).

## Kết quả trên GitHub

| Kết quả | Link | Commit |
| --- | --- | --- |
| Code tuần 8 | [4960f04](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/4960f041ed12294b595016e993720ba209fd6bf8) | cùng link |
| Code tuần 7 | [c13696e](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/c13696e4d637f098e2b3806b7f92937bf43ddf79) | cùng link |
| Báo cáo tuần 7 | [week07](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/tree/549e99beb6f001dab55d567aeccfb7544779d4a3/application/docs/week07) | [549e99b](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/549e99beb6f001dab55d567aeccfb7544779d4a3) |
| Ảnh và báo cáo tuần 8 | [week08](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/tree/__DOCS_SHA__/application/docs/week08) | [__DOCS_SHA__](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/__DOCS_SHA__) |

## Ảnh

Xem [screenshots/README.md](screenshots/README.md).

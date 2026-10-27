# Báo cáo Application — Tuần 4

Nguyễn Thế Gia Bảo – Application / Integration

Trạng thái: Jobs module đã nối Ansible trên MON01. Ba playbook allow-list đã chạy trên lab và trả HTTP 200. Evidence nằm trên nhánh `application`, thư mục `application/docs/week04/`. Không đẩy phần này lên nhánh `infra`.

## Công việc được phân công

- Kết nối Portal với Ansible execution.
- Hoàn thiện Jobs module.
- Lưu execution history.
- Hiển thị automation result.
- Kết nối alert với remediation action.
- Hoàn thiện Audit Log cho automation.

## Kết quả thực hiện

1. **Ansible controller.** Laptop SSH sang MON01 `192.168.10.10`. Ba action: `restart_nginx` trên WEB01 `192.168.10.11`, `restart_container` (`app01-web`) trên APP01 `192.168.10.12`, `restart_windows_exporter` trên WIN01 `192.168.10.13`.
2. **Allow-list.** Playbook path cố định trên MON01. Form không gửi lệnh hay path. `restart_service` và `disk_cleanup` đã gỡ.
3. **Jobs.** Server, action, Execute. Nhãn Pending, Running, Success, Failed. Lưu giờ, server, action, result, output. Giờ UTC+7.
4. **Ba flow lab, 23/10/2026.** WEB01 Nginx HTTP 200 lúc 21:08 UTC+7. APP01 container HTTP 200 lúc 21:14 UTC+7. WIN01 Windows Exporter HTTP 200 lúc 21:16 UTC+7.
5. **Fail closed.** User trống, key không mở được, hoặc `No route to host` thì job Failed. Portal vẫn mở. Audit có `job.request` và `job.result`.
6. **Unreachable.** Exporter và dịch vụ cùng DOWN thì không hiện nút restart, chỉ một thông báo.
7. **Remediation.** Nút trên Alert và Server Detail. `AUTO_REMEDIATION_ENABLED=false`, không tự chạy.

Báo cáo: [week-04-application.md](week-04-application.md). Khai báo AI: [ai-usage.md](ai-usage.md).

## Kết quả trên GitHub

| Kết quả | Link | Commit |
| --- | --- | --- |
| Code Jobs / Ansible | [application/](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/tree/aecb279c07407ae612b4b9476fec702ddeaa1eaf/application) | [aecb279](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/aecb279c07407ae612b4b9476fec702ddeaa1eaf) |
| Executor | [ansible.py](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/blob/aecb279c07407ae612b4b9476fec702ddeaa1eaf/application/app/executors/ansible.py) | cùng commit |
| Ảnh test case | [screenshots](screenshots) | [64b6de0](https://github.com/Cucbong30/cloud-infrastructure-monitoring-automation/commit/64b6de060eb31a7b09230cf36afa0e88b6673969) |

## Ảnh

- [Ba playbook Success](screenshots/02-three-playbooks-success.png)
- [Target Unreachable](screenshots/03-playbook-unreachable-failed.png)
- [Không hiện nút restart](screenshots/01-unreachable-instead-of-restart.png)
- [WEB01 Server Detail](screenshots/04-web01-server-detail.png)
- [Audit Log](screenshots/05-audit-job-events.png)

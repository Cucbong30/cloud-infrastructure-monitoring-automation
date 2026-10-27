# Cấu hình tuần 4

File mẫu: [portal.env.example](portal.env.example).

Biến mới so với tuần 3:

- `AUTOMATION_EXECUTOR=ansible` trên lab. Test pytest vẫn dùng mock.
- `ANSIBLE_CONTROLLER_HOST`, `ANSIBLE_CONTROLLER_USER`, `ANSIBLE_CONTROLLER_KEY`, `ANSIBLE_TIMEOUT_SECONDS`.
- `AUTO_REMEDIATION_ENABLED=false`.

Không commit file `.env` thật.

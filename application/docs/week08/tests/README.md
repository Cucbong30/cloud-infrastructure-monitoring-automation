# Test tuần 8

Lab tối 13/11 nằm trong báo cáo và thư mục `screenshots`. Test tự động nằm ở `application/tests/test_week8.py` và `application/tests/test_automation.py`.

- `test_viewer_cannot_trigger_and_the_denial_is_audited`
- `test_admin_and_operator_see_the_manual_form`
- `test_manual_success_records_mode_actor_and_info_mail`
- `test_active_job_skips_the_duplicate_without_running`
- `test_manual_verification_failure_does_not_retry`
- `test_manual_failure_blocked_and_retry_mails`
- `test_manual_execution_failure_does_not_retry`
- `test_manual_management_block_does_not_run_the_playbook`
- `test_auto_audit_keeps_system_actor`
- Test playbook gọi `ansible-playbook -i /etc/ansible/hosts` và không đưa `azure01_ed25519` vào lệnh portal.

Ảnh không có trang 403. Ảnh không có drawer SUCCESS của job 71 và job 72.

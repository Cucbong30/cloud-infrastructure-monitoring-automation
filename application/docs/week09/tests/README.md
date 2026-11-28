# Test tuần 9

Lab tối 20/11 nằm trong báo cáo và thư mục `screenshots`. Test tự động nằm ở `application/tests/test_week9.py`.

- `test_low_action_still_runs_without_approval`
- `test_medium_approval_runs_only_after_it_is_approved`
- `test_rejected_request_does_not_call_the_playbook`
- `test_operator_cannot_request_or_approve_a_high_risk_action`
- `test_expired_approval_is_not_executed`
- `test_viewer_cannot_approve`
- `test_direct_dispatch_cannot_skip_approval`
- `test_audit_log_filters_by_date`

Bộ ảnh không có trang 403. 403 của Operator khi request HIGH nằm ở test. Bộ ảnh không có drawer job 71 và job 72.

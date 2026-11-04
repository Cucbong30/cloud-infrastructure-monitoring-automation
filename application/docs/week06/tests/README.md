# Test tuần 6

Lab tối 4/11 nằm trong báo cáo và thư mục `screenshots`. Test tự động nằm ở `application/tests/test_auto_remediation.py`.

- `test_each_target_auto_success_records_the_audit`
- `test_each_target_execution_failure_ends_manual`
- `test_each_target_blocks_before_the_playbook`
- `test_each_target_verification_failure_does_not_retry`
- `test_repeat_firing_during_cooldown_does_not_create_a_job`
- `test_queued_action_blocks_a_duplicate_auto_job`
- `test_cooldown_is_reported_before_a_duplicate`
- `test_new_incident_starts_at_zero_after_manual_required`
- `test_operator_click_stays_manual`
- `test_maintenance_still_stores_the_alert_and_skips_auto`
- `test_capacity_alert_stays_diagnostic`
- `test_risky_actions_are_rejected`
- `test_production_playbooks_stay_on_the_lab_targets`

# Test tuần 10

Lab 28/11 nằm trong báo cáo và thư mục `screenshots`. Test tự động nằm ở `application/tests/test_week10.py`.

- `test_production_playbooks_and_timeouts_stay_on_the_lab_map`
- `test_failure_playbooks_are_classified_by_task_not_exit_code`
- `test_http_403_is_not_recovery`
- `test_active_incident_is_reused_until_it_is_closed`
- `test_acknowledge_rejects_an_illegal_status`
- `test_incident_page_requests_approval_and_keeps_the_job_waiting`
- `test_incident_detail_preselects_container_or_docker_from_the_cause`
- `test_medium_approval_links_one_incident_and_one_job`
- `test_known_cause_selects_the_runbook_and_an_unknown_cause_does_not_run`
- `test_runbook_map_prechecks_every_target`

Viewer acknowledge trả 403 trong test. Bộ ảnh không có trang 403. Bộ ảnh không có badge CLOSED và không có drawer job 71, job 72.

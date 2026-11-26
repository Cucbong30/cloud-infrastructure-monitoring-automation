# TU?N 08 – Runbook & Manual Remediation

## 1. M?c tiêu trong tu?n

Chu?n hóa quy trình x? lý s? c? thông qua Runbook, ki?m th? Manual Remediation trên c? Local và Cloud. Ð?ng th?i ki?m tra l?i RBAC, Audit Trail, Duplicate Job và Email Notification theo góp ý c?a GVHD.

## 2. Phân công công vi?c

### 2.1. Ð? Ðang Thái B?o – Infrastructure / System / Cloud

| STT | Công vi?c du?c phân công | K?t qu? th?c hi?n |
|---|---|---|
| 1 | Xây d?ng Runbook v?n hành. | Hoàn thành 5 Runbook tuong ?ng v?i Success, Execution Failed, Management Blocked, Verification Failed và Manual Required. |
| 2 | Ki?m th? Manual Remediation trên Local Lab. | Khôi ph?c thành công Nginx trên WEB01, Docker Container trên APP01 và Windows Exporter trên WIN01. |
| 3 | Ki?m th? Manual Remediation trên AZURE01. | Restart Nginx thành công và xác nh?n d?ch v? ho?t d?ng trên HTTP port 80. |
| 4 | Ki?m th? các tru?ng h?p remediation th?t b?i. | T?o l?i th?c t? trên AZURE01 d? ki?m tra Execution Failed, Verification Failed và Management Blocked. |
| 5 | Xây d?ng Manual Remediation Action Matrix. | Xác d?nh target, action, di?u ki?n th?c thi, verification và m?c r?i ro LOW cho các action hi?n t?i. |
| 6 | B?o m?t thông tin qu?n tr? Ansible. | Chuy?n credential WinRM c?a WIN01 sang Ansible Vault và ki?m tra l?i k?t n?i thành công. |
| 7 | Ki?m th? tích h?p v?i Application. | Ph?i h?p ki?m tra RBAC, Audit Trail, Duplicate Job và Email Notification. |
| 8 | C?p nh?t tài li?u tri?n khai. | Hoàn thành tài li?u Runbook, Action Matrix, Ansible Vault và k?t qu? ki?m th?. |

**Tr?ng thái: Hoàn thành.**

### 2.2. Nguy?n Th? Gia B?o – Application / Integration

| STT | Công vi?c du?c phân công | K?t qu? th?c hi?n |
|---|---|---|
| 1 | Ki?m soát quy?n Manual Remediation. | Admin và Operator du?c th?c thi remediation, Viewer b? ch?n trên giao di?n và backend. |
| 2 | Hoàn thi?n Audit Trail cho Manual Job. | Ghi nh?n actor, role, mode, target, action, timestamp, result và final status. |
| 3 | Ki?m tra Audit Trail cho Auto Job. | Các job t? d?ng du?c ghi nh?n v?i actor SYSTEM và mode AUTO. |
| 4 | Hoàn thi?n co ch? ch?ng Duplicate Job. | Job trùng du?c ghi nh?n DUPLICATE_SKIPPED, tr?ng thái th?c thi NOT_RUN. |
| 5 | Ki?m th? Email Notification. | G?i thông báo Execution Failed d?n nhóm Critical, Retry và Management Blocked d?n nhóm Warning. |
| 6 | Chu?n hóa cách g?i Ansible trên AZURE01. | Portal ch? g?i playbook, SSH Key c?a AZURE01 du?c qu?n lý tr?c ti?p trên MON01. |
| 7 | Ki?m soát Retry theo ch? d? th?c thi. | Manual Job không t? retry. Verification Failed và Management Blocked không s? d?ng lu?t retry. |
| 8 | Ki?m th? và b? sung minh ch?ng. | Ki?m tra các lu?ng RBAC, Manual/Auto Job, Duplicate Handling và Notification. |

**Tr?ng thái: Hoàn thành các ch?c nang chính, còn m?t s? hình ?nh minh ch?ng c?n b? sung.**

## 3. Công vi?c ph?i h?p gi?a hai thành viên

| Công vi?c | Infrastructure | Application |
|---|---|---|
| Manual Remediation | Chu?n b? playbook và ki?m tra d?ch v? trên b?n target server. | Th?c hi?n remediation t? Portal và hi?n th? k?t qu?. |
| RBAC | Ki?m tra vi?c th?c thi th?c t? trên Infrastructure. | Ki?m soát quy?n Admin, Operator và Viewer. |
| Audit Trail | Ð?i chi?u action và k?t qu? th?c thi. | Ghi nh?n ngu?i th?c hi?n, ch? d? và tr?ng thái job. |
| Duplicate Handling | T?o tình hu?ng remediation trùng l?p. | Ch?n job trùng và ghi nh?n DUPLICATE_SKIPPED. |
| Email Notification | T?o các tình hu?ng l?i th?c t?. | Ki?m tra n?i dung và nhóm nh?n Email theo severity. |

## 4. K?t qu? cu?i tu?n

Hoàn thành b? Runbook v?n hành và ki?m th? Manual Remediation trên WEB01, APP01, WIN01 và AZURE01. Các action v?n tuân th? Pre-check và Verification, không b? qua co ch? ki?m soát dã xây d?ng ? các tu?n tru?c.

RBAC, Audit Trail, Duplicate Handling và Email Notification dã du?c ki?m th?. Thông tin qu?n tr? WIN01 du?c b?o m?t b?ng Ansible Vault.

C?n b? sung hình ?nh Job Detail c?a job 71, job 72, minh ch?ng backend tr? 403 và xác nh?n tr?ng thái cu?i c?a Incident 46.

Tu?n 9 s? m? r?ng sang Approval Workflow và phân lo?i remediation action theo ba m?c r?i ro LOW, MEDIUM và HIGH.

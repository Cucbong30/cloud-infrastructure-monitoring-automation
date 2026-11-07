# Email Notification Group Setup

## 1. Mục tiêu

Thiết lập các Distribution Group trong Microsoft 365 để hệ thống gửi notification theo mức độ cảnh báo thay vì gửi trực tiếp đến từng người dùng.

Các nhóm được sử dụng:

- `KLTN-Alert-Critical`
- `KLTN-Alert-Warning`
- `KLTN-Alert-Info`

---

## 2. Tạo Distribution Group

Truy cập:

```text
Microsoft 365 Admin Center
→ Teams & groups
→ Active teams & groups
→ Distribution list
→ Add a distribution list
```

Tạo các group:

### Critical

```text
Name: KLTN-Alert-Critical
Email: KLTN-Alert-Critical@cucbong.id.vn
```

Dùng cho các sự kiện nghiêm trọng như:

- Service Down
- Execution Failed
- Verification Failed
- Manual Required

---

### Warning

```text
Name: KLTN-Alert-Warning
Email: KLTN-Alert-Warning@cucbong.id.vn
```

Dùng cho các sự kiện:

- Remediation Started
- Retry
- Management Blocked
- Degraded state

---

### Info

```text
Name: KLTN-Alert-Info
Email: KLTN-Alert-Info@cucbong.id.vn
```

Dùng cho:

- Remediation Success
- Service Recovered
- Service Healthy

---

## 3. Cấu hình Owner và Members

Mỗi Distribution Group được cấu hình:

- Owner: tài khoản quản trị của project.
- Members: các thành viên cần nhận notification theo từng mức độ.

Ví dụ:

```text
Critical
→ Admin
→ Operator
→ Project members

Warning
→ Operator
→ Project members

Info
→ Viewer / Project members
```

Member có thể được thêm hoặc gỡ khỏi group mà không cần thay đổi code của Portal.

---

## 4. Notification Routing

Portal không gửi email trực tiếp đến từng user.

Thay vào đó, notification được gửi đến Distribution Group tương ứng với severity:

```text
CRITICAL
→ KLTN-Alert-Critical@cucbong.id.vn

WARNING
→ KLTN-Alert-Warning@cucbong.id.vn

INFO
→ KLTN-Alert-Info@cucbong.id.vn
```

Distribution Group sau đó phân phối email đến các member bên trong group.

---

## 5. Email Sender

Email notification được gửi từ generic mailbox của môi trường Microsoft 365 E5 Developer.

Portal sử dụng Microsoft Graph API với Application Permission:

```text
Mail.Send
```

Luồng gửi mail:

```text
Portal
→ Microsoft Graph
→ Generic Mailbox
→ Distribution Group
→ Group Members
```

Không sử dụng password hoặc App Password của mailbox.

---

## 6. Environment Configuration

Các giá trị cấu hình được lưu trong file `.env` của application:

```text
GRAPH_SENDER_MAILBOX=
ALERT_CRITICAL_GROUP=
ALERT_WARNING_GROUP=
ALERT_INFO_GROUP=
```

Ví dụ:

```text
ALERT_CRITICAL_GROUP=KLTN-Alert-Critical@cucbong.id.vn
ALERT_WARNING_GROUP=KLTN-Alert-Warning@cucbong.id.vn
ALERT_INFO_GROUP=KLTN-Alert-Info@cucbong.id.vn
```

Credential của Entra Application không được lưu trực tiếp trong source code hoặc commit lên Git.

---

## 7. Kết quả

Sau khi hoàn tất cấu hình:

```text
Critical Event
        ↓
KLTN-Alert-Critical
        ↓
Critical Group Members

Warning Event
        ↓
KLTN-Alert-Warning
        ↓
Warning Group Members

Info Event
        ↓
KLTN-Alert-Info
        ↓
Info Group Members
```

Việc sử dụng Distribution Group giúp quản lý người nhận notification tập trung và không cần thay đổi application khi thay đổi thành viên nhận cảnh báo.

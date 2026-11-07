# Microsoft Entra SSO, RBAC and Mail Setup

## Mục tiêu

Chuẩn bị Microsoft Entra ID và Microsoft Graph để Application tích hợp Microsoft SSO, RBAC và email alert vào Portal.

## App Registration

App Registration:

```
KLTN-Operations-Portal
```

Cấu hình:

- Supported account type: Single Tenant
- Platform: Web
- Redirect URI: Flask Portal callback
- Client ID
- Tenant ID
- Client Secret

Client Secret không được lưu trong Git và chỉ được cung cấp cho Application thông qua biến môi trường.

## App Roles

Tạo 3 App Roles:

```
Admin
Operator
Viewer
```

Phân quyền dự kiến:

- `Admin`: full access
- `Operator`: monitoring và thực hiện remediation
- `Viewer`: read-only

Các test user được assign vào từng role thông qua Enterprise Application.

## Microsoft Graph Mail

Cấp Microsoft Graph permission:

```
Mail.Send
Application
```

Sau đó grant Admin Consent cho tenant.

Generic mailbox trong E5 Developer tenant được sử dụng làm sender cho Alert Notification.

## Application Configuration

Application sử dụng các biến môi trường:

```
ENTRA_TENANT_ID=
ENTRA_CLIENT_ID=
ENTRA_CLIENT_SECRET=
ENTRA_REDIRECT_URI=
GRAPH_SENDER_MAILBOX=
```

Thông tin được bàn giao cho Application gồm:

- Tenant ID
- Client ID
- Client Secret
- Redirect URI
- App Roles
- Generic sender mailbox

Application sẽ sử dụng cấu hình này cho:

```
Microsoft SSO
→ Role Claim
→ Portal RBAC
→ Email Alert
```

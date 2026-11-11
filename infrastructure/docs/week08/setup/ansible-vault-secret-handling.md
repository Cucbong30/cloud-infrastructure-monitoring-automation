# Ansible Vault Secret Handling

## 1. Objective

Loại bỏ credential Windows/WinRM khỏi Ansible inventory dạng plain text và chuyển thông tin nhạy cảm sang Ansible Vault.

## 2. Create Vault Variables

Tạo thư mục:

```text
/etc/ansible/group_vars/windows/
```

Tạo file:

```text
/etc/ansible/group_vars/windows/vault.yml
```

File lưu các biến nhạy cảm:

```text
ansible_user
ansible_password
```

Sau đó file được mã hóa bằng:

```text
ansible-vault encrypt /etc/ansible/group_vars/windows/vault.yml
```

Sau khi encrypt, nội dung credential không còn hiển thị dưới dạng plain text.

## 3. Update Ansible Inventory

Credential được xóa khỏi `/etc/ansible/hosts`.

Inventory Windows chỉ giữ các thông tin kết nối:

```text
[windows]
WIN01 ansible_host=192.168.10.13

[windows:vars]
ansible_connection=winrm
ansible_port=5985
ansible_winrm_transport=ntlm
ansible_winrm_server_cert_validation=ignore
```

## 4. File Permission

File Vault được giới hạn quyền truy cập cho user chạy Ansible:

```text
chmod 600 /etc/ansible/group_vars/windows/vault.yml
```

Trong quá trình kiểm tra, Ansible ban đầu gặp lỗi `Permission denied` do file Vault thuộc quyền root.

Sau khi điều chỉnh owner và permission, Ansible có thể đọc file Vault bình thường.

## 5. Connectivity Validation

Kiểm tra lại WIN01:

```text
ansible WIN01 -m win_ping --ask-vault-pass
```

Kết quả:

```text
SUCCESS
ping: pong
```

Điều này xác nhận WIN01 vẫn có thể được quản lý bằng Ansible sau khi credential được chuyển khỏi inventory.

## 6. Result

Sau khi hoàn tất:

```text
Plain-text Credential
→ Removed from Inventory
→ Stored in Ansible Vault
→ Encrypted
→ WIN01 Connectivity Verified
```

Credential nhạy cảm không còn xuất hiện trực tiếp trong Ansible inventory.

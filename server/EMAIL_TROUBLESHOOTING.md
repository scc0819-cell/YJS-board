# 📧 郵件伺服器認證問題排除

## 目前狀況

**✅ 網路連通正常**
- 伺服器 IP: 211.22.81.96
- Ping 測試：正常（2.3ms）
- 伺服器回應：正常

**❌ 認證失敗**
- IMAP (port 143): Authentication Failed
- IMAPS (port 993): Authentication Failed
- STARTTLS: Authentication Failed

---

## 🔍 可能原因

### 1️⃣ 密碼格式問題
- 密碼是否包含特殊字元需要跳脫？
- 是否有前後空格？
- 是否為中文輸入法狀態下輸入？

### 2️⃣ IMAP 服務未開啟
- 郵件伺服器可能需要手動開啟 IMAP 功能
- 可能需要聯繫 IT 管理員開啟

### 3️⃣ 需要使用應用程式密碼
- 某些郵件系統要求使用「應用程式專用密碼」
- 而非登入密碼

### 4️⃣ 帳號格式問題
- 是否需要完整 email 格式？`johnnys@yjsenergy.com`
- 或只需要使用者名稱？`johnnys`

### 5️⃣ 伺服器認證機制
- 可能需要 CRAM-MD5 或其他認證方式
- 而非PLAIN LOGIN

---

## 🔧 解決方案

### 方案 A：確認密碼正確性

請您測試以下命令（在 Windows CMD）：

```cmd
telnet mail.yjsenergy.com 143
```

如果連接成功，會看到：
```
* OK [CAPABILITY IMAP4rev1 ...] mail.yjsenergy.com IMAP server ready
```

然後手動測試登入：
```
a LOGIN johnnys@yjsenergy.com Yjs0929176533cdef
```

如果返回 `OK Logged in`，表示帳號密碼正確。

---

### 方案 B：使用 Outlook 本地資料（推薦）

既然您使用 Outlook，可以直接讀取本地的 PST/OST 檔案，無需連接伺服器！

**優勢**：
- ✅ 無需帳號密碼
- ✅ 無需網路連接
- ✅ 可讀取所有歷史郵件
- ✅ 包含所有附件

**執行方式**：
```python
import win32com.client

outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
inbox = outlook.GetDefaultFolder(6)  # 6 = olFolderInbox

for mail in inbox.Items:
    print(f"主旨：{mail.Subject}")
    print(f"寄件人：{mail.SenderName}")
    print(f"日期：{mail.ReceivedTime}")
    print(f"內文：{mail.Body[:200]}")
    
    # 附件
    for att in mail.Attachments:
        print(f"附件：{att.FileName}")
```

**請告訴我**：您是否使用 Windows Outlook 桌面應用程式？
如果是，我可以直接讀取 Outlook 資料夾！

---

### 方案 C：使用 Exchange Web Services (EWS)

如果您的郵件伺服器是 Exchange，可以使用 EWS：

```python
from exchangelib import Credentials, Account

credentials = Credentials('johnnys@yjsenergy.com', 'Yjs0929176533cdef')
account = Account('johnnys@yjsenergy.com', credentials=credentials, autodiscover=True)

for item in account.inbox.all().order_by('-datetime_received')[:100]:
    print(f"主旨：{item.subject}")
    print(f"寄件人：{item.sender}")
    print(f"日期：{item.datetime_received}")
```

**需要安裝**:
```bash
pip install exchangelib
```

---

### 方案 D：使用 IMAP 正確格式

可能密碼需要 URL 編碼或使用不同格式：

```python
import imaplib
import urllib.parse

# 嘗試 1: 完整 email
mail = imaplib.IMAP4_SSL('mail.yjsenergy.com', 993)
mail.login('johnnys@yjsenergy.com', 'Yjs0929176533cdef')

# 嘗試 2: 只有使用者名稱
mail = imaplib.IMAP4_SSL('mail.yjsenergy.com', 993)
mail.login('johnnys', 'Yjs0929176533cdef')

# 嘗試 3: 密碼 URL 編碼
encoded_pwd = urllib.parse.quote('Yjs0929176533cdef')
mail.login('johnnys@yjsenergy.com', encoded_pwd)
```

---

## 📋 需要您確認的資訊

### 1️⃣ 您使用哪個郵件客戶端？
- [ ] Outlook 桌面應用程式（Windows）
- [ ] Outlook Web Access（網頁版）
- [ ] 其他（請說明）

### 2️⃣ 郵件伺服器類型？
- [ ] Exchange Server
- [ ] IMAP
- [ ] POP3
- [ ] 不確定

### 3️⃣ 是否可以在 Outlook 中查看伺服器設定？
請在 Outlook 中：
1. 檔案 → 帳戶設定 → 帳戶設定
2. 選取您的帳號 → 變更
3. 截圖給我看伺服器設定

### 4️⃣ 是否可以使用應用程式專用密碼？
某些郵件系統要求：
1. 登入郵件網頁版
2. 設定 → 安全性 → 應用程式密碼
3. 建立新密碼給 IMAP 使用

---

## 🚀 最快解決方案

**如果您使用 Outlook 桌面應用程式**：

我可以直接讀取 Outlook 本地資料，無需任何帳號密碼！

請執行以下 Python 腳本：

```python
import win32com.client
import json
from datetime import datetime

outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
inbox = outlook.GetDefaultFolder(6)

emails = []

for mail in inbox.Items:
    if mail.ReceivedTime > datetime.now().replace(day=1):  # 本月郵件
        emails.append({
            'subject': mail.Subject,
            'from': mail.SenderName,
            'date': str(mail.ReceivedTime),
            'body': mail.Body[:500],
            'attachments': [att.FileName for att in mail.Attachments]
        })

print(f"找到 {len(emails)} 封郵件")
print(json.dumps(emails[:5], ensure_ascii=False, indent=2))
```

**請告訴我**：您想使用哪種方式？我會立即調整！

---

## 💡 建議

基於安全性和便利性，我建議：

1. **首選**: 直接讀取 Outlook 本地資料（無需帳號密碼）
2. **次選**: 使用 EWS（如果是 Exchange）
3. **最後**: 解決 IMAP 認證問題

請告訴我您的選擇，我會立即調整程式！🙏

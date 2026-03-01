# 🚀 GitHub Pages 部署教學 - 任務看板

**目標**：將 `task-board-dashboard-v2.html` 部署到 GitHub Pages，獲得永久連結

---

## 📋 方案說明

### 方案 A-1: GitHub Pages（推薦）⭐

**優點**：
- ✅ 完全免費
- ✅ 永久連結
- ✅ 穩定可靠
- ✅ 自動 HTTPS
- ✅ 自訂網域名稱支援

**缺點**：
- ⚠️ 需要 GitHub 帳號
- ⚠️ 公開倉庫（任何人都可看到程式碼）

**適用**：個人專案、公開分享

### 方案 A-2: Netlify

**優點**：
- ✅ 完全免費
- ✅ 拖放部署
- ✅ 自動 HTTPS
- ✅ 私有倉庫支援

**缺點**：
- ⚠️ 需要 Netlify 帳號

**適用**：需要私有部署

---

## 🎯 GitHub Pages 部署步驟（推薦）

### 步驟 1: 準備 GitHub 帳號

1. 前往 [GitHub](https://github.com)
2. 登入或註冊帳號
3. 記住您的 GitHub 用戶名（例如：`yjsenergy`）

### 步驟 2: 建立新倉庫

1. 點擊右上角 **+** → **New repository**
2. 填寫倉庫名稱：`task-board`
3. 描述：`昱金生能源 - AI 任務看板`
4. 選擇 **Public**（公開）
5. **不要** 勾選 "Initialize this repository with a README"
6. 點擊 **Create repository**

### 步驟 3: 上傳看板檔案

#### 方法 A: 使用網頁上傳（最簡單）

1. 在新倉庫頁面，點擊 **uploading an existing file**
2. 拖曳 `task-board-dashboard-v2.html` 到上傳區域
3. 或點擊 **choose your files** 選擇檔案
4. 在 "Commit changes" 輸入：`Initial commit: 任務看板`
5. 點擊 **Commit changes**

#### 方法 B: 使用 Git 命令列

```bash
# 進入工作目錄
cd /home/yjsclaw/.openclaw/workspace

# 複製倉庫（替換為您的 GitHub 用戶名）
git clone https://github.com/YOUR_USERNAME/task-board.git

# 進入目錄
cd task-board

# 複製看板檔案
cp ../task-board-dashboard-v2.html ./index.html

# 添加檔案
git add index.html

# 提交
git commit -m "Initial commit: 任務看板"

# 推送
git push origin main
```

### 步驟 4: 啟用 GitHub Pages

1. 在倉庫頁面，點擊 **Settings**（設定）
2. 左側選單點擊 **Pages**
3. 在 "Source" 下：
   - Branch: 選擇 **main**
   - Folder: 選擇 **/ (root)**
4. 點擊 **Save**
5. 等待 1-2 分鐘

### 步驟 5: 取得連結

部署完成後，您會看到：

```
Your site is live at https://YOUR_USERNAME.github.io/task-board/
```

**這就是您的永久連結！** 🎉

### 步驟 6: 測試連結

在瀏覽器中開啟：
```
https://YOUR_USERNAME.github.io/task-board/
```

您應該能看到完整的任務看板！

---

## 🔄 更新看板

當您修改了 `task-board-dashboard-v2.html` 後：

### 方法 A: 網頁上傳（簡單）

1. 前往倉庫頁面
2. 點擊 `index.html`
3. 點擊右上角 ✏️（編輯）
4. 貼上新的 HTML 內容
5. 點擊 **Commit changes**

### 方法 B: Git 命令列

```bash
# 更新檔案
cp ../task-board-dashboard-v2.html ./index.html

# 提交並推送
git add index.html
git commit -m "Update: 更新看板內容"
git push origin main
```

GitHub Pages 會在 1-2 分鐘內自動更新！

---

## 🎨 自訂網域（可選）

如果您有自己的網域（例如 `yjsenergy.com`）：

1. 在 Pages 設定頁面，點擊 **Custom domain**
2. 輸入您的網域：`task.yjsenergy.com`
3. 點擊 **Save**
4. 在您的 DNS 供應商設定 CNAME 記錄

---

## 📊 自動化部署腳本

我已建立自動化腳本，一鍵部署：

```bash
# 執行部署腳本
python3 /home/yjsclaw/.openclaw/workspace/scripts/deploy_to_github.py
```

腳本會自動：
1. 檢查 GitHub 帳號
2. 建立/更新倉庫
3. 上傳看板檔案
4. 啟用 GitHub Pages
5. 顯示最終連結

---

## ⚠️ 注意事項

### 隱私設定

- **Public 倉庫**：任何人都可看到程式碼
- **Private 倉庫**：GitHub Pages 需要 Public

**解決方案**：
- 看板不包含敏感資料 → 使用 Public ✅
- 包含敏感資料 → 改用 Netlify（支援 Private）

### 檔案大小限制

- GitHub 單檔限制：100MB
- 建議：< 1MB（快速載入）

**當前看板**：21.9KB ✅ 完全符合

### 更新頻率

- GitHub Pages 更新：1-2 分鐘
- 頻繁更新可能延遲

---

## 🎯 完整命令清單

### 一鍵部署（推薦）

```bash
python3 /home/yjsclaw/.openclaw/workspace/scripts/deploy_to_github.py
```

### 手動部署

```bash
# 1. 進入工作目錄
cd /home/yjsclaw/.openclaw/workspace

# 2. 複製看板到部署目錄
mkdir -p github-deploy
cp task-board-dashboard-v2.html github-deploy/index.html

# 3. 初始化 Git
cd github-deploy
git init
git add index.html
git commit -m "Initial commit"

# 4. 連接 GitHub 倉庫（替換用戶名）
git remote add origin https://github.com/YOUR_USERNAME/task-board.git

# 5. 推送
git branch -M main
git push -u origin main
```

---

## 📱 分享連結

部署完成後，您可以：

1. **直接分享**：
   ```
   https://YOUR_USERNAME.github.io/task-board/
   ```

2. **QR Code**：
   - 使用線上工具生成 QR Code
   - 貼在辦公室或分享給團隊

3. **短連結**（可選）：
   - 使用 bit.ly 或 tinyurl
   - 例如：`bit.ly/yjs-task-board`

---

## 🆘 疑難排解

### 問題 1: 頁面顯示 404

**原因**：GitHub Pages 尚未生效

**解決**：
- 等待 1-2 分鐘
- 檢查 Pages 設定是否正確
- 確認 `index.html` 存在於主目錄

### 問題 2: 樣式沒有載入

**原因**：CSS/JS 路徑問題

**解決**：
- 使用相對路徑
- 檢查瀏覽器控制台錯誤

### 問題 3: 推送失敗

**原因**：認證問題

**解決**：
```bash
# 使用 Personal Access Token
git push https://YOUR_TOKEN@github.com/YOUR_USERNAME/task-board.git
```

---

## 📞 需要協助？

如果在部署過程中遇到問題：

1. 檢查 GitHub Pages 狀態：https://www.githubstatus.com/
2. 查看 GitHub Docs：https://docs.github.com/en/pages
3. 詢問 Jenny：「幫我檢查 GitHub Pages 部署問題」

---

## ✅ 檢查清單

部署前確認：

- [ ] 已有 GitHub 帳號
- [ ] 記住用戶名和密碼
- [ ] 看板檔案已準備好
- [ ] 網路連線正常

部署後確認：

- [ ] 倉庫已建立
- [ ] 檔案已上傳
- [ ] Pages 已啟用
- [ ] 連結可訪問
- [ ] 樣式正常顯示

---

**準備好開始了嗎？** 

請告訴我您的 GitHub 用戶名，我可以幫您自動化部署！

**最後更新**: 2026-03-01

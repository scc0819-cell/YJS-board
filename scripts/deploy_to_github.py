#!/usr/bin/env python3
"""
昱金生能源 - GitHub Pages 自動化部署腳本
一鍵部署任務看板到 GitHub Pages
"""

import subprocess
import json
from pathlib import Path
from datetime import datetime
import logging
import sys
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 路徑設定
WORKSPACE_DIR = Path('/home/yjsclaw/.openclaw/workspace')
DEPLOY_DIR = WORKSPACE_DIR / 'github-deploy'
HTML_SOURCE = WORKSPACE_DIR / 'task-board-dashboard-v2.html'
GITHUB_USER = None  # 將在執行時詢問

def run_command(command, check=True):
    """執行 shell 命令"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=check
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, "", str(e)

def check_git():
    """檢查 Git 是否已安裝"""
    logger.info("🔍 檢查 Git 安裝...")
    success, stdout, stderr = run_command("git --version")
    
    if success:
        logger.info(f"✅ Git 已安裝：{stdout.strip()}")
        return True
    else:
        logger.error("❌ Git 未安裝")
        logger.info("請執行：sudo apt-get install git")
        return False

def check_github_auth():
    """檢查 GitHub 認證"""
    logger.info("🔐 檢查 GitHub 認證...")
    
    # 嘗試取得 GitHub 用戶名
    success, stdout, stderr = run_command("git config --global user.name", check=False)
    
    if success and stdout.strip():
        logger.info(f"✅ GitHub 用戶名：{stdout.strip()}")
        return stdout.strip()
    else:
        logger.warning("⚠️ 未設定 GitHub 用戶名")
        return None

def setup_github_auth():
    """設定 GitHub 認證"""
    logger.info("📝 請輸入您的 GitHub 用戶名：")
    username = input("GitHub Username: ").strip()
    
    if not username:
        logger.error("❌ 用戶名不能為空")
        return None
    
    # 設定全局用戶名
    run_command(f"git config --global user.name \"{username}\"")
    
    # 設定 email（可選）
    email = input("GitHub Email (可選，直接 Enter 跳過): ").strip()
    if email:
        run_command(f"git config --global user.email \"{email}\"")
    
    logger.info(f"✅ GitHub 用戶名已設定：{username}")
    return username

def create_deploy_directory():
    """建立部署目錄"""
    logger.info("📁 建立部署目錄...")
    
    if DEPLOY_DIR.exists():
        logger.info(f"⚠️ 部署目錄已存在：{DEPLOY_DIR}")
        # 詢問是否清空
        response = input("是否清空並重新部署？(y/N): ").strip().lower()
        if response == 'y':
            run_command(f"rm -rf {DEPLOY_DIR}")
            DEPLOY_DIR.mkdir(parents=True)
            logger.info("✅ 已清空部署目錄")
        else:
            logger.info("⏭️ 使用現有目錄")
    else:
        DEPLOY_DIR.mkdir(parents=True)
        logger.info(f"✅ 已建立部署目錄：{DEPLOY_DIR}")
    
    return True

def copy_html_file():
    """複製 HTML 檔案到部署目錄"""
    logger.info("📄 複製看板檔案...")
    
    if not HTML_SOURCE.exists():
        logger.error(f"❌ 找不到看板檔案：{HTML_SOURCE}")
        return False
    
    # 複製並改名為 index.html
    dest_file = DEPLOY_DIR / 'index.html'
    
    try:
        content = HTML_SOURCE.read_text(encoding='utf-8')
        dest_file.write_text(content, encoding='utf-8')
        logger.info(f"✅ 已複製：{HTML_SOURCE.name} → index.html")
        return True
    except Exception as e:
        logger.error(f"❌ 複製失敗：{e}")
        return False

def initialize_git_repo():
    """初始化 Git 倉庫"""
    logger.info("🔄 初始化 Git 倉庫...")
    
    # 檢查是否已有 .git 目錄
    git_dir = DEPLOY_DIR / '.git'
    
    if git_dir.exists():
        logger.info("⚠️ Git 倉庫已存在")
        response = input("是否重新初始化？(y/N): ").strip().lower()
        if response != 'y':
            return True
        run_command(f"rm -rf {git_dir}")
    
    # 初始化
    success, stdout, stderr = run_command(f"cd {DEPLOY_DIR} && git init")
    
    if success:
        logger.info("✅ Git 倉庫已初始化")
        return True
    else:
        logger.error(f"❌ Git 初始化失敗：{stderr}")
        return False

def add_and_commit():
    """添加檔案並提交"""
    logger.info("💾 添加檔案並提交...")
    
    commands = [
        f"cd {DEPLOY_DIR} && git add index.html",
        f"cd {DEPLOY_DIR} && git commit -m \"Deploy task board: {datetime.now().strftime('%Y-%m-%d %H:%M')}\""
    ]
    
    for cmd in commands:
        success, stdout, stderr = run_command(cmd)
        if not success:
            logger.error(f"❌ 命令失敗：{cmd}")
            logger.error(f"錯誤：{stderr}")
            return False
    
    logger.info("✅ 檔案已提交")
    return True

def connect_github_repo(username):
    """連接 GitHub 倉庫"""
    logger.info("🔗 連接 GitHub 倉庫...")
    
    repo_name = input("倉庫名稱 (預設：task-board): ").strip() or "task-board"
    repo_url = f"https://github.com/{username}/{repo_name}.git"
    
    logger.info(f"📋 倉庫 URL: {repo_url}")
    
    # 檢查遠端是否已存在
    success, stdout, stderr = run_command(f"cd {DEPLOY_DIR} && git remote -v")
    
    if success and "origin" in stdout:
        logger.info("⚠️ 遠端倉庫已存在")
        response = input("是否更新遠端 URL？(y/N): ").strip().lower()
        if response == 'y':
            run_command(f"cd {DEPLOY_DIR} && git remote remove origin")
        else:
            logger.info("⏭️ 使用現有遠端")
            return repo_name
    
    # 添加遠端
    success, stdout, stderr = run_command(f"cd {DEPLOY_DIR} && git remote add origin {repo_url}")
    
    if not success:
        logger.error(f"❌ 添加遠端失敗：{stderr}")
        return None
    
    logger.info(f"✅ 已連接 GitHub 倉庫：{repo_name}")
    return repo_name

def push_to_github():
    """推送到 GitHub"""
    logger.info("🚀 推送到 GitHub...")
    
    # 切換到 main 分支
    run_command(f"cd {DEPLOY_DIR} && git branch -M main")
    
    # 推送
    logger.info("請輸入 GitHub 密碼或 Personal Access Token：")
    logger.info("(密碼不會顯示在畫面上)")
    
    # 使用密碼提示
    import getpass
    password = getpass.getpass("GitHub Password/Token: ")
    
    # 構建帶認證的 URL（暫時）
    success, stdout, stderr = run_command(f"cd {DEPLOY_DIR} && git push -u origin main")
    
    if not success:
        logger.error(f"❌ 推送失敗：{stderr}")
        logger.info("💡 提示：可能需要使用 Personal Access Token")
        logger.info("   前往 https://github.com/settings/tokens 建立 Token")
        logger.info("   勾選 'repo' 權限")
        return False
    
    logger.info("✅ 已成功推送到 GitHub！")
    return True

def enable_github_pages(username, repo_name):
    """啟用 GitHub Pages"""
    logger.info("📄 啟用 GitHub Pages...")
    logger.info("請手動啟用 GitHub Pages：")
    logger.info(f"1. 前往 https://github.com/{username}/{repo_name}/settings/pages")
    logger.info("2. Source 選擇 'main' 分支")
    logger.info("3. Folder 選擇 '/ (root)'")
    logger.info("4. 點擊 Save")
    logger.info("5. 等待 1-2 分鐘")
    
    response = input("已完成啟用？(y/N): ").strip().lower()
    
    if response == 'y':
        logger.info("✅ GitHub Pages 已啟用")
        return True
    else:
        logger.warning("⚠️ GitHub Pages 尚未啟用")
        return False

def show_final_url(username, repo_name):
    """顯示最終連結"""
    logger.info("\n" + "=" * 70)
    logger.info("🎉 部署完成！")
    logger.info("=" * 70)
    
    url = f"https://{username}.github.io/{repo_name}/"
    
    logger.info(f"\n📊 您的任務看板連結：")
    logger.info(f"\n🔗 {url}")
    logger.info(f"\n💡 提示：")
    logger.info(f"   - 等待 1-2 分鐘讓 GitHub Pages 生效")
    logger.info(f"   - 如果無法訪問，請檢查 Pages 設定")
    logger.info(f"   - 更新檔案後重新執行此腳本即可自動更新")
    
    # 儲存連結到檔案
    url_file = WORKSPACE_DIR / 'github-pages-url.txt'
    url_file.write_text(url, encoding='utf-8')
    logger.info(f"\n✅ 連結已儲存至：{url_file}")
    
    return url

def main():
    """主函數"""
    logger.info("=" * 70)
    logger.info("🚀 GitHub Pages 自動化部署")
    logger.info(f"⏰ 時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70)
    
    # 步驟 1: 檢查 Git
    if not check_git():
        return False
    
    # 步驟 2: 檢查/設定 GitHub 認證
    github_user = check_github_auth()
    if not github_user:
        github_user = setup_github_auth()
        if not github_user:
            return False
    
    # 步驟 3: 建立部署目錄
    if not create_deploy_directory():
        return False
    
    # 步驟 4: 複製 HTML 檔案
    if not copy_html_file():
        return False
    
    # 步驟 5: 初始化 Git
    if not initialize_git_repo():
        return False
    
    # 步驟 6: 添加並提交
    if not add_and_commit():
        return False
    
    # 步驟 7: 連接 GitHub 倉庫
    repo_name = connect_github_repo(github_user)
    if not repo_name:
        return False
    
    # 步驟 8: 推送到 GitHub
    if not push_to_github():
        logger.warning("⚠️ 推送失敗，但您可以手動推送：")
        logger.info(f"   cd {DEPLOY_DIR}")
        logger.info("   git push -u origin main")
    
    # 步驟 9: 啟用 GitHub Pages
    enable_github_pages(github_user, repo_name)
    
    # 步驟 10: 顯示最終連結
    url = show_final_url(github_user, repo_name)
    
    logger.info("\n" + "=" * 70)
    logger.info("✅ 部署流程完成！")
    logger.info("=" * 70)
    
    return True

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.error("\n❌ 使用者中斷")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ 發生錯誤：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

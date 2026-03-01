#!/usr/bin/env python3
"""
昱金生能源 - 郵件解析與案場知識學習系統
每 30 分鐘自動執行，解析新郵件、學習案場經驗、更新知識庫
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
import subprocess
import logging

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/email_analyzer.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 路徑設定
BASE_DIR = Path('/home/yjsclaw/.openclaw/workspace')
SERVER_DIR = BASE_DIR / 'server'
DAILY_REPORT_DIR = BASE_DIR / 'daily_report_server'
OUTPUT_DIR = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/full_email_analysis')
MEMORY_DIR = BASE_DIR / 'memory'

# 狀態檔案
STATE_FILE = DAILY_REPORT_DIR / 'email_analyzer_state.json'

def load_state():
    """載入上次執行狀態"""
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'last_run': None,
        'total_emails_processed': 0,
        'total_cases_learned': 0,
        'last_new_email_time': None
    }

def save_state(state):
    """儲存執行狀態"""
    tmp = STATE_FILE.with_suffix('.json.tmp')
    tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')
    tmp.replace(STATE_FILE)

def parse_emails():
    """執行郵件解析"""
    logger.info("📧 開始解析郵件...")
    
    try:
        # 執行郵件解析腳本
        script = SERVER_DIR / 'read_outlook_emails.py'
        if script.exists():
            result = subprocess.run(
                ['python3', str(script)],
                capture_output=True,
                text=True,
                timeout=300
            )
            logger.info(f"郵件解析完成：{result.stdout[:500]}")
            return True
        else:
            logger.warning(f"郵件解析腳本不存在：{script}")
            return False
    except Exception as e:
        logger.error(f"郵件解析失敗：{e}")
        return False

def analyze_and_learn():
    """深入分析郵件並學習案場經驗"""
    logger.info("🧠 開始深入分析與學習...")
    
    try:
        # 1. 執行完整分析腳本
        script = SERVER_DIR / 'full_email_analysis.py'
        if script.exists():
            result = subprocess.run(
                ['python3', str(script)],
                capture_output=True,
                text=True,
                timeout=600
            )
            logger.info(f"分析完成：{result.stdout[:500]}")
        else:
            logger.warning(f"分析腳本不存在：{script}")
        
        # 2. 執行案場知識學習
        learner_script = DAILY_REPORT_DIR / 'case_knowledge_learner.py'
        if learner_script.exists():
            result = subprocess.run(
                ['python3', str(learner_script)],
                capture_output=True,
                text=True,
                timeout=600
            )
            logger.info(f"案場學習完成：{result.stdout[:500]}")
        
        # 複製結果到 Windows 可存取位置
        import shutil
        src_dir = DAILY_REPORT_DIR / 'full_email_analysis'
        if src_dir.exists():
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            for f in src_dir.glob('*'):
                if f.is_file():
                    shutil.copy2(f, OUTPUT_DIR / f.name)
            logger.info(f"已複製分析結果到：{OUTPUT_DIR}")
        
        return True
    except Exception as e:
        logger.error(f"分析失敗：{e}")
        return False

def update_memory():
    """更新記憶系統"""
    logger.info("🧠 更新記憶系統...")
    
    try:
        # 載入最新的案場資料庫
        case_db_file = OUTPUT_DIR / 'case_database.json'
        if case_db_file.exists():
            with open(case_db_file, 'r', encoding='utf-8') as f:
                case_db = json.load(f)
            
            # 更新今日記憶
            today = datetime.now().strftime('%Y-%m-%d')
            memory_file = MEMORY_DIR / f'{today}.md'
            
            with open(memory_file, 'a', encoding='utf-8') as f:
                f.write(f"\n\n## {datetime.now().strftime('%H:%M')} 案場知識更新\n")
                f.write(f"- 更新時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"- 學習案場數：{len(case_db)}\n")
                f.write(f"- 來源：郵件自動解析系統\n")
            
            logger.info(f"已更新記憶：{memory_file}")
            return True
        return False
    except Exception as e:
        logger.error(f"記憶更新失敗：{e}")
        return False

def generate_report():
    """生成學習報告"""
    logger.info("📊 生成學習報告...")
    
    state = load_state()
    report = {
        'timestamp': datetime.now().isoformat(),
        'emails_processed': state.get('total_emails_processed', 0),
        'cases_learned': state.get('total_cases_learned', 0),
        'last_run': state.get('last_run'),
        'status': 'success'
    }
    
    report_file = OUTPUT_DIR / f'learning_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    logger.info(f"已生成報告：{report_file}")
    return report

def main():
    """主函數"""
    logger.info("=" * 60)
    logger.info("🚀 昱金生能源 - 郵件解析與案場知識學習系統")
    logger.info(f"⏰ 執行時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    state = load_state()
    state['last_run'] = datetime.now().isoformat()
    
    # 1. 解析郵件
    if parse_emails():
        state['total_emails_processed'] += 1
    
    # 2. 深入分析與學習
    if analyze_and_learn():
        state['total_cases_learned'] += 1
    
    # 3. 更新記憶
    update_memory()
    
    # 4. 生成報告
    report = generate_report()
    
    # 5. 儲存狀態
    save_state(state)
    
    logger.info("=" * 60)
    logger.info("✅ 本輪學習完成")
    logger.info(f"📊 累計處理郵件：{state['total_emails_processed']} 次")
    logger.info(f"📊 累計學習案場：{state['total_cases_learned']} 次")
    logger.info("=" * 60)

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
🧠 昱金生能源 - 經營大腦 v4.0
數據結構化腳本：建立 AI 分析所需的視圖和指標
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

DB_PATH = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/data/app.db')

def create_ai_views():
    """建立 AI 分析所需的資料庫視圖"""
    
    print("🧠 開始建立經營大腦數據視圖...\n")
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # ==================== 1. 案件進度追蹤視圖 ====================
    print("📊 建立案件進度追蹤視圖...")
    
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS v_case_progress AS
        SELECT 
            c.case_id,
            c.name as case_name,
            c.case_code,
            c.type as case_type,
            c.milestone_stage,
            c.progress_percentage,
            
            -- 日報統計
            COUNT(DISTINCT r.report_key) as total_reports,
            COUNT(DISTINCT r.employee_id) as involved_employees,
            MAX(r.report_date) as last_report_date,
            
            -- 風險統計
            COUNT(DISTINCT risk.risk_id) as total_risks,
            SUM(CASE WHEN risk.status = 'open' THEN 1 ELSE 0 END) as open_risks,
            SUM(CASE WHEN risk.status = 'in_progress' THEN 1 ELSE 0 END) as in_progress_risks,
            SUM(CASE WHEN risk.level = 'high' AND risk.status != 'closed' THEN 1 ELSE 0 END) as high_risks,
            
            -- 任務統計
            COUNT(DISTINCT task.task_id) as total_tasks,
            SUM(CASE WHEN task.status = 'open' THEN 1 ELSE 0 END) as open_tasks,
            SUM(CASE WHEN task.status = 'overdue' THEN 1 ELSE 0 END) as overdue_tasks,
            
            -- 進度狀態判斷
            CASE 
                WHEN c.progress_percentage >= 100 THEN 'completed'
                WHEN c.progress_percentage >= 75 THEN 'advanced'
                WHEN c.progress_percentage >= 50 THEN 'in_progress'
                WHEN c.progress_percentage > 0 THEN 'started'
                ELSE 'not_started'
            END as progress_status
            
        FROM cases c
        LEFT JOIN reports r ON r.case_name = c.name
        LEFT JOIN risks risk ON risk.case_id = c.case_id
        LEFT JOIN tasks task ON task.case_id = c.case_id
        GROUP BY c.case_id, c.name, c.case_code, c.type, c.milestone_stage, c.progress_percentage
        ORDER BY c.case_id
    """)
    
    print("  ✅ v_case_progress 已建立")
    
    # ==================== 2. 風險趨勢分析視圖 ====================
    print("📈 建立風險趨勢分析視圖...")
    
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS v_risk_trend AS
        SELECT 
            strftime('%Y-%m', created_at) as month,
            category,
            level,
            COUNT(*) as risk_count,
            SUM(CASE WHEN status = 'closed' THEN 1 ELSE 0 END) as closed_count,
            SUM(CASE WHEN status = 'open' THEN 1 ELSE 0 END) as open_count,
            ROUND(100.0 * SUM(CASE WHEN status = 'closed' THEN 1 ELSE 0 END) / COUNT(*), 1) as closure_rate
        FROM risks
        WHERE created_at IS NOT NULL
        GROUP BY strftime('%Y-%m', created_at), category, level
        ORDER BY month DESC, category
    """)
    
    print("  ✅ v_risk_trend 已建立")
    
    # ==================== 3. 員工績效指標視圖 ====================
    print("👥 建立員工績效指標視圖...")
    
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS v_employee_performance AS
        SELECT 
            e.employee_id,
            e.employee_name,
            e.department,
            e.role,
            
            -- 日報統計
            COUNT(DISTINCT r.report_key) as total_reports,
            COUNT(DISTINCT r.report_date) as report_days,
            MAX(r.report_date) as last_report_date,
            
            -- 日報提交率（最近 30 天）
            ROUND(100.0 * COUNT(DISTINCT r.report_date) / 30, 1) as submit_rate_30d,
            
            -- 風險/任務統計
            COUNT(DISTINCT risk.risk_id) as reported_risks,
            COUNT(DISTINCT task.task_id) as assigned_tasks,
            SUM(CASE WHEN task.status = 'closed' THEN 1 ELSE 0 END) as completed_tasks,
            
            -- 任務完成率
            ROUND(100.0 * SUM(CASE WHEN task.status = 'closed' THEN 1 ELSE 0 END) / 
                NULLIF(COUNT(DISTINCT task.task_id), 0), 1) as task_completion_rate,
            
            -- 附件統計
            COUNT(DISTINCT att.id) as uploaded_attachments,
            
            -- 綜合評分（簡單加權）
            ROUND(
                COALESCE(100.0 * COUNT(DISTINCT r.report_date) / 30, 0) * 0.4 +
                COALESCE(100.0 * SUM(CASE WHEN task.status = 'closed' THEN 1 ELSE 0 END) / 
                    NULLIF(COUNT(DISTINCT task.task_id), 0), 0) * 0.4 +
                COALESCE(MIN(100, COUNT(DISTINCT risk.risk_id) * 10), 0) * 0.2,
                1
            ) as performance_score
            
        FROM (
            SELECT id as employee_id, name as employee_name, department, role
            FROM users
            WHERE enabled = 1
        ) e
        LEFT JOIN reports r ON e.employee_id = r.employee_id
        LEFT JOIN risks risk ON e.employee_id = risk.reporter_id
        LEFT JOIN tasks task ON e.employee_id = task.owner_id
        LEFT JOIN attachments att ON e.employee_id = att.employee_id
        GROUP BY e.employee_id, e.employee_name, e.department, e.role
        ORDER BY performance_score DESC
    """)
    
    print("  ✅ v_employee_performance 已建立")
    
    # ==================== 4. 每日經營摘要視圖 ====================
    print("📋 建立每日經營摘要視圖...")
    
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS v_daily_summary AS
        SELECT 
            r.report_date,
            
            -- 提交統計
            COUNT(DISTINCT r.employee_id) as submitted_count,
            COUNT(DISTINCT e.id) as total_employees,
            ROUND(100.0 * COUNT(DISTINCT r.employee_id) / COUNT(DISTINCT e.id), 1) as submit_rate,
            
            -- 新增風險
            COUNT(DISTINCT risk.risk_id) as new_risks,
            SUM(CASE WHEN risk.level = 'high' THEN 1 ELSE 0 END) as high_risks,
            
            -- 新增任務
            COUNT(DISTINCT task.task_id) as new_tasks,
            
            -- 案件進度
            COUNT(DISTINCT r.case_name) as active_cases
            
        FROM reports r
        CROSS JOIN (SELECT id FROM users WHERE enabled = 1) e
        LEFT JOIN risks risk ON risk.report_date = r.report_date
        LEFT JOIN tasks task ON task.report_date = r.report_date
        GROUP BY r.report_date
        ORDER BY r.report_date DESC
    """)
    
    print("  ✅ v_daily_summary 已建立")
    
    # ==================== 5. 高風險預警視圖 ====================
    print("🚨 建立高風險預警視圖...")
    
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS v_high_risk_alerts AS
        SELECT 
            risk.risk_id,
            risk.case_id,
            c.name as case_name,
            c.case_code,
            risk.category,
            risk.description,
            risk.level,
            risk.status,
            risk.owner_id,
            u.name as owner_name,
            risk.due_date,
            risk.created_at,
            julianday('now') - julianday(risk.created_at) as days_open,
            CASE 
                WHEN risk.due_date < date('now') THEN 'overdue'
                WHEN risk.due_date = date('now') THEN 'due_today'
                WHEN risk.due_date <= date('now', '+3 days') THEN 'due_soon'
                ELSE 'on_track'
            END as urgency_status
            
        FROM risks risk
        LEFT JOIN cases c ON risk.case_id = c.case_id
        LEFT JOIN users u ON risk.owner_id = u.id
        WHERE risk.level = 'high' AND risk.status != 'closed'
        ORDER BY 
            CASE 
                WHEN risk.due_date < date('now') THEN 1
                WHEN risk.due_date = date('now') THEN 2
                WHEN risk.due_date <= date('now', '+3 days') THEN 3
                ELSE 4
            END,
            risk.due_date
    """)
    
    print("  ✅ v_high_risk_alerts 已建立")
    
    # ==================== 6. 逾期任務預警視圖 ====================
    print("⏰ 建立逾期任務預警視圖...")
    
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS v_overdue_tasks_alerts AS
        SELECT 
            task.task_id,
            task.case_id,
            c.name as case_name,
            c.case_code,
            task.description,
            task.priority,
            task.status,
            task.owner_id,
            u.name as owner_name,
            task.due_date,
            julianday('now') - julianday(task.due_date) as days_overdue,
            CASE 
                WHEN task.due_date < date('now') THEN 'overdue'
                WHEN task.due_date = date('now') THEN 'due_today'
                WHEN task.due_date <= date('now', '+3 days') THEN 'due_soon'
                ELSE 'on_track'
            END as urgency_status
            
        FROM tasks task
        LEFT JOIN cases c ON task.case_id = c.case_id
        LEFT JOIN users u ON task.owner_id = u.id
        WHERE task.status != 'closed'
        ORDER BY 
            CASE 
                WHEN task.due_date < date('now') THEN 1
                WHEN task.due_date = date('now') THEN 2
                WHEN task.due_date <= date('now', '+3 days') THEN 3
                ELSE 4
            END,
            task.due_date
    """)
    
    print("  ✅ v_overdue_tasks_alerts 已建立")
    
    conn.commit()
    conn.close()
    
    print("\n✅ 經營大腦數據視圖建立完成！\n")
    
    # 顯示視圖清單
    print("📊 已建立的視圖：")
    print("  1. v_case_progress - 案件進度追蹤")
    print("  2. v_risk_trend - 風險趨勢分析")
    print("  3. v_employee_performance - 員工績效指標")
    print("  4. v_daily_summary - 每日經營摘要")
    print("  5. v_high_risk_alerts - 高風險預警")
    print("  6. v_overdue_tasks_alerts - 逾期任務預警")
    
    print("\n💡 下一步：建立 AI 自動分析 API")


if __name__ == '__main__':
    create_ai_views()

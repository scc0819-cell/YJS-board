#!/usr/bin/env python3
"""
昱金生知識管理掃描器 v2（快速版）
策略：只讀目錄名稱（不掃檔案 metadata），30 秒內完成
輸出：知識索引 JSON + 記憶檔（供 memory_search 使用）
"""
import os, json, re, subprocess
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import defaultdict

TZ8 = timezone(timedelta(hours=8))
SCAN_ROOT = '/mnt/z'
KNOWLEDGE_DIR = Path('/home/yjsclaw/.openclaw/workspace/knowledge')
KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
INDEX_FILE = KNOWLEDGE_DIR / 'z_drive_index.json'
MEMORY_FILE = Path('/home/yjsclaw/.openclaw/workspace/memory/knowledge_z_drive.md')

def get_dirs(path, depth):
    """用 find 快速取目錄（避免 Python walk 在 NAS 上太慢）"""
    r = subprocess.run(['find', path, '-maxdepth', str(depth), '-type', 'd'],
                       capture_output=True, text=True, timeout=90)
    return [l.strip() for l in r.stdout.splitlines() if l.strip() and l.strip() != path]

def classify_l1(name):
    if re.match(r'20\d{6}', name):
        return 'case'
    if '【' in name:
        return 'department'
    if '昱金生' in name or name.startswith('00'):
        return 'company'
    return 'other'

def parse_case(name):
    m = re.match(r'(20\d{6})-(.+)', name)
    if not m:
        return None
    date_str, desc = m.group(1), m.group(2)
    case_type = '標案' if '標案' in desc else '中租' if '中租' in desc else '民間' if '民間' in desc else '其他'
    loc_m = re.search(r'--(.+?)--', desc)
    location = loc_m.group(1) if loc_m else ''
    addr_m = re.search(r'--[^-]+--(.+?)(?:\d{3,}|$)', desc)
    address = addr_m.group(1)[:80] if addr_m else ''
    return {'folder': name, 'date': date_str, 'type': case_type, 'location': location, 'address': address}

def main():
    ts = datetime.now(TZ8).strftime('%Y-%m-%d %H:%M:%S')
    print(f'[{ts}] 快速掃描 {SCAN_ROOT}...')

    l1 = get_dirs(SCAN_ROOT, 1)
    l2 = get_dirs(SCAN_ROOT, 2)

    l1_names = [os.path.basename(d) for d in l1]
    l2_by_parent = defaultdict(list)
    for d in l2:
        parent = os.path.basename(os.path.dirname(d))
        l2_by_parent[parent].append(os.path.basename(d))

    # 分類
    cats = defaultdict(list)
    for name in l1_names:
        cats[classify_l1(name)].append(name)

    # 案場解析
    cases = []
    for name in cats['case']:
        c = parse_case(name)
        if c:
            subs = l2_by_parent.get(name, [])
            c['subdirs'] = len(subs)
            c['has_design'] = any('設計' in s or '圖面' in s or '結構' in s for s in subs)
            c['has_bid'] = any('投標' in s or '標案' in s or '開標' in s for s in subs)
            c['has_construction'] = any('施工' in s or '工程' in s or '進場' in s for s in subs)
            c['has_completion'] = any('完工' in s or '驗收' in s or '掛表' in s for s in subs)
            c['subdir_sample'] = subs[:12]
            cases.append(c)
    cases.sort(key=lambda x: x['date'], reverse=True)

    # 部門
    depts = []
    for name in cats['department']:
        subs = l2_by_parent.get(name, [])
        depts.append({'name': name, 'subdirs': len(subs), 'subdir_sample': subs[:8]})

    # 索引
    index = {
        'scan_time': ts,
        'total_l1': len(l1_names),
        'total_l2': len(l2),
        'cases_count': len(cases),
        'departments_count': len(depts),
        'company_count': len(cats['company']),
        'cases': cases,
        'departments': depts,
        'company': cats['company'],
        'other': cats['other'],
    }
    INDEX_FILE.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding='utf-8')

    # 記憶檔
    lines = [
        f'# 昱金生 Z Drive 知識索引',
        f'',
        f'> 掃描時間：{ts}',
        f'> 來源：/mnt/z（\\\\yjs\\yjs fs）',
        f'',
        f'## 總覽',
        f'- 頂層資料夾：{len(l1_names)}',
        f'- 二層資料夾：{len(l2)}',
        f'- 案場專案：{len(cases)} 個',
        f'- 部門專區：{len(depts)} 個',
        f'- 公司管理：{len(cats["company"])} 個',
        f'',
        f'## 案場清單（{len(cases)} 個，依時間排序）',
        f'',
    ]
    for c in cases:
        status = []
        if c['has_bid']: status.append('投標')
        if c['has_design']: status.append('設計')
        if c['has_construction']: status.append('施工')
        if c['has_completion']: status.append('完工')
        st = '→'.join(status) if status else '資料夾建立'
        lines.append(f'- [{c["date"]}] **{c["location"] or c["folder"][:30]}** | {c["type"]} | 進度：{st}')

    lines.append('')
    lines.append(f'## 部門專區（{len(depts)} 個）')
    for d in depts:
        lines.append(f'- {d["name"]}（子目錄 {d["subdirs"]}）')

    lines.append('')
    lines.append(f'## 公司管理')
    for name in cats['company']:
        lines.append(f'- {name}')

    lines.append('')
    lines.append(f'## 其他')
    for name in cats['other']:
        lines.append(f'- {name}')

    MEMORY_FILE.write_text('\n'.join(lines), encoding='utf-8')

    print(f'[{ts}] 完成！')
    print(f'  L1: {len(l1_names)} | L2: {len(l2)} | 案場: {len(cases)} | 部門: {len(depts)}')
    print(f'  索引：{INDEX_FILE}')
    print(f'  記憶：{MEMORY_FILE}')

if __name__ == '__main__':
    main()

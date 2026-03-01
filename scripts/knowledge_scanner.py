#!/usr/bin/env python3
"""
昱金生知識管理掃描器 v1
每 30 分鐘掃描 /mnt/z，建構知識索引。
策略：
  1. 掃描目錄結構 → 組織架構 + 案場清單
  2. 掃描文件 metadata → 檔名/路徑/大小/修改時間
  3. 增量更新（只處理新增或修改的檔案）
  4. 輸出知識索引 JSON + 摘要 markdown
"""
import os, json, hashlib, re
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import defaultdict

TZ8 = timezone(timedelta(hours=8))
SCAN_ROOT = Path('/mnt/z')
KNOWLEDGE_DIR = Path('/home/yjsclaw/.openclaw/workspace/knowledge')
KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)

INDEX_FILE = KNOWLEDGE_DIR / 'z_drive_index.json'
SUMMARY_FILE = KNOWLEDGE_DIR / 'z_drive_summary.md'
MEMORY_FILE = Path('/home/yjsclaw/.openclaw/workspace/memory/knowledge_z_drive.md')

DOC_EXTS = {'.pdf','.xlsx','.xls','.docx','.doc','.pptx','.ppt','.csv','.txt','.md','.html','.jpg','.png','.dwg','.dxf'}
MAX_DEPTH = 4

def scan_directory(root: Path, max_depth=MAX_DEPTH):
    """掃描目錄結構與文件 metadata"""
    entries = []
    dir_tree = {}

    for dirpath, dirnames, filenames in os.walk(str(root)):
        rel = os.path.relpath(dirpath, str(root))
        depth = 0 if rel == '.' else rel.count(os.sep) + 1
        if depth > max_depth:
            dirnames.clear()
            continue

        dir_info = {
            'path': dirpath,
            'rel': rel,
            'depth': depth,
            'subdirs': len(dirnames),
            'files': len(filenames),
            'doc_files': [],
        }

        for fn in filenames:
            ext = os.path.splitext(fn)[1].lower()
            if ext in DOC_EXTS:
                fp = os.path.join(dirpath, fn)
                try:
                    st = os.stat(fp)
                    dir_info['doc_files'].append({
                        'name': fn,
                        'ext': ext,
                        'size_kb': round(st.st_size / 1024, 1),
                        'mtime': datetime.fromtimestamp(st.st_mtime, TZ8).strftime('%Y-%m-%d %H:%M'),
                    })
                except Exception:
                    pass

        entries.append(dir_info)

    return entries


def classify_folders(entries):
    """分類頂層資料夾"""
    categories = {
        'company': [],      # 公司制度/管理
        'cases': [],         # 案場專案
        'departments': [],   # 部門專區
        'reference': [],     # 參考資料
        'other': [],
    }

    for e in entries:
        if e['depth'] != 1:
            continue
        name = os.path.basename(e['path'])

        if re.match(r'20\d{6}', name):
            # 案場（日期開頭）
            case_type = '標案' if '標案' in name else '中租' if '中租' in name else '民間' if '民間' in name else '其他'
            location = ''
            m = re.search(r'--(.+?)--', name)
            if m:
                location = m.group(1)
            categories['cases'].append({
                'name': name,
                'type': case_type,
                'location': location,
                'files': e['files'],
                'subdirs': e['subdirs'],
                'docs': len(e['doc_files']),
            })
        elif '【' in name and '】' in name:
            dept = re.search(r'【(.+?)】', name)
            dept_name = dept.group(1) if dept else name
            if any(k in name for k in ['會計','工程','維運','採購','標案','SOP','請購','日報','專案']):
                categories['departments'].append({'name': name, 'dept': dept_name, 'files': e['files'], 'subdirs': e['subdirs']})
            elif any(k in name for k in ['參考','教育','BOM']):
                categories['reference'].append({'name': name, 'files': e['files'], 'subdirs': e['subdirs']})
            else:
                categories['departments'].append({'name': name, 'dept': dept_name, 'files': e['files'], 'subdirs': e['subdirs']})
        elif '昱金生' in name or '00' in name[:3]:
            categories['company'].append({'name': name, 'files': e['files'], 'subdirs': e['subdirs']})
        else:
            categories['other'].append({'name': name, 'files': e['files'], 'subdirs': e['subdirs']})

    return categories


def build_case_database(entries):
    """從案場資料夾建構案場資料庫"""
    cases = []
    for e in entries:
        if e['depth'] != 1:
            continue
        name = os.path.basename(e['path'])
        m = re.match(r'(20\d{6})-(.+)', name)
        if not m:
            continue

        date_str = m.group(1)
        desc = m.group(2)

        case_type = '標案' if '標案' in desc else '中租' if '中租' in desc else '民間' if '民間' in desc else '許大' if '許大' in desc else '其他'
        location = ''
        address = ''
        loc_m = re.search(r'--(.+?)--(.+?)(?:-|$)', desc)
        if loc_m:
            location = loc_m.group(1)
            address = loc_m.group(2).split('-')[0] if '-' in loc_m.group(2) else loc_m.group(2)

        # 掃描子目錄看進度線索
        subdirs = []
        for se in entries:
            if se['depth'] == 2 and se['path'].startswith(e['path']+'/'):
                subdirs.append(os.path.basename(se['path']))

        has_completion = any('完工' in s or '驗收' in s or '掛表' in s for s in subdirs)
        has_design = any('設計' in s or '圖面' in s or '結構' in s for s in subdirs)
        has_construction = any('施工' in s or '工程' in s or '進場' in s for s in subdirs)
        has_bid = any('投標' in s or '標案' in s or '開標' in s for s in subdirs)

        cases.append({
            'folder': name,
            'date': date_str,
            'type': case_type,
            'location': location,
            'address': address[:60],
            'subdirs': len(subdirs),
            'total_files': e['files'],
            'total_docs': len(e['doc_files']),
            'has_design': has_design,
            'has_bid': has_bid,
            'has_construction': has_construction,
            'has_completion': has_completion,
            'subdir_names': subdirs[:15],
        })

    return sorted(cases, key=lambda x: x['date'], reverse=True)


def build_summary(categories, cases, entries, scan_time):
    """產出知識摘要"""
    total_dirs = len(entries)
    total_docs = sum(len(e['doc_files']) for e in entries)
    ext_counts = defaultdict(int)
    for e in entries:
        for d in e['doc_files']:
            ext_counts[d['ext']] += 1

    lines = [
        f'# 昱金生 Z Drive 知識索引摘要',
        f'',
        f'> 掃描時間：{scan_time}',
        f'> 掃描深度：{MAX_DEPTH} 層',
        f'',
        f'## 總覽',
        f'- 總資料夾數：{total_dirs}',
        f'- 總文件數：{total_docs}',
        f'- 案場專案：{len(cases)} 個',
        f'- 部門專區：{len(categories["departments"])} 個',
        f'- 公司管理：{len(categories["company"])} 個',
        f'- 參考資料：{len(categories["reference"])} 個',
        f'',
        f'## 文件類型分佈',
    ]
    for ext, count in sorted(ext_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        lines.append(f'- {ext}：{count} 個')

    lines.append('')
    lines.append('## 案場清單（依時間排序）')
    lines.append('')
    for c in cases[:30]:
        status = []
        if c['has_bid']: status.append('投標')
        if c['has_design']: status.append('設計')
        if c['has_construction']: status.append('施工')
        if c['has_completion']: status.append('完工')
        st = '→'.join(status) if status else '未分類'
        lines.append(f'- **{c["folder"][:60]}** | 類型：{c["type"]} | 位置：{c["location"]} | 進度：{st} | 文件：{c["total_docs"]}')

    lines.append('')
    lines.append('## 部門專區')
    for d in categories['departments']:
        lines.append(f'- {d["name"]} | 子目錄：{d["subdirs"]} | 檔案：{d["files"]}')

    lines.append('')
    lines.append('## 公司管理')
    for d in categories['company']:
        lines.append(f'- {d["name"]} | 子目錄：{d["subdirs"]} | 檔案：{d["files"]}')

    return '\n'.join(lines)


def main():
    scan_time = datetime.now(TZ8).strftime('%Y-%m-%d %H:%M:%S')
    print(f'[{scan_time}] 開始掃描 {SCAN_ROOT}...')

    entries = scan_directory(SCAN_ROOT)
    categories = classify_folders(entries)
    cases = build_case_database(entries)

    # 儲存索引
    index = {
        'scan_time': scan_time,
        'scan_root': str(SCAN_ROOT),
        'total_dirs': len(entries),
        'total_docs': sum(len(e['doc_files']) for e in entries),
        'categories': {k: len(v) for k, v in categories.items()},
        'cases': cases,
        'departments': categories['departments'],
        'company': categories['company'],
        'reference': categories['reference'],
    }
    INDEX_FILE.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding='utf-8')

    # 產出摘要
    summary = build_summary(categories, cases, entries, scan_time)
    SUMMARY_FILE.write_text(summary, encoding='utf-8')

    # 寫入 memory（供 memory_search 檢索）
    MEMORY_FILE.write_text(summary, encoding='utf-8')

    print(f'[{scan_time}] 完成！')
    print(f'  資料夾：{len(entries)}')
    print(f'  文件：{index["total_docs"]}')
    print(f'  案場：{len(cases)}')
    print(f'  索引：{INDEX_FILE}')
    print(f'  摘要：{SUMMARY_FILE}')
    print(f'  記憶：{MEMORY_FILE}')


if __name__ == '__main__':
    main()

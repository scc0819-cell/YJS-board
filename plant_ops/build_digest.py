#!/usr/bin/env python3
import json
from pathlib import Path

def main():
    base = Path(__file__).resolve().parent
    events = json.loads((base/'output/events.json').read_text(encoding='utf-8'))
    p1=[e for e in events if e['severity']=='P1']
    p2=[e for e in events if e['severity']=='P2']
    p3=[e for e in events if e['severity']=='P3']

    lines=[]
    lines.append('🟠 每小時維運摘要')
    lines.append('━━━━━━━━━━━━━━━━')
    lines.append(f"P1/P2/P3：{len(p1)}/{len(p2)}/{len(p3)}")
    lines.append('')
    for e in p1+p2+p3:
        lines.append(f"- [{e['severity']}] {e['plant_name']} | 落差 {e['gen_gap_pct']}% | 可用率 {e['inverter_availability_pct']}% | 原因：{'; '.join(e['reasons'])}")

    out='\n'.join(lines)
    (base/'output/hourly_digest.txt').write_text(out, encoding='utf-8')
    print(base/'output/hourly_digest.txt')

if __name__=='__main__':
    main()

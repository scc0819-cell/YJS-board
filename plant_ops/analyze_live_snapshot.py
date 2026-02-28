#!/usr/bin/env python3
import csv, json
from pathlib import Path
from datetime import datetime, timezone, timedelta

TZ8=timezone(timedelta(hours=8))

def parse_dt(s):
    try:
        return datetime.strptime(s,'%Y/%m/%d %H:%M:%S').replace(tzinfo=TZ8)
    except Exception:
        return None

base=Path(__file__).resolve().parent
csv_path=base/'data/auo_per_plant_live_88.csv'
rows=[]
with csv_path.open('r',encoding='utf-8') as f:
    for r in csv.DictReader(f):
        dt=parse_dt(r.get('collection_time',''))
        age=None
        if dt:
            age=round((datetime.now(TZ8)-dt).total_seconds()/60)
        rows.append({
            'plant_id':r['plant_id'],'plant_name':r['plant_name'],'state':r['state'],'city':r['city'],
            'capacity_kw':float(r['capacity_kw'] or 0),'collection_time':r['collection_time'],'data_age_min':age,
            'ac_kw':float(r['ac_kw'] or 0),'radiation':float(r['radiation'] or 0),'alert_num':int(float(r['alert_num'] or 0))
        })

summary={
    'captured_at': datetime.now(TZ8).isoformat(timespec='seconds'),
    'total_plants': len(rows),
    'total_capacity_kw': round(sum(r['capacity_kw'] for r in rows),2),
    'stale_over_180m': sum(1 for r in rows if r['data_age_min'] is not None and r['data_age_min']>180),
    'tiny_capacity_sites': sum(1 for r in rows if r['capacity_kw']<=0.001),
    'high_alert_sites': sum(1 for r in rows if r['alert_num']>=3),
}

state_dist={}
for r in rows:
    state_dist[r['state']]=state_dist.get(r['state'],0)+1
summary['top_states']=sorted(state_dist.items(), key=lambda x:x[1], reverse=True)[:6]
summary['top_stale']=sorted([r for r in rows if r['data_age_min'] is not None], key=lambda x:x['data_age_min'], reverse=True)[:10]
summary['top_alert']=sorted(rows,key=lambda x:x['alert_num'], reverse=True)[:10]

out=base/'output/live_snapshot_analysis.json'
out.write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(out)

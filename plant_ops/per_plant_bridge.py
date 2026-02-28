#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta

TZ8 = timezone(timedelta(hours=8))

def main():
    base=Path(__file__).resolve().parent
    src=base/'data/auo_per_plant_sample.json'
    plants=json.loads(src.read_text(encoding='utf-8'))
    ts=datetime.now(TZ8).isoformat(timespec='seconds')

    # v1 bridge: 先把明細轉為規則引擎可讀格式（forecast/irr/weather 待下一步接真值）
    recs=[]
    for p in plants:
        actual=max(float(p['capacity_kw'])*0.6, 1.0)  # 模擬值：待接真實逐站發電
        forecast=max(float(p['capacity_kw'])*0.62, 1.0)
        recs.append({
            'plant_id': p['plant_id'],
            'plant_name': p['plant_name'],
            'timestamp': ts,
            'actual_gen_kwh_today': round(actual,2),
            'forecast_gen_kwh_today': round(forecast,2),
            'design_offset_enabled': False,
            'design_offset_factor': 1.0,
            'weather_icon': 'unknown',
            'irr_today': 0.0,
            'irr_yday_slot': 0.0,
            'inverter_availability_pct': 100.0 if int(p.get('status',1))==1 else 70.0,
            'data_gap_min': 0
        })

    out=base/'data/auo_per_plant_hourly_records.json'
    out.write_text(json.dumps(recs, ensure_ascii=False, indent=2), encoding='utf-8')
    print(out)

if __name__=='__main__':
    main()

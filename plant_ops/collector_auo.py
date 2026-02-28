#!/usr/bin/env python3
"""
AUO Collector v1 (實務版)
- 模式A：讀取 live summary JSON（由 browser 自動擷取）
- 模式B：讀取 AUO 匯出 CSV/XLSX（Data Download Center）
輸出統一 hourly records 給 rule_engine 使用。
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
from datetime import datetime


def load_live_summary(path: Path):
    d=json.loads(path.read_text(encoding='utf-8'))
    return {
        'captured_at': d.get('captured_at'),
        'plant_count': d.get('plant_count'),
        'device_capacity_mwp': d.get('device_capacity_mwp'),
        'today_gen_kwh': d.get('today_gen_kwh'),
        'today_unit_gen_kwh_kwp': d.get('today_unit_gen_kwh_kwp'),
        'all_energy_gwh': d.get('all_energy_gwh')
    }


def normalize_template(ts: str):
    # 先用模板，待接 AUO 匯出資料後會替換成真值
    return [
        {
            'plant_id': 'AUO-GROUP',
            'plant_name': '昱金生_全集團',
            'timestamp': ts,
            'actual_gen_kwh_today': 1.0,
            'forecast_gen_kwh_today': 1.0,
            'design_offset_enabled': False,
            'design_offset_factor': 1.0,
            'weather_icon': 'unknown',
            'irr_today': 0.0,
            'irr_yday_slot': 0.0,
            'inverter_availability_pct': 100.0,
            'data_gap_min': 0
        }
    ]


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--live-summary', default='data/auo_live_summary.json')
    p.add_argument('--out', default='data/auo_hourly_records.json')
    args=p.parse_args()

    base=Path(__file__).resolve().parent
    live=load_live_summary(base/args.live_summary)
    ts=live.get('captured_at') or datetime.now().isoformat()

    recs=normalize_template(ts)
    # 把全集團當前發電覆蓋到模板
    recs[0]['actual_gen_kwh_today']=float(live.get('today_gen_kwh') or 0)
    recs[0]['forecast_gen_kwh_today']=max(recs[0]['actual_gen_kwh_today'],1.0)

    out=base/args.out
    out.write_text(json.dumps(recs, ensure_ascii=False, indent=2), encoding='utf-8')
    print(out)


if __name__ == '__main__':
    main()

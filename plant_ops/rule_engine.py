#!/usr/bin/env python3
import json, yaml
from pathlib import Path

def weather_mode(rec, cfg):
    icon = (rec.get('weather_icon') or 'unknown').lower()
    irr_today = float(rec.get('irr_today') or 0)
    irr_yday = float(rec.get('irr_yday_slot') or 0)
    irr_delta = ((irr_today - irr_yday) / irr_yday * 100) if irr_yday > 0 else 0
    if icon in ('cloudy','rainy') or irr_delta <= -15:
        return 'rainy', irr_delta
    return 'sunny', irr_delta

def evaluate_record(rec, cfg):
    wf = cfg['weather_factor'].get((rec.get('weather_icon') or 'unknown').lower(), 1.0)
    offset = rec['design_offset_factor'] if rec.get('design_offset_enabled') else 1.0
    adj_forecast = rec['forecast_gen_kwh_today'] * offset * wf
    gap = ((rec['actual_gen_kwh_today'] - adj_forecast) / adj_forecast * 100) if adj_forecast > 0 else 0
    ach = (rec['actual_gen_kwh_today'] / adj_forecast * 100) if adj_forecast > 0 else 0
    mode, irr_delta = weather_mode(rec, cfg)

    sev = 'OK'
    reasons = []

    strict_threshold = cfg['thresholds']['strict']['threshold']
    if rec.get('strict_mode_enabled', cfg['thresholds']['strict']['default_enabled']) and mode == 'sunny' and gap <= strict_threshold:
        sev = 'P2'; reasons.append(f'strict_mode gap={gap:.2f}% <= {strict_threshold}%')

    if mode == 'sunny':
        if gap <= cfg['thresholds']['sunny']['p1']:
            sev = 'P1'; reasons.append(f'sunny gap={gap:.2f}% <= {cfg["thresholds"]["sunny"]["p1"]}%')
        elif gap <= cfg['thresholds']['sunny']['p2'] and sev != 'P1':
            sev = 'P2'; reasons.append(f'sunny gap={gap:.2f}% <= {cfg["thresholds"]["sunny"]["p2"]}%')
        elif gap <= cfg['thresholds']['sunny']['p3'] and sev == 'OK':
            sev = 'P3'; reasons.append(f'sunny gap={gap:.2f}% <= {cfg["thresholds"]["sunny"]["p3"]}%')
    else:
        # rainy mode uses data completeness + availability signals as primary
        if rec['data_gap_min'] >= cfg['thresholds']['data_gap']['p2_min']:
            sev = max(sev, 'P2', key=lambda x:['OK','P3','P2','P1'].index(x)); reasons.append('rainy + data gap >=30m')

    if rec['inverter_availability_pct'] < cfg['thresholds']['availability']['p1_lt']:
        sev = 'P1'; reasons.append('availability < 50%')
    elif rec['inverter_availability_pct'] < cfg['thresholds']['availability']['p2_lt'] and sev != 'P1':
        sev = 'P2'; reasons.append('availability < 85%')

    if rec['data_gap_min'] >= cfg['thresholds']['data_gap']['p2_min'] and sev != 'P1':
        sev = 'P2'; reasons.append('data gap >= 30m')
    elif rec['data_gap_min'] >= cfg['thresholds']['data_gap']['p3_min'] and sev == 'OK':
        sev = 'P3'; reasons.append('data gap >= 10m')

    return {
        **rec,
        'mode': mode,
        'irr_delta_pct': round(irr_delta,2),
        'adj_forecast_gen_kwh_today': round(adj_forecast,2),
        'gen_gap_pct': round(gap,2),
        'gen_achievement_rate_pct': round(ach,2),
        'severity': sev,
        'reasons': reasons
    }

def run(input_path, rules_path, output_path):
    recs = json.loads(Path(input_path).read_text(encoding='utf-8'))
    cfg = yaml.safe_load(Path(rules_path).read_text(encoding='utf-8'))
    out = [evaluate_record(r, cfg) for r in recs]
    Path(output_path).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    return out

if __name__ == '__main__':
    base = Path(__file__).resolve().parent
    out = run(base/'data/sample_plants_hourly.json', base/'config/rules_v1_1.yaml', base/'output/events.json')
    print(f'generated events: {len(out)} -> {base / "output/events.json"}')

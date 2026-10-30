import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))
from actions.action_manager import handle_risk

LOG_PATH = BASE_DIR / 'scripts' / 'logs' / 'system_metrics.log'
OUTPUT_DIR = BASE_DIR / 'outputs'
METRICS = ['cpu_percent', 'ram_percent', 'disk_percent', 'swap_percent', 'disk_read_bytes', 'disk_write_bytes', 'net_bytes_sent', 'net_bytes_recv']

def load_logs():
    if not LOG_PATH.exists():
        raise FileNotFoundError(f'Metrics log missing: {LOG_PATH}')
    rows = []
    bad = 0
    for line in LOG_PATH.read_text(encoding='utf-8').splitlines():
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            bad += 1
    df = pd.DataFrame(rows)
    if df.empty or 'timestamp' not in df.columns:
        raise ValueError('No valid metrics in log')
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce', format='mixed', utc=True).dt.tz_convert(None)
    for metric in METRICS:
        df[metric] = pd.to_numeric(df.get(metric), errors='coerce') if metric in df.columns else np.nan
    df = df.dropna(subset=['timestamp', *METRICS]).sort_values('timestamp')
    if len(df) < 2:
        raise ValueError('At least two valid metrics samples are required')
    print(f'Loaded {len(df)} rows, skipped {bad} invalid JSON lines')
    return df

def engineer_features(df):
    df = df.set_index('timestamp')
    df_1m = df.resample('1min').agg({m: ['mean', 'max'] for m in METRICS})
    df_1m.columns = ['_'.join(c) for c in df_1m.columns]
    df_1m = df_1m.ffill().dropna()
    for m in ['disk_read_bytes', 'disk_write_bytes', 'net_bytes_sent', 'net_bytes_recv']:
        df_1m[f'{m}_rate'] = df_1m[f'{m}_mean'].diff().clip(lower=0).fillna(0)
    return df_1m.reset_index()

def run_isolation_forest(df_feat):
    X = df_feat.drop(columns=['timestamp']).replace([np.inf, -np.inf], np.nan).fillna(0)
    model = IsolationForest(n_estimators=200, contamination=0.15, random_state=42)
    df_feat = df_feat.copy()
    df_feat['anomaly_flag'] = (model.fit_predict(X) == -1).astype(int)
    return df_feat

def calculate_risk(df_feat):
    reasons, risk = [], 0
    last = df_feat.iloc[-1]
    recent_5m = df_feat.tail(5)
    recent_10m = df_feat.tail(10)
    if last['cpu_percent_max'] >= 70:
        risk += 20; reasons.append('CPU spike (>=70)')
    if recent_5m['cpu_percent_mean'].mean() >= 60:
        risk += 15; reasons.append('CPU high (persistent)')
    if recent_5m['ram_percent_mean'].mean() >= 60:
        risk += 15; reasons.append('RAM high (persistent)')
    if last['disk_percent_max'] >= 90:
        risk += 20; reasons.append('Disk critically full')
    if last.get('disk_read_bytes_rate', 0) > 0:
        risk += 10; reasons.append('Disk read rate activity')
    if last.get('disk_write_bytes_rate', 0) > 0:
        risk += 10; reasons.append('Disk write rate activity')
    if recent_5m['cpu_percent_mean'].mean() >= 80 and recent_5m['ram_percent_mean'].mean() >= 80:
        risk += 15; reasons.append('CPU + RAM high')
    if recent_5m['cpu_percent_mean'].mean() >= 80 and last.get('disk_read_bytes_rate', 0) > 0:
        risk += 10; reasons.append('CPU + disk activity')
    ml_ratio = float(recent_10m['anomaly_flag'].mean())
    if ml_ratio >= 0.40:
        risk += 20; reasons.append('ML anomaly density >=40%')
    risk = min(100, risk)
    level = 'LOW' if risk < 30 else 'MEDIUM' if risk < 40 else 'HIGH' if risk < 60 else 'CRITICAL'
    return level, risk, reasons, ml_ratio

def main():
    df_feat = run_isolation_forest(engineer_features(load_logs()))
    level, score, reasons, ratio = calculate_risk(df_feat)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df_feat.to_csv(OUTPUT_DIR / 'anomaly_results.csv', index=False)
    df_feat[df_feat['anomaly_flag'] == 1].to_csv(OUTPUT_DIR / 'anomalies_only.csv', index=False)
    print(f'Risk: {level} ({score}/100) @ {df_feat["timestamp"].iloc[-1]}')
    print('Reasons:', reasons, 'ML ratio:', ratio)
    handle_risk(level)

if __name__ == '__main__':
    main()

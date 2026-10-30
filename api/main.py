import json
import os
import ipaddress
from fastapi import Request
import subprocess
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

BASE_DIR = Path(__file__).resolve().parents[1]
HISTORY_FILE = BASE_DIR / 'outputs' / 'train_history.json'
METRICS_LOG_FILE = BASE_DIR / 'scripts' / 'logs' / 'system_metrics.log'
ANOMALIES_FILE = BASE_DIR / 'outputs' / 'anomalies_only.csv'
app = FastAPI(title='ML Supported DR System', version='1.0.0')
app.add_middleware(CORSMiddleware, allow_origins=['http://localhost:5173', 'http://127.0.0.1:5173'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])

@app.post('/api/train/run')
def run_train(request: Request):
    # Fail closed: local-only and explicit opt-in for AWS-impacting operations.
    try:
        peer = ipaddress.ip_address(request.client.host) if request.client else None
    except ValueError:
        peer = None
    if not peer or not peer.is_loopback:
        raise HTTPException(status_code=403, detail="Training endpoint is local-only")
    if os.getenv("ENABLE_AWS_ACTIONS") != "I_UNDERSTAND_AWS_CHANGES":
        raise HTTPException(status_code=403, detail="AWS actions disabled by default; see README")
    # WARNING: this invokes AWS operations for CRITICAL risk; restrict this endpoint before public deployment.
    try:
        proc = subprocess.run([sys.executable, 'scripts/run_and_report.py'], cwd=BASE_DIR, capture_output=True, text=True, timeout=1800)
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail='Training/recovery timed out')
    if proc.returncode:
        raise HTTPException(status_code=500, detail={'exit_code': proc.returncode, 'output': proc.stdout[-4000:], 'error': proc.stderr[-2000:]})
    return {'status': 'completed', 'output': proc.stdout[-4000:]}

@app.get('/api/train/history')
def get_train_history():
    if not HISTORY_FILE.exists():
        return []
    with HISTORY_FILE.open(encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()][::-1]

@app.get('/api/metrics')
def get_live_metrics():
    if not METRICS_LOG_FILE.exists():
        return []
    with METRICS_LOG_FILE.open(encoding='utf-8') as f:
        lines = f.readlines()[-30:]
    return [json.loads(line) for line in lines if line.strip() and 'timestamp' in json.loads(line)]

@app.get('/api/anomalies')
def get_anomalies():
    if not ANOMALIES_FILE.exists():
        return []
    import csv
    with ANOMALIES_FILE.open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))

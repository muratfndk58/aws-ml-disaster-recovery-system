import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = BASE_DIR / 'actions' / 'config.json'
OUTPUT_FILE = BASE_DIR / 'outputs' / 'train_history.json'

def load_backup_paths():
    try:
        return json.loads(CONFIG_PATH.read_text(encoding='utf-8')).get('backup_paths', [])
    except (OSError, ValueError):
        return []

def get_path_size_mb(path):
    total = 0
    if os.path.isfile(path):
        total = os.path.getsize(path)
    elif os.path.isdir(path):
        for root, _, files in os.walk(path):
            for f in files:
                try:
                    total += os.path.getsize(os.path.join(root, f))
                except OSError:
                    pass
    return round(total / 1024**2, 2)

def main():
    start_time = time.monotonic()
    snapshot_time = recovery_ready_time = None
    print('Train + recovery started', flush=True)
    proc = subprocess.Popen([sys.executable, '-u', 'scripts/train_model.py'], cwd=BASE_DIR, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    try:
        for line in proc.stdout:
            print(line, end='')
            upper = line.upper()
            if snapshot_time is None and 'SNAPSHOT CREATED:' in upper:
                snapshot_time = time.monotonic()
            if 'RECOVERY_READY' in upper:
                recovery_ready_time = time.monotonic()
        exit_code = proc.wait()
    except KeyboardInterrupt:
        proc.terminate()
        exit_code = proc.wait()
    backup_taken = recovery_ready_time is not None and exit_code == 0
    backup_items = [{'path': path, 'size_mb': get_path_size_mb(path)} for path in load_backup_paths()] if backup_taken else []
    report = {'date': datetime.now().strftime('%Y-%m-%d'), 'time': datetime.now().strftime('%H:%M:%S'), 'backup': 'TAKEN' if backup_taken else 'SKIPPED', 'rto_seconds': round(recovery_ready_time - start_time, 2) if backup_taken else None, 'rpo_seconds': None, 'backup_items': backup_items, 'total_backup_mb': round(sum(i['size_mb'] for i in backup_items), 2) if backup_taken else None, 'exit_code': exit_code}
    # RPO cannot be inferred from wall-clock elapsed time; requires actual recovery point timestamp.
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_FILE.open('a', encoding='utf-8') as f:
        f.write(json.dumps(report) + '\n')
    print('RUN COMPLETED:', report)
    return exit_code

if __name__ == '__main__':
    sys.exit(main())

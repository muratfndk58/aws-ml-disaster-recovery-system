#!/usr/bin/env python3
import json
import time
from datetime import datetime
from pathlib import Path
import psutil
import pytz

LOG_FILE = Path(__file__).resolve().parent / 'logs' / 'system_metrics.log'
INTERVAL_SECONDS = 60
TURKEY_TZ = pytz.timezone('Europe/Istanbul')

def collect_metrics():
    disk_io = psutil.disk_io_counters()
    net_io = psutil.net_io_counters()
    return {'timestamp': datetime.now(TURKEY_TZ).isoformat(), 'cpu_percent': psutil.cpu_percent(interval=1), 'ram_percent': psutil.virtual_memory().percent, 'disk_percent': psutil.disk_usage('/').percent, 'swap_percent': psutil.swap_memory().percent, 'disk_read_bytes': disk_io.read_bytes if disk_io else 0, 'disk_write_bytes': disk_io.write_bytes if disk_io else 0, 'net_bytes_sent': net_io.bytes_sent if net_io else 0, 'net_bytes_recv': net_io.bytes_recv if net_io else 0}

def write_log(data):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open('a', encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=False) + '\n')

def main():
    print('EC2 Monitor started (Europe/Istanbul)')
    while True:
        try:
            metrics = collect_metrics()
            write_log(metrics)
            print('Logged @', metrics['timestamp'])
        except Exception as exc:
            write_log({'timestamp': datetime.now(TURKEY_TZ).isoformat(), 'error': str(exc)})
        time.sleep(INTERVAL_SECONDS)

if __name__ == '__main__':
    main()

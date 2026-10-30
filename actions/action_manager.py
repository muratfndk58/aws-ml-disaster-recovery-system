import json
import time
from pathlib import Path
import boto3
from actions.snapshot_manager import take_snapshot
from actions.green_recovery_manager import full_auto_recovery
from actions.eip_manager import load_config, find_instance_id_by_tag, move_eip

STATE_FILE = Path(__file__).resolve().parent / 'incident_state.json'
DEFAULT_STATE = {'incident_active': False, 'snapshot_id': None, 'failover_in_progress': False, 'failed_over': False, 'active_instance': 'blue', 'critical_latched': False, 'last_failover_time': None, 'last_error': None, 'green_instance_id': None}

def load_state():
    if not STATE_FILE.exists():
        save_state(DEFAULT_STATE.copy())
    return {**DEFAULT_STATE, **json.loads(STATE_FILE.read_text(encoding='utf-8'))}

def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding='utf-8')

def reset_state():
    state = DEFAULT_STATE.copy()
    save_state(state)
    return state

def find_root_volume(ec2, instance_id):
    resp = ec2.describe_instances(InstanceIds=[instance_id])
    inst = resp['Reservations'][0]['Instances'][0]
    root_device = inst.get('RootDeviceName')
    mappings = inst['BlockDeviceMappings']
    root = next((m for m in mappings if m['DeviceName'] == root_device), None)
    if not root or 'Ebs' not in root:
        raise RuntimeError('Root EBS volume not found')
    return root['Ebs']['VolumeId'], root_device

def find_root_volume_id(ec2, instance_id):
    return find_root_volume(ec2, instance_id)[0]

def handle_risk(risk_level):
    cfg = load_config()
    ec2 = boto3.client('ec2', region_name=cfg['region'])
    state = load_state()
    print('[ACTION] Current state:', state)
    if risk_level in ('LOW', 'MEDIUM', 'HIGH'):
        # Do not erase the record of an already completed failover.
        if state['incident_active'] and not state['failed_over'] and not state['failover_in_progress']:
            reset_state()
        return
    if risk_level != 'CRITICAL' or state['failed_over']:
        return
    if state['failover_in_progress']:
        print('Failover already in progress; skipping duplicate request')
        return
    state['incident_active'] = True
    state['critical_latched'] = True
    state['failover_in_progress'] = True
    save_state(state)
    try:
        if not state['snapshot_id']:
            blue_id = find_instance_id_by_tag(ec2, cfg['blue_tag_key'], cfg['blue_tag_value'])
            volume_id, root_device = find_root_volume(ec2, blue_id)
            snapshot_id = take_snapshot(volume_id, 'critical', 'CRITICAL', region=cfg['region'])
            state['snapshot_id'] = snapshot_id
            state['root_device'] = root_device
            save_state(state)
        if not state['green_instance_id']:
            green_id = full_auto_recovery(state['snapshot_id'], root_device=state.get('root_device', '/dev/sda1'))
            state['green_instance_id'] = green_id
            save_state(state)
        public_ip, _ = move_eip(cfg['eip_allocation_id'], state['green_instance_id'], cfg['region'])
        state.update(failed_over=True, active_instance='green', last_failover_time=time.time(), last_error=None)
        print(f'Elastic IP moved to GREEN: {public_ip}')
        print('RECOVERY_READY')
    except Exception as exc:
        state['last_error'] = str(exc)
        print('FAILOVER FAILED:', exc)
        raise
    finally:
        state['failover_in_progress'] = False
        save_state(state)

import os
import json
import time
from pathlib import Path
from typing import Optional
import boto3

def load_config():
    config_path = Path(os.environ.get('ML_BACKUP_CONFIG', str(Path(__file__).resolve().parent / 'config.json')))
    cfg = json.loads(config_path.read_text(encoding='utf-8'))
    required = ('eip_allocation_id', 'subnet_id', 'iam_instance_profile', 'key_name')
    if any(not cfg.get(k) or cfg[k] == 'REPLACE_ME' for k in required) or not cfg.get('security_group_ids') or any(x == 'REPLACE_ME' for x in cfg['security_group_ids']):
        raise ValueError('AWS resource IDs missing: configure private actions/config.json')
    return cfg

def ec2_client(region):
    return boto3.client('ec2', region_name=region)

def find_instance_id_by_tag(ec2, tag_key, tag_value):
    resp = ec2.describe_instances(Filters=[{'Name': f'tag:{tag_key}', 'Values': [tag_value]}, {'Name': 'instance-state-name', 'Values': ['pending', 'running', 'stopping', 'stopped']}])
    ids = [inst['InstanceId'] for r in resp.get('Reservations', []) for inst in r.get('Instances', [])]
    if len(ids) != 1:
        raise RuntimeError(f'Expected exactly one instance for {tag_key}={tag_value}, got {ids}')
    return ids[0]

def get_eip_state(ec2, allocation_id):
    resp = ec2.describe_addresses(AllocationIds=[allocation_id])
    if not resp.get('Addresses'):
        raise RuntimeError(f'EIP not found: {allocation_id}')
    return resp['Addresses'][0]

def wait_eip_points_to_instance(ec2, allocation_id, instance_id, timeout_sec=120):
    deadline = time.monotonic() + timeout_sec
    while time.monotonic() < deadline:
        if get_eip_state(ec2, allocation_id).get('InstanceId') == instance_id:
            return
        time.sleep(3)
    raise TimeoutError(f'EIP {allocation_id} did not move to {instance_id}')

def move_eip(allocation_id, target_instance_id, region):
    ec2 = ec2_client(region)
    before = get_eip_state(ec2, allocation_id)
    # AllowReassociation avoids an unnecessary disconnected interval.
    ec2.associate_address(AllocationId=allocation_id, InstanceId=target_instance_id, AllowReassociation=True)
    wait_eip_points_to_instance(ec2, allocation_id, target_instance_id)
    after = get_eip_state(ec2, allocation_id)
    return after.get('PublicIp', ''), before.get('InstanceId')

def rollback_eip(allocation_id, blue_instance_id, region):
    return move_eip(allocation_id, blue_instance_id, region)[0]

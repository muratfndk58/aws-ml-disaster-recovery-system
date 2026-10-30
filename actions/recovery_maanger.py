import time
import urllib.request
import boto3

IMDS_BASE = 'http://169.254.169.254/latest'

def _imds_token(ttl_seconds=21600):
    req = urllib.request.Request(f'{IMDS_BASE}/api/token', method='PUT', headers={'X-aws-ec2-metadata-token-ttl-seconds': str(ttl_seconds)})
    with urllib.request.urlopen(req, timeout=2) as resp:
        return resp.read().decode()

def _imds_get(path, token):
    req = urllib.request.Request(f'{IMDS_BASE}/{path}', headers={'X-aws-ec2-metadata-token': token})
    with urllib.request.urlopen(req, timeout=2) as resp:
        return resp.read().decode()

def get_identity():
    token = _imds_token()
    return (_imds_get('meta-data/instance-id', token), _imds_get('meta-data/placement/region', token), _imds_get('meta-data/placement/availability-zone', token))

def wait_for_volume(ec2, volume_id, target_state='available', timeout_sec=300):
    deadline = time.monotonic() + timeout_sec
    while time.monotonic() < deadline:
        vol = ec2.describe_volumes(VolumeIds=[volume_id])['Volumes'][0]
        if vol['State'] == target_state:
            return vol
        time.sleep(5)
    raise TimeoutError(f'Volume {volume_id} did not reach {target_state}')

def create_volume_from_snapshot(snapshot_id, tag_project='ml-backup-system'):
    _, region, az = get_identity()
    ec2 = boto3.client('ec2', region_name=region)
    resp = ec2.create_volume(SnapshotId=snapshot_id, AvailabilityZone=az, VolumeType='gp3', TagSpecifications=[{'ResourceType': 'volume', 'Tags': [{'Key': 'Project', 'Value': tag_project}, {'Key': 'CreatedBy', 'Value': 'ml-backup-system-recovery'}, {'Key': 'SourceSnapshot', 'Value': snapshot_id}]}])
    volume_id = resp['VolumeId']
    wait_for_volume(ec2, volume_id)
    return volume_id

def attach_volume(volume_id, device='/dev/sdf'):
    instance_id, region, _ = get_identity()
    ec2 = boto3.client('ec2', region_name=region)
    ec2.attach_volume(VolumeId=volume_id, InstanceId=instance_id, Device=device)
    wait_for_volume(ec2, volume_id, target_state='in-use')
    return True

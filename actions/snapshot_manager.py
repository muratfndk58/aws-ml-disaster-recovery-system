import boto3
from datetime import datetime, timezone

def take_snapshot(volume_id: str, snapshot_type: str, risk_level: str, region='eu-central-1'):
    ec2 = boto3.client('ec2', region_name=region)
    now = datetime.now(timezone.utc).isoformat()
    resp = ec2.create_snapshot(VolumeId=volume_id, Description=f'{snapshot_type} snapshot ({risk_level}) at {now}', TagSpecifications=[{'ResourceType': 'snapshot', 'Tags': [{'Key': 'type', 'Value': snapshot_type}, {'Key': 'risk', 'Value': risk_level}, {'Key': 'created_at', 'Value': now}]}])
    snapshot_id = resp['SnapshotId']
    print('Snapshot created:', snapshot_id)
    ec2.get_waiter('snapshot_completed').wait(SnapshotIds=[snapshot_id])
    print('Snapshot completed:', snapshot_id)
    return snapshot_id

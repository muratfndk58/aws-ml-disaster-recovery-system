import time
import boto3
from actions.eip_manager import load_config
from actions.green_ready import wait_green_ready_by_tag

# This function creates GREEN but deliberately DOES NOT move EIP.
# The action manager owns failover, ensuring state is saved exactly once.
def register_ami_from_snapshot(snapshot_id, ec2, root_device='/dev/sda1'):
    name = f'green-recovery-{snapshot_id}-{int(time.time())}'
    resp = ec2.register_image(Name=name, Architecture='x86_64', RootDeviceName=root_device, VirtualizationType='hvm', BlockDeviceMappings=[{'DeviceName': root_device, 'Ebs': {'SnapshotId': snapshot_id, 'DeleteOnTermination': True, 'VolumeType': 'gp3'}}])
    ami_id = resp['ImageId']
    ec2.get_waiter('image_available').wait(ImageIds=[ami_id])
    return ami_id

def full_auto_recovery(snapshot_id, root_device='/dev/sda1'):
    cfg = load_config()
    region = cfg['region']
    ec2 = boto3.client('ec2', region_name=region)
    ec2.get_waiter('snapshot_completed').wait(SnapshotIds=[snapshot_id])
    ami_id = register_ami_from_snapshot(snapshot_id, ec2, root_device)
    # IMDSv2 is required; cloud-init marks restore=ok only after startup script completes.
    user_data = r'''#!/bin/bash
set -e
exec > >(tee /var/log/auto_restore.log) 2>&1
TOKEN=$(curl -fsS -X PUT -H 'X-aws-ec2-metadata-token-ttl-seconds: 21600' http://169.254.169.254/latest/api/token)
INSTANCE_ID=$(curl -fsS -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/instance-id)
REGION=$(curl -fsS -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/placement/region)
if ! command -v aws >/dev/null 2>&1; then apt-get update -y && apt-get install -y awscli; fi
aws ec2 create-tags --region "$REGION" --resources "$INSTANCE_ID" --tags Key=restore,Value=ok
echo '[READY] restore=ok tag applied'
'''
    resp = ec2.run_instances(ImageId=ami_id, InstanceType=cfg.get('instance_type', 't3.micro'), MinCount=1, MaxCount=1, SubnetId=cfg['subnet_id'], SecurityGroupIds=cfg['security_group_ids'], KeyName=cfg['key_name'], IamInstanceProfile={'Name': cfg['iam_instance_profile']}, UserData=user_data, MetadataOptions={'HttpTokens': 'required'}, TagSpecifications=[{'ResourceType': 'instance', 'Tags': [{'Key': 'role', 'Value': 'green'}, {'Key': 'dr', 'Value': 'bluegreen'}]}])
    green_id = resp['Instances'][0]['InstanceId']
    print('GREEN instance created:', green_id)
    ec2.get_waiter('instance_running').wait(InstanceIds=[green_id])
    wait_green_ready_by_tag(region, green_id, timeout_sec=900)
    return green_id

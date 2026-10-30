import time
import boto3

def ec2_client(region):
    return boto3.client('ec2', region_name=region)

def is_instance_status_ok(ec2, instance_id):
    statuses = ec2.describe_instance_status(InstanceIds=[instance_id], IncludeAllInstances=True).get('InstanceStatuses', [])
    if not statuses:
        return False
    s = statuses[0]
    return s.get('InstanceState', {}).get('Name') == 'running' and s.get('SystemStatus', {}).get('Status') == 'ok' and s.get('InstanceStatus', {}).get('Status') == 'ok'

def get_instance_tags(ec2, instance_id):
    inst = ec2.describe_instances(InstanceIds=[instance_id])['Reservations'][0]['Instances'][0]
    return {t['Key']: t['Value'] for t in inst.get('Tags', [])}

def wait_green_ready_by_tag(region, green_instance_id, ready_tag_key='restore', ready_tag_value='ok', timeout_sec=600):
    ec2 = ec2_client(region)
    deadline = time.monotonic() + timeout_sec
    while time.monotonic() < deadline:
        if is_instance_status_ok(ec2, green_instance_id) and get_instance_tags(ec2, green_instance_id).get(ready_tag_key) == ready_tag_value:
            return
        time.sleep(5)
    raise TimeoutError(f'GREEN not ready: {green_instance_id}; tags={get_instance_tags(ec2, green_instance_id)}')

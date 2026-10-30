from actions.green_recovery_manager import full_auto_recovery

def launch_green_from_snapshot(snapshot_id, instance_type='t3.micro'):
    # Compatibility wrapper; instance settings come from actions/config.json.
    # Keep instance_type argument for existing callers; config is authoritative.
    return full_auto_recovery(snapshot_id)

# Snapshot Service

The tasks defined here create snapshots (can be used to create instances or volumes based on them). The `namespace` of the following service tasks is `ext_snapshot`.

## AWS

- **Task:** [aws.main.snapshot.yml](aws/aws.main.snapshot.yml)

- **Schema:** [aws.schema.snapshot.yml](aws/aws.schema.snapshot.yml)

- **Validator:** [aws.validator.snapshot.yml](aws/aws.validator.snapshot.yml)

This task creates snapshots from existing EBS volumes at AWS.

_Example:_

```yaml
services:
  volume_service:
    base_dir: "ext-cloud"
    namespace: "ext_volume"
    task: "tasks/volume/aws/aws.main.volume.yml"
    schema: "tasks/volume/aws/aws.schema.volume.yml"
    validator: "tasks/volume/aws/aws.validator.volume.yml"
    credentials:
      volume: "aws"
    params:
      list:
        - volume_id: vol-abcdef12
          region: "us-east-1"
          description: snapshot of /data from DB123
        - instance_id: i-12345678
          region: "us-east-1"
          device_name: /dev/sdb1
          description: snapshot of /data from DB123
        - instance_id: i-12345678
          region: "us-east-1"
          device_name: /dev/sdb1
          snapshot_tags:
            frequency: hourly
            source: /data
        - snapshot_id: snap-abcd1234
          region: "us-east-1"
          absent: true
        - volume_id: vol-abcdef12
          region: "us-east-1"
          last_snapshot_min_age: 60
credentials:
  aws:
    access_key: "<aws_access_key>"
    secret_key: "<aws_secret_key>"
```

The above example will:

- Create a snapshot from the volume `vol-abcdef12`.
- Create a snapshot from the volume used by the instance `i-12345678`.
- Create a snapshot from the volume used by the instance `i-12345678`. It will be created with the tags `frequency: hourly` and `source: /data`.
- Delete the snapshot with id `snap-abcd1234`.
- Create a snapshot from the volume `vol-abcdef12` if it's the 1st snapshot from this volume, or if the last snapshot from this volume was more than 60 minutes ago.

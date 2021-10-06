# Volume Service

The tasks defined here create volumes (Block Storage) that can be attached to instances to increase its storage size. The `namespace` of the following service tasks is `ext_volume`.

## AWS

- **Task:** [aws.main.volume.yml](aws/aws.main.volume.yml)

- **Schema:** [aws.schema.volume.yml](aws/aws.schema.volume.yml)

- **Validator:** [aws.validator.volume.yml](aws/aws.validator.volume.yml)

This task creates EBS volumes (Block Storage) at AWS.

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
        - name: "aws-vol-01"
          region: "us-east-1"
          zone: "us-east-1a"
          volume_size: "15"
        - name: "aws-vol-02"
          region: "us-east-1"
          zone: "us-east-1b"
          device_name: "/dev/sdf"
          volume_size: "20"
          volume_type: "gp2"
credentials:
  aws:
    access_key: "<aws_access_key>"
    secret_key: "<aws_secret_key>"
```

The above example will create the EBS volumes:

- `aws-vol-01`: standard block storage in the zone `us-east-1a` with `15GiB`.
- `aws-vol-02`: SSD (`gp2`) block storage in the zone `us-east-1b` with `20GiB`.

## DigitalOcean

- **Task:** [digital_ocean.main.volume.yml](digital_ocean/digital_ocean.main.volume.yml)

- **Schema:** [digital_ocean.schema.volume.yml](digital_ocean/digital_ocean.schema.volume.yml)

- **Validator:** [digital_ocean.validator.volume.yml](digital_ocean/digital_ocean.validator.volume.yml)

This task creates volumes (Block Storage) at DigitalOcean.

_Example:_

```yaml
services:
  volume_service:
    base_dir: "ext-cloud"
    namespace: "ext_volume"
    task: "tasks/volume/digital_ocean/digital_ocean.main.volume.yml"
    schema: "tasks/volume/digital_ocean/digital_ocean.schema.volume.yml"
    validator: "tasks/volume/digital_ocean/digital_ocean.validator.volume.yml"
    credentials:
      volume: "digital_ocean"
    params:
      name: "digital-ocean-vol-01"
      region: "ams3"
      block_size: "15"
credentials:
  digital_ocean:
    api_token: "<digital_ocean_api_token>"
```

The above example will create a volume with `15GiB` named `digital-ocean-vol-01` in the region `ams3`.
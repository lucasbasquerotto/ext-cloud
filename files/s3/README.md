# S3 templates

Here you can find some S3 templates to be used in projects.

## S3 configuration file

_Schema:_ [s3-cli.schema.yml](s3-cli.schema.yml)

The below example will create a s3 configuration file at `s3/config` in the pod repository directory of `my_pod` based on the template.

```yaml
pods:
  my_pod:
    # ...
    transfer:
      - dest: "s3/config"
        src:
          type: "template"
          origin: "cloud"
          schema: "ext-cloud/files/s3/s3-cli.schema.yml"
          file: "ext-cloud/files/s3/{{ params.s3_cli_config_file | default('') }}"
          params:
            list:
              - alias: "backup"
                endpoint: "{{ credentials.s3.endpoint | default('') }}"
                region: "{{ credentials.s3.region | default('') }}"
                access_key: "{{ credentials.s3.access_key | default('') }}"
                secret_key: "{{ credentials.s3.secret_key | default('') }}"
```

The configuration file receives a `list` parameter which is a list of dictionaries containing `alias` (`profile`), access key, secret key, endpoint (optional) and region (optional). A `when` property, that defaults to `true`, can be defined with `false` to ignore a list item.

The value of the `s3_cli_config_file` parameter above can be one of the following:

- [config.awscli.j2](config.awscli.j2): will generate a configuration for awscli.
- [config.mc.j2](config.mc.j2): will generate a configuration for the minio client.
- [config.rclone.j2](config.rclone.j2): will generate a configuration for rclone.

## S3 lifecycle file

_File:_ [s3_lifecycle.json.j2](s3_lifecycle.json.j2)

_Schema:_ [s3_lifecycle.schema.yml](s3_lifecycle.schema.yml)

Creates a S3 lifecycle file based on the template.

_Example:_

```yaml
pods:
  my_pod:
    # ...
    transfer:
      - dest: "env/s3/etc/s3-backup-lifecycle.json"
        src:
          type: "template"
          origin: "cloud"
          file: "ext-cloud/files/s3/s3_lifecycle.json.j2"
          schema: "ext-cloud/files/s3/s3_lifecycle.schema.yml"
          params:
            rules:
              - name: "logs-expiration"
                filter_prefix: "logs/"
                expiration_days: 30
                older_versions_expiration_days: 180
```

The lifecycle file created above will define that objects created with the `logs/` prefix will expire after 30 days (in versioned buckets, versions of objects with the `logs/` prefix that were deleted for more than 180 days will be deleted permanently).

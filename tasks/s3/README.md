# S3 Service

- **Task:** [aws.main.s3.yml](aws.main.s3.yml)

- **Schema:** [schema.s3.yml](schema.s3.yml)

- **Validator:** [validator.s3.yml](validator.s3.yml)

This task can be used to create and destroy S3 buckets in a given endpoint. The buckets permissions can be specified as well. Take a look at the schema file to know which parameters this task expects, as well as what each parameter represents. The `namespace` of this service task is `ext_s3`.

_Example #1:_

```yaml
services:
  s3_service:
    base_dir: "ext-cloud"
    namespace: "ext_s3"
    task: "tasks/s3/aws.main.s3.yml"
    schema: "tasks/s3/schema.s3.yml"
    validator: "tasks/s3/validator.s3.yml"
    credentials:
      s3: "s3"
    params:
      list:
        - bucket: "private-bucket-name"
          permission: "private"
        - bucket: "public-bucket-name"
          permission: "public-read"
credentials:
  s3:
    endpoint: "https://ams3.digitaloceanspaces.com"
    access_key: "<digital_ocean_spaces_access_key>"
    secret_key: "<digital_ocean_spaces_secret_key>"
```

The above service (`s3_service`) will create a private bucket named `private-bucket-name` and a public bucket (read permission allowed) named `public-bucket-name` at Digital Ocean Spaces.

_Example #2:_

```yaml
services:
  s3_service_02:
    list: true
    services:
      - name: "s3_backup"
        key: "s3_service_base"
        params:
          bucket: "my-backup-bucket"
          permission: "private"
      - name: "s3_uploads"
        key: "s3_service_base"
        params:
          bucket: "my-uploads-bucket"
          permission: "public-read"
  s3_service_base:
    base_dir: "ext-cloud"
    namespace: "ext_s3"
    task: "tasks/s3/aws.main.s3.yml"
    schema: "tasks/s3/schema.s3.yml"
    validator: "tasks/s3/validator.s3.yml"
    credentials:
      s3: "s3"
credentials:
  s3:
    access_key: "<aws_s3_access_key>"
    secret_key: "<aws_s3_secret_key>"
```

The above service (`s3_service_02`) will create a private bucket named `my-backup-bucket` and a public bucket (read permission allowed) named `my-uploads-bucket` at AWS.

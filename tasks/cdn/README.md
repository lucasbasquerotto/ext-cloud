# CDN Service

The tasks defined here manage CDNs (Content Delivery Networks), enabling and disabling CDNs in the cloud providers specified below. Take a look at the schema files to know which parameters these tasks expect, as well as what each parameter represents. The `namespace` of the following service tasks is `ext_cdn`.

## AWS (Cloudfront)

- **Task:** [aws.main.cdn.yml](aws/aws.main.cdn.yml)

- **Schema:** [aws.schema.cdn.yml](aws/aws.schema.cdn.yml)

- **Validator:** [aws.validator.cdn.yml](aws/aws.validator.cdn.yml)

_Example:_

```yaml
services:
  cdn_service:
    base_dir: "ext-cloud"
    namespace: "ext_cdn"
    task: "tasks/cdn/aws/aws.main.cdn.yml"
    schema: "tasks/cdn/aws/aws.schema.cdn.yml"
    validator: "tasks/cdn/aws/aws.validator.cdn.yml"
    credentials:
      cdn: "aws"
    params:
      list:
        - name: test-service1
          aliases: ["www.my-distribution-source.com", "zzz.aaa.io"]
        - name: test-service2
          comment: modified by ansible cloudfront.py
          tags:
            Name: example distribution
            Project: example project
            Priority: "1"
          purge_tags: yes
        - name: test-service3
          origins:
            - id: "my test origin-000111"
              domain_name: www.example.com
              origin_path: /production
              custom_headers:
                - header_name: MyCustomHeaderName
                  header_value: MyCustomHeaderValue
          default_cache_behavior:
            target_origin_id: "my test origin-000111"
            forwarded_values:
              query_string: true
              cookies:
                forward: all
              headers:
                - "*"
              viewer_protocol_policy: allow-all
              smooth_streaming: true
              compress: true
              allowed_methods:
                items:
                  - GET
                  - HEAD
                cached_methods:
                  - GET
                  - HEAD
          logging:
            enabled: true
            include_cookies: false
            bucket: mylogbucket.s3.amazonaws.com
            prefix: myprefix/
          enabled: false
          comment: this is a CloudFront distribution with logging
        - name: test-service4
          absent: true
          comment: destroy this distribution
credentials:
  aws:
    access_key: "<aws_access_key>"
    secret_key: "<aws_secret_key>"
```

The service `cdn_service` above will create the following Cloudfront distributions:

- `test-service1`: create or update a distribution's with aliases and comment
- `test-service2`: create or update a basic distribution with defaults and tags, removing existing tags
- `test-service3`: create or update a distribution with an origin, logging and default cache behavior

It will also destroy the distribution `test-service4`.

## Fastly

- **Task:** [fastly.main.cdn.yml](fastly/fastly.main.cdn.yml)

- **Schema:** [fastly.schema.cdn.yml](fastly/fastly.schema.cdn.yml)

- **Validator:** [fastly.validator.cdn.yml](fastly/fastly.validator.cdn.yml)

_Example:_

```yaml
services:
  cdn_service:
    base_dir: "ext-cloud"
    namespace: "ext_cdn"
    task: "tasks/cdn/fastly/fastly.main.cdn.yml"
    schema: "tasks/cdn/fastly/fastly.schema.cdn.yml"
    validator: "tasks/cdn/fastly/fastly.validator.cdn.yml"
    credentials:
      cdn: "fastly"
    params:
      list:
        - name: test-service1
          domains:
            - name: mydomain1.test
              comment: static response
          response_objects:
            - name: Set 200 status code
              status: 200
              response: Test Ok
        - name: test-service2
          domains:
            - name: mydomain2.test
              comment: go to host defined by ip
          backends:
            - name: test2
              port: 80
              address: 1.2.3.4
        - name: test-service3
          domains:
            - name: mydomain3.test
              comment: go to host defined by hostname
          backends:
            - name: test3
              port: 443
              address: example.com
credentials:
  fastly:
    api_key: "<fastly_api_key>"
```

The service `cdn_service` above will make requests to:

- `mydomain1.<fastly_domain>` return status `200` with the content `Test Ok`.
- `mydomain2.<fastly_domain>` go to `http://1.2.3.4:80`.
- `mydomain3.<fastly_domain>` go to `https://example.com`.



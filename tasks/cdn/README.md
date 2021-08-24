# CDN Service

The tasks defined here manage CDNs (Content Delivery Networks), enabling and disabling CDNs in the cloud providers specified below. Take a look at the schema files to know which parameters these tasks expect, as well as what each parameter represents. The `namespace` of the following service tasks is `ext_cdn`.

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
            - name: mydomain1
              comment: static response
          response_objects:
            - name: Set 200 status code
              status: 200
              response: Test Ok
        - name: test-service2
          domains:
            - name: mydomain2
              comment: go to host defined by ip
          backends:
            - name: test2
              port: 80
              address: 1.2.3.4
        - name: test-service3
          domains:
            - name: mydomain3
              comment: go to host defined by hostname
          backends:
            - name: test3
              port: 443
              address: example.com
credentials:
  fastly:
    api_key: "<fastly_api_key>"
```

The service `cdn_service` above will make requests to :

- `mydomain1.<fastly_domain>` return status `200` with the content `Test Ok`.
- `mydomain2.<fastly_domain>` go to `http://1.2.3.4:80`.
- `mydomain3.<fastly_domain>` go to `https://example.com`.



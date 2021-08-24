# DNS Service

The tasks defined here manage DNS records, creating and destroying the records in the specified zones. Take a look at the schema files to know which parameters these tasks expect, as well as what each parameter represents. The `namespace` of the following service tasks is `ext_dns`.

## CloudFlare

- **Task:** [cloudflare.main.dns.yml](cloudflare/cloudflare.main.dns.yml)

- **Schema:** [cloudflare.schema.dns.yml](cloudflare/cloudflare.schema.dns.yml)

- **Validator:** [cloudflare.validator.dns.yml](cloudflare/cloudflare.validator.dns.yml)

_Example:_

```yaml
services:
  dns_service:
    list: true
    services:
      - name: "dns_service_item_sub1_ipv4"
        key: "dns_service_item"
        params:
          dns_type: "A"
          record: "sub1"
          value: "1.2.3.4"
      - name: "dns_service_item_sub1_ipv6"
        key: "dns_service_item"
        params:
          dns_type: "AAAA"
          record: "sub1"
          value: "2001:0db8:85a3:0000:0000:8a2e:0370:7334"
      - name: "dns_service_item_sub2_ipv4"
        key: "dns_service_item"
        params:
          dns_type: "A"
          record: "sub2"
          value: "5.6.7.8"
      - name: "dns_service_item_sub2_ipv6"
        key: "dns_service_item"
        params:
          dns_type: "AAAA"
          record: "sub2"
          value: "2804:214:861b:1137:f9b2:4339:71ca:bd72"
  dns_service_item:
    base_dir: "ext-cloud"
    namespace: "ext_dns"
    task: "tasks/dns/cloudflare/cloudflare.main.dns.yml"
    schema: "tasks/dns/cloudflare/cloudflare.schema.dns.yml"
    validator: "tasks/dns/cloudflare/cloudflare.validator.dns.yml"
    credentials:
      dns: "cloudflare"
    params:
      zone: "mydomain.com"
credentials:
  cloudflare:
    email: "<cloudflare_email>"
    token: "<cloudflare_token>"
```

The service `dns_service` above will call `dns_service_item` 4 times to create the following records in the zone `mydomain.com`:

- An `A` record for the subdomain `sub1` with the value `1.2.3.4`.
- An `AAAA` record for the subdomain `sub1` with the value `2001:0db8:85a3:0000:0000:8a2e:0370:7334`.
- An `A` record for the subdomain `sub2` with the value `5.6.7.8`.
- An `AAAA` record for the subdomain `sub2` with the value `2804:214:861b:1137:f9b2:4339:71ca:bd72`.

## Godaddy

- **Task:** [godaddy.main.dns.yml](godaddy/godaddy.main.dns.yml)

- **Schema:** [godaddy.schema.dns.yml](godaddy/godaddy.schema.dns.yml)

- **Validator:** [godaddy.validator.dns.yml](godaddy/godaddy.validator.dns.yml)

_Example:_

```yaml
services:
  dns_service:
    base_dir: "ext-cloud"
    namespace: "ext_dns"
    task: "tasks/dns/godaddy/godaddy.main.dns.yml"
    schema: "tasks/dns/godaddy/godaddy.schema.dns.yml"
    validator: "tasks/dns/godaddy/godaddy.validator.dns.yml"
    credentials:
      dns: "godaddy"
    params:
      zone: "mydomain.com"
      dns_type: "NS"
      record: "dev"
      value: ["1.1.1.1", "2.2.2.2"]
credentials:
  godaddy:
    api_server: "https://api.godaddy.com"
    api_version: "1"
    api_key: "<godaddy_api_key>"
    api_secret: "<godaddy_api_secret>"
```

The service `dns_service` above will create 2 `NS` records for the subdomain `dev` with the values `1.1.1.1` and `2.2.2.2`.
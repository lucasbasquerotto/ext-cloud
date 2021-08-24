# Nameserver Service

The tasks defined here manage nameservers, creating and destroying the records that define the nameservers in the cloud providers specified below. Take a look at the schema files to know which parameters these tasks expect, as well as what each parameter represents. The `namespace` of the following service tasks is `ext_nameserver`.

## Godaddy

- **Task:** [godaddy.main.nameserver.yml](godaddy/godaddy.main.nameserver.yml)

- **Schema:** [godaddy.schema.nameserver.yml](godaddy/godaddy.schema.nameserver.yml)

- **Validator:** [godaddy.validator.nameserver.yml](godaddy/godaddy.validator.nameserver.yml)

_Example:_

```yaml
services:
  nameserver_service:
    base_dir: "ext-cloud"
    namespace: "ext_nameserver"
    task: "tasks/nameserver/godaddy/godaddy.main.nameserver.yml"
    schema: "tasks/nameserver/godaddy/godaddy.schema.nameserver.yml"
    validator: "tasks/nameserver/godaddy/godaddy.validator.nameserver.yml"
    credentials:
      nameserver: "godaddy"
    params:
      zone: "mydomain.com"
      nameservers: ["8.8.8.8", "9.9.9.9"]
credentials:
  godaddy:
    api_server: "https://api.godaddy.com"
    api_version: "1"
    api_key: "<godaddy_api_key>"
    api_secret: "<godaddy_api_secret>"
```

The service `nameserver_service` above will define the nameservers (the 2 `NS` records with the values `8.8.8.8` and `9.9.9.9`) for the zone `mydomain.com`.

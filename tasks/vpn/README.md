# VPN Service

The tasks defined here manage VPNs or provide a VPN-like functionality. Take a look at the schema files to know which parameters these tasks expect, as well as what each parameter represents. The `namespace` of the following service tasks is `ext_vpn`.

## Digital Ocean

- **Task:** [digital_ocean.main.vpn.yml](digital_ocean.main.vpn.yml)

- **Schema:** [digital_ocean.schema.vpn.yml](digital_ocean.schema.vpn.yml)

This task creates tags and firewalls at Digital Ocean so as to provide a VPN-like behaviour. It's possible to create firewalls that restrict ports and IPs, and associate them to tags so that resources (like droplets) with those tags will be restricted by the created firewalls.

_Example:_

```yaml
services:
  digital_ocean_vpn:
    base_dir: "ext-cloud"
    namespace: "ext_vpn"
    task: "tasks/vpn/digital_ocean.main.vpn.yml"
    schema: "tasks/vpn/digital_ocean.schema.vpn.yml"
    credentials:
      vpn: "digital_ocean"
    params:
      tags:
        - "auto"
        - "dmz"
      firewalls:
        - name: "private"
          tags: ["auto"]
          inbound_rules:
            - ports: "9080"
              sources:
                addresses: "1.2.3.4"
            - ports: "9443"
              sources:
                addresses: "1.2.3.4"
        - name: "auto"
          tags: ["auto"]
          inbound_rules:
            - ports: "22"
              sources:
                tags: ["main"]
                addresses: "8.8.8.8"
          outbound_rules:
            - protocol: "tcp"
              ports: "1-65535"
              destinations:
                addresses: ["0.0.0.0/0", "::/0"]
            - protocol: "udp"
              ports: "1-65535"
              destinations:
                addresses: ["0.0.0.0/0", "::/0"]
            - protocol: "icmp"
              ports: "1-65535"
              destinations:
                addresses: ["0.0.0.0/0", "::/0"]
        - name: "dmz"
          tags: ["dmz"]
          inbound_rules:
            - ports: "80"
              sources:
                addresses: ["0.0.0.0/0", "::/0"]
            - ports: "443"
              sources:
                addresses: ["0.0.0.0/0", "::/0"]
credentials:
  digital_ocean:
    api_token: "<digital_ocean_api_token>"
```

The above example will create the tags:

- `auto`
- `dmz`

It will also create the firewalls:

- `private`: applied to resources with the tag `auto`; open access to ports `9080` and `9443` only to the ip `1.2.3.4`.
- `auto`: applied to resources with the tag `auto`; open access to the port `22` (SSH) to the ip `8.8.8.8` and to resources that have the tag `main`; this firewall allow the resources to access (outbound rules) any external resources (any ipv4, `0.0.0.0/0`, and any ipv6, `::/0`) from any port (range `1-65535`) using any protocol (`tcp`, `udp` and `icmp`).
- `dmz`: applied to resources with the tag `dmz`; open access to ports `80` and `443` to any ips (which means that these ports are public).

The credential `digital_ocean_api_token` can be obtained creating an api token in the Digital Ocean website.
# VPN Service

The tasks defined here manage VPNs or provide a VPN-like functionality. Take a look at the schema files to know which parameters these tasks expect, as well as what each parameter represents. The `namespace` of the following service tasks is `ext_vpn`.

## AWS

- **Task:** [aws.main.vpn.yml](aws/aws.main.vpn.yml)

- **Schema:** [aws.schema.vpn.yml](aws/aws.schema.vpn.yml)

- **Validator:** [aws.validator.vpn.yml](aws/aws.validator.vpn.yml)

This task creates Security Groups at AWS so as to provide a VPN-like behaviour. It's possible to restrict access to and from ports and IPs in the resources that use the created security groups.

_Example:_

```yaml
services:
  vpn_service:
    base_dir: "ext-cloud"
    namespace: "ext_vpn"
    task: "tasks/vpn/aws/aws.main.vpn.yml"
    schema: "tasks/vpn/aws/aws.schema.vpn.yml"
    validator: "tasks/vpn/aws/aws.validator.vpn.yml"
    credentials:
      vpn: "aws"
    params:
      security_groups:
        - name: "group1"
          description: sg with rule descriptions
          vpc_id: vpc-xxxxxxxx
          region: us-east-1
          rules:
            - proto: tcp
              ports:
                - 80
              cidr_ip: 0.0.0.0/0
              rule_desc: allow all on port 80
        - name: "group2"
          description: an example EC2 group
          vpc_id: "12345"
          region: eu-west-1
          rules:
            - proto: tcp
              from_port: 80
              to_port: 80
              cidr_ip: 0.0.0.0/0
            - proto: tcp
              from_port: 22
              to_port: 22
              cidr_ip: 10.0.0.0/8
            - proto: tcp
              from_port: 443
              to_port: 443
              # this should only be needed for EC2 Classic security group rules
              # because in a VPC an ELB will use a user-account security group
              group_id: amazon-elb/sg-87654321/amazon-elb-sg
            - proto: tcp
              from_port: 3306
              to_port: 3306
              group_id: 123412341234/sg-87654321/exact-name-of-sg
            - proto: udp
              from_port: 10050
              to_port: 10050
              cidr_ip: 10.0.0.0/8
            - proto: udp
              from_port: 10051
              to_port: 10051
              group_id: sg-12345678
            - proto: icmp
              from_port: 8 # icmp type, -1 = any type
              to_port: -1 # icmp subtype, -1 = any subtype
              cidr_ip: 10.0.0.0/8
            - proto: all
              # the containing group name may be specified here
              group_name: example
            - proto: all
              # in the 'proto' attribute, if you specify -1, all, or a protocol number other than tcp, udp, icmp, or 58 (ICMPv6),
              # traffic on all ports is allowed, regardless of any ports you specify
              from_port: 10050 # this value is ignored
              to_port: 10050 # this value is ignored
              cidr_ip: 10.0.0.0/8
          rules_egress:
            - proto: tcp
              from_port: 80
              to_port: 80
              cidr_ip: 0.0.0.0/0
              cidr_ipv6: 64:ff9b::/96
              group_name: example-other
              # description to use if example-other needs to be created
              group_desc: other example EC2 group
        - name: "group3"
          description: an example2 EC2 group
          vpc_id: 12345
          region: eu-west-1
          rules:
            # 'ports' rule keyword accepts a single port value or a list of values including ranges (from_port-to_port).
            - proto: tcp
              ports: 22
              group_name: example-vpn
            - proto: tcp
              ports:
                - 80
                - 443
                - 8080-8099
              cidr_ip: 0.0.0.0/0
            # Rule sources allows to define multiple sources per source type as well as multiple source types per rule.
            - proto: tcp
              ports:
                - 6379
                - 26379
              group_name:
                - example-vpn
                - example-redis
            - proto: tcp
              ports: 5665
              group_name: example-vpn
              cidr_ip:
                - 172.16.1.0/24
                - 172.16.17.0/24
              cidr_ipv6:
                - 2607:F8B0::/32
                - 64:ff9b::/96
              group_id:
                - sg-edcd9784
credentials:
  aws:
    access_key: "<aws_access_key>"
    secret_key: "<aws_secret_key>"
```

The above example will create the security groups `group1`, `group2` and `group3` with the specified inbound rules (`rules`) and outbound rules (`rules_egress`).

The security groups can be associated with resources like `ec2` to restric access to (`rules`) and from (`rules_egress`) them.

## DigitalOcean

- **Task:** [digital_ocean.main.vpn.yml](digital_ocean/digital_ocean.main.vpn.yml)

- **Schema:** [digital_ocean.schema.vpn.yml](digital_ocean/digital_ocean.schema.vpn.yml)

- **Validator:** [digital_ocean.validator.vpn.yml](digital_ocean/digital_ocean.validator.vpn.yml)

This task creates tags and firewalls at DigitalOcean so as to provide a VPN-like behaviour. It's possible to create firewalls that restrict ports and IPs, and associate them to tags so that resources (like droplets) with those tags will be restricted by the created firewalls.

_Example:_

```yaml
services:
  vpn_service:
    base_dir: "ext-cloud"
    namespace: "ext_vpn"
    task: "tasks/vpn/digital_ocean/digital_ocean.main.vpn.yml"
    schema: "tasks/vpn/digital_ocean/digital_ocean.schema.vpn.yml"
    validator: "tasks/vpn/digital_ocean/digital_ocean.validator.vpn.yml"
    credentials:
      vpn: "digital_ocean"
    params:
      tags:
        - "main"
        - "auto"
        - "dmz"
      firewalls:
        - name: "private"
          tags: ["auto"]
          inbound_rules:
            - ports: "9080"
              sources:
                addresses: ["1.2.3.4"]
            - ports: "9443"
              sources:
                addresses: ["1.2.3.4"]
        - name: "auto"
          tags: ["auto"]
          inbound_rules:
            - ports: "22"
              sources:
                tags: ["main"]
                addresses: ["8.8.8.8"]
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

The above example will create the foolowing tags (if needed):

- `main`
- `auto`
- `dmz`

It will also create the firewalls:

- `private`: applied to resources with the tag `auto`; open access to ports `9080` and `9443` only to the ip `1.2.3.4`.
- `auto`: applied to resources with the tag `auto`; open access to the port `22` (SSH) to the ip `8.8.8.8` and to resources that have the tag `main`; this firewall allow the resources to access (outbound rules) any external resources (any ipv4, `0.0.0.0/0`, and any ipv6, `::/0`) from any port (range `1-65535`) using any protocol (`tcp`, `udp` and `icmp`).
- `dmz`: applied to resources with the tag `dmz`; open access to ports `80` and `443` to any ips (which means that these ports are public).

The credential `digital_ocean_api_token` can be obtained creating an api token in the DigitalOcean website.
# Node Service

The tasks defined here create and destroy nodes/hosts. Take a look at the schema files to know which parameters these tasks expect, as well as what each parameter represents. The `namespace` of the following service tasks is `ext_node`.

The node data is handled beforehand so as to create the `replicas` variable that will be passed as a property to the services based on the number of nodes to be created relative to the total. If `max_amount` is higher than `amount` when creating nodes, the excedent nodes are destroyed (which can be useful when increasing the number of nodes temporarily, and then decreasing).

Each host/replica name is in the form `<node_name>-host-<replica_index>`, with `replica_index` starting in 1, except when `replica_index` is `1`, in which case the replica name will be `<node_name>-host`. When `hostname` is defined in the node information (where the node name is specified), the `hostname` is used instead of `<node_name>-host` (the `replica_index` follows the same rules explained before).

`Node` as defined in the environment file refers to the node type, from which the replicas will be created (if the node amount is `1`, it may be used almost as a synonym of `Host`). In this context, `Host` and `Replica` are the same (an instance of a node type).

## Digital Ocean

- **Task:** [digital_ocean.main.node.yml](digital_ocean.main.node.yml)

- **Schema:** [digital_ocean.schema.node.yml](digital_ocean.schema.node.yml)

This task creates droplets at Digital Ocean. It's possible to assign tags to the droplets so as to provide a VPN-like behaviour (if there are firewalls associated with those tags).

_Example:_

```yaml
main:
  my_context:
    #...
    nodes:
      - name: "app"
        key: "digital_ocean_node"
      - name: "app2"
        key: "digital_ocean_node"
        amount: 2
        max_amount: 3
      - name: "app3"
        key: "digital_ocean_node"
        hostname: "myapp"
        amount: 3
        max_amount: 5
nodes:
  digital_ocean_node:
    service: "digital_ocean_node_service"
    base_dir: "/var/cloud"
    credential: "host"
    root: true
    params:
      node_setup:
        setup_log_file: "/var/log/setup.log"
        setup_finished_log_regex: "^Setup Finished.*$"
        setup_success_log_last_line: "Setup Finished - Success"
        initial_connection_timeout: 90
        setup_finished_timeout: 300
services:
  digital_ocean_node_service:
    base_dir: "ext-cloud"
    namespace: "ext_node"
    task: "tasks/node/digital_ocean.main.node.yml"
    schema: "tasks/node/digital_ocean.schema.node.yml"
    credentials:
      node: "digital_ocean"
    params:
      image_id: "ubuntu-18-04-x64"
      ipv6: true
      region_id: "ams3"
      size_id: "s-1vcpu-1gb"
      tags:
        - "auto"
        - "dmz"
    contents:
      user_data:
        type: "template"
        origin: "cloud"
        file: "ext-cloud/files/user-data/ubuntu-18.04.tpl.sh"
        schema: "ext-cloud/files/user-data/ubuntu-18.04.schema.yml"
        credentials:
          node: "host"
        contents:
          host_ssh_public_keys: |
            ssh-rsa AAAAB1...
            ssh-rsa AAAAB2...
            ssh-rsa AAAAB3...
credentials:
  host:
    host_user: "my-user"
    host_pass: "p4$$w0rd"
    ssh_file: "path/to/my-ssh-key-file"
  digital_ocean:
    api_token: "<digital_ocean_api_token>"
```

The above example will create the following Digital Ocean Droplets (Hosts):

- 1 host named `app-host`
- 2 hosts named `app2-host` and `app2-host-2`, and destroy the host `app2-host-3` (if there is one host with this name).
- 3 hosts named `myapp`, `myapp-2` and `myapp-3`, and destroy the hosts `myapp-4` and `myapp-5` (if there are hosts with these names).

Each droplet (host) will be created in the Digital Ocean region `ams3`, based on the droplet image `ubuntu-18-04-x64` (Ubuntu 18.04), with size `s-1vcpu-1gb` (1 cpu and memory of 1 GB) and will have the following tags: `auto` and `dmz`.

After creating the droplet, the instructions defined at the [user data file](../../files/user-data/ubuntu-18.04.tpl.sh) (after being templated with the credentials and parameters defined above) will be executed, and if the execution finishes successfully it will print `Setup Finished - Success` in the file `/var/log/setup.log` so that the the host will be considered ready (see the `node_setup` parameters defined for the node).

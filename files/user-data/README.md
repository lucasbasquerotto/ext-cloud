# User Data

The files defined here are templates that can be used as user data when creating hosts, to run instructions right after the hosts are created. These user data files can be called as setup files too. The main objectives of the said instructions are to:

1. Create a non-root user with sudo privileges, defining the authorized ssh public keys with which the host can be accessed through the created user, disabling the root SSH login with password.

2. Install container engines, like `docker` and `podman`.

3. Install some utilities like `jq`, `haveged` and `python3-pip`.

4. Print a success message (`Setup Finished - Success`) in a log file (`/var/log/setup.log`) that can be verified later to know if the setup ended successfully.

## Ubuntu 18.04

- **File:** [ubuntu-18.04.tpl.sh](ubuntu-18.04.tpl.sh)

- **Schema:** [ubuntu-18.04.schema.yml](ubuntu-18.04.schema.yml)

_Example:_

```yaml
#...
nodes:
  my_node:
    service: "node_service"
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
  node_service:
    #...
    contents:
      user_data:
        type: "template"
        origin: "cloud"
        file: "custom-cloud/files/user-data/ubuntu-18.04.tpl.sh"
        schema: "custom-cloud/files/user-data/ubuntu-18.04.schema.yml"
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
```

Considering that the service `node_service` above creates a node/host and expects a `user_data` content as the setup data to run the initial instructions in the host, then it will:

1. Create the host with the setup instructions defined in the `user_data` content, which will:

	1. Create the user `my-user` with the password `p4$$w0rd`, and define the authorized ssh public keys as the string defined in the `host_ssh_public_keys` property (`ssh-rsa AAAAB1...`), and the private key in the controller to access the host (through the command `./ctl/launch -n <project_name> --ssh`) is defined at `path/to/my-ssh-key-file` in the environment repository (but the file used will be a copy in another location in the project directory; if this ssh key file is encrypted with ansible-vault, it will be decrypted when copying).

	2. Install `docker`, `docker-compose` and `podman`.

	3. Install some utilities like `jq`, `haveged` and `python3-pip`.

	4. Print the success message `Setup Finished - Success` in the setup log file `/var/log/setup.log`.

2. Try to access the host as `my-user` with the password `p4$$w0rd`, using the ssh private key file (wait for 90 seconds; when it goes beyond this limit, a timeout error is shown).

3. Waits 300 seconds for the setup to end (when `Setup Finished - Success` is printed to the log file). If it goes beyond this time limit, a timeout error is shown. If the setup ends with an error, a `trap` command is triggered in the script, printing `Setup Finished - Error` in the log file so that the deployment won't need to wait for the timeout, instead showing an error right after this line is printed in the log file (the `setup_finished_log_regex` is satisfied by this line and knows that the setup finished, but when comparing the last line with the value at `setup_success_log_last_line` it knows that the execution failed and ends with an error).


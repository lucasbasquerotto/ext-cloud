# Cron Template

_File:_ [pod.tpl.sh](pod.tpl.sh)
_Schema:_ [pod.schema.yml](pod.schema.yml)

This template can be used to generate a crontab file according to the parameters that are passed to it.

It can be defined in a [project environment file](http://github.com/lucasbasquerotto/cloud#project-environment-file) either in the `cron` parameter of a node, or in a transfer section of a pod. When defined for a node, the node should have only one pod defined.

_Example for a node:_

```yaml
nodes:
  my_node:
    #...
    params:
      cron:
        - dest: "/var/spool/cron/crontabs/root"
          user: "root"
          src:
            type: "template"
            origin: "cloud"
            file: "ext-cloud/files/cron/pod.tpl.sh"
            schema: "ext-cloud/files/cron/pod.schema.yml"
            params:
              tasks:
                - name: "watch"
                  task: "unique:action:watch"
                  cron: "*/1 * * * *"
                - name: "backup"
                  task: "unique:action:backup"
                  cron: "0 */6 * * *"
```

_Example for a pod:_

```yaml
pods:
  my_pod:
    #...
    transfer:
      - dest: "env/cron/cron-file"
        src:
          type: "template"
          origin: "cloud"
          file: "ext-cloud/files/cron/pod.tpl.sh"
          schema: "ext-cloud/files/cron/pod.schema.yml"
          params:
            tasks:
              - name: "watch"
                task: "unique:action:watch"
                cron: "*/1 * * * *"
              - name: "backup"
                task: "unique:action:backup"
                cron: "0 */6 * * *"
```

When used as a node parameter, it will handle creating the crontab file and replacing it only when changed, updating the crontab list, directly in the deployment process.

When used as a pod parameter, there should be an instruction or script that runs in the pod to handle the creation fo the crontab. Including it in the pod and handling in a script might be faster than letting ansible handle it when defined in the node.

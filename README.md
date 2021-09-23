# Repository extension for the Cloud Layer

This repository extends the cloud layer repository defined at http://github.com/lucasbasquerotto/cloud, mainly with tasks that run in specific cloud providers, while the cloud repository is the core of the cloud layer with generic tasks and the steps that will be executed in this layer.

For the examples in this repository, the directory in which it will reside relative to the main cloud layer directory is considered to be `ext-cloud`, as defined in the below example:

```yaml
main:
  my_context:
    repo: "cloud"
    ext_repos:
      - repo: "ext_cloud"
        dir: "ext-cloud"
    #...
repos:
  cloud:
    src: "https://github.com/lucasbasquerotto/cloud.git"
    version: "master"
  ext_cloud:
    src: "https://github.com/lucasbasquerotto/ext-cloud.git"
    version: "master"
#...
```

## Table of Contents

- [Tasks](#tasks)
- [Run Stage Tasks](run-tasks/README.md)
- [User Data](files/user-data/README.md)

## Tasks

This is the main section of this repository. It contains tasks to deploy specific services/resources in cloud providers. The types of tasks are defined below, with links to their respective documentation:

- [CDN](tasks/cdn/README.md)
- [DNS](tasks/dns/README.md)
- [Nameserver](tasks/nameserver/README.md)
- [Node](tasks/node/README.md)
- [S3](tasks/s3/README.md)
- [VPN](tasks/vpn/README.md)

## Files and Templates

Here are some useful files and templates that can be used in deployments:

- [Cron](files/cron/README.md)
- [Discourse](files/discourse/README.md)
- [User Data](files/user-data/README.md)

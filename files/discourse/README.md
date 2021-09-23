# Discourse Files and Templates

Files that can be used for a Discourse platform deployment.

## Discourse Setup

_File:_ [discourse-setup.sh](discourse-setup.sh)

This file can be usen in a [run stage task](http://github.com/lucasbasquerotto/cloud#run-stages) and runs the main instructions that are needed in the Discourse setup script (except for the creation of the `app.yml` file, that should be defined in the environment repository and moved to the host), in a non-interactive way. It:

- Checks if the script is being run by the root user (otherwise an error is thrown).

- Checks if Docker is installed.

- Checks if the host has at least 1GB of memory.

- Creates a Swap partition with 2GB if the host has 2GB or less of memory.

- Checks if the host has at least 5GB of disk size remaining (free).

## Discourse Container Template

_File:_ [container.tpl.yml](container.tpl.yml)

This template can be used to generate a discourse file that generates a container (e.g. `app.yml`).


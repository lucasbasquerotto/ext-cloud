# Tasks (Run Stages)

General tasks to run at the [run_stages](http://github.com/lucasbasquerotto/cloud#run-stages) step in the deployment.

## Discourse Setup

This run stage task runs the main instructions that are needed in the Discourse setup script (except for the creation of the `app.yml` file, that should be defined in the environment repository and moved to the host), in a non-interactive way. It:

- Checks if the script is being run by the root user (otherwise an error is thrown).

- Checks if Docker is installed.

- Checks if the host has at least 1GB of memory.

- Creates a Swap partition with 2GB if the host has 2GB or less of memory.

- Checks if the host has at least 5GB of disk size remaining (free).

## Docker

This run stage task installs `docker-compose` (if specified) and ensure docker is running.

Docker itself is expected to already be installed (see [user data](../files/user-data/README.md) for more information).


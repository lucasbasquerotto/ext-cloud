#!/usr/bin/env bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR

##
## Make sure only root can run our script
##
check_root() {
  echo "check_root started"

  if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root. Please sudo or log in as root first." 1>&2
    exit 1
  fi

  echo "check_root finished"
}

##
## Do we have docker?
##
check_docker () {
  echo "check_docker started"

  docker_path=`which docker.io || which docker`

  if [ -z $docker_path ]; then
    echo "Error: Docker not installed." 1>&2
    exit 1
  fi

  echo "check_docker finished"
}

##
## What are we running on
##
check_OS() {
  echo `uname -s`
}

##
## OS X available memory
##
check_osx_memory() {
  echo `free -m | awk '/Mem:/ {print $2}'`
}

##
## Linux available memory
##
check_linux_memory() {
  echo `free -g --si | awk ' /Mem:/  {print $2} '`
}

##
## Do we have enough memory and disk space for Discourse?
##
check_disk_and_memory() {
  echo "check_disk_and_memory started"

  os_type=$(check_OS)
  avail_mem=0

  if [ "$os_type" == "Darwin" ]; then
    avail_mem=$(check_osx_memory)
  else
    avail_mem=$(check_linux_memory)
  fi

  if [ "$avail_mem" -lt 1 ]; then
    echo "WARNING: Discourse requires 1GB RAM to run. This system does not appear"
    echo "to have sufficient memory."
    echo
    echo "Your site may not work properly, or future upgrades of Discourse may not"
    echo "complete successfully."
    exit 1
  fi

  if [ "$avail_mem" -le 2 ]; then
    total_swap=`free -g --si | awk ' /Swap:/  {print $2} '`

    if [ "$total_swap" -lt 2 ]; then
      echo "WARNING: Discourse requires at least 2GB of swap when running with 2GB of RAM"
      echo "or less. This system does not appear to have sufficient swap space."
      echo
      echo "Without sufficient swap space, your site may not work properly, and future"
      echo "upgrades of Discourse may not complete successfully."
      echo
      echo "Ctrl+C to exit or wait 5 seconds to have a 2GB swapfile created."
      sleep 5

      ##
      ## derived from https://meta.discourse.org/t/13880
      ##
      install -o root -g root -m 0640 /dev/null /swapfile
      dd if=/dev/zero of=/swapfile bs=1k count=2048k
      mkswap /swapfile
      swapon /swapfile
      echo "/swapfile       swap    swap    auto      0       0" | tee -a /etc/fstab
      sysctl -w vm.swappiness=10
      echo 'vm.swappiness = 10' > /etc/sysctl.d/30-discourse-swap.conf

      total_swap=`free -g --si | awk ' /Swap:/ {print $2} '`

      if [ "$total_swap" -lt 2 ]; then
        echo "Failed to create swap: are you root? Are you running on real hardware, or a fully virtualized server?"
        exit 1
      fi
    fi
  fi

  free_disk="$(df /var | tail -n 1 | awk '{print $4}')"

  if [ "$free_disk" -lt 5000 ]; then
    echo "WARNING: Discourse requires at least 5GB free disk space. This system"
    echo "does not appear to have sufficient disk space."
    echo
    echo "Insufficient disk space may result in problems running your site, and"
    echo "may not even allow Discourse installation to complete successfully."
    echo
    echo "Please free up some space, or expand your disk, before continuing."
    echo
    echo "Run \`apt-get autoremove && apt-get autoclean\` to clean up unused"
    echo "packages and \`./launcher cleanup\` to remove stale Docker containers."
    exit 1
  fi

  echo "check_disk_and_memory finished"
}

##
## Check requirements before creating a copy of a config file we won't edit
##
check_root
check_docker
check_disk_and_memory

#!/bin/bash
#shellcheck disable=SC1083,SC1088,SC2129
set -euo pipefail

#shellcheck disable=SC1036
USER_DIRECTORIES=( {{ params.user_directories | default([]) | join(' ') }} )

USERNAME="{{ credentials.node.host_user }}"

PASSWORD="{{ credentials.node.host_pass }}"

AUTHORIZED_KEYS="$(cat <<'SHELL'
{{ contents.host_ssh_public_keys }}
SHELL
)"

dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "$AUTHORIZED_KEYS" > "$dir/test.out.log"

for dir in "${USER_DIRECTORIES[@]}"; do
	echo "[$(date --utc '+%F %X')] Create the user directory: $dir"
	mkdir -p "$dir"
	chown "${USERNAME}":"${USERNAME}" "$dir"
done
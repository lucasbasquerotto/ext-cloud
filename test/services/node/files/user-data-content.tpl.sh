#!/bin/bash
#shellcheck disable=SC1083,SC2129
set -euo pipefail

USERNAME="{{ credentials.node.host_user }}"

PASSWORD="{{ credentials.node.host_pass }}"

AUTHORIZED_KEYS="$(cat <<'SHELL'
{{ contents.host_ssh_public_keys }}
SHELL
)"

dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "$AUTHORIZED_KEYS" > "$dir/test.out.log"
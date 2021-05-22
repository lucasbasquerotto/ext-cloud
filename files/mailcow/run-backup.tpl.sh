#!/bin/bash
set -eou pipefail

trap 'echo "[error] ${BASH_SOURCE[0]}:$LINENO"; exit $LINENO;' ERR

dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# environment vars

export BACKUP_LOCATION={{ params.backup_dir | default('/opt/backup') | quote }}

# general vars
s3_alias={{ params.s3_alias | quote }}
bucket_name={{ params.bucket_name | quote }}
bucket_path={{ params.bucket_path | default('') | quote }}
container_image={{ params.s3_container_image | quote }}
endpoint={{ params.endpoint | default('') | quote }}

# volume and command vars

{% if (params.s3_cli | default('')) == '' %}

  {% set error = {} %}
  {{ error['error.s3_cli.empty'] }}

{% elif params.s3_cli == 'awscli' %}

volume="/root/.aws/config"
command=( aws --profile="$s3_alias" s3 )
[ -n "$endpoint" ] && command+=( --endpoint="$endpoint" )
command+=( sync '/var/backup' "s3://$bucket_name/$bucket_path" )

{% elif params.s3_cli == 'mc' %}

volume="/root/.mc/config.json"
command=( mirror --overwrite '/var/backup' "$s3_alias/$bucket_name/$bucket_path" )

{% elif params.s3_cli == 'rclone' %}

volume="/config/rclone/rclone.conf"
command=( copy --verbose '/var/backup' "$s3_alias:$bucket_name/$bucket_path" )

{% else %}

  {% set error = {} %}
  {{ error['error.s3_cli.invalid.' + params.s3_cli] }}

{% endif %}

# execute local backup

if [ ! -d "$BACKUP_LOCATION" ]; then
  mkdir "$BACKUP_LOCATION"
fi

{{ input.pod_dir }}/helper-scripts/backup_and_restore.sh backup all

# execute remote backup (s3)

docker run --rm \
  -v "$dir/config.s3.txt":"$volume" \
  -v "$BACKUP_LOCATION":/var/backup \
  "$container_image" "${command[@]}"

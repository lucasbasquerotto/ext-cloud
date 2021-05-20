#!/bin/bash
set -eou pipefail

trap 'echo "[error] ${BASH_SOURCE[0]}:$LINENO"; exit $LINENO;' ERR

dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

BACKUP_LOCATION={{ params.backup_dir | default('/opt/backup') | quote }}
{{ input.pod_dir }}/helper-scripts/backup_and_restore.sh backup all

s3_alias={{ params.s3_alias | quote }}
bucket_name={{ params.bucket_name | quote }}
bucket_path={{ params.bucket_path | default('') | quote }}
container_image={{ params.s3_container_image | quote }}
endpoint={{ params.endpoint | default('') | quote }}

{% if (params.s3_cli | default('')) == '' %}
  {% set error = {} %}
  {{ error['error.s3_cli.empty'] }}
{% elif params.s3_cli == 'awscli' %}
    volume="/root/.aws/config"
    command=( aws --profile="$s3_alias" s3 )
    [ -n "$endpoint" ] && command+=( --endpoint="$endpoint" )
    command+=( sync "$BACKUP_LOCATION" "s3://$bucket_name/$bucket_path" )
{% elif params.s3_cli == 'mc' %}
    volume="/root/.mc/config.json"
    command=( mirror --overwrite "$BACKUP_LOCATION" "$s3_alias/$bucket_name/$bucket_path" )
{% elif params.s3_cli == 'rclone' %}
    volume="/config/rclone/rclone.conf"
    command=( copy --verbose "$BACKUP_LOCATION" "$s3_alias:$bucket_name/$bucket_path" )
{% else %}
  {% set error = {} %}
  {{ error['error.s3_cli.invalid.' + params.s3_cli] }}
{% endif %}

docker run --rm -v "$dir/config.s3.txt":"$volume" "$container_image" "${command[@]}"

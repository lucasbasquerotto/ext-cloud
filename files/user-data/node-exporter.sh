#!/bin/bash
set -eEou pipefail

EXPECTED_CHECKSUM=''

name=''

###################################################################################

checksum="$(sha256sum "$name.tar.gz")"

if [ -n "$EXPECTED_CHECKSUM" ] && [ "$checksum" != "$EXPECTED_CHECKSUM" ]; then
    error "checksum doesn't match (expected: $EXPECTED_CHECKSUM, found: $checksum)"
fi

useradd --no-create-home --shell /bin/false node_exporter

cp "$name"/node_exporter /usr/local/bin
chown node_exporter:node_exporter /usr/local/bin/node_exporter

cat > /etc/systemd/system/node_exporter.service <<-CONF
    [Unit]
    Description=Node Exporter
    Wants=network-online.target
    After=network-online.target

    [Service]
    User=node_exporter
    Group=node_exporter
    Type=simple
    ExecStart=/usr/local/bin/node_exporter

    [Install]
    WantedBy=multi-user.target
CONF

systemctl daemon-reload
systemctl start node_exporter
systemctl enable node_exporter

if ! systemctl is-active --quiet node_exporter; then
    error "node_exporter service is not active"
fi

rm -rf /tmp/main/setup

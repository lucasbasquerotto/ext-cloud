#!/bin/bash
set -eEou pipefail

err() {
    echo "[$(date --utc '+%F %X')] Error occurred:" >> "/var/log/setup.log"
    echo "Caller: $(caller)" >> "/var/log/setup.log"
	awk 'NR>L-4 && NR<L+4 { printf "%-5d%3s%s\n", NR, (NR==L ? ">>>" : ""), $0 }' L="$1" "$0" \
		>> "/var/log/setup.log"
	echo "Setup Finished - Error" >> "/var/log/setup.log"
}

function error {
	echo -e "[error] $(date '+%F %T') - ${BASH_SOURCE[0]}:${BASH_LINENO[0]}: ${*}" >&2
	exit 2
}

trap 'err "$LINENO"; exit $LINENO;' ERR

########################
### SCRIPT VARIABLES ###
########################

#shellcheck disable=SC1009,SC1072,SC1073,SC1083
USER_DIRECTORIES=( {{ params.user_directories | default([]) | join(' ') }} )

# Name of the user to create and grant sudo privileges
USERNAME="{{ credentials.node.host_user }}"

# Password of the user to create and grant sudo privileges
PASSWORD="{{ credentials.node.host_pass }}"

# Additional public keys to add to the new sudo user
# AUTHORIZED_KEYS=<<-SHELL
# 	ssh-rsa AAAAB...
# 	ssh-rsa AAAAB...
# SHELL
AUTHORIZED_KEYS="$(cat <<'SHELL'
{{ contents.host_ssh_public_keys }}
SHELL
)"

INSTALL_DOCKER="{{ params.install_docker | default(false) | bool | ternary('true', 'false') }}"
INSTALL_PODMAN="{{ params.install_podman | default(false) | bool | ternary('true', 'false') }}"
INSTALL_NODE_EXPORTER="{{ params.install_node_exporter | default(false) | bool | ternary('true', 'false') }}"
INSTALL_PACKAGES="{{ params.install_packages | default(false) | bool | ternary('true', 'false') }}"

DOCKER_COMPOSE_VERSION="{{ params.docker_compose_version | default('1.27.4', true) }}"
NODE_EXPORTER_VERSION="{{ params.node_exporter_version | default('1.2.0', true) }}"

EXPECTED_CHECKSUM="{{
		(params.node_exporter_version | default('') != '')
		| ternary(
			params.node_exporter_checksum | default(''),
			'f7ef26fb10d143dc4211281d7a2e8b13c4fe1bd0d7abbdff6735a6efdb4b5e56'
		)
	}}
"

export DEBIAN_FRONTEND=noninteractive

####################
### SCRIPT LOGIC ###
####################

touch "/var/log/setup.log"

# Add sudo user and grant privileges
useradd --create-home --shell "/bin/bash" --groups sudo "${USERNAME}"

# Check whether the root account has a real password set
encrypted_root_pw="$(grep root /etc/shadow | cut --delimiter=: --fields=2)"

if [ -z "${PASSWORD}" ]; then
	if [ "${encrypted_root_pw}" != "*" ]; then
		# Transfer auto-generated root password to user if present
		echo "${USERNAME}:${encrypted_root_pw}" | chpasswd --encrypted
	else
		# Delete invalid password for user if using keys so that a new password
		# can be set without providing a previous value
		passwd --delete "${USERNAME}"
	fi

	# Expire the sudo user's password immediately to force a change
	chage --lastday 0 "${USERNAME}"
else
	passwd --delete "${USERNAME}"
	echo "$USERNAME:$PASSWORD" | chpasswd

	echo "[$(date --utc '+%F %X')] New password defined for $USERNAME" >> "/var/log/setup.log"
fi

if [ "${encrypted_root_pw}" != "*" ]; then
	# lock the root account to password-based access
	# almost equivalent to: $ passwd --lock root
	# avoids errors like "You are required to change your password immediately (root enforced)"
	sed -i 's/^root:.*$/root:*:16231:0:99999:7:::/' /etc/shadow
fi

# Create SSH directory for sudo user
home_directory="$(eval echo ~"${USERNAME}")"
mkdir --parents "${home_directory}/.ssh"

if [ -n "${AUTHORIZED_KEYS}" ]; then
	# Add the provided public keys
	echo "${AUTHORIZED_KEYS}" > "${home_directory}/.ssh/authorized_keys"
fi

# Adjust SSH configuration ownership and permissions
chown --recursive "${USERNAME}":"${USERNAME}" "${home_directory}/.ssh"
chmod 0751 "${home_directory}/.ssh"

if [ -n "${AUTHORIZED_KEYS}" ]; then
	chmod 0640 "${home_directory}/.ssh/authorized_keys"
fi

# Disable root SSH login with password
sed --in-place 's/^PermitRootLogin.*/PermitRootLogin prohibit-password/g' /etc/ssh/sshd_config
sed --in-place 's/^#.*PasswordAuthentication.*/PasswordAuthentication no/g' /etc/ssh/sshd_config
sed --in-place 's/^PasswordAuthentication.*/PasswordAuthentication no/g' /etc/ssh/sshd_config
sed --in-place 's/^#.*ChallengeResponseAuthentication.*/ChallengeResponseAuthentication no/g' /etc/ssh/sshd_config
sed --in-place 's/^ChallengeResponseAuthentication.*/ChallengeResponseAuthentication no/g' /etc/ssh/sshd_config

if sshd -t -q; then
	systemctl restart sshd
fi

# Add exception for SSH and then enable UFW firewall
# ufw allow 22
# ufw allow 6443
# ufw --force enable

apt autoremove -y

echo "
ClientAliveInterval 60
TCPKeepAlive yes
ClientAliveCountMax 10000
" >> /etc/ssh/sshd_config

echo "[$(date --utc '+%F %X')] Create the user directories" >> "/var/log/setup.log"

for dir in "${USER_DIRECTORIES[@]}"; do
	echo "[$(date --utc '+%F %X')] Create the user directory: $dir" >> "/var/log/setup.log"
	mkdir -p "$dir"
	chown "${USERNAME}":"${USERNAME}" "$dir"
done

echo "[$(date --utc '+%F %X')] Main logic finished" >> "/var/log/setup.log"

########################
###      DOCKER      ###
########################

if [ "$INSTALL_DOCKER" = 'true' ]; then
	echo "[$(date --utc '+%F %X')] Preparing Docker Installation..." >> "/var/log/setup.log"

	# First, update your existing list of packages
	apt update

	# Next, install a few prerequisite packages which let apt use packages over HTTPS
	apt install -y apt-transport-https ca-certificates curl software-properties-common

	# Then add the GPG key for the official Docker repository to your system
	curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -

	# Add the Docker repository to APT sources
	add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable" -y

	# Next, update the package database with the Docker packages from the newly added repo
	apt update

	# Finally, install Docker
	apt install -y docker-ce

	echo "[$(date --utc '+%F %X')] Docker Installed" >> "/var/log/setup.log"

	# Install Docker Compose
	curl -L "https://github.com/docker/compose/releases/download/$DOCKER_COMPOSE_VERSION/docker-compose-$(uname -s)-$(uname -m)" \
		-o /usr/local/bin/docker-compose
	chmod +x /usr/local/bin/docker-compose

	echo "[$(date --utc '+%F %X')] Docker Compose Installed" >> "/var/log/setup.log"
fi

########################
###      PODMAN      ###
########################

if [ "$INSTALL_PODMAN" = 'true' ]; then
	echo "[$(date --utc '+%F %X')] Preparing Podman Installation..." >> "/var/log/setup.log"

	. /etc/os-release

	echo "[$(date --utc '+%F %X')] Environment Loaded for Podman Installation..." >> "/var/log/setup.log"

	echo "deb https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/xUbuntu_${VERSION_ID}/ /" \
		| tee /etc/apt/sources.list.d/devel:kubic:libcontainers:stable.list
	curl -L "https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/xUbuntu_${VERSION_ID}/Release.key" \
		| apt-key add -

	echo "[$(date --utc '+%F %X')] Podman repository added (apt)..." >> "/var/log/setup.log"

	apt-get update
	apt-get -y upgrade

	echo "[$(date --utc '+%F %X')] Packages updated for Podman Installation (apt)..." >> "/var/log/setup.log"

	apt-get -y install podman

	echo "[$(date --utc '+%F %X')] Podman Installed" >> "/var/log/setup.log"
fi

########################
###  NODE EXPORTER   ###
########################

if [ "$INSTALL_NODE_EXPORTER" = 'true' ]; then
	mkdir -p /tmp/setup
	cd /tmp/setup
	base_url='https://github.com/prometheus/node_exporter/releases/download'
	name="node_exporter-$NODE_EXPORTER_VERSION.linux-amd64"
	wget "$base_url/v$NODE_EXPORTER_VERSION/$name.tar.gz"
	tar xvfz "$name.tar.gz"

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
fi
########################
###      OTHERS      ###
########################

if [ "$INSTALL_PACKAGES" = 'true' ]; then
	echo "[$(date --utc '+%F %X')] Installing Packages..." >> "/var/log/setup.log"

	# First, update your existing list of packages
	apt update

	# Next, install the packages
	apt install -y jq gnupg2 pass inotify-tools haveged python3-pip

	echo "[$(date --utc '+%F %X')] Packages Installed" >> "/var/log/setup.log"
fi

########################
###       END        ###
########################

rm -rf /tmp/setup

echo "Setup Finished - Success" >> "/var/log/setup.log"

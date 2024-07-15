#!/bin/bash

set -m

tailscaled --tun=userspace-networking &
tailscale set --auto-update
tailscale up --ssh --hostname="${CONTAINER_NAME}"

fg %1
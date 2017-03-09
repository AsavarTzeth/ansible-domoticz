#!/bin/bash

# Syntax:
# update_domoticz.sh /path/to/download_dir /path/to/domoticz_dir
#
# Note that both arguments has to be directories.

# Debug
#set -o xtrace

readonly FILE='update.tgz'

err() {
  printf "$@\n" >&2
}

log() {
  printf "$@\n" >&1
}

validate_input() {
  local string="$@"

  if [[ "${string}" =~ ^- ]]; then
    err 'Invalid input: Leading dashes/hyphens are dangerous!'
    return 1
  elif ! [[ -d "${string}" ]]; then
    err 'Invalid input: Directory does not exist!'
    return 1
  fi
}

main() {

local download_dir="$1"
local update_dir="$2"

# Validate input
for args in "${download_dir}" "${update_dir}"; do
  if ! validate_input "${args}"; then
    exit 1
  fi
done

# Extract archive content
log 'Installing update...'
if ! tar xf "${download_dir}/${FILE}" -C "${update_dir}"; then
  err 'Failed to extract files'
  exit 1
fi

# Remove remaining archives
log 'Cleaning up...'
if ! rm -f "${download_dir}/${FILE}" "${download_dir}/${FILE}.sha256sum"; then
  err 'Failed to remove files'
  exit 1
fi

# Restart domoticz.service
log 'Restarting service...'
if ! /bin/systemctl restart domoticz.service; then
  err 'Failed to restart domoticz.service'
  exit 1
fi

log 'Update completed successfully!'
}

main "$@"

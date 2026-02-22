# uptime-kuma-automate
Automatically syncs active Docker containers to Uptime Kuma monitors. Ensures new containers are monitored without duplicating existing monitors and optionally performs a dry-run before making changes.

## Features

- Detects all active Docker containers on a host
- Checks existing Uptime Kuma monitors to avoid duplicates
- Adds new monitors for containers not already monitored
- Optional test/dry-run mode to verify actions before execution
- Ignores inactive containers
- Prevents the script from adding itself as a monitor

## Requirements

- Python 3.10+
- [Docker SDK for Python](https://docker-py.readthedocs.io/en/stable/)
- [Uptime Kuma API Python wrapper](https://uptime-kuma-api.readthedocs.io/)

## Installation

pip install docker uptime-kuma-api

git clone https://github.com/crosenblum/uptime-kuma-automate.git
cd uptime-kuma-automate

## Configuration

Edit the script to configure:

- `KUMA_BASE_URL` - Your Uptime Kuma Instance URL (e.g., `http://<HOST_IP>:3001`)
- `KUMA_CONTAINER_NAME` - The name of your uptime kuma container so as not add uptime-kuma to monitor itself
- `USERNAME` - Uptime Kuma Username
- `PASSWORD` - Uptime Kuma Password
- `HOST_IP` - IP Address of Docker Host
- `DRY_RUN` - True/False - dry-run mode to test the logic before adding monitors

## Usage

Run the script:

python uptime_kuma_automate.py

- The script will list containers and corresponding monitors.
- In dry-run mode, it outputs which monitors *would* be added.
- After verification, dry-run can be disabled to apply changes.

## Notes

- Only monitors for active containers are created.
- Existing monitors are matched using **case-insensitive names and URLs**.
- Duplicate monitors are never added.
- The script assumes a home network environment; only HTTP URLs are used.
- I used ChatGPT to help refine the implementation, but the concept and overall design were mine, driven by the need to keep Uptime Kuma in sync with frequently changing Docker containers.

## License

MIT License

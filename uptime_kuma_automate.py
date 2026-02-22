from uptime_kuma_api import UptimeKumaApi, MonitorType
import docker

# =========================
# CONFIG
# =========================
KUMA_BASE_URL = ":3001"
KUMA_CONTAINER_NAME = "uptime-kuma"
USERNAME = ""
PASSWORD = ""
HOST_IP = ""
DRY_RUN = "true"

# =========================
# HELPER FUNCTIONS
# =========================
def normalize_url(url: str) -> str:
    """
    Normalize a URL for consistent matching.

    Removes scheme (http:// or https://) and trailing slashes.

    Parameters:
        url (str): URL to normalize.

    Returns:
        str: Normalized URL string.
    """
    if not isinstance(url, str):
        return ""
    url = url.lower().strip()
    if url.startswith("http://"):
        url = url[7:]
    elif url.startswith("https://"):
        url = url[8:]
    # Remove trailing slash
    if url.endswith("/"):
        url = url[:-1]
    return url
    
def get_current_containers():
    """
    Retrieve all active (running) Docker containers with their name and published ports.
    Skips Uptime Kuma container itself.
    Returns:
        list of dict: [{'name': container_name, 'url': 'http://<host-ip>:<port>'}, ...]
    """
    containers_list = []
    client = docker.from_env()
    for container in client.containers.list():  # running containers only
        if container.name == KUMA_CONTAINER_NAME:
            continue  # Skip Uptime Kuma itself
        if container.status != "running":
            continue  # Extra safeguard
        ports = container.attrs['NetworkSettings']['Ports'] or {}
        for container_port, mappings in ports.items():
            if mappings:
                host_port = mappings[0]['HostPort']
                url = f"http://{HOST_IP}:{host_port}"
                containers_list.append({'name': container.name, 'url': url})
    return containers_list

def add_monitor_safe(api, name: str, url: str, test_run: bool = True):
    """
    Safely add a monitor via Uptime Kuma API.
    Parameters:
        api: UptimeKumaApi instance
        name: container name
        url: container URL
        test_run: if True, only print the monitor that would be added
    """
    if test_run:
        print(f"[TEST RUN] Would add monitor: {name} -> {url}")
    else:
        try:
            api.add_monitor(
                type=MonitorType.HTTP,
                name=name,
                url=url
            )
            print(f"Added monitor: {name} -> {url}")
        except Exception as e:
            print(f"Failed to add monitor {name}: {e}")

# =========================
# MAIN SYNC LOGIC
# =========================
with UptimeKumaApi(KUMA_BASE_URL) as api:
    # Login
    try:
        api.login(USERNAME, PASSWORD)
    except Exception as e:
        print(f"Login failed: {e}")
        exit(1)

    # Step 1: Get existing monitors
    try:
        existing_monitors = api.get_monitors()
    except Exception as e:
        print(f"Failed to get monitors: {e}")
        existing_monitors = []

    # Build lookup for comparison (normalized URL + lowercase name)
    monitor_lookup = {
        (m.get('name').lower(), normalize_url(m.get('url'))): m
        for m in existing_monitors
    }

    # Get current active containers
    try:
        containers = get_current_containers()
    except Exception as e:
        print(f"Failed to list containers: {e}")
        containers = []

    # Test run to list monitors that would be added
    for c in containers:
        key = (c['name'].lower(), normalize_url(c['url']))
        if key not in monitor_lookup:
            add_monitor_safe(api, c['name'], c['url'], test_run=DRY_RUN)
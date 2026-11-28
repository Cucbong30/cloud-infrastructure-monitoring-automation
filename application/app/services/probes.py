import socket
import time

import requests


def tcp_probe(host, port, timeout=2):
    started = time.monotonic()
    try:
        with socket.create_connection((host, int(port)), timeout=timeout):
            return True, _elapsed_ms(started)
    except OSError:
        return False, None


def http_probe(url, timeout=2):
    """Availability probe. Any response below HTTP 500 counts as reachable."""
    started = time.monotonic()
    try:
        response = requests.get(url, timeout=timeout, allow_redirects=True)
    except requests.RequestException:
        return False, None
    if response.status_code >= 500:
        return False, _elapsed_ms(started)
    return True, _elapsed_ms(started)


def http_recovery(url, timeout=3):
    """Recovery verification. Only HTTP 200 means the service recovered."""
    started = time.monotonic()
    try:
        response = requests.get(url, timeout=timeout, allow_redirects=True)
    except requests.RequestException:
        return False, "did not respond"
    latency = _elapsed_ms(started)
    if response.status_code == 200:
        return True, f"HTTP 200 ({latency} ms)"
    return False, f"HTTP {response.status_code} is not recovery. Expected HTTP 200."


def unpack_probe(result):
    if isinstance(result, tuple):
        ok = bool(result[0]) if result else False
        latency = result[1] if len(result) > 1 else None
        return ok, latency
    return bool(result), None


def _elapsed_ms(started):
    return max(1, int((time.monotonic() - started) * 1000))

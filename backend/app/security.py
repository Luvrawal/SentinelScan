import ipaddress
import socket
from urllib.parse import urlparse

from fastapi import HTTPException, status


class UnsafeTarget(ValueError):
    pass


def validate_target_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise UnsafeTarget("Target must be an absolute HTTP(S) URL")
    if parsed.username or parsed.password or parsed.fragment:
        raise UnsafeTarget("Target credentials and fragments are not allowed")
    if parsed.port not in {None, 80, 443}:
        raise UnsafeTarget("Only standard HTTP(S) ports are allowed")
    hostname = parsed.hostname.lower().rstrip(".")
    if hostname in {"localhost", "localhost.localdomain"} or hostname.endswith(".localhost"):
        raise UnsafeTarget("Local targets are not allowed")
    try:
        addresses = {ipaddress.ip_address(hostname)}
    except ValueError:
        try:
            addresses = {ipaddress.ip_address(item[4][0]) for item in socket.getaddrinfo(hostname, None)}
        except socket.gaierror as exc:
            raise UnsafeTarget("Target hostname could not be resolved") from exc
    if any(address.is_private or address.is_loopback or address.is_link_local or address.is_reserved or address.is_multicast or address.is_unspecified for address in addresses):
        raise UnsafeTarget("Private or reserved targets are not allowed")
    return parsed.geturl()


def reject_unsafe_target(value: str) -> str:
    try:
        return validate_target_url(value)
    except UnsafeTarget as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

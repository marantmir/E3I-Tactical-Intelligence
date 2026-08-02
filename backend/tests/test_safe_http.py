import socket
import urllib.error
import urllib.request

import pytest

from app.safe_http import UnsafeURLError, ValidatingRedirectHandler, validate_public_https_url


def _dns(address: str):
    return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (address, 443))]


def test_public_https_url_accepts_only_global_dns(monkeypatch):
    monkeypatch.setattr(socket, "getaddrinfo", lambda *args, **kwargs: _dns("93.184.216.34"))
    assert validate_public_https_url("https://example.com/path") == "https://example.com/path"

    for url in ("http://example.com", "https://user@example.com", "https://example.com:8443"):
        with pytest.raises(UnsafeURLError):
            validate_public_https_url(url)


@pytest.mark.parametrize("address", ["127.0.0.1", "10.0.0.1", "169.254.169.254", "192.168.1.1", "::1"])
def test_private_and_special_dns_answers_are_blocked(monkeypatch, address):
    monkeypatch.setattr(socket, "getaddrinfo", lambda *args, **kwargs: _dns(address))
    with pytest.raises(UnsafeURLError, match="non-public"):
        validate_public_https_url("https://example.com")


def test_redirect_target_is_revalidated(monkeypatch):
    monkeypatch.setattr(socket, "getaddrinfo", lambda *args, **kwargs: _dns("127.0.0.1"))
    request = urllib.request.Request("https://example.com")
    with pytest.raises(UnsafeURLError):
        ValidatingRedirectHandler().redirect_request(request, None, 302, "Found", {}, "https://internal.test")


def test_redirect_limit_is_enforced(monkeypatch):
    monkeypatch.setattr(socket, "getaddrinfo", lambda *args, **kwargs: _dns("93.184.216.34"))
    request = urllib.request.Request("https://example.com", headers={"X-E3I-Redirect-Count": "3"})
    with pytest.raises(urllib.error.HTTPError, match="Too many redirects"):
        ValidatingRedirectHandler().redirect_request(request, None, 302, "Found", {}, "/next")

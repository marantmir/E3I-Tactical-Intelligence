"""Small outbound HTTP guard used by public-source collectors.

The guard rejects user-info, non-HTTPS URLs, non-standard ports, private or
special-use DNS answers, and revalidates every redirect target.  It is not a
network sandbox; production deployments should also enforce egress policy.
"""
from __future__ import annotations

import ipaddress
import socket
import urllib.error
import urllib.parse
import urllib.request


MAX_REDIRECTS = 3
ALLOWED_PORT = 443


class UnsafeURLError(ValueError):
    """The outbound URL did not satisfy the public-network policy."""


def validate_public_https_url(url: str) -> str:
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or not parsed.hostname:
        raise UnsafeURLError("Outbound URL must use HTTPS")
    if parsed.username or parsed.password or parsed.port not in (None, ALLOWED_PORT):
        raise UnsafeURLError("Outbound URL contains forbidden authority data")
    try:
        answers = socket.getaddrinfo(parsed.hostname, ALLOWED_PORT, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise UnsafeURLError("Outbound hostname could not be resolved") from exc
    if not answers:
        raise UnsafeURLError("Outbound hostname has no DNS answers")
    for answer in answers:
        address = ipaddress.ip_address(answer[4][0])
        if not address.is_global:
            raise UnsafeURLError("Outbound hostname resolves to a non-public network")
    return urllib.parse.urlunsplit(parsed)


class ValidatingRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Validate redirect DNS/authority and enforce a short redirect chain."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        redirects = int(req.headers.get("X-e3i-redirect-count", "0")) + 1
        if redirects > MAX_REDIRECTS:
            raise urllib.error.HTTPError(newurl, code, "Too many redirects", headers, fp)
        target = validate_public_https_url(urllib.parse.urljoin(req.full_url, newurl))
        redirected = super().redirect_request(req, fp, code, msg, headers, target)
        if redirected is not None:
            redirected.add_unredirected_header("X-E3I-Redirect-Count", str(redirects))
        return redirected


def safe_urlopen(request: str | urllib.request.Request, *, timeout: float):
    """Open a validated URL and apply the same policy to every redirect."""
    url = request.full_url if isinstance(request, urllib.request.Request) else request
    validate_public_https_url(url)
    return urllib.request.build_opener(ValidatingRedirectHandler()).open(request, timeout=timeout)

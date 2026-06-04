"""Security validation utilities for InstaPay links.

This module provides tools to verify that a URL is a legitimate, official
InstaPay link - not a phishing or lookalike-domain attack.  It is the
security core of the ``instapay-eg`` SDK.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urlparse

from .exceptions import PhishingLinkError

# The single official domain for all InstaPay payment links.
_OFFICIAL_DOMAIN: str = "ipn.eg"

# Validates the URL path contains only safe characters: alphanumeric, hyphen,
# underscore, slash. Catches encoded payloads that slip through the injection
# substring check.
_VALID_URL_PATH_REGEX: re.Pattern[str] = re.compile(r"^[a-zA-Z0-9\-_/]+$")

# Patterns that suggest a lookalike / homoglyph / subdomain-spoof attack.
# Add more patterns as new phishing techniques are discovered.
_PHISHING_PATTERNS: list[re.Pattern[str]] = [
    # Subdomain spoofing: ipn.eg.evil.com
    re.compile(r"ipn\.eg\..+", re.IGNORECASE),
    # Hyphen substitution: ipn-eg.com
    re.compile(r"ipn-eg\.", re.IGNORECASE),
    # TLD swap: ipn.com, ipn.net … but NOT the legitimate ipn.eg
    re.compile(r"^ipn\.(?!eg$)[a-z]{2,}$", re.IGNORECASE),
    # Digit-for-letter homoglyph: 1pn.eg
    re.compile(r"[0-9]pn\.eg", re.IGNORECASE),
    # Keyword spoofing: instapay.fakesite.com
    re.compile(r"insta.?pay", re.IGNORECASE),
]

# Injection payloads that must never appear in a legitimate link.
_INJECTION_PATTERNS: list[str] = [
    "javascript:",
    "data:",
    "vbscript:",
    "<script",
    "%3cscript",
]


@dataclass(frozen=True)
class SecurityReport:
    """Machine-readable result of a full security audit on a URL.

    Attributes:
        is_safe: ``True`` only when **all** checks pass.
        scheme_valid: ``True`` when the scheme is ``https``.
        domain_valid: ``True`` when the domain exactly matches ``ipn.eg``.
        has_injection: ``True`` when a known injection payload is detected.
        phishing_risk: ``True`` when a lookalike-domain pattern is matched.
        url: The original URL that was audited.
        failure_reason: Human-readable explanation of the first failure, or
            ``None`` when the link is safe.
    """

    is_safe: bool
    scheme_valid: bool
    domain_valid: bool
    has_injection: bool
    has_invalid_path: bool
    phishing_risk: bool
    url: str
    failure_reason: str | None


def is_safe_link(url: str) -> bool:
    """Return ``True`` if *url* is a secure, official InstaPay link.

    This is the fast-path check used internally by ``parse_text``.  For a
    full breakdown of *why* a link fails, use ``audit_link`` instead.

    Args:
        url: The URL string to validate.

    Returns:
        ``True`` when the URL passes all security checks, ``False`` otherwise.

    Raises:
        PhishingLinkError: When the URL's domain matches a known phishing
            pattern (a positive signal of an attack, not just an invalid URL).

    Example:
        >>> is_safe_link("https://ipn.eg/S/alice/instapay/abc123")
        True
        >>> is_safe_link("http://ipn.eg/S/alice/instapay/abc123")
        False
    """
    report = audit_link(url)
    if report.phishing_risk:
        raise PhishingLinkError(
            f"Potential phishing URL detected: {url!r}. "
            "The domain resembles InstaPay's official domain but is not it."
        )
    return report.is_safe


def audit_link(url: str) -> SecurityReport:
    """Perform a full security audit on *url* and return a structured report.

    This is the recommended function to call when you want to log the specific
    reason a link was rejected - for example, in a fraud-detection pipeline or
    a Django admin dashboard.

    Args:
        url: The URL string to audit.  May be empty or malformed.

    Returns:
        A :class:`SecurityReport` dataclass with individual check results and
        an ``is_safe`` summary flag.

    Example:
        >>> report = audit_link("https://ipn.eg.evil.com/S/alice/instapay/x")
        >>> report.phishing_risk
        True
        >>> report.is_safe
        False
    """
    if not url:
        return SecurityReport(
            is_safe=False,
            scheme_valid=False,
            domain_valid=False,
            has_injection=False,
            has_invalid_path=False,
            phishing_risk=False,
            url=url,
            failure_reason="URL is empty.",
        )

    parsed = urlparse(url)
    path = parsed.path

    scheme_valid = parsed.scheme == "https"
    domain_valid = parsed.netloc == _OFFICIAL_DOMAIN

    lower_url = url.lower()
    has_injection = any(p in lower_url for p in _INJECTION_PATTERNS)

    has_invalid_path = domain_valid and not _VALID_URL_PATH_REGEX.match(path)
    phishing_risk = any(pat.search(parsed.netloc) for pat in _PHISHING_PATTERNS)

    is_safe = (
        scheme_valid
        and domain_valid
        and not has_injection
        and not has_invalid_path
        and not phishing_risk
    )

    failure_reason: str | None = None
    if not is_safe:
        if phishing_risk:
            failure_reason = (
                f"Domain '{parsed.netloc}' matches a known phishing pattern."
            )
        elif not scheme_valid:
            failure_reason = f"Scheme must be 'https', got '{parsed.scheme}'."
        elif not domain_valid:
            failure_reason = (
                f"Domain must be '{_OFFICIAL_DOMAIN}', got '{parsed.netloc}'."
            )
        elif has_injection:  # pragma: no branch
            failure_reason = "URL contains a suspected injection payload."
        elif has_invalid_path:  # pragma: no branch
            failure_reason = "URL path contains disallowed characters."

    return SecurityReport(
        is_safe=is_safe,
        scheme_valid=scheme_valid,
        domain_valid=domain_valid,
        has_injection=has_injection,
        has_invalid_path=has_invalid_path,
        phishing_risk=phishing_risk,
        url=url,
        failure_reason=failure_reason,
    )


def is_phishing_domain(url: str) -> bool:
    """Return ``True`` if the URL's domain matches a known phishing pattern.

    Use this when you want to distinguish phishing attempts from simply
    invalid URLs without raising an exception.

    Args:
        url: The URL string to check.

    Returns:
        ``True`` when a phishing pattern is detected.

    Example:
        >>> is_phishing_domain("https://ipn.eg.evil.com/S/alice/instapay/x")
        True
        >>> is_phishing_domain("https://ipn.eg/S/alice/instapay/x")
        False
    """
    netloc = urlparse(url).netloc
    return any(pat.search(netloc) for pat in _PHISHING_PATTERNS)

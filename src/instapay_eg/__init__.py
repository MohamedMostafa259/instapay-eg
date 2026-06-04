"""instapay-eg - Community SDK for Egyptian InstaPay payment links.

This package provides tools to **parse**, **validate**, and
**generate QR codes** for Egyptian InstaPay payment links (``https://ipn.eg``).

Quick start::

    from instapay_eg import parse_text

    data = parse_text(
        "https://ipn.eg/S/alice/instapay/2DcFGv\\n"
        "Click the link to send money to\\n"
        "alice@instapay\\nPowered by InstaPay"
    )
    print(data.link)              # 'https://ipn.eg/S/alice/instapay/2DcFGv'
    print(data.handle)            # 'alice'
    print(data.formatted_handle)  # 'alice@instapay'
    print(data.raw_url_id)        # '2DcFGv'
    print(data.is_verified)       # True

Disclaimer:
    This is an community-driven utility package.  It is not
    affiliated with, endorsed by, or associated with the Egyptian Banks
    Company (EBC) or InstaPay Egypt.
"""

from __future__ import annotations

from importlib.metadata import version

from .core import (
    InstaPayData,
    extract_handle,
    extract_link,
    extract_url_id,
    is_valid_handle,
    normalize_handle,
    parse_text,
)
from .exceptions import (
    InstaPayError,
    InvalidHandleError,
    InvalidLinkError,
    LinkNotFoundError,
    PhishingLinkError,
)
from .security import SecurityReport, audit_link, is_phishing_domain, is_safe_link

__version__: str = version("instapay-eg")

__all__: list[str] = [
    # Core parsing
    "InstaPayData",
    # Exceptions
    "InstaPayError",
    "InvalidHandleError",
    "InvalidLinkError",
    "LinkNotFoundError",
    "PhishingLinkError",
    # Security
    "SecurityReport",
    # Package version
    "__version__",
    "audit_link",
    "extract_handle",
    "extract_link",
    "extract_url_id",
    "is_phishing_domain",
    "is_safe_link",
    "is_valid_handle",
    "normalize_handle",
    "parse_text",
]

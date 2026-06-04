"""Core parsing and building utilities for Egyptian InstaPay links."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .exceptions import (
    InvalidHandleError,
    InvalidLinkError,
    LinkNotFoundError,
    PhishingLinkError,
)
from .security import is_phishing_domain, is_safe_link

# ---------------------------------------------------------------------------
# Compiled regex patterns
# ---------------------------------------------------------------------------

# Matches the first https://ipn.eg/S/ URL in a block of text.
# All legitimate InstaPay share-sheet links use the /S/ path prefix.
_INSTAPAY_URL_REGEX: re.Pattern[str] = re.compile(r"(https://ipn\.eg/S/[^\s]+)")

# Broad scan for ANY https URL in text - used by parse_text to detect phishing
# URLs that wouldn't be caught by the narrower _INSTAPAY_URL_REGEX.
_ANY_HTTPS_URL_REGEX: re.Pattern[str] = re.compile(r"https://[^\s]+")

# Extracts the handle from the /S/<handle>/instapay/ path segment.
# Example: /S/mohamed/instapay/2DcFGv  ->  'mohamed'
_HANDLE_EXTRACTION_REGEX: re.Pattern[str] = re.compile(r"/S/([^/]+)/instapay")

# Extracts the short unique token at the end of the URL path.
# Example: /S/mohamed/instapay/2DcFGv  →  '2DcFGv'
_URL_ID_REGEX: re.Pattern[str] = re.compile(r"/instapay/([^/?#\s]+)")

# Validates that a handle contains only characters permitted by InstaPay:
# starts/ends with letter/number, allows single dots/hyphens/underscores inside
_VALID_HANDLE_REGEX: re.Pattern[str] = re.compile(
    r"^[a-zA-Z0-9]+([._\-][a-zA-Z0-9]+)*$"
)


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class InstaPayData:
    """Immutable, validated snapshot of an InstaPay payment link.

    All fields are guaranteed to be consistent with each other - you will
    never receive a ``handle`` that does not match the ``link``.

    Attributes:
        link: The fully validated ``https://ipn.eg`` payment URL, including
            the server-generated token (e.g.
            ``'https://ipn.eg/S/alice/instapay/2DcFGv'``).
        handle: The raw handle string extracted from the URL (e.g. ``'alice'``).
        formatted_handle: The ``@instapay``-suffixed handle ready for display
            or storage (e.g. ``'alice@instapay'``).
        raw_url_id: The short server-generated token at the end of the URL
            (e.g. ``'2DcFGv'``).  Always present - links without this token
            are rejected by :func:`parse_text` as non-functional.
        is_verified: Always ``True`` for instances returned by :func:`parse_text`
            - indicates that the link has passed all security checks.

    Example:
        >>> data = parse_text(
        ...     "https://ipn.eg/S/alice/instapay/ABC123\\n"
        ...     "Click to send money\\nalice@instapay\\nPowered by InstaPay"
        ... )
        >>> data.link
        'https://ipn.eg/S/alice/instapay/ABC123'
        >>> data.handle
        'alice'
        >>> data.formatted_handle
        'alice@instapay'
        >>> data.raw_url_id
        'ABC123'
        >>> data.is_verified
        True
    """

    link: str
    handle: str
    formatted_handle: str
    raw_url_id: str
    is_verified: bool


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def extract_link(text: str) -> str | None:
    """Extract the first valid ``https://ipn.eg`` URL from a block of text.

    This is the low-level extraction primitive.  It does **not** perform any
    security checks.  Use :func:`parse_text` for a fully validated result.

    Args:
        text: Any string, including multi-line share-sheet text pasted
            directly from the InstaPay mobile app.

    Returns:
        The first ``https://ipn.eg`` URL found in *text*, or ``None`` if no
        URL is present.

    Example:
        >>> extract_link(
        ...     "https://ipn.eg/S/mohamed/instapay/2DcFGv\\n"
        ...     "Click the link to send money to\\n"
        ...     "mohamed@instapay\\nPowered by InstaPay"
        ... )
        'https://ipn.eg/S/mohamed/instapay/2DcFGv'
    """
    if not text:
        return None
    match = _INSTAPAY_URL_REGEX.search(text)
    return match.group(1) if match else None


def extract_handle(link: str) -> str | None:
    """Extract the handle from an InstaPay payment URL.

    Args:
        link: A full ``https://ipn.eg`` payment URL.

    Returns:
        The handle string (e.g. ``'mohamed'``), or ``None`` if the path does
        not contain the expected ``/<handle>/instapay/`` segment.

    Example:
        >>> extract_handle("https://ipn.eg/S/mohamed/instapay/2DcFGv")
        'mohamed'
    """
    if not link:
        return None
    match = _HANDLE_EXTRACTION_REGEX.search(link)
    return match.group(1) if match else None


def extract_url_id(link: str) -> str | None:
    """Extract the short unique token from the end of an InstaPay URL.

    Args:
        link: A full ``https://ipn.eg`` payment URL.

    Returns:
        The token string (e.g. ``'2DcFGv'``), or ``None`` if absent.

    Example:
        >>> extract_url_id("https://ipn.eg/S/mohamed/instapay/2DcFGv")
        '2DcFGv'
    """
    if not link:
        return None
    match = _URL_ID_REGEX.search(link)
    return match.group(1) if match else None


def is_valid_handle(handle: str) -> bool:
    """Return ``True`` if *handle* meets InstaPay's character constraints.

    The ``@instapay`` suffix is stripped automatically before validation, so
    both ``'alice'`` and ``'alice@instapay'`` are accepted.

    Args:
        handle: The handle string to validate.

    Returns:
        ``True`` when the handle is non-empty and contains only valid
        characters (letters, digits, underscores, hyphens, dots).

    Example:
        >>> is_valid_handle("alice")
        True
        >>> is_valid_handle("alice@instapay")
        True
        >>> is_valid_handle("alice!!!")
        False
    """
    if not handle:
        return False
    clean = normalize_handle(handle)
    return bool(_VALID_HANDLE_REGEX.match(clean))


def normalize_handle(handle: str) -> str:
    """Strip the ``@instapay`` suffix and normalise whitespace.

    This does **not** validate the handle - call :func:`is_valid_handle`
    afterwards if you need validation.

    Args:
        handle: A raw handle string, optionally including the ``@instapay``
            suffix and surrounding whitespace.

    Returns:
        The cleaned handle, with the suffix removed and whitespace stripped.
        Does **not** lowercase, because InstaPay handles are case-sensitive
        on the platform.

    Example:
        >>> normalize_handle("  Alice@instapay  ")
        'Alice'
    """
    return handle.strip().replace("@instapay", "").strip()


def parse_text(text: str) -> InstaPayData:
    """Parse raw share-sheet text and return a fully validated :class:`InstaPayData`.

    This is the **primary entry point** of the SDK.  Pass in the text that
    the user copied from the InstaPay app share sheet and receive a clean,
    safe, validated data object.

    The function will:

    1. Extract the first ``https://ipn.eg`` URL from the text.
    2. Run all security checks (HTTPS, exact domain, injection detection,
       phishing pattern matching).
    3. Extract and validate the handle.
    4. Return a frozen :class:`InstaPayData` instance.

    Args:
        text: Any string that may contain an InstaPay share link, such as the
            multi-line text copied from the InstaPay mobile app.

    Returns:
        A validated, immutable :class:`InstaPayData` instance.

    Raises:
        LinkNotFoundError: If no ``https://ipn.eg`` URL is found in *text*.
        PhishingLinkError: If the URL's domain matches a phishing pattern.
        InvalidHandleError: If the handle extracted from the URL is malformed.

    Example:
        >>> data = parse_text(
        ...     "https://ipn.eg/S/alice/instapay/2DcFGv\\n"
        ...     "Click the link to send money to\\n"
        ...     "alice@instapay\\nPowered by InstaPay"
        ... )
        >>> data.handle
        'alice'
        >>> data.is_verified
        True
    """
    # Scan ALL https URLs in the text for phishing patterns first.
    # extract_link only finds exact ipn.eg URLs, so a lookalike-domain URL
    # (e.g. https://ipn.eg.evil.com/...) would silently become a
    # LinkNotFoundError instead of the correct PhishingLinkError.
    for _match in _ANY_HTTPS_URL_REGEX.finditer(text):
        if is_phishing_domain(_match.group(0)):
            raise PhishingLinkError(
                f"Potential phishing URL detected: {_match.group(0)!r}. "
                "The domain resembles InstaPay's official domain but is not it."
            )

    link = extract_link(text)
    if not link:
        raise LinkNotFoundError(
            "No InstaPay URL (https://ipn.eg/...) was found in the provided text."
        )

    if not is_safe_link(link):
        raise InvalidLinkError(
            f"The URL {link!r} failed security validation. "
            "Use audit_link() for a detailed breakdown."
        )

    handle = extract_handle(link)
    if not handle or not is_valid_handle(handle):
        raise InvalidHandleError(f"Could not extract a valid handle from {link!r}.")

    raw_url_id = extract_url_id(link)
    if not raw_url_id:
        raise InvalidLinkError(
            f"The URL {link!r} does not contain a server-generated token and "
            "will not work as a payment link. Only links shared directly from "
            "the InstaPay app are valid."
        )

    return InstaPayData(
        link=link,
        handle=normalize_handle(handle),
        formatted_handle=f"{normalize_handle(handle)}@instapay",
        raw_url_id=raw_url_id,
        is_verified=True,
    )

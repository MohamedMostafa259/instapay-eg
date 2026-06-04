"""Shared pytest fixtures for the instapay-eg test suite."""

import pytest

# ---------------------------------------------------------------------------
# Sample data constants
# ---------------------------------------------------------------------------

VALID_HANDLE = "alice"
VALID_LINK = "https://ipn.eg/S/alice/instapay/2DcFGv"
VALID_TEXT = (
    "https://ipn.eg/S/alice/instapay/2DcFGv\n"
    "Click the link to send money to\n"
    "alice@instapay\n"
    "Powered by InstaPay"
)

# Links that should be rejected for various reasons
PHISHING_LINK_SUBDOMAIN = "https://ipn.eg.evil.com/S/alice/instapay/2DcFGv"
PHISHING_LINK_HYPHEN = "https://ipn-eg.com/S/alice/instapay/2DcFGv"
HTTP_LINK = "http://ipn.eg/S/alice/instapay/2DcFGv"
WRONG_DOMAIN_LINK = "https://notipn.eg/S/alice/instapay/2DcFGv"
INJECTION_LINK = "https://ipn.eg/S/alice/instapay/2DcFGv?x=javascript:alert(1)"


@pytest.fixture
def valid_handle() -> str:
    """A known-good InstaPay handle."""
    return VALID_HANDLE


@pytest.fixture
def valid_link() -> str:
    """A known-good InstaPay payment URL."""
    return VALID_LINK


@pytest.fixture
def valid_text() -> str:
    """Raw multi-line share-sheet text containing a valid InstaPay link."""
    return VALID_TEXT

"""Tests for instapay_eg.core - parsing, validation, and normalisation."""

import pytest

from instapay_eg.core import (
    InstaPayData,
    extract_handle,
    extract_link,
    extract_url_id,
    is_valid_handle,
    normalize_handle,
    parse_text,
)
from instapay_eg.exceptions import (
    InvalidHandleError,
    InvalidLinkError,
    LinkNotFoundError,
    PhishingLinkError,
)

from .conftest import (
    HTTP_LINK,
    PHISHING_LINK_SUBDOMAIN,
    VALID_HANDLE,
    VALID_LINK,
    VALID_TEXT,
)

# ---------------------------------------------------------------------------
# extract_link
# ---------------------------------------------------------------------------


class TestExtractLink:
    def test_extracts_link_from_multiline_text(self) -> None:
        assert extract_link(VALID_TEXT) == VALID_LINK

    def test_extracts_link_when_url_is_alone(self) -> None:
        assert extract_link(VALID_LINK) == VALID_LINK

    def test_extracts_first_link_when_multiple_present(self) -> None:
        text = f"{VALID_LINK}\nhttps://ipn.eg/S/bob/instapay/xyz"
        assert extract_link(text) == VALID_LINK

    def test_returns_none_when_no_link_present(self) -> None:
        assert extract_link("No URL here, just text.") is None

    def test_returns_none_for_empty_string(self) -> None:
        assert extract_link("") is None

    def test_does_not_match_http(self) -> None:
        assert extract_link(HTTP_LINK) is None

    def test_extracts_link_with_surrounding_whitespace(self) -> None:
        assert extract_link(f"  \n{VALID_LINK}\n  ") == VALID_LINK


# ---------------------------------------------------------------------------
# extract_handle
# ---------------------------------------------------------------------------


class TestExtractHandle:
    def test_extracts_handle_from_valid_link(self) -> None:
        assert extract_handle(VALID_LINK) == VALID_HANDLE

    def test_returns_none_for_link_without_instapay_segment(self) -> None:
        assert extract_handle("https://ipn.eg/S/alice/other/2DcFGv") is None

    def test_returns_none_for_empty_string(self) -> None:
        assert extract_handle("") is None

    def test_returns_none_for_none_like_empty(self) -> None:
        assert extract_handle("   ") is None

    def test_handles_handle_with_dots(self) -> None:
        link = "https://ipn.eg/S/alice.smith/instapay/2DcFGv"
        assert extract_handle(link) == "alice.smith"

    def test_handles_handle_with_underscores(self) -> None:
        link = "https://ipn.eg/S/alice_smith/instapay/2DcFGv"
        assert extract_handle(link) == "alice_smith"


# ---------------------------------------------------------------------------
# extract_url_id
# ---------------------------------------------------------------------------


class TestExtractUrlId:
    def test_extracts_token_from_valid_link(self) -> None:
        assert extract_url_id(VALID_LINK) == "2DcFGv"

    def test_returns_none_for_link_without_token(self) -> None:
        assert extract_url_id("https://ipn.eg/S/alice/instapay") is None

    def test_returns_none_for_empty_string(self) -> None:
        assert extract_url_id("") is None


# ---------------------------------------------------------------------------
# is_valid_handle
# ---------------------------------------------------------------------------


class TestIsValidHandle:
    def test_valid_simple_handle(self) -> None:
        assert is_valid_handle("alice") is True

    def test_valid_handle_with_suffix(self) -> None:
        assert is_valid_handle("alice@instapay") is True

    def test_valid_handle_with_dots(self) -> None:
        assert is_valid_handle("alice.smith") is True

    def test_valid_handle_with_underscores(self) -> None:
        assert is_valid_handle("alice_smith") is True

    def test_valid_handle_with_hyphens(self) -> None:
        assert is_valid_handle("alice-smith") is True

    def test_valid_handle_with_digits(self) -> None:
        assert is_valid_handle("alice123") is True

    def test_invalid_handle_with_spaces(self) -> None:
        assert is_valid_handle("alice smith") is False

    def test_invalid_handle_with_special_chars(self) -> None:
        assert is_valid_handle("alice!!!") is False

    def test_invalid_handle_with_at_sign(self) -> None:
        # '@' is invalid except as part of the @instapay suffix
        assert is_valid_handle("alice@bob") is False

    def test_empty_string_is_invalid(self) -> None:
        assert is_valid_handle("") is False

    def test_whitespace_only_is_invalid(self) -> None:
        assert is_valid_handle("   ") is False


# ---------------------------------------------------------------------------
# normalize_handle
# ---------------------------------------------------------------------------


class TestNormalizeHandle:
    def test_strips_instapay_suffix(self) -> None:
        assert normalize_handle("alice@instapay") == "alice"

    def test_strips_whitespace(self) -> None:
        assert normalize_handle("  alice  ") == "alice"

    def test_strips_suffix_and_whitespace(self) -> None:
        assert normalize_handle("  alice@instapay  ") == "alice"

    def test_does_not_lowercase(self) -> None:
        # Case is preserved - InstaPay handles are case-sensitive
        assert normalize_handle("Alice@instapay") == "Alice"

    def test_plain_handle_unchanged(self) -> None:
        assert normalize_handle("alice") == "alice"


# ---------------------------------------------------------------------------
# parse_text
# ---------------------------------------------------------------------------


class TestParseText:
    def test_happy_path_returns_instapay_data(self, valid_text: str) -> None:
        data = parse_text(valid_text)
        assert isinstance(data, InstaPayData)
        assert data.link == VALID_LINK
        assert data.handle == VALID_HANDLE
        assert data.formatted_handle == f"{VALID_HANDLE}@instapay"
        assert data.is_verified is True

    def test_extracts_raw_url_id(self) -> None:
        data = parse_text(VALID_TEXT)
        assert data.raw_url_id == "2DcFGv"

    def test_raw_url_id_is_always_present(self) -> None:
        # raw_url_id is now str, not Optional - parse_text requires the token.
        data = parse_text(VALID_TEXT)
        assert isinstance(data.raw_url_id, str)
        assert len(data.raw_url_id) > 0

    def test_raises_link_not_found_when_no_url(self) -> None:
        with pytest.raises(LinkNotFoundError):
            parse_text("No link here at all.")

    def test_raises_link_not_found_for_empty_string(self) -> None:
        with pytest.raises(LinkNotFoundError):
            parse_text("")

    def test_raises_phishing_error_for_subdomain_spoof(self) -> None:
        with pytest.raises(PhishingLinkError):
            parse_text(PHISHING_LINK_SUBDOMAIN)

    def test_raises_link_not_found_for_http(self) -> None:
        with pytest.raises(LinkNotFoundError):
            parse_text(HTTP_LINK)

    def test_raises_link_not_found_for_wrong_domain(self) -> None:
        with pytest.raises(LinkNotFoundError):
            parse_text("https://notipn.eg/S/alice/instapay/2DcFGv")

    def test_raises_invalid_link_for_injection(self) -> None:
        injection = "https://ipn.eg/S/alice/instapay/javascript:alert(1)"
        with pytest.raises(InvalidLinkError):
            parse_text(injection)

    def test_raises_invalid_link_for_missing_token(self) -> None:
        # A link without the server-generated token is non-functional.
        with pytest.raises(InvalidLinkError):
            parse_text("https://ipn.eg/S/alice/instapay")

    def test_raises_invalid_handle_for_handleless_url(self) -> None:
        with pytest.raises(InvalidHandleError):
            parse_text("https://ipn.eg/S/no-handle-here/token123")

    def test_raises_invalid_link_for_url_without_s_prefix_invalid_prefix(self) -> None:
        with pytest.raises(LinkNotFoundError):
            parse_text("https://ipn.eg/pay/alice/instapay/2DcFGv")

    def test_raises_invalid_link_for_url_without_s_prefix(self) -> None:
        with pytest.raises(LinkNotFoundError):
            parse_text("https://ipn.eg/alice/instapay/2DcFGv")

    def test_raises_invalid_handle_for_malformed_handle_in_url(self) -> None:
        # _alice starts with underscore: valid path char but fails
        # _VALID_HANDLE_REGEX which requires alphanumeric start.
        with pytest.raises(InvalidHandleError):
            parse_text("https://ipn.eg/S/_alice/instapay/tok123")

    def test_phishing_error_is_subclass_of_invalid_link_error(self) -> None:
        with pytest.raises(InvalidLinkError):
            parse_text(PHISHING_LINK_SUBDOMAIN)

    def test_all_errors_are_subclass_of_instapay_error(self) -> None:
        from instapay_eg.exceptions import InstaPayError

        with pytest.raises(InstaPayError):
            parse_text("no link")

    def test_instapay_data_is_immutable(self, valid_text: str) -> None:
        data = parse_text(valid_text)
        with pytest.raises(Exception):  # noqa: B017
            data.link = "https://ipn.eg/S/evil/instapay/xyz"  # ty:ignore[invalid-assignment]

    def test_parses_link_url_alone(self) -> None:
        data = parse_text(VALID_LINK)
        assert data.link == VALID_LINK

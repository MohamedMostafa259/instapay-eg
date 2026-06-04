"""Tests for instapay_eg.security - link auditing and phishing detection."""

import pytest

from instapay_eg.exceptions import PhishingLinkError
from instapay_eg.security import (
    SecurityReport,
    audit_link,
    is_phishing_domain,
    is_safe_link,
)

from .conftest import (
    HTTP_LINK,
    INJECTION_LINK,
    PHISHING_LINK_HYPHEN,
    PHISHING_LINK_SUBDOMAIN,
    VALID_LINK,
    WRONG_DOMAIN_LINK,
)

# ---------------------------------------------------------------------------
# is_safe_link
# ---------------------------------------------------------------------------


class TestIsSafeLink:
    def test_valid_https_ipn_link_is_safe(self) -> None:
        assert is_safe_link(VALID_LINK) is True

    def test_http_link_is_not_safe(self) -> None:
        assert is_safe_link(HTTP_LINK) is False

    def test_wrong_domain_is_not_safe(self) -> None:
        assert is_safe_link(WRONG_DOMAIN_LINK) is False

    def test_empty_string_is_not_safe(self) -> None:
        assert is_safe_link("") is False

    def test_injection_link_is_not_safe(self) -> None:
        assert is_safe_link(INJECTION_LINK) is False

    def test_phishing_subdomain_raises_phishing_error(self) -> None:
        with pytest.raises(PhishingLinkError):
            is_safe_link(PHISHING_LINK_SUBDOMAIN)

    def test_phishing_hyphen_domain_raises_phishing_error(self) -> None:
        with pytest.raises(PhishingLinkError):
            is_safe_link(PHISHING_LINK_HYPHEN)

    def test_phishing_error_message_contains_url(self) -> None:
        with pytest.raises(PhishingLinkError):
            is_safe_link(PHISHING_LINK_SUBDOMAIN)


# ---------------------------------------------------------------------------
# audit_link
# ---------------------------------------------------------------------------


class TestAuditLink:
    def test_valid_link_produces_safe_report(self) -> None:
        report = audit_link(VALID_LINK)
        assert isinstance(report, SecurityReport)
        assert report.is_safe is True
        assert report.scheme_valid is True
        assert report.domain_valid is True
        assert report.has_injection is False
        assert report.phishing_risk is False
        assert report.failure_reason is None
        assert report.url == VALID_LINK

    def test_http_link_produces_unsafe_report(self) -> None:
        report = audit_link(HTTP_LINK)
        assert report.is_safe is False
        assert report.scheme_valid is False
        assert report.domain_valid is True
        assert report.failure_reason is not None

    def test_wrong_domain_produces_unsafe_report(self) -> None:
        report = audit_link(WRONG_DOMAIN_LINK)
        assert report.is_safe is False
        assert report.domain_valid is False

    def test_phishing_subdomain_flags_phishing_risk(self) -> None:
        report = audit_link(PHISHING_LINK_SUBDOMAIN)
        assert report.is_safe is False
        assert report.phishing_risk is True
        assert report.failure_reason is not None
        assert "phishing" in report.failure_reason.lower()

    def test_injection_link_flags_injection(self) -> None:
        report = audit_link(INJECTION_LINK)
        assert report.is_safe is False
        assert report.has_injection is True

    def test_empty_string_returns_all_false_report(self) -> None:
        report = audit_link("")
        assert report.is_safe is False
        assert report.scheme_valid is False
        assert report.domain_valid is False
        assert report.has_injection is False
        assert report.phishing_risk is False
        assert report.failure_reason is not None

    def test_report_is_immutable(self) -> None:
        report = audit_link(VALID_LINK)
        with pytest.raises(Exception):  # noqa: B017
            report.is_safe = False  # ty:ignore[invalid-assignment]

    def test_data_colon_injection_detected(self) -> None:
        url = "https://ipn.eg/S/alice/instapay/data:text/html,evil"
        report = audit_link(url)
        assert report.has_injection is True
        assert report.is_safe is False

    def test_vbscript_injection_detected(self) -> None:
        url = "https://ipn.eg/S/alice/instapay/vbscript:evil"
        report = audit_link(url)
        assert report.has_injection is True

    def test_invalid_path_characters_detected(self) -> None:
        # %20 (URL-encoded space) contains %, which fails the path whitelist
        # but is NOT in the injection substring list - exercises has_invalid_path.
        url = "https://ipn.eg/S/alice/instapay/path%20here"
        report = audit_link(url)
        assert report.has_invalid_path is True
        assert report.has_injection is False
        assert report.is_safe is False
        assert report.failure_reason == "URL path contains disallowed characters."


# ---------------------------------------------------------------------------
# is_phishing_domain
# ---------------------------------------------------------------------------


class TestIsPhishingDomain:
    def test_legitimate_domain_is_not_phishing(self) -> None:
        assert is_phishing_domain(VALID_LINK) is False

    def test_subdomain_spoof_is_phishing(self) -> None:
        assert is_phishing_domain(PHISHING_LINK_SUBDOMAIN) is True

    def test_hyphen_domain_is_phishing(self) -> None:
        assert is_phishing_domain(PHISHING_LINK_HYPHEN) is True

    def test_instapay_keyword_in_domain_is_phishing(self) -> None:
        assert is_phishing_domain("https://instapay.fakesite.com/pay") is True

    def test_empty_string_is_not_phishing(self) -> None:
        assert is_phishing_domain("") is False

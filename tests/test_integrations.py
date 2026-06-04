"""Tests for instapay_eg.integrations - pydantic and qrcode."""

import base64
import importlib
import sys

import pytest
import segno
from django.core.exceptions import ValidationError as DjangoValidationError
from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError

from instapay_eg.integrations import qrcode as qr_mod
from instapay_eg.integrations.django import InstaPayHandleFormField, InstaPayLinkField
from instapay_eg.integrations.pydantic import (
    InstaPayHandle,
    InstaPayLink,
    InstaPayPaymentModel,
)
from instapay_eg.integrations.qrcode import (
    generate_qr,
    qr_as_base64,
    qr_as_bytes,
    qr_as_svg_string,
    save_qr,
)

from .conftest import PHISHING_LINK_SUBDOMAIN, VALID_HANDLE, VALID_LINK, VALID_TEXT

# ---------------------------------------------------------------------------
# Pydantic integration
# ---------------------------------------------------------------------------


class TestPydanticIntegration:
    @pytest.fixture(autouse=True)
    def _import_pydantic(self) -> None:
        pytest.importorskip("pydantic")

    def test_instapay_link_accepts_raw_text(self) -> None:
        class Model(BaseModel):
            link: InstaPayLink

        m = Model(link=VALID_TEXT)
        assert m.link == VALID_LINK

    def test_instapay_link_accepts_url_directly(self) -> None:
        class Model(BaseModel):
            link: InstaPayLink

        m = Model(link=VALID_LINK)
        assert m.link == VALID_LINK

    def test_instapay_link_rejects_phishing_url(self) -> None:
        class Model(BaseModel):
            link: InstaPayLink

        with pytest.raises(PydanticValidationError):
            Model(link=PHISHING_LINK_SUBDOMAIN)

    def test_instapay_link_rejects_non_string(self) -> None:
        class Model(BaseModel):
            link: InstaPayLink

        with pytest.raises(PydanticValidationError):
            Model(link=12345)  # ty:ignore[invalid-argument-type]

    def test_instapay_handle_accepts_plain_handle(self) -> None:
        class Model(BaseModel):
            handle: InstaPayHandle

        m = Model(handle=VALID_HANDLE)
        assert m.handle == VALID_HANDLE

    def test_instapay_handle_strips_suffix(self) -> None:
        class Model(BaseModel):
            handle: InstaPayHandle

        m = Model(handle=f"{VALID_HANDLE}@instapay")
        assert m.handle == VALID_HANDLE

    def test_instapay_handle_rejects_invalid_chars(self) -> None:
        class Model(BaseModel):
            handle: InstaPayHandle

        with pytest.raises(PydanticValidationError):
            Model(handle="alice!!!")

    def test_instapay_payment_model(self) -> None:
        m = InstaPayPaymentModel(link=VALID_TEXT, handle=VALID_HANDLE)
        assert m.link == VALID_LINK
        assert m.handle == VALID_HANDLE


# ---------------------------------------------------------------------------
# QR code integration
# ---------------------------------------------------------------------------


class TestQrcodeIntegration:
    @pytest.fixture(autouse=True)
    def _import_segno(self) -> None:
        pytest.importorskip("segno")

    def test_qr_as_bytes_returns_bytes(self) -> None:
        result = qr_as_bytes(VALID_LINK)
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_qr_as_bytes_is_valid_png(self) -> None:
        result = qr_as_bytes(VALID_LINK, file_format="png")
        # PNG magic bytes: \x89PNG
        assert result[:4] == b"\x89PNG"

    def test_qr_as_base64_returns_string(self) -> None:
        result = qr_as_base64(VALID_LINK)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_qr_as_base64_is_valid_base64(self) -> None:
        result = qr_as_base64(VALID_LINK)
        # Should not raise
        decoded = base64.b64decode(result)
        assert len(decoded) > 0

    def test_qr_as_svg_string_returns_svg(self) -> None:
        result = qr_as_svg_string(VALID_LINK)
        assert isinstance(result, str)
        assert "<svg" in result

    def test_generate_qr_returns_qr_object(self) -> None:
        result = generate_qr(VALID_LINK)
        assert isinstance(result, segno.QRCode)

    def test_save_qr_writes_file(self, tmp_path) -> None:
        out = tmp_path / "test_qr.png"
        save_qr(VALID_LINK, out)
        assert out.exists()
        assert out.stat().st_size > 0


class TestImportErrorMessages:
    def test_segno_missing_raises_helpful_error(self, monkeypatch) -> None:
        monkeypatch.setitem(sys.modules, "segno", None)
        importlib.reload(qr_mod)
        with pytest.raises(ImportError):
            qr_mod._get_segno()


# ---------------------------------------------------------------------------
# Django integration
# ---------------------------------------------------------------------------


def _configure_django() -> None:
    """Configure a minimal in-process Django setup for testing."""
    import django
    from django.conf import settings

    if not settings.configured:
        settings.configure(
            INSTALLED_APPS=[],
            DATABASES={},
            USE_TZ=True,
        )
        django.setup()


class TestDjangoIntegration:
    @pytest.fixture(autouse=True)
    def _setup_django(self) -> None:
        pytest.importorskip("django")
        _configure_django()

    def test_instapay_link_field_accepts_valid_link(self) -> None:
        field = InstaPayLinkField()
        result = field.clean(VALID_TEXT, None)
        assert result == VALID_LINK

    def test_instapay_link_field_accepts_url_directly(self) -> None:
        field = InstaPayLinkField()
        result = field.clean(VALID_LINK, None)
        assert result == VALID_LINK

    def test_instapay_link_field_rejects_phishing(self) -> None:
        field = InstaPayLinkField()
        with pytest.raises(DjangoValidationError):
            field.clean(PHISHING_LINK_SUBDOMAIN, None)

    def test_instapay_link_field_passes_through_none(self) -> None:
        field = InstaPayLinkField(blank=True, null=True)
        result = field.clean("", None)
        assert result == ""

    def test_instapay_handle_form_field_accepts_valid_handle(self) -> None:
        field = InstaPayHandleFormField()
        result = field.clean(VALID_HANDLE)
        assert result == VALID_HANDLE

    def test_instapay_handle_form_field_strips_suffix(self) -> None:
        field = InstaPayHandleFormField()
        result = field.clean(f"{VALID_HANDLE}@instapay")
        assert result == VALID_HANDLE

    def test_instapay_handle_form_field_rejects_invalid(self) -> None:
        field = InstaPayHandleFormField()
        with pytest.raises(DjangoValidationError):
            field.validate("alice!!!")

    def test_instapay_handle_form_field_validate_empty_passes(self) -> None:
        # Empty string skips the handle check (field-level required enforcement
        # is Django's job, not the handle validator's).
        field = InstaPayHandleFormField(required=False)
        field.validate("")  # must not raise

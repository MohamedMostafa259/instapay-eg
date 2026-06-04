"""Django integration for instapay-eg.

Provides a Django ORM model field and a Django form field for seamless
integration with Django applications.

Usage in a Django model::

    from django.db import models
    from instapay_eg.integrations.django import InstaPayLinkField

    class UserProfile(models.Model):
        instapay_link = InstaPayLinkField(blank=True, null=True)

Usage in a Django form::

    from django import forms
    from instapay_eg.integrations.django import InstaPayHandleFormField

    class PaymentForm(forms.Form):
        recipient = InstaPayHandleFormField()

Raises:
    ImportError: If ``django`` is not installed.  Install with
        ``pip install "instapay-eg[django]"``.
"""

from __future__ import annotations

from typing import Any

try:
    from django import forms
    from django.core.exceptions import ValidationError
    from django.db import models
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "The Django integration requires Django to be installed.\n"
        'Run: pip install "instapay-eg[django]"'
    ) from exc

from ..core import is_valid_handle, normalize_handle, parse_text
from ..exceptions import InstaPayError


class InstaPayLinkField(models.CharField):
    """A Django model field that stores a validated InstaPay payment link.

    On ``full_clean()`` / ``save()``, the field automatically:

    1. Extracts the ``https://ipn.eg`` URL from the raw input (so users can
       paste the full share-sheet text directly).
    2. Runs all security checks (HTTPS, domain, phishing patterns).
    3. Stores only the clean URL - not the surrounding text.

    Args:
        max_length: Column length.  Defaults to ``500``, which comfortably
            fits any InstaPay URL.
        **kwargs: Passed directly to :class:`django.db.models.CharField`.

    Example::

        class Professional(models.Model):
            instapay_link = InstaPayLinkField(blank=True, null=True)
    """

    description = "A validated Egyptian InstaPay payment link."

    def __init__(self, *args: Any, max_length: int = 500, **kwargs: Any) -> None:
        """Initialise the field with a sensible default ``max_length``."""
        super().__init__(*args, max_length=max_length, **kwargs)

    def clean(self, value: Any, model_instance: Any) -> str | None:
        """Validate and clean the field value.

        Args:
            value: The raw input value.
            model_instance: The model instance being saved.

        Returns:
            The validated InstaPay URL, or ``None`` if the field is nullable
            and the value is empty.

        Raises:
            ValidationError: If the link is missing, insecure, or malformed.
        """
        value = super().clean(value, model_instance)
        if not value:
            return value
        try:
            return parse_text(str(value)).link
        except InstaPayError as exc:
            raise ValidationError(str(exc)) from exc


class InstaPayHandleFormField(forms.CharField):
    """A Django form field that validates an InstaPay handle.

    Accepts both ``'alice'`` and ``'alice@instapay'`` - the ``@instapay``
    suffix is stripped and normalised automatically.

    Example::

        class PaymentForm(forms.Form):
            recipient = InstaPayHandleFormField(
                label="InstaPay Handle",
                help_text="Enter the recipient's @instapay handle.",
            )
    """

    def validate(self, value: str) -> None:
        """Validate that *value* is a correctly formatted InstaPay handle.

        Args:
            value: The submitted form value.

        Raises:
            ValidationError: If the handle contains invalid characters.
        """
        super().validate(value)
        if value:
            clean = normalize_handle(value)
            if not is_valid_handle(clean):
                raise ValidationError(
                    f"{value!r} is not a valid InstaPay handle. "
                    "Handles may only contain letters, digits, underscores, "
                    "hyphens, and dots."
                )

    def clean(self, value: str) -> str:
        """Normalise and validate the handle.

        Args:
            value: The submitted form value.

        Returns:
            The normalised handle (without ``@instapay`` suffix).
        """
        value = super().clean(value)
        return normalize_handle(value) if value else value

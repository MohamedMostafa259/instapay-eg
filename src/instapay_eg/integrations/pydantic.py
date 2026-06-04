"""Pydantic v2 integration for instapay-eg.

Provides annotated types and a ready-made model that integrate seamlessly
with **Pydantic v2** and **FastAPI**.

Usage::

    from pydantic import BaseModel
    from instapay_eg.integrations.pydantic import InstaPayLink, InstaPayHandle

    class PaymentRequest(BaseModel):
        link: InstaPayLink          # validates + extracts the URL automatically
        recipient: InstaPayHandle   # validates the handle format

FastAPI example::

    from fastapi import FastAPI
    from instapay_eg.integrations.pydantic import InstaPayPaymentModel

    app = FastAPI()

    @app.post("/payments")
    async def create_payment(payment: InstaPayPaymentModel):
        return {"link": payment.link, "handle": payment.handle}

Raises:
    ImportError: If ``pydantic`` is not installed.  Install with
        ``pip install "instapay-eg[pydantic]"``.
"""

from __future__ import annotations

from typing import Annotated, Any

try:
    from pydantic import AfterValidator, BaseModel, Field
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "The pydantic integration requires pydantic to be installed.\n"
        'Run: pip install "instapay-eg[pydantic]"'
    ) from exc

from ..core import is_valid_handle, normalize_handle, parse_text
from ..exceptions import InstaPayError

# ---------------------------------------------------------------------------
# Validator functions (internal)
# ---------------------------------------------------------------------------


def _validate_instapay_link(v: Any) -> str:
    """Pydantic AfterValidator: extract and security-check an InstaPay link."""
    try:
        return parse_text(v).link
    except InstaPayError as exc:
        raise ValueError(str(exc)) from exc


def _validate_instapay_handle(v: Any) -> str:
    """Pydantic AfterValidator: normalise and validate an InstaPay handle."""
    clean = normalize_handle(v)
    if not is_valid_handle(clean):
        raise ValueError(
            f"{v!r} is not a valid InstaPay handle. "
            "Handles may only contain letters, digits, underscores, hyphens, "
            "and dots."
        )
    return clean


# ---------------------------------------------------------------------------
# Annotated types - use these directly in your Pydantic models
# ---------------------------------------------------------------------------

InstaPayLink = Annotated[
    str,
    AfterValidator(_validate_instapay_link),
    Field(
        examples=["https://ipn.eg/S/alice/instapay/2DcFGv"],
        description=(
            "An Egyptian InstaPay payment link.  Accepts raw share-sheet "
            "text from the 'InstaPay Egypt' app (the link will be extracted "
            "and security-checked automatically)."
        ),
        json_schema_extra={
            "format": "uri",
            "pattern": r"^https://ipn\.eg/",
        },
    ),
]
"""Annotated ``str`` type that validates, extracts, and security-checks an
InstaPay payment link.  Use this as a field type in any Pydantic ``BaseModel``
or FastAPI request/response schema."""

InstaPayHandle = Annotated[
    str,
    AfterValidator(_validate_instapay_handle),
    Field(
        examples=["alice", "alice@instapay"],
        description=(
            "An InstaPay handle.  The ``@instapay`` suffix is stripped "
            "and normalised automatically."
        ),
        json_schema_extra={
            "pattern": r"^[a-zA-Z0-9]+([._\-][a-zA-Z0-9]+)*$",
        },
    ),
]
"""Annotated ``str`` type that validates and normalises an InstaPay handle.
Accepts both ``'alice'`` and ``'alice@instapay'`` - the suffix is stripped."""


# ---------------------------------------------------------------------------
# Ready-made base model
# ---------------------------------------------------------------------------


class InstaPayPaymentModel(BaseModel):
    """A ready-to-use Pydantic model representing an InstaPay payment request.

    Attributes:
        link: The validated InstaPay payment URL.
        handle: The normalised recipient handle (without ``@instapay``).

    Example::

        class MyPaymentForm(InstaPayPaymentModel):
            note: str = ""

        form = MyPaymentForm(
            link="https://ipn.eg/S/alice/instapay/2DcFGv",
            handle="alice",
        )
    """

    link: InstaPayLink
    handle: InstaPayHandle

"""QR code generation integration for instapay-eg.

Generates QR codes for InstaPay payment links using the ``segno`` library.
Supports PNG, SVG, and base64-encoded output - covering every common use case
from saving to disk, embedding in web pages, and returning from JSON APIs.

Usage::

    from instapay_eg.integrations.qrcode import qr_as_base64, save_qr

    # For a JSON API response:
    b64 = qr_as_base64("https://ipn.eg/S/alice/instapay/2DcFGv")

    # For saving to disk:
    save_qr("https://ipn.eg/S/alice/instapay/2DcFGv", "alice_payment.png")

Raises:
    ImportError: If ``segno`` is not installed.  Install with
        ``pip install "instapay-eg[qrcode]"``.
"""

from __future__ import annotations

import base64
import io
from pathlib import Path
from types import ModuleType

segno_module: ModuleType | None = None


def _get_segno() -> ModuleType:
    """Import segno at runtime and raise a helpful error if it is missing."""
    global segno_module
    try:
        import segno

        segno_module = segno
        return segno
    except ImportError as exc:
        raise ImportError(
            "The QR code integration requires segno to be installed.\n"
            'Run: pip install "instapay-eg[qrcode]"'
        ) from exc


def generate_qr(
    link: str,
    *,
    error: str = "m",
) -> segno_module.QRCode:  # ty:ignore[unresolved-attribute]
    """Generate a ``segno.QRCode`` object for *link*.

    Args:
        link: A validated ``https://ipn.eg`` payment URL.
        error: QR error correction level.  One of ``'l'``, ``'m'`` (default),
            ``'q'``, or ``'h'``.  Higher levels allow more of the QR code to
            be obscured while remaining scannable (useful when adding a logo).

    Returns:
        A :class:`segno.QRCode` instance.  Call ``.save()``, ``.svg_inline()``,
        or any other segno method on it directly.

    Example:
        >>> qr = generate_qr("https://ipn.eg/S/alice/instapay/2DcFGv")
        >>> qr.save("payment.png", scale=10)
    """
    segno = _get_segno()
    return segno.make(link, error=error)


def save_qr(
    link: str,
    path: str | Path,
    *,
    scale: int = 10,
    dark: str = "#1a1a2e",
    light: str = "#ffffff",
    file_format: str | None = None,
) -> None:
    """Save a QR code image for *link* to *path* on disk.

    The output format is inferred from the file extension of *path* (e.g.
    ``payment.png`` → PNG, ``payment.svg`` → SVG) unless *file_format* is
    given explicitly.

    Args:
        link: A validated ``https://ipn.eg`` payment URL.
        path: Destination file path.  Parent directories must already exist.
        scale: Pixel size of each QR module.  ``10`` produces a ~330x330 px
            image at the default data density.
        dark: Hex colour for the dark modules (default: deep navy ``#1a1a2e``).
        light: Hex colour for the light modules (default: white ``#ffffff``).
        file_format: Override the output format (e.g. ``'png'``, ``'svg'``).
            When ``None``, the format is inferred from *path*.

    Example:
        >>> save_qr(
        ...     "https://ipn.eg/S/alice/instapay/2DcFGv",
        ...     "alice_qr.png",
        ...     scale=12,
        ...     dark="#005f5f",
        ... )
    """
    qr = generate_qr(link)
    qr.save(
        str(path),
        scale=scale,
        dark=dark,
        light=light,
        kind=file_format,
    )


def qr_as_bytes(
    link: str,
    *,
    file_format: str = "png",
    scale: int = 10,
    dark: str = "#1a1a2e",
    light: str = "#ffffff",
) -> bytes:
    """Return the QR code image for *link* as raw bytes.

    Args:
        link: A validated ``https://ipn.eg`` payment URL.
        file_format: Image format.  ``'png'`` (default) or ``'svg'``.
        scale: Pixel size of each QR module.
        dark: Hex colour for the dark modules.
        light: Hex colour for the light modules.

    Returns:
        Raw image bytes in the requested format.

    Example:
        >>> png_bytes = qr_as_bytes("https://ipn.eg/S/alice/instapay/2DcFGv")
        >>> with open("payment.png", "wb") as f:
        ...     f.write(png_bytes)
    """
    qr = generate_qr(link)
    buf = io.BytesIO()
    qr.save(buf, kind=file_format, scale=scale, dark=dark, light=light)
    return buf.getvalue()


def qr_as_base64(
    link: str,
    *,
    file_format: str = "png",
    scale: int = 10,
    dark: str = "#1a1a2e",
    light: str = "#ffffff",
) -> str:
    """Return the QR code as a base64-encoded string, ready for a JSON API.

    The returned string can be embedded directly in an HTML ``<img>`` tag or
    returned from a REST endpoint without needing to write a file to disk.

    Args:
        link: A validated ``https://ipn.eg`` payment URL.
        file_format: Image format used for encoding.  ``'png'`` (default).
        scale: Pixel size of each QR module.
        dark: Hex colour for the dark modules.
        light: Hex colour for the light modules.

    Returns:
        A base64-encoded string of the QR code image (no ``data:`` prefix).

    Example:
        >>> b64 = qr_as_base64("https://ipn.eg/S/alice/instapay/2DcFGv")
        >>> html = f'<img src="data:image/png;base64,{b64}" />'
    """
    raw = qr_as_bytes(
        link, file_format=file_format, scale=scale, dark=dark, light=light
    )
    return base64.b64encode(raw).decode("ascii")


def qr_as_svg_string(
    link: str,
    *,
    scale: int = 10,
    dark: str = "#1a1a2e",
    light: str = "#ffffff",
) -> str:
    """Return the QR code as an inline SVG string.

    The returned string can be injected directly into an HTML document without
    a separate HTTP request, and scales perfectly at any resolution.

    Args:
        link: A validated ``https://ipn.eg`` payment URL.
        scale: Size multiplier for the SVG viewport.
        dark: Hex colour for the dark modules.
        light: Hex colour for the light modules.

    Returns:
        A complete ``<svg>...</svg>`` string.

    Example:
        >>> svg = qr_as_svg_string("https://ipn.eg/S/alice/instapay/2DcFGv")
        >>> html_response = f"<div class='qr-container'>{svg}</div>"
    """
    qr = generate_qr(link)
    buf = io.BytesIO()
    qr.save(buf, kind="svg", scale=scale, dark=dark, light=light, svgid="instapay-qr")
    return buf.getvalue().decode("utf-8")

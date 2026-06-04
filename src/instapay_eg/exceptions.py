"""Custom exception hierarchy for instapay-eg.

All exceptions inherit from ``InstaPayError`` so callers can choose how
granular their ``except`` clause needs to be:

.. code-block:: python

    from instapay_eg import InstaPayError, PhishingLinkError

    try:
        data = parse_text(raw_input)
    except PhishingLinkError:
        log.warning("Phishing attempt blocked")
    except InstaPayError as exc:
        log.error("InstaPay parsing failed: %s", exc)
"""


class InstaPayError(Exception):
    """Base exception for all instapay-eg errors.

    Catch this to handle any error raised by this library without caring
    about the specific failure mode.
    """


class LinkNotFoundError(InstaPayError):
    """Raised when no ``https://ipn.eg`` URL is found in the input text."""


class InvalidLinkError(InstaPayError):
    """Raised when a URL is found but fails one or more validation checks."""


class PhishingLinkError(InvalidLinkError):
    """Raised when the URL's domain does not exactly match ``ipn.eg``.

    This is a specialisation of ``InvalidLinkError`` that signals a likely
    phishing or lookalike-domain attack.  Always log these occurrences.
    """


class InvalidHandleError(InstaPayError):
    """Raised when the InstaPay handle extracted from a link is malformed."""

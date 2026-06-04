"""Public API for the instapay_eg.integrations sub-package.

Import from the specific integration module for the cleanest experience:

.. code-block:: python

    from instapay_eg.integrations.pydantic import InstaPayLink
    from instapay_eg.integrations.qrcode import qr_as_base64
    from instapay_eg.integrations.django import InstaPayLinkField

This ``__init__.py`` intentionally does **not** re-export integration symbols.
Doing so would eagerly import optional dependencies (pydantic, segno, django)
even when the user has not installed them.
"""

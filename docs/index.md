# Home

<p align="center">
  <strong>instapay-eg</strong> - Community SDK for Egyptian InstaPay payment links.<br>
  Zero dependencies for the core API. Built for Egyptian developers.
</p>

<p align="center">
  <a href="https://pepy.tech/projects/instapay-eg"><img alt="PyPI Downloads" src="https://static.pepy.tech/personalized-badge/instapay-eg?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads"></a>
</p>

<p align="center">
  <a href="https://mohamedmostafa259.github.io/instapay-eg/"><strong>📚 Documentation</strong></a> &middot;
  <a href="https://pypi.org/project/instapay-eg/"><strong>📦 PyPI Page</strong></a> &middot;
  <a href="https://github.com/MohamedMostafa259/instapay-eg"><strong>🐙 GitHub Repo</strong></a>
</p>

## What Can It Do?

In three lines of code:

```python
from instapay_eg import parse_text

data = parse_text("https://ipn.eg/S/alice/instapay/2DcFGv\nClick the link...\nalice@instapay")
print(data.handle)  # alice
```

See the [Quick Start](quickstart.md) for the full tour, or jump to:

- [Installation](installation.md) - `pip install instapay-eg`
- [Pydantic & FastAPI](integrations/pydantic.md) - Drop-in annotated types
- [Django](integrations/django.md) - ORM model field
- [QR Codes](integrations/qrcode.md) - PNG, SVG, base64

## Why Does This Exist?

InstaPay's mobile app generates share-sheet text like this:

```
https://ipn.eg/S/alice/instapay/2DcFGv
Click the link to send money to
alice@instapay
Powered by InstaPay
```

Developers who accept InstaPay payments in their apps need to:

1. Extract the URL from that blob of text
2. Verify it's not a phishing or lookalike-domain link
3. Store just the clean URL in their database
4. Optionally generate a QR code for display

**instapay-eg** does all of this safely and correctly, so you don't have to write and maintain your own regex and security checks.

## Disclaimer

!!! warning "Community Package"
    This is an community-driven utility package. It is not affiliated with,
    endorsed by, or associated with the Egyptian Banks Company (EBC) or InstaPay Egypt.

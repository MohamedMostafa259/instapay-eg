# instapay-eg

<p align="center">
  <img src="docs/assets/logo.png" alt="instapay-eg logo" width="200" />
</p>

<p align="center">
  <strong>Community SDK for Egyptian InstaPay payment links.</strong><br>
  Parse, validate, audit, and generate QR codes - with zero core dependencies.
</p>

<p align="center">
  <a href="https://pypi.org/project/instapay-eg/"><img alt="PyPI" src="https://img.shields.io/pypi/v/instapay-eg.svg?label=PyPI&color=teal"></a>
  <a href="https://pypi.org/project/instapay-eg/"><img alt="Python" src="https://img.shields.io/pypi/pyversions/instapay-eg.svg"></a>
  <a href="https://github.com/MohamedMostafa259/instapay-eg/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/MohamedMostafa259/instapay-eg/actions/workflows/ci.yml/badge.svg"></a>
  <a href="https://codecov.io/gh/MohamedMostafa259/instapay-eg"><img alt="Coverage" src="https://codecov.io/gh/MohamedMostafa259/instapay-eg/branch/main/graph/badge.svg"></a>
  <a href="https://github.com/MohamedMostafa259/instapay-eg/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/github/license/MohamedMostafa259/instapay-eg.svg?color=blue"></a>
</p>

---

## What is instapay-eg?

**instapay-eg** is a Python SDK for working with [Egyptian InstaPay](https://instapay.eg/) payment links (`https://ipn.eg/...`).

InstaPay is Egypt's national instant payment network, built by the Egyptian Banks Company (EBC). Developers building Egyptian fintech applications - food delivery, e-commerce, booking platforms, freelance marketplaces - regularly need to:

- Parse the multi-line share-sheet text the InstaPay app produces
- Verify that a link is genuinely from InstaPay and not a phishing URL
- Extract a user's handle for display or storage
- Generate QR codes for payment requests
- Integrate payment link validation into their Pydantic/FastAPI or Django models

This SDK solves all of that with a clean, typed, zero-dependency core API.

## Features

| Feature | Details |
|---|---|
| 🔍 **Smart Parsing** | Extracts the URL from raw multi-line share-sheet text automatically |
| 🛡️ **Anti-Phishing** | Detects lookalike domains, homoglyph attacks, and injection payloads |
| 🔬 **Security Audit** | `audit_link()` returns a structured `SecurityReport` for logging |
| 🏗️ **Link Building** | `build_link(handle)` generates valid `ipn.eg` URLs programmatically |
| 📱 **QR Codes** | PNG, SVG, bytes, and base64 - covers every web and mobile use case |
| 🤝 **Pydantic v2** | Annotated types (`InstaPayLink`, `InstaPayHandle`) for FastAPI schemas |
| 🦄 **Django** | `InstaPayLinkField` ORM field and `InstaPayHandleFormField` form field |
| 💻 **CLI** | `instapay parse "..."`, `instapay audit "..."`, `instapay build --handle ...` |
| ✅ **100% Typed** | Full `py.typed` marker, passes strict type checking |
| 🧪 **100% Tested** | 100% branch coverage enforced in CI |

## Installation

**Using pip:**
```bash
pip install instapay-eg
```

**Using uv:**
```bash
uv add instapay-eg
```

### With Optional Extras

```bash
# For Pydantic / FastAPI integration:
pip install "instapay-eg[pydantic]"

# For QR code generation:
pip install "instapay-eg[qrcode]"

# For Django integration:
pip install "instapay-eg[django]"

# Everything at once:
pip install "instapay-eg[all]"
```

## Quick Demo

```python
from instapay_eg import parse_text

# Paste the raw text from the InstaPay app share sheet:
raw = """
https://ipn.eg/S/alice/instapay/2DcFGv
Click the link to send money to
alice@instapay
Powered by InstaPay
"""

data = parse_text(raw)

print(data.link)            # https://ipn.eg/S/alice/instapay/2DcFGv
print(data.handle)          # alice
print(data.formatted_handle) # alice@instapay
print(data.raw_url_id)      # 2DcFGv
print(data.is_verified)     # True
```

### Security Audit

```python
from instapay_eg import audit_link

# Check a suspicious link:
report = audit_link("https://ipn.eg.evil.com/S/alice/instapay/fake")

print(report.is_safe)        # False
print(report.phishing_risk)  # True
print(report.failure_reason) # "Domain 'ipn.eg.evil.com' matches a known phishing pattern."
```

### Pydantic / FastAPI

```python
from fastapi import FastAPI
from pydantic import BaseModel
from instapay_eg.integrations.pydantic import InstaPayLink, InstaPayHandle

class PaymentRequest(BaseModel):
    # Users can paste raw share-sheet text - the link is extracted & verified automatically
    link: InstaPayLink
    recipient: InstaPayHandle

app = FastAPI()

@app.post("/payments")
async def create_payment(payment: PaymentRequest):
    return {"link": payment.link, "recipient": payment.recipient}
```

### QR Code Generation

```python
from instapay_eg.integrations.qrcode import qr_as_base64, save_qr

link = "https://ipn.eg/S/alice/instapay/2DcFGv"

# Return in a JSON API response - no file I/O needed:
b64 = qr_as_base64(link)
# → Use in HTML: <img src="data:image/png;base64,{b64}" />

# Or save to disk:
save_qr(link, "alice_payment_qr.png")
```

### CLI

```bash
# Parse share-sheet text:
$ instapay parse "https://ipn.eg/S/alice/instapay/2DcFGv Click to pay..."
  Link:    https://ipn.eg/S/alice/instapay/2DcFGv
  Handle:  alice
  Format:  alice@instapay
  Safe:    ✅ Yes

# Audit a suspicious URL:
$ instapay audit "https://ipn.eg.evil.com/S/alice/instapay/fake"
  Status:   ❌ UNSAFE - DO NOT USE
  Phishing: ❌ LOOKALIKE DOMAIN DETECTED

# Build a link from a handle:
$ instapay build --handle alice
  Generated URL: https://ipn.eg/S/alice/instapay
```

## Documentation

Full documentation is available at **[mohamedmostafa259.github.io/instapay-eg](https://mohamedmostafa259.github.io/instapay-eg/)**.

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

## Disclaimer

> *This is an community-driven utility package. It is not affiliated with, endorsed by, or associated with the Egyptian Banks Company (EBC) or InstaPay Egypt.*

## License

MIT - see [LICENSE](LICENSE) for details.

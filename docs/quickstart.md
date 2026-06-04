# Quick Start

Five copy-paste examples to get you up and running in under five minutes.

## 1. Parse Share-Sheet Text

```python
from instapay_eg import parse_text

raw = """
https://ipn.eg/S/alice/instapay/2DcFGv
Click the link to send money to
alice@instapay
Powered by InstaPay
"""

data = parse_text(raw)

print(data.link)             # https://ipn.eg/S/alice/instapay/2DcFGv
print(data.handle)           # alice
print(data.formatted_handle) # alice@instapay
print(data.raw_url_id)       # 2DcFGv
print(data.is_verified)      # True
```

## 2. Handle Errors Gracefully

```python
from instapay_eg import parse_text
from instapay_eg import InstaPayError, LinkNotFoundError, PhishingLinkError

try:
    data = parse_text(user_provided_text)
except PhishingLinkError:
    # Log this - it's likely an attempted attack
    logger.warning("Phishing link blocked")
except LinkNotFoundError:
    # The user pasted something that isn't an InstaPay share
    return {"error": "No InstaPay link found in your text."}
except InstaPayError as exc:
    # Catch-all for any other library error
    return {"error": str(exc)}
```

## 3. Audit a Suspicious URL

```python
from instapay_eg import audit_link

report = audit_link("https://ipn.eg.evil.com/S/alice/instapay/fake")

if not report.is_safe:
    print(f"Blocked: {report.failure_reason}")
    # Blocked: Domain 'ipn.eg.evil.com' matches a known phishing pattern.
```

## 4. FastAPI Endpoint with Pydantic

```python
from fastapi import FastAPI
from pydantic import BaseModel
from instapay_eg.integrations.pydantic import InstaPayLink, InstaPayHandle

class PaymentCreate(BaseModel):
    # Accepts raw share-sheet text - extracts and validates the link automatically
    link: InstaPayLink
    recipient: InstaPayHandle

app = FastAPI()

@app.post("/payments", status_code=201)
async def create_payment(body: PaymentCreate):
    # body.link is always a clean, verified https://ipn.eg URL
    await db.payments.insert(link=body.link, handle=body.recipient)
    return {"status": "created", "link": body.link}
```

## 5. Generate a QR Code for a Payment Link

```python
from instapay_eg.integrations.qrcode import qr_as_base64, save_qr

link = "https://ipn.eg/S/alice/instapay/2DcFGv"

# For a web API - embed directly in JSON:
b64 = qr_as_base64(link)
return {"qr_code": f"data:image/png;base64,{b64}"}

# Or save to disk:
save_qr(link, "payment_qr.png")
```

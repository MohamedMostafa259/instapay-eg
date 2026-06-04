# Pydantic & FastAPI Integration

Install: `pip install "instapay-eg[pydantic]"`

## Annotated Types

Use `InstaPayLink` and `InstaPayHandle` as drop-in field types in any Pydantic `BaseModel`:

```python
from pydantic import BaseModel
from instapay_eg.integrations.pydantic import InstaPayLink, InstaPayHandle

class PaymentCreate(BaseModel):
    # Users can paste raw share-sheet text - the link is extracted automatically
    link: InstaPayLink
    recipient: InstaPayHandle
    note: str = ""
```

When a request comes in:

- `link` accepts raw share-sheet text **or** a clean URL - both work
- The `@instapay` suffix is stripped from `recipient` automatically
- A `ValidationError` is raised if the link is a phishing URL or the handle is malformed
- The stored value is always the clean `https://ipn.eg/S/...` URL

## FastAPI Example

```python
from fastapi import FastAPI
from pydantic import BaseModel
from instapay_eg.integrations.pydantic import InstaPayLink, InstaPayHandle

app = FastAPI(title="My Payment API")

class PaymentRequest(BaseModel):
    link: InstaPayLink
    recipient: InstaPayHandle

class PaymentResponse(BaseModel):
    status: str
    link: str

@app.post("/payments", response_model=PaymentResponse, status_code=201)
async def create_payment(body: PaymentRequest):
    # body.link is guaranteed to be a clean, verified https://ipn.eg URL
    await db.payments.insert(link=body.link, handle=body.recipient)
    return PaymentResponse(status="created", link=body.link)
```

FastAPI automatically generates OpenAPI docs with:
- Description of the field
- Example values
- Format and pattern constraints

## Django Model Integration

```python
# Inside your Django app
from pydantic import BaseModel
from instapay_eg.integrations.pydantic import InstaPayLink

class ProfessionalCreate(BaseModel):
    salon_name: str | None = None
    # MAGIC: cleans the text, extracts the link, verifies it's not phishing:
    instapay_link: InstaPayLink | None = None
```

## `InstaPayPaymentModel`

A ready-to-use base model you can inherit from:

```python
from instapay_eg.integrations.pydantic import InstaPayPaymentModel

class MyPaymentForm(InstaPayPaymentModel):
    note: str = ""
    # Inherits: link: InstaPayLink, handle: InstaPayHandle
```

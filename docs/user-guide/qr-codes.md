# QR Codes

Install the QR extra first: `pip install "instapay-eg[qrcode]"`

## `qr_as_base64` - For JSON APIs

The most common use case: return a QR code from a REST endpoint without writing to disk.

```python
from instapay_eg.integrations.qrcode import qr_as_base64

link = "https://ipn.eg/S/alice/instapay/2DcFGv"
b64 = qr_as_base64(link)

# In a FastAPI response:
return {"qr_code": f"data:image/png;base64,{b64}"}

# In an HTML template:
# <img src="data:image/png;base64,{{ qr_code }}" alt="Pay alice via InstaPay" />
```

## `qr_as_svg_string` - For HTML Embedding

Inline SVG scales perfectly at any resolution - ideal for print or high-DPI screens:

```python
from instapay_eg.integrations.qrcode import qr_as_svg_string

svg = qr_as_svg_string(link)
# Inject directly into your HTML:
html = f'<div class="qr-container">{svg}</div>'
```

## `save_qr` - To Disk

```python
from instapay_eg.integrations.qrcode import save_qr

save_qr(link, "alice_payment.png", scale=12, dark="#005f5f")
save_qr(link, "alice_payment.svg")  # Format inferred from extension
```

## `qr_as_bytes` - Raw Bytes

For streaming, storing in a database, or sending over an HTTP response:

```python
from instapay_eg.integrations.qrcode import qr_as_bytes

png_bytes = qr_as_bytes(link)
# e.g., return as a StreamingResponse in FastAPI
```

## Customisation

All functions accept `dark` and `light` colour arguments (hex strings):

```python
qr_as_base64(link, dark="#1a1a2e", light="#ffffff", scale=10)
```

The `error` argument controls QR error correction level (`'l'`, `'m'`, `'q'`, `'h'`). Higher levels let you overlay a logo on the QR code without breaking scannability:

```python
from instapay_eg.integrations.qrcode import generate_qr

qr = generate_qr(link, error="h")  # 30% of the QR can be obscured
```

# Parsing Links

## The Main Entry Point: `parse_text`

`parse_text` is the primary function you will use. Pass in any string that might contain an InstaPay share link - including the full multi-line text from the app - and receive a clean, validated `InstaPayData` object.

```python
from instapay_eg import parse_text

data = parse_text(
    "https://ipn.eg/S/alice/instapay/2DcFGv\n"
    "Click the link to send money to\n"
    "alice@instapay\nPowered by InstaPay"
)
```

### The `InstaPayData` Object

| Field | Type | Description |
|---|---|---|
| `link` | `str` | The clean, verified `https://ipn.eg` URL |
| `handle` | `str` | The recipient's handle (e.g. `alice`) |
| `formatted_handle` | `str` | Handle with `@instapay` suffix (e.g. `alice@instapay`) |
| `raw_url_id` | `str \| None` | The short token at the end of the URL (e.g. `2DcFGv`) |
| `is_verified` | `bool` | Always `True` - all security checks have passed |

`InstaPayData` is a **frozen dataclass** - it is immutable after creation, which prevents accidental modification.

## Low-Level Primitives

If you need finer control, the primitives are also available:

```python
from instapay_eg import extract_link, extract_handle, extract_url_id

# Extract only the URL:
url = extract_link("... paste ... https://ipn.eg/S/alice/instapay/2DcFGv ...")
# → "https://ipn.eg/S/alice/instapay/2DcFGv"

# Extract only the handle:
handle = extract_handle("https://ipn.eg/S/alice/instapay/2DcFGv")
# → "alice"

# Extract only the token:
token = extract_url_id("https://ipn.eg/S/alice/instapay/2DcFGv")
# → "2DcFGv"
```

!!! note
    These primitives do **not** run security checks. Always prefer `parse_text` unless you have a specific reason to use them separately.

## Handle Utilities

```python
from instapay_eg import is_valid_handle, normalize_handle

# Validate a handle (accepts the @instapay suffix too):
is_valid_handle("alice")           # True
is_valid_handle("alice@instapay")  # True
is_valid_handle("alice!!!")        # False

# Normalize (strip suffix and whitespace, preserve case):
normalize_handle("  Alice@instapay  ")  # "Alice"
```

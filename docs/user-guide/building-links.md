# Building Links

## `build_link`

Generate a valid InstaPay payment URL from a handle programmatically:

```python
from instapay_eg import build_link

url = build_link("alice")
# → "https://ipn.eg/S/alice/instapay"

# The @instapay suffix is stripped automatically:
url = build_link("alice@instapay")
# → "https://ipn.eg/S/alice/instapay"
```

!!! note "About the Short Token"
    Real share-sheet links include a short token at the end (e.g. `/2DcFGv`).
    This token is generated server-side by InstaPay and cannot be reproduced locally.
    `build_link` produces the canonical base URL - sufficient for most programmatic uses
    (deep links, QR codes, display) without the token.

### When `build_link` Raises

```python
from instapay_eg import build_link
from instapay_eg import InvalidHandleError

try:
    url = build_link("alice with spaces")
except InvalidHandleError as exc:
    print(exc)
    # Cannot build link: 'alice with spaces' is not a valid InstaPay handle.
```

## `normalize_handle`

Strip the `@instapay` suffix and surrounding whitespace:

```python
from instapay_eg import normalize_handle

normalize_handle("  Alice@instapay  ")  # "Alice"
normalize_handle("alice")               # "alice"
```

## `is_valid_handle`

Check if a string meets InstaPay's character requirements:

```python
from instapay_eg import is_valid_handle

is_valid_handle("alice_smith.123")  # True - letters, digits, underscores, dots OK
is_valid_handle("alice smith")      # False - spaces not allowed
is_valid_handle("")                 # False - empty not allowed
```

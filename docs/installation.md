# Installation

## Requirements

- Python **3.10** or newer
- No mandatory runtime dependencies - the core API is pure stdlib

## Install the Core Package

=== "pip"
    ```bash
    pip install instapay-eg
    ```

=== "uv"
    ```bash
    uv add instapay-eg
    ```

=== "poetry"
    ```bash
    poetry add instapay-eg
    ```

## Install with Optional Extras

Some features require optional dependencies. Install only what you need:

| Extra | Installs | Unlocks |
|---|---|---|
| `pydantic` | `pydantic>=2.0` | `InstaPayLink`, `InstaPayHandle` annotated types |
| `qrcode` | `segno>=1.6.6` | QR code generation functions |
| `django` | `django>=3.2` | `InstaPayLinkField`, `InstaPayHandleFormField` |
| `all` | Everything above | All features |

```bash
# Pydantic / FastAPI
pip install "instapay-eg[pydantic]"

# QR code generation
pip install "instapay-eg[qrcode]"

# Django
pip install "instapay-eg[django]"

# Everything
pip install "instapay-eg[all]"
```

## Verify Installation

```python
import instapay_eg
print(instapay_eg.__version__)
```

You should see the current version number printed.

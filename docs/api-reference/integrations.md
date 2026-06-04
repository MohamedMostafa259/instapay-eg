# API Reference - Integrations

## Pydantic

::: instapay_eg.integrations.pydantic
    options:
      members:
        - InstaPayLink
        - InstaPayHandle
        - InstaPayPaymentModel

## QR Code

::: instapay_eg.integrations.qrcode
    options:
      members:
        - generate_qr
        - save_qr
        - qr_as_bytes
        - qr_as_base64
        - qr_as_svg_string

## Django

::: instapay_eg.integrations.django
    options:
      members:
        - InstaPayLinkField
        - InstaPayHandleFormField

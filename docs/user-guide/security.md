# Security & Anti-Phishing

## Why Security Matters

InstaPay links point to real money transfers. A phishing link like `https://ipn.eg.evil.com/S/alice/instapay/fake` is designed to:

1. Look legitimate at a glance
2. Redirect victims to a fraudulent payment page
3. Steal money or credentials

**instapay-eg** treats security as a first-class concern, not an afterthought.

## What Gets Checked

Every call to `parse_text` or `is_safe_link` automatically checks:

| Check | What it prevents |
|---|---|
| HTTPS scheme | HTTP links cannot be legitimate InstaPay links |
| Exact domain match (`ipn.eg`) | Subdomain-spoof attacks (`ipn.eg.evil.com`) |
| Injection payload detection | XSS / `javascript:` / `data:` injection |
| Phishing pattern matching | Lookalike domains (`ipn-eg.com`, `instapay.fakesite.com`, `1pn.eg`) |

## The Security Report

For logging and fraud pipelines, use `audit_link` to get a structured, machine-readable breakdown:

```python
from instapay_eg import audit_link

report = audit_link("https://ipn.eg.evil.com/S/alice/instapay/fake")

print(report.is_safe)        # False
print(report.phishing_risk)  # True
print(report.scheme_valid)   # True  (it's still HTTPS)
print(report.domain_valid)   # False
print(report.failure_reason) # "Domain 'ipn.eg.evil.com' matches a known phishing pattern."
```

### `SecurityReport` Fields

| Field | Type | Description |
|---|---|---|
| `is_safe` | `bool` | `True` only when all checks pass |
| `scheme_valid` | `bool` | `True` when scheme is `https` |
| `domain_valid` | `bool` | `True` when domain is exactly `ipn.eg` |
| `has_injection` | `bool` | `True` when an injection payload is detected |
| `phishing_risk` | `bool` | `True` when a phishing pattern matches |
| `failure_reason` | `str \| None` | Human-readable failure description |
| `url` | `str` | The audited URL |

## Exception Hierarchy

```python
InstaPayError
├── LinkNotFoundError      # No https://ipn.eg URL found in text
├── InvalidLinkError       # URL found but failed validation
│   └── PhishingLinkError  # Domain matches a phishing pattern (!) always log this
└── InvalidHandleError     # Handle malformed
```

!!! warning "Always Log `PhishingLinkError`"
    `PhishingLinkError` is a positive signal of an attempted attack, not just invalid input.
    Log it with the original URL and user context (IP address, user ID) to your fraud detection system.

## Checking a Domain Directly

```python
from instapay_eg import is_phishing_domain

is_phishing_domain("https://ipn.eg.evil.com/S/alice/instapay/x")  # True
is_phishing_domain("https://ipn.eg/S/alice/instapay/x")           # False
```

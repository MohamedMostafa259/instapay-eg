# Security Policy

## Supported Versions

| Version | Supported |
|---|---|
| 0.1.x | ✅ Yes |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Since this is a security-focused package (anti-phishing), responsible disclosure is critical.

**Send a private email to:** mohamedmostafa9557@gmail.com

Include in your report:
- A description of the vulnerability
- Steps to reproduce
- The potential impact
- Any suggested mitigations

### What to Expect

- **Acknowledgement** within 48 hours
- **Status update** within 7 days
- **Fix and disclosure** coordinated with you

We follow responsible disclosure - we will credit you in the release notes unless you prefer to remain anonymous.

## Scope

Issues in scope:
- Bypass of `is_safe_link` / `audit_link` security checks
- Phishing patterns that are not detected by the current regex list
- Injection payloads that pass through undetected

Issues out of scope:
- InstaPay's own infrastructure (report to EBC directly)
- Vulnerabilities in optional dependencies (report upstream)

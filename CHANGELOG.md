# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

*Changes staged for the next release will appear here.*

---

## [0.1.0] - 2026-06-04

### Added

- **Core parsing**: `parse_text`, `extract_link`, `extract_handle`, `extract_url_id` - parse raw InstaPay share-sheet text into structured data
- **`InstaPayData`** frozen dataclass with `link`, `handle`, `formatted_handle`, `raw_url_id`, and `is_verified` fields
- **Link building**: `build_link(handle)` generates valid `https://ipn.eg` payment URLs
- **Handle utilities**: `normalize_handle`, `is_valid_handle`
- **Security module**: `is_safe_link`, `audit_link`, `is_phishing_domain`, `SecurityReport` dataclass
- **Anti-phishing detection**: lookalike-domain, homoglyph, hyphen-substitution, and injection-payload checks
- **Custom exceptions**: `InstaPayError`, `LinkNotFoundError`, `InvalidLinkError`, `PhishingLinkError`, `InvalidHandleError`
- **Pydantic v2 integration**: `InstaPayLink`, `InstaPayHandle` annotated types and `InstaPayPaymentModel`
- **QR code integration**: `generate_qr`, `save_qr`, `qr_as_bytes`, `qr_as_base64`, `qr_as_svg_string` (requires `segno`)
- **Django integration**: `InstaPayLinkField` ORM model field and `InstaPayHandleFormField` form field
- **CLI**: `instapay parse`, `instapay audit`, `instapay build` commands
- **100% test coverage** enforced in CI
- **MkDocs Material** documentation site
- **Trusted Publishing** CI/CD to PyPI via GitHub Actions

[Unreleased]: https://github.com/MohamedMostafa259/instapay-eg/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/MohamedMostafa259/instapay-eg/releases/tag/v0.1.0

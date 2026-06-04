"""Command-line interface for instapay-eg.

Provides sub-commands:

``instapay parse "<text>"``
    Extract, validate, and display data from share-sheet text.

``instapay audit "<url>"``
    Run a full security audit and display a detailed report.
"""

from __future__ import annotations

import argparse
import sys
from importlib.metadata import version

from .core import parse_text
from .exceptions import InstaPayError
from .security import audit_link


def _cmd_parse(args: argparse.Namespace) -> int:
    """Handle the ``parse`` sub-command."""
    try:
        data = parse_text(args.text)
    except InstaPayError as exc:
        print(f"\n⚠️  Error: {exc}", file=sys.stderr)
        return 1

    safe_icon = "✅ Yes" if data.is_verified else "❌ No"
    print(f"""
┌─────────────────────────────────────────┐
│         InstaPay Link Parser            │
├─────────────────────────────────────────┤
  Link:    {data.link}
  Handle:  {data.handle}
  Format:  {data.formatted_handle}
  Token:   {data.raw_url_id}
  Safe:    {safe_icon}
└─────────────────────────────────────────┘""")
    return 0


def _cmd_audit(args: argparse.Namespace) -> int:
    """Handle the ``audit`` sub-command."""

    report = audit_link(args.url)

    def icon(value: bool, invert: bool = False) -> str:
        ok = not value if invert else value
        return "✅" if ok else "❌"

    status = "✅ SAFE" if report.is_safe else "❌ UNSAFE - DO NOT USE"
    print(f"""
┌─────────────────────────────────────────┐
│         InstaPay Security Audit         │
├─────────────────────────────────────────┤
  URL:        {report.url}
  Status:     {status}
  ─────────────────────────────────────
  HTTPS:      {icon(report.scheme_valid)} {"Valid" if report.scheme_valid else "Must be https"}
  Domain:     {icon(report.domain_valid)} {"ipn.eg ✓" if report.domain_valid else "Expected ipn.eg, got something else"}
  Injection:  {icon(report.has_injection, invert=True)} {"None detected" if not report.has_injection else "PAYLOAD DETECTED"}
  Phishing:   {icon(report.phishing_risk, invert=True)} {"No pattern match" if not report.phishing_risk else "LOOKALIKE DOMAIN DETECTED"}""")  # noqa: E501

    if report.failure_reason:
        print("  ─────────────────────────────────────")
        print(f"  Reason:     {report.failure_reason}")

    print("└─────────────────────────────────────────┘")
    return 0 if report.is_safe else 1


def _build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser."""
    parser = argparse.ArgumentParser(
        prog="instapay",
        description=(
            "instapay-eg - Community SDK for Egyptian InstaPay links.\n"
            "Parse and audit https://ipn.eg payment links from the command line."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {_get_version()}",
    )

    sub = parser.add_subparsers(dest="command", metavar="COMMAND")
    sub.required = True

    # parse
    parse_cmd = sub.add_parser(
        "parse",
        help="Extract and validate data from raw InstaPay share-sheet text.",
        description=(
            "Parses raw text (e.g., copied from the InstaPay app) and displays\n"
            "the extracted link, handle, and security status."
        ),
    )
    parse_cmd.add_argument(
        "text",
        help=(
            'The raw text to parse, e.g. "https://ipn.eg/S/alice/instapay/ABC123 '
            'Click the link to send money to alice@instapay"'
        ),
    )
    parse_cmd.set_defaults(func=_cmd_parse)

    # audit
    audit_cmd = sub.add_parser(
        "audit",
        help="Run a full security audit on a URL.",
        description=(
            "Performs a detailed security check on a URL and reports whether\n"
            "it is a legitimate InstaPay link."
        ),
    )
    audit_cmd.add_argument("url", help="The URL to audit.")
    audit_cmd.set_defaults(func=_cmd_audit)

    return parser


def _get_version() -> str:
    """Return the package version without crashing if metadata is missing."""
    try:
        return version("instapay-eg")
    except Exception:  # pragma: no cover
        return "unknown"


def main() -> None:
    """Entry point for the ``instapay`` CLI command."""
    # reconfigure is not available on StringIO (used in tests) or some envs.
    if hasattr(sys.stdout, "reconfigure"):  # pragma: no branch
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # ty:ignore[call-non-callable]

    if hasattr(sys.stderr, "reconfigure"):  # pragma: no branch
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # ty:ignore[call-non-callable]

    parser = _build_parser()
    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":  # pragma: no cover
    main()

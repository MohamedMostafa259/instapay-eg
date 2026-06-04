"""Tests for instapay_eg.cli - command-line interface.

Uses direct calls to main() with patched sys.argv and capsys for output
capture, so the coverage tool sees the CLI code (subprocess calls do not
contribute to coverage).
"""

import pytest

from instapay_eg.cli import main

from .conftest import PHISHING_LINK_SUBDOMAIN, VALID_HANDLE, VALID_LINK, VALID_TEXT


def _run(capsys, *args: str) -> tuple[int, str, str]:
    """Call main() with patched argv; return (exit_code, stdout, stderr)."""
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr("sys.argv", ["instapay", *args])
        with pytest.raises(SystemExit) as exc_info:
            main()
    exit_code = int(exc_info.value.code) if exc_info.value.code is not None else 0
    stdout, stderr = capsys.readouterr()
    return exit_code, stdout, stderr


class TestCliParse:
    def test_parse_valid_text(self, capsys) -> None:
        code, out, _ = _run(capsys, "parse", VALID_TEXT)
        assert code == 0
        assert VALID_LINK in out
        assert VALID_HANDLE in out
        assert f"{VALID_HANDLE}@instapay" in out
        assert "Yes" in out

    def test_parse_no_link(self, capsys) -> None:
        code, _, err = _run(capsys, "parse", "This text has no link.")
        assert code != 0
        assert "Error" in err

    def test_parse_phishing_link_exits_nonzero(self, capsys) -> None:
        code, _, _ = _run(capsys, "parse", PHISHING_LINK_SUBDOMAIN)
        assert code != 0


class TestCliAudit:
    def test_audit_valid_link(self, capsys) -> None:
        code, out, _ = _run(capsys, "audit", VALID_LINK)
        assert code == 0
        assert "SAFE" in out
        assert "Domain" in out

    def test_audit_phishing_link(self, capsys) -> None:
        code, out, _ = _run(capsys, "audit", PHISHING_LINK_SUBDOMAIN)
        assert code != 0
        assert "UNSAFE" in out


class TestCliVersion:
    def test_version_flag(self, capsys) -> None:
        code, out, _ = _run(capsys, "--version")
        assert code == 0
        assert any(char.isdigit() for char in out)

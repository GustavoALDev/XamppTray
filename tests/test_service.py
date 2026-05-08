import subprocess
from unittest.mock import MagicMock, patch

import pytest

from xampp_tray.service import XamppService


@pytest.fixture
def svc() -> XamppService:
    return XamppService("/opt/lampp/lampp")


def _ok(stdout: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess([], returncode=0, stdout=stdout, stderr="")


def _fail(stderr: str = "permission denied") -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess([], returncode=1, stdout="", stderr=stderr)


def test_start_calls_sudo(svc: XamppService) -> None:
    with patch("subprocess.run", return_value=_ok("XAMPP started.")) as mock_run:
        result = svc.start()
    mock_run.assert_called_once()
    cmd = mock_run.call_args[0][0]
    assert cmd == ["/usr/bin/sudo", "/opt/lampp/lampp", "start"]
    assert "XAMPP started." in result


def test_stop_calls_sudo(svc: XamppService) -> None:
    with patch("subprocess.run", return_value=_ok("XAMPP stopped.")) as mock_run:
        result = svc.stop()
    cmd = mock_run.call_args[0][0]
    assert cmd == ["/usr/bin/sudo", "/opt/lampp/lampp", "stop"]


def test_restart_calls_sudo(svc: XamppService) -> None:
    with patch("subprocess.run", return_value=_ok()) as mock_run:
        svc.restart()
    cmd = mock_run.call_args[0][0]
    assert cmd == ["/usr/bin/sudo", "/opt/lampp/lampp", "restart"]


def test_status_uses_noninteractive_sudo(svc: XamppService) -> None:
    with patch("subprocess.run", return_value=_ok("Apache is running.")) as mock_run:
        svc.status(silent=True)
    cmd = mock_run.call_args[0][0]
    assert "-n" in cmd
    assert cmd == ["/usr/bin/sudo", "-n", "/opt/lampp/lampp", "status"]


def test_fallback_to_pkexec_on_sudo_failure(svc: XamppService) -> None:
    calls = [_fail(), _ok("started via pkexec")]
    with patch("subprocess.run", side_effect=calls) as mock_run:
        result = svc.start()
    assert mock_run.call_count == 2
    pkexec_cmd = mock_run.call_args_list[1][0][0]
    assert pkexec_cmd[0] == "/usr/bin/pkexec"
    assert "started via pkexec" in result


def test_no_shell_true_in_any_call(svc: XamppService) -> None:
    with patch("subprocess.run", return_value=_ok()) as mock_run:
        svc.start()
    call_kwargs = mock_run.call_args[1]
    assert call_kwargs.get("shell") is not True

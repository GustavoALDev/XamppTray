from xampp_tray.service import ServiceState, XamppService


def make_service() -> XamppService:
    return XamppService("/opt/lampp/lampp")


def test_parse_both_running(lampp_output_running: str) -> None:
    svc = make_service()
    status = svc.parse_status(lampp_output_running)
    assert status.apache == ServiceState.RUNNING
    assert status.mysql == ServiceState.RUNNING


def test_parse_both_stopped(lampp_output_stopped: str) -> None:
    svc = make_service()
    status = svc.parse_status(lampp_output_stopped)
    assert status.apache == ServiceState.STOPPED
    assert status.mysql == ServiceState.STOPPED


def test_parse_mixed(lampp_output_mixed: str) -> None:
    svc = make_service()
    status = svc.parse_status(lampp_output_mixed)
    assert status.apache == ServiceState.RUNNING
    assert status.mysql == ServiceState.STOPPED


def test_parse_empty_output() -> None:
    svc = make_service()
    status = svc.parse_status("")
    assert status.apache == ServiceState.STOPPED
    assert status.mysql == ServiceState.STOPPED


def test_parse_case_insensitive() -> None:
    svc = make_service()
    status = svc.parse_status("APACHE IS RUNNING.\nMYSQL IS RUNNING.")
    assert status.apache == ServiceState.RUNNING
    assert status.mysql == ServiceState.RUNNING

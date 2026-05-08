import pytest


@pytest.fixture
def lampp_output_running() -> str:
    return (
        "XAMPP: Starting Apache...already running.\n"
        "XAMPP: Starting MySQL...already running.\n"
        "Apache is running.\n"
        "MySQL is running.\n"
    )


@pytest.fixture
def lampp_output_stopped() -> str:
    return (
        "Apache is not running.\n"
        "MySQL is not running.\n"
    )


@pytest.fixture
def lampp_output_mixed() -> str:
    return (
        "Apache is running.\n"
        "MySQL is not running.\n"
    )

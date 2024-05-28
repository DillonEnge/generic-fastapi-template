from data_api.core import hooks


def test_log_exc_in_test() -> None:
    """Run the log_exc hook."""

    hooks.log_exc(None, ValueError("testing"))

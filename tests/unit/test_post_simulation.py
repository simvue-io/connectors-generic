import threading
from unittest.mock import Mock

import pytest

from simvue_connector.connector import WrappedRun


@pytest.fixture
def wrapped_run() -> WrappedRun:
    run = object.__new__(WrappedRun)
    run._alert_raised_trigger = threading.Event()
    run._failed = False
    run._terminated = False
    run._term_color = False
    run._executor = Mock()
    run.log_event = Mock()
    return run


@pytest.mark.parametrize(
    ("failed", "executor_success", "error_summary", "expected_event"),
    (
        (True, True, {}, "Simulation Failed!"),
        (False, False, {"simulation": "process exited non-zero"}, "Simulation Failed!"),
        (False, True, {}, "Simulation Complete!"),
        (
            False,
            False,
            {},
            "Simulation monitoring ended before all process outcomes were known.",
        ),
    ),
    ids=("connector-failure", "executor-failure", "success", "unresolved-process"),
)
def test_post_simulation_logs_outcome(
    wrapped_run: WrappedRun,
    failed: bool,
    executor_success: bool,
    error_summary: dict[str, str],
    expected_event: str,
) -> None:
    wrapped_run._failed = failed
    wrapped_run._executor.success = executor_success
    wrapped_run._executor.get_error_summary.return_value = error_summary

    wrapped_run._post_simulation()

    wrapped_run.log_event.assert_called_once_with(expected_event)
    assert wrapped_run._terminated is False


def test_post_simulation_prioritizes_alert(wrapped_run: WrappedRun) -> None:
    wrapped_run._alert_raised_trigger.set()
    wrapped_run._failed = True
    wrapped_run._executor.success = False
    wrapped_run._executor.get_error_summary.return_value = {
        "simulation": "process exited non-zero"
    }

    wrapped_run._post_simulation()

    wrapped_run.log_event.assert_called_once_with(
        "Simulation aborted due to an alert being triggered."
    )
    assert wrapped_run._terminated is True
    wrapped_run._executor.get_error_summary.assert_not_called()

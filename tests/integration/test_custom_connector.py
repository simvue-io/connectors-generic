import os
from examples.custom_connector_example import TemperatureRun
import pytest
import pathlib
import tempfile
import time
import simvue
import typing
import shutil
import subprocess
from simvue.sender import Sender


def run_connector_example(
    offline: bool, method: typing.Literal["launch", "load", "watch"]
) -> str | None:

    with tempfile.TemporaryDirectory() as tempd:
        script_path = pathlib.Path(tempd).joinpath("temperatures.sh")
        shutil.copy(
            pathlib.Path(__file__).parent.joinpath("example_data", "temperatures.sh"),
            script_path,
        )

        # Use our custom connector class
        with TemperatureRun(mode="offline" if offline else "online") as run:
            # Initialize the run as normal
            run.init(
                name=f"custom-connector-tests-{method}-{'offline' if offline else 'online'}",
                folder="/test-generic",
                description="Simulate an experiment where a sample is heated and then left to cool, tracking the temperature.",
                tags=["example", "heating-cooling"],
                retention_period="1 hour",
            )
            _ = run.config(disable_resources_metrics=True)

            # Can upload extra things we care about, eg could upload some metadata
            run.update_metadata(
                {"initial_temperature": 20, "heating_time": 50, "cooling_time": 100}
            )
            if method == "launch":
                run.launch(script_path)
            elif method == "load":
                shutil.copy(
                    pathlib.Path(__file__).parent.joinpath(
                        "example_data", "temperatures.csv"
                    ),
                    pathlib.Path(tempd).joinpath("temperatures.csv"),
                )
                run.load(pathlib.Path(tempd))
            else:
                process = subprocess.Popen(["bash", str(script_path)])
                run.watch(process.pid, pathlib.Path(tempd))
                process.wait()  # reap the child process so it doesn't linger as a zombie

        # Upload after the run has been closed, so that the final status
        # (e.g. "completed") is included in the upload
        if offline:
            sender = Sender(throw_exceptions=True)
            sender.upload()
            run_id = sender._id_mapping.get(run.id)
        else:
            run_id = run.id

        return run_id


@pytest.mark.parametrize("offline", (True, False), ids=("offline", "online"))
@pytest.mark.parametrize(
    "method", ("launch", "watch", "load"), ids=("launch", "watch", "load")
)
def test_custom_connector(offline, method, set_offline_directory):

    run_id = run_connector_example(offline=offline, method=method)

    assert run_id, "Failed to retrieve Run ID from custom example"

    time.sleep(1)
    client = simvue.Client()
    run_data = client.get_run(run_id)
    events = [event["message"] for event in client.get_events(run_id)]

    assert "Starting connector..." in events

    assert (
        run_data.description
        == "Simulate an experiment where a sample is heated and then left to cool, tracking the temperature."
    )
    assert sorted(run_data.tags) == sorted(["example", "heating-cooling"])

    if method == "launch":
        # Only `launch` adds a process to the executor, so only it creates
        # the exit status alert
        assert "heating_experiment_exit_status" in [
            alert["name"] for alert in run_data.get_alert_details()
        ]

    assert run_data.metadata["initial_temperature"] == 20

    assert "Simulation Complete!" in events

    metrics = dict(run_data.metrics)
    assert metrics["sample_temperature"]["count"] == 31

    temp_dir = tempfile.TemporaryDirectory()

    if method == "launch":
        client.get_artifacts_as_files(
            run_id=run_id, category="code", output_dir=temp_dir.name
        )
        assert pathlib.Path(temp_dir.name).joinpath("temperatures.sh").exists()

    client.get_artifacts_as_files(
        run_id=run_id, category="output", output_dir=temp_dir.name
    )
    assert pathlib.Path(temp_dir.name).joinpath("temperatures.csv").exists()

    assert run_data.status == "completed"

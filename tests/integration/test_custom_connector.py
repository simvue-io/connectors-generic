from examples.custom_connector_example import custom_connector_example
import pytest
import subprocess
import pathlib
import tempfile
import simvue
from simvue.sender import sender

@pytest.mark.parametrize("offline", (True, False), ids=("offline", "online"))
def test_custom_connector(offline):

    run_id = custom_connector_example(ci=True, offline=offline)

    if offline:
        _id_mapping = sender()
        run_id = _id_mapping.get(run_id)
    
    client = simvue.Client()
    run_data = client.get_run(run_id)
    events = [event["message"] for event in client.get_events(run_id)]
    
    assert run_data.description == "Simulate an experiment where a sample is heated and then left to cool, tracking the temperature."
    assert run_data.tags == ["example", "heating-cooling"]
    
    assert "xyzxyzxyz" in [alert["name"] for alert in run_data.get_alert_details()]
    
    assert run_data.metadata["initial_temperature"] == 20
    
    assert "Simulation Complete!" in events
    
    metrics = dict(run_data.metrics)
    assert metrics["sample_temperature"]["count"] == 31
    assert metrics["sample_temperature"]["first"] == 20
    assert metrics["sample_temperature"]["last"] == 38.394

    temp_dir = tempfile.TemporaryDirectory()
    
    client.get_artifacts_as_files(run_id, "input", temp_dir.name)
    assert pathlib.Path(temp_dir.name).joinpath("temperatures.sh").exists()
    
    client.get_artifacts_as_files(run_id, "output", temp_dir.name)
    assert pathlib.Path(temp_dir.name).joinpath("temperatures.csv").exists()
    
    assert run_data.status == "completed"

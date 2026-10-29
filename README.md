# Simvue Integrations - Connectors Template

<br/>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/simvue-io/.github/blob/5eb8cfd2edd3269259eccd508029f269d993282f/simvue-white.png" />
    <source media="(prefers-color-scheme: light)" srcset="https://github.com/simvue-io/.github/blob/5eb8cfd2edd3269259eccd508029f269d993282f/simvue-black.png" />
    <img alt="Simvue" src="https://github.com/simvue-io/.github/blob/5eb8cfd2edd3269259eccd508029f269d993282f/simvue-black.png" width="500">
  </picture>
</p>

<p align="center">
A template which all new Connectors (integrations which provide Simvue tracking for Non-Python software) should inherit from.

</p>

<div align="center">
<a href="https://github.com/simvue-io/client/blob/main/LICENSE" target="_blank"><img src="https://img.shields.io/github/license/simvue-io/client"/></a>
<img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue">
</div>

<h3 align="center">
 <a href="https://simvue.io"><b>Website</b></a>
  •
  <a href="https://docs.simvue.io"><b>Documentation</b></a>
</h3>

## Implementation

A customised `WrappedRun` class has been created which has the following methods:

### Pre Simulation

The `_pre_simulation` method is called when the `launch()` or `watch()` methods are called, but before the file monitor is started. This means that it should include:

- Upload of any input or code files
- Adding any tags or metadata which are present before the simulation begins
- Creating alerts
- Logging events messages required before the simulation begins

Because this class inherits from the base Simvue Run class, all methods associated with that are available through self.

You should also call the functionality from the WrappedRun class **at the top of your method** using `super()._pre_simulation()` - this creates a trigger which can be used to abort the file monitor, and checks that a simvue Run has been initialized before the launch method was called.

### Start Simulation
The `_start_simulation()` method is called when the `launch()` method is called, before the file monitor is started. This function should be responsible for generating the command required to run the simulation from the inputs the user provides to `launch()`, as well as starting the simulation using `self.add_process()`.

### During Simulation

The `_during_simulation` method is called when the `launch()` or `watch()` methods are called, and within the self.file_monitor context manager. This is an instance of the FileMonitor class from multiparser, which monitors any files which you wish to track. You should include all of your multiparser code inside this method, eg:

- Calls to the .track() method, detailing a file to read and the methods or functions used to process and upload data from it
- Calls to the .tail() method, detailing a file to read line by line as it is written and the methods or functions used to process and upload data from it

### Post Simulation

The `_post_simulation` method is called when the `launch()` or `watch` methods are called, but after the file monitor is finished. This means that it should include:

- Upload of any output files
- Adding any tags or metadata which are generated after the simulation finishes
- Logging events messages required after the simulation finishes

Because this class inherits from the base Simvue Run class, all methods associated with that are available through self. You should also call the functionality from the WrappedRun class **at the bottom of your method** using `super()._post_simulation()` - this adds support for soft aborts of simulation, and termination of simulations with alerts.

### Launch

The `launch` method is the overall method which starts the simulation & the file monitor, and calls the four methods above. This should be overriden to require the user to provide any inputs relevant to running the simulation, for example the path to an executable, the path of an input file, and/or the path of an output directory.

Once you have created your set of required parameters, make sure to call the parent launch method: `super().launch()`.

### Watch
The `watch` method is designed for the case where the user may want to launch their simulation outside of Simvue and just use the connector for tracking generated results (eg, if they have a complex workflow or orchestration tool which they wish to use to launch the simulation). This calls the same methods as `launch()` but without `_start_simulation()`. This should be overriden to require the user to provide any inputs required to monitor the simulation, for example the path of an input file and the path of an output directory, as well as the Process ID (PID) of the simulation for resource tracking & completion detection.

### Load

The `load` method should allow you to load a set of results from the simulation which have already been run into the Simvue server. This should reuse as many of the other methods already defined as possible, such as the callback and/or parser functions, but note that it will not launch the file monitor.

## Installation

To install and use this connector, first create a virtual environment:

```
python -m venv venv
```

Then activate it:

```
source venv/bin/activate
```

And then use pip to install this module:

```
pip install simvue-connector
```

## Configuration

The service URL and token can be defined as environment variables:

```sh
export SIMVUE_URL=...
export SIMVUE_TOKEN=...
```

or a file `simvue.toml` can be created containing:

```toml
[server]
url = "..."
token = "..."
```

The exact contents of both of the above options can be obtained directly by clicking the **Create new run** button on the web UI. Note that the environment variables have preference over the config file.

## Usage example

```python
from simvue_connector.connector import WrappedRun
import multiparser.parsing.tail as mp_tail_parser

# Create a new class which inherits from WrappedRun
class TemperatureRun(WrappedRun):
    script_path: pathlib.Path | None = None
    results_dir: pathlib.Path | None = None

    # Override the `_pre_simulation` method to launch the process
    @override
    def _pre_simulation(self):
        # Call the base method first
        super()._pre_simulation()

        # Do something which should always happen
        self.log_event("Starting connector...")

    # Override the `_start_simulation` method to begin the simulation
    def _start_simulation(self):
        if not self.script_path:
            raise RuntimeError("Expected script path to be provided.")

        # Add a process to the run using `add_process`
        self.add_process(
            identifier="heating_experiment",
            executable="bash",
            script=self.script_path,
            completion_trigger=self._trigger,  # Sets a threading Event once the simulation is completed
        )

    # Override the `_during_simulation` method to track the temperature data
    @override
    def _during_simulation(self) -> None:
        # Use the `tail` method of the Multiparser `FileMonitor` object to track file, line by line
        self.file_monitor.tail(
            path_glob_exprs=str(self.results_dir.joinpath("temperatures.csv")),
            parser_func=mp_tail_parser.record_csv,  # Use the built-in CSV parser
            callback=lambda csv_data, metadata: (
                self.log_metrics(  # Use data from those two dictionaries to log a metric:
                    {"sample_temperature": csv_data["Temperature"]},
                    time=csv_data["Time"],
                    step=csv_data["Step"],
                )
            ),
        )

    # Override the `_post_simulation` method to upload the final CSV file of temperature data
    @override
    def _post_simulation(self) -> None:

        self.save_file(self.results_dir.joinpath("temperatures.csv"), category="output")
        # And finally call the base method
        super()._post_simulation()

    # Override the `launch` method to accept the path to the bash script
    @override
    def launch(self, script_path: pathlib.Path) -> None:
        self.script_path = script_path
        self.results_dir = script_path.parent
        # Call the base `launch` method to call the above methods in the correct order
        super().launch()

    # Override the `watch` method to accept a directory where results will be created and a PID
    @override
    def watch(self, pid: int, results_dir: pathlib.Path) -> None:
        self.results_dir = results_dir
        # Call the base `watch` method to call the above methods in the correct order
        super().watch(pid)

    @override
    def load(self, results_dir: pathlib.Path) -> None:
        self.results_dir = results_dir
        csv_path = results_dir.joinpath("temperatures.csv")

        if not csv_path.exists():
            raise FileNotFoundError(
                "Could not find CSV file in provided results directory!"
            )

        # Call any existing methods which can be reused
        self._pre_simulation()

        # Parse existing files (replicate FileMonitor logic, reusing parser methods where possible)
        with csv_path.open(newline="") as f:
            for csv_data in csv.DictReader(f):
                self.log_metrics(
                    {"sample_temperature": csv_data["Temperature"]},
                    time=csv_data["Time"],
                    step=csv_data["Step"],
                )

        self._post_simulation()
```

## License

Released under the terms of the [Apache 2](https://github.com/simvue-io/client/blob/main/LICENSE) license.

## Citation

To reference Simvue, please use the information outlined in this [citation file](https://github.com/simvue-io/python-api/blob/dev/CITATION.cff).

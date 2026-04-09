# Change Log

## [v1.1.1](https://github.com/simvue-io/connectors-generic/releases/tag/v1.1.1) - 2026-04-09

- Include extra parameter `server_profiles` in __init__ method

## [v1.1.0](https://github.com/simvue-io/connectors-generic/releases/tag/v1.1.0) - 2026-04-07

- Changed to using threading.Event instead of multiprocessing.Event for termination trigger
- Added load method to Connector class

## [v1.0.1](https://github.com/simvue-io/connectors-generic/releases/tag/v1.0.1) - 2026-03-31

- Added support for Python3.14

## [v1.0.0a1](https://github.com/simvue-io/connectors-generic/releases/tag/v1.0.0) - 2025-03-07

- Initial release of generic connector class. Wraps around Simvue Run, giving a uniform way to build connectors to Non-Python softwares.

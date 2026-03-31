from collections.abc import Generator
import tempfile
import pytest


@pytest.fixture(autouse=True)
def set_offline_directory(monkeypatch: pytest.MonkeyPatch) -> Generator[str]:
    with tempfile.TemporaryDirectory() as tempd:
        monkeypatch.setenv("SIMVUE_OFFLINE_DIRECTORY", tempd)
        yield tempd

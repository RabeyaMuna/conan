import pathlib

import pytest

from test import conftest


def test_tool_detection_falls_back_to_path_when_configured_path_missing(monkeypatch):
    monkeypatch.setattr(conftest.platform, "system", lambda: "Linux")
    monkeypatch.setattr(conftest, "tools_locations", {
        "cmake": {
            "default": "3.15",
            "3.15": {
                "path": {"Linux": "/does/not/exist"}
            }
        }
    })
    monkeypatch.setattr(conftest, "tools_environments", {})
    monkeypatch.setattr(conftest.os.path, "isdir", lambda path: False)
    monkeypatch.setattr(conftest, "which", lambda exe: "/usr/bin/cmake")

    result = conftest._get_individual_tool("cmake", "3.15")

    assert result == (str(pathlib.Path("/usr/bin")), None)

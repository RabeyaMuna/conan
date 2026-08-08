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


def test_tool_detection_returns_false_when_tool_missing(monkeypatch):
    monkeypatch.setattr(conftest.platform, "system", lambda: "Linux")
    monkeypatch.setattr(conftest, "tools_locations", {
        "premake": {
            "default": "5.0.0",
            "5.0.0": {
                "path": {"Linux": "/does/not/exist"}
            }
        }
    })
    monkeypatch.setattr(conftest, "tools_environments", {})
    monkeypatch.setattr(conftest.os.path, "isdir", lambda path: False)
    monkeypatch.setattr(conftest, "which", lambda exe: None)

    result = conftest._get_individual_tool("premake", "5.0.0")

    assert result is False


def test_tool_detection_applies_version_environment_on_path_fallback(monkeypatch):
    monkeypatch.setattr(conftest.platform, "system", lambda: "Linux")
    monkeypatch.setattr(conftest, "tools_locations", {
        "bazel": {
            "default": "6.5.0",
            "6.5.0": {
                "path": {"Linux": "/does/not/exist"},
                "env": {"USE_BAZEL_VERSION": "6.5.0"},
            }
        }
    })
    monkeypatch.setattr(conftest, "tools_environments", {})
    monkeypatch.setattr(conftest.os.path, "isdir", lambda path: False)
    monkeypatch.setattr(conftest, "which", lambda exe: "/usr/bin/bazel")

    result = conftest._get_individual_tool("bazel", "6.5.0")
    default_result = conftest._get_individual_tool("bazel", None)

    assert result == (str(pathlib.Path("/usr/bin")), {"USE_BAZEL_VERSION": "6.5.0"})
    assert default_result == result

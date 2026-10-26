import platform

from test import conftest


def test_get_individual_tool_skips_missing_configured_path(monkeypatch, tmp_path):
    tool_name = "missing_configured_tool"
    monkeypatch.setitem(conftest.tools_locations, tool_name, {
        "default": "1.0",
        "exe": "missing-configured-tool",
        "1.0": {"path": {platform.system(): str(tmp_path / "missing")}}
    })

    assert conftest._get_individual_tool(tool_name, None) is False


def test_get_individual_tool_skips_missing_pathless_tool(monkeypatch, tmp_path):
    tool_name = "missing_pathless_tool"
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setitem(conftest.tools_locations, tool_name, {
        "exe": "missing-pathless-tool"
    })

    assert conftest._get_individual_tool(tool_name, None) is False


def test_get_individual_tool_fails_unknown_configured_version(monkeypatch):
    tool_name = "configured_tool"
    monkeypatch.setitem(conftest.tools_locations, tool_name, {
        "default": "1.0",
        "1.0": {}
    })

    assert conftest._get_individual_tool(tool_name, "2.0") is True

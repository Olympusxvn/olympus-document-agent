import pytest

pytest.importorskip("google.adk")

from vat_agent.agent import root_agent


def test_adk_agent_has_no_write_tools():
    tools = getattr(root_agent, "tools", None) or []
    assert list(tools) == []

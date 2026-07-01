from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def test_add_numbers_tool(main_module):
    assert main_module.add_numbers.invoke({"a": 2, "b": 3}) == 5


def test_model_id_is_configured(model_module):
    assert model_module.MODEL_ID == "gpt-5-mini"


@pytest.mark.asyncio
async def test_invoke_returns_agent_response(main_module):
    mock_graph = MagicMock()
    mock_configured_graph = MagicMock()
    mock_configured_graph.ainvoke = AsyncMock(
        return_value={"messages": [MagicMock(content="Agentic AI coordinates specialized agents.")]}
    )
    mock_graph.with_config.return_value = mock_configured_graph
    main_module.mcp_client.get_tools = AsyncMock(return_value=[])

    with patch.object(main_module, "_create_react_agent", return_value=mock_graph):
        result = await main_module.invoke({"prompt": "What is Agentic AI?"})

    assert result == {"result": "Agentic AI coordinates specialized agents."}


def test_dependencies_import():
    import bedrock_agentcore
    import langchain
    import splunk_otel

    assert bedrock_agentcore.__name__ == "bedrock_agentcore"
    assert langchain.__name__ == "langchain"
    assert splunk_otel.__name__ == "splunk_otel"

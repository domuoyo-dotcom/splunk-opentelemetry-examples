from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from market_research_agent import MarketResearchAgent
from message import Message


@pytest.mark.asyncio
@patch("market_research_agent._get_fetcher", return_value=[])
@patch("market_research_agent.AssistantAgent")
@patch("market_research_agent.OpenAIChatCompletionClient")
async def test_handle_message_returns_delegate_response(
    mock_client_cls, mock_assistant_cls, mock_get_fetcher
):
    mock_delegate = AsyncMock()
    mock_response = MagicMock()
    mock_response.chat_message.content = "The market looks promising."
    mock_delegate.on_messages = AsyncMock(return_value=mock_response)
    mock_assistant_cls.return_value = mock_delegate

    agent = MarketResearchAgent("market_research_agent")
    context = MagicMock()
    context.cancellation_token = MagicMock()

    result = await agent.handle_message(Message(content="Research this idea"), context)

    assert result.content == "The market looks promising."
    mock_get_fetcher.assert_called_once()
    mock_delegate.on_messages.assert_awaited_once()

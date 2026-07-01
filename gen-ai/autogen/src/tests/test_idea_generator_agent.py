from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from idea_generator_agent import IdeaGeneratorAgent
from message import Message


@pytest.mark.asyncio
@patch("idea_generator_agent.AssistantAgent")
@patch("idea_generator_agent.OpenAIChatCompletionClient")
async def test_handle_message_returns_delegate_response(mock_client_cls, mock_assistant_cls):
    mock_delegate = AsyncMock()
    mock_response = MagicMock()
    mock_response.chat_message.content = "A subscription box for houseplants"
    mock_delegate.on_messages = AsyncMock(return_value=mock_response)
    mock_assistant_cls.return_value = mock_delegate

    agent = IdeaGeneratorAgent("idea_generator_agent")
    context = MagicMock()
    context.cancellation_token = MagicMock()

    result = await agent.handle_message(Message(content="Go!"), context)

    assert result.content == "A subscription box for houseplants"
    mock_delegate.on_messages.assert_awaited_once()
    mock_client_cls.assert_called_once_with(model="gpt-4o-mini")

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from evaluator_agent import (
    EVALUATION_INSTRUCTIONS,
    IDEA_GENERATOR_INSTRUCTIONS,
    MARKET_RESEARCH_INSTRUCTIONS,
    EvaluatorAgent,
)
from message import Message


def test_instruction_constants_are_defined():
    assert "startup" in IDEA_GENERATOR_INSTRUCTIONS.lower()
    assert "market" in MARKET_RESEARCH_INSTRUCTIONS.lower()
    assert "decision" in EVALUATION_INSTRUCTIONS.lower()


@pytest.mark.asyncio
@patch("evaluator_agent.AssistantAgent")
@patch("evaluator_agent.OpenAIChatCompletionClient")
async def test_handle_message_orchestrates_agents(mock_client_cls, mock_assistant_cls):
    mock_delegate = AsyncMock()
    mock_response = MagicMock()
    mock_response.chat_message.content = "Proceed with the idea."
    mock_delegate.on_messages = AsyncMock(return_value=mock_response)
    mock_assistant_cls.return_value = mock_delegate

    agent = EvaluatorAgent("evaluator_agent")
    agent.send_message = AsyncMock(
        side_effect=[
            Message(content="Eco-friendly lunch containers"),
            Message(content="Strong demand with moderate competition."),
        ]
    )

    context = MagicMock()
    context.cancellation_token = MagicMock()

    result = await agent.handle_message(Message(content="Go!"), context)

    assert "Eco-friendly lunch containers" in result.content
    assert "Strong demand with moderate competition." in result.content
    assert "Proceed with the idea." in result.content
    assert agent.send_message.await_count == 2
    mock_delegate.on_messages.assert_awaited_once()

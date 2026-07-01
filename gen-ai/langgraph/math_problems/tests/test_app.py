from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from langchain_core.messages import AIMessage

from app import MathQuestion, MathProblems


def test_math_question_model():
    question = MathQuestion(
        mathematics_branch="algebra",
        rationale="Practice solving equations",
        question="Solve for x: 2x + 4 = 10",
    )

    assert question.mathematics_branch == "algebra"
    assert "Solve for x" in question.question


@pytest.mark.asyncio
async def test_create_llm_sets_agent_metadata():
    math_problems = MathProblems()

    with patch("app.ChatOpenAI") as mock_chat_openai:
        mock_chat_openai.return_value = MagicMock()
        await math_problems._create_llm("teacher_agent", temperature=0.7, session_id="session-1")

    call_kwargs = mock_chat_openai.call_args.kwargs
    assert call_kwargs["model"] == "gpt-4o-mini"
    assert call_kwargs["metadata"]["agent_name"] == "teacher_agent"
    assert call_kwargs["metadata"]["session_id"] == "session-1"


@pytest.mark.asyncio
async def test_teacher_node_returns_question():
    math_problems = MathProblems()
    math_problems.teacher_agent = MagicMock()
    math_problems.teacher_agent.ainvoke = AsyncMock(
        return_value={"messages": [AIMessage(content="raw teacher output")]}
    )
    math_problems.teacher_llm_with_output = MagicMock()
    math_problems.teacher_llm_with_output.ainvoke = AsyncMock(
        return_value=MathQuestion(
            mathematics_branch="geometry",
            rationale="Triangles are foundational",
            question="What is the area of a triangle?",
        )
    )

    result = await math_problems.teacher({"messages": []})

    assert result["question"] == "What is the area of a triangle?"
    assert "triangle" in result["messages"][0]["content"]


def test_dependencies_import():
    import langchain
    import langgraph
    import splunk_otel

    assert langchain.__name__ == "langchain"
    assert langgraph.__name__ == "langgraph"
    assert splunk_otel.__name__ == "splunk_otel"

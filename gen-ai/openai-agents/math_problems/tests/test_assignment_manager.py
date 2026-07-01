from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from assignment_manager import AssignmentManager
from teacher_agent import MathQuestion
from teaching_assistant_agent import AssignmentResult


@pytest.mark.asyncio
@patch("assignment_manager.Runner.run", new_callable=AsyncMock)
async def test_assignment_manager_run(mock_runner):
    question = MathQuestion(
        mathematics_branch="algebra",
        rationale="Practice linear equations",
        question="Solve for x: x + 3 = 7",
    )
    assignment_result = AssignmentResult(
        grade="B+",
        rationale="Correct approach with a minor arithmetic slip.",
    )

    mock_runner.side_effect = [
        MagicMock(final_output_as=MagicMock(return_value=question)),
        MagicMock(final_output="x = 4"),
        MagicMock(final_output_as=MagicMock(return_value=assignment_result)),
    ]

    result = await AssignmentManager().run()

    assert result.grade == "B+"
    assert mock_runner.await_count == 3


@pytest.mark.asyncio
@patch("assignment_manager.Runner.run", new_callable=AsyncMock)
async def test_create_question_uses_teacher_agent(mock_runner):
    question = MathQuestion(
        mathematics_branch="geometry",
        rationale="Area formulas",
        question="Find the area of a rectangle with sides 3 and 5.",
    )
    mock_runner.return_value = MagicMock(final_output_as=MagicMock(return_value=question))

    result = await AssignmentManager().create_question()

    assert result.question.startswith("Find the area")
    mock_runner.assert_awaited_once()


def test_dependencies_import():
    import agents
    import openlit
    import splunk_otel

    assert agents.__name__ == "agents"
    assert openlit.__name__ == "openlit"
    assert splunk_otel.__name__ == "splunk_otel"

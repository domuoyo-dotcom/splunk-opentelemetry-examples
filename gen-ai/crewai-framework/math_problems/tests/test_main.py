import sys
from unittest.mock import MagicMock, patch

sys.modules.setdefault("openlit", MagicMock())


@patch("math_problems.crew.MathProblems")
def test_run_kickoffs_crew_with_grade_input(mock_math_problems):
    import math_problems.main as main_module

    mock_result = MagicMock()
    mock_result.raw = "Assignment complete"
    mock_crew = MagicMock()
    mock_crew.crew.return_value.kickoff.return_value = mock_result
    mock_math_problems.return_value = mock_crew

    main_module.run()

    mock_crew.crew.return_value.kickoff.assert_called_once_with(inputs={"grade": "8"})


def test_dependencies_import():
    import crewai
    import splunk_otel

    assert crewai.__name__ == "crewai"
    assert splunk_otel.__name__ == "splunk_otel"

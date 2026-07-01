from pathlib import Path

import yaml


def test_agent_config_defines_three_roles():
    config_path = Path(__file__).parent.parent / "src/math_problems/config/agents.yaml"
    config = yaml.safe_load(config_path.read_text())

    assert set(config.keys()) == {"teacher", "student", "teaching_assistant"}
    assert all("openai/gpt-4o-mini" in agent["llm"] for agent in config.values())


def test_task_config_defines_three_tasks():
    config_path = Path(__file__).parent.parent / "src/math_problems/config/tasks.yaml"
    config = yaml.safe_load(config_path.read_text())

    assert {
        "create_question_task",
        "answer_question_task",
        "grade_question_task",
    } == set(config.keys())

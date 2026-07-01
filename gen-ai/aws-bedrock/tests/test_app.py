from unittest.mock import MagicMock

from app import build_native_request, format_llama_prompt, invoke_bedrock_model


def test_format_llama_prompt_wraps_user_message():
    prompt = format_llama_prompt("Hello")

    assert "Hello" in prompt
    assert "<|begin_of_text|>" in prompt
    assert "assistant" in prompt


def test_build_native_request_uses_formatted_prompt():
    request = build_native_request("Hello", max_gen_len=128, temperature=0.2)

    assert request["max_gen_len"] == 128
    assert request["temperature"] == 0.2
    assert "Hello" in request["prompt"]


def test_invoke_bedrock_model_returns_generation():
    client = MagicMock()
    body = MagicMock()
    body.read.return_value = b'{"generation": "A hello world program prints a greeting."}'
    client.invoke_model.return_value = {"body": body}

    result = invoke_bedrock_model(client, "meta.llama3-1-8b-instruct-v1:0", "Hello")

    assert result == "A hello world program prints a greeting."
    client.invoke_model.assert_called_once()

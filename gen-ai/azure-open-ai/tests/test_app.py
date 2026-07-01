from unittest.mock import MagicMock, patch

from app import ask_about_paris, create_client


def test_create_client_uses_azure_settings():
    with patch("app.AzureOpenAI") as mock_azure_openai:
        create_client(endpoint="https://example.openai.azure.com", api_key="test-key")

    mock_azure_openai.assert_called_once_with(
        api_version="2024-12-01-preview",
        azure_endpoint="https://example.openai.azure.com",
        api_key="test-key",
    )


def test_ask_about_paris_returns_message_content():
    client = MagicMock()
    message = MagicMock()
    message.content = "Visit the Eiffel Tower."
    choice = MagicMock()
    choice.message = message
    client.chat.completions.create.return_value = MagicMock(choices=[choice])

    result = ask_about_paris(client)

    assert result == "Visit the Eiffel Tower."
    client.chat.completions.create.assert_called_once()

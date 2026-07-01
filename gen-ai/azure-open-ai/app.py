import os

from openai import AzureOpenAI
from opentelemetry.instrumentation.openai_v2 import OpenAIInstrumentor

DEFAULT_DEPLOYMENT = "gpt-35-turbo"
DEFAULT_API_VERSION = "2024-12-01-preview"


def create_client(
    *,
    endpoint: str,
    api_key: str,
    api_version: str = DEFAULT_API_VERSION,
) -> AzureOpenAI:
    return AzureOpenAI(
        api_version=api_version,
        azure_endpoint=endpoint,
        api_key=api_key,
    )


def ask_about_paris(client: AzureOpenAI, *, deployment: str = DEFAULT_DEPLOYMENT) -> str:
    response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant.",
            },
            {
                "role": "user",
                "content": "I am going to Paris, what should I see?",
            },
        ],
        max_tokens=4096,
        temperature=1.0,
        top_p=1.0,
        model=deployment,
    )
    return response.choices[0].message.content


def main() -> None:
    OpenAIInstrumentor().instrument()

    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    subscription_key = os.getenv("AZURE_OPENAI_API_KEY")
    client = create_client(endpoint=endpoint, api_key=subscription_key)
    print(ask_about_paris(client, deployment=DEFAULT_DEPLOYMENT))


if __name__ == "__main__":
    main()

import json
import os

import boto3
from botocore.exceptions import ClientError

MODEL_ID = "meta.llama3-1-8b-instruct-v1:0"
DEFAULT_PROMPT = "Describe the purpose of a 'hello world' program in one line."


def format_llama_prompt(prompt: str) -> str:
    return f"""
<|begin_of_text|><|start_header_id|>user<|end_header_id|>
{prompt}
<|eot_id|>
<|start_header_id|>assistant<|end_header_id|>
"""


def build_native_request(
    prompt: str,
    *,
    max_gen_len: int = 512,
    temperature: float = 0.5,
) -> dict:
    return {
        "prompt": format_llama_prompt(prompt),
        "max_gen_len": max_gen_len,
        "temperature": temperature,
    }


def invoke_bedrock_model(client, model_id: str, prompt: str) -> str:
    request = json.dumps(build_native_request(prompt))
    response = client.invoke_model(modelId=model_id, body=request)
    model_response = json.loads(response["body"].read())
    return model_response["generation"]


def main() -> None:
    region = os.getenv("AWS_REGION_NAME")
    client = boto3.client("bedrock-runtime", region_name=region)

    try:
        response_text = invoke_bedrock_model(client, MODEL_ID, DEFAULT_PROMPT)
    except (ClientError, Exception) as error:
        print(f"ERROR: Can't invoke '{MODEL_ID}'. Reason: {error}")
        raise SystemExit(1) from error

    print(response_text)


if __name__ == "__main__":
    main()

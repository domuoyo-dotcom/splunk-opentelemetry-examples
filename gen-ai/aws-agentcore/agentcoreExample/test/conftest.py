import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

SRC = Path(__file__).parent.parent / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


@pytest.fixture
def main_module():
    module_names = [name for name in sys.modules if name == "main" or name.startswith("model")]
    for name in module_names:
        del sys.modules[name]

    mock_mcp_client = MagicMock()
    mock_mcp_client.get_tools = AsyncMock(return_value=[])

    with (
        patch("splunk_otel.init_splunk_otel"),
        patch("opentelemetry.instrumentation.langchain.LangChainInstrumentor"),
        patch("model.load.load_model", return_value=MagicMock()),
        patch("mcp_client.client.get_streamable_http_mcp_client", return_value=mock_mcp_client),
    ):
        import main

        yield main


@pytest.fixture
def model_module():
    import model.load as load_module

    return load_module

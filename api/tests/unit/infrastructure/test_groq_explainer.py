from unittest.mock import MagicMock

from aro.domain.alerting.entities import Alert
from aro.domain.shared.value_objects import Criticity, IpAddress
from aro.infrastructure.alerting.groq_explainer import GroqExplainer


def _make_alert() -> Alert:
    return Alert.create(
        title="Port Scan Detected",
        source_ip=IpAddress("10.0.0.1"),
        criticity=Criticity.HIGH,
        rule_name="network_port_scan",
    )


def _make_explainer(response_text: str = "Analyse SOC") -> tuple[GroqExplainer, MagicMock]:
    mock_client = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = response_text
    mock_client.chat.completions.create.return_value = MagicMock(choices=[mock_choice])

    explainer = GroqExplainer(api_key="fake-key")
    explainer._client = mock_client
    return explainer, mock_client


def test_explain_returns_content() -> None:
    explainer, _ = _make_explainer("Scan de ports détecté.")
    assert explainer.explain(_make_alert()) == "Scan de ports détecté."


def test_explain_uses_configured_model() -> None:
    explainer, mock_client = _make_explainer()
    explainer._model = "llama-3.1-8b-instant"
    explainer.explain(_make_alert())
    call_kwargs = mock_client.chat.completions.create.call_args.kwargs
    assert call_kwargs["model"] == "llama-3.1-8b-instant"


def test_explain_sends_two_messages() -> None:
    explainer, mock_client = _make_explainer()
    explainer.explain(_make_alert())
    messages = mock_client.chat.completions.create.call_args.kwargs["messages"]
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"


def test_explain_includes_alert_fields_in_prompt() -> None:
    explainer, mock_client = _make_explainer()
    alert = _make_alert()
    explainer.explain(alert)
    prompt = mock_client.chat.completions.create.call_args.kwargs["messages"][1]["content"]
    assert "Port Scan Detected" in prompt
    assert "10.0.0.1" in prompt
    assert "network_port_scan" in prompt


def test_explain_returns_empty_string_on_none_content() -> None:
    mock_client = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = None
    mock_client.chat.completions.create.return_value = MagicMock(choices=[mock_choice])
    explainer = GroqExplainer(api_key="fake-key")
    explainer._client = mock_client
    assert explainer.explain(_make_alert()) == ""

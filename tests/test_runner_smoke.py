"""Smoke test for the end-to-end evaluation runner."""

from types import SimpleNamespace

from data.schema import TaskExample
from eval.runner import run_eval


class FakeClient:
    """Minimal fake OpenAI-compat client for tests."""

    def __init__(self, response: str):
        self.response = response

    def chat(self, model, messages, temperature=0.0, max_tokens=None, **kwargs):
        return self.response, {"model": model}


def test_run_eval_smoke(tmp_path, monkeypatch):
    """Run a tiny eval with faked dependencies to validate plumbing."""
    examples = [
        TaskExample(
            id="ex-1",
            task_type="multiple_choice",
            question="Pick A",
            choices=["A", "B"],
            label="A",
        ),
        TaskExample(
            id="ex-2",
            task_type="multiple_choice",
            question="Pick B",
            choices=["A", "B"],
            label="B",
        ),
    ]

    # Patch loader to avoid network calls.
    monkeypatch.setattr("data.loader.load_examples", lambda cfg: examples)
    monkeypatch.setattr("eval.runner.load_examples", lambda cfg: examples)

    # Patch provider to use fake client.
    fake_client = FakeClient("A")
    monkeypatch.setattr("llm.providers.make_openai_client", lambda cfg: fake_client)
    monkeypatch.setattr("eval.runner.make_openai_client", lambda cfg: fake_client)

    # Patch FinRobot MultiAssistant to avoid external dependency.
    class DummyUserProxy:
        def initiate_chat(self, representative, message, silent=True):
            return SimpleNamespace(chat_history=[{"name": "Final", "content": "A"}])

        def reset(self):
            return None

    class DummyGroup:
        def __init__(self, *args, **kwargs):
            self.user_proxy = DummyUserProxy()
            self.representative = object()
            self.group_chat = SimpleNamespace(messages=[{"name": "Final", "content": "A"}])

        def reset(self):
            return None

    monkeypatch.setattr("systems.finrobot_agent.MultiAssistant", DummyGroup)

    cfg = {
        "provider": "ollama",
        "base_url": "http://localhost:11434/v1/",
        "model": "dummy",
        "max_samples": 2,
        "seed": 1,
        "temperature": 0,
        "output_dir": str(tmp_path),
        "run_baseline": True,
        "run_agent": True,
        "ablations": ["agent_no_critic"],
        "datasets": [
            {
                "name": "dummy",
                "hf_path": "dummy/path",
                "split": "test",
                "task_type": "multiple_choice",
                "question_field": "query",
                "choices_field": "choices",
                "label_field": "gold",
                "label_type": "index",
            }
        ],
    }

    run_dir = run_eval(cfg)
    assert run_dir is not None

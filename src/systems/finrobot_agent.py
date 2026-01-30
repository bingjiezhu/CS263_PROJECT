"""FinRobot-backed agent runner for planner/solver/critic/final workflows."""

from __future__ import annotations

import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from data.schema import TaskExample
from llm.parsing import extract_choice_strict, extract_label
from systems.finrobot_tools import build_toolkits
from systems.prompts import (
    CRITIC_SYSTEM,
    CRITIC_SYSTEM_FULL,
    FINAL_SYSTEM,
    FINAL_SYSTEM_FULL,
    PLANNER_SYSTEM,
    PLANNER_SYSTEM_FULL,
    SOLVER_SYSTEM,
    SOLVER_SYSTEM_FULL,
    build_agent_prompt,
    build_user_prompt,
)
from utils.cache import DiskCache, make_cache_key


def _ensure_finrobot_importable() -> None:
    """Ensure the FinRobot package is importable, cloning if necessary."""
    try:
        import finrobot  # noqa: F401

        return
    except Exception:
        pass

    # Try explicit env path.
    env_path = os.environ.get("FINROBOT_PATH")
    if env_path and os.path.isdir(env_path):
        sys.path.insert(0, env_path)
        try:
            import finrobot  # noqa: F401

            return
        except Exception:
            sys.path.pop(0)

    # Try local vendor path.
    repo_root = Path(__file__).resolve().parents[2]
    vendor_path = repo_root / "third_party" / "FinRobot"
    if vendor_path.exists():
        sys.path.insert(0, str(vendor_path))
        try:
            import finrobot  # noqa: F401

            return
        except Exception:
            sys.path.pop(0)

    # Last resort: clone FinRobot into the repo.
    vendor_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run(
            [
                "git",
                "clone",
                "--depth",
                "1",
                "https://github.com/AI4Finance-Foundation/FinRobot",
                str(vendor_path),
            ],
            check=True,
        )
        sys.path.insert(0, str(vendor_path))
        import finrobot  # noqa: F401

        return
    except Exception as exc:
        raise ImportError(
            "FinRobot not found. Please clone https://github.com/AI4Finance-Foundation/FinRobot "
            "into finrobot-pixiu-eval/third_party/FinRobot or set FINROBOT_PATH."
        ) from exc


_ensure_finrobot_importable()

try:
    from finrobot.agents.workflow import MultiAssistant, MultiAssistantWithLeader
except Exception as exc:  # pragma: no cover
    MultiAssistant = None
    MultiAssistantWithLeader = None
    _IMPORT_ERROR = exc


def _strip_tool_config(cfg: Dict[str, Any]) -> Dict[str, Any]:
    """Remove tool-related keys from an AutoGen config to avoid conflicts."""
    if not isinstance(cfg, dict):
        return cfg
    clean = dict(cfg)
    for key in ["functions", "function_call", "tools", "tool_choice"]:
        if key in clean:
            clean.pop(key, None)
    return clean


def _read_multiline_input() -> str:
    """Read multi-line manual input terminated by a single END line."""
    lines: List[str] = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.strip().upper() == "END":
            break
        lines.append(line)
    return "\n".join(lines).strip()


if MultiAssistant is not None:

    class SafeMultiAssistant(MultiAssistant):
        """MultiAssistant with a safer speaker selection for tool calls."""

        def _get_representative(self):
            """Build and return a GroupChatManager with a custom speaker selector."""
            import autogen
            from autogen import GroupChat, GroupChatManager

            def custom_speaker_selection_func(
                last_speaker: autogen.Agent, groupchat: autogen.GroupChat
            ):
                """Choose the next speaker with tool-call safeguards."""
                messages = groupchat.messages
                if len(messages) <= 1:
                    return groupchat.agents[0]
                if last_speaker is self.user_proxy:
                    return groupchat.agent_by_name(messages[-2]["name"])
                if "tool_calls" in messages[-1] or messages[-1]["content"].endswith(
                    "TERMINATE"
                ):
                    return self.user_proxy
                return groupchat.next_agent(last_speaker, groupchat.agents[:-1])

            # Rebuild the group chat with a custom selection function.
            self.group_chat = GroupChat(
                self.agents + [self.user_proxy],
                messages=[],
                speaker_selection_method=custom_speaker_selection_func,
                send_introductions=True,
            )
            manager_name = (self.group_config.get("name", "") + "_chat_manager").strip("_")
            manager = GroupChatManager(
                self.group_chat,
                name=manager_name,
                llm_config=_strip_tool_config(self.llm_config),
            )
            return manager

else:
    SafeMultiAssistant = None


class FinRobotAgentRunner:
    """Runner that executes the FinRobot multi-agent workflow per example."""

    def __init__(
        self,
        llm_config: Dict[str, Any],
        temperature: float = 0.0,
        no_critic: bool = False,
        finrobot_config: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the runner with LLM config and FinRobot settings."""
        if MultiAssistant is None:
            raise ImportError(
                "Failed to import FinRobot. Please ensure finrobot is installed."
            ) from _IMPORT_ERROR
        self.llm_config = llm_config
        self.temperature = temperature
        self.no_critic = no_critic
        self.finrobot_config = finrobot_config or {}
        self._tool_info: Dict[str, Any] = {}
        self._rag_assistants: List[Any] = []
        self._logger = logging.getLogger("finrobot_pixiu_eval")

    def _select_prompts(self) -> tuple[str, str, str, str]:
        """Pick role prompts based on minimal vs full mode."""
        mode = self.finrobot_config.get("mode", "minimal")
        if mode == "full":
            planner_prompt = PLANNER_SYSTEM_FULL
            solver_prompt = SOLVER_SYSTEM_FULL
            critic_prompt = CRITIC_SYSTEM_FULL
            final_prompt = FINAL_SYSTEM_FULL
        else:
            planner_prompt = PLANNER_SYSTEM
            solver_prompt = SOLVER_SYSTEM
            critic_prompt = CRITIC_SYSTEM
            final_prompt = FINAL_SYSTEM
        return planner_prompt, solver_prompt, critic_prompt, final_prompt

    def _manual_role(self, role_name: str, system_prompt: str, user_prompt: str) -> str:
        """Run a role in manual mode by printing prompts and reading input."""
        banner = "=" * 80
        print("\n" + banner)
        print(f"[MANUAL MODE] Role: {role_name}")
        print(banner)
        print("\n[SYSTEM]\n" + system_prompt)
        print("\n[USER]\n" + user_prompt)
        print("\n[RESPONSE] End with a single line: END")
        return _read_multiline_input()

    def _run_once_manual(
        self,
        user_prompt: str,
        example: TaskExample,
    ) -> tuple[str, List[Dict[str, Any]]]:
        """Execute the multi-role workflow with human responses."""
        planner_prompt, solver_prompt, critic_prompt, final_prompt = self._select_prompts()
        history: List[Dict[str, Any]] = []

        planner_out = self._manual_role("Planner", planner_prompt, user_prompt)
        history.append({"name": "Planner", "content": planner_out})

        solver_user = user_prompt + "\n\nPlanner output:\n" + planner_out
        solver_out = self._manual_role("Solver", solver_prompt, solver_user)
        history.append({"name": "Solver", "content": solver_out})

        critic_out = ""
        if not self.no_critic:
            critic_user = (
                user_prompt
                + "\n\nPlanner output:\n"
                + planner_out
                + "\n\nSolver output:\n"
                + solver_out
            )
            critic_out = self._manual_role("Critic", critic_prompt, critic_user)
            history.append({"name": "Critic", "content": critic_out})

        final_user = build_agent_prompt(
            example.question,
            example.choices,
            example.context,
            strict=True,
        )
        final_user += "\n\nPlanner output:\n" + planner_out
        final_user += "\n\nSolver output:\n" + solver_out
        if not self.no_critic:
            final_user += "\n\nCritic output:\n" + critic_out
        final_out = self._manual_role("Final", final_prompt, final_user)
        history.append({"name": "Final", "content": final_out})
        return final_out, history

    def _build_group(self) -> MultiAssistant:
        """Construct the FinRobot MultiAssistant or MultiAssistantWithLeader group."""
        mode = self.finrobot_config.get("mode", "minimal")
        enable_tools = bool(self.finrobot_config.get("enable_tools", mode == "full"))
        workflow = self.finrobot_config.get("workflow", "group_chat")
        max_turns = int(self.finrobot_config.get("max_turns", 6))

        # Optional code execution for tool runs.
        code_exec_cfg = self.finrobot_config.get("code_execution", {}) or {}
        code_exec_enabled = bool(code_exec_cfg.get("enabled", False))
        code_execution_config = code_exec_cfg.get("config", False) if code_exec_enabled else False
        if code_exec_enabled and code_execution_config is False:
            code_execution_config = {
                "work_dir": code_exec_cfg.get("work_dir", "finrobot_codegen"),
                "use_docker": False,
            }

        toolkits: List[Any] = []
        if enable_tools:
            toolkits, self._tool_info = build_toolkits(self.finrobot_config)
            if self._logger:
                self._logger.info("FinRobot tools enabled: %s", self._tool_info.get("enabled", []))
                skipped = self._tool_info.get("skipped", [])
                if skipped:
                    self._logger.info("FinRobot tools skipped: %s", skipped)

            # Optional RAG utility from FinRobot.
            rag_cfg = self.finrobot_config.get("rag", {}) or {}
            if rag_cfg.get("enabled"):
                try:
                    from finrobot.functional.rag import get_rag_function

                    retrieve_config = rag_cfg.get("retrieve_config", {}) or {}
                    if "docs_path" not in retrieve_config:
                        retrieve_config["docs_path"] = rag_cfg.get("docs_path", [])
                    rag_desc = rag_cfg.get("description", "")
                    rag_func, rag_assistant = get_rag_function(retrieve_config, rag_desc)
                    toolkits.append(rag_func)
                    self._rag_assistants.append(rag_assistant)
                except Exception:
                    if self._logger:
                        self._logger.info("RAG tool could not be initialized; skipping.")

        planner_prompt, solver_prompt, critic_prompt, final_prompt = self._select_prompts()

        agent_configs = [
            {"name": "Planner", "profile": planner_prompt, "toolkits": toolkits if enable_tools else []},
            {"name": "Solver", "profile": solver_prompt, "toolkits": toolkits if enable_tools else []},
        ]
        if not self.no_critic:
            agent_configs.append(
                {"name": "Critic", "profile": critic_prompt, "toolkits": toolkits if enable_tools else []}
            )
        agent_configs.append(
            {"name": "Final", "profile": final_prompt, "toolkits": toolkits if enable_tools else []}
        )

        if workflow == "leader" and MultiAssistantWithLeader is not None:
            leader_cfg = self.finrobot_config.get("leader") or {
                "title": "Team_Leader",
                "responsibilities": [
                    "Coordinate the team and produce the final answer.",
                    "Ensure the final output strictly follows the required format.",
                ],
            }
            group_config = {"leader": leader_cfg, "agents": agent_configs}
            group = MultiAssistantWithLeader(
                group_config=group_config,
                agent_configs=agent_configs,
                llm_config=self.llm_config,
                human_input_mode="NEVER",
                max_consecutive_auto_reply=max_turns,
                code_execution_config=code_execution_config,
            )
            return group

        group_config = {"name": "finrobot_eval_group"}
        assistant_cls = SafeMultiAssistant if SafeMultiAssistant is not None else MultiAssistant
        group = assistant_cls(
            group_config=group_config,
            agent_configs=agent_configs,
            llm_config=self.llm_config,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=max_turns,
            code_execution_config=code_execution_config,
        )
        if hasattr(group, "group_chat") and hasattr(group.group_chat, "max_round"):
            group.group_chat.max_round = max_turns
        return group

    def _extract_history(self, chat_result: Any, group: MultiAssistant) -> List[Dict[str, Any]]:
        """Pull chat history from AutoGen result or group chat."""
        history = []
        if chat_result is not None:
            maybe = getattr(chat_result, "chat_history", None)
            if maybe:
                history = maybe
        if not history and hasattr(group, "group_chat"):
            history = getattr(group.group_chat, "messages", []) or []
        return self._sanitize(history)

    def _sanitize(self, obj: Any) -> Any:
        """Ensure trace objects are JSON-serializable for logging."""
        if isinstance(obj, list):
            return [self._sanitize(v) for v in obj]
        if isinstance(obj, dict):
            return {str(k): self._sanitize(v) for k, v in obj.items()}
        try:
            import json

            json.dumps(obj)
            return obj
        except Exception:
            return str(obj)

    def _extract_final_content(self, history: List[Dict[str, Any]]) -> str:
        """Return the final agent message content, with a safe fallback."""
        if not history:
            return ""
        for msg in reversed(history):
            name = msg.get("name") if isinstance(msg, dict) else None
            if name == "Final":
                return msg.get("content", "")
        last = history[-1]
        return last.get("content", "") if isinstance(last, dict) else ""

    def _extract_choice_from_history(
        self,
        history: List[Dict[str, Any]],
        choices: Optional[List[str]],
    ) -> Optional[str]:
        """Search the full trace for a strict answer letter."""
        if not history:
            return None
        for msg in reversed(history):
            if not isinstance(msg, dict):
                continue
            content = msg.get("content", "")
            if not content:
                continue
            pred = extract_choice_strict(content, choices)
            if pred:
                return pred
        return None

    def _run_once(
        self,
        user_prompt: str,
        example: Optional[TaskExample] = None,
    ) -> tuple[str, List[Dict[str, Any]]]:
        """Run one agent session and return final content + trace."""
        manual_mode = bool(self.finrobot_config.get("manual_mode", False))
        if manual_mode:
            if example is None:
                return "", []
            return self._run_once_manual(user_prompt, example)

        group = self._build_group()
        chat_result = group.user_proxy.initiate_chat(
            group.representative,
            message=user_prompt,
            silent=True,
        )
        history = self._extract_history(chat_result, group)
        final_content = self._extract_final_content(history)

        # Reset the group to avoid state leakage across examples.
        group.reset()
        for rag_assistant in self._rag_assistants:
            try:
                rag_assistant.reset()
            except Exception:
                pass
        self._rag_assistants = []
        return final_content, history

    def predict_one(
        self,
        example: TaskExample,
        cache: Optional[DiskCache] = None,
    ) -> Dict[str, Any]:
        """Run the agent on a single example and return a rich record."""
        mode = self.finrobot_config.get("mode", "minimal")
        if mode == "full":
            user_prompt = build_agent_prompt(example.question, example.choices, example.context)
        else:
            user_prompt = build_user_prompt(example.question, example.choices, example.context)

        cache_key = None
        if cache is not None:
            cache_key = make_cache_key(
                {
                    "system": "finrobot_agent_no_critic" if self.no_critic else "finrobot_agent",
                    "llm_config": self.llm_config,
                    "prompt": user_prompt,
                    "temperature": self.temperature,
                    "finrobot_config": self.finrobot_config,
                }
            )
            cached = cache.get(cache_key)
            if cached is not None:
                return cached

        api_error: Optional[str] = None
        api_retry_used = 0
        max_api_retries = int(self.finrobot_config.get("api_max_retries", 2))
        retry_delay = float(self.finrobot_config.get("api_retry_delay", 1.0))
        delay = retry_delay if retry_delay > 0 else 1.0
        while True:
            try:
                final_content, history = self._run_once(user_prompt, example=example)
                break
            except Exception as exc:
                api_error = str(exc)
                if api_retry_used >= max_api_retries:
                    final_content = f"ERROR: {api_error}"
                    history = []
                    break
                time.sleep(delay)
                api_retry_used += 1
                delay *= 2
        pred: Optional[str] = None
        retry_used = 0
        retry_trace: Optional[List[Dict[str, Any]]] = None
        retry_response: Optional[str] = None

        if example.choices:
            pred = extract_choice_strict(final_content, example.choices)
            if pred is None:
                pred = self._extract_choice_from_history(history, example.choices)
        else:
            pred = extract_label(final_content)

        # Retry once with a strict prompt when output parsing fails.
        retry_on_invalid = bool(self.finrobot_config.get("retry_on_invalid", True))
        max_retries = int(self.finrobot_config.get("max_retries", 1))
        if pred is None and retry_on_invalid and max_retries > 0:
            strict_prompt = build_agent_prompt(
                example.question,
                example.choices,
                example.context,
                strict=True,
            )
            for _ in range(max_retries):
                retry_used += 1
                retry_response, retry_trace = self._run_once(strict_prompt, example=example)
                if example.choices:
                    pred = extract_choice_strict(retry_response, example.choices)
                    if pred is None and retry_trace is not None:
                        pred = self._extract_choice_from_history(retry_trace, example.choices)
                else:
                    pred = extract_label(retry_response)
                if pred is not None:
                    break

        if pred is None:
            pred = "INVALID"

        record = {
            "id": example.id,
            "task_type": example.task_type,
            "question": example.question,
            "choices": example.choices,
            "label": example.label,
            "prediction": pred,
            "correct": pred == example.label,
            "raw_response": final_content,
            "trace": history,
            "meta": {
                **(example.meta or {}),
                "finrobot_tool_info": self._tool_info,
                "finrobot_mode": self.finrobot_config.get("mode", "minimal"),
                "retry_used": retry_used,
                "api_retry_used": api_retry_used,
            },
        }
        if api_error:
            record["meta"]["api_error"] = api_error
        if retry_used and retry_trace is not None:
            record["meta"]["retry_trace"] = retry_trace
            record["meta"]["retry_response"] = retry_response

        if cache is not None and cache_key is not None:
            cache.set(cache_key, record)

        return record


def run_agent(
    examples: List[TaskExample],
    llm_config: Dict[str, Any],
    temperature: float = 0.0,
    no_critic: bool = False,
    cache: Optional[DiskCache] = None,
    finrobot_config: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Run the FinRobot agent over a list of examples."""
    runner = FinRobotAgentRunner(
        llm_config=llm_config,
        temperature=temperature,
        no_critic=no_critic,
        finrobot_config=finrobot_config,
    )
    outputs = []
    for ex in examples:
        outputs.append(runner.predict_one(ex, cache=cache))
    return outputs

# Run Metadata

- Run ID: ollama-deepseek-v3-1-671b-cloud__flare-mlesg__n20__20260129_225626
- Timestamp: 2026-01-29T22:56:26.999259

## Model and Provider
- provider: ollama
- model: deepseek-v3.1:671b-cloud
- base_url: http://localhost:11434/v1/
- temperature: 0
- seed: 42
- max_samples: 20
- max_samples_per_dataset: 20
- total_examples_loaded: 20
- use_cache: True

## Datasets
- name: pixiu_mlesg | hf_path: TheFinAI/flare-mlesg | split: test | task_type: multiple_choice
  fields: question=query | choices=choices | label=gold | label_type=index

## Systems
- run_baseline: True
- run_agent: True
- ablations: agent_no_critic
  - agent_no_critic: disables the Critic step (Planner → Solver → Final only)

## FinRobot Config
- mode: full
- workflow: group_chat
- enable_tools: False
- toolsets: []
- max_turns: 6
- retry_on_invalid: True
- max_retries: 1
- manual_mode: False
- rag_enabled: False
- code_execution_enabled: False

See config_snapshot.yaml for the full configuration.

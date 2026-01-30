# Run Metadata

- Run ID: ollama-gpt-oss-120b-cloud__pixiu-fpb-finben-fomc__n20__20260129_161651
- Timestamp: 2026-01-29T16:16:51.728844

## Model and Provider
- provider: ollama
- model: gpt-oss:120b-cloud
- base_url: http://localhost:11434/v1/
- temperature: 0
- seed: 42
- max_samples: 20
- max_samples_per_dataset: 20
- total_examples_loaded: 20
- use_cache: True

## Datasets
- name: pixiu_fpb | hf_path: TheFinAI/flare-fpb | split: test | task_type: multiple_choice
  fields: question=query | choices=choices | label=gold | label_type=index
- name: finben_fomc | hf_path: TheFinAI/finben-fomc | split: test | task_type: multiple_choice
  fields: question=query | choices=choices | label=gold | label_type=index

## Systems
- run_baseline: True
- run_agent: True
- ablations: agent_no_critic

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

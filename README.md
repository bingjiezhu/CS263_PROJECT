# FinRobot x PIXIU/FinBen: Reproducible Agent Evaluation

This project builds a reproducible evaluation pipeline that compares a FinRobot-style multi-agent workflow against a direct (non-agent) baseline on PIXIU/FinBen benchmarks. It is designed to be closed-book by default and fully runnable with either Gemini (OpenAI-compat) or local Ollama models.

## Required Upstream Repositories
- FinRobot (AI4Finance Foundation): https://github.com/AI4Finance-Foundation/FinRobot
- PIXIU (The-FinAI): https://github.com/The-FinAI/PIXIU
- FinBen (The-FinAI): https://github.com/The-FinAI/FinBen

## What This Project Does
- Normalizes benchmark examples into a shared schema.
- Runs a single-shot baseline model (non-agent).
- Runs a multi-step FinRobot agent (Planner → Solver → Critic → Final).
- Produces metrics, logs, and a comparison report with error analysis.
- Supports a tool-enabled full mode when optional keys and dependencies exist.

## Repository Layout
```
finrobot-pixiu-eval/
├── README.md
├── environment.yml
├── configs/
│   ├── eval_config.yaml
│   └── keys.example.env
├── scripts/
│   └── run_eval.py
├── src/
│   ├── data/         # dataset loading + adapters
│   ├── llm/          # provider abstraction + parsing
│   ├── systems/      # baseline + FinRobot agent workflow
│   ├── eval/         # metrics + report generation
│   └── utils/        # logging, cache, seeding
└── outputs/
    └── runs/<run_id>/
        ├── baseline.jsonl
        ├── agent.jsonl
        ├── metrics_baseline.json
        ├── metrics_agent.json
        ├── compare.md
        └── config_snapshot.yaml
```

## Quickstart (Gemini)
### 1) Create Environment
```bash
conda create -n cs263_project python=3.10 -y
conda activate cs263_project
```

### 2) Install Dependencies
```bash
pip install -e .
```

To enable all optional FinRobot tool dependencies, install extras:
```bash
pip install -e ".[full]"
```

### 3) Configure GEMINI_API_KEY
```bash
export GEMINI_API_KEY="YOUR_GEMINI_KEY"
```

You can also place keys in a project `.env`; `scripts/run_eval.py` will load it automatically.

### 4) Run Evaluation
```bash
python scripts/run_eval.py --config configs/eval_config.yaml
```

## Quickstart (Ollama Local Model)
### 1) Install and Start Ollama
- Install: https://ollama.com/
- Start service:
```bash
ollama serve
```

### 2) Pull a Small Model
```bash
ollama pull qwen2.5:3b
```

### 3) Update `configs/eval_config.yaml`
```yaml
provider: ollama
base_url: "http://localhost:11434/v1/"
model: "qwen2.5:3b"
```

### 4) Run Evaluation
```bash
python scripts/run_eval.py --config configs/eval_config.yaml
```

## LLM Provider Abstraction
- Gemini (default)
  - OpenAI-compat endpoint: `https://generativelanguage.googleapis.com/v1beta/openai/`
  - Environment variable: `GEMINI_API_KEY`
- Ollama (optional)
  - OpenAI-compat endpoint: `http://localhost:11434/v1/`
  - No cloud key needed, `api_key` is fixed to `ollama`
- Manual (human-in-the-loop)
  - Provider `manual` prints prompts and waits for an `END`-terminated response

## Manual (Human-in-the-loop) Mode
If you want to answer prompts manually (e.g., by pasting responses from ChatGPT), use the manual provider.

1) Update `configs/eval_config.yaml`:
```yaml
provider: manual
model: "manual"
finrobot:
  manual_mode: true
```

2) Run:
```bash
python scripts/run_eval.py --config configs/eval_config.yaml
```

3) For each prompt, paste your response and finish with a single line: `END`.

## Evaluation Config (`configs/eval_config.yaml`)
- Includes PIXIU `flare-cfa` (CFA-style multiple-choice QA) by default
- Multiple-choice/classification subset only
- Unified schema: `TaskExample {id, task_type, question, choices, context, label}`
- Controls: `max_samples`, `seed`, `temperature`, `run_baseline`, `run_agent`, `ablations`

## Data Used (Current Default Config)
The default `configs/eval_config.yaml` uses the following benchmark datasets and tasks:
- PIXIU CFA: `TheFinAI/flare-cfa` (split: `test`), multiple-choice questions using fields `query`, `text`, `choices`, and `gold` (index label).

## Dataset Websites and Task Details
### PIXIU CFA
- Website: https://huggingface.co/datasets/TheFinAI/flare-cfa
- Task category: finance multiple-choice QA.
- Task description: answer CFA-style finance questions with three options (A/B/C).
- Labels: `A`, `B`, `C` (via `gold` index).
- Fields used in this project: `query`, `text`, `choices`, `gold` (index label).
 - Notes: the dataset provides both `query` and `text`; this project uses `query` as the main prompt and `text` as optional context.

### Other Supported Tasks (Optional)
### PIXIU MLESG
- Website: https://huggingface.co/datasets/TheFinAI/flare-mlesg
- Task category: ESG issue classification.
- Task description: classify each article into a fine-grained MSCI ESG issue label.
- Labels: multi-class labels provided in `choices` (e.g., Access to Communications, Carbon Emissions, Privacy & Data Security, etc.).
- Fields used in this project: `query`, `text`, `choices`, `gold` (index label).

### PIXIU FinArg-ECC Task2 (ARC)
- Website: https://huggingface.co/datasets/TheFinAI/flare-finarg-ecc-arc
- Task category: argument relation classification.
- Task description: classify the relation between two sentences as **norelation**, **support**, or **attack**.
- Labels: `norelation`, `support`, `attack`.
- Fields used in this project: `query`, `text`, `choices`, `gold` (index label).
- Access note: this dataset is gated on Hugging Face; accept access on the dataset page and set `HF_TOKEN`.

### PIXIU FPB (Financial PhraseBank)
- Website: https://huggingface.co/datasets/TheFinAI/flare-fpb
- Task category: sentiment classification (text classification).
- Task description: classify a financial news sentence as **positive**, **negative**, or **neutral**.
- Labels (as used in common FPB setups): `positive`, `neutral`, `negative`.
- Fields used in this project: `query`, `choices`, `gold` (index label).

### FinBen FOMC
- Website: https://huggingface.co/datasets/TheFinAI/finben-fomc
- Task category: text classification.
- Task description: classify a central-bank statement sentence as **HAWKISH**, **DOVISH**, or **NEUTRAL**.
- Fields in dataset card: `id`, `query`, `answer`, `choices`, `gold`.
- Split: test (496 instances).

## Outputs
Generated under `outputs/runs/<run_id>/`:
- `baseline.jsonl` / `agent.jsonl`: per-sample predictions and raw responses
- `metrics_baseline.json` / `metrics_agent.json`
- `compare.md`: metrics table + absolute gains (pp) + top-10 error analysis
- `config_snapshot.yaml`: resolved run config
- `README.md`: run metadata (model, datasets, sampling, agent settings)

Run folder naming convention:
`<provider>-<model>__<datasets>__n<samples>__<timestamp>`

## Ablations
- `agent_no_critic`: disables the Critic step in the FinRobot workflow (Planner → Solver → Final only). This isolates the effect of self-critique on performance.

## Full FinRobot Mode (Tools Enabled)
To enable the full FinRobot toolchain (market data, filings, news, charts), set the `finrobot` section in `configs/eval_config.yaml` to `mode: full` and `enable_tools: true`.

## FinRobot Coverage vs This Project
This project integrates FinRobot's multi-agent workflow (Planner → Solver → Critic → Final) but runs in a closed-book configuration by default. Below is a quick status summary of what is enabled vs. disabled relative to the full FinRobot stack.

### Enabled in this project
- FinRobot multi-agent workflow (via `finrobot.agents.workflow`).
- Group chat orchestration with a user proxy and role prompts.
- Optional full-mode prompts (when `mode: full`) while still keeping tools off by default.

### Not enabled by default (closed-book)
- External data tools (Finnhub, FMP, SEC, Reddit, etc.).
- Tool calls / toolsets (set `enable_tools: false` and `toolsets: []`).
- RAG pipelines (set `rag.enabled: false`).
- Code execution tools (set `code_execution.enabled: false`).

### How to enable full functionality
- Set `finrobot.enable_tools: true` and add the desired `toolsets`.
- Provide required API keys in `.env` (see below).
- Enable RAG / code execution only if you have the dependencies and a secure runtime.

### Optional Keys for Full Tool Access
- `FINNHUB_API_KEY` (Finnhub market data/news)
- `FMP_API_KEY` (Financial Modeling Prep)
- `SEC_API_KEY` (sec-api for filings)
- `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET` (Reddit data via PRAW)

Add these to `.env` or export them in your shell. Use `configs/keys.example.env` as a template.

### Tool Availability Behavior
- If a key or dependency is missing, the corresponding toolset is skipped and logged.
- The agent still runs, but only with the available tools.

### FinRobot Source
FinRobot is auto-cloned at runtime into `finrobot-pixiu-eval/third_party/FinRobot` if not present.
You can also manually clone and set:
```bash
export FINROBOT_PATH=/path/to/FinRobot
```
Note: the `third_party/` directory is excluded from version control in this repo, so it will not appear after cloning from GitHub.

## Troubleshooting
- Rate limit / 429: reduce `max_samples` and retry later.
- Parsing failures (`INVALID`): use a stronger model or lower temperature.
- HF dataset download issues: check network or set `HF_HOME` / `HF_ENDPOINT`.
- Dependency conflicts: use a fresh `cs263_project` environment, or `pip install -U`.
- Ollama connection errors: ensure `ollama serve` is running and `base_url` is correct.
- FinRobot auto-clone failed: ensure `git` is installed and GitHub is reachable, or set `FINROBOT_PATH`.

## Notes
- FinRobot/PIXIU/FinBen are used as upstream sources; this project provides a reproducible evaluation wrapper.
- For closed-book runs, the agent should avoid external data tools unless explicitly enabled.

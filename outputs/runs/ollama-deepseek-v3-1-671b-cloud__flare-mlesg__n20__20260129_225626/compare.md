# Agent vs Baseline Comparison

## Metrics

| System | Accuracy | Macro-F1 | Invalid Rate | n |
|---|---:|---:|---:|---:|
| Baseline | 0.4500 | 0.2540 | 0.1000 | 20 |
| Agent | 0.3500 | 0.2250 | 0.0000 | 20 |
| agent_no_critic | 0.4500 | 0.2784 | 0.0000 | 20 |

## Absolute Improvement (Agent - Baseline)

- Accuracy: -10.00 pp
- Macro-F1: -2.90 pp

## Error Analysis


### Top-10: Baseline Wrong / Agent Correct


### Top-10: Baseline Correct / Agent Wrong

- pixiu_mlesg-mlesg101: You're given English news articles related to Environmental, Social, and Corporate Governance (ESG) issues. Your task is to classify each article based on th... | gold=H | baseline=H | agent=I
- pixiu_mlesg-mlesg119: You're given English news articles related to Environmental, Social, and Corporate Governance (ESG) issues. Your task is to classify each article based on th... | gold=F | baseline=F | agent=U

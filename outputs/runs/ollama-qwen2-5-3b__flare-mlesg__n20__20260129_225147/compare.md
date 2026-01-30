# Agent vs Baseline Comparison

## Metrics

| System | Accuracy | Macro-F1 | Invalid Rate | n |
|---|---:|---:|---:|---:|
| Baseline | 0.3500 | 0.2111 | 0.0500 | 20 |
| Agent | 0.3500 | 0.1947 | 0.0000 | 20 |
| agent_no_critic | 0.3500 | 0.2000 | 0.0000 | 20 |

## Absolute Improvement (Agent - Baseline)

- Accuracy: 0.00 pp
- Macro-F1: -1.64 pp

## Error Analysis


### Top-10: Baseline Wrong / Agent Correct

- pixiu_mlesg-mlesg140: You're given English news articles related to Environmental, Social, and Corporate Governance (ESG) issues. Your task is to classify each article based on th... | gold=H | baseline=Y | agent=H

### Top-10: Baseline Correct / Agent Wrong

- pixiu_mlesg-mlesg279: You're given English news articles related to Environmental, Social, and Corporate Governance (ESG) issues. Your task is to classify each article based on th... | gold=D | baseline=D | agent=J

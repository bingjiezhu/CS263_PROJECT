# Agent vs Baseline Comparison

## Metrics

| System | Accuracy | Macro-F1 | Invalid Rate | n |
|---|---:|---:|---:|---:|
| Baseline | 1.0000 | 1.0000 | 0.0000 | 20 |
| Agent | 0.9500 | 0.9649 | 0.0000 | 20 |
| agent_no_critic | 0.9000 | 0.9296 | 0.0000 | 20 |

## Absolute Improvement (Agent - Baseline)

- Accuracy: -5.00 pp
- Macro-F1: -3.51 pp

## Error Analysis


### Top-10: Baseline Wrong / Agent Correct


### Top-10: Baseline Correct / Agent Wrong

- pixiu_fpb-fpb3980: Analyze the sentiment of this statement extracted from a financial news article. Provide your answer as either negative, positive, or neutral. Text: Ruukki h... | gold=A | baseline=A | agent=B

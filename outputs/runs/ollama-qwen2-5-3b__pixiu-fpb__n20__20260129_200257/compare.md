# Agent vs Baseline Comparison

## Metrics

| System | Accuracy | Macro-F1 | Invalid Rate | n |
|---|---:|---:|---:|---:|
| Baseline | 0.7000 | 0.7841 | 0.0000 | 20 |
| Agent | 0.5000 | 0.4880 | 0.0000 | 20 |
| agent_no_critic | 0.4500 | 0.4198 | 0.0000 | 20 |

## Absolute Improvement (Agent - Baseline)

- Accuracy: -20.00 pp
- Macro-F1: -29.61 pp

## Error Analysis


### Top-10: Baseline Wrong / Agent Correct

- pixiu_fpb-fpb4530: Analyze the sentiment of this statement extracted from a financial news article. Provide your answer as either negative, positive, or neutral. Text: `` This ... | gold=B | baseline=A | agent=B

### Top-10: Baseline Correct / Agent Wrong

- pixiu_fpb-fpb3901: Analyze the sentiment of this statement extracted from a financial news article. Provide your answer as either negative, positive, or neutral. Text: The comp... | gold=A | baseline=A | agent=B
- pixiu_fpb-fpb3906: Analyze the sentiment of this statement extracted from a financial news article. Provide your answer as either negative, positive, or neutral. Text: ` By sep... | gold=A | baseline=A | agent=B
- pixiu_fpb-fpb4018: Analyze the sentiment of this statement extracted from a financial news article. Provide your answer as either negative, positive, or neutral. Text: Sponda w... | gold=A | baseline=A | agent=B
- pixiu_fpb-fpb4126: Analyze the sentiment of this statement extracted from a financial news article. Provide your answer as either negative, positive, or neutral. Text: Kalnapil... | gold=A | baseline=A | agent=B
- pixiu_fpb-fpb4480: Analyze the sentiment of this statement extracted from a financial news article. Provide your answer as either negative, positive, or neutral. Text: No servi... | gold=B | baseline=B | agent=C

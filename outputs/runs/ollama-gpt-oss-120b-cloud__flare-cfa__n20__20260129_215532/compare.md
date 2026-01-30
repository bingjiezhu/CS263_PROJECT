# Agent vs Baseline Comparison

## Metrics

| System | Accuracy | Macro-F1 | Invalid Rate | n |
|---|---:|---:|---:|---:|
| Baseline | 0.8500 | 0.8363 | 0.0000 | 20 |
| Agent | 0.9000 | 0.8833 | 0.0000 | 20 |
| agent_no_critic | 0.9000 | 0.8833 | 0.0000 | 20 |

## Absolute Improvement (Agent - Baseline)

- Accuracy: 5.00 pp
- Macro-F1: 4.71 pp

## Error Analysis


### Top-10: Baseline Wrong / Agent Correct

- pixiu_cfa-4: Read the questions and answers carefully, and choose the one you think is appropriate among the three options A, B and C. Q:Under which section of a manufact... | gold=B | baseline=A | agent=B

### Top-10: Baseline Correct / Agent Wrong


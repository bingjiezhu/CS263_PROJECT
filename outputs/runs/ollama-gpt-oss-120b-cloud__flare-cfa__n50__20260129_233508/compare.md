# Agent vs Baseline Comparison

## Metrics

| System | Accuracy | Macro-F1 | Invalid Rate | n |
|---|---:|---:|---:|---:|
| Baseline | 0.8600 | 0.8615 | 0.0000 | 50 |
| Agent | 0.9000 | 0.9020 | 0.0000 | 50 |
| agent_no_critic | 0.8600 | 0.8615 | 0.0000 | 50 |

## Absolute Improvement (Agent - Baseline)

- Accuracy: 4.00 pp
- Macro-F1: 4.05 pp

## Error Analysis


### Top-10: Baseline Wrong / Agent Correct

- pixiu_cfa-24: Read the questions and answers carefully, and choose the one you think is appropriate among the three options A, B and C. Q:Which of the following is not a r... | gold=B | baseline=A | agent=B
- pixiu_cfa-41: Read the questions and answers carefully, and choose the one you think is appropriate among the three options A, B and C. Q:To the holder of a long position,... | gold=A | baseline=C | agent=A

### Top-10: Baseline Correct / Agent Wrong


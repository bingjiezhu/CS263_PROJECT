# Agent vs Baseline Comparison

## Metrics

| System | Accuracy | Macro-F1 | Invalid Rate | n |
|---|---:|---:|---:|---:|
| Baseline | 0.4500 | 0.4505 | 0.0000 | 20 |
| Agent | 0.4000 | 0.3702 | 0.0000 | 20 |
| agent_no_critic | 0.4000 | 0.4048 | 0.0000 | 20 |

## Absolute Improvement (Agent - Baseline)

- Accuracy: -5.00 pp
- Macro-F1: -8.03 pp

## Error Analysis


### Top-10: Baseline Wrong / Agent Correct

- pixiu_cfa-8: Read the questions and answers carefully, and choose the one you think is appropriate among the three options A, B and C. Q:For a lessor, the leased asset ap... | gold=C | baseline=A | agent=C
- pixiu_cfa-11: Read the questions and answers carefully, and choose the one you think is appropriate among the three options A, B and C. Q:The market value of an undervalue... | gold=A | baseline=B | agent=A

### Top-10: Baseline Correct / Agent Wrong

- pixiu_cfa-1: Read the questions and answers carefully, and choose the one you think is appropriate among the three options A, B and C. Q:From an approved list of 25 funds... | gold=A | baseline=A | agent=C
- pixiu_cfa-5: Read the questions and answers carefully, and choose the one you think is appropriate among the three options A, B and C. Q:Purple Fleur S.A., a retailer of ... | gold=A | baseline=A | agent=B
- pixiu_cfa-13: Read the questions and answers carefully, and choose the one you think is appropriate among the three options A, B and C. Q:With respect to Level III sponsor... | gold=A | baseline=A | agent=B

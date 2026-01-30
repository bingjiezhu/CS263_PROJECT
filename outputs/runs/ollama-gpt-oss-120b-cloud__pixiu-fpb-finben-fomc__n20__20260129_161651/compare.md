# Agent vs Baseline Comparison

## Metrics

| System | Accuracy | Macro-F1 | Invalid Rate | n |
|---|---:|---:|---:|---:|
| Baseline | 0.9000 | 0.9074 | 0.0000 | 20 |
| Agent | 0.9000 | 0.9074 | 0.0000 | 20 |
| agent_no_critic | 0.8500 | 0.8553 | 0.0000 | 20 |

## Absolute Improvement (Agent - Baseline)

- Accuracy: 0.00 pp
- Macro-F1: 0.00 pp

## Error Analysis


### Top-10: Baseline Wrong / Agent Correct

- finben_fomc-fomc111: Study the sentence below from a central bank's briefing. Categorize it as HAWKISH if it promotes a tightening of monetary policy, DOVISH if it represents an ... | gold=B | baseline=C | agent=B

### Top-10: Baseline Correct / Agent Wrong

- finben_fomc-fomc142: Examine the excerpt from a central bank's release below. Classify it as HAWKISH if it advocates for a tightening of monetary policy, DOVISH if it suggests an... | gold=B | baseline=B | agent=C

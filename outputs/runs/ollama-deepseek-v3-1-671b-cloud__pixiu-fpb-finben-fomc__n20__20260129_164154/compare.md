# Agent vs Baseline Comparison

## Metrics

| System | Accuracy | Macro-F1 | Invalid Rate | n |
|---|---:|---:|---:|---:|
| Baseline | 0.7500 | 0.7555 | 0.0000 | 20 |
| Agent | 0.7500 | 0.7540 | 0.0000 | 20 |
| agent_no_critic | 0.8500 | 0.8564 | 0.0000 | 20 |

## Absolute Improvement (Agent - Baseline)

- Accuracy: 0.00 pp
- Macro-F1: -0.15 pp

## Error Analysis


### Top-10: Baseline Wrong / Agent Correct

- finben_fomc-fomc101: Review the sentence from a central bank's communiqué. Designate it as HAWKISH if it expresses a tightening of monetary policy, DOVISH if it reveals an easing... | gold=C | baseline=A | agent=C
- finben_fomc-fomc111: Study the sentence below from a central bank's briefing. Categorize it as HAWKISH if it promotes a tightening of monetary policy, DOVISH if it represents an ... | gold=B | baseline=C | agent=B
- finben_fomc-fomc142: Examine the excerpt from a central bank's release below. Classify it as HAWKISH if it advocates for a tightening of monetary policy, DOVISH if it suggests an... | gold=B | baseline=C | agent=B

### Top-10: Baseline Correct / Agent Wrong

- pixiu_fpb-fpb4635: Analyze the sentiment of this statement extracted from a financial news article. Provide your answer as either negative, positive, or neutral. Text: The firs... | gold=B | baseline=B | agent=A
- finben_fomc-fomc301: Dissect the given sentence from a central bank's transcript. Tag it as HAWKISH if it denotes a tightening of monetary policy, DOVISH if it implies an easing ... | gold=C | baseline=C | agent=A
- finben_fomc-fomc359: Study the sentence below from a central bank's briefing. Categorize it as HAWKISH if it promotes a tightening of monetary policy, DOVISH if it represents an ... | gold=C | baseline=C | agent=A

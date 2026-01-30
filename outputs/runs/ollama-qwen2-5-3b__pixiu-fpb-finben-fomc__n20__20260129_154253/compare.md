# Agent vs Baseline Comparison

## Metrics

| System | Accuracy | Macro-F1 | Invalid Rate | n |
|---|---:|---:|---:|---:|
| Baseline | 0.7000 | 0.5525 | 0.0500 | 20 |
| Agent | 0.6000 | 0.5206 | 0.0000 | 20 |
| agent_no_critic | 0.6000 | 0.5323 | 0.0000 | 20 |

## Absolute Improvement (Agent - Baseline)

- Accuracy: -10.00 pp
- Macro-F1: -3.19 pp

## Error Analysis


### Top-10: Baseline Wrong / Agent Correct

- finben_fomc-fomc3: Study the sentence below from a central bank's briefing. Categorize it as HAWKISH if it promotes a tightening of monetary policy, DOVISH if it represents an ... | gold=C | baseline=B | agent=C
- finben_fomc-fomc279: Analyse the following sentence from a central bank's report. Tag it as HAWKISH if it alludes to a tightening of the monetary policy, DOVISH if it implies an ... | gold=C | baseline=INVALID | agent=C

### Top-10: Baseline Correct / Agent Wrong

- finben_fomc-fomc445: Consider the below statement from a central bank's bulletin. Identify it as HAWKISH if it supports a tightening of monetary policy, DOVISH if it hints at an ... | gold=B | baseline=B | agent=C
- pixiu_fpb-fpb4018: Analyze the sentiment of this statement extracted from a financial news article. Provide your answer as either negative, positive, or neutral. Text: Sponda w... | gold=A | baseline=A | agent=B
- finben_fomc-fomc119: Study the sentence below from a central bank's briefing. Categorize it as HAWKISH if it promotes a tightening of monetary policy, DOVISH if it represents an ... | gold=A | baseline=A | agent=B
- pixiu_fpb-fpb3901: Analyze the sentiment of this statement extracted from a financial news article. Provide your answer as either negative, positive, or neutral. Text: The comp... | gold=A | baseline=A | agent=B

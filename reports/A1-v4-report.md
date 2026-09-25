# A1-v4 Report

Same architecture as v3. Only change: pairwise margin ranking loss
instead of MSE. Objective matches the binary-choice metric.

| Variant | Cloud | Device | Delta | Verdict |
|---|---|---|---|---|
| linear | 99.8% | 91.4% | 8.4pp | FAIL |
| quadratic | 99.4% | 92.0% | 7.4pp | FAIL |
| threshold | 98.9% | 96.2% | 2.7pp | PASS |

## Overall: FAIL

Criterion: device within 3pp of cloud on every variant.
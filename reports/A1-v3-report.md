# A1-v3 Report

Task: binary route choice. Oracle = deterministic cost.
Cloud model: MLP 4->128->128->128->1. Device model: MLP 4->16->1.
Test set: 1000 scenarios per cost variant.

| Variant | Cloud | Device | Delta | Verdict |
|---|---|---|---|---|
| linear | 82.9% | 81.3% | 1.6pp | PASS |
| quadratic | 80.8% | 79.4% | 1.4pp | PASS |
| threshold | 85.1% | 76.5% | 8.6pp | FAIL |

## Overall: FAIL

Criterion: device agreement within 3pp of cloud on every variant.
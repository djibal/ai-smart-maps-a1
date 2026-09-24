# A1 Protocol

Falsification test for the claim: "On-device inference achieves <5% quality
delta vs cloud."

## Method

- 100 scenarios, 20 nodes each, ~15% edge density, 5 candidate routes each
- Oracle: hand-coded optimal scorer (ground truth)
- Cloud reference: llama3.2:3b via Ollama
- On-device proxy: qwen2.5:0.5b via Ollama

## Metric

Rank agreement with oracle, measured in percentage points of scenarios where
the model's pick matches the oracle's pick.

## Pass criterion

Delta (cloud - device) <= 5.0 percentage points.

## Limitation

The on-device proxy is a 0.5B model. A real NPU deployment would use a
quantized version of a comparable or larger model. This test establishes
the direction and magnitude of the delta, not the final production quality.

# AI-Smart-Maps A1

Falsification test for assumption A1: "On-device inference achieves <5%
quality delta vs cloud."

See docs/adr/A1-protocol.md for the full test design.

## Run

    python -m src.harness --scenarios 100

## Structure

    src/graph.py       graph generator and loader
    src/oracle.py      optimal route scorer (ground truth)
    src/cloud.py       cloud reference runner
    src/device.py      on-device proxy runner
    src/harness.py     end-to-end test driver
    src/report.py      result aggregation

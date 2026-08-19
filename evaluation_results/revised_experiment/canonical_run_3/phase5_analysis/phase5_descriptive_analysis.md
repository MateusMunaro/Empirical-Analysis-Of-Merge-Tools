# Phase 5 descriptive analysis

This report is generated from the released 117-observation canonical dataset.
Artifact names and repository paths are intentionally not part of the study's
scientific claims; the manuscript should cite the replication package and stable
table/figure identifiers instead.

## Overall results

| Tool | Applicable | Macro precision | Macro recall | Macro F1 | Micro F1 | End-to-end F1 | Complete |
|---|---:|---:|---:|---:|---:|---:|---:|
| FSTMerge | 39/39 | 35.72% | 74.07% | 46.36% | 47.99% | 45.17% | 0/39 |
| IntelliMerge | 18/39 | 74.59% | 67.63% | 71.11% | 68.82% | 31.00% | 2/39 |
| JDime | 2/39 | N/D | 0.00% | N/D | N/D | 0.00% | 0/39 |

## Interpretation boundaries

- Macro conformance describes quality only where a readable output exists.
- Micro scores pool TP/FP/FN and are secondary to scenario-level results.
- End-to-end F1 assigns zero to unavailable outputs and is a sensitivity measure.
- A clean execution is not equivalent to exact oracle conformance.
- Syntax evidence is not compilation, testing, semantic, or behavioral evidence.
- The benchmark is controlled and synthetic; claims do not generalize directly to mined projects.

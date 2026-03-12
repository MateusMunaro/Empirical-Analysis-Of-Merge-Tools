# Scientific Research on Merge Tools

## 📋 Overview

This repository contains a comprehensive scientific study evaluating the performance and effectiveness of multiple merge tools used in software development. The research employs rigorous empirical methods to compare merge tool capabilities across diverse scenarios.

**Evaluated Tools:**
- **FSTMerge** - Feature Structure Tree-based merge
- **IntelliMerge** - Intelligent semantic merge tool
- **JDime** - Java Differencing and Merging Tool
- **AutoMerge** - Automated structured merge
- **KDiff3** - Three-way merge with GUI support

## 🗂️ Project Structure

```
Pesquisa-cientifica/
├── scripts/                      # Python evaluation and execution scripts
│   ├── executor.py              # Interactive menu for running merge tools
│   ├── run_evaluation.py        # Main evaluation orchestrator
│   ├── demo_complete_evaluation.py  # Complete demonstration script
│   ├── merge_evaluation_tool.py # Core evaluation framework
│   ├── scientific_report_generator.py  # Academic report generator
│   ├── evaluation_config.py     # Configuration and data structures
│   └── graphs/                  # Visualization scripts
│       ├── accuracy_graph.py
│       ├── f1_score_graph.py
│       ├── recall_graph.py
│       └── combined_metrics_graph.py
├── merge_tools/                  # Merge tool binaries and executables
│   ├── FSTMerge/
│   ├── IntelliMerge/
│   ├── JDime/
│   ├── AutoMerge/
│   └── KDiff/
├── scenarios_base/               # Test scenarios for each tool
│   ├── FSTMerge/scenario_1..39/
│   ├── IntelliMerge/scenario_1..39/
│   ├── JDime/scenario_1..39/
│   └── AutoMerge/scenario_1..34/
├── output/                       # Merge operation results
│   ├── [Tool]/scenarios/        # Actual merge outputs
│   └── [Tool]/expected/         # Expected correct outputs
├── evaluation_results/           # Scientific evaluation results
│   └── scientific_evaluation/   # Detailed metrics and reports
├── java_dependencies/            # Java versions and native libraries
│   └── java-versions/
│       ├── jdk-11.0.2/
│       ├── jdk8u392-b08/
│       └── libgit2/
└── libs/                         # External libraries (JavaFX, activation.jar)
```

## 🔬 Research Methodology

### Phase 1: Initial Tool Execution

The first phase involved understanding and configuring each merge tool individually. Each tool has unique requirements and execution patterns:

#### 1.1 Tool-Specific Configurations

**FSTMerge:**
- Required creating `merge.expression` files for each scenario
- Uses a base directory structure with left/base/right branches
- Generates output in a `merge/` subdirectory

**IntelliMerge:**
- Java-based tool requiring explicit directory paths
- Creates nested directory structures mimicking workspace paths
- Required post-processing to flatten output structure

**JDime:**
- Requires specific JAVA_HOME configuration (JDK 8)
- Supports both structured and unstructured merge modes
- Some scenarios fail in structured mode, requiring fallback strategies

**AutoMerge:**
- Complex setup requiring JavaFX libraries
- Native library dependencies (libgit2)
- Uses JDK 11 with module path configuration
- Required downloading and configuring JavaFX SDK dynamically

**KDiff3:**
- GUI-based tool with batch mode support
- Simpler execution but limited automation capabilities

#### 1.2 Challenges Encountered

1. **Path Management:** Each tool expected different directory structures
2. **Java Version Compatibility:** Tools required different JDK versions (8 vs 11)
3. **Library Dependencies:** Missing libraries like JavaFX and libgit2
4. **Output Inconsistencies:** Tools generated outputs in varying locations
5. **Error Handling:** Some scenarios failed silently or with cryptic errors

### Phase 2: Development of Automated Executor

To streamline the execution of 39 scenarios across multiple tools, the `executor.py` script was developed with the following features:

#### 2.1 Design Goals

- **Batch Processing:** Execute all scenarios for a selected tool automatically
- **Error Recovery:** Handle failures gracefully and continue processing
- **Output Standardization:** Move outputs to consistent locations
- **Progress Tracking:** Report execution status for each scenario
- **Interactive Interface:** User-friendly menu for tool selection

#### 2.2 Implementation Strategy

```python
# Key components of executor.py:

1. Tool-specific functions (run_intellimerge, run_fstmerge, etc.)
   - Iterate through scenarios 1-39
   - Build appropriate command for each scenario
   - Handle tool-specific quirks (nested paths, output locations)

2. Environment management
   - Configure JAVA_HOME per tool requirements
   - Set LD_LIBRARY_PATH for native libraries
   - Manage classpath for Java tools

3. Post-processing
   - Relocate outputs to standardized directories
   - Clean up temporary/nested structures
   - Report success/failure statistics

4. Error handling
   - Try/catch for subprocess failures
   - Fallback modes (structured → unstructured for JDime)
   - Detailed error logging
```

#### 2.3 Execution Flow

```
User Selection → Tool Configuration → Scenario Loop
    ↓                    ↓                   ↓
[Menu]           [Paths & Env]      [For i in 1..39]
    ↓                    ↓                   ↓
Tool Function → Execute Command → Post-Process
    ↓                    ↓                   ↓
Run All          Capture Output      Move Files
Scenarios        Handle Errors       Clean Dirs
    ↓                    ↓                   ↓
    └─────────→ Summary Report ←────────────┘
```

### Phase 3: Scientific Evaluation Framework

After generating merge outputs, a comprehensive evaluation framework was developed to scientifically assess tool performance.

#### 3.1 Evaluation Metrics

The framework implements multiple rigorous metrics following software engineering research standards:

**Core Metrics:**
- **Precision:** Ratio of correct lines in output to total output lines
- **Recall:** Ratio of correct lines in output to expected lines
- **F1-Score:** Harmonic mean of precision and recall
- **Accuracy:** Overall correctness percentage

**Quality Metrics:**
- **Syntactic Correctness:** Java compilation success
- **Structural Integrity:** AST-level correctness
- **Lexical Similarity:** Token-level comparison
- **Semantic Similarity:** Meaning preservation analysis

**Classification System:**
- Perfect (100%)
- Excellent (≥95%)
- Good (≥85%)
- Acceptable (≥70%)
- Poor (≥50%)
- Failed (<50%)

#### 3.2 Evaluation Process

```python
# Evaluation pipeline:

1. Load expected outputs (ground truth)
2. Load actual tool outputs (test results)
3. For each scenario:
   a. Normalize whitespace and formatting
   b. Compute line-level differences
   c. Calculate precision, recall, F1
   d. Analyze syntax and structure
   e. Classify quality level
   f. Identify error patterns
4. Aggregate metrics per tool
5. Perform statistical comparisons
6. Generate comprehensive reports
```

#### 3.3 Implementation Components

**merge_evaluation_tool.py:**
- Core evaluation engine
- Metric calculation algorithms
- File comparison logic
- Statistical analysis functions
- Report generation

**run_evaluation.py:**
- Orchestration script
- Directory structure validation
- Tool auto-detection
- Batch evaluation execution
- Summary report generation

**scientific_report_generator.py:**
- Academic-standard report formatting
- Statistical significance testing
- Comparative analysis tables
- Methodology documentation
- Results visualization data

#### 3.4 Evaluation Outputs

The evaluation generates multiple output formats:

```
evaluation_results/scientific_evaluation/
├── tools_comparison.json          # Comparative analysis
├── scientific_merge_tools_evaluation.md  # Academic report
├── FSTMerge/
│   ├── evaluation_report.json    # Detailed metrics
│   └── scenario_metrics.csv      # Per-scenario data
├── IntelliMerge/
│   ├── evaluation_report.json
│   └── scenario_metrics.csv
└── JDime/
    ├── evaluation_report.json
    └── scenario_metrics.csv
```

### Phase 4: Results and Analysis

#### 4.1 Key Findings

The evaluation revealed:

1. **Performance Variability:** Significant differences between tools
2. **Scenario Complexity Impact:** Some tools excel with simple scenarios
3. **Structural vs Line-based:** Trade-offs between merge strategies
4. **Reliability Patterns:** Consistency across scenario types
5. **Error Categories:** Common failure modes identified

#### 4.2 Statistical Validation

- Mann-Whitney U tests for pairwise comparisons
- Effect size calculations (Cohen's d)
- Confidence intervals for metrics
- Distribution analysis of quality classifications

#### 4.3 Practical Implications

Results inform tool selection based on:
- Project characteristics (size, complexity)
- Language features used
- Team expertise level
- Merge frequency and patterns

## 🚀 Usage Guide

## 🚀 Usage Guide

### Prerequisites

- Python 3.8+
- Java 8 and Java 11
- Required Python packages (install via `pip install -r requirements.txt`)

### Running Individual Merge Tools

#### FSTMerge

```bash
java -jar ./merge_tools/FSTMerge/featurehouse_20220107.jar \
  --expression /workspaces/Pesquisa-cientifica/scenarios_base/FSTMerge/scenario_1/merge.expression \
  --base-directory /workspaces/Pesquisa-cientifica/scenarios_base/FSTMerge/scenario_1
```

### IntelliMerge

```bash
java -jar ./merge_tools/IntelliMerge/IntelliMerge-1.0.9-all.jar \
  -d "/workspaces/Pesquisa-cientifica/scenarios_base/IntelliMerge/scenario_12/left" \
     "/workspaces/Pesquisa-cientifica/scenarios_base/IntelliMerge/scenario_12/base" \
     "/workspaces/Pesquisa-cientifica/scenarios_base/IntelliMerge/scenario_12/right" \
  -o "/workspaces/Pesquisa-cientifica/output/IntelliMerge/scenario_12"
```

### AutoMerge

AutoMerge requires Java 8-11. Example with structured mode:

```bash
./java_dependencies/java-versions/jdk-11.0.2/bin/java \
  -cp ./merge_tools/AutoMerge/AutoMerge.jar:libs/activation-1.1.1.jar \
  de.fosd.jdime.Main \
  -m structured \
  -f \
  -o /workspaces/Pesquisa-cientifica/output/AutoMerge/scenario_1.java \
  /workspaces/Pesquisa-cientifica/scenarios_base/AutoMerge/scenario_1/base/Person.java \
  /workspaces/Pesquisa-cientifica/scenarios_base/AutoMerge/scenario_1/left/Person.java \
  /workspaces/Pesquisa-cientifica/scenarios_base/AutoMerge/scenario_1/right/Person.java
```

Example with line-based mode:

```bash
java -Djava.library.path=/usr/lib/x86_64-linux-gnu/ \
  -cp ./merge_tools/AutoMerge/AutoMerge.jar:libs/activation-1.1.1.jar \
  de.fosd.jdime.Main \
  -m linebased \
  -f \
  -o /workspaces/Pesquisa-cientifica/output/AutoMerge/output.java \
  /workspaces/Pesquisa-cientifica/scenarios_base/AutoMerge/base/SimpleClass.java \
  /workspaces/Pesquisa-cientifica/scenarios_base/AutoMerge/left/SimpleClass.java \
  /workspaces/Pesquisa-cientifica/scenarios_base/AutoMerge/right/SimpleClass.java
```

### KDiff3

For GUI environments:

```bash
kdiff3 \
  /workspaces/Pesquisa-cientifica/scenarios_base/KDiff3/base/SimpleClass.java \
  /workspaces/Pesquisa-cientifica/scenarios_base/KDiff3/left/SimpleClass.java \
  /workspaces/Pesquisa-cientifica/scenarios_base/KDiff3/right/SimpleClass.java \
  -m --batch -o /workspaces/Pesquisa-cientifica/output/KDiff3/output.java
```

### JDime

```bash
JAVA_HOME=/workspaces/Pesquisa-cientifica/java_dependencies/java-versions/jdk8u392-b08 \
  ./merge_tools/JDime/jdime/build/install/JDime/bin/JDime \
  --mode structured \
  --output ./output/JDime/scenario_12 \
  ./scenarios_base/JDime/scenario_12/left \
  ./scenarios_base/JDime/scenario_12/base \
  ./scenarios_base/JDime/scenario_12/right
```

## Running Scripts

All Python scripts are located in the `scripts/` directory:

```bash
# Run executor menu
python scripts/executor.py
```

### Running Complete Evaluation

#### Quick Start

```bash
# 1. Check data availability
python scripts/run_evaluation.py --check-only

# 2. Run evaluation for all available tools
python scripts/run_evaluation.py

# 3. Generate scientific report
python scripts/scientific_report_generator.py
```

#### Advanced Options

```bash
# Evaluate specific tools only
python scripts/run_evaluation.py --tools IntelliMerge JDime

# Custom output directory
python scripts/run_evaluation.py --output-dir my_results

# Verbose logging
python scripts/run_evaluation.py --verbose

# Generate summary from existing results
python scripts/run_evaluation.py --summary-only
```

#### Complete Demonstration

```bash
# Run full demonstration with explanations
python scripts/demo_complete_evaluation.py
```

This script provides an interactive walkthrough of:
1. Data structure verification
2. Complete evaluation execution
3. Scientific report generation
4. Results summary and analysis

## 📊 Understanding the Results

### Evaluation Report Structure

Each tool receives:

**JSON Report (`evaluation_report.json`):**
- Overall metrics (precision, recall, F1-score)
- Success rate and reliability score
- Quality distribution statistics
- Common error patterns
- Per-scenario detailed metrics

**CSV Data (`scenario_metrics.csv`):**
- Tabular format for statistical analysis
- One row per scenario with all metrics
- Suitable for importing into R, SPSS, or Excel

**Comparative Analysis (`tools_comparison.json`):**
- Performance ranking across all tools
- Statistical significance tests
- Quality distribution comparisons
- Strengths and weaknesses analysis

### Scientific Report

The generated Markdown report includes:

1. **Abstract & Introduction:** Research context and objectives
2. **Methodology:** Detailed evaluation approach
3. **Results:** Comprehensive tables and statistics
4. **Statistical Analysis:** Significance tests and effect sizes
5. **Discussion:** Interpretation of findings
6. **Threats to Validity:** Limitations and biases
7. **Reproducibility:** Steps to replicate the study

## 📈 Visualization

Generate graphs for presentation:

```bash
# Individual metric graphs
python scripts/graphs/accuracy_graph.py
python scripts/graphs/f1_score_graph.py
python scripts/graphs/recall_graph.py

# Combined comparison
python scripts/graphs/combined_metrics_graph.py
```

## 🔧 Development Notes

### Adding New Scenarios

1. Create scenario directories in `scenarios_base/[Tool]/scenario_N/`
2. Include `base/`, `left/`, and `right/` subdirectories
3. Add expected output to `output/[Tool]/expected/scenario_N/`
4. Update scenario count in executor functions if needed

### Adding New Tools

1. Add tool binaries to `merge_tools/[NewTool]/`
2. Create function in `executor.py` following existing patterns
3. Add tool option to menu in `main()` function
4. Create corresponding scenario directories
5. Test with a few scenarios before full batch

### Extending Metrics

To add custom evaluation metrics:

1. Update `ScenarioMetrics` dataclass in `evaluation_config.py`
2. Implement calculation logic in `merge_evaluation_tool.py`
3. Update report generation in `scientific_report_generator.py`
4. Add visualization if needed in `graphs/` directory

## 📚 Research Applications

This framework is suitable for:

- **Academic Papers:** Empirical software engineering research
- **Master's/PhD Theses:** Comparative tool evaluation studies
- **Technical Reports:** Tool selection justification
- **Tool Development:** Benchmark for new merge algorithms
- **Educational Material:** Teaching merge concepts

### Citation

If you use this framework in your research, please cite:

```bibtex
@misc{merge_tools_evaluation,
  title={Scientific Evaluation Framework for Software Merge Tools},
  author={[Your Name]},
  year={2025},
  howpublished={\url{https://github.com/MateusMunaro/Pesquisa-cientifica}}
}
```

## 🐛 Troubleshooting

### Common Issues

**Issue:** Java version conflicts
```bash
# Solution: Verify JAVA_HOME is set correctly
echo $JAVA_HOME
# Update in executor.py if needed
```

**Issue:** Missing JavaFX libraries for AutoMerge
```bash
# Solution: Libraries are auto-downloaded, ensure wget/unzip available
sudo apt-get install wget unzip
```

**Issue:** JDime scenarios failing
```bash
# Solution: Tool falls back to unstructured mode automatically
# Check logs in merge_evaluation.log for details
```

**Issue:** Permission denied on executables
```bash
# Solution: Make scripts executable
chmod +x merge_tools/JDime/jdime/build/install/JDime/bin/JDime
```

**Issue:** Output directories not found
```bash
# Solution: Create expected output structure
mkdir -p output/{FSTMerge,IntelliMerge,JDime}/{scenarios,expected}
```

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- Additional merge tools (git-merge, Spork, etc.)
- More evaluation metrics (complexity, readability)
- Language support beyond Java
- Performance benchmarking
- GUI for result exploration

## 📄 License

This research project is available for academic and educational use. Please contact the author for commercial applications.

## 👥 Authors

- **Mateus Munaro** - Initial research and implementation
- Research conducted as part of [Institution/Program Name]

## 🙏 Acknowledgments

- Tool developers for making their software available
- Academic community for evaluation methodology standards
- Open-source contributors to dependencies

## 📞 Contact

For questions, suggestions, or collaboration opportunities:
- GitHub: [@MateusMunaro](https://github.com/MateusMunaro)
- Email: [MateusSouza2@edu.unisinis.br]

---

**Last Updated:** November 2025
**Version:** 1.0.0
**Status:** Active Research Project
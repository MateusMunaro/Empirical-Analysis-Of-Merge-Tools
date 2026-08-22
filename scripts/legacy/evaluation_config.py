"""
Scientific Merge Tool Evaluation Configuration
==============================================

This module contains configuration settings and constants for the merge tool evaluation framework.
It defines the evaluation parameters, quality thresholds, and research methodology settings
following best practices in empirical software engineering research.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Any

# Version information
FRAMEWORK_VERSION = "1.0.0"
FRAMEWORK_NAME = "Scientific Merge Tool Evaluation Framework"

# Research configuration
@dataclass
class ResearchConfig:
    """Configuration for research methodology and evaluation parameters"""
    
    # Quality thresholds (based on empirical software engineering standards)
    PERFECT_THRESHOLD = 1.0         # 100% match
    EXCELLENT_THRESHOLD = 0.95      # >= 95%
    GOOD_THRESHOLD = 0.85          # >= 85%
    ACCEPTABLE_THRESHOLD = 0.70     # >= 70%
    POOR_THRESHOLD = 0.50          # >= 50%
    # Below 50% is considered FAILED
    
    # Confidence thresholds
    HIGH_CONFIDENCE = 0.9
    MEDIUM_CONFIDENCE = 0.7
    LOW_CONFIDENCE = 0.5
    
    # Statistical significance parameters
    MIN_SAMPLE_SIZE = 10
    ALPHA_LEVEL = 0.05
    
    # File processing
    SUPPORTED_EXTENSIONS = ['.java', '.py', '.cpp', '.c', '.h', '.hpp', '.js', '.ts']
    DEFAULT_ENCODING = 'utf-8'
    FALLBACK_ENCODING = 'latin-1'
    
    # Performance thresholds
    SUCCESS_RATE_THRESHOLD = 0.8    # 80% success rate considered good
    RELIABILITY_THRESHOLD = 0.75    # 75% reliability considered acceptable
    CONSISTENCY_THRESHOLD = 0.7     # 70% consistency considered acceptable


# Error classification system
class ErrorType(Enum):
    """Classification of merge errors for systematic analysis"""
    
    # Structural errors
    UNRESOLVED_CONFLICTS = "unresolved_conflicts"
    SYNTAX_ERRORS = "syntax_errors"
    BRACKET_MISMATCH = "bracket_mismatch"
    
    # Content errors
    MISSING_CONTENT = "missing_content"
    EXTRA_CONTENT = "extra_content"
    INCORRECT_CONTENT = "incorrect_content"
    
    # Semantic errors
    LOGIC_ERRORS = "logic_errors"
    TYPE_ERRORS = "type_errors"
    REFERENCE_ERRORS = "reference_errors"
    
    # Tool-specific errors
    TOOL_FAILURE = "tool_failure"
    TIMEOUT = "timeout"
    MEMORY_ERROR = "memory_error"
    
    # Evaluation errors
    FILE_NOT_FOUND = "file_not_found"
    ENCODING_ERROR = "encoding_error"
    PROCESSING_ERROR = "processing_error"


# Metric weights for composite scoring
METRIC_WEIGHTS = {
    'f1_score': 0.4,
    'precision': 0.2,
    'recall': 0.2,
    'structural_integrity': 0.1,
    'syntactic_correctness': 0.1
}

# Quality assurance parameters
QUALITY_ASSURANCE = {
    'min_file_size_bytes': 10,          # Minimum file size to consider valid
    'max_file_size_mb': 10,             # Maximum file size to process
    'max_processing_time_seconds': 30,   # Timeout for individual file processing
    'checksum_validation': True,         # Enable checksum validation
    'duplicate_detection': True,         # Detect duplicate scenarios
    'outlier_detection': True           # Detect statistical outliers
}

# Research methodology settings
RESEARCH_METHODOLOGY = {
    'evaluation_approach': 'quantitative',
    'comparison_method': 'pairwise',
    'statistical_tests': ['mannwhitney', 'wilcoxon', 'kruskal'],
    'effect_size_measures': ['cohens_d', 'cliff_delta'],
    'multiple_comparison_correction': 'bonferroni',
    'confidence_intervals': True,
    'bootstrap_iterations': 1000
}

# Output formatting configuration
OUTPUT_CONFIG = {
    'decimal_places': 4,
    'percentage_format': '.2%',
    'scientific_notation_threshold': 0.0001,
    'table_format': 'grid',
    'json_indent': 2,
    'csv_delimiter': ',',
    'include_metadata': True,
    'include_timestamps': True
}

# Validation rules for scientific rigor
VALIDATION_RULES = {
    'require_baseline_comparison': True,
    'require_statistical_significance': True,
    'require_effect_size_reporting': True,
    'require_confidence_intervals': True,
    'require_multiple_metrics': True,
    'require_error_analysis': True,
    'require_reproducibility_info': True
}

# Documentation standards
DOCUMENTATION_STANDARDS = {
    'include_methodology_description': True,
    'include_threats_to_validity': True,
    'include_limitations_discussion': True,
    'include_related_work_comparison': True,
    'include_dataset_description': True,
    'citation_format': 'apa',
    'appendix_raw_data': True
}

# Tool-specific configurations
TOOL_SPECIFIC_CONFIG = {
    'IntelliMerge': {
        'timeout_multiplier': 1.0,
        'memory_limit_mb': 512,
        'expected_output_patterns': ['*.java'],
        'known_limitations': ['large_files', 'complex_inheritance']
    },
    'JDime': {
        'timeout_multiplier': 1.5,
        'memory_limit_mb': 1024,
        'expected_output_patterns': ['*.java'],
        'known_limitations': ['annotation_handling', 'generic_types']
    },
    'FSTMerge': {
        'timeout_multiplier': 2.0,
        'memory_limit_mb': 256,
        'expected_output_patterns': ['*.java'],
        'known_limitations': ['whitespace_handling', 'comment_preservation']
    }
}

# Experimental design parameters
EXPERIMENTAL_DESIGN = {
    'randomization': False,  # Scenarios are predefined
    'blinding': False,       # Tools are known
    'control_group': 'expected_results',
    'treatment_groups': 'merge_tools',
    'repeated_measures': False,
    'counterbalancing': False,
    'power_analysis_required': True,
    'sample_size_justification_required': True
}

# Threat to validity considerations
THREATS_TO_VALIDITY = {
    'construct_validity': [
        'metric_selection_bias',
        'measurement_error',
        'incomplete_coverage'
    ],
    'internal_validity': [
        'selection_bias',
        'instrumentation_effects',
        'maturation_effects'
    ],
    'external_validity': [
        'population_generalizability',
        'ecological_generalizability',
        'temporal_generalizability'
    ],
    'conclusion_validity': [
        'statistical_power',
        'alpha_inflation',
        'assumption_violations'
    ]
}

# Reproducibility requirements
REPRODUCIBILITY_REQUIREMENTS = {
    'version_control_info': True,
    'environment_specification': True,
    'dependency_versions': True,
    'random_seed_specification': True,
    'execution_parameters': True,
    'data_provenance': True,
    'analysis_scripts': True,
    'raw_results_preservation': True
}

def get_quality_threshold(quality_level: str) -> float:
    """Get the threshold value for a quality level"""
    config = ResearchConfig()
    thresholds = {
        'perfect': config.PERFECT_THRESHOLD,
        'excellent': config.EXCELLENT_THRESHOLD,
        'good': config.GOOD_THRESHOLD,
        'acceptable': config.ACCEPTABLE_THRESHOLD,
        'poor': config.POOR_THRESHOLD
    }
    return thresholds.get(quality_level.lower(), 0.0)

def validate_configuration() -> List[str]:
    """Validate configuration settings for consistency"""
    errors = []
    
    config = ResearchConfig()
    
    # Check threshold ordering
    thresholds = [
        config.PERFECT_THRESHOLD,
        config.EXCELLENT_THRESHOLD,
        config.GOOD_THRESHOLD,
        config.ACCEPTABLE_THRESHOLD,
        config.POOR_THRESHOLD
    ]
    
    if not all(thresholds[i] >= thresholds[i+1] for i in range(len(thresholds)-1)):
        errors.append("Quality thresholds are not in descending order")
    
    # Check metric weights sum to 1.0
    if abs(sum(METRIC_WEIGHTS.values()) - 1.0) > 0.001:
        errors.append(f"Metric weights sum to {sum(METRIC_WEIGHTS.values())}, should be 1.0")
    
    # Check supported extensions
    if not config.SUPPORTED_EXTENSIONS:
        errors.append("No supported file extensions specified")
    
    return errors

# Default configuration instance
DEFAULT_CONFIG = ResearchConfig()

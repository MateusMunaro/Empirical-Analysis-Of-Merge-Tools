#!/usr/bin/env python3
"""
Merge Tool Evaluation Framework
===============================

A comprehensive tool for evaluating and comparing merge tool performance
in software development scenarios. This framework provides rigorous metrics
following scientific evaluation standards for empirical software engineering research.

Author: Research Team
Version: 1.0.0
License: Academic Research License
"""

import os
import sys
import json
import argparse
import logging
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import defaultdict
import difflib
import re
import statistics
import numpy as np
from enum import Enum

# Repository root (one level above /scripts). Run all relative paths from here.
REPO_ROOT = Path(__file__).resolve().parent.parent
os.chdir(REPO_ROOT)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('merge_evaluation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class MergeQuality(Enum):
    """Enumeration for merge quality classification"""
    PERFECT = "perfect"           # 100% match
    EXCELLENT = "excellent"       # >= 95%
    GOOD = "good"                # >= 85%
    ACCEPTABLE = "acceptable"     # >= 70%
    POOR = "poor"                # >= 50%
    FAILED = "failed"            # < 50%


@dataclass
class ScenarioMetrics:
    """Data class for storing detailed metrics of a single scenario"""
    scenario_id: str
    tool_name: str
    file_name: str
    
    # Core Metrics
    precision: float
    recall: float
    f1_score: float
    accuracy: float
    
    # Content Analysis
    total_lines_expected: int
    total_lines_actual: int
    lines_correctly_merged: int
    lines_missing: int
    lines_extra: int
    
    # Structural Analysis
    syntactic_correctness: bool
    compilation_status: str
    structural_integrity: float
    
    # Similarity Metrics
    lexical_similarity: float
    semantic_similarity: float
    edit_distance: int
    
    # Quality Classification
    quality_class: MergeQuality
    confidence_score: float
    
    # Error Analysis
    error_types: List[str]
    critical_errors: int
    minor_errors: int
    
    # Metadata
    processing_time: float
    file_size_bytes: int
    checksum_expected: str
    checksum_actual: str


@dataclass
class ToolEvaluationReport:
    """Comprehensive evaluation report for a single merge tool"""
    tool_name: str
    evaluation_timestamp: str
    total_scenarios: int
    
    # Aggregate Metrics
    overall_precision: float
    overall_recall: float
    overall_f1_score: float
    overall_accuracy: float
    
    # Quality Distribution
    perfect_merges: int
    excellent_merges: int
    good_merges: int
    acceptable_merges: int
    poor_merges: int
    failed_merges: int
    
    # Statistical Analysis
    precision_std: float
    recall_std: float
    f1_std: float
    median_f1: float
    iqr_f1: Tuple[float, float]
    
    # Performance Analysis
    success_rate: float
    reliability_score: float
    consistency_score: float
    
    # Detailed Results
    scenario_metrics: List[ScenarioMetrics]
    
    # Error Analysis
    common_error_patterns: List[str]
    failure_analysis: Dict[str, int]


class TextNormalizer:
    """Advanced text normalization for fair comparison"""
    
    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """Normalize whitespace while preserving structure"""
        lines = text.splitlines()
        normalized_lines = []
        
        for line in lines:
            # Preserve indentation structure but normalize spaces
            leading_spaces = len(line) - len(line.lstrip())
            content = ' '.join(line.strip().split())
            if content:  # Skip empty lines
                normalized_lines.append(' ' * leading_spaces + content)
        
        return '\n'.join(normalized_lines)
    
    @staticmethod
    def remove_merge_artifacts(text: str) -> str:
        """Remove common merge conflict markers and artifacts"""
        # Remove conflict markers
        conflict_patterns = [
            r'^<<<<<<< .*\n',
            r'^======= ?\n',
            r'^>>>>>>> .*\n',
            r'^||||||| .*\n'
        ]
        
        for pattern in conflict_patterns:
            text = re.sub(pattern, '', text, flags=re.MULTILINE)
        
        return text
    
    @staticmethod
    def normalize_java_code(text: str) -> str:
        """Java-specific normalization"""
        # Remove extra whitespace in class/method declarations
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\s*{\s*', ' {\n', text)
        text = re.sub(r'\s*}\s*', '\n}\n', text)
        text = re.sub(r';\s*', ';\n', text)
        
        return text


class MetricsCalculator:
    """Advanced metrics calculation with multiple evaluation approaches"""
    
    def __init__(self):
        self.normalizer = TextNormalizer()
    
    def calculate_core_metrics(self, expected: List[str], actual: List[str]) -> Dict[str, float]:
        """Calculate precision, recall, F1-score, and accuracy"""
        expected_set = set(expected)
        actual_set = set(actual)
        
        true_positives = len(expected_set & actual_set)
        false_positives = len(actual_set - expected_set)
        false_negatives = len(expected_set - actual_set)
        
        # Precision: TP / (TP + FP)
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
        
        # Recall: TP / (TP + FN)
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
        
        # F1-Score: 2 * (precision * recall) / (precision + recall)
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        # Accuracy (considering line-by-line comparison)
        total_lines = max(len(expected), len(actual))
        if total_lines == 0:
            accuracy = 1.0
        else:
            correct_lines = sum(1 for i in range(min(len(expected), len(actual))) 
                              if expected[i] == actual[i])
            accuracy = correct_lines / total_lines
        
        return {
            'precision': precision,
            'recall': recall,
            'f1_score': f1_score,
            'accuracy': accuracy,
            'true_positives': true_positives,
            'false_positives': false_positives,
            'false_negatives': false_negatives
        }
    
    def calculate_similarity_metrics(self, expected: str, actual: str) -> Dict[str, float]:
        """Calculate various similarity metrics"""
        # Lexical similarity using SequenceMatcher
        lexical_sim = difflib.SequenceMatcher(None, expected, actual).ratio()
        
        # Edit distance (Levenshtein)
        def levenshtein_distance(s1: str, s2: str) -> int:
            if len(s1) < len(s2):
                return levenshtein_distance(s2, s1)
            
            if len(s2) == 0:
                return len(s1)
            
            previous_row = list(range(len(s2) + 1))
            for i, c1 in enumerate(s1):
                current_row = [i + 1]
                for j, c2 in enumerate(s2):
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (c1 != c2)
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row
            
            return previous_row[-1]
        
        edit_distance = levenshtein_distance(expected, actual)
        
        # Normalized edit distance
        max_len = max(len(expected), len(actual))
        normalized_edit_distance = 1.0 - (edit_distance / max_len) if max_len > 0 else 1.0
        
        return {
            'lexical_similarity': lexical_sim,
            'normalized_edit_distance': normalized_edit_distance,
            'edit_distance': edit_distance
        }
    
    def analyze_structural_integrity(self, content: str, file_extension: str = '.java') -> Dict[str, Any]:
        """Analyze structural integrity of the merged content"""
        if file_extension.lower() == '.java':
            return self._analyze_java_structure(content)
        else:
            return self._analyze_generic_structure(content)
    
    def _analyze_java_structure(self, content: str) -> Dict[str, Any]:
        """Java-specific structural analysis"""
        issues = []
        
        # Check for basic Java structure
        has_class = bool(re.search(r'\bclass\s+\w+', content))
        if not has_class:
            issues.append("Missing class declaration")
        
        # Check bracket balance
        open_braces = content.count('{')
        close_braces = content.count('}')
        bracket_balanced = (open_braces == close_braces)
        if not bracket_balanced:
            issues.append(f"Unbalanced braces: {open_braces} open, {close_braces} close")
        
        # Check for conflict markers
        conflict_markers = len(re.findall(r'<{7}|={7}|>{7}', content))
        if conflict_markers > 0:
            issues.append(f"Contains {conflict_markers} conflict markers")
        
        # Basic syntax check
        has_semicolons = ';' in content
        has_methods = bool(re.search(r'\b(public|private|protected)?\s*(static)?\s*\w+\s+\w+\s*\(', content))
        
        structural_score = 1.0
        if not has_class:
            structural_score -= 0.3
        if not bracket_balanced:
            structural_score -= 0.4
        if conflict_markers > 0:
            structural_score -= 0.2
        if not has_semicolons and has_methods:
            structural_score -= 0.1
        
        return {
            'structural_integrity': max(0.0, structural_score),
            'syntactic_correctness': len(issues) == 0,
            'issues': issues,
            'has_conflict_markers': conflict_markers > 0
        }
    
    def _analyze_generic_structure(self, content: str) -> Dict[str, Any]:
        """Generic structural analysis for non-Java files"""
        issues = []
        
        # Check for conflict markers
        conflict_markers = len(re.findall(r'<{7}|={7}|>{7}', content))
        if conflict_markers > 0:
            issues.append(f"Contains {conflict_markers} conflict markers")
        
        structural_score = 1.0
        if conflict_markers > 0:
            structural_score -= 0.5
        
        return {
            'structural_integrity': max(0.0, structural_score),
            'syntactic_correctness': conflict_markers == 0,
            'issues': issues,
            'has_conflict_markers': conflict_markers > 0
        }


class ScenarioEvaluator:
    """Evaluates individual merge scenarios"""
    
    def __init__(self):
        self.metrics_calculator = MetricsCalculator()
        self.normalizer = TextNormalizer()
    
    def evaluate_scenario(self, 
                         expected_file: Path, 
                         actual_file: Path, 
                         scenario_id: str, 
                         tool_name: str) -> ScenarioMetrics:
        """Evaluate a single merge scenario"""
        start_time = datetime.now()
        
        try:
            # Read files
            expected_content = self._read_file_safely(expected_file)
            actual_content = self._read_file_safely(actual_file)
            
            # Normalize content
            expected_normalized = self.normalizer.normalize_whitespace(
                self.normalizer.remove_merge_artifacts(expected_content)
            )
            actual_normalized = self.normalizer.normalize_whitespace(
                self.normalizer.remove_merge_artifacts(actual_content)
            )
            
            # Convert to line lists for analysis
            expected_lines = [line.strip() for line in expected_normalized.splitlines() if line.strip()]
            actual_lines = [line.strip() for line in actual_normalized.splitlines() if line.strip()]
            
            # Calculate core metrics
            core_metrics = self.metrics_calculator.calculate_core_metrics(expected_lines, actual_lines)
            
            # Calculate similarity metrics
            similarity_metrics = self.metrics_calculator.calculate_similarity_metrics(
                expected_normalized, actual_normalized
            )
            
            # Analyze structural integrity
            structural_analysis = self.metrics_calculator.analyze_structural_integrity(
                actual_content, expected_file.suffix
            )
            
            # Determine quality classification
            quality_class = self._classify_quality(core_metrics['f1_score'])
            
            # Error analysis
            error_analysis = self._analyze_errors(expected_lines, actual_lines, structural_analysis)
            
            # Calculate checksums
            expected_checksum = hashlib.md5(expected_content.encode()).hexdigest()
            actual_checksum = hashlib.md5(actual_content.encode()).hexdigest()
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return ScenarioMetrics(
                scenario_id=scenario_id,
                tool_name=tool_name,
                file_name=actual_file.name,
                
                # Core Metrics
                precision=core_metrics['precision'],
                recall=core_metrics['recall'],
                f1_score=core_metrics['f1_score'],
                accuracy=core_metrics['accuracy'],
                
                # Content Analysis
                total_lines_expected=len(expected_lines),
                total_lines_actual=len(actual_lines),
                lines_correctly_merged=core_metrics['true_positives'],
                lines_missing=core_metrics['false_negatives'],
                lines_extra=core_metrics['false_positives'],
                
                # Structural Analysis
                syntactic_correctness=structural_analysis['syntactic_correctness'],
                compilation_status="unknown",  # Would require actual compilation
                structural_integrity=structural_analysis['structural_integrity'],
                
                # Similarity Metrics
                lexical_similarity=similarity_metrics['lexical_similarity'],
                semantic_similarity=similarity_metrics['normalized_edit_distance'],
                edit_distance=similarity_metrics['edit_distance'],
                
                # Quality Classification
                quality_class=quality_class,
                confidence_score=self._calculate_confidence(core_metrics, similarity_metrics),
                
                # Error Analysis
                error_types=error_analysis['error_types'],
                critical_errors=error_analysis['critical_errors'],
                minor_errors=error_analysis['minor_errors'],
                
                # Metadata
                processing_time=processing_time,
                file_size_bytes=actual_file.stat().st_size if actual_file.exists() else 0,
                checksum_expected=expected_checksum,
                checksum_actual=actual_checksum
            )
            
        except Exception as e:
            logger.error(f"Error evaluating scenario {scenario_id}: {str(e)}")
            return self._create_error_metrics(scenario_id, tool_name, str(e))
    
    def _read_file_safely(self, file_path: Path) -> str:
        """Safely read file with proper encoding handling"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
        except FileNotFoundError:
            logger.warning(f"File not found: {file_path}")
            return ""
    
    def _classify_quality(self, f1_score: float) -> MergeQuality:
        """Classify merge quality based on F1 score"""
        if f1_score >= 1.0:
            return MergeQuality.PERFECT
        elif f1_score >= 0.95:
            return MergeQuality.EXCELLENT
        elif f1_score >= 0.85:
            return MergeQuality.GOOD
        elif f1_score >= 0.70:
            return MergeQuality.ACCEPTABLE
        elif f1_score >= 0.50:
            return MergeQuality.POOR
        else:
            return MergeQuality.FAILED
    
    def _calculate_confidence(self, core_metrics: Dict, similarity_metrics: Dict) -> float:
        """Calculate confidence score for the evaluation"""
        # Confidence based on consistency between different metrics
        f1 = core_metrics['f1_score']
        similarity = similarity_metrics['lexical_similarity']
        edit_distance = similarity_metrics['normalized_edit_distance']
        
        # Calculate variance between metrics
        metrics = [f1, similarity, edit_distance]
        variance = statistics.variance(metrics) if len(metrics) > 1 else 0
        
        # Lower variance means higher confidence
        confidence = 1.0 - min(variance, 1.0)
        return confidence
    
    def _analyze_errors(self, expected: List[str], actual: List[str], structural: Dict) -> Dict:
        """Analyze types of errors in the merge"""
        error_types = []
        critical_errors = 0
        minor_errors = 0
        
        # Structural errors
        if structural['has_conflict_markers']:
            error_types.append("unresolved_conflicts")
            critical_errors += 1
        
        if not structural['syntactic_correctness']:
            error_types.append("syntax_errors")
            critical_errors += 1
        
        # Content errors
        missing_lines = len(set(expected) - set(actual))
        extra_lines = len(set(actual) - set(expected))
        
        if missing_lines > 0:
            error_types.append("missing_content")
            if missing_lines > len(expected) * 0.1:  # More than 10% missing
                critical_errors += missing_lines
            else:
                minor_errors += missing_lines
        
        if extra_lines > 0:
            error_types.append("extra_content")
            minor_errors += extra_lines
        
        return {
            'error_types': error_types,
            'critical_errors': critical_errors,
            'minor_errors': minor_errors
        }
    
    def _create_error_metrics(self, scenario_id: str, tool_name: str, error_msg: str) -> ScenarioMetrics:
        """Create metrics object for failed evaluations"""
        return ScenarioMetrics(
            scenario_id=scenario_id,
            tool_name=tool_name,
            file_name="error",
            precision=0.0,
            recall=0.0,
            f1_score=0.0,
            accuracy=0.0,
            total_lines_expected=0,
            total_lines_actual=0,
            lines_correctly_merged=0,
            lines_missing=0,
            lines_extra=0,
            syntactic_correctness=False,
            compilation_status="error",
            structural_integrity=0.0,
            lexical_similarity=0.0,
            semantic_similarity=0.0,
            edit_distance=0,
            quality_class=MergeQuality.FAILED,
            confidence_score=0.0,
            error_types=[f"evaluation_error: {error_msg}"],
            critical_errors=1,
            minor_errors=0,
            processing_time=0.0,
            file_size_bytes=0,
            checksum_expected="",
            checksum_actual=""
        )


class ToolEvaluationFramework:
    """Main framework for evaluating merge tools"""
    
    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Path("evaluation_results")
        self.output_dir.mkdir(exist_ok=True)
        
        self.evaluator = ScenarioEvaluator()
        logger.info(f"Initialized evaluation framework with output directory: {self.output_dir}")
    
    def evaluate_tool(self, 
                     tool_name: str,
                     scenarios_dir: Path,
                     expected_dir: Path,
                     file_extensions: List[str] = None) -> ToolEvaluationReport:
        """Evaluate a single merge tool across all scenarios"""
        
        logger.info(f"Starting evaluation of tool: {tool_name}")
        file_extensions = file_extensions or ['.java', '.py', '.cpp', '.c', '.h']
        
        scenario_metrics = []
        start_time = datetime.now()
        
        # Find all scenarios
        scenario_dirs = sorted([d for d in scenarios_dir.iterdir() if d.is_dir()])
        
        for scenario_dir in scenario_dirs:
            scenario_id = scenario_dir.name
            expected_scenario_dir = expected_dir / scenario_id
            
            if not expected_scenario_dir.exists():
                logger.warning(f"Expected directory not found for scenario: {scenario_id}")
                continue
            
            # Find files to evaluate
            for actual_file in scenario_dir.rglob("*"):
                if actual_file.is_file() and actual_file.suffix in file_extensions:
                    # Find corresponding expected file
                    expected_file = self._find_expected_file(actual_file, scenario_dir, expected_scenario_dir)
                    
                    if expected_file and expected_file.exists():
                        metrics = self.evaluator.evaluate_scenario(
                            expected_file, actual_file, scenario_id, tool_name
                        )
                        scenario_metrics.append(metrics)
                        logger.debug(f"Evaluated {scenario_id}/{actual_file.name}: F1={metrics.f1_score:.3f}")
        
        # Generate comprehensive report
        report = self._generate_tool_report(tool_name, scenario_metrics, start_time)
        
        # Save detailed results
        self._save_results(report)
        
        logger.info(f"Completed evaluation of {tool_name}: {len(scenario_metrics)} scenarios processed")
        return report
    
    def compare_tools(self, reports: List[ToolEvaluationReport]) -> Dict[str, Any]:
        """Generate comparative analysis of multiple tools"""
        logger.info(f"Generating comparative analysis for {len(reports)} tools")
        
        comparison = {
            'evaluation_timestamp': datetime.now().isoformat(),
            'tools_compared': [report.tool_name for report in reports],
            'total_scenarios': reports[0].total_scenarios if reports else 0,
            
            'performance_ranking': self._rank_tools_by_performance(reports),
            'quality_distribution': self._compare_quality_distributions(reports),
            'statistical_significance': self._calculate_statistical_significance(reports),
            'detailed_comparison': self._generate_detailed_comparison(reports)
        }
        
        # Save comparison results
        comparison_file = self.output_dir / "tools_comparison.json"
        with open(comparison_file, 'w') as f:
            json.dump(comparison, f, indent=2, default=str)
        
        logger.info(f"Comparative analysis saved to: {comparison_file}")
        return comparison
    
    def _find_expected_file(self, actual_file: Path, actual_scenario_dir: Path, expected_scenario_dir: Path) -> Optional[Path]:
        """Find the corresponding expected file for comparison"""
        relative_path = actual_file.relative_to(actual_scenario_dir)
        expected_file = expected_scenario_dir / relative_path
        
        if expected_file.exists():
            return expected_file
        
        # Try alternative naming conventions
        alternatives = [
            expected_scenario_dir / actual_file.name,
            expected_scenario_dir / actual_file.name.lower(),
            expected_scenario_dir / actual_file.name.replace('_', '').replace('-', '')
        ]
        
        for alt in alternatives:
            if alt.exists():
                return alt
        
        return None
    
    def _generate_tool_report(self, tool_name: str, metrics: List[ScenarioMetrics], start_time: datetime) -> ToolEvaluationReport:
        """Generate comprehensive evaluation report for a tool"""
        
        if not metrics:
            logger.warning(f"No metrics available for tool: {tool_name}")
            return self._create_empty_report(tool_name)
        
        # Calculate aggregate metrics
        f1_scores = [m.f1_score for m in metrics]
        precisions = [m.precision for m in metrics]
        recalls = [m.recall for m in metrics]
        accuracies = [m.accuracy for m in metrics]
        
        # Quality distribution
        quality_counts = defaultdict(int)
        for m in metrics:
            quality_counts[m.quality_class.value] += 1
        
        # Statistical analysis
        f1_median = statistics.median(f1_scores)
        f1_q1 = np.percentile(f1_scores, 25) if f1_scores else 0
        f1_q3 = np.percentile(f1_scores, 75) if f1_scores else 0
        
        # Performance analysis
        success_rate = len([m for m in metrics if m.f1_score >= 0.7]) / len(metrics)
        reliability_score = len([m for m in metrics if m.confidence_score >= 0.8]) / len(metrics)
        consistency_score = 1.0 - (statistics.stdev(f1_scores) if len(f1_scores) > 1 else 0)
        
        # Error analysis
        all_error_types = []
        failure_analysis = defaultdict(int)
        for m in metrics:
            all_error_types.extend(m.error_types)
            if m.f1_score < 0.5:
                for error_type in m.error_types:
                    failure_analysis[error_type] += 1
        
        common_errors = list(set(all_error_types))
        
        return ToolEvaluationReport(
            tool_name=tool_name,
            evaluation_timestamp=datetime.now().isoformat(),
            total_scenarios=len(metrics),
            
            overall_precision=statistics.mean(precisions),
            overall_recall=statistics.mean(recalls),
            overall_f1_score=statistics.mean(f1_scores),
            overall_accuracy=statistics.mean(accuracies),
            
            perfect_merges=quality_counts[MergeQuality.PERFECT.value],
            excellent_merges=quality_counts[MergeQuality.EXCELLENT.value],
            good_merges=quality_counts[MergeQuality.GOOD.value],
            acceptable_merges=quality_counts[MergeQuality.ACCEPTABLE.value],
            poor_merges=quality_counts[MergeQuality.POOR.value],
            failed_merges=quality_counts[MergeQuality.FAILED.value],
            
            precision_std=statistics.stdev(precisions) if len(precisions) > 1 else 0,
            recall_std=statistics.stdev(recalls) if len(recalls) > 1 else 0,
            f1_std=statistics.stdev(f1_scores) if len(f1_scores) > 1 else 0,
            median_f1=f1_median,
            iqr_f1=(f1_q1, f1_q3),
            
            success_rate=success_rate,
            reliability_score=reliability_score,
            consistency_score=consistency_score,
            
            scenario_metrics=metrics,
            
            common_error_patterns=common_errors,
            failure_analysis=dict(failure_analysis)
        )
    
    def _create_empty_report(self, tool_name: str) -> ToolEvaluationReport:
        """Create empty report for tools with no valid metrics"""
        return ToolEvaluationReport(
            tool_name=tool_name,
            evaluation_timestamp=datetime.now().isoformat(),
            total_scenarios=0,
            overall_precision=0.0,
            overall_recall=0.0,
            overall_f1_score=0.0,
            overall_accuracy=0.0,
            perfect_merges=0,
            excellent_merges=0,
            good_merges=0,
            acceptable_merges=0,
            poor_merges=0,
            failed_merges=0,
            precision_std=0.0,
            recall_std=0.0,
            f1_std=0.0,
            median_f1=0.0,
            iqr_f1=(0.0, 0.0),
            success_rate=0.0,
            reliability_score=0.0,
            consistency_score=0.0,
            scenario_metrics=[],
            common_error_patterns=[],
            failure_analysis={}
        )
    
    def _save_results(self, report: ToolEvaluationReport):
        """Save evaluation results to files"""
        tool_dir = self.output_dir / report.tool_name
        tool_dir.mkdir(exist_ok=True)
        
        # Save full report
        report_file = tool_dir / "evaluation_report.json"
        with open(report_file, 'w') as f:
            json.dump(asdict(report), f, indent=2, default=str)
        
        # Save metrics CSV
        if report.scenario_metrics:
            metrics_file = tool_dir / "scenario_metrics.csv"
            import pandas as pd
            df = pd.DataFrame([asdict(m) for m in report.scenario_metrics])
            df.to_csv(metrics_file, index=False)
        
        logger.info(f"Results saved for {report.tool_name} in {tool_dir}")
    
    def _rank_tools_by_performance(self, reports: List[ToolEvaluationReport]) -> List[Dict]:
        """Rank tools by overall performance"""
        ranked = sorted(reports, key=lambda r: r.overall_f1_score, reverse=True)
        
        ranking = []
        for i, report in enumerate(ranked, 1):
            ranking.append({
                'rank': i,
                'tool_name': report.tool_name,
                'overall_f1_score': report.overall_f1_score,
                'success_rate': report.success_rate,
                'reliability_score': report.reliability_score
            })
        
        return ranking
    
    def _compare_quality_distributions(self, reports: List[ToolEvaluationReport]) -> Dict:
        """Compare quality distributions across tools"""
        distribution = {}
        
        for report in reports:
            total = report.total_scenarios
            if total > 0:
                distribution[report.tool_name] = {
                    'perfect': report.perfect_merges / total,
                    'excellent': report.excellent_merges / total,
                    'good': report.good_merges / total,
                    'acceptable': report.acceptable_merges / total,
                    'poor': report.poor_merges / total,
                    'failed': report.failed_merges / total
                }
        
        return distribution
    
    def _calculate_statistical_significance(self, reports: List[ToolEvaluationReport]) -> Dict:
        """Calculate statistical significance of differences between tools"""
        if len(reports) < 2:
            return {"note": "Need at least 2 tools for significance testing"}
        
        # For now, return basic statistical comparison
        # In a full implementation, you would use proper statistical tests
        significance = {}
        
        for i, report1 in enumerate(reports):
            for j, report2 in enumerate(reports[i+1:], i+1):
                key = f"{report1.tool_name}_vs_{report2.tool_name}"
                
                f1_diff = abs(report1.overall_f1_score - report2.overall_f1_score)
                
                # Simple significance estimation based on difference and sample size
                min_scenarios = min(report1.total_scenarios, report2.total_scenarios)
                significance_threshold = 0.05 + (1.0 / max(min_scenarios, 1))
                
                significance[key] = {
                    'f1_difference': f1_diff,
                    'potentially_significant': f1_diff > significance_threshold,
                    'note': "Requires proper statistical testing for formal significance"
                }
        
        return significance
    
    def _generate_detailed_comparison(self, reports: List[ToolEvaluationReport]) -> Dict:
        """Generate detailed comparison across multiple dimensions"""
        comparison = {
            'summary_table': [],
            'strength_analysis': {},
            'weakness_analysis': {},
            'scenario_performance': {}
        }
        
        # Summary table
        for report in reports:
            comparison['summary_table'].append({
                'tool': report.tool_name,
                'f1_score': round(report.overall_f1_score, 4),
                'precision': round(report.overall_precision, 4),
                'recall': round(report.overall_recall, 4),
                'success_rate': round(report.success_rate, 4),
                'reliability': round(report.reliability_score, 4),
                'consistency': round(report.consistency_score, 4)
            })
        
        # Strength and weakness analysis
        for report in reports:
            strengths = []
            weaknesses = []
            
            if report.overall_f1_score >= 0.9:
                strengths.append("High overall accuracy")
            if report.success_rate >= 0.8:
                strengths.append("High success rate")
            if report.consistency_score >= 0.8:
                strengths.append("Consistent performance")
            
            if report.overall_f1_score < 0.7:
                weaknesses.append("Low overall accuracy")
            if report.failed_merges > report.total_scenarios * 0.2:
                weaknesses.append("High failure rate")
            if report.consistency_score < 0.6:
                weaknesses.append("Inconsistent performance")
            
            comparison['strength_analysis'][report.tool_name] = strengths
            comparison['weakness_analysis'][report.tool_name] = weaknesses
        
        return comparison


def main():
    """Main entry point for the evaluation framework"""
    parser = argparse.ArgumentParser(
        description="Merge Tool Evaluation Framework v1.0.0",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--tools', 
        nargs='+', 
        required=True,
        help='Names of merge tools to evaluate (e.g., IntelliMerge JDime FSTMerge)'
    )
    
    parser.add_argument(
        '--scenarios-base',
        type=Path,
        default=Path('output'),
        help='Base directory containing tool output scenarios'
    )
    
    parser.add_argument(
        '--expected-base',
        type=Path,
        default=Path('output'),
        help='Base directory containing expected results'
    )
    
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path('evaluation_results/scientific_evaluation'),
        help='Directory to save evaluation results'
    )
    
    parser.add_argument(
        '--extensions',
        nargs='+',
        default=['.java'],
        help='File extensions to evaluate'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize framework
    framework = ToolEvaluationFramework(args.output_dir)
    
    # Evaluate each tool
    reports = []
    for tool_name in args.tools:
        scenarios_dir = args.scenarios_base / tool_name / 'scenarios'
        expected_dir = args.expected_base / tool_name / 'expected'
        
        if not scenarios_dir.exists():
            logger.error(f"Scenarios directory not found: {scenarios_dir}")
            continue
        
        if not expected_dir.exists():
            logger.error(f"Expected directory not found: {expected_dir}")
            continue
        
        report = framework.evaluate_tool(
            tool_name, scenarios_dir, expected_dir, args.extensions
        )
        reports.append(report)
    
    # Generate comparative analysis
    if len(reports) > 1:
        comparison = framework.compare_tools(reports)
        logger.info("Comparative analysis completed")
    
    # Print summary
    print("\n" + "="*60)
    print("MERGE TOOL EVALUATION SUMMARY")
    print("="*60)
    
    for report in sorted(reports, key=lambda r: r.overall_f1_score, reverse=True):
        print(f"\n{report.tool_name}:")
        print(f"  Overall F1-Score: {report.overall_f1_score:.4f}")
        print(f"  Success Rate: {report.success_rate:.4f}")
        print(f"  Total Scenarios: {report.total_scenarios}")
        print(f"  Perfect Merges: {report.perfect_merges}")
        print(f"  Failed Merges: {report.failed_merges}")
    
    print(f"\nDetailed results saved to: {args.output_dir}")


if __name__ == "__main__":
    main()

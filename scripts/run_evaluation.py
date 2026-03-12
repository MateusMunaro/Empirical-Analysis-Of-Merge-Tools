#!/usr/bin/env python3
"""
Scientific Merge Tool Evaluation - Execution Script
==================================================

This script provides an easy-to-use interface for running the merge tool evaluation
with the specific directory structure of this research project.

Usage:
    python run_evaluation.py [options]
"""

import sys
import argparse
from pathlib import Path
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def check_directory_structure():
    """Validate the expected directory structure"""
    base_dir = Path('.')
    required_dirs = [
        'output/IntelliMerge/scenarios',
        'output/IntelliMerge/expected',
        'output/JDime/scenarios', 
        'output/JDime/expected',
        'output/FSTMerge/scenarios',
        'output/FSTMerge/expected'
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not (base_dir / dir_path).exists():
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        logger.warning("Missing directories:")
        for dir_path in missing_dirs:
            logger.warning(f"  - {dir_path}")
        logger.warning("Some tools may not be evaluated if their directories are missing.")
    
    return len(missing_dirs) == 0


def find_available_tools():
    """Find which merge tools have data available for evaluation"""
    base_dir = Path('output')
    available_tools = []
    
    for tool_dir in base_dir.iterdir():
        if tool_dir.is_dir():
            scenarios_dir = tool_dir / 'scenarios'
            expected_dir = tool_dir / 'expected'
            
            if scenarios_dir.exists() and expected_dir.exists():
                # Check if they contain any scenarios
                scenario_count = len(list(scenarios_dir.iterdir()))
                expected_count = len(list(expected_dir.iterdir()))
                
                if scenario_count > 0 and expected_count > 0:
                    available_tools.append(tool_dir.name)
                    logger.info(f"Found tool: {tool_dir.name} ({scenario_count} scenarios, {expected_count} expected)")
    
    return available_tools


def run_evaluation(tools, output_dir="evaluation_results/scientific_evaluation", verbose=False):
    """Run the evaluation framework"""
    
    # Build command
    python_cmd = "/workspaces/Pesquisa-cientifica/.venv/bin/python"
    eval_script = "scripts/merge_evaluation_tool.py"
    
    cmd = [
        python_cmd,
        eval_script,
        "--tools"
    ] + tools + [
        "--scenarios-base", "output",
        "--expected-base", "output", 
        "--output-dir", output_dir,
        "--extensions", ".java"
    ]
    
    if verbose:
        cmd.append("--verbose")
    
    logger.info(f"Running evaluation command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(result.stdout)
        if result.stderr:
            print("Warnings/Errors:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Evaluation failed with return code {e.returncode}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False


def generate_summary_report(output_dir):
    """Generate a human-readable summary report"""
    results_dir = Path(output_dir)
    
    if not results_dir.exists():
        logger.error(f"Results directory not found: {output_dir}")
        return
    
    print("\n" + "="*80)
    print("MERGE TOOL EVALUATION - SCIENTIFIC ANALYSIS SUMMARY")
    print("="*80)
    
    # Read comparison results if available
    comparison_file = results_dir / "tools_comparison.json"
    if comparison_file.exists():
        import json
        with open(comparison_file, 'r') as f:
            comparison = json.load(f)
        
        print("\n📊 PERFORMANCE RANKING:")
        print("-" * 40)
        for rank_info in comparison.get('performance_ranking', []):
            rank = rank_info['rank']
            tool = rank_info['tool_name']
            f1 = rank_info['overall_f1_score']
            success = rank_info['success_rate']
            reliability = rank_info['reliability_score']
            
            print(f"{rank}. {tool}")
            print(f"   F1-Score: {f1:.4f} | Success Rate: {success:.4f} | Reliability: {reliability:.4f}")
        
        print("\n🎯 QUALITY DISTRIBUTION:")
        print("-" * 40)
        quality_dist = comparison.get('quality_distribution', {})
        for tool, dist in quality_dist.items():
            print(f"\n{tool}:")
            print(f"  Perfect: {dist['perfect']:.2%} | Excellent: {dist['excellent']:.2%}")
            print(f"  Good: {dist['good']:.2%} | Acceptable: {dist['acceptable']:.2%}")
            print(f"  Poor: {dist['poor']:.2%} | Failed: {dist['failed']:.2%}")
    
    # Individual tool reports
    print("\n📈 DETAILED TOOL ANALYSIS:")
    print("-" * 40)
    
    for tool_dir in results_dir.iterdir():
        if tool_dir.is_dir():
            report_file = tool_dir / "evaluation_report.json"
            if report_file.exists():
                import json
                with open(report_file, 'r') as f:
                    report = json.load(f)
                
                tool_name = report['tool_name']
                print(f"\n🔧 {tool_name}:")
                print(f"   Scenarios Evaluated: {report['total_scenarios']}")
                print(f"   Overall F1-Score: {report['overall_f1_score']:.4f}")
                print(f"   Precision: {report['overall_precision']:.4f}")
                print(f"   Recall: {report['overall_recall']:.4f}")
                print(f"   Success Rate: {report['success_rate']:.4f}")
                
                if report['common_error_patterns']:
                    print(f"   Common Errors: {', '.join(report['common_error_patterns'][:3])}")
    
    print(f"\n📁 Full results available in: {output_dir}")
    print("   - Individual tool reports in subdirectories")
    print("   - Comparative analysis in tools_comparison.json")
    print("   - Detailed metrics in CSV files")


def main():
    parser = argparse.ArgumentParser(
        description="Run scientific evaluation of merge tools",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--tools',
        nargs='*',
        help='Specific tools to evaluate (default: auto-detect all available)'
    )
    
    parser.add_argument(
        '--output-dir',
        default='evaluation_results/scientific_evaluation',
        help='Output directory for results (default: evaluation_results/scientific_evaluation)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--check-only',
        action='store_true',
        help='Only check directory structure and available tools'
    )
    
    parser.add_argument(
        '--summary-only',
        action='store_true',
        help='Only generate summary from existing results'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Check directory structure
    print("🔍 Checking directory structure...")
    structure_ok = check_directory_structure()
    
    # Find available tools
    print("🔍 Detecting available merge tools...")
    available_tools = find_available_tools()
    
    if not available_tools:
        logger.error("No merge tools with complete data found!")
        logger.error("Expected directory structure:")
        logger.error("  output/[ToolName]/scenarios/")
        logger.error("  output/[ToolName]/expected/")
        return 1
    
    print(f"✅ Found {len(available_tools)} available tools: {', '.join(available_tools)}")
    
    if args.check_only:
        return 0
    
    if args.summary_only:
        generate_summary_report(args.output_dir)
        return 0
    
    # Determine which tools to evaluate
    tools_to_evaluate = args.tools if args.tools else available_tools
    
    # Validate requested tools
    invalid_tools = set(tools_to_evaluate) - set(available_tools)
    if invalid_tools:
        logger.error(f"Requested tools not available: {', '.join(invalid_tools)}")
        logger.error(f"Available tools: {', '.join(available_tools)}")
        return 1
    
    print(f"🚀 Starting evaluation of: {', '.join(tools_to_evaluate)}")
    
    # Run evaluation
    success = run_evaluation(tools_to_evaluate, args.output_dir, args.verbose)
    
    if success:
        print("\n✅ Evaluation completed successfully!")
        generate_summary_report(args.output_dir)
        return 0
    else:
        print("\n❌ Evaluation failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())

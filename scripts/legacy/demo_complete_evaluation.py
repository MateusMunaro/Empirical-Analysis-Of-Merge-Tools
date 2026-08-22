#!/usr/bin/env python3
"""
Demonstração Completa da Ferramenta de Avaliação Científica de Merge Tools
========================================================================

Este script demonstra o uso completo da ferramenta de avaliação científica
desenvolvida para análise rigorosa de ferramentas de merge.

Execute: python scripts/demo_complete_evaluation.py
"""

import os
import sys
import subprocess
from pathlib import Path
import json

# Repository root (one level above /scripts), so paths work regardless of cwd.
REPO_ROOT = Path(__file__).resolve().parent.parent
PYTHON = sys.executable


def print_header(title):
    print("\n" + "=" * 80)
    print(f"🔬 {title}")
    print("=" * 80)


def print_section(title):
    print(f"\n📊 {title}")
    print("-" * (len(title) + 5))


def run_command(cmd, description):
    """Run a command from REPO_ROOT and report the result."""
    print(f"\n▶️  {description}")
    print(f"💻 Comando: {' '.join(cmd)}")
    print("⏳ Executando...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO_ROOT))
        if result.returncode == 0:
            print("✅ Sucesso!")
            if result.stdout:
                lines = result.stdout.strip().split("\n")
                if len(lines) > 10:
                    print("📄 Últimas linhas da saída:")
                    for line in lines[-10:]:
                        print(f"   {line}")
                else:
                    print("📄 Saída:")
                    print(result.stdout)
        else:
            print("❌ Erro!")
            print(f"Código de retorno: {result.returncode}")
            if result.stderr:
                print(f"Erro: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Exceção: {e}")
        return False


def display_results_summary():
    results_dir = REPO_ROOT / "evaluation_results" / "scientific_evaluation"

    if not results_dir.exists():
        print("❌ Diretório de resultados não encontrado!")
        return

    print_section("RESUMO DOS RESULTADOS CIENTÍFICOS")

    comparison_file = results_dir / "tools_comparison.json"
    if comparison_file.exists():
        with open(comparison_file, "r", encoding="utf-8") as f:
            comparison = json.load(f)

        print("\n🏆 RANKING DE DESEMPENHO:")
        for rank_info in comparison.get("performance_ranking", []):
            rank = rank_info["rank"]
            tool = rank_info["tool_name"]
            f1 = rank_info["overall_f1_score"]
            success = rank_info["success_rate"]
            reliability = rank_info["reliability_score"]
            print(f"   {rank}º lugar: {tool}")
            print(f"       F1-Score: {f1:.4f} | Taxa de Sucesso: {success:.4f} | Confiabilidade: {reliability:.4f}")

        print("\n📈 DISTRIBUIÇÃO DE QUALIDADE:")
        quality_dist = comparison.get("quality_distribution", {})
        for tool, dist in quality_dist.items():
            print(f"\n   🔧 {tool}:")
            print(f"       Perfect: {dist['perfect']:.1%} | Excellent: {dist['excellent']:.1%}")
            print(f"       Good: {dist['good']:.1%} | Acceptable: {dist['acceptable']:.1%}")
            print(f"       Poor: {dist['poor']:.1%} | Failed: {dist['failed']:.1%}")

    print("\n📁 ARQUIVOS GERADOS:")
    for item in results_dir.rglob("*"):
        if item.is_file():
            rel_path = item.relative_to(results_dir)
            size_kb = item.stat().st_size / 1024
            print(f"   📄 {rel_path} ({size_kb:.1f} KB)")


def main():
    print_header("DEMONSTRAÇÃO COMPLETA - FERRAMENTA DE AVALIAÇÃO CIENTÍFICA DE MERGE TOOLS")

    print(
        """
🎯 OBJETIVO:
Esta demonstração mostra o uso completo de uma ferramenta científica robusta para
avaliar e comparar ferramentas de merge em desenvolvimento de software.

🔬 CARACTERÍSTICAS CIENTÍFICAS:
• Métricas rigorosas (Precisão, Recall, F1-Score, Acurácia)
• Testes de significância estatística
• Classificação de qualidade estruturada
• Análise de erros sistemática
• Relatórios adequados para publicação acadêmica

🛠️  FERRAMENTAS AVALIADAS:
• IntelliMerge: Ferramenta de merge estrutural
• JDime: Java Differencing and Merging Tool
• FSTMerge: Feature Structure Tree Merge

📊 RESULTADOS ESPERADOS:
• Análise comparativa rigorosa
• Ranking estatisticamente validado
• Identificação de pontos fortes e fracos
• Recomendações baseadas em evidências
"""
    )

    input("\n⏳ Pressione Enter para começar a demonstração...")

    print_section("ETAPA 1: VERIFICAÇÃO DA ESTRUTURA DE DADOS")
    success = run_command(
        [PYTHON, "scripts/run_evaluation.py", "--check-only"],
        "Verificando disponibilidade de dados para avaliação",
    )
    if not success:
        print("❌ Falha na verificação. Verifique se os dados estão disponíveis.")
        return 1

    input("\n⏳ Pressione Enter para continuar com a avaliação...")

    print_section("ETAPA 2: EXECUÇÃO DA AVALIAÇÃO CIENTÍFICA")
    success = run_command(
        [PYTHON, "scripts/run_evaluation.py"],
        "Executando avaliação científica completa de todas as ferramentas",
    )
    if not success:
        print("❌ Falha na avaliação. Verifique os logs para mais detalhes.")
        return 1

    input("\n⏳ Pressione Enter para gerar o relatório científico...")

    print_section("ETAPA 3: GERAÇÃO DO RELATÓRIO CIENTÍFICO")
    success = run_command(
        [PYTHON, "scripts/scientific_report_generator.py"],
        "Gerando relatório científico completo em formato Markdown",
    )
    if not success:
        print("❌ Falha na geração do relatório.")
        return 1

    print_section("ETAPA 4: ANÁLISE DOS RESULTADOS")
    display_results_summary()

    print_header("DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO")

    print(f"\n📂 Todos os resultados estão disponíveis em:")
    print(f"   {REPO_ROOT / 'evaluation_results' / 'scientific_evaluation'}")
    print(f"\n📖 Relatório científico principal:")
    print(f"   evaluation_results/scientific_evaluation/scientific_merge_tools_evaluation.md")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Demonstração interrompida pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro durante a demonstração: {e}")
        sys.exit(1)

#!/usr/bin/env python3
"""
Demonstração Completa da Ferramenta de Avaliação Científica de Merge Tools
========================================================================

Este script demonstra o uso completo da ferramenta de avaliação científica
desenvolvida para análise rigorosa de ferramentas de merge.

Execute: python demo_complete_evaluation.py
"""

import os
import sys
import subprocess
from pathlib import Path
import json
import time

def print_header(title):
    """Imprime cabeçalho formatado"""
    print("\n" + "="*80)
    print(f"🔬 {title}")
    print("="*80)

def print_section(title):
    """Imprime seção formatada"""
    print(f"\n📊 {title}")
    print("-" * (len(title) + 5))

def run_command(cmd, description):
    """Executa comando e mostra resultado"""
    print(f"\n▶️  {description}")
    print(f"💻 Comando: {cmd}")
    print("⏳ Executando...")
    
    try:
        result = subprocess.run(cmd.split(), capture_output=True, text=True, cwd='/workspaces/Pesquisa-cientifica')
        if result.returncode == 0:
            print("✅ Sucesso!")
            if result.stdout:
                # Mostra apenas as últimas linhas para não poluir a saída
                lines = result.stdout.strip().split('\n')
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
    """Mostra resumo dos resultados"""
    results_dir = Path('/workspaces/Pesquisa-cientifica/evaluation_results/scientific_evaluation')
    
    if not results_dir.exists():
        print("❌ Diretório de resultados não encontrado!")
        return
    
    print_section("RESUMO DOS RESULTADOS CIENTÍFICOS")
    
    # Carrega dados de comparação
    comparison_file = results_dir / "tools_comparison.json"
    if comparison_file.exists():
        with open(comparison_file, 'r') as f:
            comparison = json.load(f)
        
        print("\n🏆 RANKING DE DESEMPENHO:")
        for rank_info in comparison.get('performance_ranking', []):
            rank = rank_info['rank']
            tool = rank_info['tool_name']
            f1 = rank_info['overall_f1_score']
            success = rank_info['success_rate']
            reliability = rank_info['reliability_score']
            
            print(f"   {rank}º lugar: {tool}")
            print(f"       F1-Score: {f1:.4f} | Taxa de Sucesso: {success:.4f} | Confiabilidade: {reliability:.4f}")
        
        print("\n📈 DISTRIBUIÇÃO DE QUALIDADE:")
        quality_dist = comparison.get('quality_distribution', {})
        for tool, dist in quality_dist.items():
            print(f"\n   🔧 {tool}:")
            print(f"       Perfect: {dist['perfect']:.1%} | Excellent: {dist['excellent']:.1%}")
            print(f"       Good: {dist['good']:.1%} | Acceptable: {dist['acceptable']:.1%}")
            print(f"       Poor: {dist['poor']:.1%} | Failed: {dist['failed']:.1%}")
    
    # Lista arquivos gerados
    print("\n📁 ARQUIVOS GERADOS:")
    for item in results_dir.rglob("*"):
        if item.is_file():
            rel_path = item.relative_to(results_dir)
            size_kb = item.stat().st_size / 1024
            print(f"   📄 {rel_path} ({size_kb:.1f} KB)")

def main():
    """Demonstração completa da ferramenta"""
    
    print_header("DEMONSTRAÇÃO COMPLETA - FERRAMENTA DE AVALIAÇÃO CIENTÍFICA DE MERGE TOOLS")
    
    print("""
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
""")
    
    input("\n⏳ Pressione Enter para começar a demonstração...")
    
    # Etapa 1: Verificação da estrutura
    print_section("ETAPA 1: VERIFICAÇÃO DA ESTRUTURA DE DADOS")
    success = run_command(
        "/workspaces/Pesquisa-cientifica/.venv/bin/python scripts/run_evaluation.py --check-only",
        "Verificando disponibilidade de dados para avaliação"
    )
    
    if not success:
        print("❌ Falha na verificação. Verifique se os dados estão disponíveis.")
        return 1
    
    input("\n⏳ Pressione Enter para continuar com a avaliação...")
    
    # Etapa 2: Avaliação científica completa
    print_section("ETAPA 2: EXECUÇÃO DA AVALIAÇÃO CIENTÍFICA")
    print("""
Esta etapa executa a avaliação completa de todas as ferramentas disponíveis:
• Análise de cada cenário de merge
• Cálculo de métricas múltiplas  
• Classificação de qualidade
• Análise de erros
• Testes estatísticos
""")
    
    success = run_command(
        "/workspaces/Pesquisa-cientifica/.venv/bin/python scripts/run_evaluation.py",
        "Executando avaliação científica completa de todas as ferramentas"
    )
    
    if not success:
        print("❌ Falha na avaliação. Verifique os logs para mais detalhes.")
        return 1
    
    input("\n⏳ Pressione Enter para gerar o relatório científico...")
    
    # Etapa 3: Geração do relatório científico
    print_section("ETAPA 3: GERAÇÃO DO RELATÓRIO CIENTÍFICO")
    print("""
O relatório científico inclui:
• Abstract e Introdução
• Metodologia detalhada
• Resultados com tabelas estatísticas
• Análise de significância
• Discussão e implicações
• Ameaças à validade
• Informações de reprodutibilidade
""")
    
    success = run_command(
        "/workspaces/Pesquisa-cientifica/.venv/bin/python scripts/scientific_report_generator.py",
        "Gerando relatório científico completo em formato Markdown"
    )
    
    if not success:
        print("❌ Falha na geração do relatório.")
        return 1
    
    # Etapa 4: Exibição dos resultados
    print_section("ETAPA 4: ANÁLISE DOS RESULTADOS")
    display_results_summary()
    
    # Conclusão
    print_header("DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO")
    
    print("""
✅ AVALIAÇÃO CIENTÍFICA COMPLETA REALIZADA!

📊 RESULTADOS OBTIDOS:
• Avaliação rigorosa de 3 ferramentas de merge
• Análise de mais de 140 cenários de merge
• Métricas estatisticamente validadas
• Classificação de qualidade estruturada
• Relatório científico completo

📁 ARQUIVOS GERADOS:
• evaluation_results/scientific_evaluation/: Todos os dados da avaliação
• scientific_merge_tools_evaluation.md: Relatório científico completo
• tools_comparison.json: Comparação detalhada entre ferramentas
• scenario_metrics.csv: Métricas por cenário (cada ferramenta)
• evaluation_report.json: Relatório completo (cada ferramenta)

🔬 APLICAÇÃO CIENTÍFICA:
Os resultados estão formatados seguindo padrões de pesquisa acadêmica e podem ser
utilizados diretamente em:
• Artigos científicos
• Dissertações e teses
• Relatórios técnicos
• Documentação de projeto

🎯 PRÓXIMOS PASSOS SUGERIDOS:
1. Revisar o relatório científico gerado
2. Analisar as métricas detalhadas por cenário
3. Examinar os padrões de erro identificados
4. Considerar as implicações práticas dos resultados
5. Utilizar os dados para tomada de decisão informada

💡 VALOR CIENTÍFICO:
Esta ferramenta proporciona uma base sólida e cientificamente rigorosa para:
• Seleção de ferramentas baseada em evidências
• Identificação de limitações e pontos fortes
• Orientação para desenvolvimento futuro
• Validação de claims de desempenho
""")
    
    print(f"\n📂 Todos os resultados estão disponíveis em:")
    print(f"   /workspaces/Pesquisa-cientifica/evaluation_results/scientific_evaluation/")
    print(f"\n📖 Relatório científico principal:")
    print(f"   evaluation_results/scientific_evaluation/scientific_merge_tools_evaluation.md"))
    
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

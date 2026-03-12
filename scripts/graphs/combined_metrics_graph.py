import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def create_combined_metrics_chart():
    """
    Cria um gráfico de barras agrupadas para comparar todas as métricas das ferramentas
    de merge em diferentes níveis de dificuldade.
    """
    
    # Dados completos organizados
    data = {
        'Tool': ['FSTMerge', 'JDime', 'IntelliMerge'] * 3,
        'Difficulty': ['1->1'] * 3 + ['1->N'] * 3 + ['N->N'] * 3,
        'Precision': [0.00, 0.07, 0.76, 0.73, 0.82, 0.07, 0.76, 0.67, 0.11],
        'Recall': [0.00, 0.07, 0.76, 0.73, 0.80, 0.03, 0.76, 0.84, 0.11],
        'F1_Score': [0.00, 0.07, 0.76, 0.73, 0.83, 0.05, 0.76, 0.81, 0.11],
        'Accuracy': [0.00, 0.07, 0.76, 0.71, 0.82, 0.00, 0.76, 0.63, 0.07]
    }
    
    # Criar DataFrame
    df = pd.DataFrame(data)
    
    # Configurar o estilo do gráfico - usar subplots para cada dificuldade
    fig, axes = plt.subplots(1, 3, figsize=(18, 8))
    fig.suptitle('Comparação de Todas as Métricas entre Ferramentas de Merge\npor Nível de Dificuldade', 
                fontsize=18, fontweight='bold', y=0.98)
    
    difficulties = ['1->1', '1->N', 'N->N']
    tools = ['FSTMerge', 'JDime', 'IntelliMerge']
    metrics = ['Precision', 'Recall', 'F1_Score', 'Accuracy']
    
    # Definir tons de cinza para cada métrica
    metric_colors = {
        'Precision': '#1a1a1a',    # Cinza muito escuro
        'Recall': '#404040',       # Cinza escuro
        'F1_Score': '#666666',     # Cinza médio
        'Accuracy': '#999999'      # Cinza claro
    }
    
    # Configurar posições das barras
    x = np.arange(len(tools))
    width = 0.2  # Largura das barras
    
    # Criar subgráfico para cada dificuldade
    for idx, difficulty in enumerate(difficulties):
        ax = axes[idx]
        
        # Filtrar dados para a dificuldade atual
        diff_data = df[df['Difficulty'] == difficulty]
        
        # Criar barras para cada métrica
        for i, metric in enumerate(metrics):
            values = []
            for tool in tools:
                value = diff_data[diff_data['Tool'] == tool][metric].iloc[0]
                values.append(value)
            
            # Posicionar as barras
            positions = x + (i - 2) * width
            bars = ax.bar(positions, values, width, label=metric if idx == 0 else "", 
                         color=metric_colors[metric], alpha=0.8, edgecolor='white', linewidth=1)
            
            # Adicionar valores no topo das barras (apenas para valores > 0.05)
            for j, bar in enumerate(bars):
                height = bar.get_height()
                if height > 0.05:  # Só mostrar texto se o valor for significativo
                    ax.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                           f'{values[j]:.2f}', ha='center', va='bottom', 
                           fontsize=8, fontweight='bold')
        
        # Configurar cada subgráfico
        ax.set_title(f'Dificuldade {difficulty}', fontsize=14, fontweight='bold', pad=10)
        ax.set_xlabel('Ferramentas', fontsize=12, fontweight='bold')
        if idx == 0:
            ax.set_ylabel('Valor da Métrica', fontsize=12, fontweight='bold')
        
        # Configurar o eixo X
        ax.set_xticks(x)
        ax.set_xticklabels(tools, fontsize=10)
        
        # Configurar o eixo Y
        ax.set_ylim(0, 1.0)
        ax.set_yticks(np.arange(0, 1.1, 0.2))
        ax.tick_params(axis='y', labelsize=10)
        
        # Adicionar grade sutil
        ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5, axis='y')
        ax.set_axisbelow(True)
        
        # Rotacionar labels se necessário
        plt.setp(ax.get_xticklabels(), rotation=0, ha='center')
    
    # Configurar legenda apenas no primeiro subplot
    axes[0].legend(title='Métricas', title_fontsize=11, fontsize=10, 
                  loc='upper left', frameon=True, fancybox=True, shadow=True)
    
    # Melhorar a aparência geral
    plt.tight_layout()
    plt.subplots_adjust(top=0.85)
    
    return fig, axes

def create_single_combined_chart():
    """
    Cria um único gráfico com todas as métricas agrupadas por ferramenta.
    """
    # Dados completos organizados
    data = {
        'Tool': ['FSTMerge', 'JDime', 'IntelliMerge'] * 3,
        'Difficulty': ['1->1'] * 3 + ['1->N'] * 3 + ['N->N'] * 3,
        'Precision': [0.00, 0.07, 0.76, 0.73, 0.82, 0.07, 0.76, 0.67, 0.11],
        'Recall': [0.00, 0.07, 0.76, 0.73, 0.80, 0.03, 0.76, 0.84, 0.11],
        'F1_Score': [0.00, 0.07, 0.76, 0.73, 0.83, 0.05, 0.76, 0.81, 0.11],
        'Accuracy': [0.00, 0.07, 0.76, 0.71, 0.82, 0.00, 0.76, 0.63, 0.07]
    }
    
    # Calcular média de cada métrica por ferramenta
    df = pd.DataFrame(data)
    avg_data = df.groupby('Tool')[['Precision', 'Recall', 'F1_Score', 'Accuracy']].mean().reset_index()
    
    # Configurar o gráfico
    fig, ax = plt.subplots(figsize=(12, 8))
    
    tools = avg_data['Tool'].tolist()
    metrics = ['Precision', 'Recall', 'F1_Score', 'Accuracy']
    
    # Definir tons de cinza para cada métrica
    metric_colors = {
        'Precision': '#1a1a1a',    # Cinza muito escuro
        'Recall': '#404040',       # Cinza escuro
        'F1_Score': '#666666',     # Cinza médio
        'Accuracy': '#999999'      # Cinza claro
    }
    
    # Configurar posições das barras
    x = np.arange(len(tools))
    width = 0.2
    
    # Criar barras para cada métrica
    for i, metric in enumerate(metrics):
        values = avg_data[metric].tolist()
        positions = x + (i - 1.5) * width
        bars = ax.bar(positions, values, width, label=metric, 
                     color=metric_colors[metric], alpha=0.8, edgecolor='white', linewidth=1)
        
        # Adicionar valores no topo das barras
        for j, bar in enumerate(bars):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                   f'{values[j]:.2f}', ha='center', va='bottom', 
                   fontsize=9, fontweight='bold')
    
    # Configurar o gráfico
    ax.set_xlabel('Ferramentas de Merge', fontsize=14, fontweight='bold')
    ax.set_ylabel('Valor Médio das Métricas', fontsize=14, fontweight='bold')
    ax.set_title('Comparação Média de Todas as Métricas\nentre Ferramentas de Merge', 
                fontsize=16, fontweight='bold', pad=20)
    
    # Configurar eixos
    ax.set_xticks(x)
    ax.set_xticklabels(tools, fontsize=12)
    ax.set_ylim(0, 1.0)
    ax.set_yticks(np.arange(0, 1.1, 0.1))
    ax.tick_params(axis='y', labelsize=11)
    
    # Adicionar grade e legenda
    ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5, axis='y')
    ax.set_axisbelow(True)
    ax.legend(title='Métricas', title_fontsize=12, fontsize=11, 
             loc='upper right', frameon=True, fancybox=True, shadow=True)
    
    plt.tight_layout()
    return fig, ax

def save_charts():
    """
    Salva ambos os tipos de gráficos combinados.
    """
    # Gráfico com subplots
    fig1, axes = create_combined_metrics_chart()
    plt.figure(fig1.number)
    plt.savefig('combined_metrics_by_difficulty.png', dpi=300, bbox_inches='tight', facecolor='white')
    print("Gráfico combinado por dificuldade salvo como: combined_metrics_by_difficulty.png")
    
    # Gráfico com médias
    fig2, ax = create_single_combined_chart()
    plt.figure(fig2.number)
    plt.savefig('combined_metrics_average.png', dpi=300, bbox_inches='tight', facecolor='white')
    print("Gráfico combinado de médias salvo como: combined_metrics_average.png")
    
    return fig1, fig2

def display_charts():
    """
    Exibe ambos os gráficos.
    """
    fig1, axes = create_combined_metrics_chart()
    fig2, ax = create_single_combined_chart()
    plt.show()
    return fig1, fig2

def print_data_summary():
    """
    Imprime um resumo completo dos dados.
    """
    print("=== Resumo Completo dos Dados ===")
    print("\nPRECISION:")
    print("Ferramenta    | 1->1  | 1->N  | N->N")
    print("------------- | ----- | ----- | -----")
    print("FSTMerge      | 0.00  | 0.73  | 0.76")
    print("JDime         | 0.07  | 0.82  | 0.67")
    print("IntelliMerge  | 0.76  | 0.07  | 0.11")
    
    print("\nRECALL:")
    print("Ferramenta    | 1->1  | 1->N  | N->N")
    print("------------- | ----- | ----- | -----")
    print("FSTMerge      | 0.00  | 0.73  | 0.76")
    print("JDime         | 0.07  | 0.80  | 0.84")
    print("IntelliMerge  | 0.76  | 0.03  | 0.11")
    
    print("\nF1-SCORE:")
    print("Ferramenta    | 1->1  | 1->N  | N->N")
    print("------------- | ----- | ----- | -----")
    print("FSTMerge      | 0.00  | 0.73  | 0.76")
    print("JDime         | 0.07  | 0.83  | 0.81")
    print("IntelliMerge  | 0.76  | 0.05  | 0.11")
    
    print("\nACCURACY:")
    print("Ferramenta    | 1->1  | 1->N  | N->N")
    print("------------- | ----- | ----- | -----")
    print("FSTMerge      | 0.00  | 0.71  | 0.76")
    print("JDime         | 0.07  | 0.82  | 0.63")
    print("IntelliMerge  | 0.76  | 0.00  | 0.07")

if __name__ == "__main__":
    print("Gerando gráficos combinados de todas as métricas...")
    
    # Imprimir resumo dos dados
    print_data_summary()
    
    # Criar e salvar os gráficos
    fig1, fig2 = save_charts()
    
    # Exibir os gráficos
    display_charts()
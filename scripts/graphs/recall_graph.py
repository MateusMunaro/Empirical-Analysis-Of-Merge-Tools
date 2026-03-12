import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def create_recall_comparison_chart():
    """
    Cria um gráfico de barras agrupadas para comparar o recall das ferramentas
    de merge em diferentes níveis de dificuldade.
    """
    
    # Dados de recall organizados
    data = {
        'Tool': ['FSTMerge', 'JDime', 'IntelliMerge', 'FSTMerge', 'JDime', 'IntelliMerge', 
                'FSTMerge', 'JDime', 'IntelliMerge'],
        'Difficulty': ['1->1', '1->1', '1->1', '1->N', '1->N', '1->N', 
                      'N->N', 'N->N', 'N->N'],
        'Recall': [0.00, 0.07, 0.76, 0.73, 0.80, 0.03, 0.76, 0.84, 0.11]
    }
    
    # Criar DataFrame
    df = pd.DataFrame(data)
    
    # Configurar o estilo do gráfico
    plt.style.use('default')
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Definir as categorias de dificuldade e ferramentas
    difficulties = ['1->1', '1->N', 'N->N']
    tools = ['FSTMerge', 'JDime', 'IntelliMerge']
    
    # Definir tons de cinza para cada ferramenta
    colors = {
        'FSTMerge': '#2F2F2F',      # Cinza escuro
        'JDime': '#696969',         # Cinza médio
        'IntelliMerge': '#A9A9A9'   # Cinza claro
    }
    
    # Configurar posições das barras
    x = np.arange(len(difficulties))
    width = 0.25  # Largura das barras
    
    # Criar as barras para cada ferramenta
    for i, tool in enumerate(tools):
        tool_data = df[df['Tool'] == tool]
        values = []
        for difficulty in difficulties:
            recall = tool_data[tool_data['Difficulty'] == difficulty]['Recall'].iloc[0]
            values.append(recall)
        
        # Posicionar as barras
        positions = x + (i - 1) * width
        bars = ax.bar(positions, values, width, label=tool, color=colors[tool], 
                     alpha=0.8, edgecolor='white', linewidth=1)
        
        # Adicionar valores no topo das barras
        for j, bar in enumerate(bars):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                   f'{values[j]:.2f}', ha='center', va='bottom', 
                   fontsize=10, fontweight='bold')
    
    # Configurar o gráfico
    ax.set_xlabel('Nível de Dificuldade', fontsize=14, fontweight='bold')
    ax.set_ylabel('Recall', fontsize=14, fontweight='bold')
    ax.set_title('Comparação de Recall entre Ferramentas de Merge\npor Nível de Dificuldade', 
                fontsize=16, fontweight='bold', pad=20)
    
    # Configurar o eixo X
    ax.set_xticks(x)
    ax.set_xticklabels(difficulties, fontsize=12)
    
    # Configurar o eixo Y
    ax.set_ylim(0, 1.0)
    ax.set_yticks(np.arange(0, 1.1, 0.1))
    ax.tick_params(axis='y', labelsize=11)
    
    # Adicionar grade sutil
    ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5, axis='y')
    ax.set_axisbelow(True)
    
    # Configurar legenda
    ax.legend(title='Ferramentas de Merge', title_fontsize=12, fontsize=11, 
             loc='upper right', frameon=True, fancybox=True, shadow=True)
    
    # Melhorar a aparência geral
    plt.tight_layout()
    
    # Adicionar linha de referência em 0.5 (recall médio)
    ax.axhline(y=0.5, color='red', linestyle='--', alpha=0.5, linewidth=1)
    ax.text(0.02, 0.52, 'Recall = 0.5', transform=ax.transAxes, 
           fontsize=9, color='red', alpha=0.7)
    
    return fig, ax

def save_chart(filename='recall_comparison.png', dpi=300):
    """
    Salva o gráfico em alta resolução.
    
    Args:
        filename (str): Nome do arquivo para salvar
        dpi (int): Resolução da imagem
    """
    fig, ax = create_recall_comparison_chart()
    plt.savefig(filename, dpi=dpi, bbox_inches='tight', facecolor='white')
    print(f"Gráfico salvo como: {filename}")
    return fig, ax

def display_chart():
    """
    Exibe o gráfico na tela.
    """
    fig, ax = create_recall_comparison_chart()
    plt.show()
    return fig, ax

def print_data_summary():
    """
    Imprime um resumo dos dados utilizados.
    """
    print("=== Resumo dos Dados de Recall ===")
    print("Ferramenta    | 1->1  | 1->N  | N->N")
    print("------------- | ----- | ----- | -----")
    print("FSTMerge      | 0.00  | 0.73  | 0.76")
    print("JDime         | 0.07  | 0.80  | 0.84") 
    print("IntelliMerge  | 0.76  | 0.03  | 0.11")
    print("\nObservações:")
    print("- JDime apresenta melhor recall em cenários 1->N e N->N")
    print("- IntelliMerge se destaca apenas em cenários 1->1")
    print("- FSTMerge tem performance consistente em cenários complexos")

if __name__ == "__main__":
    # Exemplo de uso
    print("Gerando gráfico de comparação de recall...")
    
    # Imprimir resumo dos dados
    print_data_summary()
    
    # Criar e salvar o gráfico
    fig, ax = save_chart('recall_comparison_grayscale.png')
    
    # Exibir o gráfico
    display_chart()
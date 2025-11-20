import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional
import networkx as nx

from Modelagem import Instance

def plot_gantt(inst: Instance, res: Dict, title: Optional[str] = None) -> None:
    """
    Plota um Gantt simples da solução.
    - Cada job é representado por uma barra horizontal
    - Mostra os tempos de início (b) e término (c)
    - Setas indicam a sequência dos jobs com tempos de espera
    """
    if not res.get("feasible", False):
        print("Solução não é factível. Violações:", res.get("violations"))
        return
        
    seq = res["sequence_normalized"]  # Sequência 0-based
    b = res["b"]  # Tempos de início
    c = res["c"]  # Tempos de término

    plt.figure(figsize=(12, max(3, len(seq) * 0.5)))
    yticks = []
    ylabels = []

    # Para cada job na sequência
    for idx, j in enumerate(seq):
        y = idx  # Posição vertical
        yticks.append(y)
        ylabels.append(f"Job {j+1}")  # Mostra job+1 para usuário (1-based)
        
        # Barra horizontal do job
        start = b[j]
        duration = inst.p[j]
        plt.barh(y, duration, left=start, height=0.4)
        
        # Marcadores de início e fim
        plt.vlines(start, y-0.2, y+0.2, linewidth=1)
        plt.vlines(c[j], y-0.2, y+0.2, linewidth=1)
        
        # Rótulo com intervalo [início, fim]
        plt.text((start + c[j]) / 2, y, 
                f"[{start:.1f}, {c[j]:.1f}]",
                ha="center", va="center")

    # Setas conectando jobs consecutivos com rótulos de tempo
    for r in range(1, len(seq)):
        i = seq[r-1]  # Job anterior
        j = seq[r]    # Job atual
        
        # Calcula o tempo entre jobs
        gap = b[j] - c[i]  # Tempo entre fim de i e início de j
        
        # Desenha a seta
        plt.annotate("",
                    xy=(b[j], r),      # Ponta da seta (início do job atual)
                    xytext=(c[i], r-1), # Base da seta (fim do job anterior)
                    arrowprops=dict(arrowstyle="->", lw=1))
        
        # Adiciona o rótulo no meio da seta
        mid_x = (c[i] + b[j]) / 2
        mid_y = r - 0.5
        plt.text(mid_x, mid_y, f"{gap:.1f}", 
                ha="center", va="center",
                bbox=dict(facecolor='white', edgecolor='none', alpha=0.7))

    plt.yticks(yticks, ylabels)
    plt.xlabel("Tempo")
    if title is None:
        title = f"Gantt da solução — C_max = {res['C_max']:.1f}"
    plt.title(title)
    plt.tight_layout()
    plt.grid(True, alpha=0.3)
    plt.show()
    print("Gantt plot gerado com sucesso.")
    print("solução:", res["sequence_normalized"])

def plot_precedence_graph(inst: Instance, title: Optional[str] = None) -> None:
    """
    Desenha um grafo direcionado simples (sem networkx) para precedências.
    - Cada nó é um job real (1..n), com rótulo "j (p_j)".
    - Cada arco (i->j) em A tem rótulo "d_ij".
    - Layout por camadas: níveis topológicos simples calculados
      via Kahn (ignorando dummies 0 e n+1).
    """
    n = inst.n
    # Constrói DAG só com jobs reais
    succ = {i: [] for i in range(n)} # Lista de sucessores
    indeg = {i: 0 for i in range(n)} # Grau de entrada
    
    # Usando a matriz dij para adicionar as dependências
    for i in range(n):
        for j in range(n):
            if inst.d[i][j] != -1:  # Se há uma dependência com atraso
                succ[i].append(j)
                indeg[j] += 1

    # Kahn para camadas
    layers: List[List[int]] = []
    current = [i for i in range(n) if indeg[i] == 0]
    visited = set()
    while current:
        layers.append(current[:])
        next_level = []
        for u in current:
            visited.add(u)
            for v in succ[u]:
                indeg[v] -= 1
                if indeg[v] == 0:
                    next_level.append(v)
        current = next_level

    # Se sobrou nó não visitado (ciclos): ainda vamos plotar, empilhando restante
    remaining = [i for i in range(n) if i not in visited]
    if remaining:
        layers.append(remaining)

    # Coordenadas dos nós
    positions: Dict[int, Tuple[float, float]] = {}
    x_gap = 3.0
    y_gap = 1.5
    for lx, level in enumerate(layers):
        for k, node in enumerate(level):
            positions[node] = (lx * x_gap, -k * y_gap)

    # Figura única (sem subplots)
    plt.figure(figsize=(max(6, 2*len(layers)), max(3, 0.5*n)))
    # Nós
    for node, (x, y) in positions.items():
        plt.scatter([x], [y], s=200)
        # Mostra o job como node+1; tenta pegar p do índice correspondente (fallback caso p esteja indexado diferentemente)
        p_val = inst.p[node]
        plt.text(x, y+0.2, f"{node+1} (p={p_val})", ha="center")

    # Arestas com rótulo d_ij
    for i in range(n):
        for j in range(n):
            if inst.d[i][j] != -1:  # Se houver relação de precedência
                x1, y1 = positions[i]
                x2, y2 = positions[j]
                plt.annotate("",
                             xy=(x2, y2), xycoords='data',
                             xytext=(x1, y1), textcoords='data',
                             arrowprops=dict(arrowstyle="->", lw=1))
                # Rótulo próximo ao meio
                mx, my = (x1 + x2) / 2, (y1 + y2) / 2
                dij = inst.d[i][j]
                plt.text(mx, my+0.2, f"d={dij}", ha="center")

    plt.axis("off")
    if title is None:
        title = "Precedências (rótulo do nó = job e p; rótulo da aresta = d_ij)"
    plt.title(title)
    plt.tight_layout()
    plt.show()

